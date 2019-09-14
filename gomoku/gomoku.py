# coding=utf-8

from numpy import mat
from numpy import zeros

import tone

logger = tone.utils.get_logger()


WIDTH = 19
HEIGHT = WIDTH

NONE = 0
BLACK = 1
WHITE = -1


class Gomoku(object):

    def __init__(self):
        self.board = mat(zeros((WIDTH, HEIGHT)), dtype=int)
        self.turn = BLACK

    def has_chess(self, where):
        has = self.board[(where[1], where[0])] != 0
        return has

    def move(self, where):
        self.board[(where[1], where[0])] = self.turn
        self.turn *= -1

        # print(self.board)

    def test(self):
        pass


def main():
    gomoku = Gomoku()
    gomoku.test()


if __name__ == '__main__':
    main()
