import json
from pathlib import Path
from typing import Union

from dashcam_investigator.project_manager.project_datatypes import (
    FileAttributes,
    ProjectInfo,
    ProjectStructure,
)


class ProjectEncoder(json.JSONEncoder):
    """
    Define a JSON encoder which overrides the default implementation.
    Checks for a JSON_object aatribute and calls the function to allow writing nested objects to JSON.
    """

    def default(self, o):
        if hasattr(o, "JSON_object"):
            return o.JSON_object()

        return json.JSONEncoder.default(self, o)


def project_decoder(dictionary: dict) -> Union[dict, ProjectStructure]:
    """
    Converts a JSON dictionary into a ProjectStructure object if the tool_name attribute is present.
    params: dictinary -> JSON dictionary
    returns: ProjectStructure or unmodified dictionary
    """
    video_files = []
    image_files = []
    other_files = []

    if "tool_name" in dictionary:
        video_files = convert_to_file_attr(dictionary["video_files"])
        image_files = convert_to_file_attr(dictionary["image_files"])
        other_files = convert_to_file_attr(dictionary["other_files"])

        return ProjectStructure(
            projectInfo=convert_to_project_info(dictionary["project_info"]),
            video_files=video_files,
            image_files=image_files,
            other_files=other_files,
            tool_name=dictionary["tool_name"],
        )
    # Else return the dictionary unchanged
    return dictionary


def convert_to_project_info(proj_info: list) -> ProjectInfo:
    """
    Converts a JSON object into a ProjectInfo object
    params: proj_info -> list
    returns: ProjectInfo
    """
    project = ProjectInfo(
        input_dir=Path(proj_info["input_directory"]),
        output_dir=Path(proj_info["project_directory"]),
        date_created=proj_info["date_created"],
        case_name=proj_info["case_name"],
        investigator_name=proj_info["investigator_name"],
        report_path=proj_info["report_path"],
    )
    # Restore count fields if present
    project.num_videos = proj_info.get("num_videos")
    project.num_images = proj_info.get("num_images")
    project.num_other = proj_info.get("num_other")
    return project


def convert_to_file_attr(input_list: list) -> list:
    """
    Converts a list of JSON objects into a FileAttributes object.
    params: input_list -> list
    returns: output_list -> list of file attribute objects
    """
    output_list = []

    for item in input_list:
        output_list.append(
            FileAttributes(
                file_path=Path(item["file_path"]),
                name=item["name"],
                ftype=item["type"],
                sha256_hash=item["sha256_hash"],
                meta_files=item["meta_files"],
                output_files=item["output_files"],
                flagged=item["flagged"],
                notes=item["notes"],
            )
        )
    return output_list
