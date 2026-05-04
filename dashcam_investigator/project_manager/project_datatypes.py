from datetime import datetime
from pathlib import Path

from dashcam_investigator.constants import TOOL_NAME
from dashcam_investigator.utils.common import generate_file_hash


class ProjectInfo:
    """
    Records the high-level information of an investigation project.
    """

    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        case_name: str,
        investigator_name: str,
        report_path: str,
        date_created=None,
    ) -> None:
        self.input_directory = input_dir
        self.project_directory = output_dir
        self.date_created = (
            datetime.now().isoformat() if date_created is None else date_created
        )
        self.case_name = case_name
        self.investigator_name = investigator_name
        self.report_path = report_path
        self.num_videos = None
        self.num_images = None
        self.num_other = None

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation of this object."""
        return {
            "input_directory": str(self.input_directory.resolve()),
            "project_directory": str(self.project_directory.resolve()),
            "date_created": self.date_created,
            "case_name": self.case_name,
            "investigator_name": self.investigator_name,
            "report_path": self.report_path,
            "num_videos": self.num_videos,
            "num_images": self.num_images,
            "num_other": self.num_other,
        }


class FileAttributes:
    """
    Records the details of a file identified in an input directory.
    Saved to the project's JSON file for use throughout the application.
    """

    def __init__(
        self,
        file_path: Path,
        name=None,
        ftype=None,
        sha256_hash=None,
        meta_files=None,  # dict with keys "gpx" and "csv"
        output_files=None,
        flagged=None,
        notes=None,
    ) -> None:
        self.file_path = file_path
        self.name = self.file_path.name if name is None else name
        self.type = self.file_path.suffix if ftype is None else ftype
        # Store the hash only if provided; compute lazily on first access.
        self._sha256_hash: str | None = sha256_hash
        self.meta_files = {} if meta_files is None else meta_files
        self.output_files = [] if output_files is None else output_files
        self.flagged = False if flagged is None else flagged
        self.notes = "" if notes is None else notes

    @property
    def sha256_hash(self) -> str:
        if self._sha256_hash is None:
            self._sha256_hash = generate_file_hash(self.file_path)
        return self._sha256_hash

    @sha256_hash.setter
    def sha256_hash(self, value: str) -> None:
        self._sha256_hash = value

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation of this object."""
        return {
            "file_path": str(self.file_path.resolve()),
            "name": self.name,
            "type": self.type,
            "sha256_hash": self.sha256_hash,
            "meta_files": self.meta_files,
            "output_files": self.output_files,
            "flagged": self.flagged,
            "notes": self.notes,
        }


class ProjectStructure:
    """
    Describes the overall structure of 'dashcam_investigator.json'.
    """

    def __init__(
        self,
        projectInfo: ProjectInfo,
        video_files: list[FileAttributes],
        image_files: list[FileAttributes],
        other_files: list[FileAttributes],
        tool_name: str = TOOL_NAME,
    ) -> None:
        self.tool_name: str = tool_name
        self.project_info: ProjectInfo = projectInfo
        self.video_files: list[FileAttributes] = video_files
        self.image_files: list[FileAttributes] = image_files
        self.other_files: list[FileAttributes] = other_files

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation of this object."""
        return {
            "tool_name": self.tool_name,
            "project_info": self.project_info,
            "video_files": self.video_files,
            "image_files": self.image_files,
            "other_files": self.other_files,
        }
