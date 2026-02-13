import json
import logging
from pathlib import Path

from dashcam_investigator.project_manager.project_datatypes import (
    ProjectInfo,
    ProjectStructure,
)
from dashcam_investigator.utils.custom_json_functions import (
    ProjectEncoder,
    project_decoder,
)

logger = logging.getLogger(__name__)

DASHCAM_INVESTIGATOR_PROJECT_FILENAME = "dashcam_investigator.json"
DASHCAM_INVESTIGATOR_DIRECTORIES = [
    "Graphs",
    "Maps",
    "Metadata",
    "Reports",
    "Timelines",
]


class ProjectManager:
    def __init__(
        self,
        input_dir: Path = None,
        output_dir: Path = None,
        case_name: str = "",
        investigator_name: str = "",
    ) -> None:
        self.project_info = ProjectInfo(
            input_dir, output_dir, case_name, investigator_name, ""
        )
        self.project_directory = output_dir
        self.project_file = (
            Path(self.project_directory, DASHCAM_INVESTIGATOR_PROJECT_FILENAME)
            if self.project_directory is not None
            else None
        )

    def new_project(self) -> ProjectStructure:
        """
        This function performs the setup for a new project.
        It creates the required directories and the project file.
        """
        logger.debug(f"Creating a new project in -> {self.project_directory}")
        # Create the output directory if it does not exist
        if not self.project_directory.exists():
            logger.debug(
                f"Target project directory does not exist. Creating directory -> {self.project_directory}"
            )
            self.project_directory.mkdir()

        # Create maps, timelines, metadata and reports folders within the project directory
        logger.debug(
            f"Creating Maps, Metdata, Reports and Timelines directories in -> {self.project_directory}"
        )
        for dir in DASHCAM_INVESTIGATOR_DIRECTORIES:
            Path(self.project_directory, dir).mkdir(exist_ok=True)
            logger.debug(f"Created {dir}")

        # Create the json project file
        if not self.project_file.exists():
            logger.debug(f"Creating project file in -> {self.project_directory}")
            self.project_directory.touch(DASHCAM_INVESTIGATOR_PROJECT_FILENAME)

        # Initialise the ProjectStructure object that is to be written to the JSON file
        logger.debug("Intialising project file")
        project_structure = ProjectStructure(
            projectInfo=self.project_info,
            video_files=[],
            image_files=[],
            other_files=[],
        )
        # Write to file
        self.write_project_file(project_structure)
        logger.debug(f"Intialised project file -> {self.project_file}")

        # return the project structure object so it can be updated later on
        return project_structure

    def load_existing_project(self, project_path: Path) -> ProjectStructure:
        """
        Reads an existing 'dashcam_investigator.json' file and loads the read data into variables.
        """
        self.project_file = project_path
        project_structure = self.read_project_file()

        logger.debug("Read project file. Assigning read data to variables.")
        # Assign read data to object variables
        self.project_info = project_structure.project_info
        self.project_directory = self.project_info.project_directory

        return project_structure

    def write_project_file(self, data: ProjectStructure) -> None:
        """
        This function initialises the base project file with minimal information declared in ProjectStructure
        """
        # Write the JSON object into the file
        with self.project_file.open("w") as file:
            json.dump(
                obj=data.JSON_object(),
                fp=file,
                cls=ProjectEncoder,
                indent=4,
            )
        logger.debug(f"Wrote to project file at -> {self.project_file}")

    def read_project_file(self) -> ProjectStructure:
        """
        This function reads an existing dashcam_investigator.json project file.
        It loads the read data into a ProjectStrucutre object which can be used later on.
        """
        # Load existing project structure
        logger.debug(f"Reading project file -> {self.project_file}")
        with self.project_file.open("r") as file:
            project_json: ProjectStructure = json.load(
                fp=file, object_hook=project_decoder
            )
        return project_json
