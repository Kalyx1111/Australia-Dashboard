"""X (Twitter) through X's OFFICIAL API v2 recent search. No scraping.

- Needs an X developer app with a bearer token in X_BEARER_TOKEN (stored encrypted via the key setup).
- Recent search belongs to X's paid API access tiers. Without that access, X's own error is reported.
- Queries are listed in data/x_queries.json (at most 10). Results are classified into the dashboard's headings.
- The token is redacted from every error message.
Built against X's documented API; NOT live-tested from the build sandbox (no network there).
"""
from __future__ import annotations
import json
import os
from .base import Item, ConnectorResult
from ..classify import classify
from ..safe_http import safe_get

NAME = "x_api"
_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
QUERIES_FILE = os.path.join(_DATA, "x_queries.json")
SEARCH_URL = "https://api.x.com/2/tweets/search/recent"
MAX_QUERIES = 10


def configured() -> bool:
    return bool(os.environ.get("X_BEARER_TOKEN"))


def load_queries() -> list[str]:
    try:
        with open(QUERIES_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return []
    out = []
    for q in data if isinstance(data, list) else []:
        if isinstance(q, str) and 0 < len(q.strip()) <= 200 and "\n" not in q:
            out.append(q.strip())
    return out[:MAX_QUERIES]


def _redact(text: str) -> str:
    tok = os.environ.get("X_BEARER_TOKEN", "")
    return text.replace(tok, "[redacted]") if tok else text


def fetch() -> ConnectorResult:
    if not configured():
        return ConnectorResult(NAME, False, False,
                               "not configured - needs X_BEARER_TOKEN (official X API v2; recent search needs paid API access). Nothing fetched.")
    queries = load_queries()
    if not queries:
        return ConnectorResult(NAME, True, False, "no queries in data/x_queries.json")
    items, errors = [], []
    headers = {"Authorization": "Bearer " + os.environ["X_BEARER_TOKEN"]}
    for q in queries:
        try:
            r = safe_get(SEARCH_URL, headers=headers,
                         params={"query": f"{q} lang:en -is:retweet", "max_results": 10, "tweet.fields": "created_at"})
            if r.status_code != 200:
                errors.append(f"{q}: HTTP {r.status_code}")
                continue
            body = json.loads(r.text or "{}")
            for t in body.get("data") or []:
                text = t.get("text", "")
                if not text:
                    continue
                items.append(Item(category=classify(text), label=text[:140], text=text[:600],
                                  source=f"X (official API): {q}", date=t.get("created_at", ""),
                                  url=f"https://x.com/i/web/status/{t['id']}" if t.get("id") else None,
                                  connector=NAME))
        except Exception as exc:  # network or parse failure: report it, never the token
            errors.append(_redact(f"{q}: {type(exc).__name__}"))
    msg = f"{len(items)} posts from {len(queries)} queries"
    if errors:
        msg += "; errors: " + "; ".join(errors[:4])
    return ConnectorResult(NAME, True, bool(items) or not errors, msg, items)
