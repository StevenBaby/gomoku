# coding=utf-8


def is_valid_where(where):
    import models

    if where[0] < 0 or where[1] < 0:
        return False
    if where[0] >= models.BOARD_WIDTH:
        return False
    if where[1] >= models.BOARD_HEIGHT:
        return False
    return True
