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
        self.turn = CHESS_WHITE
        self.score = None
        self.parent = None

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
            parent.next = self

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

    def move(self, where, reverse=True):
        if self.has_chess(where):
            return MOVE_STATE_FULL

        if self.is_finished():
            return MOVE_STATE_WIN

        board = self.board.copy()
        if reverse:
            turn = self.turn * -1
        else:
            turn = self.turn
        board[where] = turn
        node = Node(board=board, turn=turn, where=where, parent=self)
        return node

    def detect_move(self, span=3):
        nodes = {}
        wheres = functions.get_search_wheres(self.board, span=span)
        for where in wheres:
            node = self.move(where)
            if not isinstance(node, Node):
                continue

            nodes.setdefault(node.get_score(), [])
            nodes[node.get_score()].append(node)
            if node.is_finished():
                return nodes

            node = self.move(where, reverse=False)
            if not isinstance(node, Node):
                continue

            nodes.setdefault(node.get_score(), [])
            nodes[node.get_score()].append(node)
            if node.is_finished():
                return nodes

        return nodes

    def next_move(self, depth=2, span=3):
        if depth == 0:
            return None

        nodes = self.detect_move(span=span)
        if not nodes:
            return None

        nodes = sorted(nodes.items(), key=lambda e: e[0], reverse=True)
        node_list = nodes[0][1]

        node = random.choice(node_list)
        if node.turn == self.turn:
            return self.move(node.where)
        else:
            return node
