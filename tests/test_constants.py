from dashcam_investigator.constants import (
    EXIFTOOL_TIMEOUT_SECONDS,
    GPX_FORMAT_FILE,
    PROJECT_FILE_NAME,
    TOOL_NAME,
    ProjectSubdir,
)


def test_project_subdirs_are_strings():
    for subdir in ProjectSubdir:
        assert isinstance(subdir, str)


def test_project_subdir_values():
    assert ProjectSubdir.METADATA == "Metadata"
    assert ProjectSubdir.MAPS == "Maps"
    assert ProjectSubdir.GRAPHS == "Graphs"
    assert ProjectSubdir.REPORTS == "Reports"


def test_tool_name_spelling():
    assert "Dashcam" in TOOL_NAME
    assert "Dascam" not in TOOL_NAME


def test_constants_types():
    assert isinstance(PROJECT_FILE_NAME, str)
    assert isinstance(GPX_FORMAT_FILE, str)
    assert isinstance(EXIFTOOL_TIMEOUT_SECONDS, int)
    assert EXIFTOOL_TIMEOUT_SECONDS > 0
