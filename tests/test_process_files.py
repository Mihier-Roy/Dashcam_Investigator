"""Tests for file processing pipeline."""

from unittest.mock import Mock, patch

import pytest

from dashcam_investigator.core.process_files import (
    create_map,
    extract_meta,
    process_files,
)
from dashcam_investigator.project_manager.project_datatypes import (
    FileAttributes,
    ProjectInfo,
    ProjectStructure,
)


class TestExtractMeta:
    """Test cases for extract_meta function."""

    @patch("dashcam_investigator.core.process_files.process_file_meta")
    @patch("dashcam_investigator.core.process_files.process_gps_data")
    def test_extract_meta_calls_both_extractors(
        self, mock_gps, mock_file_meta, temp_dir
    ):
        """Test that extract_meta calls both GPS and file metadata extractors."""
        video_file = temp_dir / "test_video.mp4"
        video_file.write_text("content")
        project_dir = temp_dir / "project"
        project_dir.mkdir()

        video_attr = FileAttributes(file_path=video_file)

        # Mock return values
        mock_gps.return_value = "/tmp/output.gpx"
        mock_file_meta.return_value = "/tmp/output.csv"

        extract_meta(video_attr, project_dir)

        # Verify both functions were called
        assert mock_gps.called
        assert mock_file_meta.called

    @patch("dashcam_investigator.core.process_files.process_file_meta")
    @patch("dashcam_investigator.core.process_files.process_gps_data")
    def test_extract_meta_stores_metadata_paths(
        self, mock_gps, mock_file_meta, temp_dir
    ):
        """Test that metadata file paths are stored in FileAttributes."""
        video_file = temp_dir / "test_video.mp4"
        video_file.write_text("content")
        project_dir = temp_dir / "project"
        project_dir.mkdir()

        video_attr = FileAttributes(file_path=video_file)

        gpx_path = "/tmp/output.gpx"
        csv_path = "/tmp/output.csv"
        mock_gps.return_value = gpx_path
        mock_file_meta.return_value = csv_path

        result = extract_meta(video_attr, project_dir)

        assert gpx_path in result.meta_files
        assert csv_path in result.meta_files
        assert len(result.meta_files) == 2

    @patch("dashcam_investigator.core.process_files.process_file_meta")
    @patch("dashcam_investigator.core.process_files.process_gps_data")
    def test_extract_meta_uses_metadata_directory(
        self, mock_gps, mock_file_meta, temp_dir
    ):
        """Test that metadata is extracted to Metadata directory."""
        video_file = temp_dir / "test_video.mp4"
        video_file.write_text("content")
        project_dir = temp_dir / "project"
        project_dir.mkdir()

        video_attr = FileAttributes(file_path=video_file)

        mock_gps.return_value = "/tmp/output.gpx"
        mock_file_meta.return_value = "/tmp/output.csv"

        extract_meta(video_attr, project_dir)

        # Verify Metadata directory was used in calls
        expected_metadata_dir = project_dir / "Metadata"
        mock_gps.assert_called_once()
        assert mock_gps.call_args[1]["output_dir"] == expected_metadata_dir
        mock_file_meta.assert_called_once()
        assert mock_file_meta.call_args[1]["output_dir"] == expected_metadata_dir


class TestCreateMap:
    """Test cases for create_map function."""

    @patch("dashcam_investigator.core.process_files.OutputGenerator")
    def test_create_map_initializes_generator(self, mock_generator_class, temp_dir):
        """Test that OutputGenerator is initialized."""
        video_file = temp_dir / "test_video.mp4"
        video_file.write_text("content")
        project_dir = temp_dir / "project"
        project_dir.mkdir()

        # Create required directories
        (project_dir / "Maps").mkdir()
        (project_dir / "Graphs").mkdir()

        video_attr = FileAttributes(file_path=video_file)
        video_attr.meta_files = ["gps.gpx", "meta.csv"]

        mock_instance = Mock()
        mock_generator_class.return_value = mock_instance

        create_map(video_attr, project_dir)

        # Verify OutputGenerator was instantiated
        mock_generator_class.assert_called_once()

    @patch("dashcam_investigator.core.process_files.OutputGenerator")
    def test_create_map_generates_map_and_graph(self, mock_generator_class, temp_dir):
        """Test that both map and speed graph are generated."""
        video_file = temp_dir / "test_video.mp4"
        video_file.write_text("content")
        project_dir = temp_dir / "project"
        project_dir.mkdir()

        (project_dir / "Maps").mkdir()
        (project_dir / "Graphs").mkdir()

        video_attr = FileAttributes(file_path=video_file)
        video_attr.meta_files = ["gps.gpx", "meta.csv"]

        mock_instance = Mock()
        mock_generator_class.return_value = mock_instance

        create_map(video_attr, project_dir)

        # Verify both methods were called
        mock_instance.generate_map.assert_called_once()
        mock_instance.generate_speed_chart.assert_called_once()

    @patch("dashcam_investigator.core.process_files.OutputGenerator")
    def test_create_map_stores_output_paths(self, mock_generator_class, temp_dir):
        """Test that output file paths are stored in FileAttributes."""
        video_file = temp_dir / "test_video.mp4"
        video_file.write_text("content")
        project_dir = temp_dir / "project"
        project_dir.mkdir()

        (project_dir / "Maps").mkdir()
        (project_dir / "Graphs").mkdir()

        video_attr = FileAttributes(file_path=video_file)
        video_attr.meta_files = ["gps.gpx", "meta.csv"]

        mock_instance = Mock()
        mock_generator_class.return_value = mock_instance

        result = create_map(video_attr, project_dir)

        # Should have 2 output files (map and graph)
        assert len(result.output_files) == 2
        # Check that paths end with expected extensions
        assert any(path.endswith("_map.html") for path in result.output_files)
        assert any(path.endswith("_speed_graph.html") for path in result.output_files)

    @patch("dashcam_investigator.core.process_files.OutputGenerator")
    def test_create_map_output_filenames(self, mock_generator_class, temp_dir):
        """Test that output filenames are derived from video name."""
        video_file = temp_dir / "dashcam_2024.mp4"
        video_file.write_text("content")
        project_dir = temp_dir / "project"
        project_dir.mkdir()

        (project_dir / "Maps").mkdir()
        (project_dir / "Graphs").mkdir()

        video_attr = FileAttributes(file_path=video_file)
        video_attr.meta_files = ["gps.gpx", "meta.csv"]

        mock_instance = Mock()
        mock_generator_class.return_value = mock_instance

        result = create_map(video_attr, project_dir)

        # Check filenames include video name (without extension)
        assert any("dashcam_2024_map.html" in path for path in result.output_files)
        assert any(
            "dashcam_2024_speed_graph.html" in path for path in result.output_files
        )


class TestProcessFiles:
    """Test cases for process_files function."""

    @pytest.fixture
    def create_test_files(self, temp_dir):
        """Create various test files."""

        def _create():
            input_dir = temp_dir / "input"
            input_dir.mkdir()

            # Create a video file (simulated)
            video_file = input_dir / "video.mp4"
            # Write MP4 signature bytes
            video_file.write_bytes(b"\x00\x00\x00\x20\x66\x74\x79\x70\x69\x73\x6f\x6d")

            # Create an image file (simulated)
            image_file = input_dir / "image.jpg"
            # Write JPEG signature bytes
            image_file.write_bytes(b"\xff\xd8\xff\xe0")

            # Create a text file (other)
            text_file = input_dir / "data.txt"
            text_file.write_text("some text data")

            return input_dir, video_file, image_file, text_file

        return _create

    @pytest.fixture
    def create_project_structure(self, temp_dir):
        """Create a basic project structure."""

        def _create():
            input_dir = temp_dir / "input"
            output_dir = temp_dir / "project"
            input_dir.mkdir()
            output_dir.mkdir()

            # Create required directories
            (output_dir / "Metadata").mkdir()
            (output_dir / "Maps").mkdir()
            (output_dir / "Graphs").mkdir()

            project_info = ProjectInfo(
                input_dir=input_dir,
                output_dir=output_dir,
                case_name="Test",
                investigator_name="Tester",
                report_path="/tmp/report.html",
            )

            project = ProjectStructure(
                projectInfo=project_info,
                video_files=[],
                image_files=[],
                other_files=[],
            )

            return input_dir, project

        return _create

    @patch("dashcam_investigator.core.process_files.create_map")
    @patch("dashcam_investigator.core.process_files.extract_meta")
    @patch("dashcam_investigator.core.process_files.filetype.guess_mime")
    def test_process_files_identifies_videos(
        self, mock_filetype, mock_extract, mock_create_map, create_project_structure
    ):
        """Test that video files are correctly identified."""
        input_dir, project = create_project_structure()

        # Create a video file
        video_file = input_dir / "test.mp4"
        video_file.write_text("content")

        mock_filetype.return_value = "video/mp4"
        mock_extract.return_value = FileAttributes(file_path=video_file)
        mock_create_map.return_value = FileAttributes(file_path=video_file)

        # Create mock progress callback
        progress_callback = Mock()
        progress_callback.emit = Mock()

        result = process_files(input_dir, project, progress_callback)

        assert result.project_info.num_videos == 1
        assert len(result.video_files) == 1

    @patch("dashcam_investigator.core.process_files.filetype.guess_mime")
    def test_process_files_identifies_images(
        self, mock_filetype, create_project_structure
    ):
        """Test that image files are correctly identified."""
        input_dir, project = create_project_structure()

        # Create an image file
        image_file = input_dir / "test.jpg"
        image_file.write_text("content")

        mock_filetype.return_value = "image/jpeg"

        progress_callback = Mock()
        progress_callback.emit = Mock()

        result = process_files(input_dir, project, progress_callback)

        assert result.project_info.num_images == 1
        assert len(result.image_files) == 1

    @patch("dashcam_investigator.core.process_files.filetype.guess_mime")
    def test_process_files_identifies_other_files(
        self, mock_filetype, create_project_structure
    ):
        """Test that other files are correctly categorized."""
        input_dir, project = create_project_structure()

        # Create a text file
        text_file = input_dir / "data.txt"
        text_file.write_text("content")

        mock_filetype.return_value = None  # Unknown type

        progress_callback = Mock()
        progress_callback.emit = Mock()

        result = process_files(input_dir, project, progress_callback)

        assert result.project_info.num_other == 1
        assert len(result.other_files) == 1

    @patch("dashcam_investigator.core.process_files.create_map")
    @patch("dashcam_investigator.core.process_files.extract_meta")
    @patch("dashcam_investigator.core.process_files.filetype.guess_mime")
    def test_process_files_emits_progress(
        self, mock_filetype, mock_extract, mock_create_map, create_project_structure
    ):
        """Test that progress signals are emitted."""
        input_dir, project = create_project_structure()

        # Create multiple files
        for i in range(3):
            file = input_dir / f"file{i}.txt"
            file.write_text("content")

        mock_filetype.return_value = None

        progress_callback = Mock()
        progress_callback.emit = Mock()

        process_files(input_dir, project, progress_callback)

        # Should emit progress for each file
        assert progress_callback.emit.call_count >= 3

    @patch("dashcam_investigator.core.process_files.create_map")
    @patch("dashcam_investigator.core.process_files.extract_meta")
    @patch("dashcam_investigator.core.process_files.filetype.guess_mime")
    def test_process_files_processes_videos_completely(
        self, mock_filetype, mock_extract, mock_create_map, create_project_structure
    ):
        """Test that video files go through full processing pipeline."""
        input_dir, project = create_project_structure()

        video_file = input_dir / "video.mp4"
        video_file.write_text("content")

        mock_filetype.return_value = "video/mp4"
        mock_video_attr = FileAttributes(file_path=video_file)
        mock_extract.return_value = mock_video_attr
        mock_create_map.return_value = mock_video_attr

        progress_callback = Mock()
        progress_callback.emit = Mock()

        process_files(input_dir, project, progress_callback)

        # Verify both extract_meta and create_map were called
        mock_extract.assert_called()
        mock_create_map.assert_called()

    @patch("dashcam_investigator.core.process_files.filetype.guess_mime")
    def test_process_files_counts_all_file_types(
        self, mock_filetype, create_project_structure
    ):
        """Test that all file type counts are updated correctly."""
        input_dir, project = create_project_structure()

        # Create mixed files
        text_file = input_dir / "file.txt"
        text_file.write_text("content")

        mock_filetype.return_value = None

        progress_callback = Mock()
        progress_callback.emit = Mock()

        result = process_files(input_dir, project, progress_callback)

        # All count fields should be set
        assert result.project_info.num_videos is not None
        assert result.project_info.num_images is not None
        assert result.project_info.num_other is not None

    @patch("dashcam_investigator.core.process_files.filetype.guess_mime")
    def test_process_files_skips_directories(
        self, mock_filetype, create_project_structure
    ):
        """Test that directories are skipped during processing."""
        input_dir, project = create_project_structure()

        # Create a subdirectory
        subdir = input_dir / "subdir"
        subdir.mkdir()

        # Create a file in subdirectory
        file_in_subdir = subdir / "file.txt"
        file_in_subdir.write_text("content")

        mock_filetype.return_value = None

        progress_callback = Mock()
        progress_callback.emit = Mock()

        result = process_files(input_dir, project, progress_callback)

        # Should process the file but not the directory
        assert result.project_info.num_other == 1
