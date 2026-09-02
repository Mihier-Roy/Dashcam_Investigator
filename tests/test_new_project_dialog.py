"""Tests for the New Project dialog."""

from pathlib import Path

from PySide6 import QtWidgets

from dashcam_investigator.gui.new_project_class import NewProjectDialog


def _app() -> QtWidgets.QApplication:
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


class TestNewProjectDialog:
    def test_fields_are_line_edits(self):
        _app()
        dialog = NewProjectDialog()
        for name in ("input_edit", "output_edit", "case_edit", "investigator_edit"):
            widget = getattr(dialog, name)
            assert isinstance(widget, QtWidgets.QLineEdit), f"{name} is {type(widget)}"

    def test_save_returns_expected_tuple(self, tmp_path):
        _app()
        dialog = NewProjectDialog()
        input_dir = tmp_path / "in"
        output_dir = tmp_path / "out"
        dialog.input_edit.setText(str(input_dir))
        dialog.output_edit.setText(str(output_dir))
        dialog.case_edit.setText("My Project")
        dialog.investigator_edit.setText("Alex")

        result = dialog.save()

        assert result == (input_dir, output_dir, "My Project", "Alex")

    def test_save_with_empty_dirs_returns_none(self):
        _app()
        dialog = NewProjectDialog()
        dialog.case_edit.setText("My Project")
        dialog.investigator_edit.setText("Alex")

        input_dir, output_dir, case_name, investigator_name = dialog.save()

        assert input_dir is None
        assert output_dir is None
        assert case_name == "My Project"
        assert investigator_name == "Alex"

    def test_pick_dir_ignores_cancel(self, monkeypatch):
        _app()
        dialog = NewProjectDialog()
        monkeypatch.setattr(
            QtWidgets.QFileDialog, "getExistingDirectory", staticmethod(lambda *a, **k: "")
        )
        dialog.input_edit.setText("unchanged")
        dialog.get_input_dir()
        assert dialog.input_edit.text() == "unchanged"
