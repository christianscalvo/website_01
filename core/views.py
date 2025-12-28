from pathlib import Path
from django.conf import settings
from django.shortcuts import render
from django.http import Http404

def home(request):
    return render(request, "core/home.html")

def ruoh(request):
    return render(request, "core/series_ruoh.html")

def ruoh_chapter_01(request):
    return render(request, "core/ruoh_chapter_01.html")

def series_scott_pilgrim_ko(request):
    return render(request, "core/series_spko.html")

def fanart_gallery(request):
    # Static folder path where your images live
    fanart_dir = Path(settings.BASE_DIR) / "core" / "static" / "core" / "spko" / "Fanart"

    allowed_ext = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
    files = []

    if fanart_dir.exists():
        for p in sorted(fanart_dir.iterdir()):
            if p.is_file() and p.suffix.lower() in allowed_ext:
                # Store the relative path portion used by {% static %}
                files.append(f"core/spko/Fanart/{p.name}")

    context = {"fanart_files": files}
    return render(request, "core/spko_fanart_gallery.html", context)

def ruoh_characters(request):
    return render(request, "core/ruoh_characters.html")

def ruoh_environments(request):
    return render(request, "core/ruoh_environments.html")

def ruoh_lore(request):
    return render(request, "core/ruoh_lore.html")



from .character_archive import load_all_characters, load_character


def ruoh_characters(request):
    characters = load_all_characters()
    return render(request, "core/ruoh_characters.html", {"characters": characters})


def ruoh_character_detail(request, character_slug):
    character = load_character(character_slug)
    if not character:
        raise Http404("Character not found")
    return render(request, "core/ruoh_character_detail.html", {"c": character})