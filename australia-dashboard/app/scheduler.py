"""Background poller - runs in its own thread, calls every registered
connector, merges results, writes to cache. A dead connector never stops
the others."""
from __future__ import annotations
import logging
import threading
import time

from . import cache
from .connectors import gdelt, rss, usgs, grok, ransomware_live, telegram_public, instagram_graph, darkweb_tor, x_api, facebook_graph

log = logging.getLogger("scheduler")
REGISTRY = [gdelt, rss, usgs, grok, ransomware_live, telegram_public, instagram_graph, darkweb_tor, x_api, facebook_graph]


def poll_once() -> dict:
    all_items = []
    statuses = []
    for mod in REGISTRY:
        name = mod.NAME
        try:
            result = mod.fetch()
            statuses.append(result.to_status_dict())
            if result.ok:
                all_items.extend(result.items)
        except Exception as e:
            log.exception("connector %s crashed", name)
            statuses.append({"name": name, "configured": True, "ok": False,
                              "message": f"unexpected error: {e}", "item_count": 0, "checked_at": time.time()})
    payload = {"items": all_items, "connector_status": statuses}
    cache.write(payload)
    log.info("poll complete: %d items across %d connectors", len(all_items), len(statuses))
    return payload


class Scheduler:
    def __init__(self, interval_seconds: int = 180):
        self.interval = interval_seconds
        self._stop = threading.Event()
        self._thread = None

    def _loop(self):
        while not self._stop.is_set():
            try:
                poll_once()
            except Exception:
                log.exception("poll_once failed unexpectedly")
            self._stop.wait(self.interval)

    def start(self):
        # Do NOT block startup on the first poll: the paced GDELT queries can take
        # minutes, and the page must open immediately while sources fill in.
        # The background loop runs the first poll, then repeats every interval.
        self._thread = threading.Thread(target=self._loop, daemon=True, name="dashboard-scheduler")
        self._thread.start()

    def stop(self):
        self._stop.set()


_poll_lock = threading.Lock()


def request_poll() -> bool:
    """Start a poll in the background unless one is already running. Returns
    False if a poll is already in progress. Used by the manual Refresh button so
    the page never waits for the paced GDELT queries."""
    if not _poll_lock.acquire(blocking=False):
        return False
    def _run():
        try:
            poll_once()
        except Exception:
            log.exception("requested poll failed")
        finally:
            _poll_lock.release()
    threading.Thread(target=_run, daemon=True, name="manual-poll").start()
    return True
