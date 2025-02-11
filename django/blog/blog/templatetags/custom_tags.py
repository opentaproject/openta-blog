from django import template

register = template.Library()

@register.simple_tag
def increment(value, increment_by=1):
    return value + increment_by
