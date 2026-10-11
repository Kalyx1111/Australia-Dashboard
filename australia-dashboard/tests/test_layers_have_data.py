"""Every layer toggle on the built page must have real data behind it.

The China build shipped toggles with nothing behind them (airports, seaports and
cantonments appeared to be broken). This test fails the build if any toggle on the
page has zero items in the live snapshot, so that cannot happen silently again.
The earthquake toggle is the one exception: it fills only when USGS reports events.
"""
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LIVE_ONLY = {"hazard", "custom"}   # fill from USGS or from the user's own plotted markers


class TestEveryToggleHasData(unittest.TestCase):
    def test_each_layer_toggle_on_the_page_has_at_least_one_item(self):
        from app import server
        html = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 "static", "dashboard.html"), encoding="utf-8").read()
        toggles = re.findall(r'data-layer="(\w+)"', html)
        self.assertTrue(toggles, "no layer toggles found on the page")
        counts = server.app.test_client().get("/api/snapshot").get_json()["layer_counts"]
        empty = [t for t in toggles if counts.get(t, 0) == 0 and t not in LIVE_ONLY]
        self.assertEqual(empty, [], f"toggles with no data behind them: {empty}")


if __name__ == "__main__":
    unittest.main()
