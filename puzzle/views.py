from django.shortcuts import render
from django.http import HttpResponse

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Min, Max, Q

import collections

User = get_user_model()

# Create your views here.

from .models import *

def levels(request):    
    levels = Level.objects.all().annotate(clears = Count("clear")).order_by("points", "moves", "configurations")

    if request.user.is_authenticated:
        level_dict = {level.id: level for level in levels}

        clears = Clear.objects.all().filter(user = request.user, successful=True).order_by("-date")

        for clear in clears:
            if clear.level.id in level_dict:
                level_dict[clear.level.id].clear = clear

    users = User.objects.count()

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

    
    times = User.objects.annotate(time = Min("clear__time", filter=Q(clear__level = level, clear__successful = True))).exclude(time__isnull = True)
    moves = User.objects.annotate(moves = Min("clear__moves", filter=Q(clear__level = level, clear__successful = True))).exclude(moves__isnull = True)

    if request.method == "GET":
        return render(request, "puzzle/level.html", {"level": level, "times": times, "moves": moves})

    if request.method == "POST":
        if not request.user.is_authenticated:
            raise Http403("You must be logged in !")
        
        else:
            data = request.POST.get("data", "")
            dataJson = json.loads(data)
            
            moves = sum(1 if move["min"] != move["max"] else 0 for move in dataJson)

            time = int(request.POST.get("time", "-1"))
            time = datetime.timedelta(milliseconds=time)

            won = True if request.POST.get("won", "") == "true" else False

            clear = Clear(level = level, user = request.user, data = data, moves = moves, time = time, successful = won)
            clear.save()

            level.recalcPoints()
            level.save() 

            return HttpResponse()



def leaderboard(request):
    users = User.objects.annotate(points = Sum("clear__level__points"), levels = Count("clear__level")).exclude(levels = 0).order_by("-points", "-levels")

    return render(request, "puzzle/leaderboard.html", {"users": users})

def index(request):
    return render(request, "puzzle/index.html", {})