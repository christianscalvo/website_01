# core/urls.py
from django.urls import path
from . import views
from .views import blog_detail, blog_index


urlpatterns = [
    path("", views.home, name="home"),
    path("series/research-unit-of-horrors/", views.ruoh, name="ruoh"),

    path("series/scott-pilgrim-ko/", views.series_scott_pilgrim_ko, name="spko"),
    path("spko/fanart/", views.fanart_gallery, name="fanart_gallery"),
    path("series/research-unit-of-horrors/comic/chapter-01/", views.ruoh_chapter_01, name="ruoh_chapter_01"),
    path("series/research-unit-of-horrors/explore/characters/", views.ruoh_characters, name="ruoh_characters"),
    path("series/research-unit-of-horrors/explore/environments/", views.ruoh_environments, name="ruoh_environments"),
    path("series/research-unit-of-horrors/explore/lore/", views.ruoh_lore, name="ruoh_lore"),
    path("series/research-unit-of-horrors/explore/characters/", views.ruoh_characters,name="ruoh_characters",),
    path("series/research-unit-of-horrors/explore/characters/<slug:character_slug>/", views.ruoh_character_detail, name="ruoh_character_detail",),
    path("series/research-unit-of-horrors/comic/", views.ruoh_comic_archive, name="ruoh_comic_archive"),
    path("series/research-unit-of-horrors/comic/<slug:comic_slug>/", views.ruoh_comic_book, name="ruoh_comic_book"),
    path("series/research-unit-of-horrors/comic/<slug:comic_slug>/<slug:chapter_slug>/", views.ruoh_comic_reader, name="ruoh_comic_reader"),
    path("about/", views.about, name="about"),
    path("linktree/", views.linktree, name="linktree"),

    path("blog/", blog_index, name="blog_index"),
    path("blog/<slug:slug>/", blog_detail, name="blog_detail"),
    path("ruoh/environments/", views.env_index, name="ruoh_env_index"),
    path("ruoh/environments/<slug:world>/", views.env_world, name="ruoh_env_world"),
    path("ruoh/environments/<slug:world>/<slug:continent>/", views.env_continent, name="ruoh_env_continent"),
    path("ruoh/environments/<slug:world>/<slug:continent>/<slug:country>/", views.env_country, name="ruoh_env_country"),
    path("ruoh/environments/<slug:world>/<slug:continent>/<slug:country>/<slug:location>/", views.env_location, name="ruoh_env_location"),
]
