import os
import random
import logging
import logging.config

count = 0

logger = logging.getLogger("gomoku")


class TreeNode(object):
    max_depth = 2
    max_width = 8

    def __init__(self, turn=1, depth=0):
        # logger.debug("init tree node turn %s depth %s", turn, depth)
        self.turn = turn
        self.depth = depth
        self.score = None
        self.temp = None
        self.children = None
        self.parent = None

        if turn == 1:
            self.max = max
            self.min = min
        else:
            self.max = min
            self.min = max

        self.init_logger()

    def init_logger(self):
        filename = os.path.abspath(__file__)
        dirname = os.path.dirname(filename)
        logfile = os.path.join(dirname, "gomoku.log")
        LOGGING = {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'verbose': {
                    # 'format': '[%(asctime)s] [%(name)s] [%(process)d] [%(module)s] [%(funcName)s] [%(lineno)d]  [%(levelname)s] | %(message)s'
                    'format': '[%(module)s] [%(lineno)d] [%(levelname)s] | %(message)s'
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'verbose',
                    "level": "DEBUG",
                },
                'file': {
                    'class': 'logging.FileHandler',
                    'formatter': 'verbose',
                    'filename': logfile,
                    "level": "INFO",
                },
            },
            'loggers': {
                'gomoku': {
                    'handlers': ['console', "file", ],
                    'level': "DEBUG",
                    'propagate': True,
                },
            },
        }
        logging.config.dictConfig(LOGGING)
        self.logger = logging.getLogger("gomoku")

    def analysis(self):
        if self.depth > self.max_depth:
            self.score = self.compute()
            return self.score

        self.children = []
        for var in xrange(0, self.max_width):
            node = TreeNode(turn=self.turn * -1, depth=self.depth + 1)
            node.parent = self
            score = node.analysis()
            self.children.append(node)
            if not self.temp:
                self.temp = score
            self.temp = self.max(score, self.temp)
            if not self.parent:
                continue
            if self.parent.temp and self.min(self.parent.temp, self.temp) == self.parent.temp:
                break
        self.score = self.temp
        if not self.parent:
            return self.score

        if not self.parent.temp:
            self.parent.temp = self.score
        return self.temp

    def compute(self):
        score = self.test()
        logger.debug("depth %s %s", self.depth, score)
        return score

    def test(self):
        global count
        count += 1
        return random.randint(1, 100)


if __name__ == '__main__':
    tree = TreeNode()
    logger.debug(tree.analysis())
    logger.debug(count)
    logger.debug(TreeNode.max_width ** (TreeNode.max_depth + 1))
