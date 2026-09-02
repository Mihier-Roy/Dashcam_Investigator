from pathlib import Path

from PySide6 import QtCore, QtWidgets


class NewProjectDialog(QtWidgets.QDialog):
    """
    Collects the inputs needed to create a new project: source directory,
    output directory, project title, and author.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.input_dir: Path | None = None
        self.output_dir: Path | None = None
        self.case_name: str = ""
        self.investigator_name: str = ""

        self.setWindowTitle("New Project")
        self.setMinimumWidth(520)

        self.input_edit = QtWidgets.QLineEdit(self)
        self.input_edit.setPlaceholderText(
            "Directory containing your dashcam files"
        )
        self.input_dir_button = QtWidgets.QPushButton("Browse…", self)
        self.input_dir_button.clicked.connect(self.get_input_dir)

        self.output_edit = QtWidgets.QLineEdit(self)
        self.output_edit.setPlaceholderText(
            "Directory where the project will be saved"
        )
        self.output_dir_button = QtWidgets.QPushButton("Browse…", self)
        self.output_dir_button.clicked.connect(self.get_output_dir)

        self.case_edit = QtWidgets.QLineEdit(self)
        self.case_edit.setPlaceholderText("Enter a name for this project")

        self.investigator_edit = QtWidgets.QLineEdit(self)
        self.investigator_edit.setPlaceholderText("Enter your name")

        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        form.addRow("Dashcam directory", self._with_browse(self.input_edit, self.input_dir_button))
        form.addRow("Output directory", self._with_browse(self.output_edit, self.output_dir_button))
        form.addRow("Project title", self.case_edit)
        form.addRow("Author", self.investigator_edit)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, self
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(button_box)

    @staticmethod
    def _with_browse(
        line_edit: QtWidgets.QLineEdit, button: QtWidgets.QPushButton
    ) -> QtWidgets.QWidget:
        """Wrap a line edit + its browse button in one row widget for QFormLayout."""
        row = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(line_edit, 1)
        row_layout.addWidget(button)
        return row

    def get_input_dir(self):
        """
        Sets the input directory path
        """
        self._pick_dir(self.input_edit)

    def get_output_dir(self):
        """
        Sets the output directory path
        """
        self._pick_dir(self.output_edit)

    def _pick_dir(self, line_edit: QtWidgets.QLineEdit) -> None:
        """Prompt for a directory and write it into `line_edit`.

        `getExistingDirectory` returns "" (never None) on cancel, so a
        truthy check is required to make cancelling a no-op.
        """
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Open Directory",
            "",
            QtWidgets.QFileDialog.ShowDirsOnly
            | QtWidgets.QFileDialog.DontResolveSymlinks,
        )
        if directory:
            line_edit.setText(directory)

    def save(self):
        self.case_name = self.case_edit.text()
        self.investigator_name = self.investigator_edit.text()
        if len(self.input_edit.text()) > 0:
            self.input_dir = Path(self.input_edit.text())

        if len(self.output_edit.text()) > 0:
            self.output_dir = Path(self.output_edit.text())
        return self.input_dir, self.output_dir, self.case_name, self.investigator_name
