import json
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
    if "tool_name" in dictionary:
        return ProjectStructure(
            projectInfo=dictionary["project_info"],
            files_identified=dictionary["files_identified"],
            tool_name=dictionary["tool_name"],
        )
    # Else return the dictionary unchanged
    return dictionary
