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

        nexts = self.detect_move(span=self.span, top=self.top)
        if not nexts:
            return self.get_score()

        if self.turn == MIN:
            current = -float("inf")
        else:
            current = float('inf')

        for var in nexts:
            value = var.minmax(depth - 1)
            if var.turn == MAX and value > current:
                current = value
            elif var.turn == MIN and value < current:
                current = value
        return current

    def evaluate(self):
        return self.minmax(depth=self.depth)
