# coding=utf-8
import tone

from . import CHESS_EMPTY
from . import functions


logger = tone.utils.get_logger()


class Score(object):

    PARAMS = {
        'horizontal': {
            'left': {
                'step': (0, -1),
                'chess': 0,
                'empty': 0,
            },
            'right': {
                'step': (0, 1),
                'chess': 0,
                'empty': 0,
            },
        },
        'vertical': {
            'upper': {
                'step': (-1, 0),
                'chess': 0,
                'empty': 0,
            },
            'lower': {
                'step': (1, 0),
                'chess': 0,
                'empty': 0,
            },
        },
        'principal': {
            'upperleft': {
                'step': (-1, -1),
                'chess': 0,
                'empty': 0,
            },
            'lowerright': {
                'step': (1, 1),
                'chess': 0,
                'empty': 0,
            },
        },
        'counter': {
            'lowerleft': {
                'step': (1, -1),
                'chess': 0,
                'empty': 0,
            },
            'upperright': {
                'step': (-1, 1),
                'chess': 0,
                'empty': 0,
            },
        },
    }

    # WEIGHT = {
    #     1: 1,
    #     2: 10,
    #     3: 100,
    #     4: 1000,
    #     5: 10000,
    # }

    MAX_SCORE = 10000

    def __init__(self, board, where):
        self.board = board
        self.where = where
        self.value = tone.utils.attrdict.attrdict.loads(self.PARAMS)
        self.compute()

    def get_score(self):
        if hasattr(self, 'summary'):
            return self.summary

        summary = 0
        for _, total in self.value.items():
            for _, direct in total.items():
                summary += direct.chess * 5
                summary += direct.empty * 1
        self.summary = summary
        return summary

    def compute(self):
        board = self.board
        where = self.where
        turn = board[where]

        for total_name in Score.PARAMS:
            total = self.value[total_name]
            for direct_name in Score.PARAMS[total_name]:
                direct = total[direct_name]
                x, y = direct.step

                for step in range(0, 5):
                    move = (where[0] + step * x, where[1] + step * y)
                    if not functions.is_valid_where(move):
                        break
                    chess = board[move]
                    if chess == turn:
                        direct.chess += 1
                        continue
                    elif chess == CHESS_EMPTY:
                        direct.empty += 1
                        continue
                    else:
                        break

    def __str__(self):
        return str(self.get_score())
