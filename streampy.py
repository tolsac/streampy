from streamexecutor import StreamExecutor
from compatibility import _mapper, _filter, _chainer, _ranger, _islicer
import functools


class StreamType(object):
    SEQUENTIAL, PARALLEL = range(2)


class StreamMapper(object):
    THREAD, PROCESS = range(2)


class Stream(object):
    def __init__(self, *_iterable):
        self.type = StreamType.SEQUENTIAL
        self.mapping = StreamMapper.PROCESS
        self.executor = None
        self.file_ref = None
        if len(_iterable) == 1:
            if _iterable[0] is None:
                raise TypeError("Argument is None")
            self.iterable = iter(_iterable[0])
        elif len(_iterable) > 1:
            raise TypeError("Takes only one argument")
        else:
            self.iterable = iter([])

    def __iter__(self):
        return self.iterable

    def __len__(self):
        return sum(1 for item in self.iterable)

    def __getitem__(self, position):
        for idx, it in enumerate(self.iterable):
            if idx == position:
                return it
        raise IndexError("Stream index out of range")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __del__(self):
        if self.file_ref:
            self.file_ref.close()

    def next(self):
        return next(self.iterable)

    def parallel(self, **kwargs):
        self.type = StreamType.PARALLEL
        if self.executor is None:
            self.executor = StreamExecutor(**kwargs)
        return self

    def sequential(self):
        self.type = StreamType.SEQUENTIAL
        return self

    def distinct(self):
        distincted = []
        for it in self.iterable:
            if it not in distincted:
                distincted.append(it)
        return self.__class__(distincted)

    def size(self):
        return self.__len__()

    def list(self):
        return list(self.iterable)

    def map(self, predicate):
        if self.type == StreamType.SEQUENTIAL:
            return self.__class__(_mapper(predicate, self.iterable))
        else:
            return self.__class__(self.executor.map(predicate, self.iterable))

    def foreach(self, func):
        for it in self.iterable:
            func(it)

    def skip(self, count):
        for i in _ranger(count):
            try:
                next(self.iterable)
            except StopIteration:
                return self.__class__()
        return self.__class__(self.iterable)

    def chain(self, _iterable):
        return self.__class__(_chainer(self.iterable, _iterable))

    def filter(self, predicate):
        return self.__class__(_filter(predicate, self.iterable))

    def exclude(self, predicate):
        return self.__class__((it for it in self.iterable if not predicate(it)))

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
        return self.__class__(_peek(self.iterable, predicate))

    def sort(self, **kwargs):
        _cmp = kwargs.pop('cmp', None)
        _key = kwargs.pop('key', None)
        if _cmp:
            kwargs['key'] = functools.cmp_to_key(_cmp)
        if _key:
            kwargs['key'] = _key
        return self.__class__(sorted(self.iterable, **kwargs))

    def limit(self, count):
        def _limit(iterable, _count):
            for _ in _ranger(_count):
                yield next(iterable)
        return self.__class__(_limit(self.iterable, count))

    def chunk(self, chunk_size):
        def _chunker(iterable, _chunk_size):
            while True:
                chunk = list(_islicer(iterable, _chunk_size))
                if not chunk:
                    return
                yield chunk
        return self.__class__(_chunker(self.iterable, chunk_size))

    def substream(self, start, end):
        def _substream(iterable, _start, _end):
            counter = 0
            for it in iterable:
                if _start <= counter < _end:
                    yield it
                counter += 1
        if 0 <= start < end and end >= 0:
            return self.__class__(_substream(self.iterable, start, end))
        elif start == end:
            return self.__class__([])
        else:
            raise IndexError("Stream index out of range")

    def max(self):
        return max(self)

    def min(self):
        return min(self)

    def any(self, predicate):
        if predicate is None:
            iterator = iter(self.iterable)
        else:
            iterator = self.map(predicate)
        return any(iterator)

    def all(self, predicate):
        if predicate is None:
            iterator = iter(self.iterable)
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

    def reverse(self):
        return self.__class__(reversed(list(self.iterable)))

    def collect(self, collector):
        return collector.collect(iterable=self.iterable)

    @staticmethod
    def file(*args):
        if isinstance(args[0], file):
            return Stream((line for line in args[0]))
        elif isinstance(args[0], str):
            _f = open(*args)
            stream = Stream.file(_f)
            stream.file_ref = _f
            ''' be aware that the file will never be closed '''
            return stream

    @staticmethod
    def range(*args):
        return Stream(_ranger(*args))

