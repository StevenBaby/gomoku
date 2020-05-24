# coding=utf-8

import tone
from .node import Node
from . import functions

logger = tone.utils.get_logger()


class MinMaxNode(Node):

    def minmax(self, node, depth):
        if depth == 0 or node.is_finished():
            return node.get_score()

        nexts = node.detect_move(span=self.span, top=self.top)
        if not nexts:
            return node.get_score()

        for var in nexts:
            var.set_score(
                self.minmax(var, depth - 1)
            )
        return node.select_node(nexts).get_score()

    def evaluate(self, node):
        return self.minmax(node=node, depth=self.depth)
