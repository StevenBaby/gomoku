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
        self.edge_x = 15
        self.edge_y = 15
        self.cell_size = 31

    def mousePressEvent(self, event):
        logger.debug("board clicked %s - %s - %s - %s",
                     event.x(), event.y(),
                     self.x(), self.y(),
                     )
        where = self.getPosition(event)
        logger.debug('get position %s', where)
        if where:
            self.setChess(where, gomoku.BLACK)

    def getPosition(self, event):
        pos_x = event.x()
        pos_y = event.y()

        x = (pos_x - self.edge_x) // self.cell_size
        y = (pos_y - self.edge_y) // self.cell_size

        if x < 0 or y < 0:
            return None
        if x > gomoku.WIDTH or y > gomoku.HEIGHT:
            return None

        where = (x, y)
        return where

    def setChess(self, where, chess):
        label = self.labels[where]
        if not label:
            logger.debug('init label for chess')
            label = QLabel(self)
            self.labels[where] = label

        if chess == gomoku.BLACK:
            image = QPixmap(BLACK_IMAGE)
        else:
            image = QPixmap(WHITE_IMAGE)

        rect = QRect(
            (where[0] * self.cell_size) + (self.cell_size),
            (where[1] * self.cell_size) + (self.cell_size),
            self.cell_size,
            self.cell_size)
        label.setPixmap(image)
        label.setScaledContents(True)
        label.setGeometry(rect)
        label.setVisible(True)

        logger.debug(rect)

    def resizeBoard(self):
        geometry = self.parent.frameGeometry()
        size = min(geometry.width(), geometry.height())

        x = (geometry.width() - size) // 2
        y = (geometry.height() - size) // 2
        self.setGeometry(QRect(x, y, size, size))

        self.cell_size = int(size / gomoku.WIDTH)
        self.edge_x = self.cell_size // 4
        self.edge_y = self.cell_size // 4

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
