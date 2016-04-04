from multiprocessing import Pool


class StreamExecutor(object):
    def __init__(self):
        self.pool = Pool()

    def map(self, predicate, iterable):
        return self.pool.map(predicate, iterable)