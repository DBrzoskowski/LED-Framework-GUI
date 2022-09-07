import json

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import *

from sandbox.audio_spectrum_analyzer.LedManager import *

import sys


# css
background_style = """AppWindow {
    background-image: url(menu_gui/background.jpg);
    background-repeat: no-repeat;
    background-position: center;
    height: 100%;
    width: 100%;
}"""

QPushButton_style = """QPushButton {
    display: block;
    position: relative;
    cursor: pointer;
    background-color: #455073;
    color: white;
    border-width: 1px;
    border-color: #c0904d;
    border-style: solid;
    border-radius: .8em;
}
QPushButton:hover {
    background-color: #6077c0;
    transition: background .3s 0.5s;
}"""

animationStateLabel_red = """QLabel {
    color: red;
}"""

animationStateLabel_green = """QLabel {
    color: green;
}"""


class DoStartGUI(threading.Thread):
    def __init__(self, obj, *args, **kwargs):
        super(DoStartGUI, self).__init__(*args, **kwargs)
        self.obj = obj

    def run(self):
        start_menu(self.obj)


def start_menu(cube):
    app = QApplication(sys.argv)
    app.setStyleSheet(background_style)
    win = AppWindow()
    win.build_cube(cube)
    win.show()
    sys.exit(app.exec_())


# def second_window():
#     second = AnotherWindow()
#     second.show()


class AppWindow(QMainWindow):
    def __init__(self):
        super(AppWindow, self).__init__()
        # self.setFixedSize(841, 501)
        self.setFixedSize(1501, 511)
        self.setWindowTitle("3D LED Framework")
        self.setWindowIcon(QtGui.QIcon('menu_gui/icon.png'))

        # self.sub_win = AnotherWindow()

        # Cube
        self.cube = None
        self.draw_status = False
        self.spectrum_status = False
        self.animation_status = False

        # variables
        self.fps = 30
        self.color_name = "#FFFFFF"
        self.currentNameBox = None
        self.files = []
        self.files_path = []
        self.file_name = None
        self.one_frame = None
        self.one_frame_copy = None
        self.all_frames = []
        self.is_spectrum_running = False
        self.is_animation_running = False
        self.frame_count = 0

        # create buttons
        self.spectrumButton = QtWidgets.QPushButton(self)
        self.openButton = QtWidgets.QPushButton(self)
        self.loadButton = QtWidgets.QPushButton(self)
        self.resetButton = QtWidgets.QPushButton(self)
        self.drawButton = QtWidgets.QPushButton(self)
        self.colorButton = QtWidgets.QPushButton(self)
        self.fpsButton = QtWidgets.QPushButton(self)
        self.saveButton = QtWidgets.QPushButton(self)

        # create labels
        self.operateAnimationLabel = QtWidgets.QLabel(self)
        self.lastOpenFileLabel = QtWidgets.QLabel(self)
        self.readyAnimationLabel = QtWidgets.QLabel(self)
        self.createAnimationLabel = QtWidgets.QLabel(self)
        self.counterFrameLabel = QtWidgets.QLabel(self)
        self.colorLabel = QtWidgets.QLabel(self)
        self.fpsLabel = QtWidgets.QLabel(self)

        # create boxes
        self.readyAnimationBox = QtWidgets.QComboBox(self)

        # create checkbox
        self.physicalCubeCheckBox = QtWidgets.QCheckBox(self)

        # create web page view
        self.browser = QWebEngineView(self)

        self.ui()

    def ui(self):
        # web page view
        self.browser.setUrl(QUrl("http://localhost:8980/"))
        self.browser.setGeometry(QtCore.QRect(840, 0, 700, 520))
        self.browser.show()

        # buttons
        self.spectrumButton.setGeometry(QtCore.QRect(10, 70, 191, 101))
        self.spectrumButton.setMinimumSize(QtCore.QSize(191, 101))
        self.spectrumButton.setMaximumSize(QtCore.QSize(191, 101))
        font = QtGui.QFont()
        font.setFamily("Dubai Medium")
        font.setPointSize(16)
        self.spectrumButton.setFont(font)
        self.spectrumButton.setObjectName("spectrumButton")
        self.spectrumButton.setStyleSheet(QPushButton_style)
        self.spectrumButton.setCheckable(True)
        self.spectrumButton.clicked.connect(self.load_spectrum)

        self.openButton.setGeometry(QtCore.QRect(220, 70, 191, 101))
        self.openButton.setMinimumSize(QtCore.QSize(191, 101))
        self.openButton.setMaximumSize(QtCore.QSize(191, 101))
        font = QtGui.QFont()
        font.setFamily("Dubai Medium")
        font.setPointSize(16)
        self.openButton.setFont(font)
        self.openButton.setObjectName("openButton")
        self.openButton.setStyleSheet(QPushButton_style)
        self.openButton.clicked.connect(self.open_file)

        self.loadButton.setGeometry(QtCore.QRect(430, 70, 191, 101))
        self.loadButton.setMinimumSize(QtCore.QSize(191, 101))
        self.loadButton.setMaximumSize(QtCore.QSize(191, 101))
        font = QtGui.QFont()
        font.setFamily("Dubai Medium")
        font.setPointSize(16)
        self.loadButton.setFont(font)
        self.loadButton.setObjectName("loadButton")
        self.loadButton.setStyleSheet(QPushButton_style)
        self.loadButton.clicked.connect(self.load_animation)

        self.resetButton.setGeometry(QtCore.QRect(640, 70, 191, 101))
        self.resetButton.setMinimumSize(QtCore.QSize(191, 101))
        self.resetButton.setMaximumSize(QtCore.QSize(191, 101))
        font = QtGui.QFont()
        font.setFamily("Dubai Medium")
        font.setPointSize(16)
        self.resetButton.setFont(font)
        self.resetButton.setObjectName("resetButton")
        self.resetButton.setStyleSheet(QPushButton_style)
        self.resetButton.clicked.connect(self.reset_cube)

        self.drawButton.setGeometry(QtCore.QRect(10, 330, 191, 101))
        self.drawButton.setMinimumSize(QtCore.QSize(191, 101))
        self.drawButton.setMaximumSize(QtCore.QSize(191, 101))
        font = QtGui.QFont()
        font.setFamily("Dubai Medium")
        font.setPointSize(16)
        self.drawButton.setFont(font)
        self.drawButton.setObjectName("drawButton")
        self.drawButton.setStyleSheet(QPushButton_style)
        self.drawButton.clicked.connect(self.draw_animation)

        self.colorButton.setGeometry(QtCore.QRect(220, 330, 191, 101))
        self.colorButton.setMinimumSize(QtCore.QSize(191, 101))
        self.colorButton.setMaximumSize(QtCore.QSize(191, 101))
        font = QtGui.QFont()
        font.setFamily("Dubai Medium")
        font.setPointSize(20)
        self.colorButton.setFont(font)
        self.colorButton.setObjectName("colorButton")
        self.colorButton.setStyleSheet(QPushButton_style)
        self.colorButton.clicked.connect(self.color_picker)

        self.fpsButton.setGeometry(QtCore.QRect(430, 330, 191, 101))
        self.fpsButton.setMinimumSize(QtCore.QSize(191, 101))
        self.fpsButton.setMaximumSize(QtCore.QSize(191, 101))
        font = QtGui.QFont()
        font.setFamily("Dubai Medium")
        font.setPointSize(20)
        self.fpsButton.setFont(font)
        self.fpsButton.setObjectName("fpsButton")
        self.fpsButton.setStyleSheet(QPushButton_style)
        self.fpsButton.clicked.connect(self.input_fps)

        self.saveButton.setGeometry(QtCore.QRect(640, 330, 191, 101))
        self.saveButton.setMinimumSize(QtCore.QSize(191, 101))
        self.saveButton.setMaximumSize(QtCore.QSize(191, 101))
        font = QtGui.QFont()
        font.setFamily("Dubai Medium")
        font.setPointSize(16)
        self.saveButton.setFont(font)
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setStyleSheet(QPushButton_style)
        # self.saveButton.setShortcut("Ctrl+Shift+S")
        self.saveButton.clicked.connect(self.save_animation)

        # labels
        self.operateAnimationLabel.setGeometry(QtCore.QRect(255, 10, 331, 40))
        self.operateAnimationLabel.setMinimumSize(QtCore.QSize(331, 40))
        self.operateAnimationLabel.setMaximumSize(QtCore.QSize(331, 40))
        font = QtGui.QFont()
        font.setFamily("Dubai Medium")
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.operateAnimationLabel.setFont(font)
        self.operateAnimationLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.operateAnimationLabel.setObjectName("operateAnimationLabel")

        self.lastOpenFileLabel.setGeometry(QtCore.QRect(230, 180, 171, 31))
        self.lastOpenFileLabel.setMinimumSize(QtCore.QSize(171, 31))
        self.lastOpenFileLabel.setMaximumSize(QtCore.QSize(171, 31))
        font = QtGui.QFont()
        font.setFamily("Dubai Medium")
        font.setPointSize(16)
        self.lastOpenFileLabel.setFont(font)
        self.lastOpenFileLabel.setWordWrap(True)
        self.lastOpenFileLabel.setObjectName("lastOpenFileLabel")

        self.readyAnimationLabel.setGeometry(QtCore.QRect(440, 180, 181, 21))
        self.readyAnimationLabel.setMinimumSize(QtCore.QSize(181, 21))
        self.readyAnimationLabel.setMaximumSize(QtCore.QSize(181, 21))
        font = QtGui.QFont()
        font.setFamily("Dubai Medium")
        font.setPointSize(10)
        self.readyAnimationLabel.setFont(font)
        self.readyAnimationLabel.setObjectName("readyAnimationLabel")

        self.createAnimationLabel.setGeometry(QtCore.QRect(255, 270, 331, 40))
        self.createAnimationLabel.setMinimumSize(QtCore.QSize(331, 40))
        self.createAnimationLabel.setMaximumSize(QtCore.QSize(331, 40))
        font = QtGui.QFont()
        font.setFamily("Dubai Medium")
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.createAnimationLabel.setFont(font)
        self.createAnimationLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.createAnimationLabel.setObjectName("createAnimationLabel")

        self.counterFrameLabel.setGeometry(QtCore.QRect(20, 440, 171, 31))
        font = QtGui.QFont()
        font.setFamily("Dubai Medium")
        font.setPointSize(16)
        self.counterFrameLabel.setFont(font)
        self.counterFrameLabel.setObjectName("counterFrameLabel")

        self.colorLabel.setGeometry(QtCore.QRect(230, 440, 171, 31))
        font = QtGui.QFont()
        font.setFamily("Dubai Medium")
        font.setPointSize(16)
        self.colorLabel.setFont(font)
        self.colorLabel.setObjectName("colorLabel")

        self.fpsLabel.setGeometry(QtCore.QRect(440, 440, 171, 31))
        font = QtGui.QFont()
        font.setFamily("Dubai Medium")
        font.setPointSize(16)
        self.fpsLabel.setFont(font)
        self.fpsLabel.setObjectName("fpsLabel")

        # boxes
        self.readyAnimationBox.setGeometry(QtCore.QRect(450, 200, 151, 21))
        font = QtGui.QFont()
        font.setFamily("Dubai Medium")
        font.setPointSize(10)
        self.readyAnimationBox.setFont(font)
        self.readyAnimationBox.setObjectName("readyAnimationBox")
        self.readyAnimationBox.addItem("Double Outline")
        self.readyAnimationBox.addItem("Outline Inside Ankle")
        self.readyAnimationBox.addItem("Outer Layer")
        self.readyAnimationBox.addItem("Random Color")
        self.readyAnimationBox.addItem("Bouncy snake")
        self.readyAnimationBox.addItem("Sin wave")
        self.readyAnimationBox.addItem("Folder")
        self.readyAnimationBox.addItem("Rain")
        self.readyAnimationBox.addItem("Color wheel")
        self.readyAnimationBox.activated[str].connect(self.choose_from_ready_box)

        # checkbox
        self.physicalCubeCheckBox.setGeometry(QtCore.QRect(670, 190, 141, 21))
        self.physicalCubeCheckBox.setMinimumSize(QtCore.QSize(141, 21))
        self.physicalCubeCheckBox.setMaximumSize(QtCore.QSize(141, 21))
        font = QtGui.QFont()
        font.setFamily("Dubai Medium")
        font.setPointSize(10)
        self.physicalCubeCheckBox.setFont(font)
        self.physicalCubeCheckBox.setObjectName("physicalCubeCheckBox")
        self.physicalCubeCheckBox.clicked.connect(self.update_send_to_cube_flag)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("AppWindow", "3D LED Framework"))
        # buttons
        self.spectrumButton.setText(_translate("AppWindow", "Start Spectrum"))
        self.openButton.setText(_translate("AppWindow", "Open Animation File"))
        self.loadButton.setText(_translate("AppWindow", "Start Animation"))
        self.resetButton.setText(_translate("AppWindow", "Reset Cube"))
        self.drawButton.setText(_translate("AppWindow", "Start Drawing"))
        self.colorButton.setText(_translate("AppWindow", "Color"))
        self.fpsButton.setText(_translate("AppWindow", "FPS"))
        self.saveButton.setText(_translate("AppWindow", "Save Animation"))
        # labels
        self.operateAnimationLabel.setText(_translate("AppWindow", "OPERATE ANIMATION"))
        self.lastOpenFileLabel.setText(_translate("AppWindow", "File:"))
        self.readyAnimationLabel.setText(_translate("AppWindow", "3D LED Framework animations"))
        self.createAnimationLabel.setText(_translate("AppWindow", "CREATE ANIMATION"))
        self.counterFrameLabel.setText(_translate("AppWindow", "Frame count:"))
        self.colorLabel.setText(_translate("AppWindow", "Color:"))
        self.fpsLabel.setText(_translate("AppWindow", "FPS: 30"))
        # checkbox
        self.physicalCubeCheckBox.setText(_translate("AppWindow", "Send to physical cube"))

    def draw_animation(self):
        if self.draw_status:
            self.one_frame = self.cube.save_animation_frame_list()
            self.frame_count += 1
            self.update_count_frame()
            self.cube.unbinding()
            self.drawButton.setText("Start Drawing")
        elif not self.draw_status:
            self.cube.set_drawing_fps(self.fps)
            self.cube.binding()
            self.drawButton.setText("Stop Drawing")
        self.draw_status = not self.draw_status

    def update_count_frame(self):
        self.counterFrameLabel.setText("Frame count: " + str(self.frame_count))

    def update_send_to_cube_flag(self):
        if self.physicalCubeCheckBox.isChecked():
            self.cube.send_to_cube_flag = True
        else:
            self.cube.send_to_cube_flag = False

    def save_animation(self):
        # open file dialog
        file = QFileDialog.getSaveFileName(self, 'Save animation file', "", "Text Files (*.txt)")
        file_path = file[0]
        # file_name = file_path.split("/")[-1]

        if file:
            try:
                save = open(file_path, 'w')
                for i in self.one_frame:
                    save.write(json.dumps(i) + "\n")
                self.frame_count = 0
                self.update_count_frame()
            except Exception as e:
                QMessageBox.information(self, 'Info',
                                        # f'The following error occurred:\n{type(e)}: {e}')
                                        f'The animation has not been saved')
                return

    def reset_cube(self):
        if self.cube.animation_thread is not None:
            self.cube.abort_animation_thread = True
            self.cube.animation_thread.join()

        if self.is_spectrum_running:
            self.is_spectrum_running = False
            self.spectrumButton.setText("Start Spectrum")

        if self.is_animation_running:
            self.is_animation_running = False
            self.loadButton.setText("Start Animation")

        self.cube.reset_cube_state()
        clean_frame = LEDFrame()
        sendFrame(self, clean_frame)

    def open_file(self):
        # open file dialog
        file = QFileDialog.getOpenFileName(self, "Open animation file", "", "Text Files (*.txt)")
        file_path = file[0]
        file_name = file_path.split("/")[-1]

        if file:
            try:
                self.lastOpenFileLabel.setText("File: " + file_name)
                self.lastOpenFileLabel.setWordWrap(True)
                # self.lastOpenFileLabel.adjustSize()
                if file_path != '':
                    self.readyAnimationBox.insertItem(0, file_name)
                    self.cube.load_animation_from_file(file_path)
                    self.files.append(file_name)
                    self.files_path.append(file_path)
            except Exception as e:
                QMessageBox.information(self, 'Info',
                                        f'The following error occurred:\n{type(e)}: {e}')
                return

    def load_spectrum(self):
        if self.is_spectrum_running:
            self.is_spectrum_running = False

            if self.cube.animation_thread is not None:
                self.cube.abort_animation_thread = True
                self.cube.animation_thread.join()

            self.spectrumButton.setText("Start Spectrum")
        else:
            self.is_spectrum_running = True
            self.spectrumButton.setText("Stop Spectrum")

            if self.cube.animation_thread is not None:
                self.cube.abort_animation_thread = True
                self.cube.animation_thread.join()

            self.cube.abort_animation_thread = False
            self.cube.animation_thread = DoSpectrumAnimation(obj=self)
            self.cube.animation_thread.start()

    def color_picker(self):
        # opening color dialog
        color = QColorDialog.getColor()
        color_name = color.name()

        if color.isValid():
            self.color_name = color_name
            self.colorLabel.setStyleSheet("background-color: " + color_name)
            self.colorLabel.setText("Color: " + color_name)
            # self.colorLabel.adjustSize()
        else:
            self.colorLabel.setText("Color: " + self.color_name)

        self.cube.set_drawing_color(self.color_name)

    def input_fps(self):
        fps_input = QInputDialog.getInt(self, "Input fps", "FPS: ")
        fps = fps_input[0]
        fps_bool = fps_input[1]

        if fps_bool:
            if 10 <= int(fps_input[0]) <= 60:
                self.fps = fps
                self.fpsLabel.setText("FPS: " + str(fps))
                # self.fpsLabel.adjustSize()
            else:
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setIcon(QMessageBox.Critical)
                msg.setText("FPS value should be between 10 to 60.")
                msg.exec_()
        else:
            self.fpsLabel.setText("FPS: " + str(self.fps))

        self.cube.set_drawing_fps(self.fps)

    def choose_from_ready_box(self):
        current = self.readyAnimationBox.currentText()
        self.currentNameBox = current

    def load_animation(self):
        if self.currentNameBox is None:
            self.currentNameBox = "Double Outline"

        if not self.is_animation_running:
            self.is_animation_running = True
            self.loadButton.setText("Stop Animation")
            # print("Set to Stop animation")
        else:
            if self.cube.animation_thread is not None:
                self.cube.abort_animation_thread = True
                self.cube.animation_thread.join()

            self.is_animation_running = False
            self.loadButton.setText("Start Animation")
            # print("Set to Start animation")
            return

        if self.currentNameBox == "Double Outline":
            self.is_spectrum_running = False
            self.spectrumButton.setText("Start Spectrum")

            if self.cube.animation_thread is not None:
                self.cube.abort_animation_thread = True
                self.cube.animation_thread.join()

            self.cube.abort_animation_thread = False
            self.cube.animation_thread = DoDoubleOutlineAnimation(obj=self)
            self.cube.animation_thread.start()
        elif self.currentNameBox == "Outline Inside Ankle":
            self.is_spectrum_running = False
            self.spectrumButton.setText("Start Spectrum")

            if self.cube.animation_thread is not None:
                self.cube.abort_animation_thread = True
                self.cube.animation_thread.join()

            self.cube.abort_animation_thread = False
            self.cube.animation_thread = DoOutlineInsideAnkleAnimation(obj=self)
            self.cube.animation_thread.start()
        elif self.currentNameBox == "Outer Layer":
            self.is_spectrum_running = False
            self.spectrumButton.setText("Start Spectrum")

            if self.cube.animation_thread is not None:
                self.cube.abort_animation_thread = True
                self.cube.animation_thread.join()

            self.cube.abort_animation_thread = False
            self.cube.animation_thread = DoOuterLayerAnimation(obj=self)
            self.cube.animation_thread.start()
        elif self.currentNameBox == "Random Color":
            self.is_spectrum_running = False
            self.spectrumButton.setText("Start Spectrum")

            if self.cube.animation_thread is not None:
                self.cube.abort_animation_thread = True
                self.cube.animation_thread.join()

            self.cube.abort_animation_thread = False
            self.cube.animation_thread = DoRandomColorAnimation(obj=self)
            self.cube.animation_thread.start()
        elif self.currentNameBox == "Bouncy snake":
            self.is_spectrum_running = False
            self.spectrumButton.setText("Start Spectrum")

            if self.cube.animation_thread is not None:
                self.cube.abort_animation_thread = True
                self.cube.animation_thread.join()

            self.cube.abort_animation_thread = False
            self.cube.animation_thread = DoBouncySnakeAnimation(obj=self)
            self.cube.animation_thread.start()
        elif self.currentNameBox == "Sin wave":
            self.is_spectrum_running = False
            self.spectrumButton.setText("Start Spectrum")

            if self.cube.animation_thread is not None:
                self.cube.abort_animation_thread = True
                self.cube.animation_thread.join()

            self.cube.abort_animation_thread = False
            self.cube.animation_thread = DoSinWaveAnimation(obj=self)
            self.cube.animation_thread.start()
        elif self.currentNameBox == "Folder":
            self.is_spectrum_running = False
            self.spectrumButton.setText("Start Spectrum")

            if self.cube.animation_thread is not None:
                self.cube.abort_animation_thread = True
                self.cube.animation_thread.join()

            self.cube.abort_animation_thread = False
            self.cube.animation_thread = DoFolderAnimation(obj=self)
            self.cube.animation_thread.start()
        elif self.currentNameBox == "Rain":
            self.is_spectrum_running = False
            self.spectrumButton.setText("Start Spectrum")

            if self.cube.animation_thread is not None:
                self.cube.abort_animation_thread = True
                self.cube.animation_thread.join()

            self.cube.abort_animation_thread = False
            self.cube.animation_thread = DoRainAnimation(obj=self)
            self.cube.animation_thread.start()
        elif self.currentNameBox == "Color wheel":
            self.is_spectrum_running = False
            self.spectrumButton.setText("Start Spectrum")

            if self.cube.animation_thread is not None:
                self.cube.abort_animation_thread = True
                self.cube.animation_thread.join()

            self.cube.abort_animation_thread = False
            self.cube.animation_thread = DoColorWheelAnimation(obj=self)
            self.cube.animation_thread.start()
        elif self.currentNameBox in self.files:
            x = self.files.index(self.currentNameBox)
            self.cube.load_animation_from_file(self.files_path[x])
        else:
            self.pathLabel.setText("outofscope")

    def build_cube(self, cube):
        self.cube = cube
        print(self.cube)


# class AnotherWindow(QWebEngineView):
#     def __init__(self):
#         super(AnotherWindow, self).__init__()
#         self.setFixedSize(800, 800)
#         self.setWindowTitle("Cube")
#
#         self.browser = QWebEngineView(self)
#
#         self.ui()
#
#     def ui(self):
#         # web page view
#         self.browser.setUrl(QUrl("http://localhost:8980/"))
#         self.browser.setGeometry(QtCore.QRect(10, 10, 700, 700))
#         self.browser.show()

