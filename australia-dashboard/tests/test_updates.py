"""Permanent-data updates, tested offline with recorded samples (no network)."""
import datetime as dt
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app import india_guard as g  # noqa: E402
from app import updates as u  # noqa: E402

CFG = {"mode": "clean", "bbox": [60, 0, 100, 40], "layer_cats": ["conflict", "pipeline"],
       "infra_layer_cats": ["airport", "air_base", "nuclear_plant", "seaport", "cantonment", "navy_base"]}
AIRPORTS = ("id,ident,type,name,latitude_deg,longitude_deg,iso_country,icao_code\n"
            "1,AAA,large_airport,Test International,28.5,77.1,IN,VIDD\n"
            "2,BBB,small_airport,Tiny Strip,20,70,IN,\n"
            "3,CCC,medium_airport,Outside The Box,50,10,DE,\n")
WRI = ("name,gppd_idnr,capacity_mw,latitude,longitude,primary_fuel,commissioning_year,owner,url\n"
       "KAKRAPAR,IND1,440,21.2,72.6,Nuclear,1993,NPCIL,https://example.org/a\n"
       "SOLAR X,IND2,10,22,70,Solar,2015,Co,\n")
OVERPASS = {"elements": [
    {"type": "node", "id": 11, "lat": 26.0, "lon": 80.0, "tags": {"military": "airfield", "name": "Test Air Station",
                                                                  "operator": "Air Force"}, "timestamp": "2026-01-02T00:00:00Z"},
    {"type": "way", "id": 12, "center": {"lat": 27.0, "lon": 81.0}, "tags": {"military": "base", "name": "Test Garrison"}},
]}


class TestSources(unittest.TestCase):
    def setUp(self):
        g._CFG = {"mode": "clean"}

    def tearDown(self):
        g._CFG = None

    def test_ourairports_keeps_large_and_medium_airports_inside_the_box(self):
        with mock.patch.object(u, "_get", return_value=AIRPORTS):
            recs, _ = u.fetch_ourairports(CFG, {"airport"}, {"left": 9, "stopped": False})
        self.assertEqual([r["name"] for r in recs], ["Test International"])
        self.assertEqual(recs[0]["cat"], "airport")
        self.assertIn("OurAirports", recs[0]["source"])

    def test_wri_keeps_nuclear_plants_only(self):
        with mock.patch.object(u, "_get", return_value=WRI):
            recs, _ = u.fetch_wri(CFG, {"nuclear_plant"}, {"left": 9, "stopped": False})
        self.assertEqual([r["name"] for r in recs], ["KAKRAPAR"])
        self.assertEqual(recs[0]["cat"], "nuclear_plant")

    def test_a_source_is_skipped_when_the_dashboard_has_no_matching_layer(self):
        recs, note = u.fetch_wri(CFG, {"airport"}, {"left": 9, "stopped": False})
        self.assertIsNone(recs)
        self.assertIn("no nuclear layer", note)

    def test_overpass_uses_only_the_layers_this_dashboard_has(self):
        cfg = dict(CFG, bbox=[60, 20, 70, 30])
        with mock.patch.object(u, "_get", return_value=json.dumps(OVERPASS)), mock.patch.object(u.time, "sleep"):
            recs, _ = u.fetch_osm_military(cfg, {"air_base"}, {"left": 50, "stopped": False})
        self.assertEqual({r["cat"] for r in recs}, {"air_base"})
        self.assertEqual(len({r["id"] for r in recs}), len(recs))
        self.assertTrue(all("openstreetmap" in r["source"].lower() for r in recs))

    def test_ucdp_follows_the_pages_and_reads_the_coordinates(self):
        page1 = {"Result": [{"id": 1, "latitude": 34.5, "longitude": 70.1, "side_a": "A", "side_b": "B", "best": 4,
                             "type_of_violence": 1, "date_start": "2026-09-01"}], "NextPageUrl": "next"}
        page2 = {"Result": [{"id": 2, "latitude": 35.0, "longitude": 71.0, "side_a": "C", "side_b": "D", "best": 0,
                             "type_of_violence": 3, "date_start": "2026-09-02"}], "NextPageUrl": ""}
        pages = iter([json.dumps(page1), json.dumps(page2)])
        cfg = dict(CFG, bbox=[60, 20, 80, 40], ucdp_versions=["25.1"])
        with mock.patch.object(u, "_get", side_effect=lambda *a, **k: next(pages)):
            recs, _ = u.fetch_ucdp(cfg, {"conflict"}, {"left": 9, "stopped": False})
        self.assertEqual(len(recs), 2)
        self.assertTrue(all(r["cat"] == "conflict" for r in recs))
        self.assertIn("UCDP", recs[0]["source"])


class TestIndiaRule(unittest.TestCase):
    def setUp(self):
        g._CFG = {"mode": "clean"}

    def tearDown(self):
        g._CFG = None

    def test_military_inside_india_is_dropped_but_civil_points_are_kept(self):
        self.assertTrue(g.block_record({"name": "Karwar naval base", "cat": "navy_base", "lat": 14.8, "lon": 74.1}))
        self.assertFalse(g.block_record({"name": "Mumbai port", "cat": "seaport", "lat": 18.94, "lon": 72.83}))
        self.assertFalse(g.block_record({"name": "Jaipur pipeline", "cat": "pipeline", "lat": 26.9, "lon": 75.8}))

    def test_a_military_name_inside_india_is_dropped_even_in_a_civil_layer(self):
        self.assertTrue(g.block_record({"name": "Indian Air Force station", "cat": "airport", "lat": 26.9, "lon": 75.8}))

    def test_focus_mode_keeps_military_inside_india(self):
        g._CFG = {"mode": "focus"}
        self.assertFalse(g.block_record({"name": "Karwar naval base", "cat": "navy_base", "lat": 14.8, "lon": 74.1}))

    def test_news_about_india_is_never_filtered(self):
        self.assertFalse(g.block_record({"label": "Indian forces leave Maldives", "text": "India signs a port deal"}))


class TestMergeAndSchedule(unittest.TestCase):
    def setUp(self):
        g._CFG = {"mode": "clean"}

    def tearDown(self):
        g._CFG = None

    def test_points_next_to_existing_ones_are_not_added_twice(self):
        tmp = tempfile.mkdtemp()
        near = {"id": "a", "cat": "airport", "lat": 28.505, "lon": 77.102, "name": "x"}
        far = {"id": "b", "cat": "airport", "lat": 28.9, "lon": 77.1, "name": "y"}
        with open(os.path.join(tmp, "ourairports.json"), "w", encoding="utf-8") as fh:
            json.dump({"records": [near, far]}, fh)
        with mock.patch.object(u, "UPDATE_DIR", tmp):
            kept = u.load_records([{"cat": "airport", "lat": 28.5, "lon": 77.1}])
        self.assertEqual([r["id"] for r in kept], ["b"])

    def test_age_in_days_drives_the_weekly_schedule(self):
        old = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=8)).isoformat()
        self.assertGreaterEqual(u._age_days(old), 7)

    def test_a_failed_source_keeps_its_last_good_data_and_reports_the_error(self):
        tmp = tempfile.mkdtemp()
        prior = {"source": "ourairports", "records": [{"id": "old", "cat": "airport", "lat": 25, "lon": 70, "name": "Old"}]}
        with open(os.path.join(tmp, "ourairports.json"), "w", encoding="utf-8") as fh:
            json.dump(prior, fh)
        cfg = dict(CFG, sources=["ourairports"], bbox=[60, 20, 80, 40])
        with mock.patch.object(u, "UPDATE_DIR", tmp), mock.patch.object(u, "STATUS_FILE", os.path.join(tmp, "status.json")), \
                mock.patch.object(u, "LOG_FILE", os.path.join(tmp, "log.txt")), \
                mock.patch.object(u, "load_config", return_value=cfg), \
                mock.patch.object(u, "_get", side_effect=OSError("network unreachable")):
            u.run_update("test")
        with open(os.path.join(tmp, "status.json"), encoding="utf-8") as fh:
            status = json.load(fh)
        with open(os.path.join(tmp, "ourairports.json"), encoding="utf-8") as fh:
            kept = json.load(fh)
        self.assertEqual(status["sources"]["ourairports"]["state"], "error")
        self.assertEqual(kept["records"][0]["id"], "old")

    def test_status_reports_the_next_run_once_an_update_has_happened(self):
        tmp = tempfile.mkdtemp()
        with open(os.path.join(tmp, "status.json"), "w", encoding="utf-8") as fh:
            json.dump({"last_run": "2026-10-01T00:00:00+00:00", "sources": {}}, fh)
        with mock.patch.object(u, "STATUS_FILE", os.path.join(tmp, "status.json")), \
                mock.patch.object(u, "load_config", return_value=dict(CFG, update_every_days=7)):
            st = u.status()
        self.assertTrue(st["next_run"].startswith("2026-10-08"))


if __name__ == "__main__":
    unittest.main()
