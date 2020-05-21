# coding=utf-8
import os
import sys
import threading

from PySide2.QtWidgets import QMainWindow
from PySide2.QtGui import QIcon
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QFileDialog
from PySide2.QtWidgets import QMessageBox
from PySide2 import QtCore

import tone

import gomoku
from . import skin
from gomoku.game import Game

logger = tone.utils.get_logger()


class NextThread(QtCore.QThread):
    signal = QtCore.Signal()

    def run(self):
        self.game.move()
        self.signal.emit()


class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        from .ui import Ui_MainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(skin.ICON_IMAGE))
        self.setWindowTitle(u"Gomoku")
        self.ui.label.setPixmap(QPixmap(skin.BOARD_IMAGE))

        self.ui.label.click = self.click
        self.ui.reset.clicked.connect(self.reset)
        self.ui.undo.clicked.connect(self.undo)
        self.ui.load.clicked.connect(self.load)
        self.ui.save.clicked.connect(self.save)

        self.game = Game()
        self.thread = NextThread()
        self.thread.game = self.game
        self.thread.signal.connect(
            self.update_next_move,
            QtCore.Qt.QueuedConnection
        )

    def resizeEvent(self, event):
        self.ui.label.resizeEvent(event)

    def refresh(self):
        import gomoku
        chess = self.game.head.turn
        if chess == gomoku.CHESS_WHITE:
            text = '''<html>
                    <body>
                        <p align="center">
                            <span style=" font-size:14pt; font-weight:600;">
                                black
                            </span>
                        </p>
                    </body>
                    </html>'''
        elif chess == gomoku.CHESS_BLACK:
            text = '''<html>
                    <body>
                        <p align="center">
                            <span style=" font-size:14pt; font-weight:600;">
                                white
                            </span>
                        </p>
                    </body>
                    </html>'''
        self.ui.chess.setText(text)
        self.ui.label.refresh()

    def check(self):
        if self.game.head.score.finished:
            if self.game.head.turn == gomoku.CHESS_BLACK:
                QMessageBox().information(self, 'Info', 'Victory!!!')
            else:
                QMessageBox().information(self, 'Info', 'Lose!!!')
            return True
        return False

    def click(self, where):
        if self.thread.isRunning():
            return

        self.game.move(where=where)
        self.ui.label.node = self.game.head
        self.refresh()
        if self.check():
            return

        self.setCursor(QtCore.Qt.WaitCursor)
        self.thread.start()

    def update_next_move(self):
        self.ui.label.node = self.game.head
        self.refresh()
        self.setCursor(QtCore.Qt.ArrowCursor)
        if self.check():
            return

    def reset(self):
        self.game.reset()
        self.ui.label.node = self.game.head
        self.refresh()

    def undo(self):
        self.game.undo()
        self.ui.label.node = self.game.head
        self.refresh()

    def save(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        filename = dialog.getSaveFileName(
            self, "Open Gomoku", ".", "Gomoku Files (*.pickle)")[0]
        if not filename:
            return
        self.game.save(filename)

    def load(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        filename = dialog.getOpenFileName(
            self, "Open Gomoku", ".", "Gomoku Files (*.pickle)")[0]
        if not filename:
            return

        if self.game.load(filename):
            self.ui.label.node = self.game.head
            self.refresh()
        else:
            QMessageBox().warning(self, 'Warning', 'Load file failure!!!')
