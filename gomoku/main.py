# coding=utf-8
import sys


def main():
    from PySide2.QtWidgets import QApplication
    from gui.window import Window
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
