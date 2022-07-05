import logging
import logging.config
from pathlib import Path
import os
from core.walk_directory import walk_directory
from core.extract_metadata import process_gps_data
from project_manager.project_datatypes import FileAttributes
from project_manager.project_manager import ProjectManager
from gui import app

if __name__ == "__main__":
    # Create a logs directory in AppData\Local\DashcamInvestigator if it doesn't already exist
    appdata_local = os.getenv("LOCALAPPDATA")
    log_path = Path(appdata_local, "DashcamInvestigator", "Logs")
    log_path = str(log_path).replace("\\", "/")
    if not Path(log_path).exists():
        Path(log_path).mkdir(parents=True, exist_ok=True)

    # Setup logging based on log.conf
    logging.config.fileConfig(
        "log.conf", defaults={"logPath": log_path}, disable_existing_loggers=False
    )

    # Launch GUI
    # app.run()
    # main()
    input_path = Path("H:\\DissertationDataset\\Trancend\\DP220")
    output_path = Path("E:\\Output_Trancend")

    # If project exists, load project
    if Path(output_path, "dashcam_investigator.json").exists():
        project_manager = ProjectManager()
        project_object = project_manager.load_existing_project(
            Path(output_path, "dashcam_investigator.json")
        )
    else:
        # Create and intialise a new project
        project_manager = ProjectManager(input_dir=input_path, output_dir=output_path)
        project_object = project_manager.new_project()

        # Walk through the directory and categorise files based on MIME type
        (
            project_object.video_files,
            project_object.image_files,
            project_object.other_files,
        ) = walk_directory(input_dir=input_path)

        # Write updated object to file
        project_manager.write_project_file(data=project_object)

    # Extract GPS data for all video files
    for i in range(0, 1):
        print(f"{project_object.video_files[0].name}")
        gps_data = process_gps_data(
            video_path=Path(project_object.video_files[0].file_path),
            output_dir=Path(project_object.project_info.project_directory, "Metadata"),
        )
        project_object.video_files[0].meta_files.append(gps_data)

    project_manager.write_project_file(data=project_object)
    print("test")
