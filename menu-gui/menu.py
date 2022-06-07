from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
import sys

from Led_animation import Cube3D
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


class AppWindow(QMainWindow):
    def __init__(self):
        super(AppWindow, self).__init__()
        self.setFixedSize(843, 549)
        self.setWindowTitle("3D LED Framework")
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        self.c = Cube3D(8, 0.15 * 1, 1, 0.1 * 1 * math.sqrt(1 / 1))
        self.c.background = color.black

        # create buttons
        self.createButton = QtWidgets.QPushButton(self)
        self.saveFrameButton = QtWidgets.QPushButton(self)
        self.saveButton = QtWidgets.QPushButton(self)
        self.endButton = QtWidgets.QPushButton(self)
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
        self.recentAnimationLabel = QtWidgets.QLabel(self)

        # create boxes
        self.readyAnimationBox = QtWidgets.QComboBox(self)
        self.recentAnimationBox = QtWidgets.QComboBox(self)

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

        self.saveButton.setGeometry(QtCore.QRect(430, 30, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.saveButton.setFont(font)
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setStyleSheet(QPushButton_style)
        self.fpsButton.clicked.connect(self.saveAnimation)

        self.endButton.setGeometry(QtCore.QRect(640, 30, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.endButton.setFont(font)
        self.endButton.setObjectName("endButton")
        self.endButton.setStyleSheet(QPushButton_style)
        self.endButton.clicked.connect(self.deleteAnimation)

        self.openButton.setGeometry(QtCore.QRect(10, 150, 191, 101))
        font = QtGui.QFont()
        font.setPointSize(24)
        self.openButton.setFont(font)
        self.openButton.setObjectName("openButton")
        self.openButton.setStyleSheet(QPushButton_style)
        self.openButton.clicked.connect(self.showPath)

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

        self.loadButton.setGeometry(QtCore.QRect(510, 340, 321, 41))
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

        self.readyAnimationLabel.setGeometry(QtCore.QRect(510, 390, 151, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.readyAnimationLabel.setFont(font)
        self.readyAnimationLabel.setObjectName("readyAnimationLabel")

        self.recentAnimationLabel.setGeometry(QtCore.QRect(680, 390, 151, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.recentAnimationLabel.setFont(font)
        self.recentAnimationLabel.setObjectName("recentAnimationLabel")

        # boxes
        self.readyAnimationBox.setGeometry(QtCore.QRect(510, 410, 151, 21))
        self.readyAnimationBox.setObjectName("readyAnimationBox")
        self.readyAnimationBox.addItem("Double Outline")
        self.readyAnimationBox.addItem("Outline Inside Ankle")
        self.readyAnimationBox.addItem("Outer Layer")
        self.readyAnimationBox.addItem("Random Color")
        self.readyAnimationBox.activated[str].connect(self.chooseFromReadyBox)
        # self.loadButton.clicked.connect(self.loadFromBox(str(current)))

        self.recentAnimationBox.setGeometry(QtCore.QRect(680, 410, 151, 21))
        self.recentAnimationBox.setObjectName("recentAnimationBox")

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("AppWindow", "3D LED Framework"))
        self.createButton.setText(_translate("AppWindow", "Create animation"))
        self.saveFrameButton.setText(_translate("AppWindow", "Save frame"))
        self.saveButton.setText(_translate("AppWindow", "Save animation"))
        self.endButton.setText(_translate("AppWindow", "End animation"))
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
        self.recentAnimationLabel.setText(_translate("AppWindow", "Recent animations"))

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
        # return color_name
        # Cube3D.drawing(self, color_name)
        # self.c.drawing(color_name)

    def showPath(self):
        # open file dialog
        file = QFileDialog.getOpenFileName(self, "Open animation file", "", "Text Files (*.txt)")
        # create file name
        file_path = file[0]
        file_path_list = file_path.split("/")
        file_name = file_path_list[-1]

        if file:
            self.pathLabel.setText("Path: " + file_path)
            self.pathLabel.setWordWrap(True)
            # font = QtGui.QFont()
            # font.setPointSize(8)
            # self.pathLabel.setFont(font)
            self.pathLabel.adjustSize()

            self.recentAnimationBox.addItem(file_name)
#            self.c.load_sim_animation_from_file()

#        Cube3D.load_sim_animation_from_file(self, str(file[0]))
#        self.c.load_sim_animation_from_file(file_path)

    def inputFps(self):
        fps_input = QInputDialog.getInt(self, "Input fps", "FPS: ")
        if input:
            if 10 <= int(fps_input[0]) <= 60:
                self.fpsLabel.setText("FPS: " + str(fps_input[0]))
                self.pathLabel.adjustSize()
            else:
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setIcon(QMessageBox.Critical)
                msg.setText("FPS value should be between 10 to 60.")
                msg.exec_()

    # need fps and color method by Damian
    def createAnimation(self):
        # self.c.drawing()
        pass
        # return c

    def chooseFromReadyBox(self):
        current = self.readyAnimationBox.currentText()
        # self.pathLabel.setText(str(asd))
        # return current
        if current == "Double Outline":
            self.pathLabel.setText("1")
#            self.c.double_outline_animation(self, 1)
        elif current == "Outline Inside Ankle":
            self.pathLabel.setText("2")
        elif current == "Outer Layer":
            self.pathLabel.setText("3")
            self.c.outer_layer_animation()
        elif current == "Random Color":
            self.pathLabel.setText("4")
        else:
            self.pathLabel.setText("outofscope")

    def loadFromBox(self, current):
        pass
#         if current == "Double Outline":
#             self.pathLabel.setText("1")
# #            Cube3D.double_outline_animation(self, (1, 1, 1), fps=30)
#         elif current == "Outline Inside Ankle":
#             self.pathLabel.setText("2")
#         elif current == "Outer Layer":
#             self.pathLabel.setText("3")
#         elif current == "Random Color":
#             self.pathLabel.setText("4")
#         else:
#             self.pathLabel.setText("outofscope")

    # need drawing function
    def saveAnimation(self):
        pass
        # self.c.save_sim_animation()

    def loadAnimationFromTheBox(self):
        pass

    def startAnimation(self):
        self.animationStateLabel.setText("Animation state: Active")
        self.animationStateLabel.setStyleSheet(animationStateLabel_green)
        self.animationStateLabel.update()

    def stopAnimation(self):
        self.animationStateLabel.setText("Animation state: Inactive")
        self.animationStateLabel.setStyleSheet(animationStateLabel_red)
        self.animationStateLabel.update()

    def deleteAnimation(self):
        self.c.delete()
        # add close tab


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(background_style)
    win = AppWindow()
    win.show()
    sys.exit(app.exec_())
