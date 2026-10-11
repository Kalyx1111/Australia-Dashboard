// Checks what the user actually sees on the REAL built page: the scrolling
// news ticker only shows UNLOCATED news, the Dark Web panel fills from
// threat-intel records (and only those), the radar sweep exists, and every
// layer toggle is present. Runs the shipped dashboard.js, not a re-implementation.
const fs = require('fs');
const { JSDOM } = require('jsdom');
const html = fs.readFileSync(__dirname + '/../static/dashboard.html', 'utf8');
const js = fs.readFileSync(__dirname + '/../static/dashboard.js', 'utf8');
const fail = m => { console.error("FAIL:", m); process.exit(1); };
const tick = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const dom = new JSDOM(html.replace('<script src="/static/dashboard.js"></script>', '<script>' + js + '</script>'),
                        { runScripts: "dangerously", url: "http://127.0.0.1:8830/" });
  const w = dom.window, d = w.document;
  await tick(200);
  const now = Date.now(), iso = ms => new Date(ms).toISOString();
  const T = w.__TEST;
  T.setData({
    updated_at: now / 1000, total_items: 4, infrastructure: {}, connector_status: [
      { name: "ransomware_live", configured: true, ok: true, message: "2 recent claimed victims (1 Asia-Pacific)", item_count: 2 },
      { name: "telegram_public", configured: true, ok: false, message: "no channels configured - add ... data/telegram_channels.json", item_count: 0 }],
    items_by_category: {
      milops: [
        { category: "milops", label: "UNLOCATED-MIL headline", text: "x", source: "Reuters", date: iso(now - 3600e3), connector: "rss" },
        { category: "milops", label: "OLD-9DAY ticker item", text: "x", source: "Reuters", date: iso(now - 9*24*3600e3), connector: "rss" },
        { category: "milops", label: "PLOTTED-MIL headline", text: "x", source: "Reuters", date: iso(now - 3600e3), connector: "rss", lat: 30, lon: 110 }],
      cyber: [
        { category: "darkweb", label: "[akira] claimed victim: AU Co", text: "t", source: "Ransomware.live (leak-site aggregation)", date: iso(now - 7200e3),
          connector: "ransomware_live", country: "AU", in_region: true },
        { category: "darkweb", label: "[qilin] claimed victim: DE Co", text: "t", source: "Ransomware.live (leak-site aggregation)", date: iso(now - 9000e3),
          connector: "ransomware_live", country: "DE", in_region: false },
        { category: "cyber", label: "Volt Typhoon reference", text: "t", source: "CISA", date: "ongoing", connector: "reference" }],
    },
    markers: [{ id: "x", name: "Yulin Naval Base", lat: 18.23, lon: 109.5, cat: "navy_base", note: "n", source: "s", date: "", linked_items: [] }],
  });
  T.setWindow("72h"); T.render();

  const ticker = d.getElementById("tickerTrack").textContent;
  if (!ticker.includes("UNLOCATED-MIL headline")) fail("ticker is missing unlocated news - the right-hand running feed is empty");
  if (ticker.includes("PLOTTED-MIL headline")) fail("ticker shows a LOCATED item - located news belongs on the map, not the ticker");
  if (ticker.includes("Volt Typhoon reference")) fail("ticker shows an undated reference item in the strict 72h view");

  // All Time must NOT widen the running ticker: an item from 9 days ago stays out
  T.setWindow("all"); T.render();
  if (d.getElementById("tickerTrack").textContent.includes("OLD-9DAY ticker item")) fail("All Time widened the running ticker past 72 hours");
  T.setWindow("72h"); T.render();

  const dw = d.getElementById("items-darkweb").textContent;
  if (!dw.includes("AU Co") || !dw.includes("DE Co")) fail("dark web panel missing the threat-intel claims");
  if (dw.includes("Volt Typhoon reference")) fail("dark web panel shows a non-threat-intel item");
  if (!d.getElementById("darkwebStatus").textContent.includes("Telegram: no channels configured")) fail("dark web panel does not state that no Telegram channels are configured");

  d.getElementById("darkwebFilter").value = "region"; d.getElementById("darkwebFilter").dispatchEvent(new w.Event("change"));
  const apac = d.getElementById("items-darkweb").textContent;
  if (!apac.includes("AU Co") || apac.includes("DE Co")) fail("regional filter did not isolate the regional victims");

  if (!d.getElementById("radarSweep")) fail("radar sweep element missing from the map");
  const toggles = d.querySelectorAll(".layer-cb").length;
  if (toggles < 9) fail(`expected at least 9 layer toggles, found ${toggles}`);
  const marker = d.querySelectorAll("#markerLayer .marker").length;
  if (marker < 1) fail("no markers rendered on the map");

  console.log(`PASS: ticker shows only unlocated, in-window news; dark web panel shows only threat-intel claims, filter works, Telegram status stated; radar present; ${toggles} layer toggles; ${marker} markers`);
  process.exit(0);
})().catch(e => { console.error("FAIL:", e); process.exit(1); });
