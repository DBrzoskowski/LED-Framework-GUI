from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
import sys

from Led_animation import Cube3D
import math
from vpython import color


background = """AppWindow
{
background-image: url(background.jpg);
background-repeat: no-repeat;
background-position: center;
height: 843px;
width: 549px;
}"""


class AppWindow(QMainWindow):
    def __init__(self):
        super(AppWindow, self).__init__()
        self.setFixedSize(843, 549)
        self.setWindowTitle("3D LED Framework")
        self.ui()

    def ui(self):
        self.openButton = QtWidgets.QPushButton(self)
        self.openButton.setGeometry(QtCore.QRect(430, 145, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(24)
        self.openButton.setFont(font)
        self.openButton.setObjectName("openButton")
        self.openButton.setStyleSheet("background-color: #55aaff; border-radius: 12px;")
        self.openButton.clicked.connect(self.showPath)

        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setGeometry(QtCore.QRect(20, 460, 411, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")

        self.loadButton = QtWidgets.QPushButton(self)
        self.loadButton.setGeometry(QtCore.QRect(510, 320, 321, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.loadButton.setFont(font)
        self.loadButton.setObjectName("loadButton")

        self.readyAnimationBox = QtWidgets.QComboBox(self)
        self.readyAnimationBox.setGeometry(QtCore.QRect(510, 390, 151, 21))
        self.readyAnimationBox.setObjectName("readyAnimationBox")

        self.createButton = QtWidgets.QPushButton(self)
        self.createButton.setGeometry(QtCore.QRect(10, 25, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.createButton.setFont(font)
        self.createButton.setObjectName("createButton")
        self.createButton.clicked.connect(self.createAnimation)

        self.saveButton = QtWidgets.QPushButton(self)
        self.saveButton.setGeometry(QtCore.QRect(220, 25, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.saveButton.setFont(font)
        self.saveButton.setObjectName("saveButton")

        self.endButton = QtWidgets.QPushButton(self)
        self.endButton.setGeometry(QtCore.QRect(430, 25, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.endButton.setFont(font)
        self.endButton.setObjectName("endButton")

        self.colorButton = QtWidgets.QPushButton(self)
        self.colorButton.setGeometry(QtCore.QRect(10, 145, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setBold(False)
        font.setWeight(50)
        self.colorButton.setFont(font)
        self.colorButton.setObjectName("colorButton")
        self.colorButton.clicked.connect(self.colorPicker)

        self.fpsButton = QtWidgets.QPushButton(self)
        self.fpsButton.setGeometry(QtCore.QRect(220, 145, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(24)
        self.fpsButton.setFont(font)
        self.fpsButton.setObjectName("fpsButton")
        self.fpsButton.clicked.connect(self.inputFps)

        self.fpsLabel = QtWidgets.QLabel(self)
        self.fpsLabel.setGeometry(QtCore.QRect(230, 255, 171, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.fpsLabel.setFont(font)
        self.fpsLabel.setObjectName("fpsLabel")

        self.colorLabel = QtWidgets.QLabel(self)
        self.colorLabel.setGeometry(QtCore.QRect(20, 255, 171, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.colorLabel.setFont(font)
        self.colorLabel.setObjectName("colorLabel")

        self.pathLabel = QtWidgets.QLabel(self)
        self.pathLabel.setGeometry(QtCore.QRect(440, 255, 171, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.pathLabel.setFont(font)
        self.pathLabel.setObjectName("pathLabel")

        self.stopButton = QtWidgets.QPushButton(self)
        self.stopButton.setGeometry(QtCore.QRect(220, 320, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.stopButton.setFont(font)
        self.stopButton.setObjectName("stopButton")

        self.startButton = QtWidgets.QPushButton(self)
        self.startButton.setGeometry(QtCore.QRect(10, 320, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.startButton.setFont(font)
        self.startButton.setObjectName("startButton")

        self.recentAnimationBox = QtWidgets.QComboBox(self)
        self.recentAnimationBox.setGeometry(QtCore.QRect(680, 390, 151, 21))
        self.recentAnimationBox.setObjectName("recentAnimationBox")
        self.readyAnimationLabel = QtWidgets.QLabel(self)
        self.readyAnimationLabel.setGeometry(QtCore.QRect(510, 370, 151, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.readyAnimationLabel.setFont(font)
        self.readyAnimationLabel.setObjectName("readyAnimationLabel")

        self.recentAnimationLabel = QtWidgets.QLabel(self)
        self.recentAnimationLabel.setGeometry(QtCore.QRect(680, 370, 151, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.recentAnimationLabel.setFont(font)
        self.recentAnimationLabel.setObjectName("recentAnimationLabel")

        self.startFrameButton = QtWidgets.QPushButton(self)
        self.startFrameButton.setGeometry(QtCore.QRect(640, 145, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.startFrameButton.setFont(font)
        self.startFrameButton.setObjectName("startFrameButton")

        self.loadSpectrumButton = QtWidgets.QPushButton(self)
        self.loadSpectrumButton.setGeometry(QtCore.QRect(640, 25, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.loadSpectrumButton.setFont(font)
        self.loadSpectrumButton.setObjectName("loadSpectrumButton")

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("AppWindow", "3D LED Framework"))
        self.openButton.setText(_translate("AppWindow", "Open"))
        self.loadButton.setText(_translate("AppWindow", "Load selected"))
        self.createButton.setText(_translate("AppWindow", "Create animation"))
        self.saveButton.setText(_translate("AppWindow", "Save animation"))
        self.endButton.setText(_translate("AppWindow", "End animation"))
        self.colorButton.setText(_translate("AppWindow", "Color"))
        self.fpsButton.setText(_translate("AppWindow", "FPS"))
        self.fpsLabel.setText(_translate("AppWindow", "FPS:"))
        self.colorLabel.setText(_translate("AppWindow", "Color:"))
        self.pathLabel.setText(_translate("AppWindow", "Path: "))
        self.stopButton.setText(_translate("AppWindow", "Stop animation"))
        self.startButton.setText(_translate("AppWindow", "Start animation"))
        self.readyAnimationLabel.setText(_translate("AppWindow", "3D LED Framework animation"))
        self.recentAnimationLabel.setText(_translate("AppWindow", "Recent animations"))
        self.startFrameButton.setText(_translate("AppWindow", "Start frame"))
        self.loadSpectrumButton.setText(_translate("AppWindow", "Load Spectrum"))

    def colorPicker(self):
        # opening color dialog
        color = QColorDialog.getColor()
        color_name = color.name()

        if color.isValid():
            self.colorLabel.setStyleSheet("background-color: " + color_name)
            self.colorLabel.setText("Color: " + color_name)
            self.colorLabel.adjustSize()
        else:
            self.colorLabel.setText("Color: ")

    def showPath(self):
        # open file dialog
        file = QFileDialog.getOpenFileName(self, "Open animation file", "", "Text Files (*.txt)")

        if file:
            self.pathLabel.setText("Path: " + file[0])
            self.pathLabel.setWordWrap(True)
            self.pathLabel.adjustSize()

    def inputFps(self):
        fps_input = QInputDialog.getInt(self, "Input fps", "FPS: ")
        if input:
            self.fpsLabel.setText("FPS: " + str(fps_input[0]))
            self.pathLabel.adjustSize()

    def createAnimation(self):
        c = Cube3D(8, 0.15 * 1, 1, 0.1 * 1 * math.sqrt(1 / 1))
        c.background = color.white


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(background)
    win = AppWindow()
    win.show()
    sys.exit(app.exec_())
