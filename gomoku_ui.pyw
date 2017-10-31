#!/usr/bin/python2
# encoding=utf8
import os
import sys
import Tkinter as tk
import ttk
import tkMessageBox
import dandan
import traceback
from PIL import Image
from PIL import ImageTk

import gomoku


class AboutWindow(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.resizable(False, False)
        self.title("About")
        dirname = os.path.dirname(os.path.abspath(__file__))
        self.iconpath = os.path.join(dirname, "favicon.ico")
        self.iconbitmap(self.iconpath)

        label = tk.Label(self, text="This is About window")
        label.pack(side="top", fill="both", expand=True, padx=100, pady=100)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        width = self.winfo_width()
        height = self.winfo_height()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)

        self.geometry('%dx%d+%d+%d' % (width, height, x, y))


class StatusBar(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.variable = tk.StringVar()
        self.label = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                              textvariable=self.variable)
        self.reset()
        self.label.pack(fill=tk.X)

    def set_info(self, current, counter):
        string = "POS: [{:02},{:02}] CUR: {} COU: {}".format(current.where[0], current.where[1], current.score(), counter.score())
        self.variable.set(string)

    def reset(self):
        self.variable.set('Status Bar')

    def set_text(self, text):
        self.variable.set(text)


class GomokuUI(tk.Tk):

    MODE_AI = 1
    MODE_MM = 2

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.initialize()

    def initialize_config(self):

        self.config_file = os.path.join(self.dirname, "config.json")
        conf = dandan.value.get_json(self.config_file) or {}
        conf = dandan.value.AttrDict(conf)
        if not conf:
            conf.board_size = 777
            conf.show_statusbar = True
            conf.show_menubar = True

        if not conf.mode:
            conf.mode = self.MODE_AI

        values = dandan.value.AttrDict()
        values.show_menubar = tk.BooleanVar()
        values.show_menubar.set(conf.show_menubar)

        values.show_statusbar = tk.BooleanVar()
        values.show_statusbar.set(conf.show_statusbar)

        values.mode = tk.IntVar()
        values.mode.set(conf.mode)

        self.values = values
        self.conf = conf

    def save_config(self):
        dandan.value.put_json(self.conf, self.config_file)

    def initialize_root(self):
        self.statusbar_heigit = 28
        self.menubar_height = 14
        self.title("Gomoku")

        self.configure()
        self.resizable(False, False)

        self.iconpath = os.path.join(self.dirname, "favicon.ico")
        self.iconbitmap(self.iconpath)

    def initialize_bg(self):
        self.bg_imagepath = os.path.join(self.dirname, "skins", 'background.png')
        if not os.path.exists(self.bg_imagepath):
            # print "Warning: background image not exists."
            return

        self.bg_image = Image.open(self.bg_imagepath).convert('RGBA')
        self.bg_tkimage = ImageTk.PhotoImage(self.bg_image)
        self.bg = ttk.Label(self, image=self.bg_tkimage,)
        self.bg.place(x=0, y=0)

        self.bg_size = 1000
        self.bg_cell = 50
        self.bg_start = 31
        self.bg_end = self.bg_start + 19 * self.bg_cell

    def initialize_board(self):
        self.board_scale = self.conf.board_size * 1.0 / self.bg_size
        self.board_cell = int(self.bg_cell * self.board_scale)
        self.board_start = int(self.bg_start * self.board_scale)
        self.board_end = int(self.bg_end * self.board_scale)
        self.board_size = (self.conf.board_size, self.conf.board_size)

        image = self.bg_image.resize(self.board_size)
        self.bg_tkimage = ImageTk.PhotoImage(image)
        self.bg.configure(image=self.bg_tkimage)

    def initialize_chess(self):
        chess_size = int(self.board_cell * 0.8)
        self.chess_size = (chess_size, chess_size)

        self.black_imagepath = os.path.join(self.dirname, "skins", 'black.png')
        if not os.path.exists(self.black_imagepath):
            # print "Warning: black chess image not exists."
            return

        self.black_image = Image.open(self.black_imagepath).convert('RGBA').resize(self.chess_size)
        self.black_chess = ImageTk.PhotoImage(self.black_image)

        self.white_imagepath = os.path.join(self.dirname, "skins", 'white.png')
        if not os.path.exists(self.white_imagepath):
            # print "Warning: white chess image not exists."
            return

        self.white_image = Image.open(self.white_imagepath).convert('RGBA').resize(self.chess_size)
        self.white_chess = ImageTk.PhotoImage(self.white_image)

        self.pos = dandan.value.AttrDict()

    def initialize_event(self):
        self.bind(sequence="<Button-1>", func=self.click)
        self.bind(sequence="<Button-2>", func=self.middle_click)
        self.bind(sequence="<Button-3>", func=self.right_click)
        self.bind(sequence="<Motion>", func=self.mouse_motion)
        # self.bind(sequence="<Configure>", func=self.configure)

        self.motion = None

    def initialize_menu(self):
        menu = tk.Menu(self, tearoff=0)
        context_menu = tk.Menu(menu, tearoff=0)
        empty_menu = tk.Menu(menu, tearoff=0)

        game_menu = tk.Menu(menu, tearoff=0)
        view_menu = tk.Menu(menu, tearoff=0)
        help_menu = tk.Menu(menu, tearoff=0)
        mode_menu = tk.Menu(menu, tearoff=0)

        menu.add_cascade(label="Game", menu=game_menu)
        menu.add_cascade(label="View", menu=view_menu)
        menu.add_cascade(label="Help", menu=help_menu)

        context_menu.add_command(label="Back", command=self.back)
        context_menu.add_command(label="Hint", command=lambda: (self.compute_pos(), self.compute_pos()) if self.conf.mode == self.MODE_AI else self.compute_pos())
        context_menu.add_command(label="Reset", command=self.reset)
        context_menu.add_separator()
        context_menu.add_cascade(label="Mode", menu=mode_menu)
        context_menu.add_cascade(label="View", menu=view_menu)
        context_menu.add_separator()
        context_menu.add_command(label="Exit", command=lambda: sys.exit())

        game_menu.add_command(label="Back", command=self.back)
        game_menu.add_command(label="Hint", command=lambda: (self.compute_pos(), self.compute_pos()) if self.conf.mode == self.MODE_AI else self.compute_pos())
        game_menu.add_command(label="Reset", command=self.reset)
        game_menu.add_cascade(label="Mode", menu=mode_menu)
        game_menu.add_command(label="Exit", command=lambda: sys.exit())

        view_menu.add_checkbutton(
            label="Menu",
            onvalue=True,
            offvalue=False,
            variable=self.values.show_menubar,
            command=self.toggle_menubar)
        view_menu.add_checkbutton(
            label="StatusBar",
            onvalue=True,
            offvalue=False,
            variable=self.values.show_statusbar,
            command=self.toggle_statusbar)

        mode_menu.add_radiobutton(label="AI", value=self.MODE_AI, variable=self.values.mode, command=self.toggle_mode)
        mode_menu.add_radiobutton(label="MM", value=self.MODE_MM, variable=self.values.mode, command=self.toggle_mode)

        help_menu.add_command(label="About", command=lambda: AboutWindow())

        self.empty_menu = empty_menu
        self.view_menu = view_menu
        self.game_menu = game_menu
        self.help_menu = help_menu
        self.mode_menu = mode_menu

        self.menu = menu
        self.context_menu = context_menu

        if self.conf.show_menubar:
            self.config(menu=menu)

    def initialize_statusbar(self):
        self.statusbar = StatusBar(self)
        if self.conf.show_statusbar:
            self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def initialize(self):
        self.gomoku = gomoku.Gomoku()
        self.logger = self.gomoku.logger
        self.filepath = os.path.abspath(__file__)
        self.dirname = os.path.dirname(self.filepath)

        self.initialize_config()
        self.initialize_root()
        self.initialize_bg()
        self.initialize_board()
        self.initialize_chess()
        self.initialize_menu()
        self.initialize_statusbar()
        self.initialize_event()

    def configure(self, event=None):
        height = self.conf.board_size
        if self.conf.show_menubar:
            height += self.menubar_height
        if self.conf.show_statusbar:
            height += self.statusbar_heigit

        self.logger.debug("window height %s", height)
        self.geometry("{}x{}".format(self.conf.board_size, height))

    def reset(self):
        self.logger.info("Reset game")
        self.gomoku.reset()

        for x in self.pos:
            for y in self.pos[x]:
                chess = self.pos[x][y]
                if not chess:
                    continue
                self.set_chess((x, y), 0)
                self.logger.debug(chess)

    def toggle_statusbar(self):
        self.logger.debug("toggle_statusbar")
        if self.values.show_statusbar.get():
            self.conf.show_statusbar = True
            self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        else:
            self.conf.show_statusbar = False
            self.statusbar.pack_forget()
        self.save_config()
        self.configure()

    def toggle_menubar(self):
        self.logger.debug("toggle_menubar")
        if self.values.show_menubar.get():
            self.config(menu=self.menu)
            self.conf.show_menubar = True
        else:
            self.conf.show_menubar = False
            self.config(menu=self.empty_menu)
        self.save_config()
        self.configure()

    def toggle_mode(self):
        self.conf.mode = self.values.mode.get()
        self.save_config()

    def set_chess(self, where, turn):
        x, y = where
        chess = self.pos[x][y]

        if turn == 0 and not chess:
            return
        if turn == 0:
            chess.label.place_forget()
            return

        if turn == 1:
            chess.image = self.black_chess
        else:
            chess.image = self.white_chess

        chess.label = ttk.Label(self, image=chess.image)
        chess.label.place(x=self.board_start + x * self.board_cell, y=self.board_start + y * self.board_cell)
        self.update()

    def get_click_pos(self, event):
        # self.logger.debug("Bg root position %s, %s", self.bg.winfo_rootx(), self.bg.winfo_rooty())
        xx = event.x_root - self.bg.winfo_rootx()
        yy = event.y_root - self.bg.winfo_rooty()
        # self.logger.debug("Click position %s, %s", xx, yy)

        if xx <= self.board_start:
            return None
        if xx >= self.board_end:
            return None
        if yy <= self.board_start:
            return None
        if yy >= self.board_end:
            return None

        x = (xx - self.board_start) / self.board_cell
        y = (yy - self.board_start) / self.board_cell
        where = (int(x), int(y))
        # self.logger.debug("Where position %s", where)
        return where

    def show_win_message(self):
        if self.conf.mode == self.MODE_AI:
            if self.gomoku.turn == 1:
                tkMessageBox.showinfo("LOSE", "YOU LOSE!!!")
            else:
                tkMessageBox.showinfo("WIN", "YOU WIN!!!")
            return
        if self.conf.mode == self.MODE_MM:
            if self.gomoku.turn == 1:
                tkMessageBox.showinfo("WIN", "WHITE WIN!!!")
            else:
                tkMessageBox.showinfo("WIN", "BLACK WIN!!!")
            return

    def compute_pos(self):
        self.statusbar.set_text("Thinking...")
        self.bg.state(["disabled"])
        self.update()

        self.update()
        where = self.gomoku.compute_pos()
        self.statusbar.reset()
        if not where:
            self.bg.state(["!disabled"])
            self.update()
            return
        self.set_chess(where, self.gomoku.turn)
        self.gomoku.set(where)
        if self.gomoku.win():
            self.show_win_message()
        self.bg.state(["!disabled"])
        self.update()

    def back(self):
        where = self.gomoku.back()
        if not where:
            tkMessageBox.showinfo("WARNING", "NO MORE STEP TO BACK!!!")
        self.set_chess(where, 0)

        if self.conf.mode == self.MODE_AI:
            where = self.gomoku.back()
            if not where:
                return
            self.set_chess(where, 0)

    def play(self, where):
        if self.gomoku.win():
            self.show_win_message()
            return
        if self.gomoku.pos[where] != 0:
            return
        self.set_chess(where, self.gomoku.turn)
        self.gomoku.set(where)
        if self.gomoku.win():
            self.show_win_message()

        if self.conf.mode == self.MODE_AI:
            self.compute_pos()

    def click(self, event):
        if "disabled" in self.bg.state():
            return
        self.infomation()
        self.logger.info("Click root position %s, %s", event.x_root, event.y_root)
        where = self.get_click_pos(event)
        if not where:
            return
        try:
            self.play(where)
        except Exception:
            self.logger.fatal(traceback.format_exc())

    def middle_click(self, event):
        if not self.conf.show_statusbar:
            return
        where = self.get_click_pos(event)
        if not where:
            return
        self.logger.debug("Middle click %s", where)
        current, counter = self.gomoku.info(where)
        self.logger.debug("current score %s", current.score())
        self.logger.debug("counter score %s", counter.score())
        self.statusbar.set_info(current, counter)

    def right_click(self, event):
        self.logger.debug("Right click %s", event)
        self.context_menu.post(event.x_root, event.y_root)

    def mouse_motion(self, event):
        # self.logger.debug("Mouse motion %s, %s", event.x_root, event.y_root)
        if not self.conf.show_statusbar:
            return
        if "disabled" in self.bg.state():
            return
        where = self.get_click_pos(event)
        if not where:
            return
        if self.motion == where:
            return
        if self.gomoku.pos[where] != 0:
            self.statusbar.reset()
            return
        self.motion = where
        self.logger.debug("Mouse where %s", where)
        current, counter = self.gomoku.info(where)
        self.logger.debug("current score %s", current.score())
        self.logger.debug("counter score %s", counter.score())
        self.statusbar.set_info(current, counter)

    def infomation(self):
        logger = self.logger
        logger.debug("menu height %s", self.menu.winfo_height())


def main():
    ui = GomokuUI()
    ui.mainloop()


if __name__ == '__main__':
    main()
