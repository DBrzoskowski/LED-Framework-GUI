from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *

from Led_animation import Cube3D
import math
from vpython import color

class Ui_MainWindow(QMainWindow):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(819, 605)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setGeometry(QtCore.QRect(30, 400, 201, 131))

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startButton.sizePolicy().hasHeightForWidth())

        self.startButton.setSizePolicy(sizePolicy)
        self.startButton.setObjectName("startButton")

        self.pauseButton = QtWidgets.QPushButton(self.centralwidget)
        self.pauseButton.setGeometry(QtCore.QRect(550, 400, 201, 131))
        self.pauseButton.setObjectName("pauseButton")

        self.stopButton = QtWidgets.QPushButton(self.centralwidget)
        self.stopButton.setGeometry(QtCore.QRect(290, 400, 201, 131))
        self.stopButton.setObjectName("stopButton")

        self.openButton = QtWidgets.QPushButton(self.centralwidget)
        self.openButton.setGeometry(QtCore.QRect(430, 130, 191, 101))
        self.openButton.setObjectName("openButton")
        self.openButton.clicked.connect(self.showPath)

        self.pathLabel = QtWidgets.QLabel(self.centralwidget)
        self.pathLabel.setGeometry(QtCore.QRect(440, 250, 171, 21))
        self.pathLabel.setObjectName("pathLabel")

        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(30, 360, 751, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")

        self.loadButton = QtWidgets.QPushButton(self.centralwidget)
        self.loadButton.setGeometry(QtCore.QRect(650, 10, 151, 71))
        self.loadButton.setObjectName("loadButton")

        self.readyAnimationBox = QtWidgets.QComboBox(self.centralwidget)
        self.readyAnimationBox.setGeometry(QtCore.QRect(650, 90, 151, 21))
        self.readyAnimationBox.setObjectName("readyAnimationBox")

        self.createButton = QtWidgets.QPushButton(self.centralwidget)
        self.createButton.setGeometry(QtCore.QRect(10, 10, 191, 101))
        self.createButton.setObjectName("createButton")
        self.createButton.clicked.connect(self.createAnimation)

        self.saveButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveButton.setGeometry(QtCore.QRect(220, 10, 191, 101))
        self.saveButton.setObjectName("saveButton")

        self.endButton = QtWidgets.QPushButton(self.centralwidget)
        self.endButton.setGeometry(QtCore.QRect(430, 10, 191, 101))
        self.endButton.setObjectName("endButton")

        self.colorChooseButton = QtWidgets.QPushButton(self.centralwidget)
        self.colorChooseButton.setGeometry(QtCore.QRect(10, 130, 191, 101))
        self.colorChooseButton.setObjectName("colorChooseButton")
        self.colorChooseButton.clicked.connect(self.colorPicker)

        self.colorLabel = QtWidgets.QLabel(self.centralwidget)
        self.colorLabel.setGeometry(QtCore.QRect(80, 250, 51, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.colorLabel.setFont(font)
        self.colorLabel.setObjectName("colorLabel")

        self.frequencyChooseButton = QtWidgets.QPushButton(self.centralwidget)
        self.frequencyChooseButton.setGeometry(QtCore.QRect(220, 130, 191, 101))
        self.frequencyChooseButton.setObjectName("frequencyChooseButton")
        self.frequencyChooseButton.clicked.connect(self.inputFreq)

        self.frequencyLabel = QtWidgets.QLabel(self.centralwidget)
        self.frequencyLabel.setGeometry(QtCore.QRect(220, 250, 191, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.frequencyLabel.setFont(font)
        self.frequencyLabel.setObjectName("frequencyLabel")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 819, 21))
        self.menubar.setObjectName("menubar")

        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.actionNew = QtWidgets.QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")

        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")

        self.actionSave_As = QtWidgets.QAction(MainWindow)
        self.actionSave_As.setObjectName("actionSave_As")

        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")

        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")

        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_As)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "3D LED Framework"))
        self.startButton.setText(_translate("MainWindow", "Start"))
        self.pauseButton.setText(_translate("MainWindow", "Pause"))
        self.stopButton.setText(_translate("MainWindow", "Stop"))
        self.openButton.setText(_translate("MainWindow", "Open animation from file"))
        self.pathLabel.setText(_translate("MainWindow", "Path: "))
        self.loadButton.setText(_translate("MainWindow", "Load animation"))
        self.createButton.setText(_translate("MainWindow", "Create animation"))
        self.saveButton.setText(_translate("MainWindow", "Save animation"))
        self.endButton.setText(_translate("MainWindow", "End creating animation"))
        self.colorChooseButton.setText(_translate("MainWindow", "Choose color"))
        self.colorLabel.setText(_translate("MainWindow", "Color"))
        self.frequencyChooseButton.setText(_translate("MainWindow", "Choose frequency"))
        self.frequencyLabel.setText(_translate("MainWindow", "Your frequency is: <frequency>"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionNew.setText(_translate("MainWindow", "New"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave_As.setText(_translate("MainWindow", "Save As"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))

    def colorPicker(self):
        # opening color dialog
        color = QColorDialog.getColor()
        color_name = color.name()

        self.colorLabel.setStyleSheet("background-color: " + color_name)
        self.colorLabel.setText(color_name)
        self.colorLabel.adjustSize()

    def showPath(self):
        # open file dialog
        file = QFileDialog.getOpenFileName(self, "Open animation file", "", "Text Files (*.txt)")

        if file:
            self.pathLabel.setText("Path: " + file[0])
            self.pathLabel.adjustSize()

    def inputFreq(self):
        freq_input = QInputDialog.getText(self, "Input frequency", "Frequency: ")
        if input:
            self.frequencyLabel.setText("Your frequency is: " + freq_input[0])
            self.pathLabel.adjustSize()

    def createAnimation(self):
        c = Cube3D(8, 0.15 * 1, 1, 0.1 * 1 * math.sqrt(1 / 1))
        c.background = color.white


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
