"""Tests for project data type classes."""

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from dashcam_investigator.project_manager.project_datatypes import (
    FileAttributes,
    ProjectInfo,
    ProjectStructure,
)


class TestProjectInfo:
    """Test cases for ProjectInfo class."""

    def test_init_with_defaults(self, temp_dir):
        """Test ProjectInfo initialization with default values."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        project = ProjectInfo(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Test Case",
            investigator_name="John Doe",
            report_path="/tmp/report.html",
        )

        assert project.input_directory == input_dir
        assert project.project_directory == output_dir
        assert project.case_name == "Test Case"
        assert project.investigator_name == "John Doe"
        assert project.report_path == "/tmp/report.html"
        assert project.num_videos is None
        assert project.num_images is None
        assert project.num_other is None
        assert isinstance(project.date_created, str)

    def test_init_with_custom_date(self, temp_dir):
        """Test ProjectInfo initialization with custom date."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        custom_date = "2024-01-15T12:00:00"
        project = ProjectInfo(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Test Case",
            investigator_name="Jane Doe",
            report_path="/tmp/report.html",
            date_created=custom_date,
        )

        assert project.date_created == custom_date

    def test_json_object_conversion(self, temp_dir):
        """Test conversion to JSON-serializable dictionary."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        project = ProjectInfo(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Test Case",
            investigator_name="John Doe",
            report_path="/tmp/report.html",
            date_created="2024-01-15T12:00:00",
        )
        project.num_videos = 5
        project.num_images = 10
        project.num_other = 2

        json_obj = project.JSON_object()

        assert json_obj["input_directory"] == str(input_dir.resolve())
        assert json_obj["project_directory"] == str(output_dir.resolve())
        assert json_obj["case_name"] == "Test Case"
        assert json_obj["investigator_name"] == "John Doe"
        assert json_obj["report_path"] == "/tmp/report.html"
        assert json_obj["date_created"] == "2024-01-15T12:00:00"
        assert json_obj["num_videos"] == 5
        assert json_obj["num_images"] == 10
        assert json_obj["num_other"] == 2


class TestFileAttributes:
    """Test cases for FileAttributes class."""

    def test_init_with_defaults(self, temp_dir):
        """Test FileAttributes initialization with default values."""
        test_file = temp_dir / "test_video.mp4"
        test_file.write_text("test content")

        file_attr = FileAttributes(file_path=test_file)

        assert file_attr.file_path == test_file
        assert file_attr.name == "test_video.mp4"
        assert file_attr.type == ".mp4"
        assert isinstance(file_attr.sha256_hash, str)
        assert len(file_attr.sha256_hash) == 64  # SHA256 hash length
        assert file_attr.meta_files == []
        assert file_attr.output_files == []
        assert file_attr.flagged is False
        assert file_attr.notes == ""

    def test_init_with_custom_values(self, temp_dir):
        """Test FileAttributes initialization with custom values."""
        test_file = temp_dir / "test_video.mp4"
        test_file.write_text("test content")

        file_attr = FileAttributes(
            file_path=test_file,
            name="custom_name.mp4",
            ftype=".avi",
            sha256_hash="abc123",
            meta_files=["meta1.json", "meta2.json"],
            output_files=["output1.html"],
            flagged=True,
            notes="Important video",
        )

        assert file_attr.name == "custom_name.mp4"
        assert file_attr.type == ".avi"
        assert file_attr.sha256_hash == "abc123"
        assert file_attr.meta_files == ["meta1.json", "meta2.json"]
        assert file_attr.output_files == ["output1.html"]
        assert file_attr.flagged is True
        assert file_attr.notes == "Important video"

    def test_json_object_conversion(self, temp_dir):
        """Test conversion to JSON-serializable dictionary."""
        test_file = temp_dir / "test_video.mp4"
        test_file.write_text("test content")

        file_attr = FileAttributes(
            file_path=test_file,
            flagged=True,
            notes="Test note",
        )
        file_attr.meta_files = ["metadata.json"]
        file_attr.output_files = ["map.html"]

        json_obj = file_attr.JSON_object()

        assert json_obj["file_path"] == str(test_file.resolve())
        assert json_obj["name"] == "test_video.mp4"
        assert json_obj["type"] == ".mp4"
        assert json_obj["sha256_hash"] == file_attr.sha256_hash
        assert json_obj["meta_files"] == ["metadata.json"]
        assert json_obj["output_files"] == ["map.html"]
        assert json_obj["flagged"] is True
        assert json_obj["notes"] == "Test note"

    def test_hash_generation(self, temp_dir):
        """Test that hash is generated correctly for file content."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello World")

        file_attr1 = FileAttributes(file_path=test_file)
        file_attr2 = FileAttributes(file_path=test_file)

        # Same file should produce same hash
        assert file_attr1.sha256_hash == file_attr2.sha256_hash

        # Different content should produce different hash
        test_file2 = temp_dir / "test2.txt"
        test_file2.write_text("Different content")
        file_attr3 = FileAttributes(file_path=test_file2)

        assert file_attr1.sha256_hash != file_attr3.sha256_hash


class TestProjectStructure:
    """Test cases for ProjectStructure class."""

    def test_init_with_default_tool_name(self, temp_dir):
        """Test ProjectStructure initialization with default tool name."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        project_info = ProjectInfo(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Test",
            investigator_name="John",
            report_path="/tmp/report.html",
        )

        structure = ProjectStructure(
            projectInfo=project_info,
            video_files=[],
            image_files=[],
            other_files=[],
        )

        assert structure.tool_name == "Dascam Investigator"
        assert structure.project_info == project_info
        assert structure.video_files == []
        assert structure.image_files == []
        assert structure.other_files == []

    def test_init_with_custom_tool_name(self, temp_dir):
        """Test ProjectStructure initialization with custom tool name."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        project_info = ProjectInfo(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Test",
            investigator_name="John",
            report_path="/tmp/report.html",
        )

        structure = ProjectStructure(
            projectInfo=project_info,
            video_files=[],
            image_files=[],
            other_files=[],
            tool_name="Custom Tool",
        )

        assert structure.tool_name == "Custom Tool"

    def test_init_with_files(self, temp_dir):
        """Test ProjectStructure initialization with file lists."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        project_info = ProjectInfo(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Test",
            investigator_name="John",
            report_path="/tmp/report.html",
        )

        video_file = temp_dir / "video.mp4"
        video_file.write_text("video")
        image_file = temp_dir / "image.jpg"
        image_file.write_text("image")
        other_file = temp_dir / "data.txt"
        other_file.write_text("data")

        video_attr = FileAttributes(file_path=video_file)
        image_attr = FileAttributes(file_path=image_file)
        other_attr = FileAttributes(file_path=other_file)

        structure = ProjectStructure(
            projectInfo=project_info,
            video_files=[video_attr],
            image_files=[image_attr],
            other_files=[other_attr],
        )

        assert len(structure.video_files) == 1
        assert len(structure.image_files) == 1
        assert len(structure.other_files) == 1
        assert structure.video_files[0].name == "video.mp4"
        assert structure.image_files[0].name == "image.jpg"
        assert structure.other_files[0].name == "data.txt"

    def test_json_object_conversion(self, temp_dir):
        """Test conversion to JSON-serializable dictionary."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        project_info = ProjectInfo(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Test",
            investigator_name="John",
            report_path="/tmp/report.html",
        )

        video_file = temp_dir / "video.mp4"
        video_file.write_text("video")
        video_attr = FileAttributes(file_path=video_file)

        structure = ProjectStructure(
            projectInfo=project_info,
            video_files=[video_attr],
            image_files=[],
            other_files=[],
            tool_name="Test Tool",
        )

        json_obj = structure.JSON_object()

        assert json_obj["tool_name"] == "Test Tool"
        assert json_obj["project_info"] == project_info
        assert json_obj["video_files"] == [video_attr]
        assert json_obj["image_files"] == []
        assert json_obj["other_files"] == []
