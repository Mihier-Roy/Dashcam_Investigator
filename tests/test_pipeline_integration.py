"""
Integration tests for the file→project→serialize→load pipeline.

These tests exercise multiple modules together to catch wiring bugs that
unit tests with mocked internals cannot surface.
"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import gpxpy
import gpxpy.gpx
import pytest

from dashcam_investigator.exceptions import ExifToolError, GPSParseError
from dashcam_investigator.project_manager.project_datatypes import (
    FileAttributes,
    ProjectInfo,
    ProjectStructure,
)
from dashcam_investigator.utils.custom_json_functions import (
    ProjectEncoder,
    project_decoder,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_gpx_content(num_points: int = 3) -> str:
    gpx = gpxpy.gpx.GPX()
    track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(track)
    segment = gpxpy.gpx.GPXTrackSegment()
    track.segments.append(segment)
    for i in range(num_points):
        segment.points.append(
            gpxpy.gpx.GPXTrackPoint(
                latitude=51.5 + i * 0.001,
                longitude=-0.1 + i * 0.001,
                elevation=20.0 + i,
                time=datetime(2024, 6, 1, 12, 0, i * 10),
            )
        )
    return gpx.to_xml()


def _make_csv_content() -> str:
    return (
        "SourceFile,FileType,FileSize,MIMEType,CreateDate,Duration,Format,Information\n"
        "/tmp/video.mp4,MP4,10485760,video/mp4,01-06-2024 12:00:00,00:03:00,MPEG-4,Test\n"
    )


def _make_project(tmp_path: Path) -> tuple[Path, ProjectStructure]:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "project"
    input_dir.mkdir()
    output_dir.mkdir()
    for subdir in ("Metadata", "Maps", "Graphs", "Reports"):
        (output_dir / subdir).mkdir()

    project_info = ProjectInfo(
        input_dir=input_dir,
        output_dir=output_dir,
        case_name="Integration Test",
        investigator_name="Tester",
        report_path="",
    )
    project = ProjectStructure(
        projectInfo=project_info,
        video_files=[],
        image_files=[],
        other_files=[],
    )
    return input_dir, project


# ---------------------------------------------------------------------------
# 1. JSON round-trip: serialize a project and reload it unchanged
# ---------------------------------------------------------------------------


class TestProjectSerializationRoundTrip:

    def test_empty_project_round_trips(self, tmp_path):
        _, project = _make_project(tmp_path)

        serialized = json.dumps(project, cls=ProjectEncoder, indent=2)
        loaded = json.loads(serialized, object_hook=project_decoder)

        assert isinstance(loaded, ProjectStructure)
        assert loaded.tool_name == project.tool_name
        assert loaded.project_info.case_name == "Integration Test"
        assert loaded.video_files == []

    def test_project_with_videos_round_trips(self, tmp_path):
        input_dir, project = _make_project(tmp_path)

        video_file = input_dir / "clip.mp4"
        video_file.write_text("fake")
        fa = FileAttributes(
            file_path=video_file,
            sha256_hash="deadbeef",
            meta_files={"gpx": "/meta/clip.gpx", "csv": "/meta/clip.csv"},
            output_files=["/maps/clip_map.html"],
            flagged=True,
            notes="important",
        )
        project.video_files.append(fa)

        serialized = json.dumps(project, cls=ProjectEncoder, indent=2)
        loaded = json.loads(serialized, object_hook=project_decoder)

        assert len(loaded.video_files) == 1
        v = loaded.video_files[0]
        assert v.name == "clip.mp4"
        assert v.sha256_hash == "deadbeef"
        assert v.meta_files == {"gpx": "/meta/clip.gpx", "csv": "/meta/clip.csv"}
        assert v.flagged is True
        assert v.notes == "important"

    def test_migration_shim_applied_during_load(self, tmp_path):
        """Old project files store meta_files as a list; confirm migration on load."""
        input_dir, project = _make_project(tmp_path)

        video_file = input_dir / "legacy.mp4"
        video_file.write_text("fake")

        raw = {
            "tool_name": "Dashcam Investigator",
            "project_info": project.project_info.to_dict(),
            "video_files": [
                {
                    "file_path": str(video_file),
                    "name": "legacy.mp4",
                    "type": ".mp4",
                    "sha256_hash": "abc",
                    "meta_files": ["/old/legacy.gpx", "/old/legacy.csv"],
                    "output_files": [],
                    "flagged": False,
                    "notes": "",
                }
            ],
            "image_files": [],
            "other_files": [],
        }

        loaded = json.loads(json.dumps(raw), object_hook=project_decoder)
        assert loaded.video_files[0].meta_files == {
            "gpx": "/old/legacy.gpx",
            "csv": "/old/legacy.csv",
        }

    def test_tool_name_typo_not_serialized(self, tmp_path):
        _, project = _make_project(tmp_path)
        serialized = json.dumps(project, cls=ProjectEncoder)
        assert "Dascam" not in serialized
        assert "Dashcam" in serialized


# ---------------------------------------------------------------------------
# 2. MetaDataFrames: GPX → DataFrame pipeline with real files
# ---------------------------------------------------------------------------


class TestGPXToDataFramePipeline:

    def test_valid_gpx_produces_correct_dataframe(self, tmp_path):
        from dashcam_investigator.core.generate_dataframe import MetaDataFrames

        gpx_path = tmp_path / "clip.gpx"
        csv_path = tmp_path / "clip_fileinfo.csv"
        gpx_path.write_text(_make_gpx_content(num_points=5))
        csv_path.write_text(_make_csv_content())

        meta = MetaDataFrames(
            video_name="clip.mp4",
            video_meta_files={"gpx": str(gpx_path), "csv": str(csv_path)},
        )

        assert len(meta.gps_df) == 5
        assert len(meta.points) == 5
        assert all(isinstance(p, tuple) and len(p) == 2 for p in meta.points)
        assert list(meta.gps_df.columns) == [
            "Longitude",
            "Latitude",
            "Altitude",
            "DateTime",
            "Speed",
        ]

    def test_empty_gpx_raises_gps_parse_error(self, tmp_path):
        from dashcam_investigator.core.generate_dataframe import MetaDataFrames

        gpx_path = tmp_path / "empty.gpx"
        csv_path = tmp_path / "empty_fileinfo.csv"
        gpx_path.write_text('<?xml version="1.0"?><gpx version="1.1"></gpx>')
        csv_path.write_text(_make_csv_content())

        with pytest.raises(GPSParseError, match="no tracks or segments"):
            MetaDataFrames(
                video_name="empty.mp4",
                video_meta_files={"gpx": str(gpx_path), "csv": str(csv_path)},
            )

    def test_dataframe_add_speed_and_label(self, tmp_path):
        from dashcam_investigator.core.generate_dataframe import MetaDataFrames

        gpx_path = tmp_path / "clip.gpx"
        csv_path = tmp_path / "clip_fileinfo.csv"
        gpx_path.write_text(_make_gpx_content(num_points=4))
        csv_path.write_text(_make_csv_content())

        meta = MetaDataFrames(
            video_name="clip.mp4",
            video_meta_files={"gpx": str(gpx_path), "csv": str(csv_path)},
        )
        meta.add_label_for_speed_chart()
        meta.add_speed()

        assert "DataSource" in meta.gps_df.columns
        assert "AverageSpeed" in meta.file_info_df.columns
        assert "MaxSpeed" in meta.file_info_df.columns


# ---------------------------------------------------------------------------
# 3. ExifTool subprocess integration
# ---------------------------------------------------------------------------


class TestExifToolSubprocess:

    def _make_run_result(self, returncode=0, stderr=b""):
        r = MagicMock()
        r.returncode = returncode
        r.stderr = stderr
        return r

    @patch("dashcam_investigator.core.extract_metadata.subprocess.run")
    @patch(
        "dashcam_investigator.core.extract_metadata.shutil.which",
        return_value="/usr/bin/exiftool",
    )
    @patch(
        "dashcam_investigator.core.process_files.filetype.guess_mime",
        return_value="video/mp4",
    )
    def test_process_files_populates_meta_files_dict(
        self, mock_filetype, mock_which, mock_run, tmp_path
    ):
        """process_files populates meta_files as {"gpx": ..., "csv": ...}."""
        from dashcam_investigator.core.process_files import process_files

        mock_run.return_value = self._make_run_result()

        input_dir, project = _make_project(tmp_path)
        video_file = input_dir / "clip.mp4"
        video_file.write_text("fake video")

        # Write dummy GPX/CSV so MetaDataFrames constructor doesn't crash
        meta_dir = project.project_info.project_directory / "Metadata"
        gpx_out = meta_dir / "clip.gpx"
        csv_out = meta_dir / "clip_fileinfo.csv"
        gpx_out.write_text(_make_gpx_content())
        csv_out.write_text(_make_csv_content())

        with patch(
            "dashcam_investigator.core.process_files.OutputGenerator"
        ) as mock_gen_cls:
            mock_gen = MagicMock()
            mock_gen_cls.return_value = mock_gen
            progress_cb = MagicMock()
            progress_cb.emit = MagicMock()
            status_cb = MagicMock()
            status_cb.emit = MagicMock()

            result = process_files(
                input_dir, project, progress_cb, status_callback=status_cb
            )

        assert result.project_info.num_videos == 1
        video = result.video_files[0]
        assert isinstance(video.meta_files, dict)
        assert "gpx" in video.meta_files
        assert "csv" in video.meta_files

    @patch("dashcam_investigator.core.extract_metadata.shutil.which", return_value=None)
    def test_exiftool_missing_raises_exiftool_error(self, mock_which, tmp_path):
        from dashcam_investigator.core.extract_metadata import process_gps_data

        video = tmp_path / "clip.mp4"
        video.write_text("x")
        with pytest.raises(ExifToolError, match="not found on PATH"):
            process_gps_data(video, tmp_path)
