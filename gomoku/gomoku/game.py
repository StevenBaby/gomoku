# coding=utf-8

import tone

from .node import Node

from . import MOVE_STATE_FULL
from . import MOVE_STATE_WIN
from . import MOVE_STATE_NONE
from . import CHESS_BLACK
from . import CHESS_WHITE
from . import DEPTH_DEFAULT
from . import SPAN_DEFAULT
from . import TOP_DEFAULT

logger = tone.utils.get_logger()


class Game(object):

    def __init__(self):
        self.root = None
        self.reset()

    def move(self, where=None):
        if self.head.gameover():
            return MOVE_STATE_WIN

        if where:
            node = self.head.move(where)
        else:
            node = self.head.next_move()
        if not isinstance(node, Node):
            return node

        self.head = node
        if self.head.gameover():
            return MOVE_STATE_WIN

    def reset(self):
        from .minmax import MinMaxNode as Node
        # from .alphabeta import AlphaBetaNode as Node

        self.depth = DEPTH_DEFAULT
        self.span = SPAN_DEFAULT
        self.top = TOP_DEFAULT
        self.root = Node(
            depth=self.depth,
            span=self.span,
            top=self.top)

        self.head = self.root

    def undo(self):
        if self.head == self.root:
            return None
        if self.head.parent:
            self.head = self.head.parent
        if self.head.parent:
            self.head = self.head.parent

    def save(self, filename):
        from . import functions
        functions.save_pickle(self, filename)

    def load(self, filename):
        from . import functions
        model = functions.load_pickle(filename)
        if not isinstance(model, Game):
            return False

        self.root = model.root
        self.head = model.head

        return True
