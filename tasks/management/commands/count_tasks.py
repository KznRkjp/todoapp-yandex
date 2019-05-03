from django.core.management import BaseCommand

from tasks.models import TodoItem


class Command(BaseCommand):
    help = u"Print total completed tasks"

    def add_arguments(self, parser):
        parser.add_argument(
            '--warning-days', dest='warn_days', type=int, default=5)

    def handle(self, *args, **options):
        user_dic = {}
        for u in TodoItem.objects.filter(is_completed=False):
        #for u in TodoItem.objects.all():
            print (u.pk)
            if u.owner in user_dic:
                user_dic[u.owner]+=1
            else:
                user_dic[u.owner] = 1
                #for t in u.owner:
        print (sorted(user_dic, key=user_dic.__getitem__))
        print(user_dic)

        #total = 0
        #for t in TodoItem.objects.filter(is_completed=True):
        #    total+=1
        #print("Всего выполнено: ", total)
