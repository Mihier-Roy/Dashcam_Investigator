"""
Phase 3: tests for the welcome screen.

The full app.MainWindow can't be instantiated on this headless host
(QtWebEngine + libEGL), but we can:

- render the template and assert it has the controls JS expects,
- verify the welcome.js asset exists and references the bridge,
- inspect the BridgeController surface that MainWindow implements
  without instantiating MainWindow itself.
"""

from __future__ import annotations

import inspect

from dashcam_investigator.gui.web import renderer
from dashcam_investigator.gui.web.bridge import BridgeController


def test_welcome_template_renders_required_controls() -> None:
    html = renderer.render("welcome.html")
    assert 'id="btn-new"' in html
    assert 'id="btn-open"' in html
    assert "New project" in html
    assert "Open project" in html


def test_welcome_template_loads_page_script() -> None:
    html = renderer.render("welcome.html")
    assert "js/pages/welcome.js" in html


def test_welcome_template_inlines_icons() -> None:
    html = renderer.render("welcome.html")
    assert html.count("<svg") >= 2  # plus + folder


def test_welcome_js_calls_bridge_actions() -> None:
    js = (renderer.static_path() / "js" / "pages" / "welcome.js").read_text()
    assert "apiReady" in js
    assert "requestNewProject" in js
    assert "requestOpenProject" in js


def test_bridge_js_exposes_api_ready_promise() -> None:
    js = (renderer.static_path() / "js" / "bridge.js").read_text()
    assert "apiReady" in js
    assert "Promise" in js


def test_app_css_defines_welcome_layout() -> None:
    css = (renderer.static_path() / "css" / "app.css").read_text()
    for cls in (".welcome", ".welcome-hero", ".welcome-grid"):
        assert cls in css, f"app.css missing {cls}"


def test_main_window_implements_bridge_controller_surface() -> None:
    """Verify MainWindow declares every method the BridgeController Protocol expects."""
    # Import lazily so the test still runs if QtWebEngine isn't available
    # for direct instantiation (we only need the class object).
    try:
        from dashcam_investigator.gui.app import MainWindow
    except ImportError as exc:
        import pytest

        pytest.skip(f"MainWindow not importable on this host: {exc}")

    expected = {
        name
        for name, _ in inspect.getmembers(BridgeController, predicate=inspect.isfunction)
        if not name.startswith("_")
    }
    actual = {name for name in dir(MainWindow) if not name.startswith("_")}
    missing = expected - actual
    assert not missing, f"MainWindow missing controller methods: {missing}"
