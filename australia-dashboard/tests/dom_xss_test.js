// XSS check against the REAL generated page. Hostile text is delivered through
// every external-text path via the page's own code (real fetch route for the
// plotted markers, real render()), then we assert it is inert TEXT everywhere.
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
const fail = m => { console.error("FAIL:", m); process.exit(1); };
const tick = ms => new Promise(r => setTimeout(r, ms));

async function main() {
  const dom = new JSDOM(html, { runScripts: "dangerously", url: "http://127.0.0.1:8830/" });
  const w = dom.window, d = w.document;
  await tick(300);                       // let the page's async boot (offline-seed render) finish FIRST
  w.__pwned = false;
  const evil = '<img src=x onerror="window.__pwned=true">';
  const evil2 = '"><script>window.__pwned=true</script>';
  const now = Date.now();

  // the plotted-marker path: served through the page's real loadCustomMarkers() fetch
  w.fetch = async (url) => {
    if (String(url).includes("/api/custom-markers"))
      return { ok: true, status: 200, json: async () => ({ markers: [{ label: evil, remark: evil2, lat: -6.3, lon: 155.0, added: "now" }] }) };
    throw new Error("no backend");
  };
  const T = w.__TEST;
  T.setData({
    updated_at: now / 1000, total_items: 1, infrastructure: {},
    connector_status: [{ name: evil, configured: true, ok: false, message: evil2, item_count: 0 }],
    items_by_category: { milops: [
      { category: "milops", label: evil, text: evil2, source: evil, date: new Date(now).toISOString(), url: 'javascript:window.__pwned=true', connector: "rss" },
      { category: "milops", label: "GOOD headline", text: "ok", source: "Reuters", date: new Date(now).toISOString(), url: 'https://example.com/a?b=1&c=2', connector: "rss" },
      { category: "milops", label: "DATA url", text: "d", source: "x", date: new Date(now).toISOString(), url: 'data:text/html,<script>window.__pwned=true</script>', connector: "rss" }] },
    markers: [{ id: "x", name: evil, lat: -6.3, lon: 155.0, cat: "flashpoint", note: evil2, source: evil, date: "",
                linked_items: [{ label: evil, date: new Date(now).toISOString() }] }],
  });
  T.setWindow("72h");
  d.getElementById("plotBtn").click();   // real handler -> real fetch route -> real customMarkers + renderCustomList()
  await tick(120);
  T.render();                            // synchronous from here on: nothing async can overwrite the hostile data
  const markers = d.querySelectorAll("#markerLayer .marker");
  markers.forEach(g => g.dispatchEvent(new w.MouseEvent("mouseenter", { bubbles: true, clientX: 60, clientY: 60 })));

  // 0. prove the paths were actually exercised (no silent skipping)
  if (markers.length < 2) fail(`expected the static marker AND the plotted marker, got ${markers.length}`);
  if (!d.getElementById("customMarkersList").textContent.includes("<img src=x")) fail("plotted-marker list never received the hostile label - path not exercised");
  if (!d.getElementById("items-milops").textContent.includes("<img src=x")) fail("hostile headline never reached the panel - path not exercised");

  // 1. nothing executed, nothing live
  if (w.__pwned) fail("script executed: hostile input ran as code");
  if (d.querySelectorAll("img[src='x']").length) fail("an injected <img> became a live element");
  if ([...d.querySelectorAll("*")].some(el => el.hasAttribute("onerror"))) fail("an element carries an injected onerror handler");
  if ([...d.querySelectorAll("script")].some(s => s.textContent.includes("__pwned=true") && !s.textContent.includes("SEED_DATA"))) fail("injected <script> element exists");
  // 2. the tooltip (built via innerHTML) is inert too
  const tip = d.getElementById("mapTip");
  if (!tip.textContent.includes("<img src=x")) fail("tooltip did not receive the hostile text (path not exercised)");
  if (tip.querySelector("img,script")) fail("tooltip contains a live injected element");
  // 3. links: a javascript: URL must not become a clickable href
  const badLinks = [...d.querySelectorAll("a[href]")].filter(a => !/^https?:/i.test(a.getAttribute("href")));
  if (badLinks.length) fail("a non-http(s) URL became a live link: " + badLinks[0].getAttribute("href"));
  // positive control: the check above is only meaningful if legitimate links DO render
  const good = [...d.querySelectorAll("#items-milops a[href]")].filter(a => a.getAttribute("href").startsWith("https://example.com/a"));
  if (good.length !== 1) fail("positive control failed: the legitimate https link did not render (link test would be vacuous)");
  if (!/noopener/.test(good[0].rel) || !/noreferrer/.test(good[0].rel) || good[0].target !== "_blank") fail("external link missing rel=noopener noreferrer / target=_blank");
  console.log("PASS: hostile headline/source/status/marker/plotted-label paths all inert; tooltip inert; javascript: URLs not linkable");
  process.exit(0);
}
main().catch(e => { console.error("FAIL:", e); process.exit(1); });
