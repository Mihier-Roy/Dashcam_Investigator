"""Tests for project manager functionality."""

import json

from dashcam_investigator.project_manager.project_datatypes import (
    FileAttributes,
    ProjectInfo,
    ProjectStructure,
)
from dashcam_investigator.project_manager.project_manager import (
    DASHCAM_INVESTIGATOR_DIRECTORIES,
    DASHCAM_INVESTIGATOR_PROJECT_FILENAME,
    ProjectManager,
)


class TestProjectManager:
    """Test cases for ProjectManager class."""

    def test_init_with_parameters(self, temp_dir):
        """Test ProjectManager initialization with parameters."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        manager = ProjectManager(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Test Case",
            investigator_name="John Doe",
        )

        assert manager.project_directory == output_dir
        assert manager.project_info.case_name == "Test Case"
        assert manager.project_info.investigator_name == "John Doe"
        assert (
            manager.project_file == output_dir / DASHCAM_INVESTIGATOR_PROJECT_FILENAME
        )

    def test_init_with_none_output_dir(self):
        """Test ProjectManager initialization with None output directory."""
        manager = ProjectManager(
            input_dir=None,
            output_dir=None,
            case_name="Test",
            investigator_name="John",
        )

        assert manager.project_directory is None
        assert manager.project_file is None

    def test_new_project_creates_directories(self, temp_dir):
        """Test that new_project creates all required directories."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "project"
        input_dir.mkdir()

        manager = ProjectManager(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="New Project",
            investigator_name="Jane Doe",
        )

        manager.new_project()

        # Verify project directory was created
        assert output_dir.exists()

        # Verify all subdirectories were created
        for dir_name in DASHCAM_INVESTIGATOR_DIRECTORIES:
            assert (output_dir / dir_name).exists()
            assert (output_dir / dir_name).is_dir()

    def test_new_project_creates_project_file(self, temp_dir):
        """Test that new_project creates the project JSON file."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "project"
        input_dir.mkdir()

        manager = ProjectManager(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Test Project",
            investigator_name="Investigator",
        )

        manager.new_project()

        project_file = output_dir / DASHCAM_INVESTIGATOR_PROJECT_FILENAME
        assert project_file.exists()
        assert project_file.is_file()

    def test_new_project_returns_project_structure(self, temp_dir):
        """Test that new_project returns a valid ProjectStructure."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "project"
        input_dir.mkdir()

        manager = ProjectManager(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Test",
            investigator_name="John",
        )

        project_structure = manager.new_project()

        assert isinstance(project_structure, ProjectStructure)
        assert project_structure.project_info.case_name == "Test"
        assert project_structure.project_info.investigator_name == "John"
        assert project_structure.video_files == []
        assert project_structure.image_files == []
        assert project_structure.other_files == []

    def test_new_project_with_existing_directory(self, temp_dir):
        """Test new_project when output directory already exists."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "existing"
        input_dir.mkdir()
        output_dir.mkdir()  # Pre-create the directory

        manager = ProjectManager(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Test",
            investigator_name="John",
        )

        manager.new_project()

        # Should still work and create subdirectories
        assert output_dir.exists()
        for dir_name in DASHCAM_INVESTIGATOR_DIRECTORIES:
            assert (output_dir / dir_name).exists()

    def test_write_project_file(self, temp_dir):
        """Test writing project data to JSON file."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "project"
        input_dir.mkdir()
        output_dir.mkdir()

        manager = ProjectManager(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Write Test",
            investigator_name="Writer",
        )

        # Create project structure
        project_info = ProjectInfo(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Write Test",
            investigator_name="Writer",
            report_path="/tmp/report.html",
        )
        project_structure = ProjectStructure(
            projectInfo=project_info,
            video_files=[],
            image_files=[],
            other_files=[],
        )

        # Write to file
        manager.write_project_file(project_structure)

        # Verify file exists and contains data
        project_file = output_dir / DASHCAM_INVESTIGATOR_PROJECT_FILENAME
        assert project_file.exists()

        with project_file.open("r") as f:
            data = json.load(f)

        assert data["tool_name"] == "Dascam Investigator"
        assert data["project_info"]["case_name"] == "Write Test"

    def test_read_project_file(self, temp_dir):
        """Test reading project data from JSON file."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "project"
        input_dir.mkdir()
        output_dir.mkdir()

        # Create and write a project file
        manager = ProjectManager(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Read Test",
            investigator_name="Reader",
        )
        manager.new_project()

        # Read it back
        loaded_structure = manager.read_project_file()

        assert isinstance(loaded_structure, ProjectStructure)
        assert loaded_structure.project_info.case_name == "Read Test"
        assert loaded_structure.project_info.investigator_name == "Reader"

    def test_load_existing_project(self, temp_dir):
        """Test loading an existing project from file path."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "project"
        input_dir.mkdir()

        # Create a project
        manager1 = ProjectManager(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Existing Project",
            investigator_name="First User",
        )
        manager1.new_project()

        # Load the existing project with a new manager
        manager2 = ProjectManager()
        project_file = output_dir / DASHCAM_INVESTIGATOR_PROJECT_FILENAME
        loaded_structure = manager2.load_existing_project(project_file)

        assert isinstance(loaded_structure, ProjectStructure)
        assert loaded_structure.project_info.case_name == "Existing Project"
        assert loaded_structure.project_info.investigator_name == "First User"
        assert manager2.project_directory == output_dir

    def test_project_with_file_attributes(self, temp_dir):
        """Test project with video, image, and other files."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "project"
        input_dir.mkdir()
        output_dir.mkdir()

        # Create test files
        video_file = temp_dir / "video.mp4"
        image_file = temp_dir / "image.jpg"
        other_file = temp_dir / "data.txt"
        video_file.write_text("video")
        image_file.write_text("image")
        other_file.write_text("data")

        manager = ProjectManager(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Files Test",
            investigator_name="Tester",
        )

        # Create project structure with files
        project_info = ProjectInfo(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Files Test",
            investigator_name="Tester",
            report_path="/tmp/report.html",
        )

        video_attr = FileAttributes(file_path=video_file)
        image_attr = FileAttributes(file_path=image_file)
        other_attr = FileAttributes(file_path=other_file)

        project_structure = ProjectStructure(
            projectInfo=project_info,
            video_files=[video_attr],
            image_files=[image_attr],
            other_files=[other_attr],
        )

        # Write and read back
        manager.write_project_file(project_structure)
        loaded_structure = manager.read_project_file()

        assert len(loaded_structure.video_files) == 1
        assert len(loaded_structure.image_files) == 1
        assert len(loaded_structure.other_files) == 1
        assert loaded_structure.video_files[0].name == "video.mp4"
        assert loaded_structure.image_files[0].name == "image.jpg"
        assert loaded_structure.other_files[0].name == "data.txt"

    def test_roundtrip_with_flagged_videos(self, temp_dir):
        """Test saving and loading project with flagged videos."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "project"
        input_dir.mkdir()
        output_dir.mkdir()

        video_file = temp_dir / "important.mp4"
        video_file.write_text("video content")

        manager = ProjectManager(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Flagged Test",
            investigator_name="Tester",
        )

        project_info = ProjectInfo(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="Flagged Test",
            investigator_name="Tester",
            report_path="/tmp/report.html",
        )

        video_attr = FileAttributes(
            file_path=video_file, flagged=True, notes="Critical evidence"
        )

        project_structure = ProjectStructure(
            projectInfo=project_info,
            video_files=[video_attr],
            image_files=[],
            other_files=[],
        )

        manager.write_project_file(project_structure)
        loaded = manager.read_project_file()

        assert loaded.video_files[0].flagged is True
        assert loaded.video_files[0].notes == "Critical evidence"

    def test_project_directories_constant(self):
        """Test that required directories constant is correct."""
        expected = ["Graphs", "Maps", "Metadata", "Reports", "Timelines"]
        assert DASHCAM_INVESTIGATOR_DIRECTORIES == expected

    def test_project_filename_constant(self):
        """Test that project filename constant is correct."""
        assert DASHCAM_INVESTIGATOR_PROJECT_FILENAME == "dashcam_investigator.json"
