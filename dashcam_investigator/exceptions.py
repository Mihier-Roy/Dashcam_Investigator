class DashcamInvestigatorError(Exception):
    """Base exception for all domain errors."""


class ExifToolError(DashcamInvestigatorError):
    """ExifTool execution failed (missing binary, non-zero exit, or timed out)."""


class GPSParseError(DashcamInvestigatorError):
    """GPX file is empty, malformed, or has no track segments."""


class ProjectLoadError(DashcamInvestigatorError):
    """Failed to load or deserialize a project file."""


class ProjectSaveError(DashcamInvestigatorError):
    """Failed to write project file to disk."""
