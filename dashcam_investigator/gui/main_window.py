"""
Hand-written MainWindow layout. Replaces the Qt Designer–generated
QtMainWindow.py — no fixed pixel-coordinate widgets anywhere.

setup_ui(window, bridge) attaches every widget the controller in app.py
expects (self.stack_widget, self.video_player, self.play_pause_button, …)
so the rest of the code didn't need to change shape.

Layout:

    QMainWindow
    ├── menu bar (File: New / Open / Generate report / Exit)
    └── QStackedWidget
        ├── [0] welcome WebPanel
        └── [1] project page
            └── QSplitter (horizontal, persisted)
                ├── sidebar WebPanel
                └── right column
                    └── QSplitter (vertical, persisted)
                        ├── player area: video + title + controls
                        └── data tabs: Map / Metadata / Speed Graph / Notes
"""

from __future__ import annotations

import logging

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtSvg import QSvgRenderer

from .web.bridge import Bridge
from .web.panel import WebPanel
from .web.renderer import static_path

logger = logging.getLogger(__name__)

_ICON_SIZE = 18


def _icon(name: str, color: str) -> QtGui.QIcon:
    """Render an SVG from gui/assets/static/icons/ to a QIcon tinted `color`.

    The on-disk SVGs use stroke="currentColor"; QSvgRenderer doesn't resolve
    CSS currentColor, so we recolor by substituting the literal string before
    rendering. Missing/unreadable assets log a warning and return a null
    QIcon rather than raising -- these are ship-time assets, a missing file
    is a packaging bug, not something to crash the UI over.
    """
    path = static_path() / "icons" / f"{name}.svg"
    try:
        svg_text = path.read_text().replace("currentColor", color)
    except OSError as exc:
        logger.warning("Failed to load icon %r: %s", name, exc)
        return QtGui.QIcon()

    renderer = QSvgRenderer(svg_text.encode("utf-8"))
    pixmap = QtGui.QPixmap(_ICON_SIZE, _ICON_SIZE)
    pixmap.fill(QtCore.Qt.GlobalColor.transparent)
    painter = QtGui.QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QtGui.QIcon(pixmap)


# Sane minimums — picked so the player + sidebar are still usable.
MIN_WINDOW_SIZE = QtCore.QSize(1100, 700)
DEFAULT_WINDOW_SIZE = QtCore.QSize(1600, 1000)
SIDEBAR_DEFAULT_WIDTH = 320
SIDEBAR_MIN_WIDTH = 240
PLAYER_MIN_HEIGHT = 240
TABS_MIN_HEIGHT = 220


def setup_ui(window: QtWidgets.QMainWindow, bridge: Bridge) -> None:
    """Build the entire MainWindow UI in code and attach widgets to `window`."""
    window.setWindowTitle("Dashcam Investigator")
    window.setMinimumSize(MIN_WINDOW_SIZE)
    window.resize(DEFAULT_WINDOW_SIZE)

    _build_menu_bar(window)

    window.stack_widget = QtWidgets.QStackedWidget()
    window.setCentralWidget(window.stack_widget)

    window.welcome_panel = WebPanel("welcome.html", bridge, parent=window.stack_widget)
    window.stack_widget.addWidget(window.welcome_panel)

    project_page = QtWidgets.QWidget()
    window.stack_widget.addWidget(project_page)
    _build_project_page(window, project_page, bridge)

    window.stack_widget.setCurrentIndex(0)


def _build_menu_bar(window: QtWidgets.QMainWindow) -> None:
    menu_bar = window.menuBar()
    file_menu = menu_bar.addMenu("&File")

    window.action_new_project = QtGui.QAction("&New project…", window)
    window.action_new_project.setShortcut(QtGui.QKeySequence.StandardKey.New)
    file_menu.addAction(window.action_new_project)

    window.action_open_project = QtGui.QAction("&Open project…", window)
    window.action_open_project.setShortcut(QtGui.QKeySequence.StandardKey.Open)
    file_menu.addAction(window.action_open_project)

    file_menu.addSeparator()

    # Name kept so the existing controller wiring keeps working.
    window.actionGenerate_Report = QtGui.QAction("&Generate report", window)
    file_menu.addAction(window.actionGenerate_Report)

    file_menu.addSeparator()

    action_exit = QtGui.QAction("E&xit", window)
    action_exit.setShortcut(QtGui.QKeySequence.StandardKey.Quit)
    action_exit.triggered.connect(window.close)
    file_menu.addAction(action_exit)


def _build_project_page(
    window: QtWidgets.QMainWindow,
    page: QtWidgets.QWidget,
    bridge: Bridge,
) -> None:
    page_layout = QtWidgets.QHBoxLayout(page)
    page_layout.setContentsMargins(0, 0, 0, 0)
    page_layout.setSpacing(0)

    h_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, page)
    h_splitter.setChildrenCollapsible(False)
    h_splitter.setHandleWidth(1)
    page_layout.addWidget(h_splitter)
    window.h_splitter = h_splitter

    window.sidebar_panel = WebPanel("sidebar.html", bridge, parent=h_splitter)
    window.sidebar_panel.setMinimumWidth(SIDEBAR_MIN_WIDTH)
    h_splitter.addWidget(window.sidebar_panel)

    right = QtWidgets.QWidget(h_splitter)
    right_layout = QtWidgets.QVBoxLayout(right)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.setSpacing(0)
    h_splitter.addWidget(right)

    h_splitter.setSizes([SIDEBAR_DEFAULT_WIDTH, 1280])
    h_splitter.setStretchFactor(0, 0)
    h_splitter.setStretchFactor(1, 1)

    v_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical, right)
    v_splitter.setChildrenCollapsible(False)
    v_splitter.setHandleWidth(1)
    right_layout.addWidget(v_splitter)
    window.v_splitter = v_splitter

    _build_player_area(window, v_splitter)
    _build_data_tabs(window, v_splitter, bridge)

    v_splitter.setSizes([520, 460])
    v_splitter.setStretchFactor(0, 1)
    v_splitter.setStretchFactor(1, 1)


def _build_player_area(
    window: QtWidgets.QMainWindow, parent: QtWidgets.QWidget
) -> None:
    area = QtWidgets.QWidget(parent)
    layout = QtWidgets.QVBoxLayout(area)
    layout.setContentsMargins(8, 8, 8, 4)
    layout.setSpacing(6)

    video_container = QtWidgets.QWidget(area)
    video_container.setMinimumHeight(PLAYER_MIN_HEIGHT)
    window.player_stack = QtWidgets.QStackedLayout(video_container)
    window.player_stack.setContentsMargins(0, 0, 0, 0)

    window.video_player = QVideoWidget(video_container)
    window.video_player.setStyleSheet("background-color: #000;")
    window.video_player.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
    window.player_stack.addWidget(window.video_player)

    window.player_idle_overlay = _build_player_idle_overlay(video_container)
    window.player_stack.addWidget(window.player_idle_overlay)
    window.player_stack.setCurrentWidget(window.player_idle_overlay)

    layout.addWidget(video_container, 1)

    window.video_title = QtWidgets.QLabel("No video loaded", area)
    window.video_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(window.video_title)

    controls = QtWidgets.QWidget(area)
    controls_layout = QtWidgets.QHBoxLayout(controls)
    controls_layout.setContentsMargins(0, 0, 0, 0)
    controls_layout.setSpacing(8)

    window.current_duration = QtWidgets.QLabel("0:00", controls)
    window.current_duration.setMinimumWidth(40)
    window.current_duration.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    controls_layout.addWidget(window.current_duration)

    window.horizontal_slider = QtWidgets.QSlider(
        QtCore.Qt.Orientation.Horizontal, controls
    )
    window.horizontal_slider.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
    controls_layout.addWidget(window.horizontal_slider, 1)

    window.total_duration = QtWidgets.QLabel("0:00", controls)
    window.total_duration.setMinimumWidth(40)
    window.total_duration.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    controls_layout.addWidget(window.total_duration)

    text_color = "#0f172a"  # matches tokens.css --text (light); native icons
    # don't re-tint on theme change, same limitation noted in Task 4.
    window.play_pause_button = QtWidgets.QPushButton(controls)
    window.play_pause_button.setCheckable(True)
    window.play_pause_button.setIcon(_icon("play", text_color))
    window.play_pause_button.setToolTip("Play (Space)")
    window.play_pause_button.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
    controls_layout.addWidget(window.play_pause_button)

    window.stop_button = QtWidgets.QPushButton(controls)
    window.stop_button.setIcon(_icon("square", text_color))
    window.stop_button.setToolTip("Stop")
    window.stop_button.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
    controls_layout.addWidget(window.stop_button)

    layout.addWidget(controls)

    parent.addWidget(area)


def _build_player_idle_overlay(parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
    """Empty-state shown over the video widget when no video is selected,
    matching the visual pattern of the WebPanel `.empty` component."""
    overlay = QtWidgets.QWidget(parent)
    overlay.setStyleSheet("background-color: #000;")
    layout = QtWidgets.QVBoxLayout(overlay)
    layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    layout.setSpacing(8)

    icon_label = QtWidgets.QLabel(overlay)
    icon_label.setPixmap(_icon("video", "#64748b").pixmap(48, 48))
    icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(icon_label)

    title = QtWidgets.QLabel("No video loaded", overlay)
    title.setStyleSheet("color: #e6e8eb; font-weight: 600; font-size: 14px;")
    title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)

    body = QtWidgets.QLabel("Select a video from the sidebar to play it", overlay)
    body.setStyleSheet("color: #64748b; font-size: 12.5px;")
    body.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(body)

    return overlay


def _build_data_tabs(
    window: QtWidgets.QMainWindow,
    parent: QtWidgets.QWidget,
    bridge: Bridge,
) -> None:
    tabs = QtWidgets.QTabWidget(parent)
    tabs.setMinimumHeight(TABS_MIN_HEIGHT)
    parent.addWidget(tabs)
    window.data_tabs = tabs

    window.map_panel = _add_panel_tab(
        tabs,
        bridge,
        "Map",
        "output_panel.html",
        context={
            "subtitle": "GPS track",
            "empty_icon": "map-pin",
            "empty_title": "No map loaded",
            "empty_body": "Select a video from the sidebar to view its GPS track.",
        },
    )
    window.metadata_panel = _add_panel_tab(
        tabs,
        bridge,
        "Metadata",
        "metadata.html",
    )
    window.graph_panel = _add_panel_tab(
        tabs,
        bridge,
        "Speed Graph",
        "output_panel.html",
        context={
            "subtitle": "Speed profile",
            "empty_icon": "bar-chart",
            "empty_title": "No speed profile",
            "empty_body": "Select a video from the sidebar to view its speed profile.",
        },
    )
    window.notes_panel = _add_panel_tab(
        tabs,
        bridge,
        "Notes",
        "notes.html",
    )

    muted_color = "#64748b"  # matches --text-muted in tokens.css (light); QSS
    # theme switching doesn't currently re-tint native icons -- acceptable
    # for this pass, see spec's "explicitly out of scope" on full theming.
    tabs.setTabIcon(0, _icon("map-pin", muted_color))
    tabs.setTabIcon(1, _icon("file", muted_color))
    tabs.setTabIcon(2, _icon("bar-chart", muted_color))
    tabs.setTabIcon(3, _icon("notebook", muted_color))


def _add_panel_tab(
    tab_widget: QtWidgets.QTabWidget,
    bridge: Bridge,
    label: str,
    template: str,
    context: dict | None = None,
) -> WebPanel:
    container = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    panel = WebPanel(template, bridge, parent=container, context=context)
    layout.addWidget(panel)
    tab_widget.addTab(container, label)
    return panel
