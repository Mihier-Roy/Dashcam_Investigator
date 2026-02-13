"""Tests for report generation functionality."""

from pathlib import Path

import pytest

from dashcam_investigator.core.generate_report import generate_report
from dashcam_investigator.project_manager.project_datatypes import (
    FileAttributes,
    ProjectInfo,
    ProjectStructure,
)


class TestGenerateReport:
    """Test cases for generate_report function."""

    @pytest.fixture
    def create_project_with_flagged_videos(self, temp_dir):
        """Create a project structure with flagged videos."""

        def _create(num_flagged=2):
            input_dir = temp_dir / "input"
            output_dir = temp_dir / "project"
            input_dir.mkdir()
            output_dir.mkdir()

            # Create Reports directory
            reports_dir = output_dir / "Reports"
            reports_dir.mkdir()

            # Create Metadata directory for CSV files
            metadata_dir = output_dir / "Metadata"
            metadata_dir.mkdir()

            # Create Maps and Graphs directories
            maps_dir = output_dir / "Maps"
            graphs_dir = output_dir / "Graphs"
            maps_dir.mkdir()
            graphs_dir.mkdir()

            project_info = ProjectInfo(
                input_dir=input_dir,
                output_dir=output_dir,
                case_name="Test Case",
                investigator_name="Test Investigator",
                report_path="/tmp/report.html",
            )

            video_files = []
            for i in range(num_flagged):
                # Create video file
                video_file = temp_dir / f"video{i}.mp4"
                video_file.write_text("video content")

                # Create metadata CSV
                csv_path = metadata_dir / f"video{i}_fileinfo.csv"
                csv_content = f"""SourceFile,FileType,FileSize,MIMEType,CreateDate,Duration,Format,Information
/tmp/video{i}.mp4,MP4,1048576,video/mp4,15-01-2024 14:30:00,00:05:30,MPEG-4,Test Device"""
                csv_path.write_text(csv_content)

                # Create GPX file
                gpx_path = metadata_dir / f"video{i}.gpx"
                gpx_path.write_text("<gpx></gpx>")

                # Create map and graph files
                map_path = maps_dir / f"video{i}_map.html"
                map_path.write_text("<html>Map</html>")
                graph_path = graphs_dir / f"video{i}_speed_graph.html"
                graph_path.write_text("<html>Graph</html>")

                # Create FileAttributes
                video_attr = FileAttributes(
                    file_path=video_file,
                    flagged=True,
                    notes=f"Note for video {i}",
                )
                video_attr.meta_files = [str(gpx_path), str(csv_path)]
                video_attr.output_files = [str(map_path), str(graph_path)]
                video_files.append(video_attr)

            project_structure = ProjectStructure(
                projectInfo=project_info,
                video_files=video_files,
                image_files=[],
                other_files=[],
            )

            return project_structure

        return _create

    def test_generate_report_creates_file(self, create_project_with_flagged_videos):
        """Test that generate_report creates an HTML file."""
        project = create_project_with_flagged_videos(num_flagged=1)
        output_file = generate_report(project)

        assert Path(output_file).exists()
        assert Path(output_file).is_file()
        assert str(output_file).endswith(".html")

    def test_generate_report_filename(self, create_project_with_flagged_videos):
        """Test that report filename includes case name."""
        project = create_project_with_flagged_videos(num_flagged=1)
        output_file = generate_report(project)

        expected_name = "Test Case_report.html"
        assert Path(output_file).name == expected_name

    def test_generate_report_location(self, create_project_with_flagged_videos):
        """Test that report is created in Reports directory."""
        project = create_project_with_flagged_videos(num_flagged=1)
        output_file = generate_report(project)

        assert "Reports" in str(output_file)
        assert Path(output_file).parent.name == "Reports"

    def test_generate_report_contains_case_name(
        self, create_project_with_flagged_videos
    ):
        """Test that report HTML contains case name."""
        project = create_project_with_flagged_videos(num_flagged=1)
        output_file = generate_report(project)

        with Path(output_file).open("r") as f:
            content = f.read()

        assert "Test Case" in content

    def test_generate_report_contains_investigator_name(
        self, create_project_with_flagged_videos
    ):
        """Test that report HTML contains investigator name."""
        project = create_project_with_flagged_videos(num_flagged=1)
        output_file = generate_report(project)

        with Path(output_file).open("r") as f:
            content = f.read()

        assert "Test Investigator" in content

    def test_generate_report_includes_flagged_videos(
        self, create_project_with_flagged_videos
    ):
        """Test that report includes all flagged videos."""
        project = create_project_with_flagged_videos(num_flagged=3)
        output_file = generate_report(project)

        with Path(output_file).open("r") as f:
            content = f.read()

        # Should include video names (without extension)
        assert "video0" in content
        assert "video1" in content
        assert "video2" in content

    def test_generate_report_excludes_unflagged_videos(
        self, create_project_with_flagged_videos, temp_dir
    ):
        """Test that unflagged videos are not included in report."""
        project = create_project_with_flagged_videos(num_flagged=1)

        # Add unflagged video
        unflagged_file = temp_dir / "unflagged.mp4"
        unflagged_file.write_text("content")
        unflagged_attr = FileAttributes(file_path=unflagged_file, flagged=False)
        project.video_files.append(unflagged_attr)

        output_file = generate_report(project)

        with Path(output_file).open("r") as f:
            content = f.read()

        # Flagged video should be present
        assert "video0" in content
        # Unflagged video should not be present
        assert "unflagged" not in content

    def test_generate_report_includes_notes(self, create_project_with_flagged_videos):
        """Test that video notes are included in report."""
        project = create_project_with_flagged_videos(num_flagged=2)
        output_file = generate_report(project)

        with Path(output_file).open("r") as f:
            content = f.read()

        assert "Note for video 0" in content
        assert "Note for video 1" in content

    def test_generate_report_includes_hashes(self, create_project_with_flagged_videos):
        """Test that video hashes are included in report."""
        project = create_project_with_flagged_videos(num_flagged=1)
        video = project.video_files[0]
        expected_hash = video.sha256_hash

        output_file = generate_report(project)

        with Path(output_file).open("r") as f:
            content = f.read()

        assert expected_hash in content

    def test_generate_report_html_structure(self, create_project_with_flagged_videos):
        """Test that report has valid HTML structure."""
        project = create_project_with_flagged_videos(num_flagged=1)
        output_file = generate_report(project)

        with Path(output_file).open("r") as f:
            content = f.read()

        # Check for basic HTML elements
        assert "<html>" in content
        assert "</html>" in content
        assert "<head>" in content
        assert "<body>" in content
        assert "<title>" in content

    def test_generate_report_includes_javascript(
        self, create_project_with_flagged_videos
    ):
        """Test that report includes JavaScript for interactivity."""
        project = create_project_with_flagged_videos(num_flagged=1)
        output_file = generate_report(project)

        with Path(output_file).open("r") as f:
            content = f.read()

        assert "<script>" in content
        assert "function openFiles" in content
        assert "const notes" in content
        assert "const hashes" in content

    def test_generate_report_includes_styling(self, create_project_with_flagged_videos):
        """Test that report includes CSS styling."""
        project = create_project_with_flagged_videos(num_flagged=1)
        output_file = generate_report(project)

        with Path(output_file).open("r") as f:
            content = f.read()

        assert "<style>" in content
        assert ".split" in content
        assert ".left" in content
        assert ".right" in content

    def test_generate_report_with_no_flagged_videos(self, temp_dir):
        """Test report generation with no flagged videos."""
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "project"
        input_dir.mkdir()
        output_dir.mkdir()
        (output_dir / "Reports").mkdir()

        project_info = ProjectInfo(
            input_dir=input_dir,
            output_dir=output_dir,
            case_name="No Flags",
            investigator_name="Tester",
            report_path="/tmp/report.html",
        )

        project_structure = ProjectStructure(
            projectInfo=project_info,
            video_files=[],
            image_files=[],
            other_files=[],
        )

        output_file = generate_report(project_structure)

        # Should still create a report file
        assert Path(output_file).exists()

        with Path(output_file).open("r") as f:
            content = f.read()

        # Should contain case info but no video links
        assert "No Flags" in content
        assert "Tester" in content

    def test_generate_report_returns_path(self, create_project_with_flagged_videos):
        """Test that generate_report returns the output file path."""
        project = create_project_with_flagged_videos(num_flagged=1)
        output_file = generate_report(project)

        assert isinstance(output_file, Path)
        assert output_file.exists()

    def test_generate_report_includes_iframes(self, create_project_with_flagged_videos):
        """Test that report includes iframe elements for maps and graphs."""
        project = create_project_with_flagged_videos(num_flagged=1)
        output_file = generate_report(project)

        with Path(output_file).open("r") as f:
            content = f.read()

        assert '<iframe id="map-iframe"' in content
        assert '<iframe id="graph-iframe"' in content

    def test_generate_report_video_links(self, create_project_with_flagged_videos):
        """Test that video links are properly formatted."""
        project = create_project_with_flagged_videos(num_flagged=1)
        output_file = generate_report(project)

        with Path(output_file).open("r") as f:
            content = f.read()

        # Should contain list items with links
        assert "<li>" in content
        assert "<a href=" in content
        assert "onclick=" in content
