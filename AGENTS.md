# Dashcam Investigator - Architecture & Agents Documentation

## Project Overview

**Dashcam Investigator** is a Python desktop application designed for forensic investigation of dashcam evidence. It provides investigators with tools to analyze video files, extract metadata, visualize GPS data on interactive maps, and generate detailed investigation reports.

**Technology Stack:**
- Python 3.9+ with Poetry for dependency management
- PySide2 (Qt 5.15.2) for GUI
- Pandas & NumPy for data analysis
- Folium for interactive mapping
- Altair for data visualization
- ExifTool for metadata extraction

---

## Core Architectural Layers

### 1. **GUI Layer** (`dashcam_investigator/gui/`)
Handles all user interface interactions and display logic using Qt/PySide2.

#### Key Components:

**`app.py` (Main Application Controller)**
- **Responsibility:** Main application window logic and event orchestration
- **Key Functions:**
  - `create_project()` - Initiates new project creation dialog
  - `load_project()` - Opens existing investigation project
  - `process_files()` - Triggers file scanning and metadata extraction
  - `display_video_info()` - Updates UI with video data
  - `generate_map()` - Renders interactive GPS map for selected video
  - `generate_graph()` - Generates speed profile charts
  - `flag_video()`, `save_notes()` - User annotation functions
  - `generate_report()` - Exports investigation report
- **Signals/Slots:** Qt signal-slot communication with worker threads
- **Threading:** Manages QThreadPool for non-blocking operations

**`QtMainWindow.py` (Qt Designer UI)**
- Auto-generated Qt GUI definition
- Contains UI element hierarchy: main window, stacked widget pages, tabs, dialogs
- Three main interface pages:
  1. Welcome page (project selection)
  2. Project page (investigation workspace)
  3. Video analysis tabs (Maps, Metadata, Speed Graphs, Notes)

**`new_project_class.py` (Project Creation Logic)**
- Handles project initialization workflow
- Validates user inputs (case name, investigator, directories)
- Creates initial project directory structure
- Initializes ProjectInfo data model

**`QtNewProjectDialog.py` (Project Dialog UI)**
- Dialog interface for creating new investigation projects
- Input fields: case name, investigator name, case number, input/output paths

**`worker_class.py` (Qt Threading Worker)**
- Inherits from QRunnable for multithreading support
- Processes long-running tasks without blocking UI:
  - Recursive file scanning
  - Metadata extraction
  - Map/graph generation
- Emits signals to update main GUI with progress

**`qt_models.py` (Custom Qt Data Models)**
- `VideoListModel` - Custom model for video file list view
- `FileTreeModel` - Custom model for directory tree view
- `MetadataTableModel` - Custom model for metadata display
- Handles data presentation and filtering in GUI tables/lists

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
- **Responsibility:** Create comprehensive investigation report
- **Key Functions:**
  - `generate_html_report()` - Create HTML report with all flagged videos
  - `create_report_structure()` - Build HTML DOM with navigation
  - `embed_video_data()` - Include video information, notes, hashes
  - `embed_map_data()` - Embed interactive maps in report
  - `create_javascript_navigation()` - Add interactive controls
- **Output:** Standalone HTML report file with embedded maps and metadata
- **Features:** Video thumbnails, notes, file hashes, flagging status

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
- **pyside2** (5.15.2) - Qt GUI framework
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computing
- **gpxpy** - GPS data parsing
- **folium** - Interactive mapping
- **altair** - Data visualization
- **filetype** - File type detection
- **pyinstaller** - Executable generation

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

- **pyproject.toml** - Dependency specifications and metadata
- **poetry.lock** - Locked versions for reproducible builds
- **log.conf** - Logging levels and output paths
- **gpx.fmt** - ExifTool format string for GPS extraction
- **.gitignore** - Standard Python project excludes

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
