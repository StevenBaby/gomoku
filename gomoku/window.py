# coding=utf-8

import os


import tkinter
from PIL import Image
from PIL import ImageTk


import tone

import gomoku
import board

from gomoku import Gomoku

DIRNAME = os.path.dirname(__file__)
SKINPATH = os.path.join(DIRNAME, '../skins')
FAVICON = os.path.join(SKINPATH, 'favicon.ico')

GAMENAME = 'Gomoku'


logger = tone.utils.get_logger()


class Menu(tkinter.Menu):

    def __init__(self, *args, **kwargs):
        tkinter.Menu.__init__(self, *args, **kwargs)
        self.init_game_menu()

    def init_game_menu(self):
        self.game_menu = tkinter.Menu(self, tearoff=0)

        self.game_menu.add_command(label="Exit", command=self.master.quit)

        self.add_cascade(label="Game", menu=self.game_menu)


class Window(tkinter.Tk):

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)
        self.gomoku = Gomoku()

        self.menu = Menu(self)
        self.config(menu=self.menu)

        self.iconbitmap(FAVICON)
        self.title(GAMENAME)
        self.resizable(False, False)

        self.init_board()

    def init_board(self):
        width = board.BOARD_SIZE
        height = board.BOARD_SIZE
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = f'{width}x{height}+{(screenwidth-width)//2}+{(screenheight-height)//2}'
        self.geometry(geometry)
        self.board = board.Board(self, callback=self.move)

    def move(self, where):
        if self.gomoku.has_chess(where):
            return
        logger.debug("gomoku move %s [%s]", where, self.gomoku.turn)
        self.board.set_chess(where, self.gomoku.turn)
        self.gomoku.move(where)


def main():
    window = Window()
    window.mainloop()


if __name__ == '__main__':
    main()
