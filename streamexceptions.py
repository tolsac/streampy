class StreamException(Exception):
    def __init__(self, message, error):
        super(Exception, self).__init__(message)
        self.error = error

    def __str__(self):
        return '{ex.message}: {ex.error}'.format(ex=self)


class StreamTypeError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)

    def __str__(self):
        return 'StreamTypeError: {ex.message}'.format(ex=self)


class StreamIndexError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)

    def __str__(self):
        return 'StreamIndexError: {ex.message}'.format(ex=self)