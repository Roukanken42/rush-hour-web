from django.shortcuts import render
from django.http import HttpResponse

from django.contrib.auth import get_user_model
from django.db.models import *
from django.db import connection

import collections, itertools

User = get_user_model()

# Create your views here.

from .models import *

def levels(request):    
    levels = (
        Level.objects.all()
        .annotate(clears = Count("clear"))
        .order_by("points", "moves", "configurations")
    )

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

    

    if request.method == "GET":
        times = (
            User.objects.annotate(time = Min("clear__time", filter=Q(clear__level = level, clear__successful = True)))
            .exclude(time__isnull = True)
            .order_by("time")
        )

        moves = (
            User.objects.annotate(moves = Min("clear__moves", filter=Q(clear__level = level, clear__successful = True)))
            .exclude(moves__isnull = True)
            .order_by("moves")
        )

        levels = (
            Level.objects.all()
            .annotate(clears = Count("clear"))
            .order_by("points", "moves", "configurations")
            .filter(points__gte = level.points)
        )

        levels = itertools.chain(levels, itertools.cycle([None]))
        levels = itertools.dropwhile(lambda x: x is not None and x.id != level.id, levels)
        levels = itertools.islice(levels, 1, None)
        next_level = next(levels)

        return render(request, "puzzle/level.html", {"level": level, "times": times, "moves": moves, "next_level": next_level})

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


def namedTupleFetchall(cursor):
    desc = cursor.description
    nt_result = collections.namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def leaderboard(request):
    with connection.cursor() as cursor: 
        cursor.execute(
            """
            SELECT username, sum(points) as points, count(*) as levels FROM 
            (
                SELECT clear.user_id, user.username, clear.level_id, max(level.points) as points
                FROM puzzle_clear clear 
                INNER JOIN puzzle_level level ON level.id = level_id
                INNER JOIN auth_user user ON user.id = user_id
                WHERE successful = 1 
                GROUP BY user_id, level_id
            )   
            GROUP BY user_id
            ORDER BY points DESC
            """
        )

        users = namedTupleFetchall(cursor)
        # print(*users, sep="\n")

        return render(request, "puzzle/leaderboard.html", {"users": users})

    return render(request, "puzzle/leaderboard.html", {"users": []})

def index(request):
    return render(request, "puzzle/index.html", {})