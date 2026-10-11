"""Ransomware victim claims from Ransomware.live API v2 - public, no key.

Documented base: https://api.ransomware.live/v2 (see https://www.ransomware.live/apidocs).
This connector first calls the documented /info endpoint, then /recentvictims,
and reports the exact HTTP status for each, so "endpoint wrong" and "service
unavailable" are distinguishable in the status panel.

What the data is: victims that ransomware groups publish on their own leak
sites, aggregated by Ransomware.live. These are group CLAIMS, not verified
facts. No state attribution is made here; the API does not supply one.
"""
from __future__ import annotations
import json
import logging
from .base import Item, ConnectorResult

log = logging.getLogger("ransomware_live")
NAME = "ransomware_live"
BASE = "https://api.ransomware.live/v2"
REGION_COUNTRIES = {"AU", "NZ", "PG", "SB", "VU", "NC", "FJ", "WS", "TO", "TV", "NR", "KI", "MH", "FM", "PW", "GU", "MP", "AS", "CK", "NU", "TK", "WF", "TL", "ID"}


def configured() -> bool:
    return True


def _clean(s, n=160):
    return (str(s or "").replace("\n", " ").replace("\r", " ").strip())[:n]


def parse(records) -> list[dict]:
    """Pure function (no network), so it can be tested against fixtures."""
    out = []
    for r in records:
        if not isinstance(r, dict):
            continue
        victim = _clean(r.get("victim"))
        if not victim:
            continue
        country = _clean(r.get("country"), 4).upper()
        group = _clean(r.get("group"), 60) or "unknown group"
        date = _clean(r.get("attackdate") or r.get("discovered"), 40)
        out.append(Item(
            category="darkweb", label=f"[{group}] claimed victim: {victim}",
            text=f"Leak-site claim against {victim} ({country or 'country not stated'}), group: {group}. Group claim, not verified.",
            source="Ransomware.live (leak-site aggregation)", date=date, url=None, connector=NAME,
        ).to_dict() | {"country": country, "group": group, "in_region": country in REGION_COUNTRIES})
    return out


def fetch() -> ConnectorResult:
    from .. import safe_http
    try:
        info = safe_http.safe_get(f"{BASE}/info")
        if info.status_code != 200:
            log.warning("ransomware.live /info returned HTTP %s", info.status_code)
            return ConnectorResult(NAME, True, False,
                                   f"/v2/info HTTP {info.status_code} - the documented API did not answer; see ransomware.live/apidocs")
        r = safe_http.safe_get(f"{BASE}/recentvictims")
        if r.status_code == 429:
            return ConnectorResult(NAME, True, False, "rate limited (1 request/minute per endpoint) - retried next cycle")
        if r.status_code != 200:
            log.warning("ransomware.live /recentvictims returned HTTP %s", r.status_code)
            return ConnectorResult(NAME, True, False,
                                   f"/v2/recentvictims HTTP {r.status_code} (/info answered OK, so the service is up; this endpoint refused the request)")
        data = json.loads(r.content)
        items = parse(data if isinstance(data, list) else data.get("victims", []))
        apac = sum(1 for i in items if i["in_region"])
        return ConnectorResult(NAME, True, True, f"{len(items)} recent claimed victims ({apac} in region)", items[:200])
    except safe_http.FetchError as e:
        return ConnectorResult(NAME, True, False, f"blocked by safety guard: {e}")
    except ValueError:
        return ConnectorResult(NAME, True, False, "response was not valid JSON")
    except Exception as e:
        return ConnectorResult(NAME, True, False, f"unreachable ({type(e).__name__})")
