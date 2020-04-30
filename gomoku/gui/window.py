# coding=utf-8
import os
import sys


from PySide2.QtWidgets import QMainWindow
from PySide2.QtGui import QIcon
from PySide2.QtGui import QPixmap

import tone

from . import skin
from gomoku.game import Game

logger = tone.utils.get_logger()


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

    def resizeEvent(self, event):
        self.ui.label.resizeEvent(event)

    def click(self, where):
        self.game.move(where)
        self.ui.label.node = self.game.head
        self.ui.label.refresh()

    def reset(self):
        self.game.reset()
        self.ui.label.node = self.game.head
        self.ui.label.refresh()

    def undo(self):
        node = self.game.undo()
        self.ui.label.node = self.game.head
        self.ui.label.refresh()

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
            self.ui.label.refresh()
        else:
            QMessageBox().warning(self, 'Warning', 'Load file failure!!!')
