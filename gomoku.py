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


__VERSION__ = "0.2.1"
colorama.init(autoreset=True)


class Step(object):

    def init_settings(self):
        self.max_depth = 2
        self.max_step = 6
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
        pos = self.pos
        turn = self.turn
        orient.score = 0
        orient.dead = 0
        orient.point = 0
        orient.cont = []

        for where in orient.range:
            if pos[where] == turn and not orient.point:
                orient.cont.append(where)
                orient.type1 += 1
                continue

            elif pos[where] == turn:
                orient.type2 += 1
                continue

            elif pos[where] == 0 and not orient.point:
                orient.type3 += 1
                orient.point += 1
                break

            elif pos[where] == 0:
                orient.type4 += 1
                continue

            elif pos[where] == turn * -1 and orient.point:
                orient.type5 += 1
                break

            elif pos[where] == turn * -1:
                orient.type6 += 1
                break

        orient.dead = (orient.type6 or 0)
        orient.score += (orient.type1 or 0) * 100
        orient.score += (orient.type2 or 0) * 50
        orient.score += (orient.type3 or 0) * 20
        orient.score += (orient.type4 or 0) * 5
        orient.score += (orient.type5 or 0)

    def make_direction(self, direction):
        direction.score = 0
        direction.win = False
        direction.range = [self.where]
        direction.dead = 0
        direction.point = 0
        for name in direction.orient:
            orient = direction.orient[name]
            orient.name = name
            orient.direction = direction.name
            self.make_orient(orient)

            direction.dead += orient.dead
            direction.point += orient.point
            direction.score += orient.score
            if direction.dead > 1 and len(direction.range) < 5:
                direction.score = 0
            direction.range.extend(orient.cont)

    def make_crude(self,):
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

            if len(direction.range) >= 5:
                crude.range = direction.range
                direction.win = True

            crude.directions.append(direction)
            crude.directions = sorted(crude.directions, key=lambda e: e.score, reverse=True)[:2]
            crude.scores = [var.score for var in crude.directions]
            if direction.win:
                crude.win = True

        crude.score = crude.scores[0]
        crude.surplus = crude.scores[1] // 10
        crude.score += crude.surplus
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
        if (self.pos == 0).sum() == 0:
            return None

        if (self.pos == 0).sum() == self.width * self.height:
            return Step(where=(self.width // 2, self.height // 2), turn=turn * -1, pos=copy.copy(self.pos))

        self.children = []

        wheres = self.get_wheres()
        for where in wheres.keys():
            current = Step(where=where, turn=turn, pos=copy.copy(self.pos))
            counter = Step(where=where, turn=turn * -1, pos=copy.copy(self.pos))
            first = current if current.score() >= counter.score() else counter
            second = current if current != first else counter
            step = (first, second)
            self.children.append(step)

        steps = sorted(self.children, key=lambda e: [e[0].score(), e[1].score(), e[0].turn, random.random()], reverse=True)[:self.max_step]
        if depth >= self.max_depth or steps[0][0].win():
            return steps[0][0]

        substeps = []
        for step, _ in steps:
            substep = step.get_next(turn=turn * -1, depth=depth + 1)
            substep.parent = step
            substeps.append(substep)

        step = sorted(substeps, key=lambda e: [e.score(), random.random()], reverse=True)[0]
        return step.parent

    def test(self):
        self.show()
        self.reset_crude()
        for name in self.crude.direction:
            for var in self.crude.direction[name].orient:
                orient = self.crude.direction[name].orient[var]
                for where in orient.range:
                    if self.pos[where] != 0:
                        break
                    self.pos[where] = self.turn
                    self.show()
                    print name, var, where
                    raw_input()
        return


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

    def dump(self):
        self.children = []
        filename = os.path.abspath('dump.bin')
        dandan.value.put_pickle(self, filename)
        self.logger.info("dump > {}".format(filename))

    def load(self):
        filename = os.path.abspath('dump.bin')
        if not os.path.exists(filename):
            print "file not exists"
            return
        data = dandan.value.get_pickle(filename)
        self.pos = data.pos
        self.turn = data.turn
        self.his = data.his
        self.where = data.where
        self.crude = data.crude

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

    def test(self, where):
        step = Step(where=where, turn=self.turn, pos=copy.copy(self.pos))
        step.test()

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
        step = self.get_next(self.turn * -1)
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

    def statistic(self):
        print "Count None:", (self.pos == 0).sum()
        print "Count Black:", (self.pos == 1).sum()
        print "Count White:", (self.pos == -1).sum()

    def play(self, ):
        while True:
            self.show()
            # self.statistic()
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


def main():
    gomoku = Gomoku()
    gomoku.play()


if __name__ == '__main__':
    main()
