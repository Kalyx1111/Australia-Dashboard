"""USGS earthquakes - free, no key. Bbox covers the 17 Middle East states and their 100 km margin."""
from __future__ import annotations
from .base import Item, ConnectorResult

NAME = "usgs"
ENDPOINT = "https://earthquake.usgs.gov/fdsnws/event/1/query"


def configured() -> bool:
    return True


def fetch(min_mag: float = 4.5, days: int = 7) -> ConnectorResult:
    from .. import safe_http
    from datetime import datetime, timedelta, timezone
    start = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    try:
        r = safe_http.safe_get(ENDPOINT, params={
            "format": "geojson", "starttime": start, "minmagnitude": str(min_mag),
            "minlatitude": "-55", "maxlatitude": "16", "minlongitude": "105", "maxlongitude": "180",
        })
        if r.status_code != 200:
            return ConnectorResult(NAME, True, False, f"HTTP {r.status_code}")
        data = r.json()
        items = []
        for f in data.get("features", []):
            props = f.get("properties", {})
            mag = props.get("mag")
            if mag is None:
                continue
            coords = f.get("geometry", {}).get("coordinates", [None, None])
            items.append(Item(
                category="hazard", label=f"M{mag} earthquake - {props.get('place','')}",
                text=f"M{mag} earthquake near {props.get('place','')}",
                source="USGS", date=str(props.get("time", "")), url=props.get("url"), connector=NAME,
            ).to_dict())
            items[-1]["lat"] = coords[1]
            items[-1]["lon"] = coords[0]
        return ConnectorResult(NAME, True, True, f"{len(items)} items", items)
    except safe_http.FetchError as e:
        return ConnectorResult(NAME, True, False, f"blocked by safety guard: {e}")
    except Exception as e:
        return ConnectorResult(NAME, True, False, str(e))
