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
                'block': 0,
            },
            'right': {
                'step': (0, 1),
                'chess': 0,
                'empty': 0,
                'suffix': 0,
                'death': 0,
                'block': 0,
            },
        },
        'vertical': {
            'upper': {
                'step': (-1, 0),
                'chess': 0,
                'empty': 0,
                'suffix': 0,
                'death': 0,
                'block': 0,
            },
            'lower': {
                'step': (1, 0),
                'chess': 0,
                'empty': 0,
                'suffix': 0,
                'death': 0,
                'block': 0,
            },
        },
        'principal': {
            'upperleft': {
                'step': (-1, -1),
                'chess': 0,
                'empty': 0,
                'suffix': 0,
                'death': 0,
                'block': 0,
            },
            'lowerright': {
                'step': (1, 1),
                'chess': 0,
                'empty': 0,
                'suffix': 0,
                'death': 0,
                'block': 0,
            },
        },
        'counter': {
            'lowerleft': {
                'step': (1, -1),
                'chess': 0,
                'empty': 0,
                'suffix': 0,
                'death': 0,
                'block': 0,
            },
            'upperright': {
                'step': (-1, 1),
                'chess': 0,
                'empty': 0,
                'suffix': 0,
                'death': 0,
                'block': 0,
            },
        },
    }

    LEVEL = {
        0: 0,
        1: 10000,
        2: 5000,
        3: 2500,
        4: 1250,
        5: 625,
        6: 312,
        7: 156,
        8: 78,
        9: 39,
    }

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

    def make_score(self, directions):
        LEVEL = self.LEVEL
        for d in directions:
            if d.chess >= 5:
                d.score = LEVEL[1]
                continue
            if d.death == 2:
                d.score = LEVEL[0]
                continue
            if d.chess >= 4 and d.death == 0:
                d.score = LEVEL[2]
                continue

            state = (d.chess, d.death, d.suffix, d.block)

            SCORES = {
                (4, 1, None, None): LEVEL[3],
                (3, 0, 1, 0): LEVEL[3] + 1,
                (2, 0, 2, 0): LEVEL[3] + 1,
                (1, 0, 3, 0): LEVEL[3] + 1,
                (3, 0, 1, 1): LEVEL[3],
                (2, 0, 2, 1): LEVEL[3],
                (1, 0, 3, 1): LEVEL[3],
                (3, 0, None, None): LEVEL[3],
                (3, 1, None, None): LEVEL[4],
                (2, 0, 1, 0): LEVEL[3],
                (1, 0, 2, 0): LEVEL[3],
                (2, 0, 1, 1): LEVEL[4],
                (1, 0, 2, 1): LEVEL[4],
                (2, 0, None, None): LEVEL[4],
                (2, 1, None, None): LEVEL[5],
                (1, 0, 1, 0): LEVEL[4],
                (1, 0, 1, 1): LEVEL[5],
                (1, 0, None, None): LEVEL[6],
                (1, 1, None, None): LEVEL[7],
            }
            if state in SCORES:
                d.score = SCORES[state]
            else:
                for state, score in SCORES.items():
                    chess, death, suffix, block = state
                    if chess != d.chess:
                        continue
                    if death != d.death:
                        continue
                    if (suffix, block) == (None, None):
                        d.score = score
                        break
            if d.score == 0:
                raise Exception('score not define %s' % d)
                logger.error('error %s', d)

            # if d.empty:
            #     d.score += 1
            # if name in ('principal', "counter"):
            #     d.score += 1

        direct = sorted(directions, key=lambda e: e.score, reverse=True)
        return direct

    def make_directions(self, value):
        directions = []

        for name, total in value.items():
            d = tone.utils.attrdict.attrdict()
            directions.append(d)
            d.name = name[0]
            d.chess = -1
            d.death = 0
            d.empty = 0
            d.suffix = 0
            d.block = 0
            d.score = 0

            for _, direct in total.items():
                if direct.suffix > d.suffix:
                    d.suffix = direct.suffix
                d.chess += direct.chess
                d.death += direct.death
                d.empty += direct.empty
                d.block += direct.block

        return directions

    def make(self, value):
        directions = self.make_directions(value)
        return self.make_score(directions)

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

                for step in range(0, 6):
                    move = (where[0] + step * x, where[1] + step * y)
                    if not functions.is_valid_where(move):
                        direct.death += 1
                        break
                    chess = board[move]
                    if reverse and move == self.where:
                        chess *= -1
                    if chess not in (turn, CHESS_EMPTY) and direct.empty == 0:
                        direct.death += 1
                        break
                    if chess not in (turn, CHESS_EMPTY) and direct.empty != 0:
                        direct.block += 1
                        break
                    if chess == turn and direct.empty == 0:
                        direct.chess += 1
                        continue
                    if chess == turn and direct.empty == 1:
                        direct.suffix += 1
                        continue
                    if chess == CHESS_EMPTY and direct.empty < 2 and direct.suffix == 0:
                        direct.empty += 1
                        continue

    def compute(self):
        self.collect(self.cvalue, reverse=False)
        direct = self.make(self.cvalue)
        self.cscore = direct[0].score
        for var in range(1, 3):
            if direct[var].chess > 2 or direct[var].suffix > 2:
                self.cscore += direct[1].score
                break

        # self.cscore = sum([direct[0].score, direct[1].score])

        if [var for var in direct if var.chess >= 5]:
            self.finished = True

        self.collect(self.rvalue, reverse=True)
        direct = self.make(self.rvalue)
        self.rscore = direct[0].score
        for var in range(1, 3):
            if direct[var].chess > 1 or direct[var].suffix > 1:
                self.rscore += direct[1].score
                break

        # self.rscore = sum([direct[0].score, direct[1].score])

        self.score = max(self.cscore, self.rscore * 0.9)
        # self.score = self.cscore + self.rscore
