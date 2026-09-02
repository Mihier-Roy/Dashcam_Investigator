"""
Phase 7: tests for the hand-written MainWindow layout.

The actual layout construction needs QtWebEngine + a display — both
unavailable on this headless host. Source-text checks always run; the
import-based checks skip cleanly when PySide6.QtWidgets can't load
(libEGL missing on bare CI hosts).
"""

from __future__ import annotations

import importlib
from importlib import resources
from pathlib import Path

import pytest
from PySide6 import QtGui, QtWidgets

from dashcam_investigator.gui.main_window import _icon


def _read(rel_path: str) -> str:
    return resources.files("dashcam_investigator").joinpath(rel_path).read_text()


def _qt_widgets_or_skip():
    try:
        return importlib.import_module("PySide6.QtWidgets")
    except ImportError as exc:
        pytest.skip(f"PySide6.QtWidgets not loadable on this host: {exc}")


def _app() -> QtWidgets.QApplication:
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


# --- Source-text regression nets (run everywhere) ---------------------
def test_qtmainwindow_source_file_is_gone() -> None:
    pkg_root = Path(str(resources.files("dashcam_investigator")))
    assert not (pkg_root / "gui" / "QtMainWindow.py").exists()


def test_qt_models_source_file_is_gone() -> None:
    pkg_root = Path(str(resources.files("dashcam_investigator")))
    assert not (pkg_root / "gui" / "qt_models.py").exists()


def test_app_py_no_longer_imports_deleted_modules() -> None:
    src = _read("gui/app.py")
    for needle in (
        "QtMainWindow",
        "qt_models",
        "Ui_MainWindow",
        "VideoListModel",
        "PandasTableModel",
        "NavigationListModel",
        "setGeometry",
    ):
        assert needle not in src, f"app.py still references {needle!r}"


def test_main_window_module_no_set_geometry_calls() -> None:
    """The whole point of Phase 7: real layouts, no pixel-coordinate widgets."""
    assert "setGeometry" not in _read("gui/main_window.py")


def test_main_window_uses_splitters_for_layout() -> None:
    src = _read("gui/main_window.py")
    assert "QSplitter" in src
    assert "QVBoxLayout" in src
    assert "QHBoxLayout" in src


def test_app_py_persists_settings_via_qsettings() -> None:
    src = _read("gui/app.py")
    assert "QSettings" in src
    assert "saveGeometry" in src
    assert "restoreGeometry" in src
    assert "saveState" in src
    assert "restoreState" in src


def test_app_py_sets_qt_application_metadata() -> None:
    src = _read("gui/app.py")
    assert "setOrganizationName" in src
    assert "setApplicationName" in src


# --- Import-based checks (skipped without QtWidgets) ------------------
def test_setup_ui_signature() -> None:
    _qt_widgets_or_skip()
    import inspect

    main_window = importlib.import_module("dashcam_investigator.gui.main_window")
    sig = inspect.signature(main_window.setup_ui)
    params = list(sig.parameters.values())
    assert len(params) == 2, "setup_ui should take exactly (window, bridge)"
    assert params[0].name == "window"
    assert params[1].name == "bridge"


def test_size_constants_are_sane() -> None:
    _qt_widgets_or_skip()
    main_window = importlib.import_module("dashcam_investigator.gui.main_window")
    assert main_window.MIN_WINDOW_SIZE.width() >= 1000
    assert main_window.MIN_WINDOW_SIZE.height() >= 600
    assert (
        main_window.DEFAULT_WINDOW_SIZE.width() >= main_window.MIN_WINDOW_SIZE.width()
    )
    assert (
        main_window.DEFAULT_WINDOW_SIZE.height() >= main_window.MIN_WINDOW_SIZE.height()
    )
    assert main_window.SIDEBAR_MIN_WIDTH < main_window.SIDEBAR_DEFAULT_WIDTH


# --- _icon() SVG-to-QIcon helper ---------------------------------------
def test_icon_returns_qicon_for_existing_asset():
    _app()
    icon = _icon("map-pin", "#000000")
    assert isinstance(icon, QtGui.QIcon)
    assert not icon.isNull()


def test_icon_returns_empty_icon_for_missing_asset(caplog):
    _app()
    with caplog.at_level("WARNING"):
        icon = _icon("does-not-exist", "#000000")
    assert isinstance(icon, QtGui.QIcon)
    assert icon.isNull()
    assert "does-not-exist" in caplog.text


def test_build_player_area_creates_expected_widgets():
    from PySide6 import QtWidgets
    from dashcam_investigator.gui.main_window import _build_player_area

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    parent = QtWidgets.QSplitter()
    _build_player_area(window, parent)

    assert isinstance(window.play_pause_button, QtWidgets.QPushButton)
    assert window.play_pause_button.isCheckable()
    assert isinstance(window.stop_button, QtWidgets.QPushButton)
    assert isinstance(window.current_duration, QtWidgets.QLabel)
    assert not isinstance(window.current_duration, QtWidgets.QLineEdit)
    assert isinstance(window.total_duration, QtWidgets.QLabel)
    assert isinstance(window.player_idle_overlay, QtWidgets.QWidget)
    assert isinstance(window.player_stack, QtWidgets.QStackedLayout)
