from django.contrib import admin
from django.db.models import Count

from .models import *

# Register your models here.

def recalc_points(modeladmin, request, queryset):
    for level in queryset.annotate(clears = Count("clear__user", distinct=True)):
        print(level, level.clears)
        level.recalcPoints()
        level.save()


class LevelAdmin(admin.ModelAdmin):
    list_display = ["name", "moves", "configurations", "points"]
    ordering = ["points", "moves", "configurations"]
    actions = [recalc_points]

class ClearAdmin(admin.ModelAdmin):
    list_display = ["level", "user", "date", "successful", "moves", "time"]

admin.site.register(Level, LevelAdmin)
admin.site.register(Clear, ClearAdmin)
