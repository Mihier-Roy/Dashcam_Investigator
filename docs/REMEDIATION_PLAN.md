# Dashcam Investigator — Remediation Plan

Phased plan derived from the deep-dive review on branch
`claude/code-review-analysis-hEYXZ`. Each task is keyed to the review IDs
(C/H/M/L = Critical/High/Medium/Low) so an executing agent can
cross-reference. Every task has a one-sentence diagnosis, concrete steps,
and a verification check that should be run before marking it done.

**Branch**: `claude/code-review-analysis-hEYXZ`
**Working tree**: `/home/user/Dashcam_Investigator`
**Style**: small, focused commits per phase. Each phase ends with
`uv run pytest`, `uv run ruff check .`, `uv run black --check .`. Push at
the end of every phase.

---

## Phase 0 — Baseline & Safety Net

Goal: Establish that the working tree builds, tests pass, and we have a
way to verify fixes.

### 0.1 Verify branch + clean state
```bash
git status                                    # must be clean
git rev-parse --abbrev-ref HEAD               # must be claude/code-review-analysis-hEYXZ
```

### 0.2 Establish baseline
```bash
uv sync --frozen --dev
uv run pytest -v 2>&1 | tee /tmp/baseline-tests.txt
uv run ruff check . 2>&1 | tee /tmp/baseline-ruff.txt
uv run black --check . 2>&1 | tee /tmp/baseline-black.txt
uv run bandit -r dashcam_investigator -ll 2>&1 | tee /tmp/baseline-bandit.txt
```
Record the failures we know about; do **not** treat them as regressions
later.

### 0.3 Verify exiftool available for integration tests
```bash
which exiftool || sudo apt install -y libimage-exiftool-perl
exiftool -ver
```

**Phase 0 done when**: baseline outputs captured; subsequent phases
compare against `/tmp/baseline-*.txt`.

---

## Phase 1 — Core Pipeline Correctness (must-fix)

These break the headline feature (map + speed graph) for end users.

### 1.1 [C1] Remove deprecated Stamen tilesets
- **File**: `dashcam_investigator/core/map_classes.py:200-202`
- **Diagnosis**: `TileLayer("Stamen Terrain")` and `"Stamen Toner"` raise
  `ValueError` on folium ≥ 0.14 because Stamen migrated to Stadia and
  needs an API key.
- **Steps**:
  1. Delete the `TileLayer("Stamen Terrain")` and `"Stamen Toner"` lines.
  2. Remove the `TileLayer("OpenStreet Map")` call too — `Map(...)`
     already adds OSM as the default layer (L3).
  3. If `add_tilelayers` becomes empty, delete it and remove its caller
     in `core/map_functions.py:22`.
- **Verify**:
  ```bash
  uv run python -c "
  from dashcam_investigator.core.map_functions import initialise_map
  m = initialise_map((37.7749, -122.4194))
  m.canvas.get_root().render()
  print('OK')
  "
  ```
  Add unit test `tests/test_map_classes.py::test_initialise_map_renders`
  asserting the rendered HTML contains `tile.openstreetmap.org`.

### 1.2 [H1] Fix `convert_to_seconds` for videos ≥ 1 hour
- **File**: `dashcam_investigator/utils/common.py:20-32`
- **Diagnosis**: `% 60` wraps minutes; the type hint lies (returns
  strings).
- **Steps**:
  1. Change return type to `tuple[str, str]`, or refactor to return
     `(hours, minutes, seconds)` and let the caller format.
  2. Drop `% 60` on minutes; format as `H:MM:SS` when total minutes
     ≥ 60.
  3. Update both callers in `gui/app.py:142, 153` to render the new
     shape.
- **Verify**: extend `tests/test_common.py` with cases:
  - `(0, "0:00")`
  - `(60_000, "1:00")`
  - `(3_600_000, "1:00:00")`
  - `(3_900_000, "1:05:00")`

### 1.3 [H5] Fix `convert_to_datetime` to match what `gpx.fmt` produces
- **File**: `dashcam_investigator/core/generate_dataframe.py:68-84`
- **Diagnosis**: `gpx.fmt` writes ISO-8601 (`%Y-%m-%dT%H:%M:%SZ`), but
  the code re-parses what is already a `datetime` object using
  DD-MM-YYYY then YY:MM:DD.
- **Steps**:
  1. In `process_gpx_to_df`, store `point.time` directly. Then
     `convert_to_datetime` becomes a `pd.to_datetime(..., errors="coerce")`
     no-op.
  2. Drop the bare `except Exception:`. Use `errors="coerce"`.
  3. Switch `process_file_meta` to `-d "%Y-%m-%d %H:%M:%S"` (ISO) and
     update the parser side to match (also resolves M12).
- **Verify**: extend `tests/test_generate_dataframe.py`:
  - Build a real GPX (using `gpxpy`) → call `MetaDataFrames` →
    `convert_to_datetime` → assert
    `gps_df["DateTime"].dtype == "datetime64[ns]"` and no `NaT`.
  - Mock CSV with ISO `CreateDate` → assert it parses.

### 1.4 [C5] Delete dead/broken `find_final_point_in_route`
- **File**: `dashcam_investigator/core/generate_dataframe.py:113-116`
- **Diagnosis**: References a column that doesn't exist; never called.
- **Steps**: Delete the function.
- **Verify**: `grep -rn find_final_point_in_route .` returns zero hits.

### 1.5 [M1] Delete duplicate mean computation
- **File**: `dashcam_investigator/core/output_generator.py:41-44`
- **Steps**: Remove the no-op tuple expression.

### 1.6 [H2] Don't append failed videos as if they succeeded
- **File**: `dashcam_investigator/core/process_files.py:27-38`
- **Diagnosis**: When `extract_meta`/`create_map` raise
  `DashcamInvestigatorError`, the partially-populated `FileAttributes`
  is still returned and added to the project.
- **Steps**:
  1. Add `processing_error: str | None = None` to `FileAttributes`
     (`project_manager/project_datatypes.py`); include in `to_dict` and
     the JSON decoder (`utils/custom_json_functions.py`).
  2. In `_process_video_file`, on exception set
     `video.processing_error = str(exc)` and return as before.
  3. In `gui/assets/static/js/pages/sidebar.js`, render a small ⚠ badge
     on rows with truthy `processing_error`. `title=` shows the error.
  4. In `output_panel.html` and `metadata.html`, render the error in the
     empty state when `processing_error` is set.
- **Verify**: extend `tests/test_process_files.py` — patch
  `extract_meta` to raise `ExifToolError`, assert the resulting
  `FileAttributes.processing_error` matches and the video appears in
  `project.video_files`.

### Phase 1 checkpoint
```bash
uv run pytest -v
uv run ruff check . && uv run black --check .
git add -A
git commit -m "fix: pipeline correctness (folium tiles, datetime, video errors)"
git push -u origin claude/code-review-analysis-hEYXZ
```

---

## Phase 2 — Security & Path Hardening

### 2.1 [C3] Sanitize `case_name` before using it as a path component
- **File**: `dashcam_investigator/core/generate_report.py:30-43`
- **Steps**:
  1. Add `_safe_filename(name: str) -> str` that replaces every char
     outside `[A-Za-z0-9._\- ]` with `_`, collapses runs to one, and
     strips leading dots.
  2. Apply when building `output_file`. Then assert
     `output_file.resolve().is_relative_to((case.project_directory / "Reports").resolve())`.
     If not, raise a new `ReportError(DashcamInvestigatorError)`.
  3. Apply the helper anywhere else `case.case_name` becomes part of a
     path: `grep -rn case_name dashcam_investigator/`.
- **Verify**: add
  `tests/test_generate_report.py::test_case_name_traversal_blocked`
  with cases `"../../escape"`, `"a/b"`, `"..\\foo"` — all must produce a
  path inside `Reports/`.

### 2.2 [C4] Replace string-concat popup HTML with escaped Jinja template
- **File**: `dashcam_investigator/core/map_classes.py:75-189`
- **Steps**:
  1. Create
     `dashcam_investigator/gui/assets/templates/partials/_marker_popup.html`
     with the table; use `{{ field }}` (autoescape on).
  2. In `StartMarkerPopup.start_marker_popup_html`, render via
     `from dashcam_investigator.gui.web.renderer import render`.
  3. Delete the inlined HTML string.
- **Verify**: add
  `tests/test_map_classes.py::test_popup_escapes_html_in_filename`:
  - Build `StartMarkerPopup` with
    `file_name="<script>alert(1)</script>"`.
  - Assert the rendered popup contains `&lt;script&gt;` and not
    `<script>`.

### Phase 2 checkpoint
```bash
uv run pytest -v
uv run bandit -r dashcam_investigator     # without -ll
git add -A
git commit -m "fix(security): sanitize case_name + escape popup HTML"
git push
```

---

## Phase 3 — Lifecycle & Concurrency

### 3.1 [C6] Stop the worker thread on window close
- **Files**: `dashcam_investigator/gui/app.py:94-96`,
  `gui/worker_class.py`
- **Steps**:
  1. Track active worker on the main window:
     `self._active_worker: Worker | None = None`. Set after
     `threadpool.start(worker)`.
  2. In `WorkerSignals` add `cancelled = Signal()`. In `Worker`, expose
     `self.cancel_event = threading.Event()`. Pass into `process_files`
     via kwargs.
  3. In `process_files`, between video iterations, check
     `cancel_event.is_set()` and break cleanly.
  4. In `MainWindow.closeEvent`, if a worker is active prompt with
     `QMessageBox`. On confirm, set the cancel event and
     `threadpool.waitForDone(5000)`. If still running, `event.ignore()`
     and warn.
  5. Disconnect signal connections to widgets that get destroyed before
     `super().closeEvent`.
- **Verify**: add
  `tests/test_main_window.py::test_close_with_running_worker` — mock
  the worker, simulate close, assert `cancel_event.set()` was called.

### 3.2 [H10] Disable File menu while a worker is in flight
- **File**: `dashcam_investigator/gui/app.py:189-228`
- **Steps**:
  1. Guard `start_new_project`: if `self._active_worker` is alive,
     return / show status.
  2. Disable `action_new_project`, `action_open_project`,
     `actionGenerate_Report` when a worker starts; re-enable in
     `thread_complete` and `_on_worker_error`.
- **Verify**: extend the test from 3.1 to confirm actions toggle.

### 3.3 Guard splitter state save in `closeEvent`
- **File**: `dashcam_investigator/gui/app.py:88-96`
- **Steps**: Check for `self.h_splitter` / `self.v_splitter` before
  saving — they don't exist on the welcome screen.

### Phase 3 checkpoint
```bash
uv run pytest -v
git add -A
git commit -m "fix(lifecycle): cancel workers on close, gate menu while busy"
git push
```

---

## Phase 4 — Performance & I/O Correctness

### 4.1 [C2] Bypass `setHtml` for large output panels
- **Files**: `gui/web/panel.py:56-59`, `gui/main_window.py:274-313`
- **Diagnosis**: `setHtml` truncates above ~2 MB.
- **Steps**:
  1. Add `WebPanel.set_url(url: QUrl)` calling `self.setUrl(url)`.
  2. Map/graph panels: load directly from the on-disk file
     (`Maps/<name>_map.html`) via `setUrl(QUrl.fromLocalFile(...))`
     instead of reading bytes and feeding them to srcdoc.
  3. Update `output_panel.html` so the empty state still renders when no
     file exists.
- **Verify**: build a 5 MB folium map (50_000 markers) and confirm the
  panel renders by running the UI manually. Add a unit test asserting
  the map panel path does not call `setHtml`.

### 4.2 [H3, M6] Cache `sha256_hash`; never recompute on save
- **Files**: `project_manager/project_datatypes.py:69-93`,
  `gui/web/bridge.py:133-139`, `gui/app.py:368-371`
- **Steps**:
  1. In `FileAttributes`, ensure `to_dict` returns `self._sha256_hash`
     directly without triggering recompute when set.
  2. Compute hashes once in `process_files` (after extraction
     succeeds): `_ = video.sha256_hash`.
  3. Allow `_sha256_hash` to be `None` (failed entries serialize as
     `null`).
- **Verify**: add
  `tests/test_project_datatypes.py::test_to_dict_does_not_recompute_hash`:
  - Patch `generate_file_hash` to count calls.
  - Build `FileAttributes` with `sha256_hash="abc"`, call `to_dict()`
    five times.
  - Assert `generate_file_hash.call_count == 0`.

### 4.3 [H4] Add `encoding="utf-8"` to every text I/O call
```bash
grep -rn "read_text()" dashcam_investigator/ tests/   # every hit needs encoding=
grep -rnE "\.open\([\"']r[\"']\)|\.open\([\"']w[\"']\)" dashcam_investigator/
```
- Patch the call sites:
  - `gui/main_window.py:310` — `path.read_text(encoding="utf-8")`
  - `gui/web/renderer.py:76, 101` — same
  - `gui/theme.py:83` — same
  - `project_manager/project_manager.py:104, 124` — open with
    `encoding="utf-8"`
  - `core/generate_report.py:103` — already correct ✓ (verify)
- **Verify**: these greps must return zero hits:
  ```bash
  grep -rn "read_text()" dashcam_investigator/ | grep -v encoding
  grep -rnE "\.open\([\"']r[\"']\)" dashcam_investigator/
  ```

### 4.4 [H6] `mkdir(parents=True, exist_ok=True)`
- **File**: `project_manager/project_manager.py:51-62`
- **Steps**: Replace both `mkdir()` calls.
- **Verify**: extend `tests/test_project_manager.py` with a test that
  creates a project where the parent of `output_dir` does not exist.

### Phase 4 checkpoint
```bash
uv run pytest -v
grep -rn "read_text()" dashcam_investigator/ | grep -v encoding && exit 1
git add -A
git commit -m "fix: cache hashes, utf-8 encoding, parents=True"
git push
```

---

## Phase 5 — GUI / UX Polish

### 5.1 [H7] Don't clear directory entry on cancel
- **File**: `gui/new_project_class.py:41, 56`
- **Steps**: Replace `if dir is not None:` with `if dir:` in both
  methods.

### 5.2 [H8, L1] QTextEdit → QLineEdit
- **File**: `gui/QtNewProjectDialog.py`
- **Steps**:
  1. Replace `QTextEdit` for `input_edit`, `output_edit`, `case_edit`,
     `investigator_edit` with `QLineEdit`.
  2. Update callers in `gui/new_project_class.py` from `.toPlainText()`
     to `.text()`.
  3. Fix the typo `"Ouput Directory"` → `"Output Directory"` (line 93).

### 5.3 [H9] Sensible initial dir
- **File**: `gui/new_project_class.py:36, 51`
- **Steps**: `"C:"` → `str(Path.home())`.

### 5.4 [M7] Cancel button on progress dialog
- **File**: `gui/app.py:212-220`
- **Steps**: Pass `"Cancel"` instead of `None` for the second arg;
  connect `progress.canceled` to a slot calling
  `self._active_worker.cancel_event.set()` (added in 3.1).

### 5.5 [M8] Surface `QMediaPlayer.errorOccurred`
- **File**: `gui/app.py:65-73`
- **Steps**: Connect
  `self.mediaPlayer.errorOccurred.connect(self._on_media_error)`.
  Implement `_on_media_error(err, msg)` to log and show a status-bar
  message ("Codec missing? See README.").

### 5.6 [M5] Document or fix multi-row CSV truncation
- **Files**: `gui/app.py:419`, `core/generate_report.py:79`
- **Steps**: Decide whether to keep `df.iloc[0]` or merge non-empty
  cells across rows. Add a comment explaining the choice. Add a test
  fixture with a 2-row CSV.

### Phase 5 checkpoint
```bash
uv run pytest -v
# Manual smoke (must run on a desktop, not in CI):
#   uv run python -m dashcam_investigator
#   - New Project dialog uses single-line inputs, opens at $HOME.
#   - Cancel preserves prior text.
#   - Progress dialog shows Cancel.
git add -A
git commit -m "fix(ux): single-line inputs, cancel button, media errors"
git push
```

---

## Phase 6 — CI, Packaging, Tooling

### 6.1 [C7] Add Windows + macOS to test matrix
- **File**: `.github/workflows/ci.yml:50-72`
- **Steps**:
  1. Change `runs-on: ubuntu-latest` → `runs-on: ${{ matrix.os }}`.
  2. Add `os: [ubuntu-latest, windows-latest, macos-latest]` to the
     matrix.
  3. Set `QT_QPA_PLATFORM: offscreen` on the test step.
  4. On Linux runners, install `libegl1`, `libxkbcommon-x11-0`,
     `libxcb-cursor0` so `QtWebEngineCore` imports.
- **Verify**: push to a PR and watch the matrix turn green.

### 6.2 [H12] Coverage gate honesty
- **File**: `pyproject.toml:58-67`
- **Steps**: Remove the `omit` list; lower `--cov-fail-under` to 5 %
  below the realistic measurement after Phase 5. Add a few headline
  tests for the previously-omitted controllers.
- **Verify**: `uv run pytest --cov-report=term-missing`.

### 6.3 [H11] Fix `.desktop` Categories
- **File**: `packaging/linux/DashcamInvestigator.desktop:9`
- **Steps**: `Categories=Office;AudioVideo;Utility;X-Forensics;` →
  `Categories=AudioVideo;Utility;X-Forensics;`.
- **Verify**:
  `desktop-file-validate packaging/linux/DashcamInvestigator.desktop`.

### 6.4 [M13] Drop bandit `-ll` and triage
- **File**: `.github/workflows/ci.yml:92`
- **Steps**: Remove `-ll`. Run locally; suppress per-finding with
  `# nosec` + justification or fix. Aim for zero findings.

### 6.5 [M14] Soften `pip-audit`
- **File**: `.github/workflows/ci.yml:94-95`
- **Steps**: Add `continue-on-error: true`, or move to a scheduled
  workflow.

### 6.6 [M15] Capture early-startup errors in frozen builds
- **File**: `dashcam_investigator/__main__.py`
- **Steps**: Wrap the `if __name__ == "__main__":` block in a
  `try/except` that writes the traceback to
  `_resolve_log_dir() / "startup-error.log"` before re-raising.

### 6.7 [L18] Bump release action
- **File**: `.github/workflows/ci.yml:191`
- **Steps**: `softprops/action-gh-release@v1` → `@v2`.

### Phase 6 checkpoint
```bash
# CI must be green on Ubuntu, Windows, macOS for the test job.
desktop-file-validate packaging/linux/DashcamInvestigator.desktop
git add -A
git commit -m "ci: cross-platform tests, honest coverage, packaging fixes"
git push
```

---

## Phase 7 — Cleanup & Documentation

### 7.1 [M16] README dependency table
- **File**: `README.md:64-78`
- **Steps**: Delete the table or rewrite it to mirror
  `[project].dependencies`. Don't pin micro versions in prose.

### 7.2 [M17] Document `build_appimage.sh` prerequisite
- **File**: `README.md` "Linux: tar.gz and AppImage" section
- **Steps**: Add an explicit "first run pyinstaller" sentence above the
  AppImage step.

### 7.3 [L1, L2] Resolve `gui/QtNewProjectDialog.py`
- **Steps** (after 5.2 the file is hand-edited):
  1. Delete the "auto-generated, do not edit" header.
  2. Replace `from PySide6.* import *` with explicit imports.
  3. Remove `setGeometry` calls in favour of layouts (HiDPI).

### 7.4 [L4] Document the `_exiftool_path` cache
- **File**: `core/extract_metadata.py:13-18`
- **Steps**: Add a one-line comment noting the cache and that tests
  must clear it (already handled in `tests/conftest.py:13`).

### 7.5 [L6] Stop shadowing `min`
- **File**: `gui/app.py:142, 153`
- **Steps**: Rename to `mins, secs = convert_to_seconds(...)`.

### 7.6 [L9] Absolute imports
- **File**: `gui/new_project_class.py:5`
- **Steps**:
  `from dashcam_investigator.gui.QtNewProjectDialog import Ui_Dialog`.

### 7.7 [L10] pyproject metadata
- **File**: `pyproject.toml`
- **Steps**: Add:
  ```toml
  [project]
  license = {file = "LICENSE"}
  classifiers = [
      "Operating System :: OS Independent",
      "Programming Language :: Python :: 3",
      "Topic :: Multimedia :: Video",
  ]

  [build-system]
  requires = ["hatchling"]
  build-backend = "hatchling.build"
  ```

### 7.8 [L11] Fix coverage `exclude_lines` regex
- **File**: `pyproject.toml:70-73`
- **Steps**: Replace `if __name__ == .__main__.:` with
  `if __name__ == ['"]__main__['"]:`.

### 7.9 [L12] Drop unused logger
- **File**: `dashcam_investigator/__main__.py:53`
- **Steps**: Delete the unused assignment.

### 7.10 [L14] Single-walk for `process_files`
- **Files**: `core/get_file_count.py`, `core/process_files.py`
- **Steps**: Inline `get_file_count` into `process_files`; emit
  progress as `(processed, total)` from one `rglob`. Delete
  `get_file_count.py` and its test.

### 7.11 [L15] Move `data_transformers.disable_max_rows()` to module top
- **File**: `core/output_generator.py:64`

### 7.12 [L17] Prune unused conftest fixtures
- **File**: `tests/conftest.py:43-138`
- **Steps**: Delete fixtures not referenced in any test file
  (`grep -rn fixture_name tests/`).

### Phase 7 checkpoint
```bash
uv run pytest -v
uv run ruff check . && uv run black --check .
git add -A
git commit -m "chore: cleanup, docs, metadata"
git push
```

---

## Phase 8 — Final Verification & Release Prep

### 8.1 Full automated suite
```bash
uv run pytest -v --cov-report=term-missing
uv run ruff check .
uv run black --check .
uv run bandit -r dashcam_investigator
uv run pip-audit
```
All must pass.

### 8.2 Manual smoke (Linux, macOS, Windows ideally)
1. `uv run python -m dashcam_investigator`.
2. New project, point at a small dir with one MP4 that has GPS metadata.
3. Watch progress dialog → Cancel button is shown.
4. After processing: sidebar populated, click a video, map renders,
   speed graph renders, metadata table populates.
5. Edit notes, Ctrl+S → toast appears.
6. Flag the video, generate report. Open the report file in a real
   browser → fully self-contained.
7. Re-open the project from disk → state restored.
8. Close the app while processing a large dir → confirmation dialog,
   clean exit.

### 8.3 Build verification
```bash
uv run pyinstaller --noconfirm --clean DashcamInvestigator.spec
./dist/DashcamInvestigator/DashcamInvestigator    # Linux/macOS
# or dist\DashcamInvestigator\DashcamInvestigator.exe on Windows
./packaging/linux/build_appimage.sh
./dist/DashcamInvestigator-x86_64.AppImage
desktop-file-validate packaging/linux/DashcamInvestigator.desktop
```

### 8.4 Adversarial check
```python
# scratch only — not committed
from dashcam_investigator.core.generate_report import _safe_filename
assert ".." not in _safe_filename("../../etc/passwd")
assert "/" not in _safe_filename("a/b")
```
Plus the popup-escaping test from 2.2.

### 8.5 Push & PR
```bash
git push -u origin claude/code-review-analysis-hEYXZ
# Open a PR. Summary references this plan and which review IDs are
# addressed per commit.
```

---

## Tracking matrix

| Phase | IDs covered                                              | Estimate    |
|-------|----------------------------------------------------------|-------------|
| 0     | —                                                        | 30 min      |
| 1     | C1, C5, H1, H2, H5, M1, M12, L3, L5                      | half day    |
| 2     | C3, C4                                                   | 2 hours     |
| 3     | C6, H10                                                  | 3 hours     |
| 4     | C2, H3, H4, H6, M6                                       | half day    |
| 5     | H7, H8, H9, M5, M7, M8, L1                               | 2 hours     |
| 6     | C7, H11, H12, M13, M14, M15, L18                         | half day    |
| 7     | L2, L4, L6, L9, L10, L11, L12, L14, L15, L17, M16, M17   | 2 hours     |
| 8     | —                                                        | 1 hour      |

**Total**: ~3 days of focused engineering. Each phase ships
independently.
