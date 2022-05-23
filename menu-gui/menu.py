from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
# from animation import Cube3D
import sys


class AppWindow(QMainWindow):
    def __init__(self):
        super(AppWindow, self).__init__()
        # 400 and 200 app window position
        # 1000 width of app window and 600 heigh
        self.setGeometry(400, 200, 1000, 600)
        self.setWindowTitle("3D LED Framework")
        self.ui()

    def ui(self):
        self.btn1 = QtWidgets.QPushButton(self)
        self.btn1.setText("Start")
        self.btn1.clicked.connect(self.UiComponents)

    def clicked(self):
        self.btn1.setText("Exit")
        self.update()

    def update(self):
        self.btn1.adjustSize()

    def UiComponents(self):
        # opening color dialog
        color = QColorDialog.getColor()

        # creating label to display the color
        self.label1 = QLabel(self)

        # setting geometry to the label
        self.label1.setGeometry(100, 100, 200, 60)

        # making label multi line
        self.label1.setWordWrap(True)

        # setting stylesheet of the label
        self.label1.setStyleSheet("QLabel"
                            "{"
                            "border : 5px solid black;"
                            "}")

        # setting text to the label
        self.label1.setText(str(color))

        # setting graphic effect to the label
        graphic = QGraphicsColorizeEffect(self)

        # setting color to the graphic
        graphic.setColor(color)

        # setting graphic to the label
        self.label1.setGraphicsEffect(graphic)


def window():
    app = QApplication(sys.argv)
    win = AppWindow()

    win.show()
    sys.exit(app.exec_())


window()
