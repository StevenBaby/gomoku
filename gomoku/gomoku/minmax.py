# coding=utf-8

import tone
from .node import Node
from . import functions
from . import MOVE_STATE_NONE
from . import CHESS_WHITE

logger = tone.utils.get_logger()


class MinMaxNode(Node):

    def minmax(self, node, depth, span, top):
        logger.debug('node %s depth %s minmax %s', node, depth, type)
        if depth == 0 or top == 0 or node.is_finished():
            return node.get_score()

        nexts = node.detect_move(span=span, top=top)
        for var in nexts:
            var.set_score(
                self.minmax(var, depth - 1, span, top)
            )

        if node.turn == CHESS_WHITE:
            return min(nexts).get_score()
        else:
            return max(nexts).get_score()

    def evaluate(self, node):
        return self.minmax(
            node=node,
            depth=self.depth,
            span=self.span,
            top=self.top)
