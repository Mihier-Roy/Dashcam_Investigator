import logging
import logging.config
from pathlib import Path
import os
from core.walk_directory import walk_directory
from core.extract_metadata import process_gps_data, process_file_meta
from core.output_generator import OutputGenerator
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

    logger = logging.getLogger(__name__)

    # Launch GUI
    # app.run()
    # main()
    input_path = Path("H:\\DissertationDataset\\Nextbase312")
    output_path = Path("E:\\Output_Nextbase_312")

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

        # Extract metadata for all video files
        for index, video in enumerate(project_object.video_files):
            logger.debug(
                f"Processing video {index+1}/{len(project_object.video_files)}"
            )
            gps_data = process_gps_data(
                video_path=Path(video.file_path),
                output_dir=Path(
                    project_object.project_info.project_directory, "Metadata"
                ),
            )
            video.meta_files.append(gps_data)
            file_meta = process_file_meta(
                video_path=Path(video.file_path),
                output_dir=Path(
                    project_object.project_info.project_directory, "Metadata"
                ),
            )
            video.meta_files.append(file_meta)

        project_manager.write_project_file(data=project_object)

        # Generate map and speed graph from extracted metadata
        for index, video in enumerate(project_object.video_files):
            logger.debug(
                f"Processed output for {index+1}/{len(project_object.video_files)}"
            )
            video_name = video.name[0:-4]
            logger.debug(f"Video name -> {video_name}")
            map_output = Path(
                project_object.project_info.project_directory,
                "Maps",
                f"{video_name}_map.html",
            )
            graph_output = Path(
                project_object.project_info.project_directory,
                "Graphs",
                f"{video_name}_speed_graph.html",
            )
            output_generator = OutputGenerator()
            # Generate route map and save output file
            output_generator.generate_map(video_file=video, output_path=map_output)
            video.output_files.append(str(map_output.resolve()))
            # Generate speed graph and save output file
            output_generator.generate_speed_chart(output_path=graph_output)
            video.output_files.append(str(graph_output.resolve()))

        project_manager.write_project_file(data=project_object)
