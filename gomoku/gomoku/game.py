# coding=utf-8

import tone

from .node import Node
from .alphabeta import AlphaBetaNode

from . import MOVE_STATE_FULL
from . import MOVE_STATE_WIN
from . import MOVE_STATE_NONE
from . import CHESS_BLACK
from . import CHESS_WHITE


logger = tone.utils.get_logger()


class Game(object):

    def __init__(self):
        self.reset()

    def move(self, where=None):
        if self.head.is_finished():
            return MOVE_STATE_WIN

        if where:
            node = self.head.move(where)
        else:
            node = self.head.next_move()
        if not isinstance(node, Node):
            return node

        logger.debug("{:0.2f} - {}".format(node.score.score, node.score.finished))

        self.head = node
        if self.head.is_finished():
            return MOVE_STATE_WIN
        return MOVE_STATE_NONE

    def reset(self):
        self.depth = 3
        self.span = 2
        self.top = 5
        self.root = AlphaBetaNode()
        self.head = self.root

    def undo(self):
        if self.head == self.root:
            return None
        if self.head.turn == CHESS_BLACK:
            self.head = self.head.parent
        else:
            self.head = self.head.parent.parent

    def save(self, filename):
        import pickle
        with open(filename, 'wb') as file:
            pickle.dump(self, file)

    def load(self, filename):
        import pickle
        try:
            with open(filename, 'rb') as file:
                model = pickle.load(file)
        except Exception:
            return False
        if not isinstance(model, Game):
            return False

        self.root = model.root
        self.head = model.head

        return True
