# Project Screen UX Redesign — Design Spec

Sub-project **A+E** of the larger "make the app good end to end" initiative. The
other sub-projects (project storage/discoverability, offline-verifiable
outputs, timeline markers/POI) are separate specs, out of scope here. "Native
codec" concern (F) required no work — PySide6's `QtMultimedia` already bundles
FFmpeg as its default backend on every platform, confirmed via our own runtime
logs (`Using Qt multimedia with FFmpeg version 7.1.2`).

## Problem

The project screen (the main working view — sidebar, video player, data tabs)
looks unpolished next to the welcome screen, in three concrete ways: raw
Qt Designer dialogs with no layouts, native media-player controls that don't
match a real player, and keyboard navigation that exists in places (arrow-key
video switching, `/` to search) but isn't discoverable or complete. Separately,
some UI copy leans harder into "forensic investigation" framing than the app
needs to.

## Root cause: the New Project dialog

`dashcam_investigator/gui/QtNewProjectDialog.py` is Qt Designer output with
**zero layouts** — every widget is placed with `setGeometry(QRect(x, y, w, h))`
in absolute pixels. No `dialog.ui` source exists in the repo to regenerate
from. This means: the dialog can't resize, ignores DPI scaling, and looks
nothing like the rest of the app (which is either hand-coded Qt layouts —
`main_window.py` — or the web-based design system in `gui/assets/`). This is
the single biggest "amateurish" offender, bigger than anything on the visible
project screen itself, and blocks a clean copy-genericization pass (labels are
baked into Designer geometry, awkward to touch surgically).

## Architecture

No new subsystems. Three existing files change shape, one is replaced:

- `dashcam_investigator/gui/QtNewProjectDialog.py` — **deleted**. Its only
  purpose was `Ui_Dialog`, consumed solely by `new_project_class.py`.
- `dashcam_investigator/gui/new_project_class.py` — `NewProjectDialog` stops
  inheriting `Ui_Dialog`; builds its own `QFormLayout` in `__init__`, same
  attribute names (`input_edit`, `output_edit`, `case_edit`,
  `investigator_edit`, buttons) so button wiring (`_pick_dir` calls) and
  `save()`'s public 4-tuple contract don't change — only `save()`'s internal
  `.toPlainText()` calls become `.text()` to match the new `QLineEdit` type.
- `dashcam_investigator/gui/main_window.py` — `_build_player_area` rewritten:
  icon transport buttons, borderless time labels, filename-only title,
  `.empty`-style idle state (an overlay `QWidget` shown/hidden over the
  `QVideoWidget`, not a template — this is native Qt, not a WebPanel).
  `_build_data_tabs` gains icons via `tab_widget.setTabIcon` using the app's
  existing SVG set (rendered to `QIcon` via `QSvgRenderer` → `QPixmap`, a
  small new helper — see below).
- `dashcam_investigator/gui/assets/static/js/pages/sidebar.js` — arrow-key row
  navigation added to the existing click handler.
- `dashcam_investigator/gui/assets/static/js/shortcuts.js` — `?` opens a
  shortcuts overlay; the overlay itself is a new tiny template
  (`shortcuts_overlay.html`) reusing existing `.card`/`.badge` components, or
  (simpler, chosen) a native `QMessageBox` triggered by a new bridge signal —
  **decision: native `QMessageBox`**, since it needs no new WebPanel, no new
  scheme routing, and is trivially keyboard-dismissable (`Esc`) for free.
- `dashcam_investigator/gui/assets/qss/light.qss` /`dark.qss` — add explicit
  `:focus` rules for `QPushButton`, `QTabBar::tab`, `QSlider::handle` (the
  current stylesheet resets some default focus indication without replacing
  it).
- `dashcam_investigator/gui/assets/templates/welcome.html` — copy changes
  only, no structural change.

## Components

### 1. `NewProjectDialog` (rebuilt)

```
QFormLayout
  "Input directory"  [QLineEdit (readonly, shows picked path)] [Browse…]
  "Output directory" [QLineEdit (readonly)]                    [Browse…]
  "Project title"    [QLineEdit]
  "Author"           [QLineEdit]
  ─────────────
  [Cancel] [Create]
```

Switches `input_edit`/`output_edit`/`case_edit`/`investigator_edit` from
`QTextEdit` (the Designer file's odd choice for single-line fields) to
`QLineEdit` — single-line semantics match single-line data, and `QLineEdit`
gets standard `returnPressed`/tab-order behavior QTextEdit doesn't.
`_pick_dir` (added last cleanup pass) keeps working unchanged since it only
calls `.setText()`, which `QLineEdit` also has. `save()`'s `.toPlainText()`
calls become `.text()`.

Field order in the tab chain is the layout order above — free, since
`QFormLayout` sets it automatically (no manual `setTabOrder` needed here).

### 2. Player area transport controls

Native Qt, no template. Uses the app's existing SVG icon set (already used via
`inline_svg()` in web templates) rendered to `QIcon`:

```python
def _icon(name: str, color: str) -> QtGui.QIcon:
    """Render an SVG from gui/assets/static/icons/ to a QIcon, tinted `color`
    (the QSS-driven text color, since SVGs on disk use `currentColor`)."""
    svg_bytes = (static_path() / "icons" / f"{name}.svg").read_bytes()
    ...
```

Play/pause is a single `QPushButton` (checkable) that swaps its icon between
`play`/`pause` on `QMediaPlayer.playbackStateChanged`; Stop stays separate.
Time labels become plain `QLabel` (not `QLineEdit` — they were never
user-editable, so a bordered input was always the wrong widget). Title label
shows `Path(video_path).name`; the resolved absolute path moves to
`setToolTip()`.

Idle state: a `QLabel`-based overlay widget (icon + "No video loaded" +
"Select a video from the sidebar to play it") stacked on top of the
`QVideoWidget` via a `QStackedLayout`, shown when `current_video is None` and
hidden on `select_video`. Styling reuses the `.empty` component's *values*
(same icon, same copy pattern) translated to QSS, since this is native Qt,
not a WebPanel — no code sharing with `components.css` is possible, but the
visual result must look consistent by eye.

### 3. Data-tab icons

`tabs.setTabIcon(index, _icon(name, muted_color))` for each of the four tabs.
Existing set (`gui/assets/static/icons/`) covers Map (`map-pin`) and Speed
Graph (`bar-chart`) directly; Metadata reuses `file`. Notes has no existing
match — add one new `notebook.svg` in the same Lucide-style/stroke
conventions as the rest of the set (a single new asset, not a new system).

### 4. Keyboard navigation

- **Sidebar list** (`sidebar.js`): `body` (the row container) gets a
  `keydown` listener for `ArrowUp`/`ArrowDown` that moves `state.selected` to
  the previous/next visible row and calls `api.selectVideo(name)` — mirrors
  the existing click handler's logic, extracted into one `selectByName(name)`
  function both call.
- **Player** (`main_window.py`/`app.py`): `QVideoWidget` and the transport
  buttons get `Qt.FocusPolicy.StrongFocus`; a `keyPressEvent` override (or an
  installed event filter, whichever is less code once written) maps `Space`
  → toggle play/pause, `ArrowLeft`/`ArrowRight` → seek ±5000 ms via
  `mediaPlayer.setPosition`.
- **Focus rings**: add to both QSS files:
  ```qss
  QPushButton:focus, QSlider:focus, QTabBar::tab:focus {
      outline: 2px solid #2563eb; /* var(--accent) light; dark file uses #60a5fa */
      outline-offset: 1px;
  }
  ```
- **Shortcuts overlay**: `shortcuts.js` adds a `?` case to its `switch` that
  calls a new bridge slot `requestShortcutsHelp()`; `MainWindow` handles it
  with `QMessageBox.information(self, "Keyboard shortcuts", <text listing
  every shortcut>)`. One new `Signal`-less slot, no new WebPanel.

### 5. Copy changes

| Location | Before | After |
|---|---|---|
| `welcome.html` hero | "Forensic analysis of dashcam evidence — GPS tracks, speed profiles, metadata, and exportable reports." | "GPS tracks, speed profiles, metadata, and exportable reports for your dashcam footage." |
| `welcome.html` new-project card subtitle | "Start a fresh investigation" | "Start a new project" |
| `welcome.html` new-project card body | "Walks you through naming a case, picking input/output directories, and processing dashcam files." | "Walks you through naming a project, picking input/output directories, and processing your files." |
| New Project dialog | "Case name" / "Investigator" | "Project title" / "Author" |

`ProjectInfo.case_name`/`investigator_name` field names, `dashcam_investigator.json`
schema, hash verification, app name ("Dashcam Investigator") — unchanged (per
copy-only scope).

## Data flow

No new data flows. `NewProjectDialog.save()` still returns the same 4-tuple
`(input_dir, output_dir, case_name, investigator_name)` `start_new_project`
already consumes — the dialog's internal widget/label rename is invisible to
`ProjectManager`. Keyboard-driven seek/play calls the same
`mediaPlayer`/`horizontal_slider` APIs the mouse-driven buttons already do.

## Error handling

- `_icon()` on a missing/unreadable SVG: log a warning, return
  `QIcon()` (Qt renders an empty icon gracefully, no crash) — matches the
  existing `inline_svg()` behavior of raising only on genuinely missing files
  the app ships itself (these are ship-time assets, not user input, so a
  missing file is a packaging bug, not a runtime condition to design around
  beyond "don't crash").
- Keyboard seek clamps to `[0, duration]` via `QMediaPlayer.setPosition`'s own
  clamping (already the platform behavior) — no new bounds-checking code
  needed.

## Testing

Both existing GUI test files state their tests avoid real widget/JS
execution (`test_welcome_page.py`: "MainWindow can't be instantiated on this
headless host"; `test_sidebar.py`: "the JS itself runs only inside
QtWebEngine, which isn't loadable on this headless host"). Both claims are
now stale — this session proved repeatedly that `MainWindow` and QtWebEngine
both load headlessly via `QT_QPA_PLATFORM=offscreen` in this repo's nix
devshell. Plain `pytest` runs don't set that variable, so real widget tests
need it set explicitly, not by accident:

- Add to `tests/conftest.py`: set `os.environ.setdefault("QT_QPA_PLATFORM",
  "offscreen")` at module load, before any Qt import anywhere in the suite.
- `tests/test_new_project_dialog.py` (new): construct a real
  `QApplication` + `NewProjectDialog`, assert `input_edit`/`output_edit`/
  `case_edit`/`investigator_edit` are `QLineEdit` (not `QTextEdit`), drive
  `save()` with `.setText(...)` on each field, assert the returned 4-tuple.
  This is strictly better than the existing repo convention (real behavior,
  not template-text greps) now that we know it's possible — use it for this
  new file; do not retrofit the existing weak-assertion tests as part of
  this change (out of scope, separate cleanup).
- `tests/test_sidebar.py` (extend): JS still has no execution harness in
  pytest (that's a separate infra investment, out of scope here) — follow
  the file's existing convention, add a source-text assertion that the new
  arrow-key handler and its extracted `selectByName`-equivalent function
  exist, matching `test_sidebar_js_subscribes_to_required_events`'s pattern.
- Real JS behavior (arrow-key navigation actually moving selection, focus
  rings actually appearing, keyboard seek actually seeking) verified by
  manual headless screenshot during the build, using the `--project`/
  `--screenshot` CLI flags and `_LoggingWebEnginePage` console output already
  built this session — same method used to verify the map-rendering and
  tile-provider fixes.

## Explicitly out of scope

- Sub-projects B (project storage location), C (offline-verifiable outputs),
  D (timeline markers/POI) — separate specs.
- Any rename of `ProjectInfo` fields, the JSON schema, or the app name.
- Full accessibility audit (screen-reader labels on WebEngine content,
  ARIA beyond what already exists) — keyboard operability only, per the
  user's ask.
