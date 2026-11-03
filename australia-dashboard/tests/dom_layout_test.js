// Checks the screen layout controls on the REAL built page, running the shipped
// scripts: Full map hides the bars and the side elements but keeps the map and the
// title; Hide bars fades the header controls, KPI strip, map header, news tab, map
// tools, zoom control and footer note after the chosen idle time and brings them
// back on activity. Runs the shipped dashboard.js and layout.js.
const fs = require('fs');
const { JSDOM } = require('jsdom');
const dir = __dirname + '/../static/';
const html = fs.readFileSync(dir + 'dashboard.html', 'utf8');
const js = fs.readFileSync(dir + 'dashboard.js', 'utf8');
const layout = fs.readFileSync(dir + 'layout.js', 'utf8');
const fail = (m) => { console.error('FAIL:', m); process.exit(1); };
const check = (cond, m) => { if (!cond) fail(m); };
let n = 0;
const ok = (cond, m) => { check(cond, m); n += 1; };

const page = html
  .replace('<script src="/static/dashboard.js"></script>', () => '<script>' + js + '</script>')
  .replace('<script src="/static/layout.js" defer></script>', () => '<script>' + layout + '</script>');
ok(page.includes('window.DashLayout = {'), 'layout script is inlined on the page');

const dom = new JSDOM(page, {
  runScripts: 'dangerously',
  url: 'http://127.0.0.1:8830/',
  beforeParse(w) { w.scrollTo = () => {}; },
});
const w = dom.window, d = w.document;
const tick = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  await tick(150);
  const L = w.DashLayout;
  ok(!!L && typeof L.evaluate === 'function', 'layout controller is available on the page');
  ok(!!d.getElementById('btnFullMap') && !!d.getElementById('btnFullScreen') && !!d.getElementById('selHideBars'),
     'the three controls are on the page');
  ok(d.getElementById('selHideBars').value === '4', 'hide bars defaults to 4 seconds');
  const title = d.querySelector('.brand-title');
  ok(!!title && !title.closest('.search-wrap, .hdr-right, #kpiRow, .map-tools, .news-tab'),
     'the title is not inside anything that hides');

  // Full map: adds the class, the button says how to go back, and M toggles it.
  d.getElementById('btnFullMap').click();
  ok(d.body.classList.contains('full-map'), 'Full map adds the full-map class');
  ok(d.getElementById('btnFullMap').textContent === 'Show panels'
     && d.getElementById('btnFullMap').getAttribute('aria-pressed') === 'true', 'Full map button shows the way back');
  d.getElementById('btnFullMap').click();
  ok(!d.body.classList.contains('full-map') && d.getElementById('btnFullMap').textContent === 'Full map',
     'a second press restores the panels');
  d.dispatchEvent(new w.KeyboardEvent('keydown', { key: 'm', bubbles: true }));
  ok(d.body.classList.contains('full-map'), 'the M key turns Full map on');
  d.dispatchEvent(new w.KeyboardEvent('keydown', { key: 'M', bubbles: true }));
  ok(!d.body.classList.contains('full-map'), 'the M key turns it off again');

  // Full screen is offered only where the browser supports it (jsdom has no Fullscreen API).
  ok(d.getElementById('btnFullScreen').disabled === true, 'Full screen is disabled where the browser lacks the API');
  d.dispatchEvent(new w.KeyboardEvent('keydown', { key: 'f', bubbles: true }));

  // Hide bars: after the chosen idle time, back on activity, and never when set to never.
  const sel = d.getElementById('selHideBars');
  sel.value = '3'; sel.dispatchEvent(new w.Event('change'));
  ok(L.state().hideMs === 3000, '3 seconds is stored');
  L.markActivity();
  const t0 = Date.now();
  ok(L.evaluate(t0 + 2000) === false, 'bars stay before the chosen time');
  ok(L.evaluate(t0 + 3500) === true && d.body.classList.contains('bars-idle'), 'bars hide after 3 seconds without activity');
  L.markActivity();
  ok(!d.body.classList.contains('bars-idle'), 'activity brings the bars back');
  sel.value = '0'; sel.dispatchEvent(new w.Event('change'));
  L.markActivity();
  ok(L.evaluate(Date.now() + 600000) === false, 'Never keeps the bars');
  sel.value = '4'; sel.dispatchEvent(new w.Event('change'));
  ok(L.state().hideMs === 4000, '4 seconds restored');

  // An open dialog, or typing in the filter, keeps the bars visible.
  L.markActivity();
  const modal = d.getElementById('settingsBackdrop');
  modal.classList.add('show');
  ok(L.evaluate(Date.now() + 600000) === false, 'an open dialog keeps the bars');
  modal.classList.remove('show');
  const filter = d.getElementById('filterInput');
  filter.focus();
  ok(L.evaluate(Date.now() + 600000) === false, 'typing in the filter keeps the bars');
  filter.blur();

  // The shipped page carries the rules that hide each element in the two modes.
  for (const rule of ['body.full-map #kpiRow', 'body.full-map .map-panel>.panel-hd', 'body.bars-idle .hdr .search-wrap',
                      'body.bars-idle .map-tools', 'body.bars-idle .dash-footer']) {
    ok(html.includes(rule), 'the page has the rule ' + rule);
  }
  console.log('PASS dom layout: ' + n + ' checks (Full map, Full screen, Hide bars, title, dialogs, typing)');
  w.close();
  process.exit(0);
})().catch((e) => fail(e && e.stack ? e.stack : String(e)));
