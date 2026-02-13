import logging
from pathlib import Path

import filetype

from dashcam_investigator.core.extract_metadata import (
    process_file_meta,
    process_gps_data,
)
from dashcam_investigator.core.output_generator import OutputGenerator
from dashcam_investigator.project_manager.project_datatypes import (
    FileAttributes,
    ProjectStructure,
)

logger = logging.getLogger(__name__)


def process_files(
    input_path: Path, project_object, progress_callback
) -> ProjectStructure:
    """
    This function identifies the file type and computes a FileAttributes object which is saved to the project file.
    """
    project_dir = project_object.project_info.project_directory
    current_progress = 1
    for item in Path(input_path).rglob("*"):
        if item.is_file():
            # Emit the current progress
            # Value sent will be picked up by the update_progress_dialog function (app.py)
            progress_callback.emit(current_progress)
            current_progress += 1

            file_type = filetype.guess_mime(item.resolve())
            if file_type is not None:
                if file_type.split("/")[0] == "video":
                    logger.debug(f"Video found : {item.name}")
                    video = FileAttributes(item)
                    # Extract metadata
                    video = extract_meta(video, project_dir)
                    # Create maps
                    video = create_map(video, project_dir)
                    # Update object
                    project_object.video_files.append(video)

                elif file_type.split("/")[0] == "image":
                    logger.debug(f"Image found : {item.name}")
                    project_object.image_files.append(FileAttributes(item))
            else:
                logger.debug(f"Other file found: {item.name}")
                project_object.other_files.append(FileAttributes(item))

    # Write count of videos, images, and other files discovered
    project_object.project_info.num_videos = len(project_object.video_files)
    project_object.project_info.num_images = len(project_object.image_files)
    project_object.project_info.num_other = len(project_object.other_files)

    return project_object


def extract_meta(video: FileAttributes, project_dir: Path) -> FileAttributes:
    """
    Extracts GPS and file metadata and saves the paths of these files in the FileAttributes object
    """
    gps_data = process_gps_data(
        video_path=Path(video.file_path),
        output_dir=Path(project_dir, "Metadata"),
    )
    video.meta_files.append(gps_data)
    file_meta = process_file_meta(
        video_path=Path(video.file_path),
        output_dir=Path(project_dir, "Metadata"),
    )
    video.meta_files.append(file_meta)

    return video


def create_map(video: FileAttributes, project_dir: Path) -> FileAttributes:
    """
    Generates a map and saves the paths of the map in the FileAttributes object
    """
    video_name = video.name[0:-4]
    map_output = Path(project_dir, "Maps", f"{video_name}_map.html")
    graph_output = Path(project_dir, "Graphs", f"{video_name}_speed_graph.html")
    output_generator = OutputGenerator()
    # Generate route map and save output file
    output_generator.generate_map(video_file=video, output_path=map_output)
    video.output_files.append(str(map_output.resolve()))
    # Generate speed graph and save output file
    output_generator.generate_speed_chart(output_path=graph_output)
    video.output_files.append(str(graph_output.resolve()))

    return video
