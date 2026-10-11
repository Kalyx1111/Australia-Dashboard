import os, sys, json, tempfile, unittest
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestHeadingRouting(unittest.TestCase):
    def test_fifteen_headings_and_representative_routing(self):
        from app.classify import classify, HEADINGS
        self.assertEqual(len(HEADINGS), 15)
        cases = {
 "B-52 bombers arrive at RAAF Base Tindal": "air",
 "HMAS Stirling hosts US nuclear submarine": "naval",
 "Cyclone Narelle knocks out Gorgon LNG": "hazard",
 "Gorgon LNG outage hits exports": "econ",
 "Rocket Lab launches Electron from Mahia": "space",
 "Woomera hypersonic missile test": "arms",
 "Pine Gap protest draws crowds": "social",
 "Chinese vessel near Perth undersea cable": "scs",
 "West Papua rebels ambush troops": "milops",
 "Vanuatu signs security treaty with Australia": "geo",
 "Cyber attack on Australian hospital": "cyber",
 "Heatwave in Adelaide": "hazard",
 "Pacific Islands Forum leaders summit": "geo",
 "Protests in Papua over mining": "social"
}
        for text, want in cases.items():
            with self.subTest(text=text):
                self.assertEqual(classify(text), want)

    def test_every_routed_heading_is_one_of_the_fifteen(self):
        from app.classify import classify, HEADINGS
        for text in ["", "random words", "Naypyidaw", "dark web", "cyber espionage"]:
            self.assertIn(classify(text), HEADINGS)


class TestTelegramChannels(unittest.TestCase):
    def test_default_list_has_groups_and_excludes_offensive_and_breach_channels(self):
        from app.connectors import telegram_public as tp
        chans = tp.load_channels()
        handles = [c["handle"] for c in chans]
        self.assertGreaterEqual(len(chans), 14)
        self.assertNotIn("OffensiveTwitter", handles)
        self.assertNotIn("HaveIBeenPwnedBreaches", handles)
        for c in chans:
            self.assertIn(c["group"], tp.GROUPS)
            self.assertTrue(tp.USERNAME_RE.match(c["handle"]), c["handle"])
            self.assertFalse(c["verified"], "nothing is marked verified without a live check")

    def test_markup_inside_a_message_cannot_inject_content(self):
        from app.connectors.telegram_public import parse_channel_page
        page = ('<div class="tgme_widget_message_text">Patch now<br>see vendor</div>'
                '<div class="tgme_widget_message_text"><img src=x onerror=alert(1)>Post &amp; text</div>')
        msgs = parse_channel_page(page)
        self.assertEqual(len(msgs), 2)
        self.assertNotIn("onerror", msgs[1])
        self.assertIn("Post & text", msgs[1])


class TestOnionAddresses(unittest.TestCase):
    def _write(self, sources):
        from app.connectors import darkweb_tor as dw
        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, "onion_sources.json")
        json.dump({"sources": sources}, open(path, "w"))
        old = dw.SOURCES_FILE; dw.SOURCES_FILE = path
        try:
            return dw.load_sources()
        finally:
            dw.SOURCES_FILE = old

    def test_only_well_formed_v3_onion_rss_sources_survive(self):
        good = "a" * 56 + ".onion"
        bad_v2 = "a" * 16 + ".onion"
        bad_chars = "0" * 56 + ".onion"   # 0, 1, 8, 9 are not in base32
        loaded = self._write([
            {"name": "ok", "url": f"http://{good}/feed.xml", "type": "rss"},
            {"name": "v2", "url": f"http://{bad_v2}/feed.xml", "type": "rss"},
            {"name": "chars", "url": f"http://{bad_chars}/feed.xml", "type": "rss"},
            {"name": "clearweb", "url": "https://example.com/feed", "type": "rss"},
            {"name": "login", "url": f"http://{good}/x", "type": "html"},
        ])
        self.assertEqual([s["name"] for s in loaded], ["ok"])


class TestInstagram(unittest.TestCase):
    def test_not_configured_without_official_credentials(self):
        from app.connectors import instagram_graph as ig
        with mock.patch.dict(os.environ, {}, clear=True):
            res = ig.fetch()
        self.assertFalse(res.configured)
        self.assertIn("INSTAGRAM_IG_USER_ID", res.message)

    def test_token_is_redacted_from_any_message(self):
        from app.connectors import instagram_graph as ig
        with mock.patch.dict(os.environ, {"INSTAGRAM_ACCESS_TOKEN": "SECRET123"}, clear=False):
            self.assertNotIn("SECRET123", ig._redact("error at https://graph.facebook.com/x?access_token=SECRET123"))

    def test_usernames_are_validated(self):
        from app.connectors import instagram_graph as ig
        tmp = tempfile.mkdtemp(); path = os.path.join(tmp, "a.json")
        json.dump({"accounts": ["good.name_1", "bad name", "../etc", "x" * 40]}, open(path, "w"))
        old = ig.ACCOUNTS_FILE; ig.ACCOUNTS_FILE = path
        try:
            self.assertEqual(ig.load_accounts(), ["good.name_1"])
        finally:
            ig.ACCOUNTS_FILE = old


class TestDarkWebFeeds(unittest.TestCase):
    def test_ransomware_claims_are_darkweb_and_never_stated_as_verified(self):
        from app.connectors.ransomware_live import parse
        items = parse([{"victim": "Acme", "group": "akira", "country": "au", "attackdate": "2026-10-07"}])
        self.assertEqual(items[0]["category"], "darkweb")
        self.assertIn("not verified", items[0]["text"].lower())
        self.assertTrue(items[0]["in_region"])

    def test_tor_not_running_is_reported_not_crashed(self):
        from app import safe_http
        with mock.patch.object(safe_http, "tor_port", return_value=None):
            from app.connectors import darkweb_tor as dw
            tmp = tempfile.mkdtemp(); path = os.path.join(tmp, "s.json")
            json.dump({"sources": [{"name": "x", "url": "http://" + "a" * 56 + ".onion/f", "type": "rss"}]}, open(path, "w"))
            old = dw.SOURCES_FILE; dw.SOURCES_FILE = path
            try:
                res = dw.fetch()
            finally:
                dw.SOURCES_FILE = old
        self.assertFalse(res.ok)
        self.assertIn("Tor not running", res.message)


class TestGdeltPacing(unittest.TestCase):
    def test_every_query_is_english_source_only_and_paced(self):
        from app.connectors import gdelt
        self.assertTrue(all("sourcelang:eng" in q for q in gdelt.QUERIES))
        self.assertGreaterEqual(gdelt.PACE_SECONDS, 5.0)
        self.assertGreater(len(gdelt.QUERIES), 10)

    def test_429_is_retried_once_after_backoff(self):
        from app.connectors import gdelt
        responses = [mock.Mock(status_code=429), mock.Mock(status_code=200)]
        fake_safe = mock.Mock(safe_get=mock.Mock(side_effect=responses))
        with mock.patch("time.sleep") as sleep:
            r = gdelt._get(fake_safe, "Pakistan sourcelang:eng")
        self.assertEqual(r.status_code, 200)
        sleep.assert_called_once_with(gdelt.BACKOFF_SECONDS)


class TestRegistryAndRefresh(unittest.TestCase):
    def test_new_connectors_are_registered(self):
        from app import scheduler
        names = [m.NAME for m in scheduler.REGISTRY]
        self.assertIn("instagram_graph", names)
        self.assertIn("darkweb_tor", names)
        self.assertIn("ransomware_live", names)

    def test_instagram_and_tor_keys_are_offered_in_the_settings_panel(self):
        from app import server
        keys = server.KEY_FIELDS
        self.assertIn("INSTAGRAM_ACCESS_TOKEN", keys)
        self.assertIn("INSTAGRAM_IG_USER_ID", keys)


if __name__ == "__main__":
    unittest.main()
