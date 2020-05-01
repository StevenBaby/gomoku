# coding=utf-8

import tone

from .node import Node
from . import MOVE_STATE_FULL
from . import MOVE_STATE_WIN
from . import MOVE_STATE_NONE


logger = tone.utils.get_logger()


class Game(object):

    def __init__(self):
        self.reset()

    def move(self, where=None, depth=2, span=3):
        if self.head.is_finished():
            return MOVE_STATE_WIN

        if where:
            node = self.head.move(where)
        else:
            node = self.head.next_move(depth=depth, span=span)
        if not isinstance(node, Node):
            return node

        logger.debug("{} - {}".format(node.score.score, node.score.finished))

        self.head = node
        if self.head.is_finished():
            return MOVE_STATE_WIN
        return MOVE_STATE_NONE

    def reset(self):
        self.root = Node()
        self.head = self.root

    def undo(self):
        if self.head == self.root:
            return None
        self.head = self.head.parent

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
