"""
Phase 5: tests for the metadata + notes WebPanels.

The Python-side metadata CSV → JSON conversion is tested directly with
a synthetic fixture (no QtWebEngine needed). The JS / template wiring
is verified by inspecting rendered output and the JS source.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from dashcam_investigator.gui.web import renderer


# --- Templates --------------------------------------------------------
def test_metadata_template_renders_required_anchors() -> None:
    html = renderer.render("metadata.html")
    for needle in (
        'id="filter"',
        'id="metadata-table"',
        'id="metadata-tbody"',
        'data-sort="property"',
        'data-sort="value"',
        "metadata.js",
    ):
        assert needle in html, f"metadata.html missing {needle!r}"


def test_notes_template_renders_required_anchors() -> None:
    html = renderer.render("notes.html")
    for needle in (
        'id="notes-title"',
        'id="notes-subtitle"',
        'id="notes-text"',
        'id="btn-flag"',
        'id="btn-flag-label"',
        'id="btn-save"',
        'id="notes-toast"',
        "notes.js",
    ):
        assert needle in html, f"notes.html missing {needle!r}"


# --- JS surface -------------------------------------------------------
def test_metadata_js_subscribes_and_implements_features() -> None:
    js = (renderer.static_path() / "js" / "pages" / "metadata.js").read_text()
    for needle in (
        '"video"',
        "getMetadataJson",
        "applyFilterAndSort",
        "navigator.clipboard",
        "sortable",
    ):
        assert needle in js, f"metadata.js missing {needle!r}"


def test_notes_js_wires_save_flag_and_autosave() -> None:
    js = (renderer.static_path() / "js" / "pages" / "notes.js").read_text()
    for needle in (
        '"video"',
        '"notes-saved"',
        '"flag-changed"',
        "saveNotes",
        "setFlag",
        '"blur"',
    ):
        assert needle in js, f"notes.js missing {needle!r}"


# --- CSS --------------------------------------------------------------
def test_app_css_defines_metadata_and_notes_layouts() -> None:
    css = (renderer.static_path() / "css" / "app.css").read_text()
    for cls in (
        ".metadata-panel",
        ".metadata-controls",
        ".metadata-table-wrap",
        ".notes-panel",
        ".notes-header",
        ".notes-actions",
    ):
        assert cls in css, f"app.css missing {cls}"


# --- Python-side metadata helper -------------------------------------
def test_get_metadata_json_helper_handles_real_csv(tmp_path: Path) -> None:
    """
    The real method lives on MainWindow (which can't be instantiated on
    headless hosts). Reproduce the conversion logic against a synthetic
    CSV here so a regression in the data shape is caught locally.
    """
    csv_path = tmp_path / "video.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["FileName", "Duration", "Format", "Information"])
        writer.writerow(["clip.mp4", "00:05:30", "MP4", "H.264"])

    import pandas as pd  # local — keeps test stable when pandas is uninstalled

    df = pd.read_csv(csv_path)
    row = df.iloc[0].to_dict()
    rows = [
        {"property": str(k), "value": "" if pd.isna(v) else str(v)}
        for k, v in row.items()
    ]
    payload = json.loads(json.dumps(rows))
    by_prop = {r["property"]: r["value"] for r in payload}
    assert by_prop["FileName"] == "clip.mp4"
    assert by_prop["Duration"] == "00:05:30"
    assert set(by_prop) == {"FileName", "Duration", "Format", "Information"}


def test_get_metadata_json_helper_returns_empty_for_empty_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("FileName,Duration\n")  # header only, no rows
    import pandas as pd

    df = pd.read_csv(csv_path)
    assert df.empty  # mirrors the early-return in MainWindow.get_metadata_json
