import pytest

from dashcam_investigator.exceptions import (
    DashcamInvestigatorError,
    ExifToolError,
    GPSParseError,
    MetadataExtractionError,
    ProjectLoadError,
    ProjectSaveError,
)


@pytest.mark.parametrize(
    "exc_class",
    [
        ExifToolError,
        MetadataExtractionError,
        GPSParseError,
        ProjectLoadError,
        ProjectSaveError,
    ],
)
def test_all_exceptions_inherit_from_base(exc_class):
    assert issubclass(exc_class, DashcamInvestigatorError)


@pytest.mark.parametrize(
    "exc_class",
    [
        DashcamInvestigatorError,
        ExifToolError,
        MetadataExtractionError,
        GPSParseError,
        ProjectLoadError,
        ProjectSaveError,
    ],
)
def test_all_exceptions_inherit_from_builtin_exception(exc_class):
    assert issubclass(exc_class, Exception)


@pytest.mark.parametrize(
    "exc_class, message",
    [
        (ExifToolError, "exiftool not found on PATH"),
        (GPSParseError, "GPX file has no tracks"),
        (ProjectLoadError, "missing required field"),
        (ProjectSaveError, "disk full"),
        (MetadataExtractionError, "empty output file"),
    ],
)
def test_exceptions_carry_message(exc_class, message):
    exc = exc_class(message)
    assert str(exc) == message


def test_base_exception_is_catchable_for_all_subclasses():
    for exc_class in [
        ExifToolError,
        MetadataExtractionError,
        GPSParseError,
        ProjectLoadError,
        ProjectSaveError,
    ]:
        with pytest.raises(DashcamInvestigatorError):
            raise exc_class("test")
