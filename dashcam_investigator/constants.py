from enum import StrEnum


class ProjectSubdir(StrEnum):
    METADATA = "Metadata"
    MAPS = "Maps"
    GRAPHS = "Graphs"
    REPORTS = "Reports"


PROJECT_FILE_NAME = "dashcam_investigator.json"
TOOL_NAME = "Dashcam Investigator"
GPX_FORMAT_FILE = "gpx.fmt"
EXIFTOOL_TIMEOUT_SECONDS = 120
