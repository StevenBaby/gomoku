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

        for var in nexts:
            if var.gameover():
                return var.get_score()
            var.set_score(
                var.minmax(depth - 1)
            )

        return self.select(nexts).get_score()

    def evaluate(self):
        return self.minmax(depth=self.depth)
