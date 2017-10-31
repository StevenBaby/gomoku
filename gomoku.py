#!/usr/bin/python2
# encoding=utf8

import sys
import re
import os
import dandan
import copy
import time
import random
import logging
import logging.config
import colorama
import traceback

from numpy import mat
from numpy import zeros


__VERSION__ = "0.6.0"
colorama.init(autoreset=True)


class Step(object):

    def init_settings(self):
        self.max_depth = 3
        self.max_step = 4
        self.percent = 1000

    def init_const(self):
        self.width = 19
        self.height = 19
        self.white = u"○"
        self.black = u"●"

        self.board_color = colorama.Fore.MAGENTA + colorama.Back.YELLOW
        self.chess_color = colorama.Fore.BLACK + colorama.Back.YELLOW

        self.win_color = colorama.Fore.RED + colorama.Back.YELLOW
        self.where_color = colorama.Fore.BLACK + colorama.Back.WHITE
        self.index_color = [
            colorama.Fore.BLACK + colorama.Back.MAGENTA,
            colorama.Fore.WHITE + colorama.Back.CYAN,
        ]

        self.wrange = range(0, self.width)
        self.hrange = range(0, self.height)

    def __init__(self, pos=None, where=None, turn=0,):
        self.init_const()
        self.init_settings()
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
        self.turn = 0
        self.where = None
        self.parent = None
        self.crude = None

    def show(self, clear=True):
        pos = self.pos
        if clear:
            dandan.system.clear()
        sys.stdout.write("  ")
        for x in xrange(-1, self.width):
            if x != -1:
                sys.stdout.write(self.index_color[x % 2] + "{:02}".format(x))
            for y in xrange(0, self.height):
                if x == -1:
                    sys.stdout.write(self.index_color[y % 2] + "{:02}".format(y))
                    continue
                chess = pos[x, y]
                if self.crude and self.crude.win and (x, y) in self.crude.range:
                    sys.stdout.write(self.win_color + (self.black if chess == 1 else self.white))
                    continue
                if chess != 0 and self.where == (x, y):
                    sys.stdout.write(self.where_color + (self.black if chess == 1 else self.white))
                    continue
                if chess != 0:
                    sys.stdout.write(self.chess_color + (self.black if chess == 1 else self.white))
                    continue
                if (x, y) == (0, 0):  # top left corner
                    sys.stdout.write(self.board_color + u"┌")
                    continue
                if (x, y) == (self.width - 1, 0):  # top right corner
                    sys.stdout.write(self.board_color + u"└")
                    continue
                if (x, y) == (0, self.height - 1):  # bottom left corner:
                    sys.stdout.write(self.board_color + u"┐")
                    continue
                if (x, y) == (self.width - 1, self.height - 1):  # bottom right corner:
                    sys.stdout.write(self.board_color + u"┘")
                    continue
                if x == 0:
                    sys.stdout.write(self.board_color + u"┬")
                    continue
                if x == self.width - 1:
                    sys.stdout.write(self.board_color + u"┴")
                    continue
                if y == 0:
                    sys.stdout.write(self.board_color + u"├")
                    continue
                if y == self.height - 1:
                    sys.stdout.write(self.board_color + u"┤")
                    continue
                sys.stdout.write(self.board_color + u"┼")
            print

    def reset_crude(self):
        crude = dandan.value.AttrDict()
        x, y = self.where
        crude.direction.hh.orient.fore.range = [
            (x, y - var) for var in xrange(1, 6) if (y - var) in self.hrange
        ]  # left
        crude.direction.hh.orient.back.range = [
            (x, y + var) for var in xrange(1, 6) if (y + var) in self.hrange
        ]  # right

        crude.direction.vv.orient.fore.range = [
            (x - var, y) for var in xrange(1, 6) if (x - var) in self.wrange
        ]  # top
        crude.direction.vv.orient.back.range = [
            (x + var, y) for var in xrange(1, 6) if (x + var) in self.wrange
        ]  # down

        crude.direction.hv.orient.fore.range = [
            (x - var, y + var) for var in xrange(1, 6) if (x - var) in self.wrange and (y + var) in self.hrange
        ]  # top right
        crude.direction.hv.orient.back.range = [
            (x + var, y - var) for var in xrange(1, 6) if (x + var) in self.wrange and (y - var) in self.hrange
        ]  # down left

        crude.direction.vh.orient.fore.range = [
            (x - var, y - var) for var in xrange(1, 6) if (x - var) in self.wrange and (y - var) in self.hrange
        ]  # top left

        crude.direction.vh.orient.back.range = [
            (x + var, y + var) for var in xrange(1, 6) if (x + var) in self.wrange and (y + var) in self.hrange
        ]  # down right
        self.crude = crude

    def make_orient(self, orient):
        # logger = logging.getLogger("gomoku")
        pos = self.pos
        turn = self.turn
        orient.score = 0
        orient.cont = []

        orient.type1 = 0
        orient.type2 = 0
        orient.type3 = 0
        orient.type4 = 0
        orient.type5 = 0
        orient.type6 = 0

        for where in orient.range:
            if pos[where] == turn and not orient.type3:
                orient.cont.append(where)
                orient.type1 += 1
                continue

            elif pos[where] == turn:
                orient.type2 += 1
                continue

            elif pos[where] == 0 and not orient.type3:
                orient.type3 += 1
                continue

            elif pos[where] == 0:
                orient.type4 += 1
                continue

            elif pos[where] == turn * -1 and orient.type3:
                orient.type5 += 1
                break

            elif pos[where] == turn * -1:
                orient.type6 += 1
                break

    def score_direction(self, direction):
        logger = logging.getLogger("gomoku")
        del direction["orient"]
        direction.win = False

        length = len(direction.range)
        dead = direction.type6

        # logger.debug("length %s dead %s", length, dead)
        if dead >= 2 and length < 5:
            direction.score = 0
            return

        if length >= 5:  # S5
            direction.score = 120000
            direction.win = True
            return

        scores = {
            # dead 0
            0: {  # length
                4: 50000,
                3: 15000,
                2: 6000,
                1: 2000,
            },
            # dead 1
            1: {  # length
                4: 10000,
                3: 4000,
                2: 1000,
                1: 100,
            },
        }

        direction.score = scores[dead][length]
        if length == 4:
            return

        away = direction.type2
        aways = {
            0: {
                3: 15000,
                2: 6000,
                1: 2000,
            },
            1: {
                3: 4000,
                2: 1000,
                1: 100,
            },
        }
        if away:
            direction.score += aways[dead][length]

    def make_direction(self, direction):
        direction.score = 0
        direction.win = False
        direction.range = [self.where]

        direction.type1 = 0
        direction.type2 = 0
        direction.type3 = 0
        direction.type4 = 0
        direction.type5 = 0
        direction.type6 = 0

        for name in direction.orient:
            orient = direction.orient[name]
            orient.name = name
            orient.direction = direction.name
            self.make_orient(orient)

            direction.range.extend(orient.cont)

            direction.type1 += orient.type1
            direction.type2 += orient.type2
            direction.type3 += orient.type3
            direction.type4 += orient.type4
            direction.type5 += orient.type5
            direction.type6 += orient.type6

    def make_crude(self,):
        logger = logging.getLogger("gomoku")
        self.reset_crude()
        crude = self.crude

        crude.score = 0
        crude.surplus = 0
        crude.win = False
        crude.scores = []
        crude.directions = []

        for name in crude.direction:
            direction = crude.direction[name]
            direction.name = name
            self.make_direction(direction)
            self.score_direction(direction)
            # logger.debug(direction)
            if direction.win:
                crude.win = True
            crude.directions.append(direction)
            crude.directions = sorted(crude.directions, key=lambda e: e.score, reverse=True)
            crude.scores = [var.score for var in crude.directions][:2]

        if crude.win:
            crude.score = crude.scores[0]
        else:
            crude.score = sum(crude.scores)
        return crude.score

    def score(self):
        if not self.where:
            return 0
        if not self.crude:
            self.make_crude()
        return self.crude.score

    def win(self):
        if not self.where:
            return False
        if not self.crude:
            self.make_crude()
        return self.crude.win

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
            counter = Step(where=where, pos=copy.copy(self.pos), turn=turn * -1, )
            pair = sorted([current, counter], key=lambda e: [e.score(), e.turn * turn], reverse=True)
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

        self.reset_crude()
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
        self.make_crude()
        self.turn *= -1

    def input_pos(self,):
        while True:
            try:
                sys.stdout.write(u"POS:")
                cmd = raw_input().strip()
                if not cmd:
                    return self.compute_pos()

                if cmd == "dump":
                    self.dump()
                    continue

                if cmd == 'load':
                    self.load()
                    continue

                if cmd == "back":
                    self.back()
                    continue

                if cmd == "show":
                    self.show()
                    continue

                cmds = cmd.split(" ")
                if len(cmds) >= 2:
                    where = (int(cmds[0]), int(cmds[1]))
                if len(cmds) > 2:
                    cmd = cmds[2].strip()
                    if cmd == "info":
                        self.info(where)
                        continue
                    if cmd == "test":
                        self.test(where)
                        continue
                    if cmd == "set":
                        if self.pos[where] != 0:
                            print "Warning: position already occupied."
                            continue
                        self.pos[where] = self.turn
                        self.his.append(where)
                        self.turn *= -1
                        self.show()
                        continue

                if self.pos[where] != 0:
                    print "Warning: position already occupied."
                    continue
                break
            except KeyboardInterrupt:
                exit()
            except Exception as e:
                e
                traceback.print_exc()
                continue
        if self.win():
            return None

        return where

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

    def get_pos(self,):
        if self.turn == 1:
            return self.input_pos()
        else:
            return self.compute_pos()

    def play(self, ):
        while True:
            self.show()
            where = self.get_pos()
            if not where:
                raw_input()
                continue

            self.where = where
            self.his.append(self.where)
            self.pos[self.where] = self.turn
            self.make_crude()
            self.show()
            if self.win():
                self.show()
                if self.turn == 1:
                    print "YOU WIN"
                else:
                    print "YOU LOSE"

            self.turn *= -1


# def main():
#     gomoku = Gomoku()
#     gomoku.play()


# if __name__ == '__main__':
#     main()
