"""Tests for metadata extraction functions."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from dashcam_investigator.core.extract_metadata import (
    process_file_meta,
    process_gps_data,
)
from dashcam_investigator.exceptions import ExifToolError


def _make_run_result(returncode=0, stderr=b""):
    result = MagicMock()
    result.returncode = returncode
    result.stderr = stderr
    return result


class TestProcessGpsData:
    """Test cases for process_gps_data function."""

    @patch("dashcam_investigator.core.extract_metadata.subprocess.run")
    @patch(
        "dashcam_investigator.core.extract_metadata.shutil.which",
        return_value="/usr/bin/exiftool",
    )
    def test_process_gps_data_creates_gpx_file(self, mock_which, mock_run, temp_dir):
        """Test that GPS data extraction calls exiftool correctly."""
        mock_run.return_value = _make_run_result()
        video_path = temp_dir / "test_video.mp4"
        video_path.write_text("fake video content")
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        result = process_gps_data(video_path, output_dir)

        assert mock_run.called
        cmd = mock_run.call_args[0][0]
        assert "exiftool" in cmd[0]
        assert "gpx.fmt" in cmd
        assert str(video_path.resolve()) in cmd

        expected_output = output_dir / "test_video.gpx"
        assert result == expected_output

    @patch("dashcam_investigator.core.extract_metadata.subprocess.run")
    @patch(
        "dashcam_investigator.core.extract_metadata.shutil.which",
        return_value="/usr/bin/exiftool",
    )
    def test_process_gps_data_output_filename(self, mock_which, mock_run, temp_dir):
        """Test that output filename is correctly derived from input using Path.stem."""
        mock_run.return_value = _make_run_result()
        video_path = temp_dir / "dashcam_2024_01_15.mp4"
        video_path.write_text("content")
        output_dir = temp_dir / "metadata"
        output_dir.mkdir()

        result = process_gps_data(video_path, output_dir)

        assert result == output_dir / "dashcam_2024_01_15.gpx"

    @patch("dashcam_investigator.core.extract_metadata.subprocess.run")
    @patch(
        "dashcam_investigator.core.extract_metadata.shutil.which",
        return_value="/usr/bin/exiftool",
    )
    @pytest.mark.parametrize("ext", [".mp4", ".avi", ".mov", ".mkv"])
    def test_process_gps_data_with_different_extensions(
        self, mock_which, mock_run, ext, temp_dir
    ):
        """Test GPS extraction with different video file extensions."""
        mock_run.return_value = _make_run_result()
        video_path = temp_dir / f"video{ext}"
        video_path.write_text("content")
        output_dir = temp_dir / "output"
        output_dir.mkdir(exist_ok=True)

        result = process_gps_data(video_path, output_dir)

        assert result == output_dir / "video.gpx"

    @patch("dashcam_investigator.core.extract_metadata.shutil.which", return_value=None)
    def test_process_gps_data_raises_when_exiftool_missing(self, mock_which, temp_dir):
        """Missing exiftool binary raises ExifToolError."""
        video_path = temp_dir / "video.mp4"
        video_path.write_text("content")
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        with pytest.raises(ExifToolError, match="not found on PATH"):
            process_gps_data(video_path, output_dir)

    @patch("dashcam_investigator.core.extract_metadata.subprocess.run")
    @patch(
        "dashcam_investigator.core.extract_metadata.shutil.which",
        return_value="/usr/bin/exiftool",
    )
    def test_process_gps_data_raises_on_nonzero_exit(
        self, mock_which, mock_run, temp_dir
    ):
        """Non-zero exiftool exit code raises ExifToolError."""
        mock_run.return_value = _make_run_result(returncode=1, stderr=b"No such file")
        video_path = temp_dir / "video.mp4"
        video_path.write_text("content")
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        with pytest.raises(ExifToolError, match="No such file"):
            process_gps_data(video_path, output_dir)

    @patch("dashcam_investigator.core.extract_metadata.subprocess.run")
    @patch(
        "dashcam_investigator.core.extract_metadata.shutil.which",
        return_value="/usr/bin/exiftool",
    )
    def test_process_gps_data_raises_on_timeout(self, mock_which, mock_run, temp_dir):
        """Subprocess timeout raises ExifToolError."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="exiftool", timeout=120)
        video_path = temp_dir / "video.mp4"
        video_path.write_text("content")
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        with pytest.raises(ExifToolError, match="timed out"):
            process_gps_data(video_path, output_dir)


class TestProcessFileMeta:
    """Test cases for process_file_meta function."""

    @patch("dashcam_investigator.core.extract_metadata.subprocess.run")
    @patch(
        "dashcam_investigator.core.extract_metadata.shutil.which",
        return_value="/usr/bin/exiftool",
    )
    def test_process_file_meta_creates_csv(self, mock_which, mock_run, temp_dir):
        """Test that file metadata extraction calls exiftool correctly."""
        mock_run.return_value = _make_run_result()
        video_path = temp_dir / "test_video.mp4"
        video_path.write_text("fake video content")
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        result = process_file_meta(video_path, output_dir)

        assert mock_run.called
        cmd = mock_run.call_args[0][0]
        assert "exiftool" in cmd[0]
        assert "-csv" in cmd
        assert str(video_path.resolve()) in cmd

        assert result == output_dir / "test_video_fileinfo.csv"

    @patch("dashcam_investigator.core.extract_metadata.subprocess.run")
    @patch(
        "dashcam_investigator.core.extract_metadata.shutil.which",
        return_value="/usr/bin/exiftool",
    )
    def test_process_file_meta_output_filename(self, mock_which, mock_run, temp_dir):
        """Test that output CSV filename is correctly derived."""
        mock_run.return_value = _make_run_result()
        video_path = temp_dir / "incident_footage.mp4"
        video_path.write_text("content")
        output_dir = temp_dir / "metadata"
        output_dir.mkdir()

        result = process_file_meta(video_path, output_dir)

        assert result == output_dir / "incident_footage_fileinfo.csv"

    @patch("dashcam_investigator.core.extract_metadata.subprocess.run")
    @patch(
        "dashcam_investigator.core.extract_metadata.shutil.which",
        return_value="/usr/bin/exiftool",
    )
    def test_process_file_meta_includes_required_flags(
        self, mock_which, mock_run, temp_dir
    ):
        """Test that exiftool command includes all required flags."""
        mock_run.return_value = _make_run_result()
        video_path = temp_dir / "video.mp4"
        video_path.write_text("content")
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        process_file_meta(video_path, output_dir)

        cmd = mock_run.call_args[0][0]
        assert "-ee" in cmd
        assert "-FileType" in cmd
        assert "-filesize" in cmd
        assert "-MIMEType" in cmd
        assert "-createDate" in cmd
        assert "-Duration" in cmd
        assert "-csv" in cmd

    @patch("dashcam_investigator.core.extract_metadata.shutil.which", return_value=None)
    def test_process_file_meta_raises_when_exiftool_missing(self, mock_which, temp_dir):
        """Missing exiftool binary raises ExifToolError."""
        video_path = temp_dir / "video.mp4"
        video_path.write_text("content")
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        with pytest.raises(ExifToolError, match="not found on PATH"):
            process_file_meta(video_path, output_dir)

    @patch("dashcam_investigator.core.extract_metadata.subprocess.run")
    @patch(
        "dashcam_investigator.core.extract_metadata.shutil.which",
        return_value="/usr/bin/exiftool",
    )
    def test_process_file_meta_raises_on_nonzero_exit(
        self, mock_which, mock_run, temp_dir
    ):
        """Non-zero exiftool exit code raises ExifToolError."""
        mock_run.return_value = _make_run_result(
            returncode=1, stderr=b"Permission denied"
        )
        video_path = temp_dir / "video.mp4"
        video_path.write_text("content")
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        with pytest.raises(ExifToolError, match="Permission denied"):
            process_file_meta(video_path, output_dir)


class TestMetadataExtraction:
    """Integration-style tests for metadata extraction."""

    @patch("dashcam_investigator.core.extract_metadata.subprocess.run")
    @patch(
        "dashcam_investigator.core.extract_metadata.shutil.which",
        return_value="/usr/bin/exiftool",
    )
    def test_both_extractions_with_same_video(self, mock_which, mock_run, temp_dir):
        """Test that both GPS and file metadata can be extracted from same video."""
        mock_run.return_value = _make_run_result()
        video_path = temp_dir / "dashcam.mp4"
        video_path.write_text("video content")
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        gps_result = process_gps_data(video_path, output_dir)
        meta_result = process_file_meta(video_path, output_dir)

        assert gps_result != meta_result
        assert gps_result.suffix == ".gpx"
        assert meta_result.suffix == ".csv"
        assert mock_run.call_count == 2

    @patch("dashcam_investigator.core.extract_metadata.subprocess.run")
    @patch(
        "dashcam_investigator.core.extract_metadata.shutil.which",
        return_value="/usr/bin/exiftool",
    )
    def test_extraction_with_special_characters_in_filename(
        self, mock_which, mock_run, temp_dir
    ):
        """Test extraction with filenames containing special characters."""
        mock_run.return_value = _make_run_result()
        video_path = temp_dir / "video_2024-01-15_14-30-00.mp4"
        video_path.write_text("content")
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        gps_result = process_gps_data(video_path, output_dir)
        meta_result = process_file_meta(video_path, output_dir)

        assert gps_result.name == "video_2024-01-15_14-30-00.gpx"
        assert meta_result.name == "video_2024-01-15_14-30-00_fileinfo.csv"
