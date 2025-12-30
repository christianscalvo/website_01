from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import markdown


@dataclass(frozen=True)
class BlogPost:
    title: str
    slug: str
    date: date
    excerpt: str
    cover: str | None
    tags: list[str]
    html: str
    source_path: Path


POSTS_DIR = Path(__file__).resolve().parent / "blog_posts"


def _parse_front_matter(raw: str) -> tuple[dict[str, str], str]:
    """
    Minimal front-matter parser:
    Expects:
    ---
    key: value
    ...
    ---
    """
    raw = raw.lstrip()
    if not raw.startswith("---"):
        return {}, raw

    lines = raw.splitlines()
    if len(lines) < 3:
        return {}, raw

    # find second --- delimiter
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return {}, raw

    header_lines = lines[1:end_idx]
    body_lines = lines[end_idx + 1 :]

    meta: dict[str, str] = {}
    for line in header_lines:
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()

    return meta, "\n".join(body_lines).lstrip()


def _parse_date(s: str) -> date:
    # expects YYYY-MM-DD
    return datetime.strptime(s, "%Y-%m-%d").date()


def _split_tags(s: str) -> list[str]:
    if not s:
        return []
    return [t.strip() for t in s.split(",") if t.strip()]


def load_posts() -> list[BlogPost]:
    if not POSTS_DIR.exists():
        return []

    posts: list[BlogPost] = []
    for md_path in POSTS_DIR.glob("*.md"):
        raw = md_path.read_text(encoding="utf-8")
        meta, body = _parse_front_matter(raw)

        title = meta.get("title", md_path.stem)
        slug = meta.get("slug", md_path.stem)
        excerpt = meta.get("excerpt", "")
        cover = meta.get("cover") or None
        tags = _split_tags(meta.get("tags", ""))

        d = meta.get("date")
        post_date = _parse_date(d) if d else date.today()

        html = markdown.markdown(
            body,
            extensions=["fenced_code", "tables", "toc"],
            output_format="html5",
        )

        posts.append(
            BlogPost(
                title=title,
                slug=slug,
                date=post_date,
                excerpt=excerpt,
                cover=cover,
                tags=tags,
                html=html,
                source_path=md_path,
            )
        )

    # newest first
    posts.sort(key=lambda p: p.date, reverse=True)
    return posts


def get_post_by_slug(slug: str) -> BlogPost | None:
    for p in load_posts():
        if p.slug == slug:
            return p
    return None
