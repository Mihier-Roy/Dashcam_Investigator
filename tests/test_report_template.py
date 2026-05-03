"""
Phase 8: tests for the report template + inline_css renderer helper.

Covers concerns the existing test_generate_report.py doesn't:
  - inline_css() returns the file contents,
  - report.html stitches in tokens + base + components + report CSS,
  - the iframe-src helper produces relative posix paths even on Windows
    drive layouts.
"""

from __future__ import annotations

from pathlib import Path

from dashcam_investigator.core import generate_report as report_module
from dashcam_investigator.gui.web import renderer


# --- inline_css ------------------------------------------------------
def test_inline_css_reads_static_file_contents() -> None:
    css = str(renderer.inline_css("css/tokens.css"))
    assert ":root" in css
    assert "--accent" in css


def test_inline_css_unknown_returns_empty_string() -> None:
    assert str(renderer.inline_css("css/does-not-exist.css")) == ""


def test_inline_css_is_jinja_global() -> None:
    env = renderer.get_env()
    assert "inline_css" in env.globals


# --- report.html template (without going through generate_report) ---
def test_report_template_inlines_all_required_stylesheets() -> None:
    html = renderer.render(
        "report.html",
        case=type("C", (), {"case_name": "X", "investigator_name": "Y"})(),
        flagged=[],
        video_info={},
        video_iframes={},
        generated_date="2026-05-03 12:00",
    )
    # Every sheet that the in-app theme uses is present inline.
    assert ":root" in html  # tokens.css
    assert "::selection" in html  # base.css
    assert ".btn-primary" in html  # components.css
    assert ".report-sidebar" in html  # report.css


def test_report_template_does_not_load_external_assets() -> None:
    html = renderer.render(
        "report.html",
        case=type("C", (), {"case_name": "X", "investigator_name": "Y"})(),
        flagged=[],
        video_info={},
        video_iframes={},
        generated_date="2026-05-03 12:00",
    )
    assert "dci://" not in html
    assert 'rel="stylesheet"' not in html
    assert "qwebchannel.js" not in html


# --- _rel_url helper -------------------------------------------------
def test_rel_url_returns_posix_relative_to_base(tmp_path: Path) -> None:
    base = tmp_path / "Reports"
    base.mkdir()
    target = tmp_path / "Maps" / "vid_map.html"
    target.parent.mkdir()
    target.write_text("<html/>")

    rel = report_module._rel_url(str(target), base)
    assert rel == "../Maps/vid_map.html"
    assert "\\" not in rel


def test_rel_url_handles_absolute_target_outside_tree(tmp_path: Path) -> None:
    """Same-drive but elsewhere — still resolved to a posix relative path."""
    base = tmp_path / "a" / "Reports"
    base.mkdir(parents=True)
    target = tmp_path / "b" / "x.html"
    target.parent.mkdir()

    rel = report_module._rel_url(str(target), base)
    # Cross-tree relative: should walk back up + over.
    assert rel.startswith("../") or rel.startswith("..")
    assert rel.endswith("x.html")


# --- _collect_info ---------------------------------------------------
def test_collect_info_returns_empty_when_meta_files_missing(tmp_path: Path) -> None:
    from dashcam_investigator.project_manager.project_datatypes import FileAttributes

    video_path = tmp_path / "v.mp4"
    video_path.write_text("x")
    video = FileAttributes(file_path=video_path)
    assert report_module._collect_info(video) == {}


def test_collect_info_returns_empty_when_csv_missing(tmp_path: Path) -> None:
    from dashcam_investigator.project_manager.project_datatypes import FileAttributes

    video_path = tmp_path / "v.mp4"
    video_path.write_text("x")
    video = FileAttributes(file_path=video_path)
    video.meta_files = ["whatever.gpx", str(tmp_path / "missing.csv")]
    assert report_module._collect_info(video) == {}


def test_collect_info_picks_known_fields(tmp_path: Path) -> None:
    from dashcam_investigator.project_manager.project_datatypes import FileAttributes

    csv_path = tmp_path / "meta.csv"
    csv_path.write_text(
        "CreateDate,Duration,Format,Information\n"
        "2024-01-15 14:30,00:05:30,MPEG-4,Test Device\n"
    )
    video_path = tmp_path / "v.mp4"
    video_path.write_text("x")
    video = FileAttributes(file_path=video_path)
    video.meta_files = ["unused.gpx", str(csv_path)]

    info = report_module._collect_info(video)
    assert info["Create date"] == "2024-01-15 14:30"
    assert info["Duration"] == "00:05:30"
    assert "MPEG-4" in info["Device"]
    assert "Test Device" in info["Device"]
