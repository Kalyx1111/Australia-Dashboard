"""Links live news items to static map markers by substring name match -
this is how "located news = colored dot" is decided, honestly: a real
text match against real place names, not invented per-article coordinates."""
from __future__ import annotations
from .static_markers import MARKERS


def match_location(text: str) -> dict | None:
    t = text.lower()
    for m in MARKERS:
        for alias in m["aliases"]:
            if alias in t:
                return m
    return None


def attach_live_items(items: list[dict]) -> list[dict]:
    """Returns the static markers list, each with a `linked_items` field
    populated from any live items whose text matched that location - used
    for the map tooltip's 'recent related items' section."""
    markers = [dict(m, linked_items=[]) for m in MARKERS]
    by_id = {m["id"]: m for m in markers}
    for it in items:
        m = match_location(it.get("text", "") or it.get("label", ""))
        if m:
            by_id[m["id"]]["linked_items"].append(it)
    return markers
