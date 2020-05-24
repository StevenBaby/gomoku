# coding=utf-8

import tone
from .node import Node
from . import functions
from . import MOVE_STATE_NONE

logger = tone.utils.get_logger()


class AlphaBetaNode(Node):

    def alphabeta(self, node, alpha, beta, depth, span, top):
        if depth == 0 or top == 0 or node.is_finished():
            return node.get_score()
        nexts = node.detect_move(span=span, top=top)
        for next in nexts:
            if next.is_finished():
                return - next.get_score()
            value = - self.alphabeta(next, -beta, -alpha, depth - 1, span, top)
            logger.debug('node %s depth %s value %s', next, depth, value)
            if value > alpha:
                alpha = value
            if value >= beta:
                return beta
        return alpha

    def next_move(self):
        nodes = self.detect_move(span=self.span, top=self.top)
        if not nodes:
            return MOVE_STATE_NONE
        for node in nodes:
            if node.is_finished():
                return node
            node.set_score(self.alphabeta(
                node=node,
                alpha=-float('inf'),
                beta=float('inf'),
                depth=self.depth,
                span=self.span,
                top=self.top
            ))

        results = sorted(nodes, key=lambda e: e.get_score(), reverse=True)
        node = results[0]
        return node
