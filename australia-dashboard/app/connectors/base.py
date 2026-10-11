from __future__ import annotations
from dataclasses import dataclass, field
import time

# The 15 dashboard headings (see app/classify.py) plus the non-news reference types.
VALID_CATEGORIES = {"myanmar", "bangladesh", "china", "drugs", "arms", "cyber", "espionage", "darkweb", "manipur", "assam", "arunachal", "nagaland", "tripura", "mizoram", "meghalaya", "sikkim", "insurgency", "military", "econ", "social", "hazard", "geo"}


@dataclass
class Item:
    category: str
    label: str
    text: str
    source: str
    date: str
    url: str | None = None
    connector: str = ""

    def to_dict(self):
        return {"category": self.category, "label": self.label, "text": self.text,
                "source": self.source, "date": self.date, "url": self.url, "connector": self.connector}


@dataclass
class ConnectorResult:
    name: str
    configured: bool
    ok: bool
    message: str
    items: list = field(default_factory=list)
    checked_at: float = field(default_factory=time.time)

    def to_status_dict(self):
        return {"name": self.name, "configured": self.configured, "ok": self.ok,
                "message": self.message, "item_count": len(self.items), "checked_at": self.checked_at}
