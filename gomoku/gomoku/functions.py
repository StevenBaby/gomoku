# coding=utf-8

import tone
from tone.utils.attrdict import attrdict

from . import BOARD_WIDTH
from . import BOARD_HEIGHT
from . import CHESS_EMPTY


def is_valid_where(where):
    if where[0] < 0 or where[1] < 0:
        return False
    if where[0] >= BOARD_WIDTH:
        return False
    if where[1] >= BOARD_HEIGHT:
        return False
    return True


def get_wheres():
    wheres = {
        (x, y): 0 for x in range(BOARD_WIDTH) for y in range(BOARD_HEIGHT)
    }
    return wheres


def get_valid_wheres(board):
    wheres = {
        (x, y): 0
        for x in range(BOARD_WIDTH)
        for y in range(BOARD_HEIGHT)
        if board[(x, y)] == CHESS_EMPTY
    }
    return wheres


def get_chess_wheres(board):
    wheres = {
        (x, y): 0
        for x in range(BOARD_WIDTH)
        for y in range(BOARD_HEIGHT)
        if board[(x, y)] != CHESS_EMPTY
    }
    return wheres


def get_related_wheres(where, span=5):
    from .score import Score

    wheres = {}
    iterate = attrdict.loads(Score.params)
    for _, total in iterate.items():
        for _, direct in total.items():
            x, y = direct.step
            for step in range(0, span + 1):
                move = (where[0] + step * x, where[1] + step * y)
                if not is_valid_where(move):
                    break
                if move == where:
                    continue
                wheres[move] = True
    return wheres


def get_search_wheres(board, span=2):
    wheres = get_chess_wheres(board)
    result = {}
    for where in wheres:
        related = get_related_wheres(where, span)
        for var in related:
            if board[var] != CHESS_EMPTY:
                continue
            result[var] = True
    return result
