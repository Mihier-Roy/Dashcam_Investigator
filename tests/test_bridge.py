"""Unit tests for the QWebChannel Bridge.

These tests do NOT require QtWebEngine — Bridge is a pure QObject. They
construct a fake controller, exercise each slot, and verify the right
controller method was called and that signals carry the expected payloads.
"""

from __future__ import annotations

import json
import sys
from typing import Any

import pytest
from PySide6 import QtWidgets

from dashcam_investigator.gui.web.bridge import Bridge


@pytest.fixture(scope="module")
def qcoreapp() -> QtWidgets.QApplication:
    # A full QApplication (not a bare QCoreApplication) is required here:
    # Qt allows only one QCoreApplication-derived singleton per process, and
    # other test modules in the same pytest run construct real QWidgets,
    # which abort if the process-wide singleton isn't a QApplication.
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    return app


class FakeController:
    """Records every call so assertions can inspect interactions."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[Any, ...]]] = []
        self.project_payload = '{"tool_name": "dci"}'
        self.metadata_payload = '[{"key": "value"}]'

    def request_new_project(self) -> None:
        self.calls.append(("request_new_project", ()))

    def request_open_project(self) -> None:
        self.calls.append(("request_open_project", ()))

    def select_video(self, name: str) -> None:
        self.calls.append(("select_video", (name,)))

    def set_flag(self, name: str, flagged: bool) -> None:
        self.calls.append(("set_flag", (name, flagged)))

    def save_notes(self, name: str, text: str) -> None:
        self.calls.append(("save_notes", (name, text)))

    def generate_report(self) -> None:
        self.calls.append(("generate_report", ()))

    def set_theme(self, name: str) -> None:
        self.calls.append(("set_theme", (name,)))

    def get_project_json(self) -> str:
        self.calls.append(("get_project_json", ()))
        return self.project_payload

    def get_metadata_json(self, name: str) -> str:
        self.calls.append(("get_metadata_json", (name,)))
        return self.metadata_payload


@pytest.fixture
def controller_and_bridge(qcoreapp: QtWidgets.QApplication) -> tuple[FakeController, Bridge]:
    controller = FakeController()
    bridge = Bridge(controller)
    return controller, bridge


def test_request_slots_forward_to_controller(
    controller_and_bridge: tuple[FakeController, Bridge],
) -> None:
    controller, bridge = controller_and_bridge
    bridge.requestNewProject()
    bridge.requestOpenProject()
    bridge.generateReport()
    assert ("request_new_project", ()) in controller.calls
    assert ("request_open_project", ()) in controller.calls
    assert ("generate_report", ()) in controller.calls


def test_parameterized_slots_forward_arguments(
    controller_and_bridge: tuple[FakeController, Bridge],
) -> None:
    controller, bridge = controller_and_bridge
    bridge.selectVideo("clip.mp4")
    bridge.setFlag("clip.mp4", True)
    bridge.saveNotes("clip.mp4", "important")
    bridge.setTheme("dark")
    assert ("select_video", ("clip.mp4",)) in controller.calls
    assert ("set_flag", ("clip.mp4", True)) in controller.calls
    assert ("save_notes", ("clip.mp4", "important")) in controller.calls
    assert ("set_theme", ("dark",)) in controller.calls


def test_getter_slots_return_controller_payload(
    controller_and_bridge: tuple[FakeController, Bridge],
) -> None:
    controller, bridge = controller_and_bridge
    assert bridge.getProjectJson() == controller.project_payload
    assert bridge.getMetadataJson("clip.mp4") == controller.metadata_payload
    assert ("get_metadata_json", ("clip.mp4",)) in controller.calls


def test_emit_project_serializes_dict(
    controller_and_bridge: tuple[FakeController, Bridge],
) -> None:
    _, bridge = controller_and_bridge
    received: list[str] = []
    bridge.project_loaded.connect(received.append)
    bridge.emit_project({"tool_name": "dci", "video_files": []})
    assert len(received) == 1
    assert json.loads(received[0]) == {"tool_name": "dci", "video_files": []}


def test_emit_video_serializes_dict(
    controller_and_bridge: tuple[FakeController, Bridge],
) -> None:
    _, bridge = controller_and_bridge
    received: list[str] = []
    bridge.video_changed.connect(received.append)
    bridge.emit_video({"name": "clip.mp4", "flagged": True})
    assert len(received) == 1
    assert json.loads(received[0]) == {"name": "clip.mp4", "flagged": True}


def test_signal_surface_is_complete(
    controller_and_bridge: tuple[FakeController, Bridge],
) -> None:
    """Lock the public signal contract so JS-side relays don't silently drift."""
    _, bridge = controller_and_bridge
    for name in (
        "project_loaded",
        "video_changed",
        "notes_saved",
        "flag_changed",
        "theme_changed",
        "progress",
        "report_generated",
    ):
        assert hasattr(bridge, name), f"Bridge is missing signal {name!r}"
