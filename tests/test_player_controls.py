"""
Behavioural tests for the native video-player transport controls.

These drive a real MainWindow under offscreen Qt: the total-duration label
and play/pause button state are wired through Qt signals, and both
regressed silently once before because nothing exercised the real widgets.
"""

from __future__ import annotations

import pytest
from PySide6 import QtCore, QtWidgets
from PySide6.QtMultimedia import QMediaPlayer

from dashcam_investigator.gui.app import MainWindow

PlaybackState = QMediaPlayer.PlaybackState


@pytest.fixture(scope="module")
def window() -> MainWindow:
    QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    return MainWindow()


def test_change_duration_updates_total_duration_label(window: MainWindow) -> None:
    window.change_duration(65000)
    assert window.total_duration.text() == "01:05"
    assert window.horizontal_slider.maximum() == 65000


def test_change_position_updates_current_duration_label(window: MainWindow) -> None:
    window.change_position(5000)
    assert window.current_duration.text() == "00:05"
    assert window.horizontal_slider.value() == 5000


def test_play_pause_button_tracks_playback_state(window: MainWindow) -> None:
    button = window.play_pause_button

    window._on_playback_state_changed(PlaybackState.PlayingState)
    assert button.isChecked()
    assert button.toolTip() == "Pause (Space)"

    window._on_playback_state_changed(PlaybackState.PausedState)
    assert not button.isChecked()
    assert button.toolTip() == "Play (Space)"

    # Media reaching its end: player goes Stopped without the user clicking.
    window._on_playback_state_changed(PlaybackState.PlayingState)
    window._on_playback_state_changed(PlaybackState.StoppedState)
    assert not button.isChecked()
    assert button.toolTip() == "Play (Space)"


def test_state_sync_does_not_reenter_toggled(window: MainWindow, monkeypatch) -> None:
    """Syncing the button from the player must not call play()/pause() back."""
    calls: list[str] = []
    monkeypatch.setattr(window.mediaPlayer, "play", lambda: calls.append("play"))
    monkeypatch.setattr(window.mediaPlayer, "pause", lambda: calls.append("pause"))

    window._on_playback_state_changed(PlaybackState.PlayingState)
    window._on_playback_state_changed(PlaybackState.StoppedState)
    assert calls == []


def test_toggled_drives_player_only(window: MainWindow, monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(window.mediaPlayer, "play", lambda: calls.append("play"))
    monkeypatch.setattr(window.mediaPlayer, "pause", lambda: calls.append("pause"))
    monkeypatch.setattr(window.mediaPlayer, "stop", lambda: calls.append("stop"))

    window.play_pause_button.blockSignals(True)
    window.play_pause_button.setChecked(False)
    window.play_pause_button.blockSignals(False)

    window.play_pause_button.setChecked(True)
    window.play_pause_button.setChecked(False)
    window.stop_video()
    assert calls == ["play", "pause", "stop"]


def test_transport_icons_follow_theme(window: MainWindow) -> None:
    window.theme_manager.set_mode("light")
    light = window.play_pause_button.icon().cacheKey()
    window.theme_manager.set_mode("dark")
    dark = window.play_pause_button.icon().cacheKey()
    assert not window.play_pause_button.icon().isNull()
    assert not window.stop_button.icon().isNull()
    assert light != dark
    # Icons are cached per (name, theme): flipping back reuses the same QIcon.
    window.theme_manager.set_mode("light")
    assert window.play_pause_button.icon().cacheKey() == light
    window.theme_manager.set_mode("system")


def test_slider_does_not_take_focus(window: MainWindow) -> None:
    assert window.horizontal_slider.focusPolicy() == QtCore.Qt.FocusPolicy.NoFocus
