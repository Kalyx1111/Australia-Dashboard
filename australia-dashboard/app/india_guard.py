"""Shared India rule for every dashboard (identical copy in each project).

- India's survey outline is drawn in orange on every dashboard that shows India. Pakistan-administered Kashmir,
  Gilgit-Baltistan and Aksai Chin lie inside it, as part of India.
- Military sites inside that outline are not shown on dashboards other than North East India and J&K.
  Civil points (pipelines, ports, airports, power plants, cables and other non-military points) are shown.
- News, notes and inputs about India are never filtered.
"""
import json
import os
import re

from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
from shapely.prepared import prep

_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

MILITARY_CATS = {"air_base", "navy_base", "submarine_base", "cantonment", "missile_base", "us_base", "foreign_base",
                 "nuclear_site", "defense_industry", "defense_hq", "scs_outpost", "radar", "carrier_port",
                 "satellite_station", "military", "military_airfield", "naval_base", "division", "cyber_hub"}
NAME_MILITARY = re.compile(r"\b(air ?force|navy|naval|army|cantonment|garrison|military|missile|radar|defen[cs]e|"
                           r"regiment|brigade|barracks|submarine|test range|nuclear weapons?)\b", re.IGNORECASE)
_OVERLAY_TERM = re.compile(
    r"india|indian|kashmir|ladakh|aksai|arunachal|\bloc\b|\blac\b|siachen|sir creek|gilgit|jammu|assam|"
    r"sikkim|manipur|nagaland|mizoram|tripura|meghalaya|andaman|nicobar|lakshadweep|line of control|"
    r"line of actual control", re.IGNORECASE)
_CFG = None


def _outline():
    with open(os.path.join(_DATA, "india_survey_lonlat.json"), encoding="utf-8") as fh:
        rings = json.load(fh)["rings"]
    polys = [Polygon(ring).buffer(0) for ring in rings if len(ring) >= 3]
    return prep(unary_union([p for p in polys if not p.is_empty]))


_INDIA = _outline()


def _config():
    global _CFG
    if _CFG is None:
        try:
            with open(os.path.join(_DATA, "dashboard.json"), encoding="utf-8") as fh:
                _CFG = json.load(fh)
        except (OSError, ValueError):
            _CFG = {"mode": "clean"}
    return _CFG


def mode():
    return _config().get("mode", "clean")


def inside_india(lat, lon):
    """True when a point lies inside India's survey outline (Pakistan-administered Kashmir, Gilgit-Baltistan and Aksai Chin included)."""
    try:
        return _INDIA.contains(Point(float(lon), float(lat)))
    except (TypeError, ValueError):
        return False


def is_military(rec):
    if rec.get("cat") in MILITARY_CATS:
        return True
    return bool(NAME_MILITARY.search(str(rec.get("name") or "")))


def block_record(rec):
    """True for a map record that must not be shown: a military site inside India's outline (not in focus dashboards)."""
    if not isinstance(rec, dict) or mode() == "focus":
        return False
    lat = rec.get("lat", rec.get("latitude"))
    lon = rec.get("lon", rec.get("lng", rec.get("longitude")))
    if lat is None or lon is None or not inside_india(lat, lon):
        return False
    return is_military(rec)


def clean_points(obj):
    """Removes military map records inside the outline, wherever they sit (lists, categories, dicts)."""
    if isinstance(obj, dict):
        if "lat" in obj or "latitude" in obj:
            return obj
        return {k: (clean_points(v) if isinstance(v, (list, dict)) else v) for k, v in obj.items()}
    if isinstance(obj, list):
        out = []
        for item in obj:
            if isinstance(item, dict) and block_record(item):
                continue
            out.append(clean_points(item) if isinstance(item, (list, dict)) else item)
        return out
    return obj


def clean_overlay(items):
    """Drops Kashmir, Ladakh, Aksai Chin and other India-related overlay lines (clean dashboards only)."""
    kept = []
    for it in items:
        if isinstance(it, dict):
            text = " ".join(v for k, v in it.items() if isinstance(v, str) and k not in ("d", "color", "colour", "style"))
        else:
            text = it if isinstance(it, str) else ""
        if not _OVERLAY_TERM.search(text):
            kept.append(it)
    return kept
