class StreamException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)

    def __str__(self):
        return '{ex.message}'.format(ex=self)


class StreamTypeError(StreamException):
    pass


class StreamIndexError(StreamException):
    pass
