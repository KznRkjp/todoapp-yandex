
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.urls import reverse
from django.views.generic import ListView
from tasks.forms import AddTaskForm, TodoItemForm, TodoItemExportForm
from tasks.models import TodoItem
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from taggit.models import Tag, TaggedItem
from trello import TrelloClient
from accounts.models import Profile
from django.db.models import Count


@login_required
def index(request):
    counts = Tag.objects.annotate(
        total_tasks=Count('todoitem')
    ).order_by("-total_tasks")

    counts = {
        c.name: c.total_tasks
        for c in counts
    }


    p_counts = {
        t.get_priority_display(): TodoItem.objects.filter(priority=t.priority).count()
        for t in TodoItem.objects.all()
    }

    #print (p_counts)


    # qs = TodoItem.objects.values_list("priority")
    # counts1 = Count(qs)
    # print (counts1)
    #
    # counts1 = TodoItem.objects.annotate(
    #      total_priorities=Count('priority')
    #  )
    # print(counts1)
    # print(58*"*")
    # counts1 = {
    #     c.get_priority_display(): c.total_priorities
    #     for c in counts1
    # }
    # print(counts1)


    return render(request, "tasks/index.html", {"counts": counts, "p_counts": p_counts})



def complete_task(request, uid):
    t = TodoItem.objects.get(id=uid)
    t.is_completed = True
    t.save()
    if t.trello_id:
        complete_task_trello(t,request.user)
    return HttpResponse("OK")

def complete_task_trello(task, owner):
    prof = Profile.objects.get(user=owner) #получаем профайл пользователя
    key = prof.trello_key #из профайла достаем ключ
    token = prof.trello_token
    client = TrelloClient(api_key=key, api_secret=token)
    card = client.get_card(task.trello_id)
    board = client.get_board(task.trello_board_id)
    card.change_list(board.list_lists()[2].id)



def uncomplete_task(request, uid):
    t = TodoItem.objects.get(id=uid)
    t.is_completed = False
    t.save()
    if t.trello_id:
        uncomplete_task_trello(t,request.user)
    return HttpResponse("OK")

def uncomplete_task_trello(task, owner):
    prof = Profile.objects.get(user=owner) #получаем профайл пользователя
    key = prof.trello_key #из профайла достаем ключ
    token = prof.trello_token
    client = TrelloClient(api_key=key, api_secret=token)
    card = client.get_card(task.trello_id)
    board = client.get_board(task.trello_board_id)
    card.change_list(board.list_lists()[0].id)

def api_error(request):
    1/0


def add_task(request):
    if request.method == "POST":
        desc = request.POST["description"]
        t = TodoItem(description=desc)
        t.save()

    return redirect(reverse("tasks:list"))


def delete_task(request, uid):
    #print (request.path)
    t = TodoItem.objects.get(id=uid)
    t.delete()
    messages.success(request, "Задача удалена")
    return redirect(reverse("tasks:list"))

def delete_task_by_tag(request, uid, tag_slug):
    print (tag_slug)
    t = TodoItem.objects.get(id=uid)
    t.delete()
    messages.success(request, "Задача удалена")
    print(58*"*")
    return_path = reverse("tasks:list")+"tag/"+tag_slug
    print(return_path)
    print(58*"*")
    return redirect(return_path)


class TaskListView(LoginRequiredMixin, ListView):
    model = TodoItem
    context_object_name = "tasks"
    template_name = "tasks/list.html"

    def get_queryset(self):
        u = self.request.user
        return u.tasks.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_tasks = self.get_queryset()
        tags = []
        for t in user_tasks:
            tags.append(list(t.tags.all()))
            context['tags'] = filter_tags(tags)
        return context


class TaskCreateView(View):
    def post(self, request, *args, **kwargs):
        form = TodoItemForm(request.POST)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.owner = request.user
            new_task.save()
            form.save_m2m()
            return redirect(reverse("tasks:list"))
        return render(request, "tasks/create.html", {"form": form})

    def get(self, request, *args, **kwargs):
        form = TodoItemForm()
        return render(request, "tasks/create.html", {"form": form})


class TaskDetailsView(DetailView):
    model = TodoItem
    template_name = 'tasks/details.html'


def tasks_import(request):
    if request.method == "POST":   #если был переход из формы
        board_id = (request.POST['board_id']) #получаем ID борда
        owner = request.user #получаем пользователя
        prof = Profile.objects.get(user=owner) #получаем профайл пользователя
        key = prof.trello_key #из профайла достаем ключ
        token = prof.trello_token #из профайла достаем токен
        delete_all(owner)
        task_list = get_tasks_from_trello(key, token, board_id) #получаем список тасок из Трелло

        for task in task_list: # сохраняем таски из списка в нашу базу
            import_task = TodoItem()
            import_task.description = task[0]
            import_task.trello_id = task[1]
            import_task.trello_board_id = task[2]
            import_task.owner  = owner
            import_task.save()

        return redirect(reverse("tasks:list"))

    else: #если перешли поссылке, то гененрируем форму
        return render(request, "tasks/import.html")
def delete_all(u):
    tasks = TodoItem.objects.filter(owner=u).all()
    for t in tasks:
        t.delete()

def get_tasks_from_trello(key, token, board_id): #возвращает список списков [имя,id,board_id]
    client = TrelloClient(api_key=key, api_secret=token)
    lists = client.list_boards(board_id)
    result = []
    for board in client.list_boards():
        if board.id == board_id:
            current_list = board.list_lists()[0]
            for card in current_list.list_cards():
                result.append([(str(card)).strip('<>'),card.id, board_id])
    return(result)


class TasksImportView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        form = TodoItemForm(request.POST)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.owner = request.user
            new_task.save()
            form.save_m2m()
            return redirect(reverse("tasks:list"))
        return render(request, "tasks/create.html", {"form": form})

    def get(self, request, *args, **kwargs):
        form = TodoItemForm()
        return render(request, "tasks/create.html", {"form": form})


class TaskEditView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        t = TodoItem.objects.get(id=pk)
        form = TodoItemForm(request.POST, instance=t)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.owner = request.user
            new_task.save()
            form.save_m2m()
            return redirect(reverse("tasks:list"))

        return render(request, "tasks/edit.html", {"form": form, "task": t})

    def get(self, request, pk, *args, **kwargs):
        t = TodoItem.objects.get(id=pk)
        form = TodoItemForm(instance=t)
        return render(request, "tasks/edit.html", {"form": form, "task": t})

class TaskExportView(LoginRequiredMixin, View):
    def generate_body(self, user, priorities):
        q = Q()
        if priorities["prio_high"]:
            q = q | Q(priority=TodoItem.PRIORITY_HIGH)
        if priorities["prio_med"]:
            q = q | Q(priority=TodoItem.PRIORITY_MEDIUM)
        if priorities["prio_low"]:
            q = q | Q(priority=TodoItem.PRIORITY_LOW)
        tasks = TodoItem.objects.filter(owner=user).filter(q).all()

        body = "Ваши задачи и приоритеты:\n"

        for t in list(tasks):
            tag_string ='Тэги: '
            for tt in t.tags.all():
                tag_string+=str(tt)+" "
            if t.is_completed:
                body += f"[x] {t.description} ({t.get_priority_display()}) \n {tag_string}\n \n"
            else:
                body += f"[ ] {t.description} ({t.get_priority_display()}) \n {tag_string}\n \n"

        return body

    def post(self, request, *args, **kwargs):
        form = TodoItemExportForm(request.POST)
        if form.is_valid():
            email = request.user.email
            body = self.generate_body(request.user, form.cleaned_data)
            send_mail("Задачи", body, settings.EMAIL_HOST_USER, [email])
            messages.success(
                request, "Задачи были отправлены на почту %s" % email)
        else:
            messages.error(request, "Что-то пошло не так, попробуйте ещё раз")
        return redirect(reverse("tasks:list"))

    def get(self, request, *args, **kwargs):
        form = TodoItemExportForm()
        return render(request, "tasks/export.html", {"form": form})


def tasks_by_tag(request, tag_slug=None):
    u = request.user
    tasks = TodoItem.objects.filter(owner=u).all()
    #print (tasks)

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        tasks = tasks.filter(tags__in=[tag])

    all_tags = []
    for t in tasks:
        all_tags.append(list(t.tags.all()))
    all_tags = filter_tags(all_tags)

    return render(
        request,
        "tasks/list_by_tag.html",
        {"tag": tag, "tasks": tasks, "all_tags": all_tags},
    )

def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    user_tasks = self.get_queryset()
    tags = []
    for t in user_tasks:
        tags.append(list(t.tags.all()))

    context['tags'] = filter_tags(tags)
    return context

def filter_tags(tags_by_task):
    filtered_tags = []
    for sub_tag in tags_by_task:
        for tag in sub_tag:
            if tag not in filtered_tags:
                filtered_tags.append(tag)

    return (filtered_tags)

def filter_tasks(tasks,tag):
    result = []
    for task in tasks:
        if tag in task['tags']:
            result.append(task["task_id"])
    return result
