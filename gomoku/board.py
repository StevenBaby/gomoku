# coding=utf-8
import os
import tkinter

from numpy import mat
from numpy import zeros

from PIL import Image
from PIL import ImageTk

import tone
import gomoku

logger = tone.utils.get_logger()


DIRNAME = os.path.dirname(__file__)
SKINPATH = os.path.join(DIRNAME, '../skins')
BACKGROUND = os.path.join(SKINPATH, 'background.png')
CHESS_BLACK = os.path.join(SKINPATH, 'black.png')
CHESS_WHITE = os.path.join(SKINPATH, 'white.png')

BOARD_SIZE = 600

CELL_WIDTH = BOARD_SIZE // (gomoku.WIDTH + 1)
CHESS_WIDTH = int(CELL_WIDTH * 0.9)
CHESS_SIZE = (CHESS_WIDTH, CHESS_WIDTH)

BOARD_START = CHESS_WIDTH // 2
BOARD_END = BOARD_SIZE - BOARD_START

CHESS_OFFSET_X = BOARD_START + 4
CHESS_OFFSET_Y = BOARD_START + 3


class Board(tkinter.Label):

    def __init__(self, *args, **kwargs):
        if 'callback' in kwargs:
            self.callback = kwargs.pop('callback')
        else:
            self.callback = None

        # init board image
        self.board_image = Image.open(BACKGROUND).convert('RGBA')
        self.board_tkimage = ImageTk.PhotoImage(self.board_image)

        tkinter.Label.__init__(self, image=self.board_tkimage, *args, **kwargs)
        self.place(x=0, y=0)

        self.init_event()
        self.init_chess()

    def init_chess(self):

        self.black_image = Image.open(CHESS_BLACK).convert('RGBA').resize(CHESS_SIZE)
        self.black_chess = ImageTk.PhotoImage(self.black_image)

        self.white_image = Image.open(CHESS_WHITE).convert('RGBA').resize(CHESS_SIZE)
        self.white_chess = ImageTk.PhotoImage(self.white_image)

        self.labels = mat(zeros((gomoku.WIDTH, gomoku.HEIGHT,)), dtype=tkinter.Label)

    def init_event(self):
        self.bind(sequence="<Button-1>", func=self.click)

    def get_position(self, event):
        xx = event.x_root - self.winfo_rootx()
        yy = event.y_root - self.winfo_rooty()

        x = (xx - BOARD_START) // CELL_WIDTH
        y = (yy - BOARD_START) // CELL_WIDTH

        if x < 0 or y < 0:
            return None
        if x > gomoku.WIDTH or y > gomoku.HEIGHT:
            return None

        where = (x, y)
        # logger.debug('get position %s', where)
        return where

    def click(self, event):
        where = self.get_position(event)
        if not where:
            return
        self.callback(where)

    def set_chess(self, where, chess):
        label = self.labels[where]
        if not label:
            label = tkinter.Label(self.master)
            self.labels[where] = label

        if chess == gomoku.BLACK:
            image = self.black_chess
        else:
            image = self.white_chess

        label.config(image=image)
        label.place(
            x=where[0] * CELL_WIDTH + CHESS_OFFSET_X,
            y=where[1] * CELL_WIDTH + CHESS_OFFSET_Y)
