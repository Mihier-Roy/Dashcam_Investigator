# Dashcam Investigator

A Python desktop application to aid in the forensic investigation of evidence gathered from dashcam devices.

## Documentation

- **[AGENTS.md](./AGENTS.md)** - Comprehensive architecture documentation covering all system components, data flow, and module responsibilities

## Development

### Requirements

- **Python 3.10 - 3.12** (3.13+ not supported due to PyInstaller limitations)
- **[uv](https://docs.astral.sh/uv/)** - Fast, modern Python package manager written in Rust

The project uses [uv](https://docs.astral.sh/uv/) for dependency management. Install uv from [here](https://docs.astral.sh/uv/getting-started/installation/).

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

### Dependencies

#### System Requirements

The following software must be installed on the system where the application is executed:

- **[ExifTool by Phil Harvey](https://exiftool.org/)** - Used to extract metadata (GPS data, timestamps, codecs) from video and image files. ExifTool must be available on the system PATH.
- **Video Codecs** - The application requires video codecs to support playback.

**Windows:**

- ExifTool: download `exiftool.exe` from [exiftool.org](https://exiftool.org/) and place it on `PATH`.
- Codecs: install the [K-Lite Codec Pack](https://www.codecguide.com/download_k-lite_codec_pack_basic.htm).

**Linux (Debian/Ubuntu):**

```bash
sudo apt install \
  libimage-exiftool-perl \
  gstreamer1.0-libav \
  gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad \
  gstreamer1.0-plugins-ugly
```

`QMediaPlayer` on Linux is backed by GStreamer, so the codec packages above are what makes typical dashcam streams (H.264 / H.265 / AAC) play. On Fedora the equivalent is `perl-Image-ExifTool` plus the `gstreamer1-plugin-*` family from RPM Fusion.

#### Python Dependencies

All Python dependencies are automatically resolved and installed by uv. Current versions:

| Package | Version | Purpose |
|---------|---------|---------|
| **PySide6** | >= 6.5 | Qt6 GUI framework (with QtWebEngine + QtWebChannel) |
| **Jinja2** | >= 3.1 | HTML templating for the web panels and exported report |
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
- **File Logs** - Written to a per-user log directory:
  - Windows: `%LOCALAPPDATA%/DashcamInvestigator/DashcamInvestigator/Logs/`
  - Linux: `$XDG_STATE_HOME/DashcamInvestigator/log/` (typically `~/.local/state/DashcamInvestigator/log/`)
  - macOS: `~/Library/Logs/DashcamInvestigator/`

  Files in that directory:
  - `error.log` - ERROR and CRITICAL messages
  - `debug.log` - DEBUG and higher messages with module/line information

#### Building Executables

PyInstaller is driven by `DashcamInvestigator.spec`, which works on Windows, Linux, and macOS:

```bash
uv run pyinstaller --noconfirm --clean DashcamInvestigator.spec
```

The spec bundles `gpx.fmt`, `log.conf`, and the entire `gui/assets` tree (Jinja templates, CSS tokens, JS bridge, inline SVG icons — the web panels render empty without these). ExifTool is **not** bundled; users install it system-wide as described under System Requirements.

**Build Output:** `dist/DashcamInvestigator/` — standalone application directory. Launch with `DashcamInvestigator.exe` (Windows) or `./DashcamInvestigator` (Linux/macOS).

##### Linux: tar.gz and AppImage

After running PyInstaller, package the result for distribution:

```bash
# Portable tar.gz (extract anywhere, run ./DashcamInvestigator)
tar -czf dist/DashcamInvestigator-linux-x86_64.tar.gz -C dist DashcamInvestigator

# Single-file AppImage (requires `appimagetool` on PATH)
./packaging/linux/build_appimage.sh
```

`packaging/linux/build_appimage.sh` wraps the PyInstaller bundle in an AppDir with the `.desktop` entry and icon under `packaging/linux/`, then invokes `appimagetool` to produce `dist/DashcamInvestigator-x86_64.AppImage`. Get `appimagetool` from the [AppImageKit releases](https://github.com/AppImage/AppImageKit/releases).

### Keyboard shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New project |
| `Ctrl+O` | Open project |
| `Ctrl+S` | Save the current video's notes |
| `Ctrl+Q` | Quit |
| `/` | Focus the sidebar filter |
| `f` | Toggle flag on the currently selected video |
| `←` / `→` | Previous / next video |