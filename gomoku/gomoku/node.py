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
        self.children = []

    def summary(self):
        score = self.score.get_score() * self.turn
        loss = self.loss
        return score if abs(score) > abs(loss) else loss

    def is_finished(self):
        if not self.score:
            return False
        return self.score.get_score() >= Score.MAX_SCORE

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
        if node.turn == CHESS_BLACK and next:
            next_node = node.get_next_move()

        return next_node or node

    def get_search_keys(self, span=2):
        wheres = functions.get_wheres()
        result = {}
        for where in wheres.keys():
            if self.board[where] == CHESS_EMPTY:
                result[where] = True
        return result

    def get_next_move(self, depth=DEPTH_DEFAULT, span=5):
        if depth < 0:
            return None

        nodes = []
        keys = self.get_search_keys(span=span)
        for key in keys:
            node = self.move(key, next=False)
            if not isinstance(node, Node):
                continue
            logger.debug("depth %s summary %s where %s", depth, node.summary(), key)
            nodes.append(node)

        self.turn *= -1

        for key in keys:
            node = self.move(key, next=False)
            if not isinstance(node, Node):
                continue
            logger.debug("depth %s summary %s where %s", depth, node.summary(), key)
            nodes.append(node)

        self.turn *= -1

        if not nodes:
            return None

        scores = {}
        for node in nodes:
            summary = node.summary()
            where = node.where
            scores.setdefault(where, 0)
            scores[where] += summary
            # scores.setdefault(summary, [])
            # scores[summary].append(node)

        items = sorted(scores.items(), key=lambda e: e[1], reverse=True)
        where = items[0][0]
        node = self.move(where, next=False)
        return node

    def __str__(self):
        chess = 'black'
        if self.turn == CHESS_WHITE:
            chess = 'white'
        return f"Node [{self.where}] - {chess} - {self.summary()}"

    def __repr__(self):
        return self.__str__()
