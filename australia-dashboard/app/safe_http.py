"""Hardened fetch wrapper - every connector goes through this, never raw requests.

Timeout, a streamed size cap, http/https only, and a generic browser User-Agent
(so server logs don't single out a monitoring tool; this is not anonymity).

Proxies:
- PROXY_URL (optional, e.g. a VPN's local proxy or socks5h://127.0.0.1:9050)
  routes clear-web source requests through that proxy.
- Dark-web (.onion) requests ALWAYS go through a Tor SOCKS proxy, never direct,
  and are only made when Tor is actually listening locally (see tor_port()).
"""
from __future__ import annotations
import os
import socket
import requests

TIMEOUT = (6, 15)
MAX_BYTES = 8 * 1024 * 1024
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
TOR_PORTS = (9050, 9150)   # 9050: Tor service / expert bundle.  9150: Tor Browser's bundled SOCKS port.


class FetchError(Exception):
    pass


def tor_port():
    """The first Tor SOCKS port that is actually accepting connections, else None.
    Tor Browser must be open (9150) or the Tor service running (9050)."""
    for port in TOR_PORTS:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.6)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return port
    return None


def _proxies_for(url: str, explicit=None):
    if explicit is not None:
        return explicit
    from urllib.parse import urlsplit
    host = (urlsplit(url).hostname or "").lower()
    if host.endswith(".onion"):
        port = tor_port()
        if port is None:
            raise FetchError("Tor is not running - start Tor Browser (port 9150) or the Tor service (port 9050)")
        p = f"socks5h://127.0.0.1:{port}"
        return {"http": p, "https": p}
    proxy = os.environ.get("PROXY_URL", "").strip()
    return {"http": proxy, "https": proxy} if proxy else None


def safe_get(url: str, headers: dict | None = None, params: dict | None = None, proxies=None):
    if not (url.startswith("http://") or url.startswith("https://")):
        raise FetchError(f"refused non-http(s) scheme: {url}")
    hdrs = {"User-Agent": USER_AGENT}
    if headers:
        hdrs.update(headers)
    r = requests.get(url, headers=hdrs, params=params, timeout=TIMEOUT, stream=True,
                     proxies=_proxies_for(url, proxies))
    total, chunks = 0, []
    for chunk in r.iter_content(8192):
        total += len(chunk)
        if total > MAX_BYTES:
            raise FetchError(f"response exceeded {MAX_BYTES} byte cap")
        chunks.append(chunk)
    r._content = b"".join(chunks)
    return r
