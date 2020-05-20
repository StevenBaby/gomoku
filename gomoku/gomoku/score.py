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

    GAP = 2.1
    LEVEL_0 = 0
    LEVEL_1 = 1
    LEVEL_2 = (GAP * LEVEL_1)
    LEVEL_3 = (GAP * LEVEL_2)
    LEVEL_4 = (GAP * LEVEL_3)
    LEVEL_5 = (GAP * LEVEL_4)
    LEVEL_6 = (GAP * LEVEL_5)
    LEVEL_7 = (GAP * LEVEL_6)
    LEVEL_8 = (GAP * LEVEL_7)
    LEVEL_9 = (GAP * LEVEL_8)
    LEVEL_10 = (GAP * LEVEL_9)

    def __init__(self, board, where):
        self.board = board
        self.where = where
        self.cvalue = tone.utils.attrdict.attrdict.loads(self.PARAMS)
        self.rvalue = tone.utils.attrdict.attrdict.loads(self.PARAMS)
        self.finished = False
        self.cscore = 0
        self.rscore = 0
        self.score = 0
        self.compute()

    def make(self, value):
        directions = []

        for name, total in value.items():
            d = tone.utils.attrdict.attrdict()
            directions.append(d)
            d.name = name[0]
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
                d.score = Score.LEVEL_10
                continue

            if d.death == 2:
                d.score = Score.LEVEL_0
                continue

            if d.chess == 4 and d.death == 0:
                d.score = Score.LEVEL_9

            elif d.chess == 4 and d.death == 1:
                d.score = Score.LEVEL_8 + 1

            elif d.chess == 3 and d.suffix >= 1:
                d.score = Score.LEVEL_8

            elif d.chess == 2 and d.suffix >= 2:
                d.score = Score.LEVEL_8

            elif d.chess == 1 and d.suffix >= 3:
                d.score = Score.LEVEL_8

            elif d.chess == 3 and d.death == 0:
                d.score = Score.LEVEL_7 + 1

            elif d.chess == 2 and d.suffix >= 1:
                d.score = Score.LEVEL_7

            elif d.chess == 1 and d.suffix >= 2:
                d.score = Score.LEVEL_7

            elif d.chess == 2 and d.death == 0:
                d.score = Score.LEVEL_6

            elif d.chess == 1 and d.suffix >= 1:
                d.score = Score.LEVEL_6

            elif d.chess == 3 and d.death == 1:
                d.score = Score.LEVEL_5

            elif d.chess == 2 and d.death == 1:
                d.score = Score.LEVEL_4

            elif d.chess == 1 and d.death == 0:
                d.score = Score.LEVEL_4

            elif d.chess == 1 and d.death == 1:
                d.score = Score.LEVEL_3

            if d.score == 0:
                raise Exception('score not define %s' % d)
                logger.error('error %s', d)

            if d.empty:
                d.score += 1
            # if name in ('principal', "counter"):
            #     d.score += 1

        direct = sorted(directions, key=lambda e: e.score, reverse=True)
        return direct

    def collect(self, value, reverse=False):
        board = self.board
        where = self.where
        turn = board[where]

        if reverse:
            turn *= -1

        for total_name in Score.PARAMS:
            total = value[total_name]
            for direct_name in Score.PARAMS[total_name]:
                direct = total[direct_name]
                x, y = direct.step

                for step in range(0, 5):
                    move = (where[0] + step * x, where[1] + step * y)
                    if not functions.is_valid_where(move):
                        direct.death += 1
                        break
                    chess = board[move]
                    if reverse and move == self.where:
                        chess *= -1
                    if chess == turn and direct.empty == 1:
                        direct.suffix += 1
                        continue
                    if chess == turn and direct.empty == 0:
                        direct.chess += 1
                        continue
                    if chess == CHESS_EMPTY and direct.empty < 2 and direct.suffix == 0:
                        direct.empty += 1
                        continue
                    if chess != turn and direct.empty == 0:
                        direct.death += 1
                        break
                    if chess != turn and direct.empty == 1:
                        break

    def compute(self):
        self.collect(self.cvalue, reverse=False)
        direct = self.make(self.cvalue)
        self.cscore = 0
        # percent = 0.99
        # for index, d in enumerate(direct):
        #     self.cscore += d.score * (percent ** index)
        self.cscore = sum([direct[0].score, direct[1].score])
        if [var for var in direct if var.chess >= 5]:
            self.finished = True

        self.collect(self.rvalue, reverse=True)
        direct = self.make(self.rvalue)
        # for index, d in enumerate(direct):
        #     self.rscore += d.score * (percent ** index)
        self.rscore = sum([direct[0].score, direct[1].score])

        # self.score = max(self.cscore, self.rscore - 1)
        self.score = self.cscore + self.rscore
