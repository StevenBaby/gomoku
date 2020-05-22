# coding=utf-8
import multiprocessing

import tone
from .node import Node
from . import functions

logger = tone.utils.get_logger()


class AlphaBetaNode(Node):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alpha = - float('inf')
        self.beta = - self.alpha

    def move(self, where):
        node = super().move(where)
        node.alpha = -self.alpha
        node.beta = -self.beta
        return node

    def detect_move(self, span=2, top=5):
        nodes = []
        wheres = functions.get_search_wheres(self.board, span=span)
        for where in wheres:
            node = self.move(where)
            if not isinstance(node, Node):
                continue
            nodes.append(node)

        nodes = sorted(nodes, key=lambda e: e.get_score(), reverse=True)[:top]
        return nodes

    def alphabeta(self, node, depth=2, span=2, top=5):
        if depth == 0 or top == 0 or node.is_finished():
            return node.get_score()
        wheres = functions.get_search_wheres(node.board, span=span)
        nexts = self.detect_move(span=span, top=top)
        for next in nexts:
            if next.is_finished():
                return - next.get_score()
            # logger.debug('node %s depth %s', next, depth)
            value = - self.alphabeta(next, depth=depth - 1, span=span, top=top - 1)
            if value > node.alpha:
                node.alpha = value
            if value >= node.beta:
                return node.beta
        return node.alpha

    def compute(self, node, queue=None):
        score = self.alphabeta(node, self.depth, self.span, self.top)
        logger.debug(score)
        node.set_score(score)
        queue.put(node)

    def next_move_process(self):
        processes = []
        nodes = self.detect_move(span=self.span, top=self.top)
        for node in nodes:
            if node.is_finished():
                return node
            queue = multiprocessing.Queue()
            process = multiprocessing.Process(
                target=self.compute,
                args=(node, queue),
            )
            process.node = node
            process.queue = queue
            processes.append(process)
            logger.debug('setup process')

        for process in processes:
            process.daemon = True
            process.start()
            logger.debug('start process')

        results = []

        for process in processes:
            results.append(process.queue.get())
            process.join()
            logger.debug('join process')

        results = sorted(results, key=lambda e: e.get_score(), reverse=True)
        return results[0]

    def next_move_sync(self):
        if depth == 0:
            return None

        nodes = self.detect_move(span=self.span, top=self.top)
        for node in nodes:
            if node.is_finished():
                return node
            node.set_score(self.alphabeta(
                node=node,
                depth=self.depth,
                span=self.span,
                top=self.top
            ))

        results = sorted(nodes, key=lambda e: e.get_score(), reverse=True)
        return results[0]

    def next_move(self):
        return self.next_move_process()
