from PySide2 import QtWidgets, QtGui
from QtMainWindow import Ui_DashcamInvestigator


class MainWindow(QtWidgets.QMainWindow, Ui_DashcamInvestigator):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # Move the application window to the center of the screen
        # Get current screen size
        screen_size = QtGui.QScreen.availableGeometry(
            QtWidgets.QApplication.primaryScreen()
        )
        # Compute the  coordinates for the center of the screen
        x_coordinates = (screen_size.width() - self.width()) / 2
        y_coordinates = (screen_size.height() - self.height()) / 2 - 20
        self.move(x_coordinates, y_coordinates)


app = QtWidgets.QApplication([])

window = MainWindow()
window.show()
app.exec_()
