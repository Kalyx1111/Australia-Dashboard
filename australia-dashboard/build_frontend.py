import json, math

import os as _os
BASE = _os.path.dirname(_os.path.abspath(__file__))
countries = json.load(open(f"{BASE}/data/countries.json"))
proj = json.load(open(f"{BASE}/data/proj-constants.json"))
seed = json.load(open(f"{BASE}/data/seed.json"))
base_css = open(f"{BASE}/base_theme.css").read()

W, H = proj["width"], proj["height"]
pivot_lon, pivot_lat = 150.0, -25.0
pivot_x = proj["translate"][0]
pivot_y = proj["translate"][1]
old_css = base_css.replace("__PIVOTX__", str(round(pivot_x,1))).replace("__PIVOTY__", str(round(pivot_y,1)))

EXTRA_CSS = """
/* ---------- live/offline status + refresh (new) ---------- */
.status-pill{display:inline-flex;align-items:center;gap:6px;font-family:var(--mono);font-size:10.5px;
  font-weight:700;letter-spacing:.04em;padding:4px 10px;border-radius:999px;border:1px solid var(--border);
  text-transform:uppercase;white-space:nowrap;}
.status-pill.live{color:var(--green);border-color:rgba(95,196,143,.35);background:rgba(95,196,143,.08);}
.status-pill.offline{color:var(--amber);border-color:rgba(255,154,77,.35);background:rgba(255,154,77,.08);}
.status-pill .dot{width:6px;height:6px;border-radius:50%;background:currentColor;}
.status-pill.live .dot{animation:blink 1.6s ease-in-out infinite;}
.refresh-btn{background:var(--panel2);border:1px solid var(--border);color:var(--text-dim);
  border-radius:8px;padding:7px 12px;font-size:11px;font-family:var(--sans);cursor:pointer;
  display:inline-flex;align-items:center;gap:6px;transition:border-color .15s,color .15s;}
.refresh-btn:hover{border-color:var(--gold-soft);color:var(--text);}
.refresh-btn:disabled{opacity:.5;cursor:default;}
.refresh-btn svg{transition:transform .5s;}
.refresh-btn.spinning svg{animation:spin 0.8s linear infinite;}
@keyframes spin{to{transform:rotate(360deg);}}
.offline-banner{display:none;background:rgba(255,154,77,.10);border:1px solid rgba(255,154,77,.35);
  color:#ffbf8a;border-radius:8px;padding:10px 14px;font-size:12px;margin-bottom:14px;line-height:1.5;}
.offline-banner.show{display:block;}
.offline-banner b{color:#fff;}
.connector-strip{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;}
.conn-badge{font-family:var(--mono);font-size:9.5px;padding:3px 8px;border-radius:5px;border:1px solid var(--border-soft);
  color:var(--text-faint);}
.conn-badge.ok{color:var(--green);border-color:rgba(95,196,143,.3);}
.conn-badge.err{color:var(--red);border-color:rgba(239,83,84,.3);}
.conn-badge.off{color:var(--text-faint);}
.empty-note{font-size:11.5px;color:var(--text-faint);font-style:italic;padding:6px 0;}
.infra-note{font-size:9.5px;color:var(--text-faint);margin-top:8px;padding-top:8px;
  border-top:1px solid var(--border-soft);line-height:1.5;}

/* ---------- settings modal (new) ---------- */
.icon-btn{background:var(--panel2);border:1px solid var(--border);color:var(--text-dim);
  border-radius:8px;width:34px;height:34px;display:inline-flex;align-items:center;justify-content:center;
  cursor:pointer;flex:none;transition:border-color .15s,color .15s;}
.icon-btn:hover{border-color:var(--gold-soft);color:var(--text);}
.modal-backdrop{position:fixed;inset:0;background:rgba(4,6,10,.7);display:none;align-items:center;
  justify-content:center;z-index:100;padding:20px;}
.modal-backdrop.show{display:flex;}
.modal{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:22px;
  max-width:480px;width:100%;max-height:85vh;overflow-y:auto;}
.modal h3{margin:0 0 4px;font-size:15px;color:var(--text);}
.modal .modal-sub{font-size:11.5px;color:var(--text-faint);margin-bottom:18px;line-height:1.5;}
.key-field{margin-bottom:16px;}
.key-field label{display:flex;align-items:center;gap:7px;font-size:12px;font-weight:700;color:var(--text);margin-bottom:4px;}
.key-field .kf-status{width:6px;height:6px;border-radius:50%;background:var(--text-faint);}
.key-field .kf-status.on{background:var(--green);box-shadow:0 0 6px 1px var(--green);}
.key-field .kf-help{font-size:10.5px;color:var(--text-faint);margin-bottom:6px;}
.key-field input{width:100%;background:var(--panel2);border:1px solid var(--border);border-radius:7px;
  padding:9px 11px;color:var(--text);font-size:12px;font-family:var(--mono);outline:none;}
.key-field input:focus{border-color:var(--gold-soft);}
.modal-actions{display:flex;gap:10px;margin-top:20px;align-items:center;}
.btn-primary{background:var(--gold);color:#1a1408;border:none;border-radius:8px;padding:10px 18px;
  font-size:12px;font-weight:700;cursor:pointer;}
.btn-primary:hover{opacity:.9;}
.btn-secondary{background:transparent;border:1px solid var(--border);color:var(--text-dim);
  border-radius:8px;padding:10px 18px;font-size:12px;cursor:pointer;}
.modal-msg{font-size:11.5px;margin-top:12px;min-height:16px;}
.modal-msg.ok{color:var(--green);}
.modal-msg.err{color:var(--red);}
.skel{background:linear-gradient(90deg,var(--panel2) 25%,#131f30 37%,var(--panel2) 63%);
  background-size:400% 100%;animation:skel 1.4s ease infinite;border-radius:4px;}
@keyframes skel{0%{background-position:100% 50%;}100%{background-position:0 50%;}}
.marker-tt-link{display:block;color:var(--gold);font-size:10px;margin-top:3px;text-decoration:none;}

/* ---------- map body: map + layer toggles side by side (new) ---------- */
.map-body{display:grid;grid-template-columns:1fr 190px;gap:12px;align-items:start;}
.layers-panel{background:#070a10;border:1px solid var(--border-soft);border-radius:8px;padding:10px;
  display:flex;flex-direction:column;gap:2px;}
.layers-hd{font-family:var(--mono);font-size:10px;letter-spacing:.08em;color:var(--text-faint);
  font-weight:700;margin-bottom:6px;}
.layer-toggle{display:flex;align-items:center;gap:8px;font-size:11px;color:var(--text-dim);
  padding:6px 4px;border-radius:5px;cursor:pointer;user-select:none;}
.layer-toggle:hover{background:var(--panel2);color:var(--text);}
.layer-toggle input{accent-color:var(--gold);width:13px;height:13px;flex:none;}
.layer-toggle i{width:8px;height:8px;border-radius:50%;display:inline-block;flex:none;}
@media (max-width:900px){.map-body{grid-template-columns:1fr;}}

"""

EXTRA_CSS += '''
.main-grid{display:grid;grid-template-columns:minmax(0,1fr) 330px;gap:14px;align-items:stretch;}
.ticker-panel{background:var(--panel);border:1px solid var(--border);border-radius:var(--radius);display:flex;flex-direction:column;min-height:0;overflow:hidden;}
.ticker-hd{display:flex;align-items:center;gap:8px;padding:14px 16px 10px;flex:none;}
.live-dot{width:8px;height:8px;border-radius:50%;background:var(--red);box-shadow:0 0 8px 1px var(--red);animation:blink 1.6s ease-in-out infinite;}
.ticker-viewport{flex:1;min-height:600px;overflow:hidden;position:relative;padding:0 4px;
  mask-image:linear-gradient(to bottom,transparent 0,black 24px,black calc(100% - 24px),transparent 100%);
  -webkit-mask-image:linear-gradient(to bottom,transparent 0,black 24px,black calc(100% - 24px),transparent 100%);}
.ticker-track{display:flex;flex-direction:column;animation:tickerScroll 110s linear infinite;}
.ticker-track.paused{animation-play-state:paused;}
@keyframes tickerScroll{from{transform:translateY(0);}to{transform:translateY(-50%);}}
.tick-item{padding:10px 12px;border-bottom:1px solid var(--border-soft);}
.tick-item .tag{display:inline-block;font-family:var(--mono);font-size:9px;font-weight:700;padding:1.5px 6px;border-radius:4px;margin-right:6px;color:#0a0e17;}
.tick-item .txt{font-size:12px;line-height:1.45;color:var(--text);display:block;margin-top:5px;}
.tick-item .meta{font-family:var(--mono);font-size:9.5px;color:var(--text-faint);margin-top:5px;}
.ticker-ftr{flex:none;padding:9px 16px;border-top:1px solid var(--border-soft);font-size:10px;color:var(--text-faint);text-align:center;}
.dw-select{margin-left:auto;background:var(--panel2);color:var(--text);border:1px solid var(--border);border-radius:6px;padding:4px 8px;font-size:11px;}
.dw-status{font-family:var(--mono);font-size:10px;color:var(--text-faint);margin:-4px 0 10px;}
@media (max-width:1180px){.main-grid{grid-template-columns:1fr;}}
@media (prefers-reduced-motion: reduce){.ticker-track,.live-dot{animation:none !important;}}
'''
CSS = old_css + EXTRA_CSS + ".disputed-outline{fill:rgba(240,180,41,0.12);stroke:#f0b429;stroke-width:1.4;stroke-dasharray:4 3;}\n.state-line{fill:none;stroke:#8fb3d9;stroke-width:0.9;stroke-opacity:0.85;}\n.state-label{fill:#cfe3f5;font-size:11px;text-anchor:middle;paint-order:stroke;stroke:#0a0e17;stroke-width:3px;}\n.sea-label{fill:#7fb3d5;font-size:14px;font-style:italic;letter-spacing:.08em;text-anchor:middle;}\n.river-line{fill:none;stroke:#3f7fbf;stroke-width:1.3;stroke-opacity:0.85;}\n.place-dot{fill:#e8eef7;}\n.place-label{fill:#e8eef7;font-size:11px;paint-order:stroke;stroke:#0a0e17;stroke-width:3px;}\n.state-line.ne{fill:rgba(96,165,250,0.10);stroke:#7fb8ff;stroke-width:1.4;}\n.state-line.margin{stroke-dasharray:6 4;stroke:#64748b;fill:none;}\n.country.focus{fill:#1d3a5c;}\n\n"

# ---------- static map: country paths only (geography is not "live data") ----------
R_SWEEP = 470
def _sweep_pt(deg):
    r = math.radians(deg)
    return pivot_x + R_SWEEP * math.cos(r), pivot_y + R_SWEEP * math.sin(r)
_x1, _y1 = _sweep_pt(-100); _x2, _y2 = _sweep_pt(-58)
RADAR_SVG = (f'<g id="radarSweep" data-cx="{pivot_x:.1f}" data-cy="{pivot_y:.1f}" transform="rotate(0 {pivot_x:.1f} {pivot_y:.1f})">'
             f'<path d="M {pivot_x:.1f} {pivot_y:.1f} L {_x1:.1f} {_y1:.1f} A {R_SWEEP} {R_SWEEP} 0 0 1 {_x2:.1f} {_y2:.1f} Z" fill="url(#sweepGrad)"/></g>')
REGION_FOCUS = {"Australia", "New Zealand", "Papua New Guinea", "Solomon Islands", "Vanuatu", "New Caledonia", "Fiji", "Samoa", "Tonga", "Tuvalu", "Nauru", "Kiribati", "Marshall Islands", "Federated States of Micronesia", "Palau", "Guam", "Northern Mariana Islands", "American Samoa", "Cook Islands", "Niue", "Wallis and Futuna", "Norfolk Island", "East Timor", "Indonesia"}
country_paths = "\n".join(f'<path class="country{" focus" if c["name"] in REGION_FOCUS else ""}" d="{c["d"]}" />' for c in countries)
kashmir_overlay = json.load(open(f"{BASE}/data/kashmir_paths.json"))
disputed_overlay = json.load(open(f"{BASE}/data/disputed_paths.json"))
def _esc(s): return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
regions = json.load(open(f"{BASE}/data/regions.json"))
KIND_CLASS = {"admin1": ""}
LABELLED = set()
rivers = json.load(open(f"{BASE}/data/rivers.json"))
places = json.load(open(f"{BASE}/data/places.json"))
rivers_svg = "\n".join(f'<path class="river-line" d="{r["d"]}"><title>{_esc(r["name"] or "river")}</title></path>' for r in rivers)
places_svg = "\n".join(f'<circle class="place-dot" cx="{p["x"]}" cy="{p["y"]}" r="{3 if p["country"] == "Bangladesh" else 2.5}"/>'
                       f'<text class="place-label" x="{p["x"] + 6}" y="{p["y"] + 3}">{_esc(p["name"])}</text>' for p in places)
sea_labels = json.load(open(f"{BASE}/data/sea_labels.json"))
states_svg = "\n".join(f'<path class="state-line{KIND_CLASS.get(s.get('kind', ''), '')}" d="{s["d"]}"><title>{_esc(s["name"])} </title></path>'
                       f'<text class="state-label" x="{s["x"]}" y="{s["y"]}">{_esc(s["name"]) if s["name"] in LABELLED else ""}</text>' for s in regions)
sea_svg = "\n".join(f'<text class="sea-label" x="{s["x"]}" y="{s["y"]}">{_esc(s["name"])}</text>' for s in sea_labels)
disputed_svg = "\n".join(f'<path class="disputed-outline" d="{t["d"]}"><title>{t["name"]}</title></path>' for t in disputed_overlay)
kashmir_svg = "\n".join(f'<path class="kashmir" d="{k["d"]}"><title>{k["name"]}</title></path>' for k in kashmir_overlay)

MAP_SVG = f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" id="mapSvg" role="img" aria-label="Tactical map of Australia, New Zealand and the Pacific">
  <defs>
    <linearGradient id="sweepGrad" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#c9a35c" stop-opacity="0.38"/><stop offset="100%" stop-color="#c9a35c" stop-opacity="0"/></linearGradient>
    <radialGradient id="oceanGrad" cx="50%" cy="35%" r="75%">
      <stop offset="0%" stop-color="#0b1420"/>
      <stop offset="100%" stop-color="#05080d"/>
    </radialGradient>
  </defs>
  <rect x="0" y="0" width="{W}" height="{H}" fill="url(#oceanGrad)"/>
  <g class="countries">{country_paths}</g>
  <g class="disputed-overlay">{kashmir_svg}</g>
  <g class="disputed-overlay">{disputed_svg}</g>
  <g class="rivers-layer">{rivers_svg}</g>
  <g class="states-layer">{states_svg}</g>
  <g class="places-layer">{places_svg}</g>
  <g class="sea-layer">{sea_svg}</g>
  {RADAR_SVG}
  <g class="markers" id="markerLayer"></g>
</svg>'''

LOGO_SVG = '''<svg width="34" height="34" viewBox="0 0 34 34" fill="none">
  <circle cx="17" cy="17" r="15.5" stroke="#c9a35c" stroke-width="1.3" opacity="0.55"/>
  <circle cx="17" cy="17" r="10.5" stroke="#c9a35c" stroke-width="1.3" opacity="0.75"/>
  <circle cx="17" cy="17" r="2.6" fill="#c9a35c"/>
  <path d="M17 1.5V8.5M17 25.5V32.5M1.5 17H8.5M25.5 17H32.5" stroke="#c9a35c" stroke-width="1.3" opacity="0.85"/>
</svg>'''
SEARCH_ICON = '''<svg width="15" height="15" viewBox="0 0 24 24" fill="none">
  <circle cx="11" cy="11" r="7" stroke="#8b9bb4" stroke-width="2"/>
  <path d="M21 21l-4.3-4.3" stroke="#8b9bb4" stroke-width="2" stroke-linecap="round"/></svg>'''
REFRESH_ICON = '''<svg width="13" height="13" viewBox="0 0 24 24" fill="none">
  <path d="M21 12a9 9 0 11-2.6-6.4M21 4v6h-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'''

LEGEND_ITEMS = [
    ("capital","#c9a35c","Capital or territorial capital"),
    ("foreign_base","#3b82f6","Allied or joint base (US, UK, France) or base with foreign access"),
    ("navy_base","#f97316","Navy base or fleet headquarters"),
    ("submarine_base","#fb923c","Submarine base"),
    ("missile_base","#fb7185","Missile test range"),
    ("nuclear_site","#facc15","Research reactor, waste site, uranium mine or test site"),
    ("defense_industry","#84cc16","Shipyard or defence industry site (not verified where noted)"),
    ("space_site","#34d399","Launch, test or tracking site"),
    ("cantonment","#94a3b8","Command headquarters or station"),
    ("cyber_hub","#e879f9","Signals, cyber or seismic monitoring site"),
    ("flashpoint","#ef4444","Dispute or insurgency (reported)"),
    ("chokepoint","#22d3ee","Chokepoint or strait"),
    ("pipeline","#a78bfa","LNG plant, gas pipeline or subsea cable"),
    ("air_base","#c4b5fd","Air base or military-named airfield"),
    ("airport","#38bdf8","Civil airport (large and medium)"),
    ("seaport","#22c55e","Seaport"),
    ("hazard","#fbbf24","Live earthquake (USGS)"),
    ("custom","#ffffff","Your plotted marker")]
legend_html = "\n".join(f'<span><i style="background:{c}"></i>{l}</span>' for _,c,l in LEGEND_ITEMS)

PANEL_DEFS = []
PANEL_DEFS2 = []
PANEL_DEFS3 = []

def panel_shell(cat, title, color):
    return f'''<div class="panel" data-cat="{cat}">
      <div class="panel-hd"><span class="panel-dot" style="background:{color};color:{color}"></span>
      <span class="panel-title">{title}</span><span class="panel-count" id="count-{cat}">&hellip;</span></div>
      <div class="panel-items" id="items-{cat}"><div class="skel" style="height:60px;"></div></div>
    </div>'''

panels_row1 = "\n".join(panel_shell(*p) for p in PANEL_DEFS)
panels_row2 = "\n".join(panel_shell(*p) for p in PANEL_DEFS2)
panels_row3 = "\n".join(panel_shell(*p) for p in PANEL_DEFS3)





METHOD_PANEL = '''<div class="panel">
  <div class="panel-hd"><span class="panel-dot" style="background:var(--text-faint);color:var(--text-faint)"></span>
  <span class="panel-title">Connector Status</span></div>
  <div class="connector-strip" id="connectorStrip"><div class="skel" style="height:20px;width:100%;"></div></div>
  <div class="item" style="margin-top:12px;border-left-color:var(--gold-soft);">
    <div class="txt" id="methodNote">Loading&hellip;</div>
  </div>
</div>'''

GEAR_ICON = '''<svg width="15" height="15" viewBox="0 0 24 24" fill="none">
  <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" stroke="currentColor" stroke-width="2"/>
  <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 11-4 0v-.09a1.65 1.65 0 00-1-1.51 1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 11-2.83-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 110-4h.09a1.65 1.65 0 001.51-1 1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 112.83-2.83l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 114 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 112.83 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 110 4h-.09a1.65 1.65 0 00-1.51 1z" stroke="currentColor" stroke-width="1.6"/>
</svg>'''

PLOT_ICON = '''<svg width="15" height="15" viewBox="0 0 24 24" fill="none">
  <path d="M12 2C8 2 5 5.5 5 9.5C5 14.5 12 22 12 22S19 14.5 19 9.5C19 5.5 16 2 12 2Z" stroke="currentColor" stroke-width="1.8"/>
  <circle cx="12" cy="9.5" r="2.3" fill="currentColor"/>
</svg>'''

HEADER = f'''<header class="hdr">
  <div class="brand">{LOGO_SVG}
    <div class="brand-text"><div class="brand-title">AUSTRALIA Dashboard</div>
      <div class="brand-sub"Australia, New Zealand &amp; the Pacific &middot; Open-Source Intelligence</div></div>
  </div>
  <div class="search-wrap">{SEARCH_ICON}
    <input id="filterInput" type="text" placeholder="Filter dashboard (e.g. Pine Gap, Stirling, Lombrum)&hellip;" autocomplete="off"/>
  </div>
  <div class="hdr-right">
    <div class="window-toggle" id="windowToggle">
      <button class="wt-btn active" data-window="72h">Last 72h</button>
      <button class="wt-btn" data-window="all">All Time</button>
    </div>
    <span class="status-pill offline" id="statusPill"><span class="dot"></span><span id="statusPillText">Checking&hellip;</span></span>
    <button class="icon-btn" id="plotBtn" title="Plot a location on the map">{PLOT_ICON}</button>
    <button class="icon-btn" id="settingsBtn" title="API Keys">{GEAR_ICON}</button>
    <button class="refresh-btn" id="refreshBtn">{REFRESH_ICON}<span>Refresh</span></button>
    <div class="hdr-clock"><b id="snapClock">&mdash;</b><span id="snapDate">&nbsp;</span></div>
  </div>
</header>

<div class="modal-backdrop" id="settingsBackdrop">
  <div class="modal">
    <h3>API Keys</h3>
    <div class="modal-sub">Stored AES-256-GCM encrypted on this machine (data/secrets.enc), never sent anywhere
      but this local server. GDELT, RSS, and USGS already work with zero keys - these three are optional,
      for more sources.</div>
    <div id="keyFields">Loading&hellip;</div>
    <div class="modal-actions">
      <button class="btn-primary" id="saveKeysBtn">Save &amp; reconnect</button>
      <button class="btn-secondary" id="closeSettingsBtn">Close</button>
    </div>
    <div class="modal-msg" id="settingsMsg"></div>
  </div>
</div>

<div class="modal-backdrop" id="plotBackdrop">
  <div class="modal">
    <h3>Plot a location</h3>
    <div class="modal-sub">Adds a marker at the coordinates you enter, with your remark - saved locally in
      data/custom_markers.json on this machine, never sent anywhere else.</div>
    <label>Label</label><input type="text" id="plotLabel" placeholder="e.g. Reported incident site"/>
    <label>Remark / comment (optional)</label><input type="text" id="plotRemark" placeholder="e.g. Source, context, notes"/>
    <label>Latitude</label><input type="text" id="plotLat" placeholder="e.g. 30.5"/>
    <label>Longitude</label><input type="text" id="plotLon" placeholder="e.g. 114.3"/>
    <div class="modal-actions">
      <button class="btn-primary" id="plotAddBtn">Add marker</button>
      <button class="btn-secondary" id="plotCloseBtn">Close</button>
    </div>
    <div class="modal-msg" id="plotMsg"></div>
    <div id="customMarkersList" style="margin-top:14px;max-height:200px;overflow-y:auto;"></div>
  </div>
</div>'''

KPI_ROW = '''<div class="kpi-row" id="kpiRow">
  <div class="kpi" style="--accent:var(--gold)"><div class="eyebrow">Map markers</div><div class="num" id="kpi-markers"><span class="skel" style="display:inline-block;width:30px;height:24px;"></span></div><div class="sub">plotted on the tactical map</div></div>
  <div class="kpi" style="--accent:var(--amber)"><div class="eyebrow">Military signals</div><div class="num" id="kpi-military">&hellip;</div><div class="sub">current items in feed</div></div>
  <div class="kpi" style="--accent:var(--cyan-h)"><div class="eyebrow">Economic &amp; trade</div><div class="num" id="kpi-economic">&hellip;</div><div class="sub">current items in feed</div></div>
  <div class="kpi" style="--accent:var(--green)"><div class="eyebrow">Diplomatic events</div><div class="num" id="kpi-political">&hellip;</div><div class="sub">current items in feed</div></div>
  <div class="kpi" style="--accent:var(--violet)"><div class="eyebrow">Hazard alerts</div><div class="num" id="kpi-hazard">&hellip;</div><div class="sub">current items in feed</div></div>
  <div class="kpi" style="--accent:var(--red)"><div class="eyebrow">Dark-web claims (region)</div><div class="num" id="kpi-darkweb">&hellip;</div><div class="sub">leak-site, Telegram and Tor sources</div></div>
</div>'''

# Only the layers this region has data for. A toggle with nothing behind it is not shown
# (a test fails the build if a toggle has no data), so every button on the page works.
# Only the layers this region has data for. A toggle with nothing behind it is not shown
# (a test fails the build if a toggle has no data), so every button on the page works.
# Only the layers this region has data for. A toggle with nothing behind it is not shown
# (a test fails the build if a toggle has no data), so every button on the page works.
# Only the layers this region has data for. A toggle with nothing behind it is not shown
# (a test fails the build if a toggle has no data), so every button on the page works.
# Only the layers Myanmar has data for. A toggle with nothing behind it is not shown (a test fails the build
# if a toggle has no data), so every button on the page works. No nuclear layer: Myanmar has no operating plant.
# Only the layers Bangladesh has data for. A toggle with nothing behind it is not shown (a test fails the build
# if a toggle has no data), so every button on the page works.
# Only the layers this region has data for. A toggle with nothing behind it is not shown (a test fails the build
# if a toggle has no data), so every button on the page works. No naval or nuclear layer: the north-east has neither.
# Only the layers this frame has data for. A toggle with nothing behind it is not shown (a test fails the build
# if a toggle has no data). No naval or nuclear layer: Jammu and Kashmir has neither. Indian Army units and
# deployment are not plotted; Air Force stations sit in the airbase toggle, which can be hidden.
LAYER_CATS = ["capital","foreign_base","navy_base","submarine_base","missile_base","nuclear_site","defense_industry","space_site","cantonment","cyber_hub","flashpoint","chokepoint","pipeline","hazard","custom"]
INFRA_LAYER_CATS = ["air_base","airport","seaport"]

def toggle_row(cat, color, label, checked=True):
    chk = "checked" if checked else ""
    return (f'<label class="layer-toggle"><input type="checkbox" class="layer-cb" data-layer="{cat}" {chk}/>'
            f'<i style="background:{color}"></i>{label}</label>')

_legend_by_cat = {c: (col, lab) for c, col, lab in LEGEND_ITEMS}
layer_toggles_html = "\n".join(
    toggle_row(cat, *_legend_by_cat[cat]) for cat in LAYER_CATS
)
# infrastructure layers default OFF (airports especially - 69 dots is a lot
# to show before the user's asked for it); one click each to reveal.
infra_toggles_html = "\n".join(
    toggle_row(cat, *_legend_by_cat[cat], checked=True) for cat in INFRA_LAYER_CATS
)

MAP_PANEL = f'''<div class="map-panel">
  <div class="panel-hd"><span class="panel-dot" style="background:var(--gold);color:var(--gold)"></span>
    <span class="panel-title">Tactical Map &mdash; Australia, New Zealand and the Pacific</span>
    <span class="panel-count" id="count-markers">&hellip;</span></div>
  <div class="map-body">
    <div class="map-svg-wrap" id="mapWrap">{MAP_SVG}<div class="map-tip" id="mapTip"></div></div>
    <div class="layers-panel">
      <div class="layers-hd">LAYERS</div>
      {layer_toggles_html}
      <div class="layers-hd" style="margin-top:8px;">INFRASTRUCTURE</div>
      {infra_toggles_html}
      <div class="infra-note" id="infraNote">&hellip;</div>
      <div class="infra-note"><b>Map basis:</b> Lambert azimuthal equal-area projection centred on 150 degrees east and 25 degrees south, drawn from Natural Earth country boundaries, state, region and province lines, rivers and sea labels. The frame runs from 105 degrees east to 202 degrees east (the Pacific is drawn across the date line, so Samoa, Tonga, Niue and the Cook Islands sit inside the region) and from 55 degrees south to 16 degrees north. Australia, New Zealand, Papua New Guinea, the Pacific states and the Indonesian islands are shaded; neighbouring countries are outlines. India is outside the frame and nothing about India is plotted. Disputed or contested areas are described, not settled: the Spratly Islands and Scarborough Reef (claimed by several states; outlined only), West Papua (Indonesian sovereignty, contested by insurgents), Bougainville (autonomy, with an independence vote pending in PNG's Parliament), and the Chatham and Cook islands' status as self-governing states in free association. Most positions are approximate; each tooltip gives its source and whether it is verified in this build. Incidents and displacement figures are reported claims. Events reflect reports up to 10 October 2026.</div>
    </div>
  </div>
</div>'''

TICKER_HTML = '''<aside class="ticker-panel">
  <div class="ticker-hd"><span class="live-dot"></span><span class="panel-title">Latest News (running)</span>
    <span class="panel-count" id="count-ticker">&hellip;</span></div>
  <div class="ticker-viewport" id="tickerViewport"><div class="ticker-track" id="tickerTrack">
    <div class="skel" style="height:60px;margin:10px;"></div></div></div>
  <div class="ticker-ftr">Hover to pause &middot; moves bottom&rarr;top &middot; unlocated news only (located news is on the map)</div>
</aside>'''

DARKWEB_PANEL = '''<div class="panel darkweb-panel">
  <div class="panel-hd"><span class="panel-dot" style="background:var(--red);color:var(--red)"></span>
  <span class="panel-title">Dark Web &amp; Threat Intel</span><span class="panel-count" id="count-darkweb">&hellip;</span>
  <select id="darkwebFilter" class="dw-select"><option value="all">All claims</option><option value="region">Regional victims only</option></select></div>
  <div class="dw-status" id="darkwebStatus"></div>
  <div class="panel-items" id="items-darkweb" style="max-height:460px;overflow-y:auto;"><div class="skel" style="height:60px;"></div></div>
  <div class="infra-note">Sources: Ransomware.live (public leak-site claims - group claims, not verified facts) and any defensive Telegram channels listed in data/telegram_channels.json. This dashboard does not access .onion sites, stealer-log or carding markets.</div>
</div>'''

HEADINGS = [
  ("geo", "Geopolitical & Diplomatic", "var(--green)"),
  ("milops", "Military Operations & Force Posture", "var(--amber)"),
  ("arms", "Strategic Arms & Nuclear Program", "var(--magenta)"),
  ("naval", "Naval & Maritime Security", "var(--cyan-h)"),
  ("scs", "Maritime Chokepoints & Sea Lanes", "var(--cyan-h)"),
  ("air", "Air Force & Aviation", "var(--violet)"),
  ("space", "Space Tech & Aerospace", "var(--cyan-h)"),
  ("tech", "Critical Tech & AI Governance", "var(--gold)"),
  ("cyber", "Cyber Espionage & APTs", "var(--red)"),
  ("darkweb", "Darkweb & Threat Intel", "var(--red)"),
  ("econ", "Economic & Trade (energy, shipping)", "var(--cyan-h)"),
  ("mss", "Internal Security & Intelligence Operations", "var(--amber)"),
  ("social", "Social Pulse & Public Sentiment", "var(--gold)"),
  ("wellbeing", "Happiness & Wellbeing Indices", "var(--magenta)"),
  ("hazard", "Natural Hazards & Environmental Risks", "var(--violet)"),
]

WELLBEING_STATIC = '''<div style="font-size:12px;color:var(--text-dim);line-height:1.6;margin-bottom:8px;">
  <b style="color:var(--text);">World Happiness Report 2026:</b> country ranks for Australia, New Zealand and the Pacific in this frame were not verified in this build. Check the report directly.</div>
  <div class="meta" style="font-size:10.5px;color:var(--text-faint);">Annual report - static reference, not a live feed.</div>'''

DARKWEB_PANEL_HTML = '''<div class="panel darkweb-panel" data-cat="darkweb" style="grid-column:1/-1;">
  <div class="panel-hd"><span class="panel-dot" style="background:var(--red);color:var(--red)"></span>
  <span class="panel-title">Darkweb &amp; Threat Intel</span><span class="panel-count" id="count-darkweb">&hellip;</span>
  <select id="darkwebFilter" class="dw-select"><option value="all">All claims</option><option value="region">Regional victims only</option></select></div>
  <div class="dw-status" id="darkwebStatus"></div>
  <div class="panel-items" id="items-darkweb" style="max-height:460px;overflow-y:auto;"><div class="skel" style="height:60px;"></div></div>
  <div class="infra-note"><b>Sources:</b> Ransomware.live (leak-site claims - group claims, not verified facts); Telegram threat-intel channels; and dark-web RSS sources reached through Tor that you verify yourself (data/onion_sources.json).
  <br/><b>To read onion sources</b> you need Tor on this PC: open <b>Tor Browser</b> (it listens on port 9150) or install and start the <b>Tor service</b> (port 9050). Keep it running, then press Refresh. Nothing is needed for the clear-web and Telegram sources. This dashboard never opens .onion pages in a browser and does not search or crawl the dark web.</div>
</div>'''


def heading_panel(key, title, color):
    extra = WELLBEING_STATIC if key == "wellbeing" else ""
    return (f'''<div class="panel" data-cat="{key}">
      <div class="panel-hd"><span class="panel-dot" style="background:{color};color:{color}"></span>
      <span class="panel-title">{title}</span><span class="panel-count" id="count-{key}">&hellip;</span></div>
      {extra}<div class="panel-items" id="items-{key}"><div class="skel" style="height:60px;"></div></div>
    </div>''')


def _panel_grid():
    rows, buf = [], []
    for key, title, color in HEADINGS:
        if key == "darkweb":
            if buf:
                rows.append(f'<div class="panel-row" style="grid-template-columns:repeat({len(buf)},1fr);">' + "".join(buf) + "</div>")
                buf = []
            rows.append('<div class="panel-row" style="grid-template-columns:1fr;">' + DARKWEB_PANEL_HTML + "</div>")
            continue
        buf.append(heading_panel(key, title, color))
        if len(buf) == 3:
            rows.append('<div class="panel-row">' + "".join(buf) + "</div>")
            buf = []
    if buf:
        rows.append(f'<div class="panel-row" style="grid-template-columns:repeat({len(buf)},1fr);">' + "".join(buf) + "</div>")
    rows.append('<div class="panel-row" style="grid-template-columns:1fr;">' + METHOD_PANEL + "</div>")
    return "\n".join(rows)


LEFT_COL = f'''<div class="left-col">
  {MAP_PANEL}
  <div class="offline-banner" id="offlineBanner"></div>
  {_panel_grid()}
</div>'''

FOOTER = '''<div class="dash-footer">
  <div><span class="brandline">AUSTRALIA Dashboard</span> &middot; By Aryan &middot; @EPureNest</div>
  <div id="footerNote">Loading&hellip;</div>
</div>'''

print("Sections built OK")

SEED_JSON_STR = json.dumps(seed, ensure_ascii=False)

CAT_META = {
    "military": {"label": "Military & Strategic", "color": "var(--amber)"},
    "economic": {"label": "Economic & Trade", "color": "var(--cyan-h)"},
    "political": {"label": "Political & Diplomatic", "color": "var(--green)"},
    "hazard": {"label": "Natural Hazards", "color": "var(--violet)"},
    "aviation": {"label": "Aviation & Maritime Notices", "color": "var(--violet)"},
    "strategic": {"label": "Strategic & Arms Monitoring", "color": "var(--magenta)"},
    "cyber": {"label": "Cyber & MSS", "color": "var(--red)"},
    "space": {"label": "Space Program", "color": "var(--cyan-h)"},
    "social_local": {"label": "Social pulse", "color": "var(--gold)"},
    "social_global": {"label": "Social pulse (global)", "color": "var(--gold)"},
}
CAT_META_JSON = json.dumps(CAT_META)

SCRIPT = r"""
(function(){
  "use strict";

  const PROJ = __PROJ__;
  const HEADING_KEYS = __HKEYS__;
  const SEED_DATA = __SEED__;
  const CAT_META = __CATMETA__;

  function escapeHtml(s){
    if(s === null || s === undefined) return "";
    return String(s).replace(/[&<>"']/g, function(c){
      return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];
    });
  }

  function project(lon, lat){
    const phi = lat * Math.PI/180, lam = lon * Math.PI/180;
    const dl = lam - PROJ.lam0;
    const cosc = PROJ.sinp0 * Math.sin(phi) + PROJ.cosp0 * Math.cos(phi) * Math.cos(dl);
    const k = Math.sqrt(2 / (1 + cosc));
    const x = k * Math.cos(phi) * Math.sin(dl);
    const y = k * (PROJ.cosp0 * Math.sin(phi) - PROJ.sinp0 * Math.cos(phi) * Math.cos(dl));
    return [PROJ.translate[0] + x*PROJ.scale, PROJ.translate[1] - y*PROJ.scale];
  }

  const MARKER_COLOR = {"capital": "#c9a35c", "flashpoint": "#ef5354", "chokepoint": "#f59e0b", "hazard": "#58c4ff", "submarine_base": "#fb923c", "navy_base": "#f97316", "carrier_port": "#fdba74", "cantonment": "#c084fc", "nuclear_site": "#facc15", "space_site": "#06b6d4", "satellite_station": "#60a5fa", "defense_industry": "#84cc16", "pipeline": "#4ade80", "nuclear_plant": "#eab308", "air_base": "#a78bfa", "airport": "#38bdf8", "seaport": "#22c55e", "custom": "#ffffff"};

  // ---------------- 72h / All-time window ----------------
  let timeWindow = "72h";   // default per request; stays until the user picks otherwise
  const WINDOW_MS = 72 * 3600 * 1000;

  // Robust across the formats the connectors actually emit: ISO, RFC-822 (RSS
  // "published"), GDELT "YYYYMMDDTHHMMSSZ", and USGS epoch-ms as a string.
  function parseItemDate(s){
    if(!s) return null;
    if(/^\d{13}$/.test(String(s))) return new Date(parseInt(s, 10));
    const g = /^(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z$/.exec(String(s));
    if(g) return new Date(Date.UTC(+g[1], +g[2]-1, +g[3], +g[4], +g[5], +g[6]));
    const d = new Date(s);
    return isNaN(d.getTime()) ? null : d;
  }
  function inWindow(it){
    if(timeWindow === "all") return true;
    const d = parseItemDate(it.date);
    // Strict by design: an item with no verifiable timestamp (background
    // reference entries dated "ongoing"/"background", or a date string that
    // can't be parsed) is NOT shown in the 72h view - claiming it's "last
    // 72 hours" news when nothing proves that would break the one rule this
    // toggle exists to enforce. Switch to All Time to see them.
    if(!d) return false;
    return (Date.now() - d.getTime()) <= WINDOW_MS;
  }
  function windowedCats(cats){
    const out = {};
    Object.keys(cats).forEach(function(k){ out[k] = (cats[k]||[]).filter(inWindow); });
    return out;
  }

  let currentData = null, isLive = false;
  // start activeLayers from whatever the checkboxes actually show as checked
  // in the HTML (event layers on, infrastructure layers off by default),
  // rather than hardcoding it separately and risking the two going out of sync
  let activeLayers = new Set(
    Array.from(document.querySelectorAll(".layer-cb")).filter(cb => cb.checked).map(cb => cb.dataset.layer)
  );
  let refreshTimer = null;
  let customMarkers = [];

  // ---------------- data loading ----------------
  async function loadData(manual){
    const btn = document.getElementById("refreshBtn");
    if(manual && btn){ btn.classList.add("spinning"); btn.disabled = true; }
    try {
      const url = manual ? "/api/refresh" : "/api/snapshot";
      const opts = manual ? {method:"POST"} : {cache:"no-store"};
      const res = await fetch(url, opts);
      if(!res.ok){
        if(res.status === 429){ const j = await res.json().catch(()=>({})); throw new Error(j.error || "rate limited"); }
        // try to surface the server's own error detail (e.g. a specific
        // connector/rendering failure), not just the bare status code
        const body = await res.json().catch(()=>null);
        throw new Error(body && body.error ? ("HTTP " + res.status + ": " + body.error) : ("HTTP " + res.status));
      }
      const data = await res.json();
      currentData = data; isLive = true;
      render(data, true, null);
    } catch(e) {
      currentData = SEED_DATA; isLive = false;
      render(SEED_DATA, false, e.message);
    } finally {
      if(btn){ btn.classList.remove("spinning"); btn.disabled = false; }
    }
  }

  // ---------------- render orchestration ----------------
  function render(data, live, errMsg){
    // apply the 72h / All-time window ONCE, then everything below (panels,
    // KPIs, map dots) reads from the same filtered view - they can't disagree
    const view = Object.assign({}, data, {items_by_category: windowedCats(data.items_by_category || {})});
    view.markers = (data.markers || []).map(function(m){
      return Object.assign({}, m, {linked_items: (m.linked_items || []).filter(inWindow)});
    });
    renderStatusBar(live, view, errMsg);
    renderKPIs(view);
    renderMarkers(view.markers, view.items_by_category);
    renderPanels(view.items_by_category);
    renderTicker(view);
    renderDarkWeb(view);
    renderConnectorStrip(view.connector_status || [], live);
    applyFilter(); // keep an active search query applied across re-renders
  }

  function renderStatusBar(live, data, errMsg){
    const pill = document.getElementById("statusPill");
    const txt = document.getElementById("statusPillText");
    const banner = document.getElementById("offlineBanner");
    const footerNote = document.getElementById("footerNote");
    const snapDate = document.getElementById("snapDate");
    if(live){
      pill.className = "status-pill live"; txt.textContent = "Live backend";
      banner.classList.remove("show");
      const when = data.updated_at ? new Date(data.updated_at*1000).toLocaleTimeString() : "just now";
      snapDate.textContent = "Backend last polled " + when;
      footerNote.innerHTML = "Live backend connected &middot; " + (data.total_items||0) + " items in feed &middot; not investment/operational advice, verify time-critical items against primary sources";
    } else {
      pill.className = "status-pill offline"; txt.textContent = "Offline snapshot";
      banner.classList.add("show");
      banner.innerHTML = "<b>Backend not reachable" + (errMsg ? " (" + escapeHtml(errMsg) + ")" : "") +
        "</b> &mdash; showing the embedded Aug 10, 2026 research snapshot instead of live data. " +
        "Run <code>python run.py</code> and reload this page to connect the real backend.";
      snapDate.textContent = "Offline snapshot - Aug 10, 2026";
      footerNote.textContent = "Offline snapshot mode - start the Python backend for live data.";
    }
  }

  function countItems(cats, dataObj){
    let n = 0;
    cats.forEach(c => n += (dataObj[c]||[]).length);
    return n;
  }

  function renderKPIs(data){
    const cats = data.items_by_category || {};
    document.getElementById("kpi-markers").textContent = (data.markers||[]).length;
    document.getElementById("kpi-military").textContent = (cats.milops||[]).length;
    document.getElementById("kpi-economic").textContent = (cats.econ||[]).length;
    document.getElementById("kpi-political").textContent = (cats.geo||[]).length;
    document.getElementById("kpi-hazard").textContent = (cats.hazard||[]).length;
    document.getElementById("kpi-darkweb").textContent = (cats.darkweb||[]).length;
    document.getElementById("count-markers").textContent = (data.markers||[]).length + " sites";
    const infraNote = document.getElementById("infraNote");
    if(infraNote){
      const info = data.infrastructure || {};
      if(isLive){
        infraNote.textContent = (info.airport_count||0) + " airports live from OurAirports (CC0 dataset) + " +
          "verified seaports/naval bases/defense HQs. Real-time ship/submarine positions aren't shown - " +
          "no open source publishes that for any navy (see README).";
      } else {
        infraNote.textContent = "Offline snapshot: infrastructure markers frozen from build time, not live.";
      }
    }
  }

  // ---------------- map markers ----------------
  function addMarkerEl(layer, m, color, extra){
    const [x,y] = project(m.lon, m.lat);
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    g.setAttribute("class", "marker");
    g.setAttribute("transform", "translate(" + x.toFixed(1) + "," + y.toFixed(1) + ")");
    g.dataset.name = m.name; g.dataset.note = m.note || "";
    g.dataset.source = m.source || ""; g.dataset.date = m.date || "";
    g.dataset.color = color;
    g.dataset.linked = JSON.stringify(m.linked_items || []);
    const pulse = (m.linked_items && m.linked_items.length) || (extra && extra.pulse);
    g.innerHTML = (pulse ? '<circle class="pulse" r="5" fill="none" stroke="'+color+'" stroke-width="1.6"/>' : '') +
                  '<circle class="core" r="3.4" fill="'+color+'"/>';
    layer.appendChild(g);
  }

  function renderMarkers(markers, cats){
    const layer = document.getElementById("markerLayer");
    if(!layer) return;
    layer.innerHTML = "";
    // 1. named strategic sites (pulse when a windowed headline mentions them)
    (markers || []).forEach(function(m){
      if(!activeLayers.has(m.cat)) return;
      addMarkerEl(layer, m, MARKER_COLOR[m.cat] || "#c9a35c");
    });
    // 2. any windowed item that carries its OWN coordinates (USGS quakes) -
    // a real lat/lon from the source, not a guess
    if(activeLayers.has("hazard")){
      Object.keys(cats || {}).forEach(function(k){
        (cats[k] || []).forEach(function(it){
          if(typeof it.lat === "number" && typeof it.lon === "number"){
            addMarkerEl(layer, {name: it.label, note: it.text, source: it.source, date: it.date,
              lat: it.lat, lon: it.lon, linked_items: []}, MARKER_COLOR.hazard, {pulse: true});
          }
        });
      });
    }
    // 3. the user's own plotted markers
    if(activeLayers.has("custom")){
      customMarkers.forEach(function(cm){
        addMarkerEl(layer, {name: cm.label, note: cm.remark || "(no remark)", source: "You",
          date: cm.added, lat: cm.lat, lon: cm.lon, linked_items: []}, MARKER_COLOR.custom, {pulse: true});
      });
    }
    wireMarkerEvents();
  }

  function wireMarkerEvents(){
    const wrap = document.getElementById("mapWrap");
    const tip = document.getElementById("mapTip");
    if(!wrap || !tip) return;
    function hideTip(){ tip.classList.remove("show"); }
    function positionTip(evt){
      const rect = wrap.getBoundingClientRect();
      let cx, cy;
      if(evt.touches && evt.touches[0]){ cx = evt.touches[0].clientX; cy = evt.touches[0].clientY; }
      else { cx = evt.clientX; cy = evt.clientY; }
      let x = cx - rect.left, y = cy - rect.top;
      const tw = 260, th = 130;
      if(x + tw + 24 > rect.width) x = x - tw - 18; else x = x + 16;
      if(y + th + 20 > rect.height) y = Math.max(4, y - th - 10); else y = y + 14;
      tip.style.left = x+"px"; tip.style.top = y+"px";
    }
    function showTip(m, evt){
      const name = m.dataset.name, note = m.dataset.note, source = m.dataset.source,
            date = m.dataset.date, color = m.dataset.color;
      let linked = [];
      try { linked = JSON.parse(m.dataset.linked || "[]"); } catch(e){ linked = []; }
      let html = '<div class="t-name" style="color:'+color+'">'+escapeHtml(name)+'</div>' +
                 '<div>'+escapeHtml(note)+'</div>' +
                 '<div class="t-meta">'+escapeHtml(source)+(date?(" &middot; "+escapeHtml(date)):"")+'</div>';
      if(linked.length){
        html += '<div class="t-meta" style="margin-top:6px;color:var(--text-dim);">Recent related items:</div>';
        linked.slice(0,3).forEach(function(li){
          html += '<div class="marker-tt-link">&bull; ' + escapeHtml((li.label||"").slice(0,60)) + '</div>';
        });
      }
      tip.innerHTML = html;
      positionTip(evt);
      tip.classList.add("show");
    }
    wrap.querySelectorAll(".marker").forEach(function(m){
      m.addEventListener("mouseenter", function(evt){ showTip(m, evt); });
      m.addEventListener("mousemove", positionTip);
      m.addEventListener("mouseleave", hideTip);
      m.addEventListener("click", function(evt){
        if(tip.classList.contains("show")){ hideTip(); } else { showTip(m, evt); }
      });
    });
    wrap.removeEventListener("mouseleave", hideTip);
    wrap.addEventListener("mouseleave", hideTip);
  }

  // layer toggle checkboxes
  document.querySelectorAll(".layer-cb").forEach(function(cb){
    cb.addEventListener("change", function(){
      const cat = cb.dataset.layer;
      if(cb.checked) activeLayers.add(cat); else activeLayers.delete(cat);
      if(currentData) renderMarkers(currentData.markers || []);
    });
  });

  // ---------------- panels ----------------
  // Only http(s) URLs ever become links. A feed-supplied "javascript:" / "data:" URL
  // would otherwise be a click-to-run XSS even though every text field is escaped.
  function safeUrl(u){
    if(!u) return null;
    try { const x = new URL(String(u)); return (x.protocol === "http:" || x.protocol === "https:") ? x.href : null; }
    catch(e){ return null; }
  }
  function fmtDate(s){
    const d = parseItemDate(s);
    return d ? d.toLocaleString([], {dateStyle:"medium", timeStyle:"short"}) : (s || "");
  }
  function itemHtml(it){
    const href = safeUrl(it.url);
    return '<div class="item" data-search="'+escapeHtml(((it.label||"")+" "+(it.text||"")).toLowerCase())+'">' +
      '<div class="lbl">'+escapeHtml(it.label)+'</div>' +
      (it.text && it.text !== it.label ? '<div class="txt">'+escapeHtml(it.text)+'</div>' : '') +
      '<div class="meta">'+escapeHtml(it.source)+(it.date?(" &middot; "+escapeHtml(fmtDate(it.date))):"")+
      (href ? ' &middot; <a href="'+escapeHtml(href)+'" target="_blank" rel="noopener noreferrer">source &#8599;</a>' : '')+
      '</div></div>';
  }

  function renderPanels(cats){
    const ids = HEADING_KEYS;
    ids.forEach(function(cat){
      const container = document.getElementById("items-"+cat);
      const countEl = document.getElementById("count-"+cat);
      if(!container) return;
      const list = (cats[cat] || []).slice(0, 25);
      if(countEl) countEl.textContent = list.length;
      container.innerHTML = list.length
        ? list.map(itemHtml).join("")
        : '<div class="empty-note">' + (timeWindow === "72h"
            ? (isLive
                ? 'Nothing in the last 72 hours for this heading. Switch to <b>All Time</b> (top right) to see older items.'
                : 'Backend offline - the embedded research snapshot is older than 72 hours, so it is hidden in this view. Switch to <b>All Time</b> to read it, or start the backend for live news.')
            : 'No items for this heading yet.') + '</div>';
    });
  }

  // ---------------- connector status strip ----------------
  function renderConnectorStrip(statuses, live){
    const el = document.getElementById("connectorStrip");
    const note = document.getElementById("methodNote");
    if(!live){
      el.innerHTML = '<span class="conn-badge off">offline snapshot - connectors not queried</span>';
      note.textContent = "Backend not connected. Start it with: python run.py  (see README.md)";
      return;
    }
    el.innerHTML = statuses.map(function(s){
      const cls = !s.configured ? "off" : (s.ok ? "ok" : "err");
      const label = s.name + (s.configured ? (s.ok ? " \u2713 " + s.item_count : " \u2717") : " (not set)");
      return '<span class="conn-badge '+cls+'" title="'+escapeHtml(s.message||"")+'">'+escapeHtml(label)+'</span>';
    }).join("");
    const okCount = statuses.filter(s=>s.ok).length;
    note.textContent = okCount + " of " + statuses.length + " connectors returned data this poll. " +
      "Hover a badge for its exact status message. Add API keys in .env or via secure_setup.py to enable more.";
  }

  // ---------------- search filter ----------------
  let lastQuery = "";
  function applyFilter(){
    const q = lastQuery;
    document.querySelectorAll(".item[data-search]").forEach(function(it){
      if(!q){ it.classList.remove("dim"); return; }
      const hay = it.getAttribute("data-search") || "";
      if(hay.indexOf(q) === -1) it.classList.add("dim"); else it.classList.remove("dim");
    });
  }
  const filterInput = document.getElementById("filterInput");
  if(filterInput){
    filterInput.addEventListener("input", function(){
      lastQuery = filterInput.value.trim().toLowerCase();
      applyFilter();
    });
  }

  // ---------------- refresh button ----------------
  const refreshBtn = document.getElementById("refreshBtn");
  if(refreshBtn) refreshBtn.addEventListener("click", function(){ loadData(true); });

  // ---------------- settings modal (API keys) ----------------
  const settingsBackdrop = document.getElementById("settingsBackdrop");
  const settingsBtn = document.getElementById("settingsBtn");
  const closeSettingsBtn = document.getElementById("closeSettingsBtn");
  const saveKeysBtn = document.getElementById("saveKeysBtn");
  const keyFieldsEl = document.getElementById("keyFields");
  const settingsMsg = document.getElementById("settingsMsg");

  async function openSettings(){
    settingsBackdrop.classList.add("show");
    settingsMsg.textContent = ""; settingsMsg.className = "modal-msg";
    keyFieldsEl.innerHTML = "Loading&hellip;";
    try {
      const res = await fetch("/api/keys");
      if(!res.ok) throw new Error("HTTP " + res.status);
      const fields = await res.json();
      keyFieldsEl.innerHTML = Object.keys(fields).map(function(name){
        const f = fields[name];
        return '<div class="key-field">' +
          '<label><span class="kf-status'+(f.configured?" on":"")+'"></span>' + escapeHtml(f.label) +
          (f.configured ? ' <span style="font-weight:400;color:var(--text-faint);">(set via '+escapeHtml(f.source)+')</span>' : '') +
          '</label>' +
          '<div class="kf-help">'+escapeHtml(f.help)+'</div>' +
          '<input type="password" data-key="'+name+'" placeholder="'+
            (f.configured ? "Already set - paste a new value to replace it" : "Paste key here, or leave blank to skip") +
          '" autocomplete="off"/></div>';
      }).join("");
    } catch(e) {
      keyFieldsEl.innerHTML = '<div class="modal-msg err">Could not load key status: ' + escapeHtml(e.message) +
        (isLive ? "" : " (backend not connected - start it with python run.py first)") + '</div>';
    }
  }
  function closeSettings(){ settingsBackdrop.classList.remove("show"); }

  if(settingsBtn) settingsBtn.addEventListener("click", openSettings);
  if(closeSettingsBtn) closeSettingsBtn.addEventListener("click", closeSettings);
  if(settingsBackdrop) settingsBackdrop.addEventListener("click", function(e){
    if(e.target === settingsBackdrop) closeSettings();
  });

  if(saveKeysBtn) saveKeysBtn.addEventListener("click", async function(){
    const inputs = keyFieldsEl.querySelectorAll("input[data-key]");
    const body = {};
    inputs.forEach(function(inp){ if(inp.value.trim()) body[inp.dataset.key] = inp.value.trim(); });
    if(!Object.keys(body).length){
      settingsMsg.textContent = "Nothing to save - all fields blank."; settingsMsg.className = "modal-msg";
      return;
    }
    saveKeysBtn.disabled = true; saveKeysBtn.textContent = "Saving\u2026";
    try {
      const res = await fetch("/api/keys", {method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify(body)});
      const j = await res.json();
      if(!res.ok) throw new Error(j.error || ("HTTP " + res.status));
      settingsMsg.textContent = "Saved " + j.saved.length + " key(s), encrypted. Reconnecting\u2026";
      settingsMsg.className = "modal-msg ok";
      await loadData(true);
      setTimeout(function(){ openSettings(); }, 400); // refresh the configured/not-configured status shown
    } catch(e) {
      settingsMsg.textContent = "Save failed: " + e.message;
      settingsMsg.className = "modal-msg err";
    } finally {
      saveKeysBtn.disabled = false; saveKeysBtn.textContent = "Save & reconnect";
    }
  });

  // ---------------- live clock ----------------
  function pad(n){ return n<10 ? "0"+n : n; }
  function tickClock(){
    const d = new Date();
    const el = document.getElementById("snapClock");
    if(el) el.textContent = pad(d.getHours())+":"+pad(d.getMinutes())+":"+pad(d.getSeconds())+" local";
  }
  tickClock(); setInterval(tickClock, 1000);

  // ---------------- running news ticker (unlocated news, newest first, bottom->top) ----------------
  function ts(it){ const d = parseItemDate(it.date); return d ? d.getTime() : 0; }
  function wireTickerPause(){
    const viewport = document.getElementById("tickerViewport");
    const track = document.getElementById("tickerTrack");
    if(!viewport || !track) return;
    viewport.onpointerenter = function(){ track.classList.add("paused"); };
    viewport.onpointerleave = function(){ track.classList.remove("paused"); };
    viewport.ontouchstart = function(){ track.classList.add("paused"); };
    viewport.ontouchend = function(){ track.classList.remove("paused"); };
  }
  function in72h(it){
    const d = parseItemDate(it.date);
    if(!d) return false;                       // undated background items never qualify as "latest news"
    return (Date.now() - d.getTime()) <= 72 * 3600 * 1000;
  }
  function renderTicker(view){
    // The running feed is ALWAYS the last 72 hours - it ignores the All-Time toggle.
    const track = document.getElementById("tickerTrack");
    const cnt = document.getElementById("count-ticker");
    if(!track) return;
    const src = (currentData && currentData.items_by_category) || {};
    const all = [];
    Object.keys(src).forEach(function(k){
      (src[k] || []).forEach(function(it){
        if(!(typeof it.lat === "number" && typeof it.lon === "number") && in72h(it)) all.push(it);
      });
    });
    all.sort(function(a, b){ return ts(b) - ts(a); });
    const list = all.slice(0, 80);
    if(cnt) cnt.textContent = list.length + " in 72h";
    if(!list.length){
      track.innerHTML = '<div class="empty-note" style="padding:14px;">No unlocated news in the last 72 hours yet.</div>';
      return;
    }
    const TAG = {geo:["GEO","var(--green)"], milops:["MIL","var(--amber)"], arms:["ARMS","var(--magenta)"],
      naval:["NAVAL","var(--cyan-h)"], scs:["SCS","var(--cyan-h)"], air:["AIR","var(--violet)"], space:["SPACE","var(--cyan-h)"],
      tech:["TECH","var(--gold)"], cyber:["CYBER","var(--red)"], darkweb:["DARK","var(--red)"], econ:["ECON","var(--cyan-h)"],
      mss:["MSS","var(--amber)"], social:["SOC","var(--gold)"], wellbeing:["WELL","var(--magenta)"], hazard:["HAZ","var(--violet)"]};
    const one = list.map(function(it){
      const t = TAG[it.category] || ["NEWS","var(--cyan-h)"];
      return '<div class="tick-item"><span class="tag" style="background:'+t[1]+'">'+t[0]+'</span>' +
        '<span class="txt">'+escapeHtml(it.label)+'</span>' +
        '<div class="meta">'+escapeHtml(it.source)+(it.date ? ' &middot; '+escapeHtml(fmtDate(it.date)) : '')+'</div></div>';
    }).join("");
    track.innerHTML = one + one;
    wireTickerPause();
  }

  function renderDarkWeb(view){
    const el = document.getElementById("items-darkweb");
    if(!el) return;
    const want = document.getElementById("darkwebFilter").value;
    const all = [];
    Object.keys(view.items_by_category || {}).forEach(function(k){
      (view.items_by_category[k] || []).forEach(function(it){
        if(it.category === "darkweb") all.push(it);
      });
    });
    all.sort(function(a, b){ return ts(b) - ts(a); });
    const shown = all.filter(function(it){ return want === "all" || it.in_region; }).slice(0, 80);
    document.getElementById("count-darkweb").textContent = shown.length + " of " + all.length;
    const LABEL = {ransomware_live:"Ransomware.live: ", telegram_public:"Telegram: ", darkweb_tor:"Dark web via Tor: "};
    const st = (view.connector_status || []).filter(function(s){ return LABEL[s.name]; })
      .map(function(s){ return LABEL[s.name] + s.message; });
    document.getElementById("darkwebStatus").textContent = st.join("   |   ");
    el.innerHTML = shown.length ? shown.map(function(it){
      const href = safeUrl(it.url);
      return '<div class="item"><div class="lbl">'+escapeHtml(it.label)+'</div><div class="meta">' +
        escapeHtml(it.source) + (it.country ? ' &middot; '+escapeHtml(it.country) : '') +
        (it.date ? ' &middot; '+escapeHtml(fmtDate(it.date)) : '') +
        (href ? ' &middot; <a href="'+escapeHtml(href)+'" target="_blank" rel="noopener noreferrer">source &#8599;</a>' : '') +
        '</div></div>';
    }).join("") : '<div class="empty-note">No dark-web or threat-intel claims in the current window. ' +
        (timeWindow === "72h" ? 'Switch to All Time (top right) to see older claims.' : '') + '</div>';
  }

  // ---------------- radar sweep: 2D scanner rotating over the map (off for reduced-motion) ----------------
  // Cosmetic only, so it is isolated: a missing animation API or any error here
  // must never stop the data panels from rendering. Falls back to a timer when
  // requestAnimationFrame is unavailable (older or embedded browsers).
  try {
    (function radar(){
      const g = document.getElementById("radarSweep");
      if(!g || (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches)) return;
      const cx = g.getAttribute("data-cx"), cy = g.getAttribute("data-cy");
      const raf = (typeof window.requestAnimationFrame === "function")
        ? function(f){ window.requestAnimationFrame(f); }
        : function(f){ setTimeout(f, 33); };
      let a = 0;
      (function step(){
        a = (a + 0.5) % 360;
        g.setAttribute("transform", "rotate(" + a + " " + cx + " " + cy + ")");
        raf(step);
      })();
    })();
  } catch(e) { /* sweep is decoration; the dashboard works without it */ }

  const dwFilter = document.getElementById("darkwebFilter");
  if(dwFilter) dwFilter.addEventListener("change", function(){ if(currentData) render(currentData, isLive, null); });

  // ---------------- 72h / All-time toggle ----------------
  document.querySelectorAll(".wt-btn").forEach(function(btn){
    btn.addEventListener("click", function(){
      timeWindow = btn.dataset.window;
      document.querySelectorAll(".wt-btn").forEach(b => b.classList.toggle("active", b === btn));
      // re-render from what we already have - no new network call needed
      if(currentData) render(currentData, isLive, null);
    });
  });

  // ---------------- Plot a location (lat/long + remark) ----------------
  const plotBackdrop = document.getElementById("plotBackdrop");
  const plotMsg = document.getElementById("plotMsg");

  async function loadCustomMarkers(){
    try {
      const res = await fetch("/api/custom-markers", {cache:"no-store"});
      if(!res.ok) throw new Error("HTTP " + res.status);
      customMarkers = (await res.json()).markers || [];
    } catch(e) { customMarkers = []; }
  }

  function renderCustomList(){
    const el = document.getElementById("customMarkersList");
    if(!customMarkers.length){ el.innerHTML = ""; return; }
    el.innerHTML = '<div style="font-size:11px;color:var(--text-faint);margin-bottom:6px;">Your plotted markers:</div>' +
      customMarkers.map(function(m, i){
        return '<div class="custom-marker-row"><span><b>'+escapeHtml(m.label)+'</b> ('+m.lat+', '+m.lon+')' +
          (m.remark ? '<br/><span style="color:var(--text-faint);">'+escapeHtml(m.remark)+'</span>' : '') +
          '</span><button data-idx="'+i+'" title="Remove">&times;</button></div>';
      }).join("");
    el.querySelectorAll("button[data-idx]").forEach(function(btn){
      btn.addEventListener("click", async function(){
        try {
          const res = await fetch("/api/custom-markers/" + btn.dataset.idx, {method:"DELETE"});
          const j = await res.json();
          if(!res.ok) throw new Error(j.error || ("HTTP " + res.status));
          customMarkers = j.markers || [];
          renderCustomList();
          if(currentData) render(currentData, isLive, null);
        } catch(e) {
          plotMsg.textContent = "Remove failed: " + e.message; plotMsg.className = "modal-msg err";
        }
      });
    });
  }

  const plotBtn = document.getElementById("plotBtn");
  if(plotBtn) plotBtn.addEventListener("click", async function(){
    plotBackdrop.classList.add("show");
    plotMsg.textContent = ""; plotMsg.className = "modal-msg";
    await loadCustomMarkers();
    renderCustomList();
  });
  document.getElementById("plotCloseBtn").addEventListener("click", () => plotBackdrop.classList.remove("show"));
  plotBackdrop.addEventListener("click", function(e){ if(e.target === plotBackdrop) plotBackdrop.classList.remove("show"); });

  document.getElementById("plotAddBtn").addEventListener("click", async function(){
    const label = document.getElementById("plotLabel").value.trim();
    const remark = document.getElementById("plotRemark").value.trim();
    const lat = parseFloat(document.getElementById("plotLat").value);
    const lon = parseFloat(document.getElementById("plotLon").value);
    if(!label || isNaN(lat) || isNaN(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180){
      plotMsg.textContent = "Enter a label and valid lat (-90 to 90) / lon (-180 to 180)."; plotMsg.className = "modal-msg err";
      return;
    }
    try {
      const res = await fetch("/api/custom-markers", {method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({label: label, remark: remark, lat: lat, lon: lon})});
      const j = await res.json();
      if(!res.ok) throw new Error(j.error || ("HTTP " + res.status));
      customMarkers = j.markers || [];
      ["plotLabel","plotRemark","plotLat","plotLon"].forEach(id => document.getElementById(id).value = "");
      plotMsg.textContent = "Added."; plotMsg.className = "modal-msg ok";
      renderCustomList();
      if(currentData) render(currentData, isLive, null);
    } catch(e) {
      plotMsg.textContent = "Add failed: " + e.message; plotMsg.className = "modal-msg err";
    }
  });

  // ---------------- boot ----------------
  loadCustomMarkers().then(function(){ loadData(false); });
  // auto-update news & data every 3 minutes, per request
  refreshTimer = setInterval(function(){ loadData(false); }, 3*60*1000);

  // Test hooks (harmless in production) so the DOM regression test can drive
  // the real code paths instead of re-implementing them
  window.__TEST = {render: function(){ if(currentData) render(currentData, isLive, null); },
                   setData: function(d){ currentData = d; isLive = true; },
                   setWindow: function(w){ timeWindow = w; },
                   parseItemDate: parseItemDate, inWindow: inWindow};
})();
"""

SCRIPT = (SCRIPT.replace("__PROJ__", json.dumps(proj))
                .replace("__HKEYS__", json.dumps([k for k, _, _ in HEADINGS if k != "darkweb"]))
                .replace("__SEED__", SEED_JSON_STR)
                .replace("__CATMETA__", CAT_META_JSON))

print("SCRIPT length:", len(SCRIPT))

PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>AUSTRALIA Dashboard &mdash; OSINT Snapshot</title>
<style>{css}</style>
</head>
<body>
<div class="wrap">
  {header}
  {kpi}
  <div class="main-grid">
    {left}
    {ticker}
  </div>
  {footer}
</div>
<script src="/static/dashboard.js"></script>
</body>
</html>'''.format(css=CSS, header=HEADER, kpi=KPI_ROW, left=LEFT_COL, ticker=TICKER_HTML, footer=FOOTER)

out_path = f"{BASE}/static/dashboard.html"
open(out_path, "w", encoding="utf-8").write(PAGE)
print("WROTE", out_path, "bytes:", len(PAGE.encode("utf-8")))

# A same-origin external file (not an inline <script> block) is what lets the
# server's CSP use a strict `script-src 'self'` with no 'unsafe-inline' - an
# inline block can only be allowed via 'unsafe-inline' (defeats most of the
# point) or a per-response nonce (real complexity for no gain when a plain
# same-origin file does the same job).
js_path = f"{BASE}/static/dashboard.js"
open(js_path, "w", encoding="utf-8").write(SCRIPT)
print("WROTE", js_path, "bytes:", len(SCRIPT.encode("utf-8")))
