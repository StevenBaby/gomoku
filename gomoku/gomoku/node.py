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
        depth=None,
        span=None,
        top=None,
    ):
        self.where = where
        self.next = None
        self.turn = CHESS_WHITE
        self.score = None  # current score of compute
        self._score = None  # number of evaluated
        self.parent = None
        self.height = 0
        self.Node = type(self)
        self.depth = depth
        self.span = span
        self.top = top

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
        return f'{self.where} - {self.turn_name()} - [{self.get_score():0.1f}]'

    def __repr__(self):
        return self.__str__()

    def turn_name(self):
        if self.turn == CHESS_BLACK:
            return 'B'
        elif self.turn == CHESS_WHITE:
            return 'W'
        else:
            return ' '

    def gameover(self):
        if not self.score:
            return False
        return self.score.gameover

    def has_chess(self, where):
        return self.board[where] != CHESS_EMPTY

    def __lt__(self, other):
        return self.get_score() < other.get_score()

    def get_score(self):
        if self._score is not None:
            return self._score
        if not self.score:
            return 0
        return self.score.score * self.turn

    def set_score(self, score):
        self._score = score

    def detect_move(self, span, top):
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

        cnodes = sorted(nodes, key=lambda e: e.score.cscore, reverse=True)[:top]
        rnodes = sorted(nodes, key=lambda e: e.score.rscore, reverse=True)[:top]
        result = cnodes + rnodes
        return result

    def move(self, where):
        if self.has_chess(where):
            return MOVE_STATE_FULL

        if self.gameover():
            return MOVE_STATE_WIN

        board = self.board.copy()
        turn = self.turn * -1

        board[where] = turn
        node = self.Node(
            board=board, turn=turn, where=where, parent=self,
            depth=self.depth, span=self.span, top=self.top)

        return node

    def next_move(self):
        nodes = self.detect_move(span=self.span, top=self.top)
        if not nodes:
            return MOVE_STATE_NONE
        for node in nodes:
            if node.gameover():
                return node
            value = node.evaluate()
            node.set_score(value)
        node = self.select(nodes)
        logger.debug(node)
        return node

    def select(self, nodes):
        if self.turn == CHESS_BLACK:
            node = max(nodes)
        else:
            node = min(nodes)
        return node

    def evaluate(self):
        return self.get_score()
