// Checks the controls the layout changes added: the news drawer opens and hides, Pause and Resume toggle the ticker,
// and the Layers overlay opens and closes. The map starts with the news collapsed so it fills the screen.
const fs = require('fs');
const { JSDOM } = require('jsdom');
let html = fs.readFileSync(__dirname + '/../static/dashboard.html', 'utf8');
const scriptFile = fs.readFileSync(__dirname + '/../static/dashboard.js', 'utf8');
html = html.replace('<script src="/static/dashboard.js"></script>', '<script>' + scriptFile + '</script>');
const fail = m => { console.error('FAIL:', m); process.exit(1); };
const wait = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const dom = new JSDOM(html, { runScripts: 'dangerously', url: 'http://127.0.0.1:8845/' });
  const w = dom.window, d = w.document;
  w.fetch = async () => ({ ok: true, status: 200, json: async () => ({ updated_at: 'test', total_items: 0, connector_status: [], items_by_category: {}, markers: [] }) });
  const click = el => el.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  await wait(150);
  const grid = d.getElementById('mainGrid');
  if (!grid || !grid.classList.contains('news-closed')) fail('the news must start collapsed so the map fills the screen');
  click(d.getElementById('newsTab')); await wait(10);
  if (!grid.classList.contains('news-open')) fail('the news tab did not open the latest-news panel');
  const pause = d.getElementById('tickerPause'), track = d.getElementById('tickerTrack');
  click(pause); await wait(10);
  if (!track.classList.contains('paused') || pause.textContent.trim() !== 'Resume') fail('Pause did not pause the running news');
  click(pause); await wait(10);
  if (track.classList.contains('paused') || pause.textContent.trim() !== 'Pause') fail('Resume did not resume the running news');
  click(d.getElementById('newsHide')); await wait(10);
  if (!grid.classList.contains('news-closed')) fail('Hide did not collapse the news panel');
  const mb = d.getElementById('mapBody');
  click(d.getElementById('layersBtn')); await wait(10);
  if (!mb.classList.contains('layers-open')) fail('the Layers button did not open the overlay');
  click(d.getElementById('layersClose')); await wait(10);
  if (mb.classList.contains('layers-open')) fail('Close did not hide the Layers overlay');
  console.log('drawer PASS: news opens and hides from the right edge; Pause and Resume toggle; Layers opens and closes');
  process.exit(0);
})().catch(e => fail(e && e.stack || e));
