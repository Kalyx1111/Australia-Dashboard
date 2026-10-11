"""Instagram via Meta's OFFICIAL Graph API, "Business Discovery" - no scraping.

What this can and cannot do (verified against Meta's developer documentation):
- It reads PUBLIC data of Instagram Business or Creator accounts only. Personal
  accounts cannot be read through this route at all.
- It needs: an Instagram Business or Creator account YOU own (its numeric ID),
  a Meta developer app, and a Facebook user access token with the instagram_basic
  and pages_read_engagement permissions. Set INSTAGRAM_IG_USER_ID and
  INSTAGRAM_ACCESS_TOKEN (encrypted with AES-256 via the key setup).
- Targets are listed in data/instagram_accounts.json (usernames only).

Without those, this connector reports exactly what is missing and fetches nothing.
The token is redacted from every error message, because the request URL carries it.
"""
from __future__ import annotations
import json
import os
import re
from .base import Item, ConnectorResult
from ..classify import classify

NAME = "instagram_graph"
_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
ACCOUNTS_FILE = os.path.join(_DATA, "instagram_accounts.json")
USERNAME_RE = re.compile(r"^[A-Za-z0-9._]{1,30}$")
DEFAULT_VERSION = "v25.0"   # version used in Meta's current Business Discovery documentation


def configured() -> bool:
    return bool(os.environ.get("INSTAGRAM_ACCESS_TOKEN") and os.environ.get("INSTAGRAM_IG_USER_ID"))


def load_accounts() -> list[str]:
    try:
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    names = raw.get("accounts", []) if isinstance(raw, dict) else raw
    out = []
    for n in names:
        u = (n.get("username") if isinstance(n, dict) else n) or ""
        if USERNAME_RE.match(u):
            out.append(u)
    return out


def _redact(text: str) -> str:
    tok = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
    return text.replace(tok, "[token]") if tok else text


def fetch() -> ConnectorResult:
    from .. import safe_http
    if not configured():
        return ConnectorResult(NAME, False, False,
                               "not configured - needs INSTAGRAM_IG_USER_ID and INSTAGRAM_ACCESS_TOKEN (Meta Business Discovery; see README)")
    accounts = load_accounts()
    if not accounts:
        return ConnectorResult(NAME, True, False, "no accounts listed in data/instagram_accounts.json")
    version = os.environ.get("INSTAGRAM_API_VERSION", DEFAULT_VERSION)
    ig_id = os.environ["INSTAGRAM_IG_USER_ID"]
    token = os.environ["INSTAGRAM_ACCESS_TOKEN"]
    items, per_account = [], []
    for user in accounts:
        try:
            r = safe_http.safe_get(
                f"https://graph.facebook.com/{version}/{ig_id}",
                params={"fields": f"business_discovery.username({user}){{username,media.limit(10){{caption,timestamp,permalink,media_type}}}}",
                        "access_token": token})
            data = json.loads(r.content)
            if "error" in data:
                per_account.append(f"@{user}: {_redact(str(data['error'].get('message', 'error')))[:80]}")
                continue
            media = (data.get("business_discovery") or {}).get("media", {}).get("data", [])
            per_account.append(f"@{user}: {len(media)} posts")
            for m in media:
                caption = (m.get("caption") or "").strip().replace("\n", " ")
                if not caption:
                    continue
                items.append(Item(category=classify(caption), label=caption[:90], text=caption[:500],
                                  source=f"Instagram @{user} (Business Discovery)", date=m.get("timestamp", ""),
                                  url=m.get("permalink"), connector=NAME).to_dict())
        except Exception as e:
            per_account.append(f"@{user}: {_redact(type(e).__name__)}")
    ok = sum(1 for p in per_account if "posts" in p)
    return ConnectorResult(NAME, True, ok > 0,
                           f"{len(items)} posts; {ok} of {len(accounts)} accounts answered. " + " | ".join(per_account)[:600],
                           items)
