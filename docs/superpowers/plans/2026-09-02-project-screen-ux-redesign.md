# Project Screen UX Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the New Project dialog (currently zero-layout Qt Designer output), give the video player real transport controls and an idle state, add tab icons, make the project screen keyboard-navigable with a discoverable shortcuts overlay, and soften forensic-specific UI copy — with zero change to `ProjectManager`/`ProjectInfo`/the JSON schema/app name.

**Architecture:** All native-Qt work lives in `dashcam_investigator/gui/` (`new_project_class.py`, `main_window.py`, `app.py`), no new subsystems. JS keyboard-nav work extends the existing `sidebar.js`/`shortcuts.js` files in place. One new SVG asset. Full spec: `docs/superpowers/specs/2026-09-02-project-screen-ux-design.md`.

**Tech Stack:** PySide6 (QtWidgets, QtGui, QtSvg), Jinja2/vanilla JS (existing WebPanel system, unchanged), pytest.

## Global Constraints

- `ProjectInfo.case_name`/`investigator_name` field names, `dashcam_investigator.json` schema, hash verification, and the app name ("Dashcam Investigator") do NOT change — copy-only genericization.
- `NewProjectDialog.save()` must keep returning `(input_dir: Path | None, output_dir: Path | None, case_name: str, investigator_name: str)` — `MainWindow.start_new_project` unpacks this tuple positionally and must not change.
- No new dependencies. `QtSvg` ships with PySide6 already (used implicitly by folium/Qt icon rendering elsewhere is not required — verify `PySide6.QtSvg` imports cleanly before relying on it in Task 4).
- Every new/changed Python file must pass `direnv exec . uv run python -m pytest <file>` before moving to the next task.

---

### Task 1: Force offscreen Qt platform for tests

**Files:**
- Modify: `tests/conftest.py:1-9`

**Interfaces:**
- Produces: every subsequent test in this plan that constructs a real `QApplication`/`QWidget` can rely on `QT_QPA_PLATFORM=offscreen` already being set.

- [ ] **Step 1: Add the env var before any Qt import can happen**

Read the current top of the file first (`tests/conftest.py:1-9`) to confirm exact current imports, then edit:

```python
"""Pytest configuration and shared fixtures."""

import json
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
```

(Keep every existing import/fixture below unchanged — this only adds the `import os` line and the `setdefault` call, placed before any `dashcam_investigator.gui` import anywhere in the suite could pull in Qt.)

- [ ] **Step 2: Verify existing suite still passes**

Run: `direnv exec . uv run python -m pytest -q`
Expected: same pass count as before this change (236 passed at the point this plan was written), no new failures.

- [ ] **Step 3: Commit**

```bash
git add tests/conftest.py
git commit -m "test: force offscreen Qt platform for headless widget tests"
```

---

### Task 2: Rebuild NewProjectDialog with real layouts

**Files:**
- Delete: `dashcam_investigator/gui/QtNewProjectDialog.py`
- Modify: `dashcam_investigator/gui/new_project_class.py` (full rewrite)
- Test: `tests/test_new_project_dialog.py` (new)

**Interfaces:**
- Produces: `NewProjectDialog(parent=None)` with attributes `input_edit`, `output_edit`, `case_edit`, `investigator_edit` (all `QtWidgets.QLineEdit`), `input_dir_button`, `output_dir_button` (`QtWidgets.QPushButton`), and `.save() -> tuple[Path | None, Path | None, str, str]` — same public shape `app.py:start_new_project` already consumes via `dialog.save()`.

- [ ] **Step 1: Write the failing test**

```python
"""Tests for the New Project dialog."""

from pathlib import Path

from PySide6 import QtWidgets

from dashcam_investigator.gui.new_project_class import NewProjectDialog


def _app() -> QtWidgets.QApplication:
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


class TestNewProjectDialog:
    def test_fields_are_line_edits(self):
        _app()
        dialog = NewProjectDialog()
        for name in ("input_edit", "output_edit", "case_edit", "investigator_edit"):
            widget = getattr(dialog, name)
            assert isinstance(widget, QtWidgets.QLineEdit), f"{name} is {type(widget)}"

    def test_save_returns_expected_tuple(self, tmp_path):
        _app()
        dialog = NewProjectDialog()
        input_dir = tmp_path / "in"
        output_dir = tmp_path / "out"
        dialog.input_edit.setText(str(input_dir))
        dialog.output_edit.setText(str(output_dir))
        dialog.case_edit.setText("My Project")
        dialog.investigator_edit.setText("Alex")

        result = dialog.save()

        assert result == (input_dir, output_dir, "My Project", "Alex")

    def test_save_with_empty_dirs_returns_none(self):
        _app()
        dialog = NewProjectDialog()
        dialog.case_edit.setText("My Project")
        dialog.investigator_edit.setText("Alex")

        input_dir, output_dir, case_name, investigator_name = dialog.save()

        assert input_dir is None
        assert output_dir is None
        assert case_name == "My Project"
        assert investigator_name == "Alex"

    def test_pick_dir_ignores_cancel(self, monkeypatch):
        _app()
        dialog = NewProjectDialog()
        monkeypatch.setattr(
            QtWidgets.QFileDialog, "getExistingDirectory", staticmethod(lambda *a, **k: "")
        )
        dialog.input_edit.setText("unchanged")
        dialog.get_input_dir()
        assert dialog.input_edit.text() == "unchanged"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `direnv exec . uv run python -m pytest tests/test_new_project_dialog.py -v`
Expected: FAIL — `ModuleNotFoundError` or `ImportError` (file doesn't exist yet in the new shape) / `AttributeError` on `input_edit` (still a `QTextEdit`, or module still imports the soon-to-be-deleted `QtNewProjectDialog`).

- [ ] **Step 3: Delete the Designer-generated file**

```bash
rm dashcam_investigator/gui/QtNewProjectDialog.py
```

- [ ] **Step 4: Rewrite new_project_class.py**

```python
from pathlib import Path

from PySide6 import QtCore, QtWidgets


class NewProjectDialog(QtWidgets.QDialog):
    """
    Collects the inputs needed to create a new project: source directory,
    output directory, project title, and author.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.input_dir: Path | None = None
        self.output_dir: Path | None = None
        self.case_name: str = ""
        self.investigator_name: str = ""

        self.setWindowTitle("New Project")
        self.setMinimumWidth(520)

        self.input_edit = QtWidgets.QLineEdit(self)
        self.input_edit.setPlaceholderText(
            "Directory containing your dashcam files"
        )
        self.input_dir_button = QtWidgets.QPushButton("Browse…", self)
        self.input_dir_button.clicked.connect(self.get_input_dir)

        self.output_edit = QtWidgets.QLineEdit(self)
        self.output_edit.setPlaceholderText(
            "Directory where the project will be saved"
        )
        self.output_dir_button = QtWidgets.QPushButton("Browse…", self)
        self.output_dir_button.clicked.connect(self.get_output_dir)

        self.case_edit = QtWidgets.QLineEdit(self)
        self.case_edit.setPlaceholderText("Enter a name for this project")

        self.investigator_edit = QtWidgets.QLineEdit(self)
        self.investigator_edit.setPlaceholderText("Enter your name")

        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        form.addRow("Dashcam directory", self._with_browse(self.input_edit, self.input_dir_button))
        form.addRow("Output directory", self._with_browse(self.output_edit, self.output_dir_button))
        form.addRow("Project title", self.case_edit)
        form.addRow("Author", self.investigator_edit)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, self
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(button_box)

    @staticmethod
    def _with_browse(
        line_edit: QtWidgets.QLineEdit, button: QtWidgets.QPushButton
    ) -> QtWidgets.QWidget:
        """Wrap a line edit + its browse button in one row widget for QFormLayout."""
        row = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(line_edit, 1)
        row_layout.addWidget(button)
        return row

    def get_input_dir(self):
        """
        Sets the input directory path
        """
        self._pick_dir(self.input_edit)

    def get_output_dir(self):
        """
        Sets the output directory path
        """
        self._pick_dir(self.output_edit)

    def _pick_dir(self, line_edit: QtWidgets.QLineEdit) -> None:
        """Prompt for a directory and write it into `line_edit`.

        `getExistingDirectory` returns "" (never None) on cancel, so a
        truthy check is required to make cancelling a no-op.
        """
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Open Directory",
            "",
            QtWidgets.QFileDialog.ShowDirsOnly
            | QtWidgets.QFileDialog.DontResolveSymlinks,
        )
        if directory:
            line_edit.setText(directory)

    def save(self):
        self.case_name = self.case_edit.text()
        self.investigator_name = self.investigator_edit.text()
        if len(self.input_edit.text()) > 0:
            self.input_dir = Path(self.input_edit.text())

        if len(self.output_edit.text()) > 0:
            self.output_dir = Path(self.output_edit.text())
        return self.input_dir, self.output_dir, self.case_name, self.investigator_name
```

Changed from the old dialog: default directory for `getExistingDirectory` is
now `""` (current directory) instead of the old hardcoded `"C:"`, which made
no sense on Linux/macOS and isn't part of any test contract.

- [ ] **Step 5: Run test to verify it passes**

Run: `direnv exec . uv run python -m pytest tests/test_new_project_dialog.py -v`
Expected: PASS (4 tests)

- [ ] **Step 6: Check for other references to the deleted module**

Run: `grep -rn "QtNewProjectDialog\|Ui_Dialog" dashcam_investigator/ tests/`
Expected: no matches. If any appear (e.g. a stray import), remove them.

- [ ] **Step 7: Run the full suite**

Run: `direnv exec . uv run python -m pytest -q`
Expected: PASS, count = previous + 4.

- [ ] **Step 8: Commit**

```bash
git add -A dashcam_investigator/gui/new_project_class.py dashcam_investigator/gui/QtNewProjectDialog.py tests/test_new_project_dialog.py
git commit -m "refactor: rebuild NewProjectDialog with real Qt layouts"
```

---

### Task 3: Copy pass — soften forensic-specific wording

**Files:**
- Modify: `dashcam_investigator/gui/assets/templates/welcome.html`

**Interfaces:** none (template text only; no ids/classes change, so `test_welcome_page.py`'s existing assertions on `id="btn-new"` etc. are unaffected).

- [ ] **Step 1: Confirm no test pins the old copy**

Run: `grep -n "Forensic\|fresh investigation\|naming a case" tests/test_welcome_page.py`
Expected: no matches (already verified during spec research; re-verify before editing in case the file changed).

- [ ] **Step 2: Edit welcome.html**

In `dashcam_investigator/gui/assets/templates/welcome.html`, change:

```html
<p>Forensic analysis of dashcam evidence — GPS tracks, speed profiles, metadata, and exportable reports.</p>
```
to
```html
<p>GPS tracks, speed profiles, metadata, and exportable reports for your dashcam footage.</p>
```

and:
```html
<p class="card-subtitle">Start a fresh investigation</p>
```
to
```html
<p class="card-subtitle">Start a new project</p>
```

and:
```html
Walks you through naming a case, picking input/output directories, and processing dashcam files.
```
to
```html
Walks you through naming your project, picking input/output directories, and processing your files.
```

- [ ] **Step 3: Run the welcome page tests**

Run: `direnv exec . uv run python -m pytest tests/test_welcome_page.py -v`
Expected: PASS (all existing tests, unaffected by copy-only changes).

- [ ] **Step 4: Commit**

```bash
git add dashcam_investigator/gui/assets/templates/welcome.html
git commit -m "copy: soften forensic-specific wording on welcome screen"
```

---

### Task 4: Icon helper + notebook.svg + tab icons

**Files:**
- Create: `dashcam_investigator/gui/assets/static/icons/notebook.svg`
- Modify: `dashcam_investigator/gui/main_window.py`
- Test: `tests/test_main_window.py` (new)

**Interfaces:**
- Consumes: `dashcam_investigator.gui.web.renderer.static_path()` (already exists, returns `Path` to `gui/assets/static/`).
- Produces: `_icon(name: str, color: str) -> QtGui.QIcon` in `main_window.py`, used by Task 5 (player transport buttons) too.

- [ ] **Step 1: Add the new icon asset**

Create `dashcam_investigator/gui/assets/static/icons/notebook.svg` matching the
existing set's conventions (24x24 viewBox, `stroke="currentColor"`,
`stroke-width="1.75"`, no fill) — check `dashcam_investigator/gui/assets/static/icons/file.svg` for the exact attribute pattern before writing this, then author a simple notebook/lined-page glyph:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M4 3h13a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H4z"/><path d="M4 3v18"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="9" y1="12" x2="15" y2="12"/><line x1="9" y1="16" x2="13" y2="16"/></svg>
```

- [ ] **Step 2: Write the failing test**

```python
"""Tests for main_window.py helpers."""

from PySide6 import QtGui, QtWidgets

from dashcam_investigator.gui.main_window import _icon


def _app() -> QtWidgets.QApplication:
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def test_icon_returns_qicon_for_existing_asset():
    _app()
    icon = _icon("map-pin", "#000000")
    assert isinstance(icon, QtGui.QIcon)
    assert not icon.isNull()


def test_icon_returns_empty_icon_for_missing_asset(caplog):
    _app()
    icon = _icon("does-not-exist", "#000000")
    assert isinstance(icon, QtGui.QIcon)
    assert icon.isNull()
```

- [ ] **Step 3: Run test to verify it fails**

Run: `direnv exec . uv run python -m pytest tests/test_main_window.py -v`
Expected: FAIL — `ImportError: cannot import name '_icon'`

- [ ] **Step 4: Implement `_icon()` in main_window.py**

Read `dashcam_investigator/gui/main_window.py:1-40` first to see the exact current imports and constants block, then add near the top (after existing imports):

```python
import logging

from PySide6.QtSvg import QSvgRenderer

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
```

- [ ] **Step 5: Run test to verify it passes**

Run: `direnv exec . uv run python -m pytest tests/test_main_window.py -v`
Expected: PASS (2 tests)

- [ ] **Step 6: Wire icons onto the data tabs**

In `_build_data_tabs` (`dashcam_investigator/gui/main_window.py`), after each
`_add_panel_tab(...)` call, set the icon on the tab you just added. Change:

```python
    window.map_panel = _add_panel_tab(
        tabs,
        bridge,
        "Map",
        "output_panel.html",
        context={...},
    )
```
to also call, right after all four `_add_panel_tab` calls (once `tabs` has
all 4 tabs added, indices 0-3 in creation order Map/Metadata/Speed
Graph/Notes):

```python
    muted_color = "#64748b"  # matches --text-muted in tokens.css (light); QSS
    # theme switching doesn't currently re-tint native icons -- acceptable
    # for this pass, see spec's "explicitly out of scope" on full theming.
    tabs.setTabIcon(0, _icon("map-pin", muted_color))
    tabs.setTabIcon(1, _icon("file", muted_color))
    tabs.setTabIcon(2, _icon("bar-chart", muted_color))
    tabs.setTabIcon(3, _icon("notebook", muted_color))
```

- [ ] **Step 7: Run the full suite**

Run: `direnv exec . uv run python -m pytest -q`
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add dashcam_investigator/gui/assets/static/icons/notebook.svg dashcam_investigator/gui/main_window.py tests/test_main_window.py
git commit -m "feat: add tab icons via new _icon() SVG-to-QIcon helper"
```

---

### Task 5: Player transport controls + idle state

**Files:**
- Modify: `dashcam_investigator/gui/main_window.py` (`_build_player_area`)
- Modify: `dashcam_investigator/gui/app.py` (`_wire_media_player`, `load_video_data`)
- Modify: `tests/test_main_window.py` (extend)

**Interfaces:**
- Consumes: `_icon()` from Task 4.
- Produces: `window.play_pause_button` (`QtWidgets.QPushButton`, checkable), `window.stop_button` (unchanged name), `window.current_duration`/`window.total_duration` now `QtWidgets.QLabel` (were `QLineEdit`), `window.video_title` (unchanged name, now shows filename only), `window.player_idle_overlay` (`QtWidgets.QWidget`), `window.player_stack` (`QtWidgets.QStackedLayout` holding the video widget + idle overlay).
- `app.py:play_video`/`pause_video`/`stop_video` collapse to fewer entry points — see Step 3.

- [ ] **Step 1: Write the failing test**

```python
def test_build_player_area_creates_expected_widgets(qtbot=None):
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
```

Append this to `tests/test_main_window.py`.

- [ ] **Step 2: Run test to verify it fails**

Run: `direnv exec . uv run python -m pytest tests/test_main_window.py -v`
Expected: FAIL — `AttributeError: 'QMainWindow' object has no attribute 'play_pause_button'`

- [ ] **Step 3: Rewrite `_build_player_area`**

Read the current `_build_player_area` (`dashcam_investigator/gui/main_window.py`,
the version shown in the design spec's "Component 2" section) fully before
editing, then replace it with:

```python
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
```

You will need two more icon assets that don't exist yet: `play.svg` and
`square.svg` (stop), plus `pause.svg` for the toggle (added in Step 5). Check
`dashcam_investigator/gui/assets/static/icons/` for the existing naming/style
convention (confirmed in Task 4: 24x24 viewBox, `stroke="currentColor"`,
`stroke-width="1.75"`) and add:

`play.svg`:
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polygon points="6 3 20 12 6 21 6 3"/></svg>
```

`pause.svg`:
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
```

`square.svg`:
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="5" width="14" height="14" rx="1"/></svg>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `direnv exec . uv run python -m pytest tests/test_main_window.py -v`
Expected: PASS (all tests in the file so far)

- [ ] **Step 5: Update app.py to wire the new controls**

Read `dashcam_investigator/gui/app.py`'s current `_wire_media_player`,
`play_video`, `pause_video`, `stop_video`, `change_position`, `change_duration`,
`video_position`, and `load_video_data` in full first (all currently reference
`play_button`/`pause_button` which no longer exist). Replace:

```python
    def _wire_media_player(self) -> None:
        self.mediaPlayer = QMediaPlayer(self)
        self.mediaPlayer.setVideoOutput(self.video_player)
        self.play_button.clicked.connect(self.play_video)
        self.pause_button.clicked.connect(self.pause_video)
        self.stop_button.clicked.connect(self.stop_video)
        self.mediaPlayer.durationChanged.connect(self.change_duration)
        self.mediaPlayer.positionChanged.connect(self.change_position)
        self.horizontal_slider.sliderMoved.connect(self.video_position)
```
with:
```python
    def _wire_media_player(self) -> None:
        self.mediaPlayer = QMediaPlayer(self)
        self.mediaPlayer.setVideoOutput(self.video_player)
        self.play_pause_button.toggled.connect(self._on_play_pause_toggled)
        self.stop_button.clicked.connect(self.stop_video)
        self.mediaPlayer.durationChanged.connect(self.change_duration)
        self.mediaPlayer.positionChanged.connect(self.change_position)
        self.horizontal_slider.sliderMoved.connect(self.video_position)
```

and replace `play_video`/`pause_video`/`stop_video`:
```python
    def play_video(self):
        self.mediaPlayer.play()
        duration = self.mediaPlayer.duration()
        sec, min = convert_to_seconds(int(duration))
        self.total_duration.setText(f"{min}:{sec}")

    def pause_video(self):
        self.mediaPlayer.pause()

    def stop_video(self):
        self.mediaPlayer.stop()
```
with:
```python
    def _on_play_pause_toggled(self, checked: bool) -> None:
        icon_color = "#0f172a"
        if checked:
            self.mediaPlayer.play()
            self.play_pause_button.setIcon(_icon("pause", icon_color))
            self.play_pause_button.setToolTip("Pause (Space)")
        else:
            self.mediaPlayer.pause()
            self.play_pause_button.setIcon(_icon("play", icon_color))
            self.play_pause_button.setToolTip("Play (Space)")

    def stop_video(self):
        self.mediaPlayer.stop()
        self.play_pause_button.setChecked(False)
```

Add the import at the top of `app.py`: `from dashcam_investigator.gui.main_window import _icon, setup_ui` (extend the existing `from .main_window import setup_ui` line — check the exact current import line first).

In `load_video_data`, after the existing body sets `self.current_video`, add
overlay switching (find the block that does `self.mediaPlayer.setSource(...)`
and `self.video_title.setText(...)` and change the title line + add the
stack switch):

```python
        self.mediaPlayer.stop()
        self.play_pause_button.setChecked(False)
        self.player_stack.setCurrentWidget(self.video_player)
        logger.debug(f"New item selected. Loading -> {str(video_path.resolve())}")
        self.mediaPlayer.setSource(QUrl.fromLocalFile(str(video_path.resolve())))
        self.video_title.setText(video_path.name)
        self.video_title.setToolTip(str(video_path.resolve()))
```

(Replaces the old `self.video_title.setText(f"Currently playing : {...}")`
line — filename only now, full path moved to the tooltip per the spec.)

- [ ] **Step 6: Manual smoke test**

Run:
```bash
direnv exec . env QT_QPA_PLATFORM=offscreen uv run python -m dashcam_investigator \
    --project test_project --screenshot /tmp/player_check.png --screenshot-delay 3
```
Read `/tmp/player_check.png` and confirm: idle overlay shows (icon + "No
video loaded" + body text) since no video is auto-selected, play/pause is a
single icon button not three text buttons, time labels have no input-box
border.

- [ ] **Step 7: Run the full suite**

Run: `direnv exec . uv run python -m pytest -q`
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add dashcam_investigator/gui/main_window.py dashcam_investigator/gui/app.py \
    dashcam_investigator/gui/assets/static/icons/play.svg \
    dashcam_investigator/gui/assets/static/icons/pause.svg \
    dashcam_investigator/gui/assets/static/icons/square.svg \
    tests/test_main_window.py
git commit -m "feat: real transport controls and idle state for the video player"
```

---

### Task 6: Sidebar keyboard navigation

**Files:**
- Modify: `dashcam_investigator/gui/assets/static/js/pages/sidebar.js`
- Modify: `tests/test_sidebar.py`

**Interfaces:**
- Consumes: existing `state`, `body`, `render()`, `filterVideos()` already in `sidebar.js`.
- Produces: a `selectByName(api, name)` function used by both the existing click handler and the new arrow-key handler.

- [ ] **Step 1: Read the current click handler**

Read `dashcam_investigator/gui/assets/static/js/pages/sidebar.js` in full
(it was last touched in the earlier cleanup pass — re-read fresh, don't
rely on this plan's memory of line numbers) to find the exact
`window.apiReady.then((api) => { ... body.addEventListener("click", ...) ... })`
block.

- [ ] **Step 2: Write the failing test**

```python
def test_sidebar_js_has_arrow_key_navigation() -> None:
    js = (renderer.static_path() / "js" / "pages" / "sidebar.js").read_text()
    assert "selectByName" in js
    assert "ArrowDown" in js
    assert "ArrowUp" in js
```

Add this to `tests/test_sidebar.py`, matching the file's existing
source-text-assertion convention.

- [ ] **Step 3: Run test to verify it fails**

Run: `direnv exec . uv run python -m pytest tests/test_sidebar.py -v`
Expected: FAIL — `assert 'selectByName' in js` fails.

- [ ] **Step 4: Extract selectByName and add arrow-key handling**

Inside the `window.apiReady.then((api) => { ... })` block, add a helper and
a keydown listener alongside the existing `body.addEventListener("click", ...)`.
Replace the click handler's row-selection branch:

```javascript
    body.addEventListener("click", (e) => {
        const folder = e.target.closest(".tree-folder");
        if (folder) {
            const key = folder.dataset.folder;
            if (state.collapsedFolders.has(key)) state.collapsedFolders.delete(key);
            else state.collapsedFolders.add(key);
            render();
            return;
        }
        const row = e.target.closest(".list-row");
        if (row) {
            const name = row.dataset.name;
            state.selected = name;
            api.selectVideo(name);
            render();
        }
    });
```

with (extracting the last branch's body into a shared function, then calling
it from both the click handler and a new keydown handler):

```javascript
    const selectByName = (name) => {
        state.selected = name;
        api.selectVideo(name);
        render();
    };

    body.addEventListener("click", (e) => {
        const folder = e.target.closest(".tree-folder");
        if (folder) {
            const key = folder.dataset.folder;
            if (state.collapsedFolders.has(key)) state.collapsedFolders.delete(key);
            else state.collapsedFolders.add(key);
            render();
            return;
        }
        const row = e.target.closest(".list-row");
        if (row) selectByName(row.dataset.name);
    });

    body.addEventListener("keydown", (e) => {
        if (e.key !== "ArrowDown" && e.key !== "ArrowUp") return;
        const rows = Array.from(body.querySelectorAll(".list-row"));
        if (rows.length === 0) return;
        e.preventDefault();
        const currentIndex = rows.findIndex((r) => r.dataset.name === state.selected);
        const delta = e.key === "ArrowDown" ? 1 : -1;
        const nextIndex = currentIndex === -1
            ? 0
            : (currentIndex + delta + rows.length) % rows.length;
        const nextRow = rows[nextIndex];
        selectByName(nextRow.dataset.name);
        nextRow.focus();
    });
```

Each `.list-row` element needs `tabindex="0"` for `.focus()` to work and for
it to be reachable via Tab at all — find `videoRowHtml(video)` (the function
building each row's HTML) and add `tabindex="0"` to its root element's
attributes. Read that function first to see its exact current template
string before editing.

- [ ] **Step 5: Run test to verify it passes**

Run: `direnv exec . uv run python -m pytest tests/test_sidebar.py -v`
Expected: PASS.

- [ ] **Step 6: Manual smoke test**

```bash
direnv exec . env QT_QPA_PLATFORM=offscreen uv run python -m dashcam_investigator \
    --project test_project --screenshot /tmp/sidebar_check.png --screenshot-delay 2
```
(Arrow-key behavior itself needs a live interactive session to verify by eye
— a screenshot alone won't show a keypress. Do a manual interactive run,
`uv run python -m dashcam_investigator --project test_project`, Tab into the
sidebar list, press ArrowDown/ArrowUp, confirm the map panel updates and the
highlighted row moves.)

- [ ] **Step 7: Run the full suite**

Run: `direnv exec . uv run python -m pytest -q`
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add dashcam_investigator/gui/assets/static/js/pages/sidebar.js tests/test_sidebar.py
git commit -m "feat: arrow-key navigation for the sidebar video list"
```

---

### Task 7: Player keyboard shortcuts + focus rings

**Files:**
- Modify: `dashcam_investigator/gui/app.py`
- Modify: `dashcam_investigator/gui/assets/qss/light.qss`
- Modify: `dashcam_investigator/gui/assets/qss/dark.qss`

**Interfaces:**
- Consumes: `self.mediaPlayer`, `self.play_pause_button` from Task 5.

- [ ] **Step 1: Add a keyPressEvent override on MainWindow**

Read `MainWindow.__init__` and its existing method list in `app.py` first.
Add a new method:

```python
    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:  # noqa: N802 (Qt API)
        focus_widget = QtWidgets.QApplication.focusWidget()
        typing_widgets = (QtWidgets.QLineEdit, QtWidgets.QTextEdit, QtWidgets.QPlainTextEdit)
        if isinstance(focus_widget, typing_widgets):
            super().keyPressEvent(event)
            return

        if event.key() == QtCore.Qt.Key.Key_Space and self.current_video is not None:
            self.play_pause_button.toggle()
            event.accept()
            return
        if event.key() == QtCore.Qt.Key.Key_Right and self.current_video is not None:
            self.mediaPlayer.setPosition(self.mediaPlayer.position() + 5000)
            event.accept()
            return
        if event.key() == QtCore.Qt.Key.Key_Left and self.current_video is not None:
            self.mediaPlayer.setPosition(max(0, self.mediaPlayer.position() - 5000))
            event.accept()
            return
        super().keyPressEvent(event)
```

Add `from PySide6 import QtGui` to the existing `from PySide6 import
QtCore, QtWidgets` import line if not already present (check first —
`QtGui.QKeyEvent` is only used for the type hint here).

Note: `ArrowLeft`/`ArrowRight` are already bound globally in
`shortcuts.js` to previous/next-video navigation, but those run inside the
WebEngine sidebar panel's JS context, not the native `QMainWindow` — they
don't conflict because Qt key events only reach `MainWindow.keyPressEvent`
when a *native* widget (not a WebPanel) has focus. Confirm this doesn't
double-fire by checking during Step 3's manual test that arrow keys seek the
video only when the video/transport area has focus, and still switch videos
when the sidebar has focus.

- [ ] **Step 2: Give the video widget and transport controls real focus**

They already got `Qt.FocusPolicy.StrongFocus` in Task 5's `_build_player_area`
rewrite. No additional change needed here — verify by reading Task 5's
final `_build_player_area` code before moving on.

- [ ] **Step 3: Manual smoke test**

Run `uv run python -m dashcam_investigator --project test_project`
interactively (this task's behavior needs real keyboard input, not a
screenshot). Load a video, click on the player area to focus it, press
Space (confirm play/pause toggles and the icon swaps), press Right/Left
(confirm the scrubber position jumps ~5s). Then Tab into the sidebar and
press ArrowLeft/ArrowRight, confirm that still switches videos (Task 6/
pre-existing `shortcuts.js` behavior), not seeking.

- [ ] **Step 4: Add focus rings to both QSS files**

Read `dashcam_investigator/gui/assets/qss/light.qss` in full, find the
"Buttons" section, add after the existing `QPushButton:default:hover` rule:

```qss
QPushButton:focus, QTabBar::tab:focus {
    outline: 2px solid #2563eb;
    outline-offset: 1px;
}
QSlider::handle:horizontal:focus {
    border-color: #1d4fd0;
    outline: 2px solid #2563eb;
    outline-offset: 2px;
}
```

Read `dashcam_investigator/gui/assets/qss/dark.qss` in full, same location,
add the dark-theme equivalent using that file's accent color (`#60a5fa`):

```qss
QPushButton:focus, QTabBar::tab:focus {
    outline: 2px solid #60a5fa;
    outline-offset: 1px;
}
QSlider::handle:horizontal:focus {
    border-color: #7eb6fb;
    outline: 2px solid #60a5fa;
    outline-offset: 2px;
}
```

- [ ] **Step 5: Verify QSS still loads without a Qt parse warning**

Run:
```bash
direnv exec . env QT_QPA_PLATFORM=offscreen uv run python -m dashcam_investigator \
    --screenshot /tmp/focus_check.png --screenshot-delay 1 2>&1 | grep -i "qss\|stylesheet\|warning"
```
Expected: no QSS-parsing warnings in output (Qt logs to stderr if a QSS
selector/property is invalid).

- [ ] **Step 6: Run the full suite**

Run: `direnv exec . uv run python -m pytest -q`
Expected: PASS (no Python tests target QSS content; this task is manually
verified per Steps 3 and 5).

- [ ] **Step 7: Commit**

```bash
git add dashcam_investigator/gui/app.py dashcam_investigator/gui/assets/qss/light.qss dashcam_investigator/gui/assets/qss/dark.qss
git commit -m "feat: keyboard-operable video transport and visible focus rings"
```

---

### Task 8: Discoverable shortcuts overlay

**Files:**
- Modify: `dashcam_investigator/gui/web/bridge.py`
- Modify: `dashcam_investigator/gui/app.py`
- Modify: `dashcam_investigator/gui/assets/static/js/shortcuts.js`
- Modify: `tests/test_bridge.py`

**Interfaces:**
- Produces: `Bridge.requestShortcutsHelp()` slot (JS→Python), `BridgeController.request_shortcuts_help()` protocol method, `MainWindow.request_shortcuts_help()` implementation.

- [ ] **Step 1: Read the current Bridge/BridgeController surface**

Read `dashcam_investigator/gui/web/bridge.py` in full to see the exact
pattern other no-argument slots follow (e.g. `requestSaveNotes`).

- [ ] **Step 2: Write the failing test**

```python
def test_bridge_exposes_request_shortcuts_help_slot():
    from dashcam_investigator.gui.web.bridge import Bridge, BridgeController

    assert hasattr(Bridge, "requestShortcutsHelp")
    assert "request_shortcuts_help" in {
        name for name, _ in inspect.getmembers(BridgeController, predicate=inspect.isfunction)
    }
```

Add this to `tests/test_bridge.py` (add `import inspect` at the top if not
already present — check first).

- [ ] **Step 3: Run test to verify it fails**

Run: `direnv exec . uv run python -m pytest tests/test_bridge.py -v`
Expected: FAIL — `AttributeError`/assertion failure, slot doesn't exist yet.

- [ ] **Step 4: Add the slot to Bridge and the Protocol**

In `BridgeController` Protocol, add alongside the other keyboard-shortcut
entry points (`toggle_flag_current`, `select_next_video`,
`select_previous_video`):
```python
    def request_shortcuts_help(self) -> None: ...
```

In the `Bridge` class, alongside `requestSaveNotes`:
```python
    @Slot()
    def requestShortcutsHelp(self) -> None:  # noqa: N802
        logger.debug("bridge: requestShortcutsHelp")
        self._controller.request_shortcuts_help()
```

- [ ] **Step 5: Run test to verify it passes**

Run: `direnv exec . uv run python -m pytest tests/test_bridge.py -v`
Expected: PASS.

- [ ] **Step 6: Implement in MainWindow**

Add to `app.py`, alongside `toggle_flag_current`/`select_next_video`:

```python
    def request_shortcuts_help(self) -> None:
        QtWidgets.QMessageBox.information(
            self,
            "Keyboard shortcuts",
            "/          Focus the sidebar filter\n"
            "F          Flag / un-flag the current video\n"
            "← / →      Previous / next video (sidebar focused)\n"
            "Space      Play / pause (player focused)\n"
            "← / →      Seek ±5s (player focused)\n"
            "Ctrl+S     Save notes\n"
            "?          Show this help",
        )
```

This also satisfies `test_main_window_implements_bridge_controller_surface`
in `test_welcome_page.py` — no separate change needed there, it discovers
methods via `dir(MainWindow)` automatically.

- [ ] **Step 7: Wire the `?` key in shortcuts.js**

Read `dashcam_investigator/gui/assets/static/js/shortcuts.js` in full, add a
case to the existing `switch (event.key)` block:

```javascript
        case "?":
            event.preventDefault();
            call("requestShortcutsHelp");
            break;
```

Update the file's header comment block (the `//   /  focus...` list) to
include the new `?` entry, matching the existing comment style.

- [ ] **Step 8: Run the full suite**

Run: `direnv exec . uv run python -m pytest -q`
Expected: PASS.

- [ ] **Step 9: Manual smoke test**

Interactive run: `uv run python -m dashcam_investigator --project test_project`,
press `?` outside any text field, confirm the message box appears listing
every shortcut and is dismissable with `Esc` or click.

- [ ] **Step 10: Commit**

```bash
git add dashcam_investigator/gui/web/bridge.py dashcam_investigator/gui/app.py \
    dashcam_investigator/gui/assets/static/js/shortcuts.js tests/test_bridge.py
git commit -m "feat: discoverable keyboard shortcuts overlay (? key)"
```

---

## Final Verification

- [ ] Run: `direnv exec . uv run python -m pytest -q`
  Expected: all tests pass, coverage ≥ 60% gate.
- [ ] Run the full interactive app once (`uv run python -m dashcam_investigator
  --project test_project`) and walk through: open New Project dialog (resizes
  cleanly, Tab order flows top-to-bottom), select a video (player controls
  update, idle overlay disappears), Space/arrow-key seek, Tab to sidebar,
  arrow-key row navigation, press `?` for the shortcuts overlay.
- [ ] Update `AGENTS.md`'s `new_project_class.py` / `main_window.py`
  descriptions if their responsibilities changed enough to make the existing
  doc misleading (read the current entries first — likely only
  `new_project_class.py`'s "stays native Qt" bullet needs a note that it's
  now hand-coded layouts, not Designer-generated).
