"""Facebook Pages through Meta's OFFICIAL Graph API. No scraping.

- Reads posts from Pages YOU manage, or from Pages that grant you Page Public Content Access through Meta's app review.
- Needs FACEBOOK_PAGE_TOKEN (a Page access token) and Page IDs in data/facebook_pages.json.
- The token is redacted from every error message.
Built against Meta's documented Graph API; NOT live-tested from the build sandbox (no network there).
"""
from __future__ import annotations
import json
import os
import re
from .base import Item, ConnectorResult
from ..classify import classify
from ..safe_http import safe_get

NAME = "facebook_graph"
_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
PAGES_FILE = os.path.join(_DATA, "facebook_pages.json")
GRAPH = "https://graph.facebook.com/v25.0"
PAGE_ID_RE = re.compile(r"^[0-9]{5,20}$")


def configured() -> bool:
    return bool(os.environ.get("FACEBOOK_PAGE_TOKEN"))


def load_pages() -> list[dict]:
    try:
        with open(PAGES_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return []
    out = []
    for p in data if isinstance(data, list) else []:
        if isinstance(p, dict) and PAGE_ID_RE.match(str(p.get("id", ""))):
            out.append({"id": str(p["id"]), "name": str(p.get("name", p["id"]))[:80]})
    return out[:20]


def _redact(text: str) -> str:
    tok = os.environ.get("FACEBOOK_PAGE_TOKEN", "")
    return text.replace(tok, "[redacted]") if tok else text


def fetch() -> ConnectorResult:
    if not configured():
        return ConnectorResult(NAME, False, False,
                               "not configured - needs FACEBOOK_PAGE_TOKEN (Meta Graph API Page token). Nothing fetched.")
    pages = load_pages()
    if not pages:
        return ConnectorResult(NAME, True, False, "no Page IDs in data/facebook_pages.json")
    token = os.environ["FACEBOOK_PAGE_TOKEN"]
    items, errors = [], []
    for pg in pages:
        try:
            r = safe_get(f"{GRAPH}/{pg['id']}/posts",
                         params={"fields": "message,created_time,permalink_url", "limit": 10, "access_token": token})
            if r.status_code != 200:
                errors.append(f"{pg['name']}: HTTP {r.status_code}")
                continue
            for post in json.loads(r.text or "{}").get("data") or []:
                msg = post.get("message") or ""
                if not msg:
                    continue
                items.append(Item(category=classify(msg), label=msg[:140], text=msg[:600],
                                  source=f"Facebook page: {pg['name']}", date=post.get("created_time", ""),
                                  url=post.get("permalink_url"), connector=NAME))
        except Exception as exc:
            errors.append(_redact(f"{pg['name']}: {type(exc).__name__}"))
    msg = f"{len(items)} posts from {len(pages)} pages"
    if errors:
        msg += "; errors: " + "; ".join(errors[:4])
    return ConnectorResult(NAME, True, bool(items) or not errors, msg, items)
