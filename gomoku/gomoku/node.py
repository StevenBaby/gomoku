# coding=utf-8

import numpy as np
from numpy import mat
from numpy import zeros

import tone

from . import BOARD_WIDTH
from . import BOARD_HEIGHT
from . import CHESS_WHITE
from . import CHESS_BLACK
from . import CHESS_EMPTY
from . import DEPTH_DEFAULT
from . import MOVE_STATE_WIN
from . import MOVE_STATE_FULL
from . import MOVE_STATE_NONE
from .score import Score
from . import functions

logger = tone.utils.get_logger()


class Node(object):

    def __init__(self, board=None, where=None, turn=None, parent=None):
        self.where = where
        self.next = None

        if board is not None:
            self.board = board
        else:
            self.board = mat(zeros((BOARD_WIDTH, BOARD_HEIGHT)), dtype=int)
        if turn:
            self.turn = turn
        else:
            self.turn = CHESS_WHITE

        if self.board is not None and self.where is not None:
            self.score = Score(self.board, self.where)
        else:
            self.score = None

        if parent:
            self.parent = parent
            parent.next = self
        else:
            self.parent = None

        self.loss = 0
        self.children = {}

    def is_finished(self):
        if not self.score:
            return False
        return self.score.finished

    def has_chess(self, where):
        return self.board[where] != CHESS_EMPTY

    def move(self, where, next=True):
        if self.has_chess(where):
            return MOVE_STATE_FULL

        if self.is_finished():
            return MOVE_STATE_WIN

        board = self.board.copy()
        turn = self.turn * -1
        board[where] = turn
        node = Node(board=board, turn=turn, where=where, parent=self)
        return node
