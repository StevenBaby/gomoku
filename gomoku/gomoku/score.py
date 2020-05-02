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
                'suffix': 0,
                'death': 0,
            },
            'right': {
                'step': (0, 1),
                'chess': 0,
                'empty': 0,
                'suffix': 0,
                'death': 0,
            },
        },
        'vertical': {
            'upper': {
                'step': (-1, 0),
                'chess': 0,
                'empty': 0,
                'suffix': 0,
                'death': 0,
            },
            'lower': {
                'step': (1, 0),
                'chess': 0,
                'empty': 0,
                'suffix': 0,
                'death': 0,
            },
        },
        'principal': {
            'upperleft': {
                'step': (-1, -1),
                'chess': 0,
                'empty': 0,
                'suffix': 0,
                'death': 0,
            },
            'lowerright': {
                'step': (1, 1),
                'chess': 0,
                'empty': 0,
                'suffix': 0,
                'death': 0,
            },
        },
        'counter': {
            'lowerleft': {
                'step': (1, -1),
                'chess': 0,
                'empty': 0,
                'suffix': 0,
                'death': 0,
            },
            'upperright': {
                'step': (-1, 1),
                'chess': 0,
                'empty': 0,
                'suffix': 0,
                'death': 0,
            },
        },
    }

    SCORE_LEVEL_0 = 0
    SCORE_LEVEL_1 = 1
    SCORE_LEVEL_2 = (2 * SCORE_LEVEL_1) + 1
    SCORE_LEVEL_3 = (2 * SCORE_LEVEL_2) + 1
    SCORE_LEVEL_4 = (2 * SCORE_LEVEL_3) + 1
    SCORE_LEVEL_5 = (2 * SCORE_LEVEL_4) + 1
    SCORE_LEVEL_6 = (2 * SCORE_LEVEL_5) + 1
    SCORE_LEVEL_7 = (2 * SCORE_LEVEL_6) + 1
    SCORE_LEVEL_8 = (2 * SCORE_LEVEL_7) + 1
    SCORE_LEVEL_9 = (2 * SCORE_LEVEL_8) + 1

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
            d = tone.utils.attrdict.attrdict()
            directions.append(d)
            d.chess = -1
            d.death = 0
            d.empty = 0
            d.suffix = 0
            d.score = 0

            for _, direct in total.items():
                if direct.suffix > d.suffix:
                    d.suffix = direct.suffix
                d.chess += direct.chess
                d.death += direct.death
                d.empty += direct.empty

            if d.chess >= 5:
                self.finished = True
                d.score = Score.SCORE_LEVEL_9
                continue

            if d.death == 2:
                d.score = Score.SCORE_LEVEL_0
                continue

            if d.chess == 4 and d.death == 0:
                d.score = Score.SCORE_LEVEL_8

            elif d.chess == 4 and d.death == 1:
                d.score = Score.SCORE_LEVEL_6

            elif d.chess == 3 and d.suffix >= 1:
                d.score = Score.SCORE_LEVEL_6

            elif d.chess == 2 and d.suffix >= 2:
                d.score = Score.SCORE_LEVEL_6

            elif d.chess == 1 and d.suffix >= 3:
                d.score = Score.SCORE_LEVEL_6

            elif d.chess == 3 and d.death == 0:
                d.score == Score.SCORE_LEVEL_5

            elif d.chess == 2 and d.suffix >= 1:
                d.score == Score.SCORE_LEVEL_5

            elif d.chess == 1 and d.suffix >= 2:
                d.score == Score.SCORE_LEVEL_5

            elif d.chess == 2 and d.death == 0:
                d.score = Score.SCORE_LEVEL_4

            elif d.chess == 1 and d.suffix >= 1:
                d.score == Score.SCORE_LEVEL_4

            elif d.chess == 1 and d.death == 0:
                d.score = Score.SCORE_LEVEL_3

            elif d.chess == 3 and d.death == 1:
                d.score = Score.SCORE_LEVEL_3

            elif d.chess == 2 and d.death == 1:
                d.score = Score.SCORE_LEVEL_2

            elif d.chess == 1 and d.death == 1:
                d.score = Score.SCORE_LEVEL_1

            if name in ('principal', "counter"):
                d.score += 1

        direct = sorted(directions, key=lambda e: e.score, reverse=True)
        self.score = direct[0].score + direct[1].score * 0.5

    def collect(self):
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
                        direct.death += 1
                        break
                    chess = board[move]
                    if chess == turn and direct.empty == 1:
                        direct.suffix += 1
                        continue
                    if chess == turn and direct.empty == 0:
                        direct.chess += 1
                        continue
                    if chess == CHESS_EMPTY and direct.empty < 2:
                        direct.empty += 1
                        continue
                    if chess != turn and direct.empty == 0:
                        direct.death += 1
                        break

    def compute(self):
        self.collect()
        self.make()
