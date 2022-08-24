from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import *

import pytest
import sys
import unittest
from menu_gui import menu
import Led_animation


def test_gui(qtbot):
    app = menu.AppWindow()
    qtbot.addWidget(app)

    qtbot.mouseClick(app.drawButton, Qt.LeftButton)

    assert app.drawButton.text() == "Stop Drawing"
    # return app

# Traceback (most recent call last):
#   File "C:\repo\LED-Framework-GUI\menu_gui\menu.py", line 340, in draw_animation
#     self.cube.set_drawing_fps(self.fps)
# AttributeError: 'NoneType' object has no attribute 'set_drawing_fps'