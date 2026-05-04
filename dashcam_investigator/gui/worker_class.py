import logging
import sys
import traceback

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

logger = logging.getLogger(__name__)


# Adapted from https://www.pythonguis.com/tutorials/multithreading-pyside-applications-qthreadpool/
class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    Supported signals are: finished, error, result, progress, status
    """

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)
    status = Signal(str)


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

        self.kwargs["progress_callback"] = self.signals.progress
        self.kwargs["status_callback"] = self.signals.status

    @Slot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        logger.debug("Begin thread execution")
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()
