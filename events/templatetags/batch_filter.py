from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def batch(iterable, n):
    """
    Batch items in a list into chunks of size n.
    Usage: {% for batch in items|batch:3 %}...{% endfor %}
    """
    if not iterable:
        return []
    
    # Convert to list if it's a QuerySet or other iterable
    try:
        iterable_list = list(iterable)
    except:
        return []
        
    result = []
    for i in range(0, len(iterable_list), n):
        result.append(iterable_list[i:i+n])
    return result

@register.filter
def add(list1, list2):
    """
    Add two lists or querysets together
    Usage: {% with combined=list1|add:list2 %}...{% endwith %}
    """
    try:
        result = list(list1) + list(list2)
        return result
    except:
        return [] 