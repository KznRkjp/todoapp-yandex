from django import template
#from tasks.models import TodoItem
register = template.Library()

@register.simple_tag
def not_completed(tasks):
    return len(tasks.filter(is_completed = False).all())
