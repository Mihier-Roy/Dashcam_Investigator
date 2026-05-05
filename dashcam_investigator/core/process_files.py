import logging
from pathlib import Path

import filetype

from dashcam_investigator.constants import ProjectSubdir
from dashcam_investigator.core.extract_metadata import (
    process_file_meta,
    process_gps_data,
)
from dashcam_investigator.core.output_generator import OutputGenerator
from dashcam_investigator.exceptions import DashcamInvestigatorError
from dashcam_investigator.project_manager.project_datatypes import (
    FileAttributes,
    ProjectStructure,
)

logger = logging.getLogger(__name__)


def _emit_status(callback, msg: str) -> None:
    if callback is not None:
        callback.emit(msg)


def process_files(
    input_path: Path, project_object, progress_callback, status_callback=None
) -> ProjectStructure:
    """
    Identifies file types, extracts metadata, and builds maps for each video found.
    """
    project_dir = project_object.project_info.project_directory
    current_progress = 1
    for item in Path(input_path).rglob("*"):
        if item.is_file():
            progress_callback.emit(current_progress)
            current_progress += 1

            file_type = filetype.guess_mime(item.resolve())
            if file_type is not None:
                if file_type.split("/")[0] == "video":
                    logger.debug(f"Video found : {item.name}")
                    video = FileAttributes(item)
                    try:
                        _emit_status(
                            status_callback, f"Extracting metadata: {item.name}"
                        )
                        video = extract_meta(video, project_dir)
                        _emit_status(status_callback, f"Generating map: {item.name}")
                        video = create_map(video, project_dir)
                    except DashcamInvestigatorError as exc:
                        logger.warning("Skipping %s: %s", item.name, exc)
                    project_object.video_files.append(video)

                elif file_type.split("/")[0] == "image":
                    logger.debug(f"Image found : {item.name}")
                    project_object.image_files.append(FileAttributes(item))
            else:
                logger.debug(f"Other file found: {item.name}")
                project_object.other_files.append(FileAttributes(item))

    project_object.project_info.num_videos = len(project_object.video_files)
    project_object.project_info.num_images = len(project_object.image_files)
    project_object.project_info.num_other = len(project_object.other_files)

    return project_object


def extract_meta(video: FileAttributes, project_dir: Path) -> FileAttributes:
    """
    Extracts GPS and file metadata and stores the paths as a dict in the FileAttributes object.
    """
    meta_dir = Path(project_dir, ProjectSubdir.METADATA)
    gps_path = process_gps_data(
        video_path=Path(video.file_path),
        output_dir=meta_dir,
    )
    csv_path = process_file_meta(
        video_path=Path(video.file_path),
        output_dir=meta_dir,
    )
    video.meta_files = {"gpx": str(gps_path), "csv": str(csv_path)}
    return video


def create_map(video: FileAttributes, project_dir: Path) -> FileAttributes:
    """
    Generates a route map and speed graph, saving their paths in the FileAttributes object.
    """
    video_stem = Path(video.name).stem
    map_output = Path(project_dir, ProjectSubdir.MAPS, f"{video_stem}_map.html")
    graph_output = Path(
        project_dir, ProjectSubdir.GRAPHS, f"{video_stem}_speed_graph.html"
    )
    output_generator = OutputGenerator()
    output_generator.generate_map(video_file=video, output_path=map_output)
    video.output_files.append(str(map_output.resolve()))
    output_generator.generate_speed_chart(output_path=graph_output)
    video.output_files.append(str(graph_output.resolve()))
    return video
