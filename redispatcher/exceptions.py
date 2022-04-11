class RedispatcherException(Exception):
    ...


class UndefinedQueue(RedispatcherException):
    ...


class UndefinedMessage(RedispatcherException):
    ...
