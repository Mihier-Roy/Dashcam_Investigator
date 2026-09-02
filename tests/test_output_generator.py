"""Smoke tests for output_generator.py.

No prior coverage existed for this module (it's always mocked in
test_process_files.py). These exercise the real folium/altair pipeline
end to end with hand-built GPS data, no exiftool required.
"""

from datetime import datetime
from pathlib import Path

import gpxpy
import pytest
from altair import Chart

from dashcam_investigator.core.output_generator import OutputGenerator
from dashcam_investigator.project_manager.project_datatypes import FileAttributes


@pytest.fixture
def file_attributes(temp_dir):
    gpx = gpxpy.gpx.GPX()
    track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(track)
    segment = gpxpy.gpx.GPXTrackSegment()
    track.segments.append(segment)
    for i in range(4):
        segment.points.append(
            gpxpy.gpx.GPXTrackPoint(
                latitude=37.7749 + i * 0.001,
                longitude=-122.4194 + i * 0.001,
                elevation=10.0,
                time=datetime(2024, 1, 15, 14, 30, i * 10),
            )
        )
    gpx_path = temp_dir / "route.gpx"
    gpx_path.write_text(gpx.to_xml())

    csv_path = temp_dir / "route_fileinfo.csv"
    csv_path.write_text(
        "SourceFile,FileType,FileSize,MIMEType,CreateDate,Duration,Format,Information\n"
        "/tmp/video.mp4,MP4,10485760,video/mp4,15-01-2024 14:30:00,00:05:30,MPEG-4,Test"
    )

    return FileAttributes(
        Path("/tmp/video.mp4"),
        name="video.mp4",
        meta_files={"gpx": str(gpx_path), "csv": str(csv_path)},
    )


def test_generate_map_writes_html(file_attributes, temp_dir):
    output_path = temp_dir / "map.html"
    OutputGenerator().generate_map(file_attributes, output_path)

    assert output_path.is_file()
    html = output_path.read_text()
    assert "leaflet" in html.lower()
    assert "openstreetmap" in html.lower()


def test_generate_speed_chart_writes_html(file_attributes, temp_dir):
    gen = OutputGenerator()
    gen.generate_map(file_attributes, temp_dir / "map.html")  # populates self.speed_data

    output_path = temp_dir / "speed.html"
    chart = gen.generate_speed_chart(output_path)

    assert isinstance(chart, Chart)
    assert output_path.is_file()
