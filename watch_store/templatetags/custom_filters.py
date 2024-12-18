from django import template

register = template.Library()

@register.filter
def make_groups(value, group_size):
    """
    Groups the input queryset or list into chunks of the given size.
    """
    group_size = int(group_size)
    return [value[i:i + group_size] for i in range(0, len(value), group_size)]
