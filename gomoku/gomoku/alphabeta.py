# coding=utf-8

import tone
from .node import Node
from . import functions
from . import MOVE_STATE_NONE
from .minmax import MIN, MAX

logger = tone.utils.get_logger()


class AlphaBetaNode(Node):

    def alphabeta(self, alpha, beta, depth):
        if depth == 0 or self.gameover():
            return self.get_score()

        nexts = self.detect_move(span=self.span, top=self.top)
        if not nexts:
            return self.get_score()

        for var in nexts:
            if var.gameover():
                return var.get_score()

            value = var.alphabeta(alpha, beta, depth - 1)
            if self.turn == MIN:
                alpha = max(alpha, value)
            else:
                beta = min(beta, value)

            if beta <= alpha:
                # logger.debug('pruning')
                break

        if self.turn == MIN:
            return alpha
        else:
            return beta

    def evaluate(self):
        alpha = -float("inf")
        beta = float("inf")

        return self.alphabeta(
            alpha=alpha,
            beta=beta,
            depth=self.depth)
