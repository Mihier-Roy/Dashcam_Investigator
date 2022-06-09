# Dashcam Investigator

A python desktop application to aid in the forensic investigation of evidence gathered from dashcam devices.

## Development

The project was built using Python 3.9 and uses [Poetry](https://python-poetry.org/) for dependency management. Before getting started with development, install Poetry by following the instructions [here](https://python-poetry.org/docs/)

The following commands can be used to install the dependencies and run the application.

```bash
# Install dependencies
$ poetry install

# Run the application using the Poetry virtual environment
$ poetry run python ./dashcam_investigator/__main__.py 
```

### Dependencies

The application was built using the following open source projects

- Pandas
- Numpy
- Black (code formatting)
- PyTest (unit testing)

### Log configuration

The application uses pythons built in `logging` module for logging across the application. The module was configured to log `DEBUG` messages and higher to the console during development. In addition, the application writes the following logs to `%LOCALAPPDATA%/DashcamInvestigator/Logs`:

- `error.log` - All `ERROR` and `CRITICAL` messages are written here.
- `debug.log` - All `DEBUG` and higher events are written here. These logs also include the line and module where the log record was written.