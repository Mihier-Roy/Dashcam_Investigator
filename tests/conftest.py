"""Pytest configuration and shared fixtures."""

import json
import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_gps_data() -> dict:
    """Sample GPS data extracted from ExifTool."""
    return {
        "GPSLatitude": 37.7749,
        "GPSLongitude": -122.4194,
        "GPSSpeed": 25.5,
        "GPSDateTime": "2024:01:15 14:30:45",
        "GPSAltitude": 10.5,
    }


@pytest.fixture
def sample_file_metadata() -> dict:
    """Sample file metadata from ExifTool."""
    return {
        "FileName": "test_video.mp4",
        "FileSize": "10485760",
        "FileType": "MP4",
        "MIMEType": "video/mp4",
        "Duration": "00:05:30",
        "ImageWidth": 1920,
        "ImageHeight": 1080,
        "VideoCodec": "H.264",
        "CreateDate": "2024:01:15 14:30:00",
    }


@pytest.fixture
def sample_gpx_xml() -> str:
    """Sample GPX XML data."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.0">
  <trk>
    <trkseg>
      <trkpt lat="37.7749" lon="-122.4194">
        <ele>10.5</ele>
        <time>2024-01-15T14:30:45Z</time>
        <speed>25.5</speed>
      </trkpt>
      <trkpt lat="37.7750" lon="-122.4195">
        <ele>11.0</ele>
        <time>2024-01-15T14:30:50Z</time>
        <speed>26.0</speed>
      </trkpt>
      <trkpt lat="37.7751" lon="-122.4196">
        <ele>11.5</ele>
        <time>2024-01-15T14:30:55Z</time>
        <speed>26.5</speed>
      </trkpt>
    </trkseg>
  </trk>
</gpx>"""


@pytest.fixture
def sample_project_info_dict() -> dict:
    """Sample project info dictionary."""
    return {
        "project_name": "Test Project",
        "project_path": "/tmp/test_project",
        "case_number": "CASE-2024-001",
        "description": "Test forensic investigation",
        "investigator": "John Doe",
        "flagged_videos": [],
    }


@pytest.fixture
def sample_file_attributes_dict() -> dict:
    """Sample file attributes dictionary."""
    return {
        "file_path": "/tmp/test_video.mp4",
        "file_hash": "abc123def456",
        "file_meta": {"FileName": "test_video.mp4", "FileSize": "1048576"},
        "gps_meta": {"GPSLatitude": 37.7749, "GPSLongitude": -122.4194},
        "notes": "Sample video file",
        "flagged": False,
    }


@pytest.fixture
def mock_exiftool_output() -> str:
    """Mock ExifTool JSON output."""
    return json.dumps(
        [
            {
                "SourceFile": "/tmp/test_video.mp4",
                "FileName": "test_video.mp4",
                "FileSize": "10 MB",
                "GPSLatitude": 37.7749,
                "GPSLongitude": -122.4194,
                "GPSSpeed": 25.5,
                "CreateDate": "2024:01:15 14:30:00",
            }
        ]
    )
