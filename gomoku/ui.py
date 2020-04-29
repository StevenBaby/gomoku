# coding=utf-8
import os

from numpy import mat
from numpy import zeros

from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QMainWindow
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile
from PySide2.QtGui import QIcon
from PySide2.QtGui import QPixmap
from PySide2.QtCore import QRect
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtCore import Qt
from PySide2.QtCore import QObject
from PySide2 import QtCore

import gomoku
import tone


DIRNAME = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(DIRNAME)


SKINSPATH = os.path.join(PROJECT, 'skins')

WINDOW_UI = os.path.join(SKINSPATH, 'window.ui')

ICON_IMAGE = os.path.join(SKINSPATH, 'favicon.ico')
BOARD_IMAGE = os.path.join(SKINSPATH, 'board.png')
BLACK_IMAGE = os.path.join(SKINSPATH, 'black.png')
WHITE_IMAGE = os.path.join(SKINSPATH, 'white.png')


logger = tone.utils.get_logger()


class Board(QLabel):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.parent = parent
        self.labels = mat(zeros((gomoku.WIDTH, gomoku.HEIGHT,)), dtype=QLabel)

    def mousePressEvent(self, event):
        logger.debug("board clicked")

        x = event.x()
        y = event.y()

        

    def makeChess(self):
        chess = QLabel(self.parent)
        self.label_2.setGeometry(QRect(220, 130, 100, 100))
        self.label_2.setPixmap(QPixmap(u"black.png"))
        self.label_2.setScaledContents(True)

    def resizeBoard(self):
        geometry = self.parent.frameGeometry()
        size = min(geometry.width(), geometry.height())

        x = int((geometry.width() - size) / 2)
        y = int((geometry.height() - size) / 2)

        self.setGeometry(QRect(x, y, size, size))

    def resizeEvent(self, event):
        self.resizeBoard()


class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        from window import Ui_MainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(ICON_IMAGE))
        self.setWindowTitle(u"Gomoku")
        self.ui.label.setPixmap(QPixmap(BOARD_IMAGE))
        # self.resize(939, 618)

    def resizeEvent(self, event):
        self.ui.label.resizeEvent(event)
        # super().resizeEvent(event)

    # def mousePressEvent(self, event):
    #     logger.debug('hello event')
