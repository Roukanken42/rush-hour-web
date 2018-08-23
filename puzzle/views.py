from django.shortcuts import render
from django.http import HttpResponse

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum

import collections

User = get_user_model()

# Create your views here.

from .models import *

def levels(request):    
    levels = Level.objects.all().annotate(clears = Count("clear")).order_by("-clears", "moves", "configurations")

    if request.user.is_authenticated:
        level_dict = {level.id: level for level in levels}

        clears = Clear.objects.all().filter(user = request.user).order_by("-date")

        for clear in clears:
            if clear.level.id in level_dict:
                level_dict[clear.level.id].clear = clear

    users = User.objects.count()

    # for level in levels:
        # level.progress = 100 - level.clears / users * 95


    return render(
        request,
        "puzzle/level_list.html",
        {"levels": list(levels)}
    )

def level(request, level_id):
    try:
        level = Level.objects.get(id = level_id)
    except Level.DoesNotExist:
        raise Http404("Level does not exist")

    if request.method == "GET":
        return render(request, "puzzle/level.html", {"level": level})

    if request.method == "POST":
        data = request.POST.get("data", "")

        if not request.user.is_authenticated:
            raise Http403("You must be logged in !")

        try:
            Clear.objects.get(level = level, user = request.user)
            raise Http403("Already cleared")

        except Clear.DoesNotExist:
            clear = Clear(level = level, user = request.user, data = data)
            clear.save()

            level.recalcPoints()
            level.save() 

            return HttpResponse()


def leaderboard(request):
    users = User.objects.annotate(points = Sum("clear__level__points"), levels = Count("clear__level")).exclude(levels = 0).order_by("-points", "-levels")

    return render(request, "puzzle/leaderboard.html", {"users": users})

def index(request):
    return render(request, "puzzle/index.html", {})