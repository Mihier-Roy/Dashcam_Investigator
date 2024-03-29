import sys
import traceback
import logging
from PySide2.QtCore import QRunnable, Slot, Signal, QObject

logger = logging.getLogger(__name__)

# Adapted from https://www.pythonguis.com/tutorials/multithreading-pyside-applications-qthreadpool/
class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    Supported signals are: finished, error, result, progress
    """

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)


# Adapted from https://www.pythonguis.com/tutorials/multithreading-pyside-applications-qthreadpool/
class Worker(QRunnable):
    """
    Defines a Qt Worker thread by inheriting QRunnable to manage thread setup, signals and clean up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs["progress_callback"] = self.signals.progress

    @Slot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        logger.debug(f"Begin thread execution")
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
