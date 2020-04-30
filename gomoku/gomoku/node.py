# coding=utf-8
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

        next_node = None
        if next:
            next_node = node.get_next_move()

        return next_node or node

    def get_next_move(self):
        nodes = []
        wheres = functions.get_search_wheres(self.board, span=3)
        for where in wheres:
            node = self.move(where, next=False)
            if not isinstance(node, Node):
                continue
            if node.is_finished():
                return node
            nodes.append(node)

        self.turn *= -1
        for where in wheres:
            node = self.move(where, next=False)
            if not isinstance(node, Node):
                continue
            if node.is_finished():
                self.turn *= -1
                return self.move(where, next=False)
            node.score.score += 1
            nodes.append(node)
        self.turn *= -1

        if not nodes:
            return None

        scores = {}
        for node in nodes:
            scores.setdefault(node.score.score, [])
            scores[node.score.score].append(node)

        nodes = sorted(scores.items(), key=lambda e: e[0], reverse=True)
        node = random.choice(nodes[0][1])
        if node.turn == (self.turn * -1):
            return node
        else:
            return self.move(node.where, next=False)
