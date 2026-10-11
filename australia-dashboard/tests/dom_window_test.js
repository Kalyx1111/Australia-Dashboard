// Loads the REAL generated dashboard.html and exercises the 72h/All-time
// logic with the actual date formats each connector emits. This is the
// riskiest new logic (strict date filtering across 4 formats), so it's
// tested against the shipped page, not a re-implementation of it.
const fs = require('fs');
const { JSDOM } = require('jsdom');
// dashboard.js is now a real external file (needed for a strict CSP
// script-src 'self' with no 'unsafe-inline' - see server.py). jsdom can load
// external <script src> too, but only via its real resource-fetch path,
// which is unnecessary complexity here - inlining the exact same file
// content tests byte-identical code without that.
let html = fs.readFileSync(__dirname + '/../static/dashboard.html', 'utf8');
const scriptFile = fs.readFileSync(__dirname + '/../static/dashboard.js', 'utf8');
html = html.replace('<script src="/static/dashboard.js"></script>', '<script>' + scriptFile + '</script>');

async function main() {
  const dom = new JSDOM(html, { runScripts: "dangerously", url: "http://127.0.0.1:8830/" });
  const w = dom.window;
  let uncaught = null;
  w.addEventListener("error", e => { uncaught = e.error || e.message; });
  const now = Date.now();
  const iso = ms => new Date(ms).toISOString();
  const hrs = h => now - h * 3600 * 1000;
  const gdelt = ms => iso(ms).replace(/[-:]/g, "").replace(/\.\d+Z$/, "Z");   // 20260927T101500Z
  const rfc = ms => new Date(ms).toUTCString();                               // RSS-style
  const T = w.__TEST;
  const fail = m => { console.error("FAIL:", m); process.exit(1); };

  // --- parseItemDate handles all 4 real formats ---
  for (const [name, s] of [["ISO", iso(hrs(5))], ["GDELT", gdelt(hrs(5))], ["RFC822", rfc(hrs(5))], ["USGS-epoch", String(hrs(5))]]) {
    const d = T.parseItemDate(s);
    if (!d || Math.abs(d.getTime() - hrs(5)) > 2000) fail(`parseItemDate(${name}) gave ${d} for ${s}`);
  }
  if (T.parseItemDate("ongoing") !== null || T.parseItemDate("") !== null || T.parseItemDate(null) !== null)
    fail("unparseable/undated values must return null, not a bogus date");

  // --- strict 72h window ---
  T.setWindow("72h");
  const cases = [
    ["1h old ISO", iso(hrs(1)), true], ["71h old GDELT", gdelt(hrs(71)), true],
    ["73h old ISO", iso(hrs(73)), false], ["200h old RFC822", rfc(hrs(200)), false],
    ["undated 'ongoing'", "ongoing", false], ["empty date", "", false],
  ];
  for (const [n, d, expect] of cases) {
    if (T.inWindow({ date: d }) !== expect) fail(`72h window: "${n}" expected ${expect}`);
  }
  T.setWindow("all");
  if (!T.inWindow({ date: iso(hrs(9999)) }) || !T.inWindow({ date: "ongoing" })) fail("All Time must include everything");

  // --- end to end: real render, panel content, toggle button, map dots ---
  const data = {
    updated_at: now / 1000, total_items: 3, connector_status: [], infrastructure: {},
    items_by_category: {
      milops: [
        { category: "milops", label: "FRESH headline", text: "fresh", source: "T", date: iso(hrs(2)), url: null, connector: "rss" },
        { category: "milops", label: "STALE headline", text: "stale", source: "T", date: iso(hrs(100)), url: null, connector: "rss" }],
      hazard: [{ category: "hazard", label: "M5.1 quake FRESH", text: "q", source: "USGS", date: String(hrs(3)),
                 url: null, connector: "usgs", lat: 30.0, lon: 103.0 }],
    },
    markers: [{ id: "hz", name: "Chattogram test point", lat: -6.3, lon: 155.0, cat: "flashpoint", note: "n", source: "s", date: "",
                linked_items: [{ label: "fresh link", date: iso(hrs(1)) }, { label: "old link", date: iso(hrs(90)) }] }],
  };
  T.setData(data); T.setWindow("72h"); T.render();
  const txt = () => w.document.getElementById("items-milops").textContent;
  if (!txt().includes("FRESH headline")) fail("fresh item missing in 72h view");
  if (txt().includes("STALE headline")) fail("STALE item leaked into the 72h view - the one rule this feature exists for");
  const dots72 = w.document.querySelectorAll("#markerLayer .marker").length;
  if (dots72 < 2) fail(`expected static marker + USGS quake dot in 72h, got ${dots72}`);
  const linked72 = JSON.parse(w.document.querySelector("#markerLayer .marker").dataset.linked);
  if (linked72.length !== 1) fail(`tooltip should list only the 1 in-window linked headline, got ${linked72.length}`);

  // click the real toggle button
  w.document.querySelector('.wt-btn[data-window="all"]').click();
  if (!txt().includes("STALE headline")) fail("All Time button did not reveal older items");
  if (!w.document.querySelector('.wt-btn[data-window="all"]').classList.contains("active")) fail("toggle active state not updated");
  w.document.querySelector('.wt-btn[data-window="72h"]').click();
  if (txt().includes("STALE headline")) fail("clicking back to 72h did not re-hide older items");

  // default must be 72h on a fresh load
  const fresh = new JSDOM(html, { runScripts: "dangerously", url: "http://127.0.0.1:8830/" });
  if (!fresh.window.document.querySelector('.wt-btn[data-window="72h"]').classList.contains("active")) fail("72h is not the default active window");

  if (uncaught) fail("uncaught page error: " + uncaught);
  console.log("PASS: 4 date formats parse; strict 72h window; All-time toggle; default=72h; markers/tooltips respect the window");
  process.exit(0);
}
main().catch(e => { console.error("FAIL:", e); process.exit(1); });
