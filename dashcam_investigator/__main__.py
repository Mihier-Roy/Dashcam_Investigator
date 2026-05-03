"""
This is the entrypoint of the application that configures logging and then executes the GUI.
"""

import logging
import logging.config
import os
from pathlib import Path

# The dci:// URL scheme must be registered BEFORE QApplication is created,
# which happens inside app.run(). Doing it here at import time keeps the
# ordering correct regardless of how Qt modules get imported below.
from .gui.web.scheme import register_scheme

register_scheme()

from .gui import app  # noqa: E402  (import after register_scheme on purpose)

if __name__ == "__main__":
    # Create a logs directory in AppData\Local\DashcamInvestigator if it doesn't already exist
    appdata_local = os.getenv("LOCALAPPDATA")
    log_path = Path(appdata_local, "DashcamInvestigator", "Logs")
    LOG_PATH = str(log_path).replace("\\", "/")
    if not Path(LOG_PATH).exists():
        Path(LOG_PATH).mkdir(parents=True, exist_ok=True)

    # Setup logging based on log.conf
    logging.config.fileConfig(
        "log.conf", defaults={"logPath": LOG_PATH}, disable_existing_loggers=False
    )

    logger = logging.getLogger(__name__)

    # Launch GUI
    app.run()
