# coding=utf-8

import numpy as np
from numpy import mat
from numpy import zeros

import tone

logger = tone.utils.get_logger()


WIDTH = 19
HEIGHT = WIDTH

EMPTY = 0
BLACK = 1
WHITE = -1


class Node(object):

    def __init__(
            self,
            where=None,
            turn=None,
            parent=None,
            next_node=None,
            score=1):

        self.where = where
        self.turn = turn
        self.next_node = next_node
        self.parent = parent
        self.children = {}
        self.score = score

        if where:
            self.pos = (where[1], where[0])

    def train(self):
        self.score.summary()


class Score(object):

    params = [
        (-1, -1, 'upperleft'),
        (-1, 0, 'upper'),
        (-1, 1, 'upperright'),
        (0, -1, 'left'),
        (0, 1, 'right'),
        (1, -1, 'lowerleft'),
        (1, 0, 'lower'),
        (1, 1, 'lowerright'),
    ]

    weight = {
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

    def summary(self):
        scores = {
            "horizontal": self.left + self.right - 1,
            "vertical": self.left + self.right - 1,
            "principal": self.upperleft + self.lowerright - 1,
            "counter": self.lowerleft + self.upperright - 1,
        }

        scores = sorted(scores.items(), key=lambda e: e[1], reverse=True)

        result = 0
        for _, score in scores:
            if score > 5:
                score = 5
            result += self.weight[score]
        return result

    def __str__(self):
        return "{}-{}-{}-{}-{}-{}-{}-{}".format(
            self.upperleft,
            self.upper,
            self.upperright,
            self.left,
            self.right,
            self.lowerleft,
            self.lower,
            self.lowerright,
        )


class Gomoku(object):

    def __init__(self):
        self.reset()

    def has_chess(self, where):
        has = self.board[where] != 0
        return has

    def valid_where(self, where):
        if where[0] < 0 or where[1] < 0:
            return False
        if where[0] > WIDTH:
            return False
        if where[1] > HEIGHT:
            return False
        return True

    def get_score(self, where):
        turn = self.board[where]

        score = Score()

        for x, y, attr in score.params:
            for step in range(0, 5):
                key = (where[0] + step * x, where[1] + step * y)
                if not self.valid_where(key):
                    break
                if self.board[key] != turn:
                    break
                setattr(score, attr, getattr(score, attr) + 1)

        return score

    def move(self, where):
        if self.finished:
            return False

        self.board[where] = self.turn
        self.turn *= -1

        score = self.get_score(where)
        self.current = Node(
            where=where,
            turn=self.turn,
            parent=self.current,
            score=score)
        logger.debug('summary %s', score.summary())
        if score.summary() >= Score.MAX_SCORE:
            self.finished = True
        self.current.train()
        return True

    def reset(self):
        self.board = mat(zeros((WIDTH, HEIGHT)), dtype=int)
        self.turn = BLACK
        self.root = Node()
        self.current = self.root
        self.finished = False

    def undo(self):
        if self.current == self.root:
            return None
        node = self.current
        self.current = self.current.parent
        self.board[node.where] = EMPTY
        self.finished = False
        return node

    def test(self, where):
        pass
