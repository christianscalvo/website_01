from pathlib import Path
from django.conf import settings
from django.shortcuts import render
from django.http import Http404
import os
import re

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


import os
from django.conf import settings
from django.http import Http404
from django.shortcuts import render

# Points to: core/static/core/ruoh/comic
def _ruoh_comic_root():
    # settings.BASE_DIR / "core" / "static" / "core" / "ruoh" / "comic"
    return os.path.join(settings.BASE_DIR, "core", "static", "core", "ruoh", "comic")

def ruoh_comic_archive(request):
    root = _ruoh_comic_root()
    if not os.path.isdir(root):
        raise Http404("Comic folder not found.")

    # comic books = folders inside comic root, excluding "covers"
    comic_slugs = []
    for name in sorted(os.listdir(root)):
        full = os.path.join(root, name)
        if os.path.isdir(full) and name != "covers":
            comic_slugs.append(name)

    comics = []
    for slug in comic_slugs:
        book_path = os.path.join(root, slug)
        chapters = []
        for ch in sorted(os.listdir(book_path)):
            ch_path = os.path.join(book_path, ch)
            if os.path.isdir(ch_path):
                chapters.append(ch)

        comics.append({
            "slug": slug,
            "title": slug.replace("-", " ").upper(),
            "chapter_count": len(chapters),
            # optional per-book cover (if exists)
            "cover": f"core/ruoh/comic/covers/{slug}.png",
            "chapters": chapters,
        })

    return render(request, "core/ruoh_comic_archive.html", {"comics": comics})


def ruoh_comic_book(request, comic_slug):
    root = _ruoh_comic_root()
    book_path = os.path.join(root, comic_slug)
    if not os.path.isdir(book_path):
        raise Http404("Comic book not found.")

    chapters = []
    for ch in sorted(os.listdir(book_path)):
        ch_path = os.path.join(book_path, ch)
        if os.path.isdir(ch_path):
            chapters.append({
                "slug": ch,
                "title": ch.replace("-", " ").upper(),
                "url": f"/series/research-unit-of-horrors/comic/{comic_slug}/{ch}/",
            })

    ctx = {
        "comic_slug": comic_slug,
        "comic_title": comic_slug.replace("-", " ").upper(),
        "chapters": chapters,
        "cover": f"core/ruoh/comic/covers/{comic_slug}.png",
    }
    return render(request, "core/ruoh_comic_book.html", ctx)

def _natural_key(s: str):
    # "page_2.png" < "page_10.png"
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

def ruoh_comic_reader(request, comic_slug, chapter_slug):
    root = _ruoh_comic_root()
    chapter_root = os.path.join(root, comic_slug, chapter_slug)
    if not os.path.isdir(chapter_root):
        raise Http404("Chapter not found.")

    # Expect subfolders:
    # core/static/core/ruoh/comic/<comic>/<chapter>/desktop/
    # core/static/core/ruoh/comic/<comic>/<chapter>/webtoon/
    requested_mode = (request.GET.get("mode") or "").strip().lower()
    if requested_mode not in {"desktop", "webtoon"}:
        requested_mode = "desktop"

    # Optional: auto-prefer webtoon for mobile-like UAs (remove if you only want CSS/JS switching)
    ua = (request.META.get("HTTP_USER_AGENT") or "").lower()
    if "mobile" in ua and request.GET.get("mode") is None:
        requested_mode = "webtoon"

    exts = (".png", ".jpg", ".jpeg", ".webp")

    def collect_pages(mode: str):
        folder = os.path.join(chapter_root, mode)
        if not os.path.isdir(folder):
            return []
        fns = [fn for fn in os.listdir(folder) if fn.lower().endswith(exts)]
        fns.sort(key=_natural_key)
        # paths must be relative to STATIC root for {% static p %}
        return [f"core/ruoh/comic/{comic_slug}/{chapter_slug}/{mode}/{fn}" for fn in fns]

    pages = collect_pages(requested_mode)

    # Fallback logic so you don't 404 if one folder isn't made yet
    if not pages:
        fallback = "desktop" if requested_mode == "webtoon" else "webtoon"
        pages = collect_pages(fallback)
        if pages:
            requested_mode = fallback

    if not pages:
        raise Http404("No pages found in chapter (desktop/ or webtoon/).")

    ctx = {
        "comic_slug": comic_slug,
        "chapter_slug": chapter_slug,
        "comic_title": comic_slug.replace("-", " ").upper(),
        "chapter_title": chapter_slug.replace("-", " ").upper(),
        "pages": pages,
        "mode": requested_mode,  # template uses this
    }
    return render(request, "core/ruoh_comic_reader.html", ctx)

def about(request):
    return render(request, "core/about.html")


from .blog_loader import get_post_by_slug, load_posts


def blog_index(request):
    posts = load_posts()
    return render(request, "core/blog_index.html", {"posts": posts})


def blog_detail(request, slug: str):
    post = get_post_by_slug(slug)
    if not post:
        raise Http404("Post not found")
    return render(request, "core/blog_detail.html", {"post": post})