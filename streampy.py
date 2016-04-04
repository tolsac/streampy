from streamexceptions import StreamException
from streamexecutor import StreamExecutor
import itertools

try:
    _ranger = xrange
except NameError:
    _ranger = range


class StreamType(object):
    SEQUENTIAL, PARALLEL = range(2)


class Stream(object):
    def __init__(self, *_iterable):
        self.type = StreamType.SEQUENTIAL
        self.executor = None

        if len(_iterable) == 1:
            if _iterable[0] is None:
                raise StreamException("StreamTypeError", "Argument is None")
            self.iterable = iter(_iterable[0])
        elif len(_iterable) > 1:
            raise StreamException("StreamTypeError", "Takes only one argument")
        else:
            self.iterable = iter([])

    def __iter__(self):
        return self

    def __len__(self):
        return sum(1 for item in self.iterable)

    def __getitem__(self, position):
        i = 0
        if i <= 0:
            for it in self.iterable:
                if i == position:
                    return it
                i += 1
        raise StreamException("StreamIndexError", "Stream index out of range")

    def next(self):
        return self.iterable.next()

    @staticmethod
    def range(size):
        return Stream(_ranger(size))

    def parallel(self):
        self.type = StreamType.PARALLEL
        if self.executor is None:
            self.executor = StreamExecutor()
        return self

    def distinct(self):
        distincted = []
        for it in self.iterable:
            if it not in distincted:
                distincted.append(it)
        return self.__class__(distincted)

    def sequential(self):
        self.type = StreamType.SEQUENTIAL
        return self

    def size(self):
        return self.__len__()

    def list(self):
        return list(self.iterable)

    def map(self, predicate):
        if self.type == StreamType.SEQUENTIAL:
            return self.__class__(iter(itertools.imap(predicate, self.iterable)))
        else:
            return self.__class__(iter(self.executor.map(predicate, self.iterable)))

    def chain(self, _iterable):
        return self.__class__(iter(itertools.chain(self.iterable, _iterable)))

    def filter(self, predicate):
        return self.__class__(iter(list(itertools.ifilter(predicate, self.iterable))))

    def reduce(self, predicate, initializer=None):
        if initializer is None:
            value = next(self.iterable)
        else:
            value = initializer
        for element in self.iterable:
            value = predicate(value, element)
        return value

    def peek(self, predicate):
        def _peek(iterable, fc):
            for it in iterable:
                fc(it)
                yield it
        return self.__class__(_peek(self, predicate))

    def sort(self, **kwargs):
        return self.__class__(sorted(self.iterable, **kwargs))

    def limit(self, count):
        def _limit(iterable, _count):
            for _ in _ranger(_count):
                yield next(iterable)
        return self.__class__(_limit(self, count))

    def substream(self, start, end):
        pass

    def max(self):
        return max(self)

    def min(self):
        return min(self)

    def any(self, predicate):
        if predicate is None:
            iterator = iter(self)
        else:
            iterator = self.map(predicate)
        return any(iterator)

    def all(self, predicate):
        if predicate is None:
            iterator = iter(self)
        else:
            iterator = self.map(predicate)
        return all(iterator)

    def first(self, predicate=None):
        if predicate is None:
            return next(self.iterable)
        else:
            return self.filter(predicate).first()

    def last(self, predicate=None):
        if predicate is None:
            last_it = None
            for it in self.iterable:
                last_it = it
            return last_it
        else:
            return self.filter(predicate).last()


