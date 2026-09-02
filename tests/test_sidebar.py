"""
Phase 4: tests for the sidebar WebPanel.

These tests verify the template + asset wiring; the JS itself runs only
inside QtWebEngine, which isn't loadable on this headless host.
"""

from __future__ import annotations

from dashcam_investigator.gui.web import renderer


def test_sidebar_template_renders_required_anchors() -> None:
    html = renderer.render("sidebar.html")
    for needle in (
        'id="case-name"',
        'id="case-meta"',
        'id="filter"',
        'id="sidebar-body"',
        'data-mode="list"',
        'data-mode="tree"',
    ):
        assert needle in html, f"sidebar.html missing {needle!r}"


def test_sidebar_template_loads_page_script() -> None:
    html = renderer.render("sidebar.html")
    assert "js/pages/sidebar.js" in html


def test_sidebar_template_inlines_search_icon() -> None:
    html = renderer.render("sidebar.html")
    # Search icon (circle + line) should appear inline in the input-group
    assert "input-group" in html
    assert html.count("<svg") >= 2  # search + initial-empty-state video icon


def test_sidebar_js_subscribes_to_required_events() -> None:
    js = (renderer.static_path() / "js" / "pages" / "sidebar.js").read_text()
    for needle in (
        '"project"',
        '"flag-changed"',
        '"video"',
        "selectVideo",
        "buildTree",
        "filterVideos",
    ):
        assert needle in js, f"sidebar.js missing {needle!r}"


def test_sidebar_js_handles_path_separators() -> None:
    """Tree builder must normalize Windows backslashes."""
    js = (renderer.static_path() / "js" / "pages" / "sidebar.js").read_text()
    assert r"replace(/\\/g, " in js


def test_sidebar_js_has_arrow_key_navigation() -> None:
    js = (renderer.static_path() / "js" / "pages" / "sidebar.js").read_text()
    assert "selectByName" in js
    assert "ArrowDown" in js
    assert "ArrowUp" in js
    # Regression: keyboard focus must be re-queried on the freshly-rendered
    # DOM after selectByName()/render() replaces body.innerHTML, not applied
    # to the stale (now-detached) row element captured before the re-render.
    assert "CSS.escape" in js


def test_app_css_defines_sidebar_layout() -> None:
    css = (renderer.static_path() / "css" / "app.css").read_text()
    for cls in (
        ".sidebar",
        ".sidebar-header",
        ".sidebar-controls",
        ".sidebar-body",
        ".sidebar-tabs",
        ".tree-folder",
        ".tree-children",
    ):
        assert cls in css, f"app.css missing {cls}"
