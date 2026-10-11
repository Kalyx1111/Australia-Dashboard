"""
Boots the REAL Flask server on a real socket and fetches pages exactly as a
browser would - no inlining, no test-only shortcuts. This is the class of
test that would have caught the actual bug reported live: dashboard.html
referenced <script src="dashboard.js"> (resolves against the PAGE's own
path, "/", per the tag's own semantics - not against "/static/", where the
file is actually served) - a 404 that a code-level unit test can't see
because it never fetches anything, it just imports functions and calls them.
"""
import os
import re
import sys
import threading
import time
import unittest
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestLiveDelivery(unittest.TestCase):
    PORT = 18830

    @classmethod
    def setUpClass(cls):
        from werkzeug.serving import make_server
        from app.server import app
        cls.server = make_server("127.0.0.1", cls.PORT, app, threaded=True)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.3)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=5)

    def _get(self, path):
        url = f"http://127.0.0.1:{self.PORT}{path}"
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def test_every_script_and_link_src_actually_resolves(self):
        """The real regression test: parse every <script src> / <link href>
        out of the actual HTML the server returns for '/', then fetch each
        EXACT path a browser would (relative to '/', not guessed as
        '/static/...') and require 200. This is precisely the check that
        was missing - previous tests fetched /static/dashboard.js directly,
        which passed even while the page's own reference to it was broken."""
        status, body = self._get("/")
        self.assertEqual(status, 200)
        html = body.decode("utf-8")
        srcs = re.findall(r'<script[^>]+src="([^"]+)"', html) + re.findall(r'<link[^>]+href="([^"]+)"', html)
        self.assertTrue(srcs, "expected at least one script/link tag - none found, test itself may be broken")
        for src in srcs:
            with self.subTest(src=src):
                # urljoin (not naive string concatenation) is what actually
                # matches how a browser resolves a relative src against the
                # page's own URL ("/") - the previous version of this test
                # built the URL by hand and got a confusing error instead of
                # a clean 404 on exactly the case that mattered.
                from urllib.parse import urljoin
                path = urljoin("/", src)
                s, _ = self._get(path)
                self.assertEqual(s, 200, f"{src} (browser would request {path}) did not resolve")

    def test_served_js_is_the_same_file_the_page_references(self):
        _, html = self._get("/")
        m = re.search(r'<script[^>]+src="([^"]+)"', html.decode("utf-8"))
        self.assertIsNotNone(m, "no script src found in the served page")
        status, js_body = self._get(m.group(1))
        self.assertEqual(status, 200)
        self.assertIn(b"function escapeHtml", js_body, "served JS doesn't look like the real dashboard script")

    def test_snapshot_and_trends_reachable_on_the_real_socket(self):
        for path in ("/api/snapshot", "/api/keys", "/healthz"):
            status, _ = self._get(path)
            self.assertEqual(status, 200, path)


if __name__ == "__main__":
    unittest.main()
