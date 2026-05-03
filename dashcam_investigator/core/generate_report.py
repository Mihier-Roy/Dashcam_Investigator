"""
Render the standalone HTML investigation report.

The report shares Jinja templates and CSS with the in-app UI so the two
look like one product. CSS and SVG icons are inlined into the rendered
HTML; map / speed-graph HTMLs stay as separate files referenced via
relative iframe srcs (the user normally ships the whole project dir).

Public surface — preserved across the rewrite:
    generate_report(project_object: ProjectStructure) -> Path
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

import pandas as pd

from dashcam_investigator.gui.web.renderer import render
from dashcam_investigator.project_manager.project_datatypes import (
    FileAttributes,
    ProjectStructure,
)

logger = logging.getLogger(__name__)


def generate_report(project_object: ProjectStructure) -> Path:
    """Render an HTML report covering every flagged video and return its path."""
    flagged = [v for v in project_object.video_files if v.flagged]
    case = project_object.project_info

    output_file = Path(
        case.project_directory,
        "Reports",
        f"{case.case_name}_report.html",
    )
    output_file.parent.mkdir(parents=True, exist_ok=True)

    video_info = {v.name: _collect_info(v) for v in flagged}
    video_iframes = {
        v.name: _collect_iframes(v, output_file.parent) for v in flagged
    }

    logger.debug("Rendering report for %d flagged video(s)", len(flagged))
    html = render(
        "report.html",
        case=case,
        flagged=flagged,
        video_info=video_info,
        video_iframes=video_iframes,
        generated_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
        app=False,
    )

    logger.debug("Writing report -> %s", output_file)
    output_file.write_text(html, encoding="utf-8")
    logger.debug("Report generation complete")
    return output_file


# --- helpers ---------------------------------------------------------
def _collect_info(video: FileAttributes) -> dict[str, str]:
    """Pull headline metadata fields out of the video's CSV, if present."""
    if not video.meta_files or len(video.meta_files) < 2:
        return {}
    csv_path = Path(video.meta_files[1])
    if not csv_path.is_file():
        logger.debug("Metadata CSV missing for report: %s", csv_path)
        return {}
    try:
        df = pd.read_csv(csv_path)
    except Exception as exc:  # noqa: BLE001 — surface as empty info section
        logger.warning("Failed to read metadata CSV %s: %s", csv_path, exc)
        return {}
    if df.empty:
        return {}

    row = df.iloc[0].to_dict()
    info: dict[str, str] = {}
    if "CreateDate" in row:
        info["Create date"] = _fmt(row["CreateDate"])
    if "Duration" in row:
        info["Duration"] = _fmt(row["Duration"])
    if "Format" in row or "Information" in row:
        device = " ".join(filter(None, (_fmt(row.get("Format")), _fmt(row.get("Information")))))
        if device.strip():
            info["Device"] = device.strip()
    return info


def _collect_iframes(video: FileAttributes, report_dir: Path) -> dict[str, str]:
    """Compute relative iframe URLs for the map (output_files[0]) and graph ([1])."""
    iframes: dict[str, str] = {}
    if video.output_files and len(video.output_files) > 0:
        iframes["map"] = _rel_url(video.output_files[0], report_dir)
    if video.output_files and len(video.output_files) > 1:
        iframes["graph"] = _rel_url(video.output_files[1], report_dir)
    return iframes


def _rel_url(target: str, base: Path) -> str:
    """Return a Posix-style URL pointing at `target` relative to `base`."""
    try:
        rel = os.path.relpath(target, str(base))
    except ValueError:
        # Different drives on Windows — fall back to the absolute path.
        return Path(target).as_posix()
    return Path(rel).as_posix()


def _fmt(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value)
