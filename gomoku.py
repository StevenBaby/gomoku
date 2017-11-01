#!/usr/bin/python2
# encoding=utf8

import os
import dandan
import copy
import random
import logging
import logging.config
# import traceback

from numpy import mat
from numpy import zeros


__VERSION__ = "0.7.0"


class Direct(object):

    TYPE_SS = "TYPE_SS"
    TYPE_FF = "TYPE_FF"

    TYPE_A4 = "TYPE_A4"
    TYPE_A3 = "TYPE_A3"
    TYPE_A2 = "TYPE_A2"
    TYPE_A1 = "TYPE_A1"

    TYPE_D4 = "TYPE_D4"
    TYPE_D3 = "TYPE_D3"
    TYPE_D2 = "TYPE_D2"
    TYPE_D1 = "TYPE_D1"

    TYPE_C5 = "TYPE_C5"
    TYPE_C4 = "TYPE_C4"
    TYPE_C3 = "TYPE_C3"
    TYPE_C2 = "TYPE_C2"

    TYPE_F5 = "TYPE_F5"
    TYPE_F4 = "TYPE_F4"
    TYPE_F3 = "TYPE_F3"
    TYPE_F2 = "TYPE_F2"

    def __init__(self, pos, where, turn, fore, back, name):
        self.pos = pos
        self.where = where
        self.turn = turn
        self.fore = fore
        self.back = back
        self.name = name

        self.type = None
        self.range = []
        self.length = 0

        self.remain = 0
        self.remains = [0, 0]

        self.dead = 0
        self.point = 0
        self.points = [0, 0]

        self.win = False

    def make_orient(self, wheres, orient, debug=False):
        logger = logging.getLogger("gomoku")
        pos = self.pos
        turn = self.turn

        if debug:
            logger.debug(wheres)

        for where in wheres:
            if not where:
                if debug:
                    logger.debug('test %s border', where)
                self.dead += 1
                return

            if pos[where] == turn and not self.points[orient]:
                if debug:
                    logger.debug('test %s continuous', where)
                self.range.append(where)
                continue

            if pos[where] == turn:
                if debug:
                    logger.debug('test %s interrupt', where)
                self.remains[orient] += 1
                continue

            if pos[where] == 0 and not self.points[orient]:
                if debug:
                    logger.debug('test %s first point', where)
                self.point += 1
                self.points[orient] = 1
                continue

            if pos[where] == 0:
                if debug:
                    logger.debug('test %s second point', where)
                return

            if pos[where] == turn * -1 and self.points[orient] and not self.remains[orient]:
                if debug:
                    logger.debug('test %s second finish', where)
                return

            if pos[where] == turn * -1:
                if debug:
                    logger.debug('test %s dead', where)
                self.dead += 1
                return

            logger.warning('make orient %s uncatched', where)

    def make_direct(self, debug):
        # logger = logging.getLogger("gomoku")
        self.range.append(self.where)
        # go fore
        self.make_orient(self.fore, 0, debug)
        # go back
        self.make_orient(self.back, 1, debug)

        self.remain = max(self.remains)
        self.length = len(self.range) + self.remain

    def make_type(self, debug):
        logger = logging.getLogger("gomoku")
        length = self.length
        dead = self.dead
        remain = self.remain
        point = self.point

        if length >= 5 and not remain:
            self.win = True
            self.type = self.TYPE_SS
            return

        if length >= 5:
            self.type = self.TYPE_C5
            return

        if length < 5 and dead == 2:
            self.type = self.TYPE_FF
            return

        types = {
            # length
            4: {
                #  remain
                True: {
                    # dead
                    0: self.TYPE_C4,
                    1: self.TYPE_F4,
                },
                False: {
                    # dead
                    0: self.TYPE_A4,
                    1: self.TYPE_D4,
                },
            },
            3: {
                #  remain
                True: {
                    # dead
                    0: self.TYPE_C3,
                    1: self.TYPE_F3,
                },
                False: {
                    # dead
                    0: self.TYPE_A3,
                    1: self.TYPE_D3,
                },
            },
            2: {
                #  remain
                True: {
                    # dead
                    0: self.TYPE_C2,
                    1: self.TYPE_F2,
                },
                False: {
                    # dead
                    0: self.TYPE_A2,
                    1: self.TYPE_D2,
                },
            },
            1: {
                #  remain
                True: {
                    # dead
                    0: None,
                    1: None,
                },
                False: {
                    # dead
                    0: self.TYPE_A1,
                    1: self.TYPE_D1,
                },
            },
        }
        # logger.debug(types)
        try:
            self.type = types[length][remain > 0][dead]
        except Exception:
            logger.warning("make type uncatched length %s remain %s dead %s point %s", length, remain, dead, point)

    def score(self):
        scores = {
            self.TYPE_SS: 50000,
            self.TYPE_FF: 0,

            self.TYPE_A4: 10000,
            self.TYPE_A3: 4000,
            self.TYPE_A2: 1500,
            self.TYPE_A1: 500,

            self.TYPE_C5: 6000,
            self.TYPE_C4: 4500,
            self.TYPE_C3: 3500,
            self.TYPE_C2: 1200,

            self.TYPE_D4: 5000,
            self.TYPE_D3: 2000,
            self.TYPE_D2: 800,
            self.TYPE_D1: 100,

            self.TYPE_F5: 4500,
            self.TYPE_F4: 3500,
            self.TYPE_F3: 1500,
            self.TYPE_F2: 200,

            None: 0,
        }
        res = scores[self.type]
        if self.name in ("vh", "hv"):
            res += 10
        return res

    def make(self, debug=False):
        self.make_direct(debug)
        self.make_type(debug)


class Step(object):

    max_depth = 0
    max_step = 8

    width = 19
    height = 19
    wrange = dict([(var, True) for var in xrange(0, width)])
    hrange = dict([(var, True) for var in xrange(0, height)])

    def __init__(self, pos=None, where=None, turn=0,):
        self.reset()

        if pos is not None:
            self.pos = pos

        self.where = where
        if where:
            self.pos[where] = turn

        self.turn = turn

    def reset(self):
        self.pos = mat(zeros((self.width, self.height,)), dtype=int)
        self.children = []
        self.directs = []
        self.turn = 0
        self.where = None
        self.parent = None
        self._score = 0
        self._win = False

    def get_ranges(self):
        # logger = logging.getLogger("gomoku")
        ranges = dandan.value.AttrDict()
        x, y = self.where
        orange = xrange(1, 6)

        ranges.hh.fore = [
            (x, y - var) for var in orange if (y - var) in self.hrange
        ]  # left

        ranges.hh.back = [
            (x, y + var) for var in orange if (y + var) in self.hrange
        ]  # right

        ranges.vv.fore = [
            (x - var, y) for var in orange if (x - var) in self.wrange
        ]  # top
        ranges.vv.back = [
            (x + var, y) for var in orange if (x + var) in self.wrange
        ]  # down

        ranges.hv.fore = [
            (x - var, y + var) for var in orange if (x - var) in self.wrange and (y + var) in self.hrange
        ]  # top right

        ranges.hv.back = [
            (x + var, y - var) for var in orange if (x + var) in self.wrange and (y - var) in self.hrange
        ]  # down left

        ranges.vh.fore = [
            (x - var, y - var) for var in orange if (x - var) in self.wrange and (y - var) in self.hrange
        ]  # top left

        ranges.vh.back = [
            (x + var, y + var) for var in orange if (x + var) in self.wrange and (y + var) in self.hrange
        ]  # down right

        for direct in ranges:
            for orient in ranges[direct]:
                # if len(ranges[direct][orient]) < len(orange):
                ranges[direct][orient].append(None)
        return ranges

    def make_directs(self, debug=False):
        # logger = logging.getLogger("gomoku")
        ranges = self.get_ranges()
        directs = []
        for direct_name in ranges:
            direct = Direct(
                pos=self.pos,
                where=self.where,
                turn=self.turn,
                fore=ranges[direct_name].fore,
                back=ranges[direct_name].back,
                name=direct_name,
            )
            direct.make(debug)
            directs.append(direct)
        directs = sorted(directs, reverse=True, key=lambda e: e.score())
        if directs[0].type == Direct.TYPE_A4:
            self._score = directs[0].score()
        else:
            self._score = sum([var.score() for var in directs[:2]])
        self._win = directs[0].win
        self.directs = directs

    def score(self):
        if not self.where:
            return self.score
        if not self.directs:
            self.make_directs()
        return self._score

    def win(self):
        if not self.where:
            return False
        if not self.directs:
            self.make_directs()
        return self._win

    def get_wheres(self):
        whole = [(xx, yy) for xx in xrange(0, self.width) for yy in xrange(0, self.height) if self.pos[(xx, yy)] != 0]

        wheres = {}
        for where in whole:
            xx, yy = where
            ws = [(x, y) for x in xrange(xx - 2, xx + 3) for y in xrange(yy - 2, yy + 3) if x in self.wrange and y in self.hrange and self.pos[(x, y)] == 0 and (x, y) not in wheres]
            for w in ws:
                wheres[w] = True
        return wheres

    def get_next(self, turn, depth=0):
        logger = logging.getLogger("gomoku")
        logger.debug("Thinking turn %s depth %s", turn, depth)
        if (self.pos == 0).sum() == 0:
            return None

        if (self.pos == 0).sum() == self.width * self.height:
            return Step(where=(self.width // 2, self.height // 2), turn=turn * -1, pos=copy.copy(self.pos))

        children = []
        wheres = self.get_wheres()
        for where in wheres.keys():
            current = Step(where=where, pos=copy.copy(self.pos), turn=turn, )
            if current.win():
                return current
            counter = Step(where=where, pos=copy.copy(self.pos), turn=turn * -1, )

            first = current if current.score() >= counter.score() else counter
            second = current if first != current else counter

            pair = [first, second]
            children.append(pair)

        steps = sorted(children,
                       reverse=True,
                       key=lambda e: [e[0].score(), e[1].score(), random.random()],)[:self.max_step]
        logger.debug([(e[0].score(), e[1].score()) for e in steps])

        if depth >= self.max_depth or steps[0][0].win():
            return steps[0][0]

        substeps = []
        for step, _ in steps:
            substep = step.get_next(turn=turn * -1, depth=depth + 1)
            substep.parent = step
            substeps.append(substep)

        step = sorted(substeps, key=lambda e: [e.score(), random.random()], reverse=True)[0]
        return step.parent


class Gomoku(Step):

    def __init__(self):
        Step.__init__(self)
        self.reset()
        self.init_logger()

    def init_logger(self):
        filename = os.path.abspath(__file__)
        dirname = os.path.dirname(filename)
        logfile = os.path.join(dirname, "gomoku.log")

        LOGGING = {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'verbose': {
                    # 'format': '[%(asctime)s] [%(name)s] [%(process)d] [%(module)s] [%(funcName)s] [%(lineno)d]  [%(levelname)s] | %(message)s'
                    'format': '[%(module)s] [%(lineno)d] [%(levelname)s] | %(message)s'
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'verbose',
                    "level": "DEBUG",
                },
                'file': {
                    'class': 'logging.FileHandler',
                    'formatter': 'verbose',
                    'filename': logfile,
                    "level": "INFO",
                },
            },
            'loggers': {
                'gomoku': {
                    'handlers': ['console', "file", ],
                    'level': "DEBUG",
                    'propagate': True,
                },
            },
        }
        logging.config.dictConfig(LOGGING)
        self.logger = logging.getLogger("gomoku")

    def reset(self):
        Step.reset(self)
        self.his = []
        self.turn = 1
        self.thinking = False

    def dump(self, filename=None):
        if not filename:
            filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dumps/default.gomo")
        filename = os.path.abspath(filename)
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        data = dandan.value.AttrDict()
        data.filetype = "gomo"
        data.pos = self.pos
        data.turn = self.turn
        data.where = self.where
        data.his = self.his
        dandan.value.put_pickle(data, filename)

        self.logger.info("dump > {}".format(filename))

    def load(self, filename=None):
        if not filename:
            filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dumps/default.gomo")
        if not os.path.exists(filename):
            self.logger.warning("file {} not exists".format(filename))
            return
        data = dandan.value.get_pickle(filename)
        if not isinstance(data, dandan.value.AttrDict):
            return
        if data.filetype != "gomo":
            return
        self.pos = data.pos
        self.turn = data.turn
        self.his = data.his
        self.where = data.where

    def back(self):
        if len(self.his) < 1:
            self.logger.warning("No more step to back")
            return None
        self.directs = []
        where = self.his[-1]
        self.pos[where] = 0
        self.his.pop()
        self.turn *= -1
        return where

    def info(self, where):
        pos = copy.copy(self.pos)
        pos[where] = 0
        current = Step(where=where, turn=self.turn, pos=pos)

        pos = copy.copy(self.pos)
        pos[where] = 0
        counter = Step(where=where, turn=self.turn * -1, pos=pos)
        return current, counter

    def set(self, where):
        if self.pos[where] != 0:
            return
        self.where = where
        self.his.append(self.where)
        self.pos[self.where] = self.turn
        self.make_directs()
        self.turn *= -1

    def compute_pos(self):
        if self.win():
            return None

        logger = self.logger
        logger.debug("Thinking ...")
        step = self.get_next(self.turn)
        if not step:
            # print "No more step..."
            return None

        if self.pos[step.where] != 0:
            print step.where
            raw_input()
        return step.where

    def test(self, where):
        logger = self.logger

        for x in xrange(0, 2):
            logger.debug('==================== %s start =============================', x)
            step = Step(where=where, turn=self.turn, pos=copy.copy(self.pos))
            step.make_directs()
            directs = step.directs

            logger.debug("point %s", [(var.name, var.point) for var in directs])
            logger.debug("dead %s", [(var.name, var.dead) for var in directs])
            logger.debug("remain %s", [(var.name, var.remain) for var in directs])
            logger.debug("type %s", [(var.name, var.type) for var in directs])
            logger.debug("score %s", [(var.name, var.score()) for var in directs])
            self.turn *= -1
