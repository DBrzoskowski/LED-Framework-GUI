# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'untitlednMOOiT.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        if not mainWindow.objectName():
            mainWindow.setObjectName(u"mainWindow")
        mainWindow.resize(979, 723)
        self.actionNew = QAction(mainWindow)
        self.actionNew.setObjectName(u"actionNew")
        self.actionOpen = QAction(mainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionOpen_as = QAction(mainWindow)
        self.actionOpen_as.setObjectName(u"actionOpen_as")
        self.actionSave = QAction(mainWindow)
        self.actionSave.setObjectName(u"actionSave")
        self.actionSave_as = QAction(mainWindow)
        self.actionSave_as.setObjectName(u"actionSave_as")
        self.actionClose = QAction(mainWindow)
        self.actionClose.setObjectName(u"actionClose")
        self.actionUndo = QAction(mainWindow)
        self.actionUndo.setObjectName(u"actionUndo")
        self.actionRedo = QAction(mainWindow)
        self.actionRedo.setObjectName(u"actionRedo")
        self.actionCut = QAction(mainWindow)
        self.actionCut.setObjectName(u"actionCut")
        self.actionCopy = QAction(mainWindow)
        self.actionCopy.setObjectName(u"actionCopy")
        self.actionPaste = QAction(mainWindow)
        self.actionPaste.setObjectName(u"actionPaste")
        self.actionDelete = QAction(mainWindow)
        self.actionDelete.setObjectName(u"actionDelete")
        self.actionAbout = QAction(mainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionCheck_for_updates = QAction(mainWindow)
        self.actionCheck_for_updates.setObjectName(u"actionCheck_for_updates")
        self.actionRun_project = QAction(mainWindow)
        self.actionRun_project.setObjectName(u"actionRun_project")
        self.actionStop = QAction(mainWindow)
        self.actionStop.setObjectName(u"actionStop")
        self.centralwidget = QWidget(mainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        mainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(mainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 979, 21))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuRun = QMenu(self.menubar)
        self.menuRun.setObjectName(u"menuRun")
        mainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(mainWindow)
        self.statusbar.setObjectName(u"statusbar")
        mainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuRun.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionOpen_as)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_as)
        self.menuFile.addAction(self.actionClose)
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionCut)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)
        self.menuEdit.addAction(self.actionDelete)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionCheck_for_updates)
        self.menuRun.addAction(self.actionRun_project)
        self.menuRun.addAction(self.actionStop)

        self.retranslateUi(mainWindow)

        QMetaObject.connectSlotsByName(mainWindow)
    # setupUi

    def retranslateUi(self, mainWindow):
        mainWindow.setWindowTitle(QCoreApplication.translate("mainWindow", u"LED Framework GUI", None))
        self.actionNew.setText(QCoreApplication.translate("mainWindow", u"New", None))
        self.actionOpen.setText(QCoreApplication.translate("mainWindow", u"Open", None))
        self.actionOpen_as.setText(QCoreApplication.translate("mainWindow", u"Open as", None))
        self.actionSave.setText(QCoreApplication.translate("mainWindow", u"Save", None))
        self.actionSave_as.setText(QCoreApplication.translate("mainWindow", u"Save as", None))
        self.actionClose.setText(QCoreApplication.translate("mainWindow", u"Close", None))
        self.actionUndo.setText(QCoreApplication.translate("mainWindow", u"Undo", None))
        self.actionRedo.setText(QCoreApplication.translate("mainWindow", u"Redo", None))
        self.actionCut.setText(QCoreApplication.translate("mainWindow", u"Cut", None))
        self.actionCopy.setText(QCoreApplication.translate("mainWindow", u"Copy", None))
        self.actionPaste.setText(QCoreApplication.translate("mainWindow", u"Paste", None))
        self.actionDelete.setText(QCoreApplication.translate("mainWindow", u"Delete", None))
        self.actionAbout.setText(QCoreApplication.translate("mainWindow", u"About", None))
        self.actionCheck_for_updates.setText(QCoreApplication.translate("mainWindow", u"Check for updates", None))
        self.actionRun_project.setText(QCoreApplication.translate("mainWindow", u"Run {file_name}", None))
        self.actionStop.setText(QCoreApplication.translate("mainWindow", u"Stop", None))
        self.menuFile.setTitle(QCoreApplication.translate("mainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("mainWindow", u"Edit", None))
        self.menuHelp.setTitle(QCoreApplication.translate("mainWindow", u"Help", None))
        self.menuRun.setTitle(QCoreApplication.translate("mainWindow", u"Run", None))
    # retranslateUi
