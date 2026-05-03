"""
Phase 9: tests for keyboard shortcuts + the bridge surface they depend on.

The shortcuts JS itself runs only inside QtWebEngine, but the contract
between bridge / shortcuts.js / panel listeners is verifiable by
inspection.
"""

from __future__ import annotations

import sys
from typing import Any

import pytest
from PySide6.QtCore import QCoreApplication

from dashcam_investigator.gui.web import renderer
from dashcam_investigator.gui.web.bridge import Bridge, BridgeController


# --- shortcuts.js asset wiring --------------------------------------
def test_shortcuts_js_exists_and_handles_required_keys() -> None:
    js = (renderer.static_path() / "js" / "shortcuts.js").read_text()
    for needle in (
        '"/"',
        "ArrowRight",
        "ArrowLeft",
        '"f"',
        "ctrlKey",
        "isTyping",
        "focusSearch",
        "toggleFlagCurrent",
        "selectNextVideo",
        "selectPreviousVideo",
        "requestSaveNotes",
    ):
        assert needle in js, f"shortcuts.js missing {needle!r}"


def test_base_html_loads_shortcuts_when_app() -> None:
    html = renderer.render("base.html")  # app=True by default
    assert "js/shortcuts.js" in html


def test_base_html_omits_shortcuts_in_report_mode() -> None:
    html = renderer.render("base.html", app=False)
    assert "js/shortcuts.js" not in html
    assert "qwebchannel.js" not in html


def test_bridge_js_relays_focus_and_save_signals() -> None:
    js = (renderer.static_path() / "js" / "bridge.js").read_text()
    assert '"focus_search"' in js
    assert '"focus-search"' in js
    assert '"save_requested"' in js
    assert '"save-requested"' in js


def test_sidebar_js_listens_for_focus_search() -> None:
    js = (renderer.static_path() / "js" / "pages" / "sidebar.js").read_text()
    assert '"focus-search"' in js
    assert "filterInput.focus" in js


def test_notes_js_listens_for_save_requested() -> None:
    js = (renderer.static_path() / "js" / "pages" / "notes.js").read_text()
    assert '"save-requested"' in js


# --- Bridge slots ----------------------------------------------------
@pytest.fixture(scope="module")
def qcoreapp() -> QCoreApplication:
    return QCoreApplication.instance() or QCoreApplication(sys.argv)


class FakeController:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[Any, ...]]] = []

    def __getattr__(self, name):
        def _record(*args):
            self.calls.append((name, args))

        return _record


def test_focus_search_slot_emits_signal(qcoreapp) -> None:
    bridge = Bridge(FakeController())
    received: list = []
    bridge.focus_search.connect(lambda: received.append(True))
    bridge.focusSearch()
    assert received == [True]


def test_request_save_notes_slot_emits_signal(qcoreapp) -> None:
    bridge = Bridge(FakeController())
    received: list = []
    bridge.save_requested.connect(lambda: received.append(True))
    bridge.requestSaveNotes()
    assert received == [True]


def test_shortcut_slots_forward_to_controller(qcoreapp) -> None:
    controller = FakeController()
    bridge = Bridge(controller)
    bridge.toggleFlagCurrent()
    bridge.selectNextVideo()
    bridge.selectPreviousVideo()
    method_calls = [name for name, _ in controller.calls]
    assert "toggle_flag_current" in method_calls
    assert "select_next_video" in method_calls
    assert "select_previous_video" in method_calls


def test_bridge_controller_protocol_includes_shortcut_methods() -> None:
    import inspect

    methods = {
        name
        for name, _ in inspect.getmembers(
            BridgeController, predicate=inspect.isfunction
        )
    }
    assert "toggle_flag_current" in methods
    assert "select_next_video" in methods
    assert "select_previous_video" in methods


# --- ARIA audits -----------------------------------------------------
def test_sidebar_search_has_aria_label() -> None:
    html = renderer.render("sidebar.html")
    assert 'aria-label="Filter videos by name or hash"' in html
    assert 'role="search"' in html


def test_metadata_search_has_aria_label() -> None:
    html = renderer.render("metadata.html")
    assert 'aria-label="Filter metadata"' in html


def test_metadata_table_headers_are_aria_sortable() -> None:
    html = renderer.render("metadata.html")
    # Both headers expose aria-sort and are keyboard-focusable.
    assert html.count('aria-sort="none"') == 2
    assert html.count('tabindex="0"') >= 2


def test_notes_toast_is_a_polite_live_region() -> None:
    html = renderer.render("notes.html")
    assert 'role="status"' in html
    assert 'aria-live="polite"' in html


def test_notes_flag_button_has_aria_pressed() -> None:
    html = renderer.render("notes.html")
    assert 'aria-pressed="false"' in html
