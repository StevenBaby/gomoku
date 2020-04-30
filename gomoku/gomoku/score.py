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
                'death': 0,
            },
            'right': {
                'step': (0, 1),
                'chess': 0,
                'empty': 0,
                'death': 0,
            },
        },
        'vertical': {
            'upper': {
                'step': (-1, 0),
                'chess': 0,
                'empty': 0,
                'death': 0,
            },
            'lower': {
                'step': (1, 0),
                'chess': 0,
                'empty': 0,
                'death': 0,
            },
        },
        'principal': {
            'upperleft': {
                'step': (-1, -1),
                'chess': 0,
                'empty': 0,
                'death': 0,
            },
            'lowerright': {
                'step': (1, 1),
                'chess': 0,
                'empty': 0,
                'death': 0,
            },
        },
        'counter': {
            'lowerleft': {
                'step': (1, -1),
                'chess': 0,
                'empty': 0,
                'death': 0,
            },
            'upperright': {
                'step': (-1, 1),
                'chess': 0,
                'empty': 0,
                'death': 0,
            },
        },
    }

    def __init__(self, board, where):
        self.board = board
        self.where = where
        self.value = tone.utils.attrdict.attrdict.loads(self.PARAMS)
        self.finished = False
        self.score = 0
        self.compute()

    def make(self):
        directions = []

        for name, total in self.value.items():
            direction = tone.utils.attrdict.attrdict()
            directions.append(direction)
            direction.chess = -1
            direction.death = 0
            direction.empty = 0
            direction.score = 0
            for _, direct in total.items():
                direction.chess += direct.chess
                direction.death += direct.death
                direction.empty += direct.empty

            if direction.chess >= 5:
                self.finished = True
                direction.score = 100
                continue

            if name in ('principal', "counter"):
                direction.score += 2
            direction.score += direction.chess * 3
            direction.score += direction.empty * 1
            direction.score -= direction.death * 5
            if direction.death == 2:
                direction.score = 0

        direct = sorted(directions, key=lambda e: e.score, reverse=True)
        for var in range(4):
            self.score += direct[var].score * (0.3 ** var)

    def collect(self):
        board = self.board
        where = self.where
        turn = board[where]

        for total_name in Score.PARAMS:
            total = self.value[total_name]
            for direct_name in Score.PARAMS[total_name]:
                direct = total[direct_name]
                x, y = direct.step

                empty = 0
                for step in range(0, 5):
                    move = (where[0] + step * x, where[1] + step * y)
                    if not functions.is_valid_where(move):
                        direct.death += 1
                        break
                    chess = board[move]
                    if chess == turn:
                        direct.chess += 1
                        continue
                    elif chess == CHESS_EMPTY and empty < 2:
                        empty += 1
                        direct.empty += 1
                        break
                    else:
                        direct.death += 1
                        break

    def compute(self):
        self.collect()
        self.make()
