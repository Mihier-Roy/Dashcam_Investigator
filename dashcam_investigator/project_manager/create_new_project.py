import logging
from pathlib import Path
from core.extract_metadata import process_file_meta, process_gps_data
from core.output_generator import OutputGenerator
from core.walk_directory import walk_directory
from project_manager.project_datatypes import ProjectStructure
from project_manager.project_manager import ProjectManager

logger = logging.getLogger(__name__)


def create_new_project(project_manager: ProjectManager) -> ProjectStructure:
    """
    Accepts an input and output directory, creates a new project and processes files within the directory.
    It extracts/creates and saves GPS & file metadata, maps and graphs.
    Finally, it returns a project_object with data for the current project.
    """
    project_object = project_manager.new_project()

    # Walk through the directory and categorise files based on MIME type
    (
        project_object.video_files,
        project_object.image_files,
        project_object.other_files,
    ) = walk_directory(input_dir=project_object.project_info.input_directory)

    # Write updated object to file
    project_manager.write_project_file(data=project_object)

    # Extract metadata for all video files
    for index, video in enumerate(project_object.video_files):
        logger.debug(f"Processing video {index+1}/{len(project_object.video_files)}")
        gps_data = process_gps_data(
            video_path=Path(video.file_path),
            output_dir=Path(project_object.project_info.project_directory, "Metadata"),
        )
        video.meta_files.append(gps_data)
        file_meta = process_file_meta(
            video_path=Path(video.file_path),
            output_dir=Path(project_object.project_info.project_directory, "Metadata"),
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

    # Save updated object to file
    project_manager.write_project_file(data=project_object)

    return project_object
