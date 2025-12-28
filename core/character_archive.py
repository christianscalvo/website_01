from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Optional

from django.contrib.staticfiles import finders


@dataclass(frozen=True)
class CharacterRecord:
    slug: str
    static_base: str  # e.g. "core/characters/scio-calavera"
    name: str
    nickname: str
    bio: str
    abilities: List[Tuple[str, str]]   # (ability_name, ability_desc)
    details: List[str]
    thumb: str
    splash: str                        # static path to main.png
    gallery: List[str]                 # static paths to other images


def _find_characters_root() -> Path:
    """
    Locate the filesystem directory for static 'core/characters'.
    Works with Django staticfiles finders (dev + collectstatic environments).
    """
    # We look for a file we expect could exist inside that directory.
    # If you always have at least one character folder, this will work.
    # If not, we fall back to finding the directory via a known marker.
    root = finders.find("core/characters")
    if root:
        return Path(root)

    # If finders can't return a directory, try finding a known file.
    # This requires at least one character to exist and have data.txt.
    maybe = finders.find("core/characters/.keep")
    if maybe:
        return Path(maybe).parent

    raise FileNotFoundError(
        "Could not locate static directory 'core/characters'. "
        "Ensure it exists under core/static/core/characters."
    )


def _parse_block(lines: List[str]) -> List[str]:
    out = []
    for line in lines:
        line = line.rstrip("\n")
        if line.strip() == "END":
            break
        out.append(line)
    return out


def parse_data_txt(text: str) -> Dict[str, object]:
    """
    Parses the custom data.txt format described above.
    """
    raw_lines = text.splitlines(True)
    i = 0

    name = ""
    nickname = ""
    bio_lines: List[str] = []
    abilities: List[Tuple[str, str]] = []
    details: List[str] = []

    def read_block(start_index: int) -> Tuple[List[str], int]:
        block_lines = []
        j = start_index
        while j < len(raw_lines):
            s = raw_lines[j].rstrip("\n")
            if s.strip() == "END":
                return block_lines, j + 1
            block_lines.append(s)
            j += 1
        return block_lines, j

    while i < len(raw_lines):
        line = raw_lines[i].rstrip("\n").strip()
        i += 1

        if not line:
            continue

        if line.startswith("NAME:"):
            name = line.split("NAME:", 1)[1].strip().strip('"')
            continue

        if line.startswith("NICKNAME:"):
            nickname = line.split("NICKNAME:", 1)[1].strip().strip('"')
            continue

        if line == "BIO:":
            block, i = read_block(i)
            bio_lines = block
            continue

        if line == "ABILITIES:":
            block, i = read_block(i)
            for b in block:
                b = b.strip()
                if not b.startswith("-"):
                    continue
                item = b[1:].strip()
                if " | " in item:
                    a_name, a_desc = item.split(" | ", 1)
                else:
                    a_name, a_desc = item, ""
                abilities.append((a_name.strip(), a_desc.strip()))
            continue

        if line == "DETAILS:":
            block, i = read_block(i)
            for b in block:
                b = b.strip()
                if b.startswith("-"):
                    details.append(b[1:].strip())
                elif b:
                    details.append(b)
            continue

    return {
        "name": name,
        "nickname": nickname,
        "bio": "\n".join([x for x in bio_lines if x.strip()]).strip(),
        "abilities": abilities,
        "details": details,
    }


def load_all_characters() -> List[CharacterRecord]:
    root = _find_characters_root()

    records: List[CharacterRecord] = []
    if not root.exists():
        return records

    for folder in sorted([p for p in root.iterdir() if p.is_dir()]):
        slug = folder.name
        static_base = f"core/characters/{slug}"

        data_path = folder / "data.txt"
        splash_path = folder / "main.png"

        if not data_path.exists():
            # Skip folders that don't match the contract
            continue

        data = parse_data_txt(data_path.read_text(encoding="utf-8", errors="replace"))

        # Gallery: all images except main.png
        exts = {".png", ".jpg", ".jpeg", ".webp"}
        images = [
            p for p in folder.iterdir()
            if p.is_file() and p.suffix.lower() in exts
        ]
        gallery_files = []
        for p in sorted(images):
            if p.name.lower() == "main.png":
                continue
            gallery_files.append(f"{static_base}/{p.name}")

        # Fallback if main.png missing (still let the page render)
        splash_static = f"{static_base}/main.png"
        thumb_static = f"{static_base}/thumb.png"

        records.append(
            CharacterRecord(
                slug=slug,
                static_base=static_base,
                name=str(data.get("name") or slug.replace("-", " ").title()),
                nickname=str(data.get("nickname") or ""),
                bio=str(data.get("bio") or ""),
                abilities=list(data.get("abilities") or []),
                details=list(data.get("details") or []),
                splash=splash_static,
                thumb=thumb_static,
                gallery=gallery_files,
            )
        )

    return records


def load_character(slug: str) -> Optional[CharacterRecord]:
    for c in load_all_characters():
        if c.slug == slug:
            return c
    return None
