from django.utils.safestring import mark_safe
from django.template import Library

import json

register = Library()

@register.filter(is_safe=True)
def safe(obj):
    return mark_safe(obj)

@register.filter('startswith')
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False

@register.filter()
def to_int(value):
    return int(value)

@register.filter()
def divide(value, x):
    return value / x