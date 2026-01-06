from pathlib import Path
from django.conf import settings
from django.shortcuts import render
from django.http import Http404
import os
import re
from types import SimpleNamespace

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



# =========================
#  CONFIG
# =========================
# This points to: core/static/core/ruoh/environments
ENV_ROOT_STATIC = "core/ruoh/environments"
ENV_ROOT_FS = Path(settings.BASE_DIR) / "core" / "static" / ENV_ROOT_STATIC


# =========================
#  HELPERS
# =========================
def _parse_data_txt(path: str) -> dict:
    data = {}
    current_key = None
    in_block = False
    block_lines = []

    def flush_block():
        nonlocal current_key, in_block, block_lines
        if in_block and current_key:
            # preserve blank lines; strip only outer whitespace
            data[current_key] = "\n".join(block_lines).strip()
        in_block = False
        block_lines = []
        current_key = None

    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")

            # Ignore pure comment lines
            if line.strip().startswith("#"):
                continue

            # If we're inside a block, keep collecting until a new top-level key appears
            if in_block:
                if line and not line.startswith(" ") and ":" in line:
                    # new key starts, flush block first
                    flush_block()
                else:
                    # block content: remove one leading indent if present
                    block_lines.append(line[2:] if line.startswith("  ") else line)
                    continue

            s = line.strip()
            if not s:
                continue

            # list item (must belong to a current key)
            if s.startswith("- "):
                if current_key and current_key not in data:
                    data[current_key] = []
                if current_key and isinstance(data.get(current_key), list):
                    data[current_key].append(s[2:].strip())
                continue

            # key line
            if ":" in s:
                key, val = s.split(":", 1)
                key = key.strip()
                val = val.strip()

                current_key = key

                # block mode
                if val == "|":
                    in_block = True
                    block_lines = []
                    continue

                # normal scalar
                data[key] = val
                continue

    flush_block()
    return data



def _node_path(*parts) -> Path:
    return ENV_ROOT_FS.joinpath(*parts)


def _node_exists(*parts) -> bool:
    return _node_path(*parts).exists()


def _get_node(kind: str, rel_parts: list[str], slug: str) -> dict:
    """
    kind used only for defaults
    rel_parts points to the folder for the node
    slug is the folder name used for routing
    """
    folder = _node_path(*rel_parts)
    if not folder.exists():
        raise Http404(f"Missing env folder: {str(folder)}")

    data = _parse_data_txt(folder / "data.txt")
    name = data.get("name") or slug.replace("_", " ").replace("-", " ").title()

    # Static image path for templates: "core/ruoh/environments/....../main.png"
    static_base = f"{ENV_ROOT_STATIC}/" + "/".join(rel_parts)
    splash = f"{static_base}/main.png"

    return {
        "slug": slug,
        "name": name,
        "subtitle": data.get("subtitle", ""),
        "status": data.get("status", "ONLINE"),
        "type": data.get("type", kind.upper()),
        "logline": data.get("logline", ""),
        "bio": data.get("bio", ""),
        "notes": data.get("notes", []),
        "facts": data.get("facts", []),
        "splash": splash,
        "static_base": static_base,
        "raw": data,
    }


def _list_children(parent_parts: list[str], child_dirname: str) -> list[str]:
    """
    Returns folder names under parent/child_dirname.
    """
    base = _node_path(*parent_parts, child_dirname)
    if not base.exists():
        return []
    return sorted([p.name for p in base.iterdir() if p.is_dir()])


# =========================
#  VIEWS
# =========================
def env_index(request):
    # Worlds live directly under ENV_ROOT_FS
    world_slugs = sorted([p.name for p in ENV_ROOT_FS.iterdir() if p.is_dir()])

    worlds = []
    for w in world_slugs:
        node = _get_node("world", [w], w)
        # optional: count continents
        node["children"] = _list_children([w], "continents")
        worlds.append(node)

    return render(request, "core/ruoh_env_index.html", {"worlds": worlds})


def env_world(request, world):
    node = _get_node("world", [world], world)
    continent_slugs = _list_children([world], "continents")

    continents = []
    for c in continent_slugs:
        continents.append(_get_node("continent", [world, "continents", c], c))

    return render(
        request,
        "core/ruoh_env_world.html",
        {"world": node, "continents": continents},
    )


def env_continent(request, world, continent):
    node = _get_node("continent", [world, "continents", continent], continent)
    country_slugs = _list_children([world, "continents", continent], "countries")

    countries = []
    for co in country_slugs:
        countries.append(_get_node("country", [world, "continents", continent, "countries", co], co))

    return render(
        request,
        "core/ruoh_env_continent.html",
        {"world_slug": world, "continent": node, "countries": countries},
    )

ENV_ROOT = ENV_ROOT_FS

def _get_node(node_type, parts, slug):
    base_path = os.path.join(ENV_ROOT, *parts)
    data_path = os.path.join(base_path, "data.txt")

    data = parse_data_txt(data_path)

    # Make sure you always have these keys
    data.setdefault("slug", slug)
    data.setdefault("type", node_type.upper())
    data.setdefault("splash", os.path.join(*parts, "splash.jpg"))  # whatever your logic is

    return SimpleNamespace(**data)  # or dict, depending on your existing code


SECTION_KEYS = {
    "NAME": "name",
    "TYPE": "type",
    "SUBTITLE": "subtitle",
    "BIO": "bio",
    "OVERVIEW": "bio",         # allow OVERVIEW synonym
    "HISTORY": "history",
    "GEOGRAPHY": "geography",
    "CULTURE": "culture",
    "GOVERNMENT": "government",
    "ECONOMY": "economy",
    "NOTES": "notes",
}

def parse_data_txt(path: str) -> dict:
    """
    Parses a data.txt file with either:
      KEY: single line value
    or:
      KEY:
      multi-line until next KEY:
    """
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().replace("\r\n", "\n")

    # Match SECTION headers like "HISTORY:" at start of line.
    pattern = re.compile(r"^(?P<key>[A-Z_ ]+):[ \t]*?(?P<inline>.*)?$", re.MULTILINE)

    matches = list(pattern.finditer(raw))
    if not matches:
        return {}

    out = {}
    for i, m in enumerate(matches):
        key_raw = m.group("key").strip()
        inline = (m.group("inline") or "").strip()

        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        block = raw[start:end].strip("\n").strip()

        normalized_key = SECTION_KEYS.get(key_raw.replace(" ", "_"), None) or SECTION_KEYS.get(key_raw, None)
        if not normalized_key:
            # store unknown keys in a safe normalized form
            normalized_key = key_raw.lower().replace(" ", "_")

        value = inline if inline else block
        out[normalized_key] = value.strip()

    return out


def env_country(request, world, continent, country):
    node = _get_node("country", [world, "continents", continent, "countries", country], country)

    # Parse extra section fields from data.txt (History/Geography/Culture/etc.)
    base_path = os.path.join(ENV_ROOT, world, "continents", continent, "countries", country)
    data_path = os.path.join(base_path, "data.txt")
    data = parse_data_txt(data_path)

    # Attach fields onto node if it's an object-like node
    # (If node is a dict, swap these for node["history"] etc.)
    for k, v in data.items():
        setattr(node, k, v)

    # Locations
    location_slugs = _list_children([world, "continents", continent, "countries", country], "locations")
    locations = [
        _get_node("location", [world, "continents", continent, "countries", country, "locations", loc], loc)
        for loc in location_slugs
    ]

    # Provide a predictable section map for templates
    sections = {
        "overview": getattr(node, "bio", ""),
        "history": getattr(node, "history", ""),
        "geography": getattr(node, "geography", ""),
        "culture": getattr(node, "culture", ""),
        "government": getattr(node, "government", ""),
        "economy": getattr(node, "economy", ""),
        "notes": getattr(node, "notes", ""),
    }

    return render(
        request,
        "core/ruoh_env_country.html",
        {
            "world_slug": world,
            "continent_slug": continent,
            "country": node,
            "locations": locations,
            "sections": sections,
        },
    )



def env_location(request, world, continent, country, location):
    node = _get_node("location", [world, "continents", continent, "countries", country, "locations", location], location)

    return render(
        request,
        "core/ruoh_env_location.html",
        {
            "world_slug": world,
            "continent_slug": continent,
            "country_slug": country,
            "location": node,
        },
    )
