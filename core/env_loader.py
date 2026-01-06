# env_loader.py
from dataclasses import dataclass
from pathlib import Path
from django.conf import settings

@dataclass
class EnvNode:
    world: str
    path: str            # "aeternicht/earlsian-kingdom"
    slug: str            # last segment
    name: str
    type: str            # World/Continent/Country/Location
    subtitle: str
    summary: str
    tags: list[str]
    facts: list[str]
    sections: list[tuple[str, str]]  # [("History","..."), ...]
    splash: str          # "core/ruoh/environments/surface/aeternicht/main.png"
    children: list[dict] # minimal info for cards

def _static_roots():
    roots = []
    for p in getattr(settings, "STATICFILES_DIRS", []):
        roots.append(Path(p))
    # include STATIC_ROOT as fallback (useful in production)
    if getattr(settings, "STATIC_ROOT", None):
        roots.append(Path(settings.STATIC_ROOT))
    return [r for r in roots if r.exists()]

def _base_folder():
    return Path("core/ruoh/environments")

def load_env_node(world: str, node_path: str = "") -> EnvNode:
    # folder on disk
    rel = _base_folder() / world / node_path
    folder = None
    for root in _static_roots():
        candidate = root / rel
        if candidate.exists():
            folder = candidate
            break
    if folder is None:
        raise FileNotFoundError(f"Missing env folder: {rel}")

    # required files
    data_file = folder / "data.txt"
    splash_file = folder / "main.png"
    if not data_file.exists():
        raise FileNotFoundError(f"Missing data.txt in {rel}")
    if not splash_file.exists():
        raise FileNotFoundError(f"Missing main.png in {rel}")

    data = parse_data_txt(data_file.read_text(encoding="utf-8"))

    # children detection (direct subfolders only)
    children = []
    for child in folder.iterdir():
        if not child.is_dir():
            continue
        if (child / "data.txt").exists() and (child / "main.png").exists():
            child_rel = str((_base_folder() / world / node_path / child.name).as_posix()).strip("/")
            # build url path part AFTER world
            child_path_after_world = (Path(node_path) / child.name).as_posix() if node_path else child.name
            children.append({
                "slug": child.name,
                "name": data_peek_name(child / "data.txt") or child.name.replace("-", " ").title(),
                "subtitle": data_peek_subtitle(child / "data.txt") or "",
                "url": f"/ruoh/environments/{world}/{child_path_after_world}/",
                "thumb": f"core/ruoh/environments/{world}/{child_path_after_world}/main.png",
            })

    splash_static = str((rel / "main.png").as_posix())  # "core/ruoh/environments/..."
    # IMPORTANT: rel already begins with "core/..." so it's usable in {% static %}

    return EnvNode(
        world=world,
        path=node_path,
        slug=(Path(node_path).name if node_path else world),
        name=data.get("name", world.title()),
        type=data.get("type", infer_type_from_depth(node_path)),
        subtitle=data.get("subtitle", ""),
        summary=data.get("summary", ""),
        tags=data.get("tags", []),
        facts=data.get("facts", []),
        sections=data.get("sections", []),
        splash=splash_static,
        children=sorted(children, key=lambda c: c["name"].lower()),
    )


def build_crumbs(world, node_path):
    crumbs = [{"name": world.replace("-", " ").title(), "url": f"/ruoh/environments/{world}/"}]
    if not node_path:
        return crumbs
    parts = node_path.split("/")
    running = ""
    for p in parts:
        running = f"{running}/{p}".strip("/")
        crumbs.append({"name": p.replace("-", " ").title(), "url": f"/ruoh/environments/{world}/{running}/"})
    return crumbs
