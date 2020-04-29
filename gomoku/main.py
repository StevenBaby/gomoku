# coding=utf-8
import os
import sys

import ui
import config


class Gomoku():

    def __init__(self):
        self.app = self.load_app()
        self.window = ui.Window()

    def load_app(self):
        from PySide2.QtWidgets import QApplication
        from PySide2 import QtCore
        app = QApplication(sys.argv)
        return app

    def run(self):
        self.window.show()
        self.app.exec_()


def main():
    gomoku = Gomoku()
    gomoku.run()


if __name__ == '__main__':
    main()
