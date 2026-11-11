"""The Markdown documents a session writes outside the work folders: `docs/` and `.audit/`.

Read-only. The caller names a path taken from the listing, never one of its own: a path
is served only when the same scan finds it, so nothing outside these folders can be read.
"""

from __future__ import annotations

from pathlib import Path

from .reports import split_front_matter

DOC_FOLDERS = ("docs", ".audit")
MAX_DOCS = 300
MAX_DOC_CHARS = 200_000


def _read(path: Path) -> str | None:
    try:
        return path.read_text(errors="replace")
    except OSError:
        return None


def _title(text: str, fallback: str) -> str:
    _, body = split_front_matter(text)
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip() or fallback
    return fallback


def _scan(root: Path) -> list[Path]:
    """Every Markdown file of the document folders that really lives under the root, newest first."""
    root = Path(root)
    real_root = root.resolve()
    found = []
    for folder in DOC_FOLDERS:
        try:
            candidates = list((root / folder).rglob("*.md"))
        except OSError:
            continue
        for path in candidates:
            try:
                real = path.resolve()
                if path.is_file() and real_root in real.parents:
                    found.append((real.stat().st_mtime, path))
            except OSError:
                continue
    found.sort(key=lambda item: (-item[0], str(item[1])))
    return [path for _, path in found[:MAX_DOCS]]


def list_docs(root: Path) -> list[dict]:
    root = Path(root)
    out = []
    for path in _scan(root):
        text = _read(path)
        if text is None:
            continue
        out.append({
            "path": path.relative_to(root).as_posix(),
            "title": _title(text, path.stem),
            "mtime": path.stat().st_mtime,
            "size": len(text),
        })
    return out


def read_doc(root: Path, rel: str) -> dict | None:
    """One document of the listing, by its listed path; None when it is not listed."""
    root = Path(root)
    for path in _scan(root):
        if path.relative_to(root).as_posix() != rel:
            continue
        text = _read(path)
        if text is None:
            return None
        front, body = split_front_matter(text)
        return {
            "path": rel, "title": _title(text, path.stem), "mtime": path.stat().st_mtime,
            "front": front, "body": body[:MAX_DOC_CHARS], "truncated": len(body) > MAX_DOC_CHARS,
        }
    return None
