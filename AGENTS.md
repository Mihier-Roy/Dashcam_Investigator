# Dashcam Investigator - Architecture & Agents Documentation

## Project Overview

**Dashcam Investigator** is a Python desktop application designed for forensic investigation of dashcam evidence. It provides investigators with tools to analyze video files, extract metadata, visualize GPS data on interactive maps, and generate detailed investigation reports.

**Technology Stack:**
- Python 3.10–3.12 with [uv](https://docs.astral.sh/uv/) for dependency management
- PySide6 (Qt 6.5+) for the desktop shell, with QtWebEngine for embedded HTML panels
- Jinja2 for HTML templating (in-app panels and exported report share one template set)
- Pandas & NumPy for data analysis
- Folium for interactive mapping
- Altair for data visualization
- ExifTool for metadata extraction

---

## Core Architectural Layers

### 1. **GUI Layer** (`dashcam_investigator/gui/`)
Hybrid: a thin Qt shell (`QMainWindow` + native video player + dialogs) hosting HTML panels rendered by QtWebEngine. Every content surface (welcome screen, sidebar, metadata table, notes editor, map, speed graph) is a Jinja-rendered template inside a `WebPanel`. A single `Bridge` QObject is exposed to every panel via `QWebChannel`, giving JS one consistent `window.api`.

#### Key Components:

**`app.py` (Main Application Controller)**
- **Responsibility:** `MainWindow` lifecycle, project state, bridge controller.
- Implements the `BridgeController` Protocol — every JS-callable slot
  forwards here: `select_video`, `set_flag`, `save_notes`,
  `get_metadata_json`, `toggle_flag_current`, `select_next_video`,
  `select_previous_video`, etc.
- Persists window geometry + splitter state via `QSettings` on
  `closeEvent`.
- Threading via `QThreadPool` for non-blocking file processing.

**`main_window.py` (Hand-written Layout)**
- `setup_ui(window, bridge)` builds the entire UI in code: menu bar
  (File → New / Open / Generate report / Exit), `QStackedWidget`
  (welcome panel + project page), horizontal `QSplitter`
  (sidebar | right column), vertical `QSplitter` inside the right
  column (player area | data tabs), and four `WebPanel`s in the tab
  widget (Map / Metadata / Speed Graph / Notes).
- No fixed pixel coordinates — layouts handle resizing; both splitter
  positions and the window geometry are persisted via `QSettings`.

**`theme.py` (Theme Manager)**
- Listens to `QStyleHints.colorSchemeChanged`, broadcasts the resolved
  theme over `Bridge.theme_changed`, and applies the matching QSS
  (`light.qss` / `dark.qss`) to the Qt shell so native widgets stay in
  sync with the embedded web pages.

**`web/`**
- `bridge.py` — `Bridge(QObject)` exposed via `QWebChannel`. Signals
  carry JSON; slots forward to a `BridgeController` (the MainWindow).
- `panel.py` — `WebPanel(QWebEngineView)` helper that renders a
  Jinja template, attaches the shared bridge, and serves assets via
  the custom `dci://` scheme.
- `scheme.py` — registers `dci://` (must run before `QApplication`)
  and serves files from `gui/assets/` with proper MIME types. Avoids
  `file://` quirks that bite QtWebEngine.
- `renderer.py` — Jinja2 environment, `static_url()`, `inline_svg()`
  and `inline_css()` globals. Resolves `gui/assets` in both dev and
  PyInstaller-frozen layouts.

**`assets/`** — static, shipped via PyInstaller `--add-data`.
- `templates/` — Jinja templates: `base.html`, `welcome.html`,
  `sidebar.html`, `metadata.html`, `notes.html`, `output_panel.html`
  (shared by Map + Speed Graph), `report.html`.
- `static/css/` — `tokens.css` (single source of truth for colors,
  spacing, typography), `base.css`, `components.css`, `app.css`,
  `report.css`.
- `static/js/` — `bridge.js` (QWebChannel handshake + signal relays
  exposing `window.api` and `window.events`), `theme.js`,
  `shortcuts.js`, plus per-page modules in `pages/`.
- `static/icons/` — inline-able Lucide-style SVGs.
- `qss/` — `light.qss` and `dark.qss` mirroring the CSS tokens.

**`new_project_class.py` + `QtNewProjectDialog.py`**
- The new-project dialog stays native Qt — it's small, infrequent, and
  benefits from native file pickers.

**`worker_class.py` (Qt Threading Worker)**
- `QRunnable`-based worker that runs file scanning + metadata extraction
  off the UI thread; emits progress / result / finished signals.

---

### 2. **Core Processing Layer** (`dashcam_investigator/core/`)
Contains business logic for data processing, analysis, and visualization.

#### Key Components:

**`extract_metadata.py` (Metadata Extraction Agent)**
- **Responsibility:** Extract technical metadata from video/image files
- **Key Functions:**
  - `ExifToolWrapper` class - Interface to ExifTool command-line utility
  - `extract_gps_data()` - Extracts GPS coordinates into GPX format
  - `extract_file_metadata()` - Gets creation date, duration, resolution, MIME type, file size
  - `get_video_duration()` - Parses video duration from metadata
  - `parse_gps_coordinates()` - Converts GPS data to usable format
- **External Dependency:** ExifTool (must be installed separately)
- **Output:** JSON metadata files, GPX files with GPS track data

**`process_files.py` (File Processing Pipeline)**
- **Responsibility:** Scan directories and classify files
- **Key Functions:**
  - `scan_directory()` - Recursive directory traversal
  - `classify_file()` - Determine file type (video/image/other)
  - `process_file_batch()` - Process multiple files in sequence
  - `get_file_type_from_mime()` - MIME type detection
- **Dependencies:** Uses `filetype` library for file type detection
- **Output:** Classified file lists with metadata

**`generate_dataframe.py` (GPS Data Processing)**
- **Responsibility:** Convert GPS/temporal data into analysis-ready format
- **Key Functions:**
  - `gpx_to_dataframe()` - Parse GPX file into pandas DataFrame
  - `extract_speed_profile()` - Convert m/s to km/h, extract speed values over time
  - `interpolate_coordinates()` - Fill gaps in GPS data
  - `calculate_statistics()` - Distance traveled, average speed, max speed
- **Dependencies:** gpxpy, pandas, numpy
- **Output:** Structured DataFrames for mapping and charting

**`map_functions.py` (Map Generation Utilities)**
- **Responsibility:** Helper functions for interactive map creation
- **Key Functions:**
  - `create_base_map()` - Initialize folium map centered on GPS data
  - `add_gps_track()` - Render GPS line segments on map
  - `add_markers()` - Place start/end and waypoint markers
  - `add_speed_coloring()` - Apply speed-based color gradient to track
  - `add_layer_controls()` - Enable layer toggling UI
  - `add_drawing_tools()` - Enable user annotation drawing
- **Dependencies:** folium, branca
- **Output:** HTML map files

**`map_classes.py` (Map Object Wrappers)**
- **Responsibility:** Object-oriented wrapper classes for map components
- **Key Classes:**
  - `GpsTrack` - Represents a GPS trajectory
  - `MapPoint` - Individual map marker with metadata
  - `InteractiveMap` - Full map with all layers and controls
  - `MapLayer` - Individual layer (track, markers, etc.)
- **Methods:** Add features, set styles, export to HTML

**`output_generator.py` (Map & Chart Generation Orchestrator)**
- **Responsibility:** Coordinate generation of all visual outputs
- **Key Functions:**
  - `generate_all_outputs()` - Main orchestration function
  - `generate_map_for_video()` - Create and save map HTML
  - `generate_speed_graph()` - Create and save speed chart HTML
  - `generate_metadata_csv()` - Export metadata to CSV
- **Dependencies:** Calls extract_metadata, generate_dataframe, map_functions
- **Output:** HTML files for maps and graphs

**`generate_report.py` (HTML Report Generation)**
- **Responsibility:** Render the standalone investigation report from
  the same Jinja templates the in-app UI uses, so the report and the
  app share one visual language.
- **Public API:** `generate_report(project_object) -> Path`.
- **Output:** Self-contained HTML file. CSS (tokens + base + components +
  report) and SVG icons are inlined via `inline_css()` / `inline_svg()`.
  Map and speed-graph HTMLs are referenced via iframes with relative
  posix paths (`../Maps/foo.html`) so the report ships alongside the
  project's standard sibling directories.
- **Features:** flagged-only filter, sidebar list with hash preview,
  per-video info card (Create date / Duration / Device), notes card,
  iframe for GPS map, iframe for speed graph. `@media print` drops the
  sidebar and shows every video pane in sequence.

**`get_file_count.py` (File Counting Utility)**
- **Responsibility:** Count files in directory (with caching for performance)
- **Key Functions:**
  - `count_files_by_type()` - Get counts of videos, images, other files
  - `get_total_file_count()` - Count all files recursively

---

### 3. **Project Management Layer** (`dashcam_investigator/project_manager/`)
Handles project lifecycle: creation, loading, persistence, and serialization.

#### Key Components:

**`project_manager.py` (Project Lifecycle Manager)**
- **Responsibility:** Create, load, save, and manage investigation projects
- **Key Functions:**
  - `create_new_project()` - Initialize new project with directory structure
  - `load_project()` - Load existing project from JSON
  - `save_project()` - Persist project state to JSON
  - `get_project_info()` - Retrieve project metadata
  - `add_file_to_project()` - Register new file in project
  - `update_file_annotations()` - Save user notes and flags
- **Project Structure Creation:**
  ```
  output_dir/
  ├── Maps/
  ├── Graphs/
  ├── Metadata/
  ├── Reports/
  ├── Timelines/
  └── dashcam_investigator.json  (project file)
  ```
- **Serialization:** Custom JSON functions for complex data types

**`project_datatypes.py` (Data Models)**
- **Responsibility:** Define data structures for project information
- **Key Classes:**
  - `ProjectInfo` - Case metadata (name, investigator, dates, paths)
  - `FileAttributes` - Video file data (path, hash, duration, metadata references)
  - `VideoMetadata` - Technical metadata (creation date, resolution, codec)
  - `GpsMetadata` - GPS-specific data (track points, speed data)
  - `ProjectStructure` - Hierarchical project organization
- **Serialization:** Custom JSON encoding/decoding for complex objects

---

### 4. **Utility Layer** (`dashcam_investigator/utils/`)
Helper functions used across layers.

#### Key Components:

**`common.py` (Common Utilities)**
- **Responsibility:** Reusable utility functions
- **Key Functions:**
  - `generate_sha256_hash()` - Create file integrity hash
  - `convert_timestamp()` - Convert between time formats
  - `format_duration()` - Human-readable time formatting
  - `format_file_size()` - Human-readable size formatting
  - `get_system_info()` - Gather system details for reports

**`custom_json_functions.py` (Custom JSON Serialization)**
- **Responsibility:** Handle serialization of complex objects to JSON
- **Key Functions:**
  - `json_encoder()` - Custom encoder for datetime, UUID, other types
  - `json_decoder()` - Custom decoder for JSON objects
  - `serialize_project()` - Convert ProjectStructure to JSON
  - `deserialize_project()` - Load ProjectStructure from JSON

---

### 5. **Application Entry Point** (`dashcam_investigator/__main__.py`)
- **Responsibility:** Bootstrap the application
- **Key Functions:**
  - Application initialization and configuration
  - Logging setup (dual output to console and file)
  - Window creation and display
  - Qt event loop initialization
- **Logging:** Configured via `log.conf`
  - Debug logs: `%LOCALAPPDATA%/DashcamInvestigator/Logs/debug.log`
  - Error logs: `%LOCALAPPDATA%/DashcamInvestigator/Logs/error.log`

---

## Data Flow Architecture

### Investigation Workflow:

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER LAUNCHES APP                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │   Welcome Screen        │
              │   (Create/Load Project) │
              └────────────┬────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
    ┌───▼────────┐              ┌────────────▼─────┐
    │ New Project│              │ Load Project      │
    └───┬────────┘              └────────┬──────────┘
        │                                │
        │ project_manager.py             │ project_manager.py
        │ create_new_project()           │ load_project()
        │                                │
        └────────────────┬───────────────┘
                         │
              ┌──────────▼──────────────┐
              │  Project Page Loaded    │
              │  in Main GUI (app.py)   │
              └──────────┬──────────────┘
                         │
         ┌───────────────▼──────────────┐
         │  User Selects Directory      │
         │  or Processes Files          │
         └───────────────┬──────────────┘
                         │
         ┌───────────────▼──────────────────┐
         │  File Scanning (worker_class.py) │
         │  Runs in Thread                  │
         └───────────────┬──────────────────┘
                         │
    ┌────────────────────▼────────────────────┐
    │ For Each Video File:                    │
    │ 1. extract_metadata.py                  │
    │    - ExifTool extracts GPS, duration    │
    │ 2. process_files.py                     │
    │    - Classify file type                 │
    │ 3. generate_dataframe.py                │
    │    - Convert GPS to DataFrame           │
    │ 4. map_functions.py + output_generator  │
    │    - Generate interactive map           │
    │    - Generate speed graph               │
    │ 5. project_manager.py                   │
    │    - Save FileAttributes to project     │
    └────────────────────┬────────────────────┘
                         │
    ┌────────────────────▼────────────────────┐
    │  Results Available in GUI:              │
    │  - Maps tab: Display GPS route          │
    │  - Metadata tab: File info table         │
    │  - Speed Graphs tab: Speed profile      │
    │  - Notes tab: User annotations          │
    └────────────────────┬────────────────────┘
                         │
    ┌────────────────────▼────────────────────┐
    │  User Can:                              │
    │  - Flag important videos                │
    │  - Add investigation notes              │
    │  - Review GPS and speed data            │
    │  - Export metadata                      │
    └────────────────────┬────────────────────┘
                         │
    ┌────────────────────▼────────────────────┐
    │  Generate Report                        │
    │  generate_report.py creates HTML with:  │
    │  - All flagged videos                   │
    │  - Embedded maps and graphs             │
    │  - File hashes (integrity)              │
    │  - Investigation notes                  │
    │  - Interactive navigation               │
    └────────────────────┬────────────────────┘
                         │
    ┌────────────────────▼────────────────────┐
    │  Report Available for Review/Export     │
    └────────────────────────────────────────┘
```

---

## Inter-Agent Communication

### API Contracts:

**File Processing Pipeline:**
```
process_files.py:scan_directory(path)
  → [FileInfo, FileInfo, ...]

extract_metadata.py:extract_gps_data(video_path)
  → GPX file + GPS DataFrame

generate_dataframe.py:gpx_to_dataframe(gpx_file)
  → pandas.DataFrame with columns: [timestamp, latitude, longitude, speed]

map_functions.py:create_base_map(center_point, zoom)
  → folium.Map object

output_generator.py:generate_all_outputs(project, video_file)
  → {map_html, graph_html, metadata_csv}

generate_report.py:generate_html_report(project, flagged_videos)
  → HTML report file
```

**Project Persistence:**
```
project_manager.py:save_project(project_structure)
  → dashcam_investigator.json file

project_manager.py:load_project(json_path)
  → ProjectStructure object
```

**Qt Communication:**
```
app.py (Main Thread)
  ↓ Creates & emits signals
worker_class.py (Worker Thread)
  ↓ Processes in background
  ↓ Emits progress signals
app.py (Main Thread)
  ↓ Receives signals, updates GUI
```

---

## External Dependencies

### System Dependencies:
- **ExifTool** - Command-line utility for metadata extraction
  - Required for GPS data and file metadata
  - Must be installed separately on system
  - Called via subprocess from `extract_metadata.py`

### Python Dependencies (see pyproject.toml):
- **PySide6** (>= 6.5) — Qt6 GUI framework, with QtWebEngine + QtWebChannel
- **Jinja2** (>= 3.1) — HTML templating shared by the app and the report
- **pandas** — Data manipulation and analysis
- **numpy** — Numerical computing
- **gpxpy** — GPS data parsing
- **folium** — Interactive mapping
- **altair** — Data visualization
- **filetype** — File type detection
- **pyinstaller** — Executable generation

---

## Key Design Patterns

1. **Separation of Concerns:** GUI, processing, and project management are isolated
2. **Threading Model:** Long operations run in QThreadPool to keep UI responsive
3. **Signal-Slot Pattern:** Qt's signal/slot for thread-safe GUI updates
4. **Factory Pattern:** Project creation through ProjectManager
5. **Repository Pattern:** ProjectManager handles data persistence
6. **Wrapper Pattern:** ExifToolWrapper abstracts command-line calls
7. **MVC Pattern:** Custom Qt models separate data from presentation

---

## Configuration Files

- **pyproject.toml** — Dependency specifications and metadata
- **uv.lock** — Locked versions for reproducible builds
- **log.conf** — Logging levels and output paths
- **gpx.fmt** — ExifTool format string for GPS extraction
- **.gitignore** — Standard Python project excludes
- **flake.nix** / **.envrc** — Nix + direnv dev shell: `python3.12`, `uv`,
  `exiftool`, and the system libraries PySide6/QtWebEngine dlopen at
  runtime (Chromium/X11/Mesa stack). `direnv allow` once per checkout;
  `uv sync` inside the shell to get the project venv.

---

## Running Headless & Scripted Interaction

`__main__.py` accepts CLI flags for non-interactive runs, sharing the
same code path as normal GUI use (`MainWindow.open_project_path`) —
no separate "headless mode" to drift out of sync:

```
uv run python -m dashcam_investigator --project path/to/project \
    --screenshot out.png --screenshot-delay 2.0
```

- `--project PATH` — opens a project on startup (a
  `dashcam_investigator.json` file, or its containing directory)
  instead of showing the welcome screen. Load failures exit 1 with a
  logged error instead of a blocking dialog whenever `--screenshot` is
  also set, since a headless run has nobody to dismiss one.
- `--screenshot PATH` — grabs the main window shortly after startup
  and exits. Combine with `QT_QPA_PLATFORM=offscreen` (a built-in Qt
  platform plugin, no display server needed) for CI/headless
  verification:
  ```
  QT_QPA_PLATFORM=offscreen uv run python -m dashcam_investigator \
      --project test_project --screenshot out.png
  ```
- `--screenshot-delay SECONDS` (default 2.0) — WebEngine panels
  (map/graph/notes) render asynchronously; bump this if a screenshot
  captures before they've finished painting.

**JS console → Python log:** every `WebPanel` uses a
`QWebEnginePage` subclass (`gui/web/panel.py::_LoggingWebEnginePage`)
that routes `console.log/warn/error` to the Python logger as
`JS console [source:line] message`. There's no devtools to open on a
headless run, so this is the only way page-side JS errors (a broken
CDN load, a bridge signal race, a template bug) surface at all —
check the log first whenever a panel renders blank.

**Driving the app without a real display/input device:** there's no
"click at coordinates" API — instead, construct `MainWindow` in a
script and call its public methods directly, then let the Qt event
loop process a `QTimer` before grabbing:

```python
import sys
from pathlib import Path
from PySide6 import QtCore, QtWidgets
from dashcam_investigator.gui.web.scheme import register_scheme
register_scheme()  # must run before QApplication
from dashcam_investigator.gui.app import MainWindow

app = QtWidgets.QApplication([])
window = MainWindow()
window.open_project_path(Path("test_project"), interactive=False)
window.show()

def select_and_capture():
    window.select_video("some_video.mp4")          # sidebar row click
    QtCore.QTimer.singleShot(2000, lambda: (
        window.grab().save("out.png"), app.quit()
    ))

QtCore.QTimer.singleShot(1500, select_and_capture)  # let panels finish loading first
sys.exit(app.exec())
```

Run this from the repo root (so `dashcam_investigator` is importable)
with `QT_QPA_PLATFORM=offscreen uv run python script.py`. Other
`BridgeController` methods (`set_flag`, `save_notes`,
`toggle_flag_current`, `select_next_video`, …) work the same way —
call them directly on `window` instead of simulating a click.

**Common pitfalls this setup avoids/exposes:**
- `Bridge.project_loaded`/`video_changed` are fire-once signals with
  no replay; a panel whose QWebChannel handshake finishes late (e.g.
  a project opened immediately at startup) would silently show stale
  empty state forever. `sidebar.js` pulls current state via
  `api.getProjectJson()` on ready in addition to listening for pushes
  — follow that pattern for any new panel that needs current state.
- `--project` before `window.show()` used to lose the initial
  broadcast; call order alone isn't a reliable fix (WebEngineViews
  finish loading asynchronously regardless), which is why the pull-on-
  ready fix above is the real guard, not a `show()`-then-open
  reordering.

---

## Output Artifacts

For each analyzed video:
1. **GPS Map** - Interactive HTML with folium
2. **Speed Graph** - HTML chart with Altair
3. **Metadata File** - JSON with technical details
4. **GPX File** - GPS track data in standard format
5. **Project File** - dashcam_investigator.json (project metadata)
6. **Investigation Report** - Standalone HTML with all flagged videos

---

## Future Enhancement Points

- **Video Processing:** Frame extraction, optical character recognition (OCR)
- **Advanced Analytics:** Machine learning for anomaly detection in speed patterns
- **Database Backend:** Replace JSON with SQLite for large projects
- **Multi-user:** Collaborative investigation features
- **Mobile UI:** Web-based interface for remote access
- **Additional Formats:** Support for dash cam API integrations (Viofo, Thinkware, etc.)
- **Recent projects:** Welcome-screen list of recently opened projects
- **Single-file portable report:** Inline map/graph HTMLs into the report so it travels without sibling dirs
