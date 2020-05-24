# coding=utf-8
import copy
import tone
from tone.utils.attrdict import attrdict

from . import CHESS_EMPTY
from . import functions


logger = tone.utils.get_logger()


class Direct(object):

    def __init__(self, step=None, name=''):
        self.step = step
        self.name = name
        self.chess = 0
        self.death = 0
        self.empty = 0
        self.suffix = 0
        self.block = 0
        self.score = 0
        self.gameover = False

    def compute_score(self):
        chess = self.chess
        death = self.death
        suffix = self.suffix
        block = self.block

        if chess >= 5:
            self.gameover = True
            return 100000
        if death == 2:
            return 0
        if (chess, death) == (4, 0):
            return 10000

        total = chess + suffix
        if total >= 4:
            return 5000

        if block > 0:
            death = 1

        state = (total, death)

        SCORES = {
            (3, 0): 4800,
            (3, 1): 2500,
            (2, 0): 2400,
            (2, 1): 1200,
            (1, 0): 1100,
            (1, 1): 500,
        }

        if state in SCORES:
            return SCORES[state]
        else:
            logger.error(f'error state {state}')
            raise Exception(f'score not define {state}')

    def make_score(self):
        score = self.compute_score()
        self.score = score


class Score(object):
    params = {
        'horizontal': {
            'left': Direct(step=(0, -1)),
            'right': Direct(step=(0, 1)),
        },
        'vertical': {
            'upper': Direct(step=(-1, 0)),
            'lower': Direct(step=(1, 0)),
        },
        'principal': {
            'upperleft': Direct(step=(-1, -1)),
            'lowerright': Direct(step=(1, 1)),
        },
        'counter': {
            'lowerleft': Direct(step=(1, -1)),
            'upperright': Direct(step=(-1, 1)),
        },
    }

    def __init__(self, board, where):

        self.board = board
        self.where = where
        self.cvalue = attrdict.loads(copy.deepcopy(self.params))
        self.rvalue = attrdict.loads(copy.deepcopy(self.params))
        self.gameover = False
        self.cscore = 0
        self.rscore = 0
        self.score = 0
        self.compute()

    def make(self, value):
        directions = []

        for name, total in value.items():
            d = Direct(name=name[0])
            directions.append(d)
            d.chess = -1

            for _, direct in total.items():
                if direct.suffix > d.suffix:
                    d.suffix = direct.suffix
                if direct.block > d.block:
                    d.block = direct.block
                d.chess += direct.chess
                d.death += direct.death
                d.empty += direct.empty
            d.make_score()

        directions = sorted(directions, key=lambda e: e.score, reverse=True)
        return directions

    def collect(self, value, reverse=False):
        board = self.board
        where = self.where
        turn = board[where]

        if reverse:
            turn *= -1

        for total_name in self.params:
            total = value[total_name]
            for direct_name in self.params[total_name]:
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
                    if direct.empty == 2:
                        break

    def compute(self):
        self.collect(self.cvalue, reverse=False)
        direct = self.make(self.cvalue)
        self.cvalue.direct = direct
        if any([var.gameover for var in direct]):
            self.gameover = True

        # self.cscore = direct[0].score
        self.cscore = direct[0].score + direct[1].score

        self.score = self.cscore
        return

        self.collect(self.rvalue, reverse=True)
        direct = self.make(self.rvalue)
        self.rvalue.direct = direct
        self.rscore = direct[0].score + direct[1].score
        self.score = max(self.cscore, self.rscore - 1)
        # self.score = self.cscore + self.rscore
