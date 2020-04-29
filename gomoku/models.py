# coding=utf-8
import random

import numpy as np
from numpy import mat
from numpy import zeros

import tone
import functions

BOARD_WIDTH = 19
BOARD_HEIGHT = BOARD_WIDTH


CHESS_EMPTY = 0
CHESS_BLACK = 1
CHESS_WHITE = -1

MOVE_STATE_NONE = 0
MOVE_STATE_FULL = 1
MOVE_STATE_WIN = 2

DEPTH_DEFAULT = 2

logger = tone.utils.get_logger()


class Score(object):

    STEP = [
        (-1, -1, 'upperleft'),
        (-1, 0, 'upper'),
        (-1, 1, 'upperright'),
        (0, -1, 'left'),
        (0, 1, 'right'),
        (1, -1, 'lowerleft'),
        (1, 0, 'lower'),
        (1, 1, 'lowerright'),
    ]

    WEIGHT = {
        1: 1,
        2: 10,
        3: 100,
        4: 1000,
        5: 10000,
    }

    MAX_SCORE = 10000

    def __init__(self):
        self.upperleft = 0
        self.upper = 0
        self.upperright = 0
        self.left = 0
        self.right = 0
        self.lowerleft = 0
        self.lower = 0
        self.lowerright = 0

    def get_score(self):
        scores = {
            "horizontal": self.left + self.right - 1,
            "vertical": self.upper + self.lower - 1,
            "principal": self.upperleft + self.lowerright - 1,
            "counter": self.lowerleft + self.upperright - 1,
        }

        summary = 0
        for _, score in scores.items():
            if score > 5:
                score = 5
            summary += self.WEIGHT[score]
        return summary

    @classmethod
    def collect_score(cls, board, where):
        turn = board[where]

        score = Score()

        for x, y, attr in Score.STEP:
            for step in range(0, 5):
                key = (where[0] + step * x, where[1] + step * y)
                if not functions.is_valid_where(key):
                    break
                if board[key] != turn:
                    break
                setattr(score, attr, getattr(score, attr) + 1)
        return score

    def __str__(self):
        return str(self.get_score())


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
            self.score = Score.collect_score(self.board, self.where)
        else:
            self.score = None

        if parent:
            self.parent = parent
            parent.next = self
        else:
            self.parent = None

        self.loss = 0

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

    def move(self, where, depth=DEPTH_DEFAULT):
        if depth < 0:
            return MOVE_STATE_NONE

        if self.has_chess(where):
            return MOVE_STATE_FULL

        if self.is_finished():
            return MOVE_STATE_WIN

        board = self.board.copy()
        turn = self.turn * -1
        board[where] = turn
        node = Node(board=board, turn=turn, where=where, parent=self)

        next_node = None
        if node.turn == CHESS_BLACK:
            next_node = node.get_next_move(depth=depth)

        return next_node or node

    def get_next_move(self, depth=DEPTH_DEFAULT, span=2):
        if depth < 0:
            return None

        where = self.where

        nodes = []

        for x, y, attr in Score.STEP:
            for step in range(0, span):
                key = (where[0] + step * x, where[1] + step * y)
                if not functions.is_valid_where(key):
                    break

                node = self.move(key, depth=depth - 1)
                if not isinstance(node, Node):
                    continue
                logger.debug("get node depth %s summary %s where %s", depth, node.summary(), key)
                nodes.append(node)

        if not nodes:
            return None

        for node in nodes:
            next_node = node.get_next_move(depth=depth - 1)
            if not isinstance(next_node, Node):
                continue

            node.loss = next_node.summary() * -1

        scores = {}
        for node in nodes:
            summary = node.summary()
            scores.setdefault(summary, [])
            scores[summary].append(node)

        if self.turn > 0:
            items = sorted(scores.items(), key=lambda e: e[0], reverse=False)
        else:
            items = sorted(scores.items(), key=lambda e: e[0], reverse=True)
        node = random.choice(items[0][1])
        return node

    def __str__(self):
        chess = 'black'
        if self.turn == CHESS_WHITE:
            chess = 'white'
        return f"Node [{self.where}] - {chess} - {self.summary()}"

    def __repr__(self):
        return self.__str__()
