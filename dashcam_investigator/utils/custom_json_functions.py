import json
from typing import Union

from dashcam_investigator.constants import TOOL_NAME
from dashcam_investigator.project_manager.project_datatypes import (
    FileAttributes,
    ProjectInfo,
    ProjectStructure,
)


class ProjectEncoder(json.JSONEncoder):
    """
    Define a JSON encoder which overrides the default implementation.
    Checks for a to_dict attribute and calls the function to allow writing nested objects to JSON.
    """

    def default(self, o):
        if hasattr(o, "to_dict"):
            return o.to_dict()

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
            tool_name=TOOL_NAME,  # normalize: old files may have had a typo
        )
    # Else return the dictionary unchanged
    return dictionary


def convert_to_project_info(proj_info: dict) -> ProjectInfo:
    """
    Converts a JSON object into a ProjectInfo object.
    params: proj_info -> dict
    returns: ProjectInfo
    """
    return ProjectInfo.from_dict(proj_info)


def convert_to_file_attr(input_list: list) -> list:
    """
    Converts a list of JSON objects into FileAttributes objects.
    params: input_list -> list
    returns: output_list -> list of file attribute objects
    """
    return [FileAttributes.from_dict(item) for item in input_list]
