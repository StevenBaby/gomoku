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

        nodes = self.detect_move(span=self.span, top=self.top)

        scores = [node.minmax(depth - 1) for node in nodes]

        if self.turn == MIN:
            value = max(scores)
        else:
            value = min(scores)
        return value

    def evaluate(self):
        return self.minmax(depth=self.depth)
