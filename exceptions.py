class TimerError(Exception):
    pass


class UnknownDuration(TimerError):
    pass


class UnknownReason(TimerError):
    pass


class NoTimer(TimerError):
    pass
