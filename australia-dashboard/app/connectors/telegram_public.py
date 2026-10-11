"""Public Telegram channels via the official public web preview (t.me/s/<name>).
No account, no API key, read-only, public channels only.

data/telegram_channels.json holds the list. Each channel has a group that sets
its heading behaviour: news, osint, defence, cyber, or darkweb (threat-intel
channels that report on dark-web activity; their posts land in the Darkweb &
Threat Intel heading). A channel marked verified:false has been listed but not
checked live by this build; its own status line shows whether it answers.

Safety: a handle must match Telegram's username rules before any URL is built,
so a bad entry cannot redirect a fetch. Channel text is escaped on display.
"""
from __future__ import annotations
import json
import os
import re
from html.parser import HTMLParser
from .base import Item, ConnectorResult
from ..classify import classify

NAME = "telegram_public"
_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
CHANNELS_FILE = os.path.join(_DATA, "telegram_channels.json")
USERNAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{4,31}$")
GROUPS = {"news", "osint", "defence", "cyber", "darkweb"}
MAX_PER_CHANNEL = 15


def configured() -> bool:
    return True


def load_channels() -> list[dict]:
    try:
        with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    entries = raw.get("channels", []) if isinstance(raw, dict) else raw
    out = []
    for e in entries:
        handle = e if isinstance(e, str) else (e.get("handle", "") if isinstance(e, dict) else "")
        group = (e.get("group") if isinstance(e, dict) else "news") or "news"
        verified = bool(e.get("verified")) if isinstance(e, dict) else False
        if USERNAME_RE.match(handle or ""):
            out.append({"handle": handle, "group": group if group in GROUPS else "news", "verified": verified})
    return out


class _MessageParser(HTMLParser):
    """Collects the text of each message bubble on a t.me/s page using the
    standard HTML parser (not regular expressions over markup)."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.messages, self._depth, self._buf, self._in = [], 0, [], False

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class", "") or ""
        if "tgme_widget_message_text" in cls.split():
            self._in, self._depth, self._buf = True, 1, []
        elif self._in and tag in ("div", "span"):
            self._depth += 1
        elif self._in and tag == "br":
            self._buf.append("\n")

    def handle_endtag(self, tag):
        if self._in and tag in ("div", "span"):
            self._depth -= 1
            if self._depth == 0:
                text = "".join(self._buf).strip()
                if text:
                    self.messages.append(text)
                self._in = False

    def handle_data(self, data):
        if self._in:
            self._buf.append(data)


def parse_channel_page(html: str) -> list[str]:
    p = _MessageParser()
    p.feed(html)
    return p.messages[-MAX_PER_CHANNEL:]


def fetch() -> ConnectorResult:
    from .. import safe_http
    channels = load_channels()
    if not channels:
        return ConnectorResult(NAME, False, False,
                               "no channels configured - add public channel names to data/telegram_channels.json")
    items, per_channel, errors = [], [], []
    for ch in channels:
        handle, group = ch["handle"], ch["group"]
        try:
            r = safe_http.safe_get(f"https://t.me/s/{handle}")
            if r.status_code != 200:
                per_channel.append(f"@{handle}: HTTP {r.status_code}")
                continue
            msgs = parse_channel_page(r.text)
            if not msgs:
                per_channel.append(f"@{handle}: no public posts visible (preview may be disabled)")
                continue
            per_channel.append(f"@{handle}: {len(msgs)} posts")
            for msg in msgs:
                cat = "darkweb" if group == "darkweb" else classify(msg)
                items.append(Item(category=cat, label=msg[:90], text=msg[:500],
                                  source=f"Telegram @{handle} ({group})", date="",
                                  url=f"https://t.me/{handle}", connector=NAME).to_dict())
        except safe_http.FetchError as e:
            per_channel.append(f"@{handle}: blocked ({e})")
        except Exception as e:
            per_channel.append(f"@{handle}: {type(e).__name__}")
    ok = sum(1 for p in per_channel if "posts" in p)
    msg = f"{len(items)} posts; {ok} of {len(channels)} channels answered. " + " | ".join(per_channel)[:600]
    return ConnectorResult(NAME, True, ok > 0, msg, items)
