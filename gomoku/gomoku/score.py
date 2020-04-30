# coding=utf-8

from . import CHESS_EMPTY
from . import functions


class Score(object):

    STEP = [
        (-1, -1, 'upperleft'),
        (-1, 0, 'upper'),
        (-1, 1, 'upperright'),
        (0, -1, 'left'),
        (0, 1, 'right'),
        (1, -1, 'lowerleft'),
        (1, 0, 'lower'),
        (1, 1, 'lowerright'),
    ]

    WEIGHT = {
        1: 1,
        2: 10,
        3: 100,
        4: 1000,
        5: 10000,
    }

    MAX_SCORE = 10000

    def __init__(self):
        self.upperleft = 0
        self.upper = 0
        self.upperright = 0
        self.left = 0
        self.right = 0
        self.lowerleft = 0
        self.lower = 0
        self.lowerright = 0

    def get_score(self):
        scores = {
            "horizontal": self.left + self.right - 1,
            "vertical": self.upper + self.lower - 1,
            "principal": self.upperleft + self.lowerright - 1,
            "counter": self.lowerleft + self.upperright - 1,
        }

        summary = 0
        for _, score in scores.items():
            if score > 5:
                score = 5
            summary += self.WEIGHT[score]
        return summary

    @classmethod
    def collect_score(cls, board, where):
        turn = board[where]

        score = Score()

        for x, y, attr in Score.STEP:
            for step in range(0, 5):
                key = (where[0] + step * x, where[1] + step * y)
                if not functions.is_valid_where(key):
                    break
                if board[key] == turn:
                    setattr(score, attr, getattr(score, attr) + 1)
                elif board[key] == CHESS_EMPTY:
                    # setattr(score, attr, getattr(score, attr) + 1)
                    break
                else:
                    break
        return score

    def __str__(self):
        return str(self.get_score())
