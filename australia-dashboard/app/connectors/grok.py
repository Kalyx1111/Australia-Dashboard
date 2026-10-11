"""
Optional: xAI's Grok API with its x_search tool (docs.x.ai/docs/guides/
live-search), letting Grok search X scoped to specific handles via
allowed_x_handles. Verified during development that this endpoint/tool
exists and is documented - not guessed. Could not test a live call (no key,
and this sandbox can't reach api.x.ai either way) - if the request shape
has drifted since, the error message says so; check the docs link above.
"""
from __future__ import annotations
import json
import os
from .base import Item, ConnectorResult
from ..classify import classify

NAME = "grok"
ENDPOINT = "https://api.x.ai/v1/chat/completions"


def configured() -> bool:
    return bool(os.environ.get("GROK_API_KEY"))


def fetch() -> ConnectorResult:
    key = os.environ.get("GROK_API_KEY")
    if not key:
        return ConnectorResult(NAME, False, False, "not configured (optional - see secure_setup.py)")
    handles = [h.strip() for h in os.environ.get("GROK_TRACKED_HANDLES", "").split(",") if h.strip()]
    if not handles:
        return ConnectorResult(NAME, True, False, "GROK_API_KEY set but GROK_TRACKED_HANDLES is empty")

    import urllib.request
    import urllib.error
    payload = {
        "model": "grok-4",
        "messages": [{"role": "user", "content":
            f"Summarize recent military and political developments from the last 3 days from these "
            f"X accounts, as a plain bullet list of distinct facts, no commentary: "
            f"{', '.join('@' + h for h in handles[:25])}"}],
        "tools": [{"type": "x_search", "x_search": {"allowed_x_handles": handles[:25]}}],
    }
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return ConnectorResult(NAME, True, False, f"xAI API HTTP {e.code} - check docs.x.ai/docs/guides/live-search")
    except Exception as e:
        return ConnectorResult(NAME, True, False, f"network/parse error: {e}")

    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return ConnectorResult(NAME, True, False, "unexpected response shape - see docs.x.ai for current schema")

    lines = [l.strip("-* \t") for l in text.split("\n") if len(l.strip()) > 10]
    items = [Item(category=classify(l), label=l[:90], text=l, source="Grok/xAI (x_search)",
                   date="", connector=NAME).to_dict() for l in lines]
    return ConnectorResult(NAME, True, True, f"{len(items)} points from {min(len(handles),25)} accounts", items)
