"""Tests for metadata extraction functions."""

from unittest.mock import patch

from dashcam_investigator.core.extract_metadata import (
    process_file_meta,
    process_gps_data,
)


class TestProcessGpsData:
    """Test cases for process_gps_data function."""

    @patch("dashcam_investigator.core.extract_metadata.system")
    def test_process_gps_data_creates_gpx_file(self, mock_system, temp_dir):
        """Test that GPS data extraction calls exiftool correctly."""
        video_path = temp_dir / "test_video.mp4"
        video_path.write_text("fake video content")
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        result = process_gps_data(video_path, output_dir)

        # Verify system call was made
        assert mock_system.called
        call_args = mock_system.call_args[0][0]
        assert "exiftool" in call_args
        assert "gpx.fmt" in call_args
        assert str(video_path.resolve()) in call_args

        # Verify output path
        expected_output = output_dir / "test_video.gpx"
        assert result == str(expected_output.resolve())

    @patch("dashcam_investigator.core.extract_metadata.system")
    def test_process_gps_data_output_filename(self, mock_system, temp_dir):
        """Test that output filename is correctly derived from input."""
        video_path = temp_dir / "dashcam_2024_01_15.mp4"
        video_path.write_text("content")
        output_dir = temp_dir / "metadata"
        output_dir.mkdir()

        result = process_gps_data(video_path, output_dir)

        expected_output = output_dir / "dashcam_2024_01_15.gpx"
        assert result == str(expected_output.resolve())

    @patch("dashcam_investigator.core.extract_metadata.system")
    def test_process_gps_data_with_different_extensions(self, mock_system, temp_dir):
        """Test GPS extraction with different video file extensions."""
        for ext in [".mp4", ".avi", ".mov", ".mkv"]:
            video_path = temp_dir / f"video{ext}"
            video_path.write_text("content")
            output_dir = temp_dir / "output"
            output_dir.mkdir(exist_ok=True)

            result = process_gps_data(video_path, output_dir)

            expected_output = output_dir / "video.gpx"
            assert result == str(expected_output.resolve())


class TestProcessFileMeta:
    """Test cases for process_file_meta function."""

    @patch("dashcam_investigator.core.extract_metadata.system")
    def test_process_file_meta_creates_csv(self, mock_system, temp_dir):
        """Test that file metadata extraction calls exiftool correctly."""
        video_path = temp_dir / "test_video.mp4"
        video_path.write_text("fake video content")
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        result = process_file_meta(video_path, output_dir)

        # Verify system call was made
        assert mock_system.called
        call_args = mock_system.call_args[0][0]
        assert "exiftool" in call_args
        assert "-csv" in call_args
        assert str(video_path.resolve()) in call_args

        # Verify output path
        expected_output = output_dir / "test_video_fileinfo.csv"
        assert result == str(expected_output.resolve())

    @patch("dashcam_investigator.core.extract_metadata.system")
    def test_process_file_meta_output_filename(self, mock_system, temp_dir):
        """Test that output CSV filename is correctly derived."""
        video_path = temp_dir / "incident_footage.mp4"
        video_path.write_text("content")
        output_dir = temp_dir / "metadata"
        output_dir.mkdir()

        result = process_file_meta(video_path, output_dir)

        expected_output = output_dir / "incident_footage_fileinfo.csv"
        assert result == str(expected_output.resolve())

    @patch("dashcam_investigator.core.extract_metadata.system")
    def test_process_file_meta_includes_required_flags(self, mock_system, temp_dir):
        """Test that exiftool command includes all required flags."""
        video_path = temp_dir / "video.mp4"
        video_path.write_text("content")
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        process_file_meta(video_path, output_dir)

        call_args = mock_system.call_args[0][0]
        # Check for required flags
        assert "-ee" in call_args
        assert "-FileType" in call_args
        assert "-filesize" in call_args
        assert "-MIMEType" in call_args
        assert "-createDate" in call_args
        assert "-Duration" in call_args
        assert "-csv" in call_args

    @patch("dashcam_investigator.core.extract_metadata.system")
    def test_process_file_meta_with_different_extensions(self, mock_system, temp_dir):
        """Test file metadata extraction with different extensions."""
        for ext in [".mp4", ".avi", ".jpg", ".png"]:
            video_path = temp_dir / f"file{ext}"
            video_path.write_text("content")
            output_dir = temp_dir / "output"
            output_dir.mkdir(exist_ok=True)

            result = process_file_meta(video_path, output_dir)

            expected_output = output_dir / "file_fileinfo.csv"
            assert result == str(expected_output.resolve())


class TestMetadataExtraction:
    """Integration-style tests for metadata extraction."""

    @patch("dashcam_investigator.core.extract_metadata.system")
    def test_both_extractions_with_same_video(self, mock_system, temp_dir):
        """Test that both GPS and file metadata can be extracted from same video."""
        video_path = temp_dir / "dashcam.mp4"
        video_path.write_text("video content")
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        gps_result = process_gps_data(video_path, output_dir)
        meta_result = process_file_meta(video_path, output_dir)

        # Both should succeed and produce different output files
        assert gps_result != meta_result
        assert gps_result.endswith(".gpx")
        assert meta_result.endswith(".csv")

        # Verify both exiftool calls were made
        assert mock_system.call_count == 2

    @patch("dashcam_investigator.core.extract_metadata.system")
    def test_extraction_with_special_characters_in_filename(
        self, mock_system, temp_dir
    ):
        """Test extraction with filenames containing special characters."""
        video_path = temp_dir / "video_2024-01-15_14-30-00.mp4"
        video_path.write_text("content")
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        gps_result = process_gps_data(video_path, output_dir)
        meta_result = process_file_meta(video_path, output_dir)

        assert "video_2024-01-15_14-30-00.gpx" in gps_result
        assert "video_2024-01-15_14-30-00_fileinfo.csv" in meta_result
