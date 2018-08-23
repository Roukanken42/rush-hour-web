from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("levels/", views.levels, name="level_list"),
    path("levels/<int:level_id>/", views.level, name="level"),
    path("leaderboard", views.leaderboard, name="leaderboard"),
]