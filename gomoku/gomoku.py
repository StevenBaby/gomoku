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

    def train(self):
        pass


class Gomoku(object):

    def __init__(self):
        self.reset()

    def has_chess(self, where):
        has = self.board[(where[1], where[0])] != 0
        return has

    def get_score(self, where):
        pass

    def move(self, where):
        self.board[(where[1], where[0])] = self.turn
        self.turn *= -1

        score = self.get_score(where)
        self.current = Node(
            where=where,
            turn=self.turn,
            parent=self.current,
            score=score)

    def reset(self):
        self.board = mat(zeros((WIDTH, HEIGHT)), dtype=int)
        self.turn = BLACK
        self.root = Node()
        self.current = self.root

    def undo(self):
        if self.current == self.root:
            return None
        node = self.current
        self.current = self.current.parent
        self.board[(node.where[1], node.where[0])] = EMPTY
        return node

    def test(self, where):
        pass
