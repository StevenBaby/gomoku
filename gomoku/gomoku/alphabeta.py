# coding=utf-8

import tone
from .node import Node
from . import functions
from . import MOVE_STATE_NONE
from . import CHESS_WHITE

logger = tone.utils.get_logger()


class AlphaBetaNode(Node):

    def alphabeta(self, node, alpha, beta, depth):
        if depth == 0 or node.gameover():
            return node.get_score()

        nexts = node.detect_move(span=self.span, top=self.top)
        for next in nexts:
            if next.gameover():
                return - next.get_score()

            value = self.alphabeta(next, alpha, beta, depth - 1)
            # logger.debug('node %s depth %s value %s', next, depth, value)

            if node.turn == CHESS_WHITE:
                beta = min(beta, value)
            else:
                alpha = max(alpha, value)
            if beta <= alpha:
                logger.debug("pruned depth %s", depth)
                break

        if node.turn == CHESS_WHITE:
            return beta
        else:
            return alpha

    def evaluate(self, node):
        alpha = float("inf")
        if node.turn == CHESS_WHITE:
            alpha = -float('inf')
        beta = -alpha

        return self.alphabeta(
            node=node,
            alpha=alpha,
            beta=beta,
            depth=self.depth)
