from __future__ import annotations
import logging
import os
import time

from flask import Flask, jsonify, send_from_directory, request

from . import cache
from .scheduler import Scheduler, poll_once
from .geomatch import attach_live_items
from .reference_content import REFERENCE_ITEMS
from . import secure_store
from .infra import INFRA_MARKERS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("server")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, static_folder=None)

_last_manual_refresh = 0.0
MIN_REFRESH_GAP = 20  # 3-min auto-poll already covers most needs; this just guards the button


@app.after_request
def _security_headers(resp):
    # softwaresafety section 6. This page is fully self-contained (no
    # external scripts/fonts/styles - verified: zero http(s):// src/href in
    # static/dashboard.html once Chart.js/Three.js were removed), so the CSP
    # can be `'self'` with no carve-outs, not a loose policy with exceptions.
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; "
        "base-uri 'none'; object-src 'none'"
    )
    return resp


def create_app(poll_interval: int = 180) -> Flask:
    sched = Scheduler(interval_seconds=poll_interval)
    sched.start()
    app.config["SCHEDULER"] = sched
    return app


@app.get("/")
def index():
    return send_from_directory(STATIC_DIR, "dashboard.html")


@app.get("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)


@app.get("/api/snapshot")
def snapshot():
    try:
        data = cache.read() or {"items": [], "connector_status": []}
        items = data.get("items", [])
        markers = attach_live_items(items) + [dict(m) for m in INFRA_MARKERS]
        by_category: dict = {}
        for it in items:
            by_category.setdefault(it.get("category", "political"), []).append(it)
        for ref in REFERENCE_ITEMS:
            by_category.setdefault(ref["category"], []).append(ref)
        for cat in by_category:
            by_category[cat].sort(key=lambda x: str(x.get("date") or ""), reverse=True)
        from collections import Counter
        layer_counts = dict(Counter(m["cat"] for m in markers))
        for it in items:
            if isinstance(it.get("lat"), (int, float)) and isinstance(it.get("lon"), (int, float)):
                layer_counts[it.get("category", "hazard")] = layer_counts.get(it.get("category", "hazard"), 0) + 1
        return jsonify({
            "updated_at": data.get("updated_at"),
            "layer_counts": layer_counts,
            "items_by_category": by_category,
            "markers": markers,
            "connector_status": data.get("connector_status", []),
            "total_items": len(items),
        })
    except Exception as e:
        log.exception("snapshot() failed unexpectedly")
        return jsonify({"updated_at": None, "items_by_category": {}, "markers": [],
                         "connector_status": [], "total_items": 0,
                         "error": f"snapshot rendering failed: {e}"}), 500


@app.get("/api/status")
def status():
    data = cache.read() or {}
    return jsonify({"updated_at": data.get("updated_at"), "connector_status": data.get("connector_status", [])})


@app.post("/api/refresh")
def refresh():
    global _last_manual_refresh
    now = time.time()
    if now - _last_manual_refresh < MIN_REFRESH_GAP:
        wait = round(MIN_REFRESH_GAP - (now - _last_manual_refresh), 1)
        return jsonify({"error": f"refreshed too recently, wait {wait}s"}), 429
    _last_manual_refresh = now
    from .scheduler import request_poll
    started = request_poll()
    resp = snapshot()
    return resp


@app.get("/healthz")
def healthz():
    return jsonify({"ok": True})


@app.get("/api/diagnostics")
def diagnostics():
    """Live self-diagnostic, not just a startup check - what a support
    conversation would actually need to see: is the background poller
    alive, when did it last succeed, and what's each connector's current
    status. Real state, read directly, not a hardcoded "all good"."""
    sched = app.config.get("SCHEDULER")
    data = cache.read() or {}
    updated_at = data.get("updated_at")
    age_seconds = (time.time() - updated_at) if updated_at else None
    thread_alive = bool(sched and sched._thread and sched._thread.is_alive())
    statuses = data.get("connector_status", [])
    stale = age_seconds is not None and age_seconds > 600  # 2 missed 3-min cycles
    return jsonify({
        "scheduler_thread_alive": thread_alive,
        "last_poll_age_seconds": age_seconds,
        "last_poll_stale": stale,
        "connectors_ok": sum(1 for s in statuses if s.get("ok")),
        "connectors_total": len(statuses),
        "connector_detail": statuses,
        "healthy": thread_alive and not stale,
    })


@app.get("/favicon.ico")
def favicon():
    return "", 204


KEY_FIELDS = {
    "GROK_API_KEY": {"label": "xAI Grok API key", "help": "x.ai - powers the x_search-based X feed"},
    "GROK_TRACKED_HANDLES": {"label": "Grok tracked X handles", "help": "comma-separated, no @"},
    "X_THIRDPARTY_API_KEY": {"label": "TwitterAPI.io", "help": "twitterapi.io - cheaper raw-tweet alternative"},
    "NEWSAPI_KEY": {"label": "NewsAPI.org", "help": "Free key at newsapi.org/register"},
    "INSTAGRAM_ACCESS_TOKEN": {"label": "Instagram (Meta) access token", "help": "Facebook user token with instagram_basic + pages_read_engagement - official Business Discovery route"},
    "INSTAGRAM_IG_USER_ID": {"label": "Your Instagram Business/Creator account ID", "help": "numeric ID of an account YOU own (Meta developer app setup)"},
}


@app.get("/api/keys")
def get_keys():
    try:
        stored = secure_store.decrypt_secrets()
    except (secure_store.CryptoUnavailable, secure_store.DecryptError) as e:
        log.warning("GET /api/keys: %s", e)
        stored = {}
    out = {}
    for name, meta in KEY_FIELDS.items():
        in_store = bool(stored.get(name))
        in_env = bool(os.environ.get(name))
        out[name] = {**meta, "configured": in_store or in_env,
                     "source": "encrypted store" if in_store else ("env/.env" if in_env else None)}
    return jsonify(out)


@app.post("/api/keys")
def save_keys():
    body = request.get_json(silent=True) or {}
    updates = {k: (v or "").strip() for k, v in body.items() if k in KEY_FIELDS}
    if not updates:
        return jsonify({"error": "no recognized key fields in request body"}), 400
    try:
        secure_store.update_secrets(updates)
    except secure_store.CryptoUnavailable as e:
        return jsonify({"error": str(e)}), 500
    for k, v in updates.items():
        if v:
            os.environ[k] = v
        else:
            os.environ.pop(k, None)
    return jsonify({"saved": [k for k, v in updates.items() if v], "cleared": [k for k, v in updates.items() if not v]})


# ---------------- Custom user-plotted markers (client-owned; server only persists them) ----------------
@app.get("/api/custom-markers")
def get_custom_markers():
    data = cache.read("custom_markers.json") or {"markers": []}
    return jsonify(data)


@app.post("/api/custom-markers")
def add_custom_marker():
    body = request.get_json(silent=True) or {}
    label = (body.get("label") or "").strip()
    remark = (body.get("remark") or "").strip()
    try:
        lat, lon = float(body.get("lat")), float(body.get("lon"))
    except (TypeError, ValueError):
        return jsonify({"error": "lat/lon must be numbers"}), 400
    if not label or not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return jsonify({"error": "label required; lat in [-90,90]; lon in [-180,180]"}), 400
    data = cache.read("custom_markers.json") or {"markers": []}
    data["markers"].append({"label": label[:200], "remark": remark[:500], "lat": lat, "lon": lon,
                              "added": time.strftime("%Y-%m-%d %H:%M:%S")})
    cache.write(data, "custom_markers.json")
    return jsonify(data)


@app.delete("/api/custom-markers/<int:idx>")
def delete_custom_marker(idx):
    data = cache.read("custom_markers.json") or {"markers": []}
    if 0 <= idx < len(data["markers"]):
        data["markers"].pop(idx)
        cache.write(data, "custom_markers.json")
        return jsonify(data)
    return jsonify({"error": "index out of range"}), 404
