import logging
import logging.config
import os


def main():
    logger = logging.getLogger(__name__)
    logger.info("Running dashcam investigator info")


if __name__ == "__main__":
    # Create a logs directory in AppData\Local\DashcamInvestigator if it doesn't already exist
    appdata_local = os.getenv("LOCALAPPDATA")
    log_path = os.path.join(appdata_local, "DashcamInvestigator", "Logs")
    log_path = log_path.replace("\\", "/")
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # Setup logging based on log.conf
    logging.config.fileConfig("log.conf", defaults={"logPath": log_path})

    # Call main function
    main()
