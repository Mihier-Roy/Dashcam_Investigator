from pathlib import Path
from datetime import datetime
from utils.generate_file_hash import generate_file_hash


class ProjectInfo:
    """
    Objects of this class record the high level information of the project.
    """

    def __init__(self, input_dir, output_dir) -> None:
        self.input_directory = str(Path(input_dir).resolve())
        self.project_directory = str(Path(output_dir).resolve())
        self.date_created = datetime.now().isoformat()

    def JSON_object(self) -> dict:
        return dict(
            input_directory=self.input_directory,
            project_directory=self.project_directory,
            date_created=self.date_created,
        )


class FileAttributes:
    """
    Objects of this class are used to record the details of each file identified in an input directory.
    These files are saved to the project's JSON file for use throughout the application.
    """

    def __init__(self, file_path) -> None:
        self.file_path = str(Path(file_path).resolve())
        self.name = self.file_path.name
        self.type = self.file_path.suffix
        self.sha256_hash = generate_file_hash(self.file_path)
        self.meta_files, self.output_files = []
        self.flagged = False
        self.notes = ""

    def JSON_object(self) -> dict:
        return dict(
            file_path=self.file_path,
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

    def __init__(self, projectInfo: ProjectInfo) -> None:
        self.tool_name: str = "Dashcam Investigator"
        self.project_info: ProjectInfo = projectInfo
        self.files_identified: list[FileAttributes] = []

    def JSON_object(self) -> dict:
        return dict(
            tool_name=self.tool_name,
            project_info=self.project_info,
            files_identified=self.files_identified,
        )
