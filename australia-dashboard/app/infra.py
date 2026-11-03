"""Loads the real infrastructure layers from data/*.json (generated from
verified open datasets - see README for each source). Every item keeps its
own `source`, shown in the map tooltip. Missing files degrade to an empty
layer (never a crash), and the snapshot reports the counts so an empty layer
is visible rather than silently broken."""
from __future__ import annotations
try:
    from .india_guard import block_record as _india_block
except ImportError:  # run as a plain script
    from india_guard import block_record as _india_block
import json
import logging
import os

log = logging.getLogger("infra")
_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
LAYER_FILES = ["airports_region.json", "military_airfields_region.json", "seaports_region.json", "nuclear_plants_region.json"]


def load_infra() -> list[dict]:
    out = []
    for fn in LAYER_FILES:
        path = os.path.join(_DATA, fn)
        try:
            with open(path, "r", encoding="utf-8") as f:
                items = json.load(f)
            for it in items:
                if not all(k in it for k in ("id", "name", "lat", "lon", "cat", "source")):
                    continue
                if not (-90 <= float(it["lat"]) <= 90 and -180 <= float(it["lon"]) <= 180):
                    continue
                if not _india_block(it): out.append(dict(it, linked_items=[]))
        except (OSError, json.JSONDecodeError) as e:
            log.warning("infrastructure layer %s unavailable: %s", fn, e)
    return out


INFRA_MARKERS = load_infra()


# permanent-data updates join the layers here (military sites inside India's outline are never added outside focus dashboards)
from . import updates as _updates  # noqa: E402
try:
    from .static_markers import MARKERS as _DEDUPE_STATIC
except ImportError:
    _DEDUPE_STATIC = []
_BASE_INFRA_COUNT = len(INFRA_MARKERS)


def _merge_update_records():
    INFRA_MARKERS[_BASE_INFRA_COUNT:] = _updates.load_records(list(_DEDUPE_STATIC) + INFRA_MARKERS[:_BASE_INFRA_COUNT])


_updates.on_update(_merge_update_records)
_merge_update_records()
