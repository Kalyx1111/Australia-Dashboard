/* Screen layout for the regional dashboards (the same file in all 17 builds).
   Full map hides the KPI strip, the map's header row, the news drawer and its tab,
   the layers panel and the footer note, so the map fills the window below the title.
   Hide bars fades the header controls, the KPI strip, the map's header row, the news
   tab, the map tools, the zoom control and the footer note after the chosen idle time
   (3, 4 or 5 seconds, or never) with no mouse, touch, wheel or key use. The title always
   stays. Full screen hides the browser's tabs and address bar. Choices are kept in this
   browser only; nothing is sent anywhere. */
(() => {
  "use strict";
  const KEY = "dashboard.layout.v1";
  const S = { hideMs: 4000, fullMap: false, last: Date.now() };
  const $ = (id) => document.getElementById(id);
  const body = () => document.body;

  function load() {
    try {
      const v = JSON.parse(localStorage.getItem(KEY) || "{}");
      if ([0, 3, 4, 5].includes(v.hide)) S.hideMs = v.hide * 1000;
      S.fullMap = v.fullMap === true;
    } catch (e) {
      /* storage unavailable or corrupt: keep the defaults */
    }
  }
  function save() {
    try {
      localStorage.setItem(KEY, JSON.stringify({ hide: S.hideMs / 1000, fullMap: S.fullMap }));
    } catch (e) {
      /* storage unavailable: the choice lasts until the page is reloaded */
    }
  }
  const typing = () => {
    const a = document.activeElement;
    return !!(a && a.matches && a.matches("input, select, textarea"));
  };
  const modalOpen = () => !!document.querySelector(".modal-backdrop.show");

  // The top edge of the map in the document, so the map can fill the rest of the window.
  function setMapTop() {
    const wrap = $("mapWrap");
    if (!wrap) return;
    const top = Math.max(0, Math.round(wrap.getBoundingClientRect().top + window.scrollY));
    document.documentElement.style.setProperty("--map-top", top + "px");
  }
  function setIdle(on) {
    if (body().classList.contains("bars-idle") === on) return;
    body().classList.toggle("bars-idle", on);
    setMapTop();
  }
  function markActivity() {
    S.last = Date.now();
    setIdle(false);
  }
  function evaluate(now) {
    const t = typeof now === "number" ? now : Date.now();
    const idle = S.hideMs > 0 && !typing() && !modalOpen() && t - S.last >= S.hideMs;
    setIdle(idle);
    return idle;
  }

  function refresh() {
    const fm = $("btnFullMap");
    if (fm) {
      fm.setAttribute("aria-pressed", String(S.fullMap));
      fm.textContent = S.fullMap ? "Show panels" : "Full map";
    }
    const fs = $("btnFullScreen");
    if (fs) {
      const on = !!document.fullscreenElement;
      fs.setAttribute("aria-pressed", String(on));
      fs.textContent = on ? "Exit full screen" : "Full screen";
      fs.disabled = !document.fullscreenEnabled;
      fs.title = document.fullscreenEnabled
        ? "Hide the browser's tabs and address bar (F)"
        : "Full screen is not available in this browser";
    }
    const sel = $("selHideBars");
    if (sel) sel.value = String(S.hideMs / 1000);
  }
  function setFullMap(on) {
    S.fullMap = !!on;
    body().classList.toggle("full-map", S.fullMap);
    if (S.fullMap) window.scrollTo(0, 0);
    setMapTop();
    refresh();
    save();
    markActivity();
  }
  function toggleFullMap() {
    setFullMap(!S.fullMap);
  }
  function toggleFullScreen() {
    if (!document.fullscreenEnabled) return;
    if (document.fullscreenElement) document.exitFullscreen().catch(() => {});
    else document.documentElement.requestFullscreen().catch(() => {});
    markActivity();
  }
  function setHideSeconds(seconds) {
    const n = Number(seconds);
    S.hideMs = [0, 3, 4, 5].includes(n) ? n * 1000 : 4000;
    save();
    refresh();
    markActivity();
  }

  function bind() {
    const on = (id, type, fn) => {
      const n = $(id);
      if (n) n.addEventListener(type, fn);
    };
    on("btnFullMap", "click", toggleFullMap);
    on("btnFullScreen", "click", toggleFullScreen);
    on("selHideBars", "change", (e) => setHideSeconds(e.target.value));
    ["pointermove", "pointerdown", "wheel", "touchstart", "keydown", "focusin"].forEach((t) =>
      window.addEventListener(t, markActivity, { passive: true })
    );
    document.addEventListener("fullscreenchange", () => {
      refresh();
      markActivity();
    });
    window.addEventListener("resize", setMapTop);
    document.addEventListener("keydown", (e) => {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      if (e.target && e.target.matches && e.target.matches("input, textarea, select")) return;
      if (modalOpen()) return;
      if (e.key === "m" || e.key === "M") toggleFullMap();
      else if (e.key === "f" || e.key === "F") toggleFullScreen();
    });
  }
  function init() {
    load();
    bind();
    body().classList.toggle("full-map", S.fullMap);
    setMapTop();
    refresh();
    markActivity();
    setInterval(() => evaluate(), 500);
  }

  window.DashLayout = {
    setFullMap,
    toggleFullMap,
    toggleFullScreen,
    setHideSeconds,
    markActivity,
    evaluate,
    state: () => ({ fullMap: S.fullMap, hideMs: S.hideMs, idle: body().classList.contains("bars-idle") }),
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
