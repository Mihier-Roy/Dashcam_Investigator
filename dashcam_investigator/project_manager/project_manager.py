import json
from pathlib import Path
import logging
from utils.custom_json_functions import ProjectEncoder, project_decoder
from project_manager.project_datatypes import (
    ProjectStructure,
    ProjectInfo,
    FileAttributes,
)

logger = logging.getLogger(__name__)

DASHCAM_INVESTIGATOR_PROJECT_FILENAME = "dashcam_investigator.json"
DASHCAM_INVESTIGATOR_DIRECTORIES = ["Maps", "Metadata", "Reports", "Timelines"]


class ProjectManager:
    def __init__(self, input_dir, output_dir) -> None:
        self.project_info = ProjectInfo(input_dir, output_dir)
        self.project_directory = Path(output_dir)
        self.project_file = Path(
            self.project_directory, DASHCAM_INVESTIGATOR_PROJECT_FILENAME
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

        # Initialise the project file
        project_structure = self.initialise_project_file()
        # return the project structure object so it can be updated later on
        return project_structure

    def initialise_project_file(self) -> ProjectStructure:
        """
        This function initialises the base project file with minimal information declared in ProjectStructure
        """
        # Create the json project file
        if not self.project_file.exists():
            logger.debug(f"Creating project file in -> {self.project_directory}")
            self.project_directory.touch(DASHCAM_INVESTIGATOR_PROJECT_FILENAME)

        # Initialise the ProjectStructure object that is to be written to the JSON file
        project_structure = ProjectStructure(
            projectInfo=self.project_info, files_identified=[]
        )
        logger.debug(f"Intialising project file")
        # Write the JSON object into the file
        with self.project_file.open("w") as file:
            json.dump(
                obj=project_structure.JSON_object(),
                fp=file,
                cls=ProjectEncoder,
                indent=4,
            )
        logger.debug(f"Succsfully intialised project file at -> {self.project_file}")
        return project_structure

    def update_files_identified(self, data: FileAttributes) -> None:
        """
        This function updates the files_identified section of the project file.
        It loads the current project information and updates the files_identified section.
        The file is then overwritten with the new data.
        """
        # Load existing project structure
        logger.debug(f"Reading project file -> {self.project_file}")
        with self.project_file.open("r") as file:
            project_json: ProjectStructure = json.load(
                fp=file, object_hook=project_decoder
            )

        # Update the files_identified section
        logger.debug(f"Updating files_identified -> {self.project_file}")
        project_json.files_identified.append(data)

        # Save updated project data
        with self.project_file.open("w") as file:
            json.dump(
                obj=project_json.JSON_object(),
                fp=file,
                cls=ProjectEncoder,
                indent=4,
            )
