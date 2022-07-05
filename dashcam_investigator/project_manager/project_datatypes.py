from pathlib import Path
from datetime import datetime
from utils.generate_file_hash import generate_file_hash


class ProjectInfo:
    """
    Objects of this class record the high level information of the project.
    """

    def __init__(
        self, input_dir: Path, output_dir: Path, case_name: str, investigator_name: str
    ) -> None:
        self.input_directory = input_dir
        self.project_directory = output_dir
        self.date_created = datetime.now().isoformat()
        self.case_name = ""
        self.investigator_name = ""

    def JSON_object(self) -> dict:
        return dict(
            input_directory=str(self.input_directory.resolve()),
            project_directory=str(self.project_directory.resolve()),
            date_created=self.date_created,
            case_name=self.case_name,
            investigator_name=self.investigator_name,
        )


class FileAttributes:
    """
    Objects of this class are used to record the details of each file identified in an input directory.
    These files are saved to the project's JSON file for use throughout the application.
    """

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.name = self.file_path.name
        self.type = self.file_path.suffix
        self.sha256_hash = generate_file_hash(self.file_path)
        self.meta_files = []
        self.output_files = []
        self.flagged = False
        self.notes = ""

    def JSON_object(self) -> dict:
        return dict(
            file_path=str(self.file_path.resolve()),
            name=self.name,
            type=self.type,
            sha256_hash=self.sha256_hash,
            meta_files=self.meta_files,
            output_files=self.output_files,
            flagged=self.flagged,
            notes=self.notes,
        )


class ProjectStructure:
    """
    This class describes the overall structure of 'dashcam_investigator.json'
    """

    def __init__(
        self,
        projectInfo: ProjectInfo,
        video_files: list[FileAttributes],
        image_files: list[FileAttributes],
        other_files: list[FileAttributes],
        tool_name: str = "Dascam Investigator",
    ) -> None:
        self.tool_name: str = tool_name
        self.project_info: ProjectInfo = projectInfo
        self.video_files: list[FileAttributes] = video_files
        self.image_files: list[FileAttributes] = image_files
        self.other_files: list[FileAttributes] = other_files

    def JSON_object(self) -> dict:
        return dict(
            tool_name=self.tool_name,
            project_info=self.project_info,
            video_files=self.video_files,
            image_files=self.image_files,
            other_files=self.other_files,
        )
