#!/usr/bin/python2
# encoding=utf8
import os
import Tkinter
import ttk
import tkMessageBox 
import dandan
from PIL import Image
from PIL import ImageTk

import gomoku


class GomokuUI(object):

    def __init__(self):
        self.initialize()

    def initialize_root(self):
        self.size = 800
        self.root = Tkinter.Tk()
        self.root.title("Gomoku")

        self.root.minsize(self.size, self.size)
        self.root.maxsize(self.size, self.size)
        self.root.resizable(False, False)

        self.filepath = os.path.abspath(__file__)
        self.dirname = os.path.dirname(self.filepath)
        self.iconpath = os.path.join(self.dirname, "favicon.ico")
        self.root.iconbitmap(self.iconpath)

    def initialize_bg(self):
        self.bg_imagepath = os.path.join(self.dirname, "skins", 'background.png')
        if not os.path.exists(self.bg_imagepath):
            print "Warning: background image not exists."
            return

        self.bg_image = Image.open(self.bg_imagepath).convert('RGBA')
        self.bg_tkimage = ImageTk.PhotoImage(self.bg_image)
        self.bg = ttk.Label(self.root, image=self.bg_tkimage,)
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)

        self.bg_size = 1000
        self.bg_cell = 50
        self.bg_start = 31
        self.bg_end = self.bg_start + 19 * self.bg_cell

    def initialize_board(self):
        self.board_scale = self.size * 1.0 / self.bg_size
        self.board_cell = int(self.bg_cell * self.board_scale)
        self.board_start = int(self.bg_start * self.board_scale)
        self.board_end = int(self.bg_end * self.board_scale)
        self.board_size = (self.size, self.size)

        image = self.bg_image.resize(self.board_size)
        self.bg_tkimage = ImageTk.PhotoImage(image)
        self.bg.configure(image=self.bg_tkimage)

    def initialize_chess(self):
        chess_size = int(self.board_cell * 0.8)
        self.chess_size = (chess_size, chess_size)

        self.black_imagepath = os.path.join(self.dirname, "skins", 'black.png')
        if not os.path.exists(self.black_imagepath):
            print "Warning: black chess image not exists."
            return

        self.black_image = Image.open(self.black_imagepath).convert('RGBA').resize(self.chess_size)
        self.black_chess = ImageTk.PhotoImage(self.black_image)

        self.white_imagepath = os.path.join(self.dirname, "skins", 'white.png')
        if not os.path.exists(self.white_imagepath):
            print "Warning: white chess image not exists."
            return

        self.white_image = Image.open(self.white_imagepath).convert('RGBA').resize(self.chess_size)
        self.white_chess = ImageTk.PhotoImage(self.white_image)

        self.pos = dandan.value.AttrDict()

    def initialize_event(self):
        self.bg.bind(sequence="<Button-1>", func=self.click)
        self.root.bind(sequence="<Configure>", func=self.update)

    def initialize(self):
        self.master = gomoku.Gomoku()
        self.initialize_root()
        self.initialize_bg()
        self.initialize_board()
        self.initialize_chess()
        self.initialize_event()

    def window_size(self):
        return self.root.winfo_width(), self.root.winfo_height()

    def update(self, event=None):
        pass
        # size = self.window_size()
        # if size[0] != size[1]:
        #     length = min(*size)
        #     self.root.geometry("{}x{}".format(length, length))
        #     return
        # if size != self.before_size:
        #     self.before_size = size

        #     self.board_length = min(*size)

        #     self.board_size = (self.board_length, self.board_length)
        #     self.board_scale = self.board_length * 1.0 / self.bg_length
        #     self.board_delta = int(abs(size[0] - size[1]) / 2)
        #     self.board_cell = int(self.bg_cell * self.board_scale)
        #     self.chess_size = int(self.board_cell * 0.8)
        #     self.board_delta_x = int(self.bg_range[0] * self.board_scale)
        #     self.board_delta_y = int(self.bg_range[0] * self.board_scale)

        #     image = self.bg_image.resize(self.board_size)
        #     self.bg_tkimage = ImageTk.PhotoImage(image)
        #     self.bg.configure(image=self.bg_tkimage)

        #     for x in self.pos:
        #         for y in self.pos[x]:
        #             chess = self.pos[x][y]
        #             if not chess:
        #                 continue
        #             print chess
        #             chess.image = chess.chess_image.resize((self.chess_size, self.chess_size))
        #             chess.tkimage = ImageTk.PhotoImage(chess.image)
        #             chess.label.configure(image=chess.tkimage)
        #             chess.label.place(
        #                 x=self.board_delta_x + x * self.board_cell,
        #                 y=self.board_delta_y + y * self.board_cell,)

        # pass

    def set_chess(self, where, turn):
        x, y = where
        chess = self.pos[x][y]

        if turn == 0 and not chess:
            return
        if turn == 0:
            print chess
            # chess.label.distroy()
            return

        if turn == 1:
            chess.image = self.black_chess
        else:
            chess.image = self.white_chess

        chess.label = ttk.Label(self.root, image=chess.image)
        chess.label.place(x=self.board_start + x * self.board_cell, y=self.board_start + y * self.board_cell)
        self.root.update()

    def get_click_pos(self, event):
        prange = xrange(self.board_start, self.board_end)

        if event.x not in prange:
            return None
        if event.y not in prange:
            return None

        print self.board_cell
        x = (event.x - self.board_start) / self.board_cell
        y = (event.y - self.board_start) / self.board_cell
        print event.x, event.y, x, y

        return int(x), int(y)

    def play(self, event):
        if self.master.win():
            if self.master.turn == 1:
                tkMessageBox.showinfo("LOSE", "YOU LOSE!!!")
            else:
                tkMessageBox.showinfo("WIN", "YOU WIN!!!")
            return
        print "Click", (event.x, event.y)
        where = self.get_click_pos(event)
        if not where:
            return
        if self.master.pos[where] != 0:
            return
        self.set_chess(where, self.master.turn)
        self.master.set(where)
        if self.master.win():
            tkMessageBox.showinfo("WIN", "YOU WIN!!!")

        where = self.master.compute_pos()
        if not where:
            return
        self.set_chess(where, self.master.turn)
        self.master.set(where)
        if self.master.win():
            tkMessageBox.showinfo("LOSE", "YOU LOSE!!!")

    def click(self, event):
        print "Click", (event.x, event.y)
        self.bg.config(state="disabled")
        self.play(event)
        self.bg.config(state="enabled")

    def run(self):
        self.root.mainloop()


def main():
    ui = GomokuUI()
    ui.run()


if __name__ == '__main__':
    main()
