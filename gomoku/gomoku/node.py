# coding=utf-8
import os
import random

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


dirname = os.path.abspath(os.path.join(__file__, '../..'))


class Node(object):

    filename = os.path.join(dirname, 'node.db')

    def __init__(
        self,
        board=None,
        where=None,
        turn=None,
        parent=None,
        depth=6,
        span=2,
        top=5,
    ):
        self.where = where
        self.next = None
        self.turn = CHESS_WHITE
        self.score = None
        self.parent = None
        self.height = 0
        self.Node = type(self)
        self.depth = depth
        self.span = span
        self.top = top
        self.children = {}
        self.searched = {}

        if board is not None:
            self.board = board
        else:
            self.board = mat(zeros((BOARD_WIDTH, BOARD_HEIGHT)), dtype=int)

        if turn is not None:
            self.turn = turn

        if self.board is not None and self.where is not None:
            self.score = Score(self.board, self.where)

        if parent:
            self.parent = parent
            self.height = parent.height + 1
            parent.next = self

    def __str__(self):
        return f'{self.where} - {self.turn_name()} - {self.get_score():0.2f}'

    def __repr__(self):
        return self.__str__()

    def turn_name(self):
        if self.turn == CHESS_BLACK:
            return 'B'
        elif self.turn == CHESS_WHITE:
            return 'W'
        else:
            return ' '

    def is_finished(self):
        if not self.score:
            return False
        return self.score.finished

    def has_chess(self, where):
        return self.board[where] != CHESS_EMPTY

    def get_score(self):
        if not self.score:
            return 0
        return self.score.score

    def set_score(self, score):
        if not self.score:
            return
        self.score.score = score

    def detect_move(self, span, top):
        if self.children:
            nodes = self.children.values()
            nodes = sorted(nodes, key=lambda e: e.get_score(), reverse=True)[:top]
            return nodes

        if self.where is None:
            node = self.move(where=(9, 9))
            return [node]

        nodes = []
        wheres = functions.get_search_wheres(self.board, span=span)
        for where in wheres:
            node = self.move(where)
            if not isinstance(node, Node):
                continue
            nodes.append(node)

        nodes = sorted(nodes, key=lambda e: e.get_score(), reverse=True)[:top]
        return nodes

    def move(self, where):
        if self.has_chess(where):
            return MOVE_STATE_FULL

        if self.is_finished():
            return MOVE_STATE_WIN

        if where in self.children:
            node = self.children[where]
            return node

        board = self.board.copy()
        turn = self.turn * -1

        board[where] = turn
        node = self.Node(board=board, turn=turn, where=where, parent=self)

        self.children[where] = node

        return node

    def save(self):
        import pickle
        with open(self.filename, 'wb') as file:
            pickle.dump(self, file)

    @classmethod
    def load(cls):
        import pickle
        try:
            with open(cls.filename, 'rb') as file:
                model = pickle.load(file)
        except Exception:
            return cls()
        if not isinstance(model, cls):
            return cls()
        return model
