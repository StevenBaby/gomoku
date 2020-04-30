# coding=utf-8

import numpy as np
from numpy import mat
from numpy import zeros

from PySide2.QtWidgets import QLabel
from PySide2.QtCore import QRect
from PySide2.QtGui import QPixmap

import tone

import skin
import gomoku
from gomoku import node
from gomoku import functions


logger = tone.utils.get_logger()


class Board(QLabel):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.parent = parent
        self.labels = mat(zeros((gomoku.BOARD_WIDTH, gomoku.BOARD_HEIGHT,)), dtype=QLabel)
        self.size = 600
        self.node = node.Node()
        self.refresh()

    def click(self, where):
        pass

    def mousePressEvent(self, event):
        pos = self.getPosition(event)
        if not pos:
            return
        if self.hasChess(pos):
            return
        logger.debug('get position %s', pos)
        where = (pos[1], pos[0])
        self.click(where)

    def getPosition(self, event):
        x = int((event.x() - self.getEdge()) / self.getCellSize())
        y = int((event.y() - self.getEdge()) / self.getCellSize())

        pos = (x, y)
        if not functions.is_valid_where(pos):
            return None
        return pos

    def hasChess(self, pos):
        label = self.labels[pos]
        if not isinstance(label, QLabel):
            return False
        return label.isVisible()

    def setChess(self, pos, chess):
        label = self.labels[pos]
        if not label:
            label = QLabel(self)
            self.labels[pos] = label

        if chess == gomoku.CHESS_BLACK:
            image = QPixmap(skin.BLACK_IMAGE)
        elif chess == gomoku.CHESS_WHITE:
            image = QPixmap(skin.WHITE_IMAGE)
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
        for x in range(gomoku.BOARD_WIDTH):
            for y in range(gomoku.BOARD_HEIGHT):
                where = (x, y)
                pos = (y, x)
                self.setChess(pos, self.node.board[where])

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
