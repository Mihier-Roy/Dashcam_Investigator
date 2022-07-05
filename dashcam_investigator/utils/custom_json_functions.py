import json
from pathlib import Path
from project_manager.project_datatypes import (
    ProjectStructure,
    ProjectInfo,
    FileAttributes,
)


class ProjectEncoder(json.JSONEncoder):
    """
    Define a JSON encoder which overrides the default implementation.
    This definition checks for the presence of a JSON_object function so that nested objects can be written to JSON.
    """

    def default(self, obj):
        if hasattr(obj, "JSON_object"):
            return obj.JSON_object()
        else:
            return json.JSONEncoder.default(self, obj)


def project_decoder(dictionary):
    # If the json dictionary contains the tool_name key, then convert the dictionary to the ProjectStructure object
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


def convert_to_project_info(projInfo):
    return ProjectInfo(
        input_dir=Path(projInfo["input_directory"]),
        output_dir=Path(projInfo["project_directory"]),
        date_created=projInfo["date_created"],
        case_name=projInfo["case_name"],
        investigator_name=projInfo["investigator_name"],
    )


def convert_to_file_attr(input_list):
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
