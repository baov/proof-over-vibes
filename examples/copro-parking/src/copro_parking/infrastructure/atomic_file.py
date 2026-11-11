"""Atomic file write shared by the JSON adapters (ADR-0002)."""
import os
import tempfile
from pathlib import Path


def write_atomically(path: Path, text: str) -> None:
    """Write `text` to a temporary file, then replace `path` in one step."""
    handle, temporary = tempfile.mkstemp(
        dir=path.parent, prefix=path.name, suffix=".tmp")
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.replace(temporary, path)
    except BaseException:
        if os.path.exists(temporary):
            os.unlink(temporary)
        raise
