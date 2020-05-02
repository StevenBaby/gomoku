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

    def set_score(self, score):
        if not self.score:
            return
        self.score.score = score

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
        if not reverse:
            node.turn *= -1
            board[where] = node.turn
            node.score.finished = False

        return node

    def detect_move(self, span=2):
        nodes = {}
        wheres = functions.get_search_wheres(self.board, span=span)
        for where in wheres:
            node = self.move(where)
            if not isinstance(node, Node):
                continue

            nodes.setdefault(node.get_score(), [])
            nodes[node.get_score()].append(node)
            if node.is_finished():
                break

            node = self.move(where, reverse=False)
            if not isinstance(node, Node):
                continue

            node.set_score(node.get_score() / 2 + 1)
            nodes.setdefault(node.get_score(), [])
            nodes[node.get_score()].append(node)
            if node.is_finished():
                break
        nodes = sorted(nodes.items(), key=lambda e: e[0], reverse=True)
        return nodes

    def next_move(self, depth=2, span=2):
        if depth == 0:
            return None

        score_nodes = self.detect_move(span=span)
        if not score_nodes:
            return None

        result_nodes = []
        max_detect_node = 5
        for score, nodes in score_nodes:
            if max_detect_node == 0:
                break
            for node in nodes:
                logger.debug(node)
                if max_detect_node == 0:
                    break
                if node.is_finished():
                    return node
                next_node = node.next_move(depth=depth - 1, span=span)
                if not next_node:
                    result_nodes.append(node)
                    max_detect_node -= 1
                    continue

                if next_node.get_score() > node.get_score():
                    node.set_score(-next_node.get_score())
                result_nodes.append(node)
                max_detect_node -= 1

        nodes = sorted(result_nodes, key=lambda e: e.get_score(), reverse=True)
        return nodes[0]
        # node_list = nodes[0][1]

        # node = random.choice(node_list)
        # if node.turn == self.turn:
        #     return self.move(node.where)
        # else:
        #     return node
