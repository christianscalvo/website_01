# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("series/research-unit-of-horrors/", views.ruoh, name="ruoh"),
    path("series/scott-pilgrim-ko/", views.series_scott_pilgrim_ko, name="spko"),

    path("series/research-unit-of-horrors/comic/chapter-01/", views.ruoh_chapter_01, name="ruoh_chapter_01"),
]
