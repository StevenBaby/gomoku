# coding=utf-8

import tone
from .node import Node
from . import functions
from . import CHESS_BLACK
from . import CHESS_WHITE

logger = tone.utils.get_logger()

MIN = CHESS_BLACK
MAX = CHESS_WHITE


class MinMaxNode(Node):

    def minmax(self, depth):
        if depth == 0 or self.gameover():
            return self.get_score()

        children = self.detect_move(span=self.span, top=self.top)
        if not children:
            return self.get_score()

        current = self.get_score()

        for var in children:
            value = var.minmax(depth - 1)
            if self.turn == MIN:
                current = max(value, current)
            else:
                current = min(value, current)
        return current

    def evaluate(self):
        value = self.minmax(depth=self.depth)
        return value
