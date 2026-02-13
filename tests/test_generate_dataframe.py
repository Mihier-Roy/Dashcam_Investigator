"""Tests for GPS data processing and dataframe generation."""

from datetime import datetime

import gpxpy
import pandas as pd
import pytest

from dashcam_investigator.core.generate_dataframe import (
    MetaDataFrames,
    make_speed_dataframe,
)


class TestMetaDataFrames:
    """Test cases for MetaDataFrames class."""

    @pytest.fixture
    def create_gpx_file(self, temp_dir):
        """Helper fixture to create a GPX file."""

        def _create_gpx(filename: str, num_points: int = 3):
            gpx = gpxpy.gpx.GPX()
            track = gpxpy.gpx.GPXTrack()
            gpx.tracks.append(track)
            segment = gpxpy.gpx.GPXTrackSegment()
            track.segments.append(segment)

            # Create test points
            base_lat = 37.7749
            base_lon = -122.4194
            for i in range(num_points):
                point = gpxpy.gpx.GPXTrackPoint(
                    latitude=base_lat + i * 0.0001,
                    longitude=base_lon + i * 0.0001,
                    elevation=10.0 + i,
                    time=datetime(2024, 1, 15, 14, 30, i),
                )
                segment.points.append(point)

            gpx_path = temp_dir / filename
            gpx_path.write_text(gpx.to_xml())
            return gpx_path

        return _create_gpx

    @pytest.fixture
    def create_csv_file(self, temp_dir):
        """Helper fixture to create a CSV file."""

        def _create_csv(filename: str):
            csv_content = """SourceFile,FileType,FileSize,MIMEType,CreateDate,Duration,Format,Information
/tmp/video.mp4,MP4,10485760,video/mp4,15-01-2024 14:30:00,00:05:30,MPEG-4,Test video"""
            csv_path = temp_dir / filename
            csv_path.write_text(csv_content)
            return csv_path

        return _create_csv

    def test_init_basic(self, create_gpx_file, create_csv_file, temp_dir):
        """Test basic initialization of MetaDataFrames."""
        gpx_file = create_gpx_file("test.gpx")
        csv_file = create_csv_file("test_fileinfo.csv")

        meta = MetaDataFrames(
            video_name="test_video", video_meta_files=[str(gpx_file), str(csv_file)]
        )

        assert meta.video_name == "test_video"
        assert isinstance(meta.gps_df, pd.DataFrame)
        assert isinstance(meta.file_info_df, pd.DataFrame)
        assert isinstance(meta.points, list)

    def test_gps_dataframe_structure(self, create_gpx_file, create_csv_file):
        """Test that GPS dataframe has correct columns."""
        gpx_file = create_gpx_file("test.gpx")
        csv_file = create_csv_file("test_fileinfo.csv")

        meta = MetaDataFrames(
            video_name="test", video_meta_files=[str(gpx_file), str(csv_file)]
        )

        expected_columns = ["Longitude", "Latitude", "Altitude", "DateTime", "Speed"]
        assert list(meta.gps_df.columns) == expected_columns

    def test_gps_dataframe_content(self, create_gpx_file, create_csv_file):
        """Test that GPS dataframe contains correct data."""
        gpx_file = create_gpx_file("test.gpx", num_points=3)
        csv_file = create_csv_file("test_fileinfo.csv")

        meta = MetaDataFrames(
            video_name="test", video_meta_files=[str(gpx_file), str(csv_file)]
        )

        # Should have 3 points
        assert len(meta.gps_df) == 3

        # Check first point coordinates
        assert abs(meta.gps_df.iloc[0]["Latitude"] - 37.7749) < 0.0001
        assert abs(meta.gps_df.iloc[0]["Longitude"] - (-122.4194)) < 0.0001

    def test_points_list_extraction(self, create_gpx_file, create_csv_file):
        """Test that route points are correctly extracted."""
        gpx_file = create_gpx_file("test.gpx", num_points=5)
        csv_file = create_csv_file("test_fileinfo.csv")

        meta = MetaDataFrames(
            video_name="test", video_meta_files=[str(gpx_file), str(csv_file)]
        )

        # Should have 5 points as tuples
        assert len(meta.points) == 5
        assert all(isinstance(p, tuple) for p in meta.points)
        assert all(len(p) == 2 for p in meta.points)

        # Points should be (latitude, longitude)
        first_point = meta.points[0]
        assert abs(first_point[0] - 37.7749) < 0.0001
        assert abs(first_point[1] - (-122.4194)) < 0.0001

    def test_add_label_for_speed_chart(self, create_gpx_file, create_csv_file):
        """Test adding data source label for speed chart."""
        gpx_file = create_gpx_file("test.gpx", num_points=3)
        csv_file = create_csv_file("test_fileinfo.csv")

        meta = MetaDataFrames(
            video_name="test", video_meta_files=[str(gpx_file), str(csv_file)]
        )
        meta.add_label_for_speed_chart()

        assert "DataSource" in meta.gps_df.columns
        assert len(meta.gps_df["DataSource"]) == 3
        assert all(
            label == "Extracted metadata using exiftool"
            for label in meta.gps_df["DataSource"]
        )

    def test_add_speed(self, create_gpx_file, create_csv_file, temp_dir):
        """Test calculating and adding speed statistics."""
        # Create GPX with known speeds
        gpx = gpxpy.gpx.GPX()
        track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(track)
        segment = gpxpy.gpx.GPXTrackSegment()
        track.segments.append(segment)

        # Add points
        for i in range(3):
            point = gpxpy.gpx.GPXTrackPoint(
                latitude=37.7749 + i * 0.001,
                longitude=-122.4194 + i * 0.001,
                elevation=10.0,
                time=datetime(2024, 1, 15, 14, 30, i * 10),
            )
            segment.points.append(point)

        gpx_path = temp_dir / "speed_test.gpx"
        gpx_path.write_text(gpx.to_xml())
        csv_file = create_csv_file("speed_test_fileinfo.csv")

        meta = MetaDataFrames(
            video_name="test", video_meta_files=[str(gpx_path), str(csv_file)]
        )
        meta.add_speed()

        assert "AverageSpeed" in meta.file_info_df.columns
        assert "MaxSpeed" in meta.file_info_df.columns
        # Values should be numeric
        assert isinstance(meta.file_info_df["AverageSpeed"].iloc[0], (int, float))
        assert isinstance(meta.file_info_df["MaxSpeed"].iloc[0], (int, float))

    def test_process_gpx_to_df_with_elevation(self, create_gpx_file, create_csv_file):
        """Test that elevation data is correctly extracted."""
        gpx_file = create_gpx_file("test.gpx", num_points=3)
        csv_file = create_csv_file("test_fileinfo.csv")

        meta = MetaDataFrames(
            video_name="test", video_meta_files=[str(gpx_file), str(csv_file)]
        )

        assert "Altitude" in meta.gps_df.columns
        # Elevations should be 10.0, 11.0, 12.0
        assert abs(meta.gps_df.iloc[0]["Altitude"] - 10.0) < 0.1
        assert abs(meta.gps_df.iloc[1]["Altitude"] - 11.0) < 0.1
        assert abs(meta.gps_df.iloc[2]["Altitude"] - 12.0) < 0.1


class TestMakeSpeedDataframe:
    """Test cases for make_speed_dataframe function."""

    @pytest.fixture
    def create_meta_handler(self, temp_dir):
        """Create a mock MetaDataFrames handler."""

        def _create(num_points=3):
            # Create GPX file
            gpx = gpxpy.gpx.GPX()
            track = gpxpy.gpx.GPXTrack()
            gpx.tracks.append(track)
            segment = gpxpy.gpx.GPXTrackSegment()
            track.segments.append(segment)

            for i in range(num_points):
                point = gpxpy.gpx.GPXTrackPoint(
                    latitude=37.7749 + i * 0.001,
                    longitude=-122.4194 + i * 0.001,
                    elevation=10.0,
                    time=datetime(2024, 1, 15, 14, 30, i * 10),
                )
                segment.points.append(point)

            gpx_path = temp_dir / "test.gpx"
            gpx_path.write_text(gpx.to_xml())

            # Create CSV file
            csv_content = """SourceFile,FileType,FileSize,MIMEType,CreateDate,Duration,Format,Information
/tmp/video.mp4,MP4,10485760,video/mp4,15-01-2024 14:30:00,00:05:30,MPEG-4,Test"""
            csv_path = temp_dir / "test_fileinfo.csv"
            csv_path.write_text(csv_content)

            meta = MetaDataFrames(
                video_name="test", video_meta_files=[str(gpx_path), str(csv_path)]
            )
            meta.add_label_for_speed_chart()
            return meta

        return _create

    def test_make_speed_dataframe_basic(self, create_meta_handler):
        """Test basic speed dataframe creation."""
        meta = create_meta_handler(num_points=5)
        speed_df = make_speed_dataframe(meta)

        assert isinstance(speed_df, pd.DataFrame)
        assert len(speed_df) == 5

    def test_make_speed_dataframe_columns(self, create_meta_handler):
        """Test that speed dataframe has correct columns."""
        meta = create_meta_handler()
        speed_df = make_speed_dataframe(meta)

        expected_columns = ["Speed", "DateTime", "DataSource"]
        assert list(speed_df.columns) == expected_columns

    def test_make_speed_dataframe_content(self, create_meta_handler):
        """Test that speed dataframe contains correct data."""
        meta = create_meta_handler(num_points=3)
        speed_df = make_speed_dataframe(meta)

        # Check that DataSource is populated
        assert all(
            source == "Extracted metadata using exiftool"
            for source in speed_df["DataSource"]
        )

        # Speed column should exist
        assert "Speed" in speed_df.columns

    def test_make_speed_dataframe_preserves_data(self, create_meta_handler):
        """Test that speed dataframe preserves original GPS data."""
        meta = create_meta_handler(num_points=4)
        original_speeds = meta.gps_df["Speed"].copy()

        speed_df = make_speed_dataframe(meta)

        # Should have same number of rows
        assert len(speed_df) == len(original_speeds)
