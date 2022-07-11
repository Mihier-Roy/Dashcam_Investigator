import logging
import logging.config
from pathlib import Path
import os
from gui import app

if __name__ == "__main__":
    # Create a logs directory in AppData\Local\DashcamInvestigator if it doesn't already exist
    appdata_local = os.getenv("LOCALAPPDATA")
    log_path = Path(appdata_local, "DashcamInvestigator", "Logs")
    log_path = str(log_path).replace("\\", "/")
    if not Path(log_path).exists():
        Path(log_path).mkdir(parents=True, exist_ok=True)

    # Setup logging based on log.conf
    logging.config.fileConfig(
        "log.conf", defaults={"logPath": log_path}, disable_existing_loggers=False
    )

    logger = logging.getLogger(__name__)

    # Launch GUI
    app.run()
