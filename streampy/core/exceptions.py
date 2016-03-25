class StreamException(Exception):
    def __init__(self, message, error):
        super(Exception, self).__init__(message)
        self.error = error

    def __str__(self):
        return '{ex.message}: {ex.error}'.format(ex=self)