import itertools

_islicer = itertools.islice

try:
    _ranger = xrange
except NameError:
    _ranger = range

try:
    _filter = itertools.ifilter
except (ImportError, AttributeError):
    _filter = filter

try:
    _mapper = itertools.imap
except (ImportError, AttributeError):
    _mapper = map


def _chainer(*iterables):
    for it in iterables:
        for element in it:
            yield element
