"""

"""
import itertools
from typing import Iterable, List


def _chunk(iterable: Iterable, chunk_size: int) -> Iterable:
    if chunk_size < 1:
        raise ValueError('chunk_size must be at least one')

    while batch := list(itertools.islice(iterable, chunk_size)):
        yield batch


def _compact(iterable: Iterable) -> Iterable:
    return filter(lambda x: x is not None, iterable)


def _chainer(*iterable: Iterable) -> Iterable:
    return itertools.chain(*iterable)
