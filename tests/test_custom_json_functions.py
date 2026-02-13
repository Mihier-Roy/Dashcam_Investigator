"""Tests for custom JSON encoding and decoding functions."""

import json
from pathlib import Path

import pytest

from dashcam_investigator.project_manager.project_datatypes import (
    FileAttributes,
    ProjectInfo,
    ProjectStructure,
)
from dashcam_investigator.utils.custom_json_functions import (
    ProjectEncoder,
    convert_to_file_attr,
    convert_to_project_info,
    project_decoder,
)


class TestProjectEncoder:
    """Test cases for ProjectEncoder class."""

    def test_encode_project_info(self, temp_dir):
        """Test encoding ProjectInfo to JSON."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        project_info = ProjectInfo(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Test Case",
            investigator_name="John Doe",
            report_path="/tmp/report.html",
            date_created="2024-01-15T12:00:00",
        )

        json_str = json.dumps(project_info, cls=ProjectEncoder)
        result = json.loads(json_str)

        assert result["case_name"] == "Test Case"
        assert result["investigator_name"] == "John Doe"
        assert result["report_path"] == "/tmp/report.html"
        assert result["date_created"] == "2024-01-15T12:00:00"

    def test_encode_file_attributes(self, temp_dir):
        """Test encoding FileAttributes to JSON."""
        test_file = temp_dir / "test.mp4"
        test_file.write_text("content")

        file_attr = FileAttributes(
            file_path=test_file,
            flagged=True,
            notes="Test note",
        )

        json_str = json.dumps(file_attr, cls=ProjectEncoder)
        result = json.loads(json_str)

        assert result["name"] == "test.mp4"
        assert result["type"] == ".mp4"
        assert result["flagged"] is True
        assert result["notes"] == "Test note"

    def test_encode_project_structure(self, temp_dir):
        """Test encoding entire ProjectStructure to JSON."""
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

        json_str = json.dumps(structure, cls=ProjectEncoder)
        result = json.loads(json_str)

        assert result["tool_name"] == "Test Tool"
        assert "project_info" in result
        assert "video_files" in result
        assert len(result["video_files"]) == 1
        assert result["video_files"][0]["name"] == "video.mp4"

    def test_encode_nested_structure(self, temp_dir):
        """Test encoding nested objects correctly."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        project_info = ProjectInfo(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Nested Test",
            investigator_name="Jane",
            report_path="/tmp/report.html",
        )
        project_info.num_videos = 3

        structure = ProjectStructure(
            projectInfo=project_info,
            video_files=[],
            image_files=[],
            other_files=[],
        )

        json_str = json.dumps(structure, cls=ProjectEncoder, indent=2)
        result = json.loads(json_str)

        # Check nested project_info is properly encoded
        assert result["project_info"]["case_name"] == "Nested Test"
        assert result["project_info"]["num_videos"] == 3


class TestProjectDecoder:
    """Test cases for project_decoder function."""

    def test_decode_project_structure(self, temp_dir):
        """Test decoding JSON to ProjectStructure."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        json_data = {
            "tool_name": "Test Tool",
            "project_info": {
                "input_directory": str(input_dir),
                "project_directory": str(output_dir),
                "case_name": "Test Case",
                "investigator_name": "John Doe",
                "report_path": "/tmp/report.html",
                "date_created": "2024-01-15T12:00:00",
                "num_videos": None,
                "num_images": None,
                "num_other": None,
            },
            "video_files": [],
            "image_files": [],
            "other_files": [],
        }

        result = project_decoder(json_data)

        assert isinstance(result, ProjectStructure)
        assert result.tool_name == "Test Tool"
        assert isinstance(result.project_info, ProjectInfo)
        assert result.project_info.case_name == "Test Case"
        assert result.project_info.investigator_name == "John Doe"

    def test_decode_returns_dict_without_tool_name(self):
        """Test that decoder returns dict unchanged if no tool_name."""
        json_data = {
            "some_key": "some_value",
            "another_key": 123,
        }

        result = project_decoder(json_data)

        assert result == json_data
        assert isinstance(result, dict)
        assert not isinstance(result, ProjectStructure)

    def test_decode_with_file_lists(self, temp_dir):
        """Test decoding with video, image, and other files."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        video_file = temp_dir / "video.mp4"
        video_file.write_text("video")

        json_data = {
            "tool_name": "Test Tool",
            "project_info": {
                "input_directory": str(input_dir),
                "project_directory": str(output_dir),
                "case_name": "Test",
                "investigator_name": "John",
                "report_path": "/tmp/report.html",
                "date_created": "2024-01-15T12:00:00",
                "num_videos": None,
                "num_images": None,
                "num_other": None,
            },
            "video_files": [
                {
                    "file_path": str(video_file),
                    "name": "video.mp4",
                    "type": ".mp4",
                    "sha256_hash": "abc123",
                    "meta_files": [],
                    "output_files": [],
                    "flagged": False,
                    "notes": "",
                }
            ],
            "image_files": [],
            "other_files": [],
        }

        result = project_decoder(json_data)

        assert isinstance(result, ProjectStructure)
        assert len(result.video_files) == 1
        assert isinstance(result.video_files[0], FileAttributes)
        assert result.video_files[0].name == "video.mp4"


class TestConvertToProjectInfo:
    """Test cases for convert_to_project_info function."""

    def test_convert_basic_project_info(self, temp_dir):
        """Test conversion of basic project info dict."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        proj_dict = {
            "input_directory": str(input_dir),
            "project_directory": str(output_dir),
            "case_name": "Test Case",
            "investigator_name": "John Doe",
            "report_path": "/tmp/report.html",
            "date_created": "2024-01-15T12:00:00",
        }

        result = convert_to_project_info(proj_dict)

        assert isinstance(result, ProjectInfo)
        assert result.input_directory == input_dir
        assert result.project_directory == output_dir
        assert result.case_name == "Test Case"
        assert result.investigator_name == "John Doe"
        assert result.report_path == "/tmp/report.html"
        assert result.date_created == "2024-01-15T12:00:00"

    def test_convert_preserves_paths(self, temp_dir):
        """Test that Path objects are correctly created."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        proj_dict = {
            "input_directory": str(input_dir),
            "project_directory": str(output_dir),
            "case_name": "Test",
            "investigator_name": "John",
            "report_path": "/tmp/report.html",
            "date_created": "2024-01-15T12:00:00",
        }

        result = convert_to_project_info(proj_dict)

        assert isinstance(result.input_directory, Path)
        assert isinstance(result.project_directory, Path)


class TestConvertToFileAttr:
    """Test cases for convert_to_file_attr function."""

    def test_convert_empty_list(self):
        """Test conversion of empty list."""
        result = convert_to_file_attr([])

        assert result == []
        assert isinstance(result, list)

    def test_convert_single_file(self, temp_dir):
        """Test conversion of single file attributes."""
        test_file = temp_dir / "test.mp4"
        test_file.write_text("content")

        input_list = [
            {
                "file_path": str(test_file),
                "name": "test.mp4",
                "type": ".mp4",
                "sha256_hash": "abc123",
                "meta_files": [],
                "output_files": [],
                "flagged": False,
                "notes": "",
            }
        ]

        result = convert_to_file_attr(input_list)

        assert len(result) == 1
        assert isinstance(result[0], FileAttributes)
        assert result[0].name == "test.mp4"
        assert result[0].type == ".mp4"
        assert result[0].sha256_hash == "abc123"

    def test_convert_multiple_files(self, temp_dir):
        """Test conversion of multiple file attributes."""
        file1 = temp_dir / "video.mp4"
        file2 = temp_dir / "image.jpg"
        file1.write_text("video")
        file2.write_text("image")

        input_list = [
            {
                "file_path": str(file1),
                "name": "video.mp4",
                "type": ".mp4",
                "sha256_hash": "hash1",
                "meta_files": ["meta1.json"],
                "output_files": [],
                "flagged": True,
                "notes": "Flagged video",
            },
            {
                "file_path": str(file2),
                "name": "image.jpg",
                "type": ".jpg",
                "sha256_hash": "hash2",
                "meta_files": [],
                "output_files": ["map.html"],
                "flagged": False,
                "notes": "",
            },
        ]

        result = convert_to_file_attr(input_list)

        assert len(result) == 2
        assert all(isinstance(item, FileAttributes) for item in result)
        assert result[0].name == "video.mp4"
        assert result[0].flagged is True
        assert result[0].notes == "Flagged video"
        assert result[1].name == "image.jpg"
        assert result[1].output_files == ["map.html"]

    def test_convert_preserves_all_attributes(self, temp_dir):
        """Test that all attributes are preserved in conversion."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        input_list = [
            {
                "file_path": str(test_file),
                "name": "custom_name.txt",
                "type": ".custom",
                "sha256_hash": "custom_hash",
                "meta_files": ["file1.json", "file2.json"],
                "output_files": ["out1.html", "out2.html"],
                "flagged": True,
                "notes": "Important notes here",
            }
        ]

        result = convert_to_file_attr(input_list)

        attr = result[0]
        assert attr.name == "custom_name.txt"
        assert attr.type == ".custom"
        assert attr.sha256_hash == "custom_hash"
        assert attr.meta_files == ["file1.json", "file2.json"]
        assert attr.output_files == ["out1.html", "out2.html"]
        assert attr.flagged is True
        assert attr.notes == "Important notes here"


class TestRoundTripSerialization:
    """Test cases for round-trip encoding/decoding."""

    def test_roundtrip_project_structure(self, temp_dir):
        """Test encoding and decoding ProjectStructure maintains data."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        # Create original structure
        project_info = ProjectInfo(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Roundtrip Test",
            investigator_name="Test User",
            report_path="/tmp/report.html",
            date_created="2024-01-15T12:00:00",
        )
        project_info.num_videos = 5

        video_file = temp_dir / "video.mp4"
        video_file.write_text("video content")
        video_attr = FileAttributes(file_path=video_file, flagged=True, notes="Test")

        original = ProjectStructure(
            projectInfo=project_info,
            video_files=[video_attr],
            image_files=[],
            other_files=[],
            tool_name="Roundtrip Tool",
        )

        # Encode to JSON
        json_str = json.dumps(original, cls=ProjectEncoder)

        # Decode back
        decoded_dict = json.loads(json_str)
        decoded = project_decoder(decoded_dict)

        # Verify data is preserved
        assert isinstance(decoded, ProjectStructure)
        assert decoded.tool_name == "Roundtrip Tool"
        assert decoded.project_info.case_name == "Roundtrip Test"
        assert decoded.project_info.investigator_name == "Test User"
        assert decoded.project_info.num_videos == 5
        assert len(decoded.video_files) == 1
        assert decoded.video_files[0].name == "video.mp4"
        assert decoded.video_files[0].flagged is True
        assert decoded.video_files[0].notes == "Test"
