import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
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


def _process_video_file(
    item: Path, project_dir: Path, status_callback
) -> FileAttributes:
    video = FileAttributes(item)
    try:
        _emit_status(status_callback, f"Extracting metadata: {item.name}")
        video = extract_meta(video, project_dir)
        _emit_status(status_callback, f"Generating map: {item.name}")
        video = create_map(video, project_dir)
    except DashcamInvestigatorError as exc:
        logger.warning("Skipping %s: %s", item.name, exc)
    return video


def process_files(
    input_path: Path, project_object, progress_callback, status_callback=None
) -> ProjectStructure:
    """
    Identifies file types, extracts metadata, and builds maps for each video found.
    Video files are processed concurrently; other file types are classified inline.
    """
    project_dir = project_object.project_info.project_directory
    current_progress = 1
    video_paths: list[Path] = []

    for item in Path(input_path).rglob("*"):
        if not item.is_file():
            continue
        file_type = filetype.guess_mime(item.resolve())
        if file_type is not None:
            prefix = file_type.split("/")[0]
            if prefix == "video":
                logger.debug(f"Video found : {item.name}")
                video_paths.append(item)
                continue
            elif prefix == "image":
                logger.debug(f"Image found : {item.name}")
                project_object.image_files.append(FileAttributes(item))
        else:
            logger.debug(f"Other file found: {item.name}")
            project_object.other_files.append(FileAttributes(item))
        progress_callback.emit(current_progress)
        current_progress += 1

    with ThreadPoolExecutor() as executor:
        future_to_item = {
            executor.submit(
                _process_video_file, item, project_dir, status_callback
            ): item
            for item in video_paths
        }
        for future in as_completed(future_to_item):
            progress_callback.emit(current_progress)
            current_progress += 1
            project_object.video_files.append(future.result())

    project_object.project_info.num_videos = len(project_object.video_files)
    project_object.project_info.num_images = len(project_object.image_files)
    project_object.project_info.num_other = len(project_object.other_files)

    return project_object


def extract_meta(video: FileAttributes, project_dir: Path) -> FileAttributes:
    """
    Extracts GPS and file metadata concurrently and stores the paths in FileAttributes.
    """
    meta_dir = Path(project_dir, ProjectSubdir.METADATA)
    video_path = Path(video.file_path)
    with ThreadPoolExecutor(max_workers=2) as executor:
        gps_future = executor.submit(
            process_gps_data, video_path=video_path, output_dir=meta_dir
        )
        csv_future = executor.submit(
            process_file_meta, video_path=video_path, output_dir=meta_dir
        )
        gps_path = gps_future.result()
        csv_path = csv_future.result()
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
