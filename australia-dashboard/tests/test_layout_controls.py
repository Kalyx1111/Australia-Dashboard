"""The screen layout controls (Full map, Full screen, Hide bars) are on the shipped page,
load from a same-origin file, and the shipped page is exactly what build_frontend.py builds."""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "static" / "dashboard.html").read_text(encoding="utf-8")


def test_the_page_offers_the_three_layout_controls():
    for token in ('id="mapTools"', 'id="btnFullMap"', 'id="btnFullScreen"', 'id="selHideBars"'):
        assert token in PAGE, token


def test_the_layout_script_is_a_same_origin_file_and_the_page_has_no_inline_script():
    assert '<script src="/static/layout.js" defer></script>' in PAGE
    assert (ROOT / "static" / "layout.js").is_file()
    assert "<script>" not in PAGE


def test_the_shipped_page_is_exactly_what_the_generator_builds(tmp_path):
    work = tmp_path / "build"
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "node_modules"))
    subprocess.run([sys.executable, "build_frontend.py"], cwd=work, check=True, capture_output=True, timeout=600)
    for name in ("dashboard.html", "dashboard.js"):
        assert (ROOT / "static" / name).read_bytes() == (work / "static" / name).read_bytes(), name
