import json
from collections import namedtuple
from project_manager.project_datatypes import ProjectStructure


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
            projectInfo=dictionary["project_info"],
            video_files=video_files,
            image_files=image_files,
            other_files=other_files,
            tool_name=dictionary["tool_name"],
        )
    # Else return the dictionary unchanged
    return dictionary


def convert_to_file_attr(input_list):
    output_list = []
    file_attr = namedtuple(
        "FileAttributes",
        "file_path name type sha256_hash meta_files output_files flagged notes",
    )

    for item in input_list:
        output_list.append(
            file_attr(
                file_path=item["file_path"],
                name=item["name"],
                type=item["type"],
                sha256_hash=item["sha256_hash"],
                meta_files=item["meta_files"],
                output_files=item["output_files"],
                flagged=item["flagged"],
                notes=item["notes"],
            )
        )
    return output_list
