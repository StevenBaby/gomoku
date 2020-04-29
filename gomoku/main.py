# coding=utf-8
import sys

import gomoku
import ui


class Application(object):

    def __init__(self):
        from PySide2.QtWidgets import QApplication
        self.app = QApplication(sys.argv)
        self.window = ui.Window()

    def run(self):
        self.window.show()
        self.app.exec_()


def main():
    app = Application()
    app.run()


if __name__ == '__main__':
    main()
