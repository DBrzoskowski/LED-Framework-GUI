from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot, QThreadPool
from PyQt5.QtWidgets import *
import time
import sys

# from Led_animation import Cube3D
import math
from vpython import color

# css
background_style = """AppWindow {
    background-image: url(background.png);
    background-repeat: no-repeat;
    background-position: center;
    height: 843px;
    width: 549px;
}"""

QPushButton_style = """QPushButton {
    display: block;
    position: relative;
    cursor: pointer;
    background-color: #ffb13d;
    border-width: 1px;
    border-color: #ff3045;
    border-style: solid;
    border-radius: .8em;
}
QPushButton:hover {
    background-color: #7bff42;
    transition: background .3s 0.5s;
}"""

animationStateLabel_red = """QLabel {
    color: red;
}"""

animationStateLabel_green = """QLabel {
    color: green;
}"""

# create Cube3D
# c = Cube3D(8, 0.15 * 1, 1, 0.1 * 1 * math.sqrt(1 / 1))
# c.background = color.white

def start_menu(kostka):
    app = QApplication(sys.argv)
    app.setStyleSheet(background_style)
    win = AppWindow()
    win.build_kostka(kostka)
    win.show()
    sys.exit(app.exec_())


class AppWindow(QMainWindow):
    def __init__(self):
        super(AppWindow, self).__init__()
        self.setFixedSize(843, 549)
        self.setWindowTitle("3D LED Framework")
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        self.kostka = None

        # Cube
        # self.c = Cube3D(8, 0.15 * 1, 1, 0.1 * 1 * math.sqrt(1 / 1))
        # self.c.background = color.black

        # variable
        self.fps = None
        self.color_name = None
        self.one_frame = None
        self.all_frames = []

        # create buttons
        self.createButton = QtWidgets.QPushButton(self)
        self.saveFrameButton = QtWidgets.QPushButton(self)
        self.saveButton = QtWidgets.QPushButton(self)
        self.resetButton = QtWidgets.QPushButton(self)
        self.openButton = QtWidgets.QPushButton(self)
        self.loadSpectrumButton = QtWidgets.QPushButton(self)
        self.colorButton = QtWidgets.QPushButton(self)
        self.fpsButton = QtWidgets.QPushButton(self)
        self.startButton = QtWidgets.QPushButton(self)
        self.stopButton = QtWidgets.QPushButton(self)
        self.loadButton = QtWidgets.QPushButton(self)

        # create labels
        self.pathLabel = QtWidgets.QLabel(self)
        self.colorLabel = QtWidgets.QLabel(self)
        self.fpsLabel = QtWidgets.QLabel(self)
        self.animationStateLabel = QtWidgets.QLabel(self)
        self.readyAnimationLabel = QtWidgets.QLabel(self)

        # create boxes
        self.readyAnimationBox = QtWidgets.QComboBox(self)

        self.ui()

    def ui(self):
        # buttons
        self.createButton.setGeometry(QtCore.QRect(10, 30, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.createButton.setFont(font)
        self.createButton.setObjectName("createButton")
        self.createButton.setStyleSheet(QPushButton_style)
        self.createButton.clicked.connect(self.createAnimation)

        self.saveFrameButton.setGeometry(QtCore.QRect(220, 30, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.saveFrameButton.setFont(font)
        self.saveFrameButton.setObjectName("saveFrameButton")
        self.saveFrameButton.setStyleSheet(QPushButton_style)
        self.saveFrameButton.clicked.connect(self.saveFrame)

        self.saveButton.setGeometry(QtCore.QRect(430, 30, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.saveButton.setFont(font)
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setStyleSheet(QPushButton_style)
        self.saveButton.clicked.connect(self.saveAnimation)

        self.resetButton.setGeometry(QtCore.QRect(640, 30, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.resetButton.setFont(font)
        self.resetButton.setObjectName("endButton")
        self.resetButton.setStyleSheet(QPushButton_style)
        self.resetButton.clicked.connect(self.resetAnimation)

        self.openButton.setGeometry(QtCore.QRect(10, 150, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(24)
        self.openButton.setFont(font)
        self.openButton.setObjectName("openButton")
        self.openButton.setStyleSheet(QPushButton_style)
        self.openButton.clicked.connect(self.openFile)

        self.loadSpectrumButton.setGeometry(QtCore.QRect(220, 150, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.loadSpectrumButton.setFont(font)
        self.loadSpectrumButton.setObjectName("loadSpectrumButton")
        self.loadSpectrumButton.setStyleSheet(QPushButton_style)

        self.colorButton.setGeometry(QtCore.QRect(430, 150, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setWeight(50)
        self.colorButton.setFont(font)
        self.colorButton.setObjectName("colorButton")
        self.colorButton.setStyleSheet(QPushButton_style)
        self.colorButton.clicked.connect(self.colorPicker)

        self.fpsButton.setGeometry(QtCore.QRect(640, 150, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(24)
        self.fpsButton.setFont(font)
        self.fpsButton.setObjectName("fpsButton")
        self.fpsButton.setStyleSheet(QPushButton_style)
        self.fpsButton.clicked.connect(self.inputFps)

        self.startButton.setGeometry(QtCore.QRect(10, 340, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.startButton.setFont(font)
        self.startButton.setStyleSheet(QPushButton_style)
        self.startButton.setObjectName("startButton")
        self.startButton.clicked.connect(self.startAnimation)

        self.stopButton.setGeometry(QtCore.QRect(220, 340, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.stopButton.setFont(font)
        self.stopButton.setStyleSheet(QPushButton_style)
        self.stopButton.setObjectName("stopButton")
        self.stopButton.clicked.connect(self.stopAnimation)

        self.loadButton.setGeometry(QtCore.QRect(440, 340, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.loadButton.setFont(font)
        self.loadButton.setObjectName("loadButton")
        self.loadButton.setStyleSheet(QPushButton_style)
        # self.loadButton.clicked.connect(self.loadFromBox(x))

        # labels
        self.pathLabel.setGeometry(QtCore.QRect(20, 260, 171, 31))
        # self.pathLabel.setMaximumSize(QtCore.QSize(350, 65))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.pathLabel.setFont(font)
        self.pathLabel.setWordWrap(True)
        self.pathLabel.setObjectName("pathLabel")

        self.colorLabel.setGeometry(QtCore.QRect(440, 260, 171, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.colorLabel.setFont(font)
        self.colorLabel.setObjectName("colorLabel")

        self.fpsLabel.setGeometry(QtCore.QRect(650, 260, 171, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.fpsLabel.setFont(font)
        self.fpsLabel.setObjectName("fpsLabel")

        self.animationStateLabel.setGeometry(QtCore.QRect(30, 460, 361, 41))
        font = QtGui.QFont()
        font.setPointSize(24)
        self.animationStateLabel.setFont(font)
        self.animationStateLabel.setObjectName("animationStateLabel")
        self.animationStateLabel.setStyleSheet(animationStateLabel_red)

        self.readyAnimationLabel.setGeometry(QtCore.QRect(660, 340, 151, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.readyAnimationLabel.setFont(font)
        self.readyAnimationLabel.setObjectName("readyAnimationLabel")

        # boxes
        self.readyAnimationBox.setGeometry(QtCore.QRect(660, 360, 151, 21))
        self.readyAnimationBox.setObjectName("readyAnimationBox")
        self.readyAnimationBox.addItem("Double Outline")
        self.readyAnimationBox.addItem("Outline Inside Ankle")
        self.readyAnimationBox.addItem("Outer Layer")
        self.readyAnimationBox.addItem("Random Color")
        self.readyAnimationBox.activated[str].connect(self.chooseFromReadyBox)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("AppWindow", "3D LED Framework"))
        self.createButton.setText(_translate("AppWindow", "Create animation"))
        self.saveFrameButton.setText(_translate("AppWindow", "Save frame"))
        self.saveButton.setText(_translate("AppWindow", "Save animation"))
        self.resetButton.setText(_translate("AppWindow", "Reset animation"))
        self.openButton.setText(_translate("AppWindow", "Open"))
        self.pathLabel.setText(_translate("AppWindow", "Path: "))
        self.loadSpectrumButton.setText(_translate("AppWindow", "Load spectrum"))
        self.colorButton.setText(_translate("AppWindow", "Color"))
        self.colorLabel.setText(_translate("AppWindow", "Color:"))
        self.fpsButton.setText(_translate("AppWindow", "FPS"))
        self.fpsLabel.setText(_translate("AppWindow", "FPS:"))
        self.startButton.setText(_translate("AppWindow", "Start animation"))
        self.stopButton.setText(_translate("AppWindow", "Stop animation"))
        self.animationStateLabel.setText(_translate("AppWindow", "Animation state: Inactive"))
        self.loadButton.setText(_translate("AppWindow", "Load selected"))
        self.readyAnimationLabel.setText(_translate("AppWindow", "3D LED Framework animations"))

    # change name
    def createAnimation(self):
        self.colorAndFps()

    def saveFrame(self):
        self.one_frame = self.kostka.save_animation_to_frame()
        self.all_frames.append(self.one_frame)
        print(self.one_frame)
        print(self.all_frames)
        self.kostka.drawing_path['pos'] = []
        self.kostka.drawing_path['color'] = []


    # TODO check it in pyqt5
    # need drawing function
    def saveAnimation(self):
        print(self.one_frame)
        print(self.all_frames)
        file = QFileDialog.getSaveFileName(self, 'Save File', "", "Text Files (*.txt)")
        file_name = file[0]
        save = open(file_name, 'w')
        save.write(str(self.all_frames))

    def resetAnimation(self):
        self.kostka.reset_cube_state()
        # self.c.delete()
        # add close tab

    def openFile(self):
        # open file dialog
        file = QFileDialog.getOpenFileName(self, "Open animation file", "", "Text Files (*.txt)")
        # create file name
        file_path = file[0]
        file_path_list = file_path.split("/")
        file_name = file_path_list[-1]

        if file:
            self.pathLabel.setText("Path: " + file_path)
            self.pathLabel.setWordWrap(True)
            self.pathLabel.adjustSize()

            self.readyAnimationBox.addItem(file_name)
            # TODO
            self.kostka.load_animation_from_file(file_path)

    # TODO
    def loadSpectrum(self):
        pass

    # TODO color to method
    def colorPicker(self, color_name=None):
        # opening color dialog
        color = QColorDialog.getColor()
        color_name = color.name()

        if color.isValid():
            self.colorLabel.setStyleSheet("background-color: " + color_name)
            self.colorLabel.setText("Color: " + color_name)
            self.colorLabel.adjustSize()
        else:
            self.colorLabel.setText("Color: ")

        self.color_name = color_name
        # return color_name

    # TODO fps to method
    def inputFps(self, fps=None):
        fps_input = QInputDialog.getInt(self, "Input fps", "FPS: ")
        fps = fps_input[0]
        if input:
            if 10 <= int(fps_input[0]) <= 60:
                self.fpsLabel.setText("FPS: " + str(fps))
                self.pathLabel.adjustSize()
            else:
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setIcon(QMessageBox.Critical)
                msg.setText("FPS value should be between 10 to 60.")
                msg.exec_()

        self.fps = fps
        # return fps

    # TODO
    def colorAndFps(self):
        self.kostka.gui_args_builder(self.color_name, self.fps)

    # TODO connect it with hardware cube
    def startAnimation(self):
        self.animationStateLabel.setText("Animation state: Active")
        self.animationStateLabel.setStyleSheet(animationStateLabel_green)
        self.animationStateLabel.update()

    # TODO connect it with hardware cube
    def stopAnimation(self):
        self.animationStateLabel.setText("Animation state: Inactive")
        self.animationStateLabel.setStyleSheet(animationStateLabel_red)
        self.animationStateLabel.update()

    def chooseFromReadyBox(self):
        current = self.readyAnimationBox.currentText()
        # self.pathLabel.setText(str(asd))
        # return current
        if current == "Double Outline":
            self.pathLabel.setText("1")
            self.kostka.double_outline_animation()
        elif current == "Outline Inside Ankle":
            self.pathLabel.setText("2")
            self.kostka.outline_inside_ankle_animation()
        elif current == "Outer Layer":
            self.pathLabel.setText("3")
            self.kostka.outer_layer_animation()
        elif current == "Random Color":
            self.pathLabel.setText("4")
            self.kostka.random_color_animation()
        else:
            self.pathLabel.setText("outofscope")

    # TODO
    def loadAnimationFromTheBox(self):
        pass

    def build_kostka(self, kostka):
        self.kostka = kostka
        print(self.kostka)
