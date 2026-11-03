"""Permanent-data updates for this dashboard.

Fetches public, licensed sources and adds their points to the layers this dashboard already shows.
- The sources are fixed in this file. No address typed by a user is ever fetched.
- Every point keeps its source, licence, accuracy rating and fetch date; click a point to see them.
- Curated points are never overwritten. A new point within 2 km of a point in the same layer is skipped.
- Military sites inside India's survey outline are never added to a dashboard that is not in focus mode.
- If a source cannot be reached, its last good data stays and the error is shown in the status.
Run from the Update data button, on the weekly schedule, or once from the command line: python run.py --update-now
"""
import csv
import datetime as dt
import io
import json
import math
import os
import re
import threading
import time
import urllib.parse
import urllib.request

from . import india_guard as guard

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
UPDATE_DIR = os.path.join(DATA, "updates")
STATUS_FILE = os.path.join(UPDATE_DIR, "status.json")
LOG_FILE = os.path.join(UPDATE_DIR, "log.txt")
USER_AGENT = "PermanentDataUpdater/1.0 (local dashboard; public open data)"
URL_OURAIRPORTS = "https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airports.csv"
URL_WRI = "https://raw.githubusercontent.com/wri/global-power-plant-database/master/output_database/global_power_plant_database.csv"
URL_UCDP = "https://ucdpapi.pcr.uu.se/api/gedevents/{version}?pagesize=1000&page={page}&StartDate={start}&EndDate={end}"
URL_OVERPASS = "https://overpass-api.de/api/interpreter"

SOURCES = {
    "ourairports": {"title": "OurAirports airports", "licence": "Public domain (CC0)", "accuracy": "High"},
    "wri_nuclear": {"title": "WRI Global Power Plant Database, nuclear plants", "licence": "CC BY 4.0", "accuracy": "Medium"},
    "ucdp_events": {"title": "UCDP georeferenced conflict events", "licence": "CC BY 4.0", "accuracy": "High"},
    "osm_military": {"title": "OpenStreetMap military sites", "licence": "ODbL, OpenStreetMap contributors", "accuracy": "Medium"},
    "osm_ports": {"title": "OpenStreetMap ports", "licence": "ODbL, OpenStreetMap contributors", "accuracy": "Medium"},
    "osm_pipelines": {"title": "OpenStreetMap pipelines (as points)", "licence": "ODbL, OpenStreetMap contributors", "accuracy": "Medium"},
}
MIL_QUERIES = [
    ("airfield", 'nwr["military"="airfield"]', ["air_base", "military_airfield", "military"]),
    ("naval_base", 'nwr["military"="naval_base"]', ["navy_base", "submarine_base", "military"]),
    ("base", 'nwr["military"="base"]', ["cantonment", "us_base", "foreign_base", "missile_base", "military"]),
    ("barracks", 'nwr["military"="barracks"]', ["cantonment", "military"]),
    ("landuse", 'nwr["landuse"="military"]["name"]', ["cantonment", "military"]),
]
PORT_QUERIES = [
    ("port", 'nwr["landuse"="port"]["name"]', ["seaport", "inland_port"]),
    ("industrial", 'nwr["industrial"="port"]["name"]', ["seaport", "inland_port"]),
]
PIPE_QUERIES = [("pipeline", 'nwr["man_made"="pipeline"]["name"]', ["pipeline"])]
UCDP_TYPES = {"1": "state-based conflict", "2": "non-state conflict", "3": "one-sided violence"}

_LOCK = threading.Lock()
_STATE = {"running": False}
_HOOKS = []


def _now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _age_days(iso):
    then = dt.datetime.fromisoformat(iso)
    if then.tzinfo is None:
        then = then.replace(tzinfo=dt.timezone.utc)
    return (dt.datetime.now(dt.timezone.utc) - then).total_seconds() / 86400.0


def _num(value):
    try:
        f = float(value)
        return f if math.isfinite(f) else None
    except (TypeError, ValueError):
        return None


def _plain(value):
    f = _num(value)
    if f is None:
        return value or '-'
    return str(int(f)) if f.is_integer() else f"{f:g}"


def _in_box(lat, lon, box):
    w, s, e, n = box
    return s <= lat <= n and w <= lon <= e


def load_config():
    cfg = {"mode": "clean", "bbox": [-180, -90, 180, 90], "layer_cats": [], "infra_layer_cats": [],
           "update_every_days": 7, "osm_tile_deg": 15, "osm_max_requests": 150, "ucdp_versions": ["25.1", "24.1"],
           "ucdp_days": 30, "sources": list(SOURCES)}
    try:
        with open(os.path.join(DATA, "dashboard.json"), encoding="utf-8") as fh:
            cfg.update(json.load(fh))
    except (OSError, ValueError):
        pass
    return cfg


def _get(url, data=None, max_bytes=40 * 2 ** 20, timeout=120):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read(max_bytes + 1)
    if len(body) > max_bytes:
        raise ValueError("the source sent more data than the safety limit")
    return body.decode("utf-8", "replace")


def _rec(source, key, name, cat, lat, lon, note, source_text, date, accuracy):
    safe_key = re.sub(r"[^A-Za-z0-9_-]", "_", str(key or "x"))[:60]
    return {"id": f"upd_{source}_{safe_key}", "name": (name or "unnamed")[:120], "cat": cat,
            "lat": round(lat, 5), "lon": round(lon, 5), "note": f"{note} · Accuracy: {accuracy}",
            "source": source_text, "date": date or "", "linked_items": [], "update": True}


def fetch_ourairports(cfg, avail, budget):
    if "airport" not in avail:
        return None, "no airport layer in this dashboard"
    out = []
    for r in csv.DictReader(io.StringIO(_get(URL_OURAIRPORTS, max_bytes=80 * 2 ** 20))):
        if (r.get("type") or "") not in ("large_airport", "medium_airport"):
            continue
        lat, lon = _num(r.get("latitude_deg")), _num(r.get("longitude_deg"))
        if lat is None or lon is None or not _in_box(lat, lon, cfg["bbox"]):
            continue
        ident = r.get("ident") or r.get("id") or ""
        note = f"{r['type'].replace('_', ' ')}; ICAO {r.get('icao_code') or '-'}; country {r.get('iso_country') or '-'}"
        out.append(_rec("ourairports", ident, r.get("name") or ident, "airport", lat, lon, note,
                        f"OurAirports, public domain · https://ourairports.com/airports/{ident}/", "",
                        SOURCES["ourairports"]["accuracy"]))
    return out, f"{len(out)} airports in the region"


def fetch_wri(cfg, avail, budget):
    if "nuclear_plant" not in avail:
        return None, "no nuclear layer in this dashboard"
    out = []
    for r in csv.DictReader(io.StringIO(_get(URL_WRI, max_bytes=60 * 2 ** 20))):
        if (r.get("primary_fuel") or "").strip().lower() != "nuclear":
            continue
        lat, lon = _num(r.get("latitude")), _num(r.get("longitude"))
        if lat is None or lon is None or not _in_box(lat, lon, cfg["bbox"]):
            continue
        name = r.get("name") or r.get("gppd_idnr") or "nuclear plant"
        note = (f"{_plain(r.get('capacity_mw'))} MW nuclear power plant; commissioned "
                f"{_plain(r.get('commissioning_year'))}; owner {r.get('owner') or '-'}")
        src = f"WRI Global Power Plant Database, CC BY 4.0 · {r.get('url') or 'https://datasets.wri.org/'}"
        out.append(_rec("wri_nuclear", r.get("gppd_idnr") or name, name, "nuclear_plant", lat, lon, note, src, "",
                        SOURCES["wri_nuclear"]["accuracy"]))
    return out, f"{len(out)} nuclear plants in the region"


def fetch_ucdp(cfg, avail, budget):
    cat = next((c for c in ("conflict", "flashpoint") if c in avail), None)
    if cat is None:
        return None, "no conflict layer in this dashboard"
    end = dt.date.today()
    start = end - dt.timedelta(days=int(cfg.get("ucdp_days", 30)))
    errors = []
    for version in cfg.get("ucdp_versions", []):
        out, page = [], 0
        try:
            while page < 10:
                page += 1
                url = URL_UCDP.format(version=version, page=page, start=start.isoformat(), end=end.isoformat())
                payload = json.loads(_get(url, max_bytes=30 * 2 ** 20))
                for ev in payload.get("Result", []):
                    lat, lon = _num(ev.get("latitude")), _num(ev.get("longitude"))
                    if lat is None or lon is None or not _in_box(lat, lon, cfg["bbox"]):
                        continue
                    kind = UCDP_TYPES.get(str(ev.get("type_of_violence")), "conflict event")
                    name = f"{ev.get('side_a') or 'unknown'} vs {ev.get('side_b') or 'unknown'}"
                    note = (f"{kind}; {ev.get('best', '?')} deaths (best estimate); {ev.get('country') or '-'}; "
                            f"coordinate precision {ev.get('where_prec', '?')}")
                    out.append(_rec("ucdp_events", ev.get("id"), name, cat, lat, lon, note,
                                    "UCDP Georeferenced Event Dataset, CC BY 4.0 · https://ucdp.uu.se/",
                                    str(ev.get("date_start") or "")[:10], SOURCES["ucdp_events"]["accuracy"]))
                if not payload.get("NextPageUrl"):
                    break
            return out, f"UCDP {version}: {len(out)} events in the last {cfg.get('ucdp_days', 30)} days"
        except (OSError, ValueError) as exc:
            errors.append(f"version {version}: {exc}")
    raise RuntimeError("; ".join(errors) or "no UCDP version configured")


def _tiles(box, step):
    w, s, e, n = box
    lat = s
    while lat < n:
        lat2 = min(lat + step, n)
        lon = w
        while lon < e:
            lon2 = min(lon + step, e)
            yield (lat, lon, lat2, lon2)
            lon = lon2
        lat = lat2


def _overpass(queries, cfg, budget):
    rows, errors = [], []
    for (s, w, n, e) in _tiles(cfg["bbox"], float(cfg.get("osm_tile_deg", 15))):
        for label, selector, cats in queries:
            if budget["left"] <= 0:
                budget["stopped"] = True
                return rows, errors
            budget["left"] -= 1
            q = f"[out:json][timeout:90];({selector}({s},{w},{n},{e}););out center meta;"
            try:
                body = _get(URL_OVERPASS, data=urllib.parse.urlencode({"data": q}).encode(),
                            max_bytes=80 * 2 ** 20, timeout=170)
                rows.extend((label, cats, el) for el in json.loads(body).get("elements", []))
            except (OSError, ValueError) as exc:
                errors.append(f"{label}: {exc}")
                if len(errors) >= 5:
                    return rows, errors
            time.sleep(1.0)
    return rows, errors


def _osm_records(rows, source, avail):
    out = []
    for label, cats, el in rows:
        cat = next((c for c in cats if c in avail), None)
        if cat is None:
            continue
        if el.get("type") == "node":
            lat, lon = _num(el.get("lat")), _num(el.get("lon"))
        else:
            center = el.get("center") or {}
            lat, lon = _num(center.get("lat")), _num(center.get("lon"))
        if lat is None or lon is None:
            continue
        tags = el.get("tags") or {}
        name = tags.get("name") or tags.get("name:en") or f"OSM {el.get('type')} {el.get('id')}"
        detail = tags.get("military") or tags.get("landuse") or tags.get("industrial") or tags.get("man_made") or label
        note = f"OpenStreetMap {label}: {detail}; operator {tags.get('operator') or '-'}; crowd-sourced, check before use"
        link = f"https://www.openstreetmap.org/{el.get('type')}/{el.get('id')}"
        out.append(_rec(source, f"{el.get('type')}{el.get('id')}", name, cat, lat, lon, note,
                        f"OpenStreetMap contributors, ODbL · {link}", str(el.get("timestamp") or "")[:10],
                        SOURCES[source]["accuracy"]))
    return out


def _osm_source(source, spec, cfg, avail, budget, what):
    queries = [(label, selector, [c for c in cats if c in avail]) for label, selector, cats in spec]
    queries = [q for q in queries if q[2]]
    if not queries:
        return None, f"no {what} layer in this dashboard"
    rows, errors = _overpass(queries, cfg, budget)
    if not rows and errors:
        raise RuntimeError("; ".join(errors)[:300])
    out = _osm_records(rows, source, avail)
    note = f"OpenStreetMap: {len(out)} {what} points in the region"
    if errors:
        note += f"; {len(errors)} request(s) failed"
    if budget.get("stopped"):
        note += "; request budget reached, run again to continue"
    return out, note


def fetch_osm_military(cfg, avail, budget):
    return _osm_source("osm_military", MIL_QUERIES, cfg, avail, budget, "military")


def fetch_osm_ports(cfg, avail, budget):
    return _osm_source("osm_ports", PORT_QUERIES, cfg, avail, budget, "port")


def fetch_osm_pipelines(cfg, avail, budget):
    return _osm_source("osm_pipelines", PIPE_QUERIES, cfg, avail, budget, "pipeline")


SOURCE_FETCHERS = {"ourairports": fetch_ourairports, "wri_nuclear": fetch_wri, "ucdp_events": fetch_ucdp,
                   "osm_military": fetch_osm_military, "osm_ports": fetch_osm_ports, "osm_pipelines": fetch_osm_pipelines}


def _km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0 * math.asin(min(1.0, math.sqrt(h)))


def _cell(lat, lon):
    return math.floor(lat * 20), math.floor(lon * 20)


def _grid_add(grid, rec):
    la, lo = _cell(rec["lat"], rec["lon"])
    grid.setdefault((rec.get("cat"), la, lo), []).append((rec["lat"], rec["lon"]))


def _near_any(rec, grid):
    la, lo = _cell(rec["lat"], rec["lon"])
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for plat, plon in grid.get((rec.get("cat"), la + dx, lo + dy), []):
                if _km(rec["lat"], rec["lon"], plat, plon) <= 2.0:
                    return True
    return False


def _clean_batch(records, cfg):
    kept, seen, grid = [], set(), {}
    for r in records:
        if r["id"] in seen or not _in_box(r["lat"], r["lon"], cfg["bbox"]) or guard.block_record(r):
            continue
        if _near_any(r, grid):
            continue
        seen.add(r["id"])
        kept.append(r)
        _grid_add(grid, r)
    return kept


def load_records(existing=()):
    """Update points to join the layers: not military inside India's outline (outside focus dashboards), not next to a point already shown."""
    grid = {}
    for r in existing:
        if isinstance(r, dict) and _num(r.get("lat")) is not None and _num(r.get("lon")) is not None:
            _grid_add(grid, {"cat": r.get("cat"), "lat": float(r["lat"]), "lon": float(r["lon"])})
    kept = []
    for sid in SOURCES:
        try:
            with open(os.path.join(UPDATE_DIR, sid + ".json"), encoding="utf-8") as fh:
                records = json.load(fh).get("records", [])
        except (OSError, ValueError, AttributeError):
            continue
        for r in records:
            if not isinstance(r, dict) or guard.block_record(r) or _near_any(r, grid):
                continue
            kept.append(r)
            _grid_add(grid, r)
    return kept


def _write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False)
    os.replace(tmp, path)


def _read_status():
    try:
        with open(STATUS_FILE, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def _stored_count(sid):
    try:
        with open(os.path.join(UPDATE_DIR, sid + ".json"), encoding="utf-8") as fh:
            return len(json.load(fh).get("records", []))
    except (OSError, ValueError, AttributeError):
        return None


def _log(line):
    os.makedirs(UPDATE_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as fh:
        fh.write(f"{_now()} {line}\n")


def on_update(fn):
    _HOOKS.append(fn)


def run_update(reason="manual"):
    if not _LOCK.acquire(blocking=False):
        return {"started": False, "summary": "an update is already running"}
    _STATE["running"] = True
    try:
        cfg = load_config()
        avail = set(cfg.get("layer_cats", [])) | set(cfg.get("infra_layer_cats", []))
        results = {}
        budget = {"left": int(cfg.get("osm_max_requests", 150)), "stopped": False}
        for sid in cfg.get("sources", []):
            fetch = SOURCE_FETCHERS.get(sid)
            if fetch is None:
                continue
            try:
                records, note = fetch(cfg, avail, budget)
                if records is None:
                    results[sid] = {"state": "skipped", "count": None, "message": note, "fetched_at": None}
                    continue
                records = _clean_batch(records, cfg)
                _write_json(os.path.join(UPDATE_DIR, sid + ".json"),
                            {"source": sid, "title": SOURCES[sid]["title"], "licence": SOURCES[sid]["licence"],
                             "fetched_at": _now(), "records": records})
                results[sid] = {"state": "ok", "count": len(records), "message": note, "fetched_at": _now()}
            except Exception as exc:  # keep the last good file and report the error
                results[sid] = {"state": "error", "count": _stored_count(sid),
                                "message": f"{type(exc).__name__}: {exc}"[:300], "fetched_at": _now()}
        for hook in _HOOKS:
            try:
                hook()
            except Exception as exc:
                _log(f"merge: {type(exc).__name__}: {exc}")
        summary = "; ".join(f"{sid} {v['state']}" + (f" ({v['count']})" if v.get("count") is not None else "")
                            for sid, v in results.items())
        _write_json(STATUS_FILE, {"last_run": _now(), "reason": reason, "sources": results})
        _log(f"{reason}: {summary}")
        return {"started": True, "summary": summary}
    finally:
        _STATE["running"] = False
        _LOCK.release()


def status():
    cfg = load_config()
    st = _read_status()
    last = st.get("last_run")
    days = float(cfg.get("update_every_days") or 0)
    nxt = None
    if last and days > 0:
        nxt = (dt.datetime.fromisoformat(last) + dt.timedelta(days=days)).isoformat()
    return {"running": _STATE["running"], "last_run": last, "next_run": nxt, "update_every_days": days,
            "sources": st.get("sources", {}), "licences": {k: v["licence"] for k, v in SOURCES.items()}}


def start_background(reason):
    if _STATE["running"]:
        return False
    threading.Thread(target=run_update, args=(reason,), daemon=True, name="permanent-data-update").start()
    return True


def start_scheduler():
    def loop():
        time.sleep(120)
        while True:
            try:
                cfg = load_config()
                days = float(cfg.get("update_every_days") or 0)
                last = _read_status().get("last_run")
                if days > 0 and not _STATE["running"] and (not last or _age_days(last) >= days):
                    run_update("weekly schedule")
            except Exception as exc:
                _log(f"scheduler: {type(exc).__name__}: {exc}")
            time.sleep(3600)
    threading.Thread(target=loop, daemon=True, name="permanent-data-scheduler").start()
