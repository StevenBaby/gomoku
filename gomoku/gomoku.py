# coding=utf-8
import tone
import functions
import models

logger = tone.utils.get_logger()


class Gomoku(object):

    def __init__(self):
        self.reset()

    def move(self, where):
        node = self.head.move(where)
        if not isinstance(node, models.Node):
            return node

        self.head = node
        if self.head.is_finished():
            return models.MOVE_STATE_WIN
        return models.MOVE_STATE_NONE

    def reset(self):
        self.root = models.Node()
        self.head = self.root

    def undo(self):
        if self.head == self.root:
            return None
        self.head = self.head.parent

    def save(self, filename):
        import pickle
        with open(filename, 'wb') as file:
            pickle.dump(self, file)

    def load(self, filename):
        import pickle
        try:
            with open(filename, 'rb') as file:
                model = pickle.load(file)
        except Exception:
            return False
        if not isinstance(model, Gomoku):
            return False

        self.root = model.root
        self.head = model.head

        return True
