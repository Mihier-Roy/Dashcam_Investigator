from pathlib import Path
from PySide2 import QtWidgets
from QtNewProjectDialog import Ui_Dialog


class NewProjectDialog(QtWidgets.QDialog, Ui_Dialog):
    """
    Launches the dialog to collect information to create a new project.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.input_dir = None
        self.output_dir = None
        self.case_name = None
        self.investigator_name = None

        # Run the .setupUi() method to show the GUI
        self.setupUi(self)

        # Open file dialog for input dir
        self.input_dir_button.clicked.connect(self.get_input_dir)

        # Open file dialog for output dir
        self.output_dir_button.clicked.connect(self.get_output_dir)

    def get_input_dir(self):
        """
        Sets the input directory path
        """
        dir = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Open Directory",
            "C:",
            QtWidgets.QFileDialog.ShowDirsOnly
            | QtWidgets.QFileDialog.DontResolveSymlinks,
        )

        if dir != None:
            self.input_edit.setText(dir)

    def get_output_dir(self):
        """
        Sets the output directory path
        """
        dir = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Open Directory",
            "C:",
            QtWidgets.QFileDialog.ShowDirsOnly
            | QtWidgets.QFileDialog.DontResolveSymlinks,
        )

        if dir != None:
            self.output_edit.setText(dir)

    def save(self):
        self.case_name = self.case_edit.toPlainText()
        self.investigator_name = self.investigator_edit.toPlainText()
        if len(self.input_edit.toPlainText()) > 0:
            self.input_dir = Path(self.input_edit.toPlainText())

        if len(self.output_edit.toPlainText()) > 0:
            self.output_dir = Path(self.output_edit.toPlainText())
        return self.input_dir, self.output_dir, self.case_name, self.investigator_name
