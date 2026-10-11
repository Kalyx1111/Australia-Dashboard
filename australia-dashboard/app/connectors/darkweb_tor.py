"""Dark-web news feeds, fetched through Tor - but only from a short, user-curated
list of onion addresses (data/onion_sources.json). No crawling, no search, no
forum or marketplace scraping.

Requirements, stated plainly:
- Tor must be running locally: Tor Browser (open; SOCKS port 9150) or the Tor
  service (port 9050). This build checks both ports and reports which it found.
- Each onion address must come from the outlet's OWN official website (fake
  onion lookalikes are common). This connector only checks the address shape:
  a v3 onion is 56 characters from a-z and 2-7, followed by .onion.
- Only sources that publish an RSS feed are read. Sources that need a login are
  not supported.
"""
from __future__ import annotations
import json
import os
import re
from .base import Item, ConnectorResult

NAME = "darkweb_tor"
_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
SOURCES_FILE = os.path.join(_DATA, "onion_sources.json")
ONION_V3 = re.compile(r"^[a-z2-7]{56}\.onion$")


def configured() -> bool:
    return True


def load_sources() -> list[dict]:
    try:
        with open(SOURCES_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    out = []
    for s in (raw.get("sources", []) if isinstance(raw, dict) else []):
        url = (s.get("url") or "").strip()
        from urllib.parse import urlsplit
        host = (urlsplit(url).hostname or "").lower()
        if s.get("type", "rss") == "rss" and ONION_V3.match(host) and url.startswith(("http://", "https://")):
            out.append({"name": s.get("name", host)[:60], "url": url})
    return out


def fetch() -> ConnectorResult:
    from .. import safe_http
    import feedparser
    sources = load_sources()
    if not sources:
        return ConnectorResult(NAME, False, False,
                               "no onion sources configured - add RSS sources you verified on the outlet's own site to data/onion_sources.json")
    port = safe_http.tor_port()
    if port is None:
        return ConnectorResult(NAME, True, False,
                               "Tor not running - open Tor Browser (listens on 9150) or start the Tor service (9050), then refresh")
    items, per_source = [], []
    for s in sources:
        try:
            r = safe_http.safe_get(s["url"])
            if r.status_code != 200:
                per_source.append(f"{s['name']}: HTTP {r.status_code}")
                continue
            parsed = feedparser.parse(r.content)
            n = 0
            for entry in parsed.entries[:20]:
                title = (getattr(entry, "title", "") or "").strip()
                if not title:
                    continue
                n += 1
                items.append(Item(category="darkweb", label=title[:90], text=title[:500],
                                  source=f"Dark web (Tor): {s['name']}",
                                  date=getattr(entry, "published", "") or "", url=None, connector=NAME).to_dict())
            per_source.append(f"{s['name']}: {n} items")
        except safe_http.FetchError as e:
            per_source.append(f"{s['name']}: {e}")
        except Exception as e:
            per_source.append(f"{s['name']}: {type(e).__name__}")
    ok = sum(1 for p in per_source if "items" in p)
    return ConnectorResult(NAME, True, ok > 0,
                           f"via Tor port {port}; {ok} of {len(sources)} sources answered. " + " | ".join(per_source)[:500],
                           items)
