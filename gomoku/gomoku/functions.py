# coding=utf-8


def is_valid_where(where):
    from . import BOARD_WIDTH
    from . import BOARD_HEIGHT

    if where[0] < 0 or where[1] < 0:
        return False
    if where[0] >= BOARD_WIDTH:
        return False
    if where[1] >= BOARD_HEIGHT:
        return False
    return True
