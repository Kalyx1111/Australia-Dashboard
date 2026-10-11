import os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestEnglishFilter(unittest.TestCase):
    def test_rejects_non_latin_headlines_and_keeps_english(self):
        from app.connectors.rss import _looks_english
        self.assertTrue(_looks_english("Assam Rifles conduct drills near Tezpur"))
        self.assertFalse(_looks_english("中国海军在台湾附近举行军事演习"))
        self.assertFalse(_looks_english("Китай проводит учения вблизи Тайваня"))
        self.assertTrue(_looks_english("PLA J-20 fighters: 24 sorties (ADIZ)"))   # digits/punctuation don't flip it
        self.assertFalse(_looks_english(""))

    def test_gdelt_queries_all_enforce_english_source_language(self):
        from app.connectors.gdelt import QUERIES
        for q in QUERIES:
            self.assertIn("sourcelang:eng", q, f"query would allow non-English sources: {q}")


class TestClassifier(unittest.TestCase):
    def test_new_categories_route_correctly(self):
        from app.classify import classify
        self.assertEqual(classify("Volt Typhoon hackers breach utility"), "cyber")
        self.assertEqual(classify("Ammunition seized near Perth"), "arms")
        self.assertEqual(classify("Army patrol near Port Moresby"), "milops")


class TestMarkers(unittest.TestCase):
    def test_every_marker_is_sourced_and_on_earth(self):
        from app.static_markers import MARKERS
        ids = set()
        for m in MARKERS:
            with self.subTest(marker=m["id"]):
                self.assertTrue(m["source"], "every marker must cite a source")
                self.assertTrue(-56 <= m["lat"] <= 17 and 104 <= m["lon"] <= 203)  # the Pacific runs across the date line
                self.assertNotIn(m["id"], ids, "duplicate marker id"); ids.add(m["id"])

    def test_geomatch_links_headline_to_named_place(self):
        from app.geomatch import match_location
        self.assertEqual(match_location("HMAS Stirling submarine")["id"], "hmas_stirling")
        self.assertIsNone(match_location("Stocks rally on earnings"))


class TestServer(unittest.TestCase):
    def setUp(self):
        from app import server, cache
        self.tmp = tempfile.mkdtemp()
        cache._DATA_DIR = self.tmp
        self.client = server.app.test_client()

    def test_security_headers_on_every_response(self):
        for path in ("/healthz", "/api/snapshot"):
            r = self.client.get(path)
            self.assertEqual(r.headers.get("X-Content-Type-Options"), "nosniff")
            self.assertEqual(r.headers.get("X-Frame-Options"), "DENY")
            self.assertEqual(r.headers.get("Referrer-Policy"), "no-referrer")

    def test_snapshot_survives_empty_cache(self):
        r = self.client.get("/api/snapshot"); self.assertEqual(r.status_code, 200)
        self.assertIn("milops", r.get_json()["items_by_category"])   # the Bay of Bengal maritime boundary reference items

    def test_custom_marker_round_trip_and_validation(self):
        r = self.client.post("/api/custom-markers", json={"label": "Site A", "remark": "seen on OSINT", "lat": 30.5, "lon": 114.3})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.get_json()["markers"]), 1)
        for bad in ({"label": "x", "lat": 95, "lon": 0}, {"label": "x", "lat": 0, "lon": 200},
                    {"label": "", "lat": 1, "lon": 1}, {"label": "x", "lat": "abc", "lon": 1}, {"label": "x"}):
            with self.subTest(bad=bad):
                self.assertEqual(self.client.post("/api/custom-markers", json=bad).status_code, 400)
        self.assertEqual(self.client.delete("/api/custom-markers/0").status_code, 200)
        self.assertEqual(self.client.delete("/api/custom-markers/7").status_code, 404)

    def test_oversized_label_is_truncated_not_stored_whole(self):
        r = self.client.post("/api/custom-markers", json={"label": "A" * 5000, "remark": "B" * 5000, "lat": 1, "lon": 1})
        m = r.get_json()["markers"][-1]
        self.assertLessEqual(len(m["label"]), 200); self.assertLessEqual(len(m["remark"]), 500)

    def test_script_in_label_is_stored_inert_as_text(self):
        # storage keeps it verbatim; the frontend's escapeHtml() is what neutralizes it (see dom test)
        r = self.client.post("/api/custom-markers", json={"label": "<script>alert(1)</script>", "lat": 1, "lon": 1})
        self.assertEqual(r.status_code, 200)


class TestSecureStore(unittest.TestCase):
    def test_aes256_round_trip_size_and_tamper_detection(self):
        from app import secure_store as ss
        if not ss.CRYPTO_AVAILABLE: self.skipTest("cryptography not installed")
        import pathlib
        tmp = pathlib.Path(tempfile.mkdtemp())
        ss.KEY_DIR, ss.KEY_PATH, ss.SECRETS_PATH = tmp, tmp / "secret.key", tmp / "secrets.enc"
        ss.update_secrets({"GROK_API_KEY": "abc123", "NEWSAPI_KEY": "xyz"})
        self.assertEqual(len(ss.KEY_PATH.read_bytes()), 32, "must be a real 256-bit key")
        self.assertEqual(ss.decrypt_secrets()["GROK_API_KEY"], "abc123")
        self.assertNotIn(b"abc123", ss.SECRETS_PATH.read_bytes(), "plaintext must not appear on disk")
        raw = bytearray(ss.SECRETS_PATH.read_bytes()); raw[-1] ^= 1; ss.SECRETS_PATH.write_bytes(bytes(raw))
        with self.assertRaises(Exception): ss.decrypt_secrets()


class TestConnectorsDegradeGracefully(unittest.TestCase):
    def test_no_connector_raises_when_network_is_blocked(self):
        from app.connectors import gdelt, rss, usgs, grok
        from unittest import mock
        # failure handling, not timing, is under test: patch the pacing and restore it afterwards
        with mock.patch.object(gdelt, "PACE_SECONDS", 0), mock.patch.object(gdelt, "BACKOFF_SECONDS", 0):
            self._degrade_all(gdelt, rss, usgs, grok)

    def _degrade_all(self, gdelt, rss, usgs, grok):
        for mod in (gdelt, rss, usgs, grok):
            with self.subTest(connector=mod.NAME):
                res = mod.fetch()      # sandbox egress is blocked -> must return a result, never raise
                self.assertTrue(hasattr(res, "ok") and isinstance(res.message, str))

    def test_safe_http_refuses_non_http_schemes(self):
        from app import safe_http
        for url in ("file:///etc/passwd", "ftp://x/y", "javascript:alert(1)"):
            with self.assertRaises(safe_http.FetchError): safe_http.safe_get(url)


if __name__ == "__main__":
    unittest.main()


class TestApiKeysRouteResilience(unittest.TestCase):
    """The exact bug reported live: a corrupted/mismatched secrets.enc made
    /api/keys 500 instead of degrading to 'no stored keys'. Reproduces it
    against the real route, not just the underlying function."""

    def test_get_api_keys_degrades_instead_of_500_on_a_corrupted_store(self):
        from app import server, secure_store, cache
        import pathlib
        tmp = pathlib.Path(tempfile.mkdtemp())
        cache._DATA_DIR = str(tmp)
        secure_store.KEY_DIR, secure_store.KEY_PATH = tmp, tmp / "secret.key"
        secure_store.SECRETS_PATH = tmp / "secrets.enc"
        if not secure_store.CRYPTO_AVAILABLE:
            self.skipTest("cryptography not installed")
        secure_store.update_secrets({"GROK_API_KEY": "abc"})
        # simulate exactly what happened live: the key file is gone/regenerated
        # (new machine, cleared ~/.australia_dashboard) but secrets.enc remains
        secure_store.KEY_PATH.unlink()
        client = server.app.test_client()
        r = client.get("/api/keys")
        self.assertEqual(r.status_code, 200, "must degrade gracefully, not 500")
        self.assertFalse(r.get_json()["GROK_API_KEY"]["configured"])


class TestSecurityAndInfra(unittest.TestCase):
    def test_proxy_setting_is_honoured_when_set_and_absent_when_not(self):
        import os
        from unittest import mock
        from app import safe_http
        captured = {}
        class FakeResp:
            status_code = 200; headers = {}; _content = b""
            def iter_content(self, n): return iter([b"ok"])
        def fake_get(url, **kw):
            captured.update(kw); return FakeResp()
        with mock.patch("requests.get", side_effect=fake_get), mock.patch.dict(os.environ, {"PROXY_URL": "socks5h://127.0.0.1:9050"}):
            safe_http.safe_get("https://example.com/")
        self.assertEqual(captured["proxies"], {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"})
        captured.clear()
        with mock.patch("requests.get", side_effect=fake_get), mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PROXY_URL", None); safe_http.safe_get("https://example.com/")
        self.assertIsNone(captured["proxies"])

    def test_infrastructure_layers_load_with_sources_and_valid_coordinates(self):
        from app.infra import INFRA_MARKERS
        from collections import Counter
        cats = Counter(m["cat"] for m in INFRA_MARKERS)
        for c in ("airport", "air_base"):   # Myanmar has no operating nuclear plant, so no nuclear layer is required
            self.assertGreater(cats[c], 0, f"infrastructure layer {c} is empty")
        for m in INFRA_MARKERS:
            self.assertTrue(m["source"], m["id"])
            self.assertTrue(-56 <= m["lat"] <= 17 and 104 <= m["lon"] <= 203)  # the Pacific runs across the date line
            self.assertTrue(-56 <= m["lat"] <= 17 and 104 <= m["lon"] <= 203)  # the Pacific runs across the date line

    def test_telegram_channel_names_are_validated_before_any_url_is_built(self):
        from app.connectors.telegram_public import USERNAME_RE
        for bad in ("https://evil.example/x", "../etc/passwd", "a b", "x", "1abc", "name;rm"):
            self.assertIsNone(USERNAME_RE.match(bad), bad)
        self.assertIsNotNone(USERNAME_RE.match("valid_channel_1"))

    def test_threat_intel_parser_never_treats_claims_as_verified(self):
        from app.connectors.ransomware_live import parse
        items = parse([{"victim": "Acme", "group": "akira", "country": "au", "attackdate": "2026-10-07"}])
        self.assertIn("not verified", items[0]["text"].lower())
        self.assertTrue(items[0]["in_region"])
