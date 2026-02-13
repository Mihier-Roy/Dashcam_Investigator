# Dashcam Investigator

A Python desktop application to aid in the forensic investigation of evidence gathered from dashcam devices.

## Documentation

- **[AGENTS.md](./AGENTS.md)** - Comprehensive architecture documentation covering all system components, data flow, and module responsibilities

## Development

### Requirements

- **Python 3.10 - 3.12** (3.13+ not supported due to PyInstaller limitations)
- **[uv](https://docs.astral.sh/uv/)** - Fast, modern Python package manager written in Rust

The project uses [uv](https://docs.astral.sh/uv/) for dependency management. uv is ~10-100x faster than Poetry/pip and provides deterministic builds. Install uv from [here](https://docs.astral.sh/uv/getting-started/installation/).

### Quick Start

The following commands can be used to install dependencies and run the application:

```bash
# Install dependencies and create virtual environment
$ uv sync

# Run the application
$ uv run python -m dashcam_investigator

# Install with development dependencies
$ uv sync --dev
```

### Recent Updates (2025)

- **uv Migration** - Switched from Poetry to [uv](https://docs.astral.sh/uv/) for ~100x faster dependency resolution
- **PySide6 Upgrade** - Modernized GUI framework from PySide2 (Qt 5) to PySide6 (Qt 6)
- **Dependency Updates** - All packages updated to latest stable versions (pandas 3.0, numpy 2.4, etc.)
- **Architecture Documentation** - Added [AGENTS.md](./AGENTS.md) with comprehensive system design
- **Python 3.10-3.12** - Target runtime compatibility

### Dependencies

#### System Requirements

The following software must be installed on the system where the application is executed:

- **[ExifTool by Phil Harvey](https://exiftool.org/)** - Used to extract metadata (GPS data, timestamps, codecs) from video and image files. ExifTool must be available on the system PATH, or included with the application bundle.
- **Video Codecs** - The application requires video codecs to support playback. Install the [K-Lite Codec Pack](https://www.codecguide.com/download_k-lite_codec_pack_basic.htm) for Windows or use your system's codec manager.

#### Python Dependencies

All Python dependencies are automatically resolved and installed by uv. Current versions:

| Package | Version | Purpose |
|---------|---------|---------|
| **PySide6** | 6.10.2 | Modern Qt6 GUI framework (upgraded from PySide2) |
| **Pandas** | 3.0.0 | Data manipulation and analysis |
| **NumPy** | 2.4.2 | Numerical computing |
| **gpxpy** | 1.6.2 | GPS data processing |
| **folium** | 0.20.0 | Interactive map generation |
| **Altair** | 6.0.0 | Declarative data visualization |
| **Filetype** | 1.2.0 | File type detection |
| **PyInstaller** | 6.18.0 | Create standalone executables |
| **Black** | 26.1.0 | Code formatting (dev) |
| **pytest** | 9.0.2 | Unit testing (dev) |

See `pyproject.toml` for complete dependency specifications and `uv.lock` for pinned versions.

### Application Configuration

#### Logging

The application uses Python's built-in `logging` module configured via `log.conf`. Logging behavior:

- **Console Output** - DEBUG level and higher during development
- **File Logs** - Written to `%LOCALAPPDATA%/DashcamInvestigator/Logs/`:
  - `error.log` - ERROR and CRITICAL messages
  - `debug.log` - DEBUG and higher messages with module/line information

#### Building Executables

PyInstaller creates standalone Windows executables. The build includes ExifTool and supporting files:

```bash
# Build with uv
uv run pyinstaller \
  --clean \
  --noconsole \
  --add-data "gpx.fmt;." \
  --add-data "log.conf;." \
  --add-binary "exiftool.exe;." \
  --name DashcamInvestigator \
  dashcam_investigator/__main__.py
```

**Build Output:** `dist/DashcamInvestigator/` - Standalone application directory