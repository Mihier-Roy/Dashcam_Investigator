"""Smoke tests for map_functions.py.

No prior coverage existed for this module (OutputGenerator is always
mocked in test_process_files.py). These exercise the real folium/branca
pipeline end to end with hand-built GPS data, no exiftool required.
"""

from datetime import datetime

import gpxpy
import pandas as pd
import pytest

from dashcam_investigator.core.generate_dataframe import (
    MetaDataFrames,
    make_speed_dataframe,
)
from dashcam_investigator.core.map_functions import (
    add_data_to_map,
    generate_speed_colour_map,
    initialise_map,
)


@pytest.fixture
def meta_handler(temp_dir):
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

    handler = MetaDataFrames(
        video_name="route.mp4",
        video_meta_files={"gpx": str(gpx_path), "csv": str(csv_path)},
    )
    handler.convert_to_datetime()
    handler.add_speed()
    handler.add_label_for_speed_chart()
    return handler


def test_add_data_to_map_populates_feature_groups(meta_handler):
    """The full add_data_to_map path (routeline + start marker + speed
    line) must run without raising and actually add children to each
    feature group -- regression coverage for the inlined
    add_routeline_to_map/add_start_marker_to_map/add_speedline_to_map.
    """
    mean_point = (
        meta_handler.gps_df["Latitude"].mean(),
        meta_handler.gps_df["Longitude"].mean(),
    )
    mappy = initialise_map(mean_point)
    speed_data = make_speed_dataframe(meta_handler)
    colour_map = generate_speed_colour_map(speed_data)
    mappy.canvas.add_child(colour_map)

    add_data_to_map(
        meta_handler,
        mappy.routelines,
        mappy.start_markers,
        mappy.speed_lines,
        "blue",
        colour_map,
    )

    assert len(mappy.routelines._children) > 0
    assert len(mappy.start_markers._children) > 0
    assert len(mappy.speed_lines._children) > 0


def test_generate_speed_colour_map_scales_to_data_range(meta_handler):
    speed_data = make_speed_dataframe(meta_handler)
    colour_map = generate_speed_colour_map(speed_data)

    assert colour_map.vmin == pytest.approx(speed_data["Speed"].min())
    assert colour_map.vmax == pytest.approx(speed_data["Speed"].max())


def test_make_speed_dataframe_type(meta_handler):
    assert isinstance(make_speed_dataframe(meta_handler), pd.DataFrame)
