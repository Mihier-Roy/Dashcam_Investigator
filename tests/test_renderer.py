"""Unit tests for the Jinja2 renderer and asset path resolution."""

from pathlib import Path

import pytest

from dashcam_investigator.gui.web import renderer


def test_assets_path_points_at_source_tree() -> None:
    path = renderer.assets_path()
    assert path.is_dir(), f"assets_path() returned non-directory: {path}"
    assert (path / "templates").is_dir()
    assert (path / "static").is_dir()
    assert (path / "qss").is_dir()


def test_static_url_uses_dci_scheme_by_default() -> None:
    assert renderer.static_url("css/tokens.css") == "dci://app/static/css/tokens.css"
    assert renderer.static_url("/css/tokens.css") == "dci://app/static/css/tokens.css"


def test_static_url_accepts_alternate_base() -> None:
    url = renderer.static_url("css/tokens.css", base="static/")
    assert url == "static/css/tokens.css"


def test_render_base_template_produces_html() -> None:
    html = renderer.render("base.html")
    assert html.startswith("<!doctype html>")
    assert "<html" in html
    assert "tokens.css" in html


def test_render_passes_context_through() -> None:
    html = renderer.render("base.html", theme="dark")
    assert 'data-theme="dark"' in html


def test_static_global_uses_dci_scheme_in_output() -> None:
    html = renderer.render("base.html")
    assert "dci://app/static/css/tokens.css" in html


def test_tokens_css_exists_and_defines_root() -> None:
    tokens = renderer.static_path() / "css" / "tokens.css"
    assert tokens.is_file()
    text = tokens.read_text()
    assert ":root" in text
    assert "--bg" in text
    assert "prefers-color-scheme: dark" in text


@pytest.mark.parametrize(
    "subdir, expected",
    [
        ("templates", Path("templates")),
        ("static", Path("static")),
        ("qss", Path("qss")),
    ],
)
def test_helper_paths_match_assets_path(subdir: str, expected: Path) -> None:
    helpers = {
        "templates": renderer.templates_path,
        "static": renderer.static_path,
        "qss": renderer.qss_path,
    }
    assert helpers[subdir]() == renderer.assets_path() / expected
