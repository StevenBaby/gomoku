# coding=utf-8

import os

from numpy import mat
from numpy import zeros

import tkinter
from PIL import Image
from PIL import ImageTk


import tone

import gomoku
from gomoku import Gomoku

DIRNAME = os.path.dirname(__file__)
SKINPATH = os.path.join(DIRNAME, '../skins')
FAVICON = os.path.join(SKINPATH, 'favicon.ico')
BACKGROUND = os.path.join(SKINPATH, 'background.png')
CHESS_BLACK = os.path.join(SKINPATH, 'black.png')
CHESS_WHITE = os.path.join(SKINPATH, 'white.png')

GAMENAME = 'Gomoku'

BOARD_SIZE = 600

CELL_WIDTH = BOARD_SIZE // (gomoku.WIDTH + 1)
CHESS_WIDTH = int(CELL_WIDTH * 0.9)
CHESS_SIZE = (CHESS_WIDTH, CHESS_WIDTH)

BOARD_START = CHESS_WIDTH // 2
BOARD_END = BOARD_SIZE - BOARD_START

CHESS_START_X = BOARD_START + 4
CHESS_START_Y = BOARD_START + 3


logger = tone.utils.get_logger()


class Window(tkinter.Tk):

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)
        self.gomoku = Gomoku()

        self.iconbitmap(FAVICON)
        self.title(GAMENAME)
        self.resizable(False, False)

        self.init_board()
        self.init_event()
        self.init_chess()

    def init_board(self):
        width = BOARD_SIZE
        height = BOARD_SIZE
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = f'{width}x{height}+{(screenwidth-width)//2}+{(screenheight-height)//2}'
        self.geometry(geometry)

        self.bg_image = Image.open(BACKGROUND).convert('RGBA')
        self.bg_tkimage = ImageTk.PhotoImage(self.bg_image)
        self.bg = tkinter.Label(self, image=self.bg_tkimage,)
        self.bg.place(x=0, y=0)

    def init_chess(self):

        self.black_image = Image.open(CHESS_BLACK).convert('RGBA').resize(CHESS_SIZE)
        self.black_chess = ImageTk.PhotoImage(self.black_image)

        self.white_image = Image.open(CHESS_WHITE).convert('RGBA').resize(CHESS_SIZE)
        self.white_chess = ImageTk.PhotoImage(self.white_image)

        self.labels = mat(zeros((gomoku.WIDTH, gomoku.HEIGHT,)), dtype=tkinter.Label)

    def set_chess(self, where, chess):
        label = self.labels[where]
        if not label:
            label = tkinter.Label(self)
            self.labels[where] = label

        if chess == gomoku.BLACK:
            image = self.black_chess
        else:
            image = self.white_chess

        label.config(image=image)
        label.place(
            x=where[0] * CELL_WIDTH + CHESS_START_X,
            y=where[1] * CELL_WIDTH + CHESS_START_Y)

    def move(self, where):
        if self.gomoku.has_chess(where):
            return
        logger.debug("gomoku move %s [%s]", where, self.gomoku.turn)
        self.set_chess(where, self.gomoku.turn)
        self.gomoku.move(where)

    def init_event(self):
        self.bind(sequence="<Button-1>", func=self.click)

    def get_position(self, event):
        xx = event.x_root - self.bg.winfo_rootx()
        yy = event.y_root - self.bg.winfo_rooty()

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

        self.move(where)


def main():
    window = Window()
    window.mainloop()


if __name__ == '__main__':
    main()
