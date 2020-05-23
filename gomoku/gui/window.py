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


class ComputeThread(QtCore.QThread):

    signal = QtCore.Signal()

    def __init__(self, window):
        super().__init__()
        self.window = window

    def run(self):
        self.window.game.move()
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
        self.ui.hint.clicked.connect(self.hint)
        self.ui.reverse.clicked.connect(self.reverse)

        self.game = Game()
        self.thread = ComputeThread(self)
        self.thread.signal.connect(
            self.post_compute,
            QtCore.Qt.QueuedConnection
        )

        self.hinting = False

    def resizeEvent(self, event):
        self.ui.label.resizeEvent(event)

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            'Message',
            "Do you want to save trained models?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.accept()

    def refresh(self):
        import gomoku
        chess = self.game.head.turn
        if chess == gomoku.CHESS_WHITE:
            text = skin.LABEL_STYLE.format(text="black")
        elif chess == gomoku.CHESS_BLACK:
            text = skin.LABEL_STYLE.format(text="white")
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

        self.compute()

    def compute(self):
        self.setCursor(QtCore.Qt.WaitCursor)
        self.thread.start()
        # self.game.move()
        # self.post_compute()

    def post_compute(self):
        self.ui.label.node = self.game.head
        self.refresh()
        self.setCursor(QtCore.Qt.ArrowCursor)
        if self.check():
            return
        if self.hinting:
            self.hinting = False
            self.compute()

    def hint(self):
        self.hinting = True
        self.compute()

    def reverse(self):
        self.compute()

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
