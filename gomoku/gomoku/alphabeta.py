# coding=utf-8
import tone
from .node import Node

logger = tone.utils.get_logger()


class AlphaBetaNode(Node):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alpha = float('inf')
        self.beta = -float('inf')

    def get_score(self):
        if not self.score:
            return 0
        return self.score.score

    def move(self, where, reverse=True):
        node = super().move(where, reverse)
        node.alpha = -self.alpha
        node.beta = -self.beta
        return node

    def alphabeta(self, node, depth=2, span=2):
        if depth == 0 or node.is_finished():
            return node.get_score()
        score_nodes = node.detect_move(span=span)
        if not score_nodes:
            return node.get_score()

        parent = node
        best = node.get_score()
        counter = 3
        for score, nodes in score_nodes:
            counter -= 1
            if counter == 0:
                break
            for node in nodes:
                logger.debug(node)
                value = - self.alphabeta(node, depth=depth - 1, span=span)
                if value > parent.alpha:
                    parent.alpha = value
                if value >= parent.beta:
                    return parent.beta
        return parent.alpha

    def next_move(self, depth=2, span=1):
        if depth == 0:
            return None

        score_nodes = self.detect_move(span=span)
        if not score_nodes:
            return None

        result = None

        results = []

        counter = 2
        for score, nodes in score_nodes:
            counter -= 1
            if counter == 0:
                break
            for node in nodes:
                logger.debug(node)
                if node.is_finished():
                    return node
                node.set_score(self.alphabeta(node, depth=depth, span=span))
                results.append(node)

        results = sorted(results, key=lambda e: e.get_score(), reverse=True)
        return results[0]
