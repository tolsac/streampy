import multiprocessing
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool


class StreamExecutor(object):
    def __init__(self, **kwargs):
        _thread = kwargs.get('thread', False)
        _process = kwargs.get('process', False)

        if _thread:
            self.pool = ThreadPool(multiprocessing.cpu_count() if _thread is True else _thread)
        elif _process:
            self.pool = Pool(multiprocessing.cpu_count() if _process is True else _process)
        else:
            self.pool = Pool()

    def map(self, predicate, iterable):
        return self.pool.map(predicate, iterable)
