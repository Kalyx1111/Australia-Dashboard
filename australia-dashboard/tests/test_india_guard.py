"""India rule: military sites inside India's survey outline are not shown outside focus dashboards; civil points and news are."""
import os
import sys
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app import india_guard as g  # noqa: E402


def _clean_rule():
    """The rule for dashboards that are not in focus mode, restored afterwards so the other tests see the real configuration."""
    return mock.patch.object(g, "_CFG", {"mode": "clean"})


def test_survey_outline_includes_pok_gilgit_and_aksai_chin():
    assert g.inside_india(35.92, 74.31)  # Gilgit
    assert g.inside_india(35.40, 79.20)  # Aksai Chin
    assert g.inside_india(34.37, 73.47)  # Muzaffarabad


def test_points_outside_india_are_never_blocked():
    with _clean_rule():
        assert not g.block_record({"name": "Karachi naval base", "cat": "navy_base", "lat": 24.85, "lon": 67.0})


def test_military_inside_india_is_blocked_and_civil_is_not():
    with _clean_rule():
        assert g.block_record({"name": "Karwar naval base", "cat": "navy_base", "lat": 14.8, "lon": 74.1})
        assert not g.block_record({"name": "Mumbai port", "cat": "seaport", "lat": 18.94, "lon": 72.83})
        assert not g.block_record({"name": "Jaipur pipeline", "cat": "pipeline", "lat": 26.9, "lon": 75.8})


def test_news_and_notes_are_never_blocked():
    with _clean_rule():
        assert not g.block_record({"label": "India test-fires a new missile", "text": "Indian Navy base at Karwar"})


def test_clean_points_removes_only_military_records_inside_the_outline():
    data = [{"name": "Karwar naval base", "cat": "navy_base", "lat": 14.8, "lon": 74.1},
            {"name": "Mumbai port", "cat": "seaport", "lat": 18.94, "lon": 72.83}]
    with _clean_rule():
        assert [r["name"] for r in g.clean_points(data)] == ["Mumbai port"]
