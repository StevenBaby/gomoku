# coding=utf-8
import os
import sys

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

import gomoku

DIRNAME = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(DIRNAME)


SKINSPATH = os.path.join(PROJECT, 'skins')

WINDOW_UI = os.path.join(SKINSPATH, 'window.ui')

ICON_IMAGE = os.path.join(SKINSPATH, 'favicon.ico')
BOARD_IMAGE = os.path.join(SKINSPATH, 'board.png')
BLACK_IMAGE = os.path.join(SKINSPATH, 'black.png')
WHITE_IMAGE = os.path.join(SKINSPATH, 'white.png')


class Board(object):

    def __init__(self, window):
        self.window = window

        self.label = window.ui.label
        self.label.setPixmap(QPixmap(config.BOARD_IMAGE))

        self.labels = mat(zeros((gomoku.WIDTH, gomoku.HEIGHT,)), dtype=QLabel)

    def clicked(self):
        pass

    def makeChess(self):
        chess = QLabel(self.ui.container)
        self.label_2.setGeometry(QRect(220, 130, 100, 100))
        self.label_2.setPixmap(QPixmap(u"black.png"))
        self.label_2.setScaledContents(True)

    def resizeBoard(self):
        geometry = self.window.ui.container.frameGeometry()
        size = min(geometry.width(), geometry.height())

        x = int((geometry.width() - size) / 2)
        y = int((geometry.height() - size) / 2)

        self.label.setGeometry(QRect(x, y, size, size))

    def resizeEvent(self, event):
        self.resizeBoard()


class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        self.ui = QUiLoader().load(config.WINDOW_UI)
        self.setWindowIcon(QIcon(config.ICON_IMAGE))
        self.setWindowTitle(u"Gomoku")
        self.setCentralWidget(self.ui)
        self.resize(939, 618)

        self.board = Board(self)

    def resizeEvent(self, event):
        self.board.resizeEvent(event)
        # super().resizeEvent(event)


class Application(object):

    def __init__(self):
        self.app = self.load_app()
        self.window = Window()

    def load_app(self):
        from PySide2.QtWidgets import QApplication
        from PySide2 import QtCore
        app = QApplication(sys.argv)
        return app

    def run(self):
        self.window.show()
        self.app.exec_()


def main():
    app = Application()
    app.run()


if __name__ == '__main__':
    main()
