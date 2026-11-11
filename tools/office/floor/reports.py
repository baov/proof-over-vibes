"""Read what the roles write: report front-matter and the run brief."""

from __future__ import annotations

import re

DEFAULT_LIMIT = 5

_COUNTER = re.compile(r"iteration(?:s| counter)?:?\s*(\d+)", re.IGNORECASE)
_LIMIT = re.compile(r"limit\D{0,3}(\d+)", re.IGNORECASE)


def split_front_matter(text: str) -> tuple[dict[str, str], str]:
    """Return (front-matter pairs, body) of a report.

    A missing or unclosed `---` block gives ({}, text): a file caught while it is written.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    pairs: dict[str, str] = {}
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return pairs, "\n".join(lines[index + 1:])
        key, sep, value = line.partition(":")
        if sep:
            pairs[key.strip()] = value.strip()
    return {}, text


def parse_front_matter(text: str) -> dict[str, str]:
    """Return the `key: value` pairs of a leading `---` block, {} when it is missing or unclosed."""
    return split_front_matter(text)[0]


def parse_brief(text: str) -> tuple[int, int]:
    """Return (iteration, limit) from a brief, defaulting to (0, 5)."""
    counter = _COUNTER.search(text)
    limit = _LIMIT.search(text)
    return (
        int(counter.group(1)) if counter else 0,
        int(limit.group(1)) if limit else DEFAULT_LIMIT,
    )
