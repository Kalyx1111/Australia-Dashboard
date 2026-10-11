"""Regenerates data/seed.json - the offline snapshot shown when the backend is
not running. Contains only the regional reference items and strategic sites;
it never contains invented news. Run: python build_seed_json.py"""
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.static_markers import MARKERS          # noqa: E402
from app.reference_content import REFERENCE_ITEMS  # noqa: E402

by_cat = defaultdict(list)
for it in REFERENCE_ITEMS:
    by_cat[it["category"]].append(it)
markers = [{"id": m["id"], "name": m["name"], "lat": m["lat"], "lon": m["lon"], "cat": m["cat"],
            "note": m["note"], "source": m["source"], "date": "", "linked_items": []} for m in MARKERS]
seed = {"updated_at": "offline-snapshot", "items_by_category": dict(by_cat), "markers": markers,
        "connector_status": [{"name": "offline_seed", "configured": True, "ok": True,
                              "message": "Offline snapshot: reference items and strategic sites only; backend not connected",
                              "item_count": len(REFERENCE_ITEMS)}],
        "total_items": len(REFERENCE_ITEMS)}
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "seed.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(seed, f, ensure_ascii=False)
print(f"wrote {out}: {len(REFERENCE_ITEMS)} items, {len(markers)} markers")
