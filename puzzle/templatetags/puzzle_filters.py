from django.utils.safestring import mark_safe
from django.template import Library

import json, math

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

@register.filter()
def duration(td, decimals = 0):
    decimals = int(decimals)

    total = round(td.total_seconds() * (10 ** decimals)) / (10 ** decimals)

    mins = int(total // 60) 
    sec = int(total % 60)
    rest = int(total % 1 * (10 ** decimals))

    return f"{mins}:{sec:02}" + ("" if decimals <= 0 else f".{rest:0{decimals}}")