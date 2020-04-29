# coding=utf-8
import os

import numpy as np
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
from PySide2.QtCore import QRectF
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtCore import Qt
from PySide2.QtCore import QObject
from PySide2 import QtCore

from PySide2.QtWidgets import QFileDialog
from PySide2.QtWidgets import QMessageBox

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
        self.labels = mat(zeros((gomoku.BOARD_WIDTH, gomoku.BOARD_HEIGHT,)), dtype=QLabel)
        self.size = 600
        self.gomoku = gomoku.Gomoku()
        self.refresh()

    def mousePressEvent(self, event):
        pos = self.getPosition(event)
        logger.debug('get position %s', pos)
        if not pos:
            return

        where = (pos[1], pos[0])
        state = self.gomoku.move(where)
        if state == gomoku.MOVE_STATE_NONE:
            self.refresh()
        elif state == gomoku.MOVE_STATE_FULL:
            pass
        elif state == gomoku.MOVE_STATE_WIN:
            self.refresh()
            QMessageBox.information(self.parent, 'Information', "Victory!!!")

    def getPosition(self, event):
        x = int((event.x() - self.getEdge()) / self.getCellSize())
        y = int((event.y() - self.getEdge()) / self.getCellSize())

        if x < 0 or y < 0:
            return None
        if x >= gomoku.BOARD_WIDTH or y >= gomoku.BOARD_HEIGHT:
            return None

        pos = (x, y)
        return pos

    def hasChess(self, pos):
        return isinstance(self.labels[pos], QLabel)

    def setChess(self, pos, chess):
        label = self.labels[pos]
        if not label:
            label = QLabel(self)
            self.labels[pos] = label

        if chess == gomoku.CHESS_BLACK:
            image = QPixmap(BLACK_IMAGE)
        elif chess == gomoku.CHESS_WHITE:
            image = QPixmap(WHITE_IMAGE)
        else:
            label.setVisible(False)
            return

        # label.setStyleSheet(u"background-color: rgb(0, 170, 127);")
        label.setPixmap(image)
        label.setScaledContents(True)
        label.setGeometry(self.getChessGeometry(pos))
        label.setVisible(True)

    def getCellSize(self):
        return self.size / (gomoku.BOARD_WIDTH + 1)

    def refresh(self):
        chess = self.gomoku.turn
        if chess == gomoku.CHESS_BLACK:
            text = '''<html>
                    <body>
                        <p align="center">
                            <span style=" font-size:14pt; font-weight:600;">
                                black
                            </span>
                        </p>
                    </body>
                    </html>'''
        elif chess == gomoku.CHESS_WHITE:
            text = '''<html>
                    <body>
                        <p align="center">
                            <span style=" font-size:14pt; font-weight:600;">
                                white
                            </span>
                        </p>
                    </body>
                    </html>'''
        if hasattr(self, 'main'):
            self.main.ui.chess.setText(text)

        for x in range(gomoku.BOARD_WIDTH):
            for y in range(gomoku.BOARD_HEIGHT):
                where = (x, y)
                pos = (y, x)
                self.setChess(pos, self.gomoku.board[where])

    def getEdge(self):
        return self.getCellSize() / 2

    def getChessGeometry(self, pos):
        return QRect(
            int((pos[0] * self.getCellSize()) + (self.getEdge())),
            int((pos[1] * self.getCellSize()) + (self.getEdge())),
            int(self.getCellSize()),
            int(self.getCellSize())
        )

    def resizeEvent(self, event):
        geometry = self.parent.frameGeometry()
        size = min(geometry.width(), geometry.height())

        x = (geometry.width() - size) // 2
        y = (geometry.height() - size) // 2
        self.setGeometry(QRect(x, y, size, size))
        self.size = size

        for x in range(gomoku.BOARD_WIDTH):
            for y in range(gomoku.BOARD_HEIGHT):
                pos = (x, y)
                if not self.hasChess(pos):
                    continue
                label = self.labels[pos]
                label.setGeometry(self.getChessGeometry(pos))


class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        from window import Ui_MainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(ICON_IMAGE))
        self.setWindowTitle(u"Gomoku")
        self.ui.label.setPixmap(QPixmap(BOARD_IMAGE))
        self.ui.label.main = self

        self.gomoku = self.ui.label.gomoku

        self.ui.reset.clicked.connect(self.reset)
        self.ui.undo.clicked.connect(self.undo)
        self.ui.load.clicked.connect(self.load)
        self.ui.save.clicked.connect(self.save)

    def resizeEvent(self, event):
        self.ui.label.resizeEvent(event)

    def reset(self):
        self.gomoku.reset()
        self.ui.label.refresh()

    def undo(self):
        node = self.gomoku.undo()
        self.ui.label.refresh()

    def save(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        filename = dialog.getSaveFileName(
            self, "Open Gomoku", ".", "Gomoku Files (*.pickle)")[0]
        if not filename:
            return
        self.gomoku.save(filename)

    def load(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        filename = dialog.getOpenFileName(
            self, "Open Gomoku", ".", "Gomoku Files (*.pickle)")[0]
        if not filename:
            return

        if self.gomoku.load(filename):
            self.ui.label.refresh()
        else:
            QMessageBox().warning(self, 'Warning', 'Load file failure!!!')
