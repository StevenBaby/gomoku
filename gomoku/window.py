# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'window.ui'
##
## Created by: Qt User Interface Compiler version 5.14.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QMetaObject,
    QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter,
    QPixmap, QRadialGradient)
from PySide2.QtWidgets import *

from ui import Board


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(939, 648)
        MainWindow.setMinimumSize(QSize(0, 0))
        icon = QIcon()
        iconThemeName = u"../skins/favicon.ico"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        MainWindow.setWindowIcon(icon)
        MainWindow.setWindowOpacity(1.000000000000000)
        MainWindow.setStyleSheet(u"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.window_layout = QHBoxLayout(self.centralwidget)
        self.window_layout.setObjectName(u"window_layout")
        self.container = QWidget(self.centralwidget)
        self.container.setObjectName(u"container")
        self.container.setMinimumSize(QSize(600, 600))
        self.label = Board(self.container)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(0, 0, 600, 600))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QSize(600, 0))
        self.label.setStyleSheet(u"background-color: rgb(170, 170, 127);")
        self.label.setPixmap(QPixmap(u"board.png"))
        self.label.setScaledContents(True)
        self.label.setAlignment(Qt.AlignCenter)

        self.window_layout.addWidget(self.container)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy1)
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.window_layout.addWidget(self.line)

        self.controller = QWidget(self.centralwidget)
        self.controller.setObjectName(u"controller")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.controller.sizePolicy().hasHeightForWidth())
        self.controller.setSizePolicy(sizePolicy2)
        self.controller.setMinimumSize(QSize(300, 0))
        self.verticalLayout = QVBoxLayout(self.controller)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.reset = QPushButton(self.controller)
        self.reset.setObjectName(u"reset")
        self.reset.setMinimumSize(QSize(0, 45))

        self.verticalLayout.addWidget(self.reset)

        self.undo = QPushButton(self.controller)
        self.undo.setObjectName(u"undo")
        self.undo.setMinimumSize(QSize(0, 45))

        self.verticalLayout.addWidget(self.undo)

        self.load = QPushButton(self.controller)
        self.load.setObjectName(u"load")
        self.load.setMinimumSize(QSize(0, 45))

        self.verticalLayout.addWidget(self.load)

        self.save = QPushButton(self.controller)
        self.save.setObjectName(u"save")
        self.save.setMinimumSize(QSize(0, 45))

        self.verticalLayout.addWidget(self.save)


        self.window_layout.addWidget(self.controller)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Gomoku", None))
        self.label.setText("")
        self.reset.setText(QCoreApplication.translate("MainWindow", u"Reset", None))
        self.undo.setText(QCoreApplication.translate("MainWindow", u"Undo", None))
        self.load.setText(QCoreApplication.translate("MainWindow", u"Load", None))
        self.save.setText(QCoreApplication.translate("MainWindow", u"Save", None))
    # retranslateUi

