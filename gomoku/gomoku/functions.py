# coding=utf-8

from . import BOARD_WIDTH
from . import BOARD_HEIGHT


def get_wheres():
    wheres = {
        (x, y): 0 for x in range(BOARD_WIDTH) for y in range(BOARD_HEIGHT)
    }
    return wheres


def is_valid_where(where):
    if where[0] < 0 or where[1] < 0:
        return False
    if where[0] >= BOARD_WIDTH:
        return False
    if where[1] >= BOARD_HEIGHT:
        return False
    return True
