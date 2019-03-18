#!/usr/bin/env python3
import operator
import threading
import time

from exceptions import UnknownDuration, UnknownReason, NoTimer


class Timer(threading.Thread):
    """Simple timer because threading.Timer cannot report the remaining time."""

    def __init__(self, interval, name, target, args):
        super().__init__(target=target, name=name, args=args)
        self.interval = interval
        self.started_at = None
        self.cancelled = False

    def start(self):
        print('Timer.start', self.name)
        self.started_at = time.time()
        super().start()

    def run(self):
        print('Timer.run', self.name)
        time.sleep(self.interval)
        # Even if cancelled, return to the TimerManager so it can clean up
        super().run()

    def cancel(self):
        print('Timer.cancel', self.name)
        self.cancelled = True

    def remaining_time(self):
        print('Timer.remaining_time', self.name)
        return int(self.started_at + self.interval - time.time())


class TimerManager:
    """Start and manage timers identified by their reason or duration."""

    durations = {}
    reasons = {}

    @classmethod
    def start_timer(cls, interval, duration_sentence, reason, callback):
        timer = Timer(
            interval,
            name=reason or duration_sentence,
            target=cls.callback,
            args=(duration_sentence, reason, callback),
        )
        cls.durations[duration_sentence] = timer
        if reason:
            cls.reasons[reason] = timer
        timer.start()

    @classmethod
    def _get_timer(cls, duration_sentence=None, reason=None):
        if duration_sentence:
            try:
                return cls.durations[duration_sentence]
            except KeyError:
                raise UnknownDuration(duration_sentence)
        if reason:
            try:
                return cls.reasons[reason]
            except KeyError:
                raise UnknownReason(reason)
        # Else find the timer ending first
        by_remaining = sorted(
            cls.durations.values(), key=operator.methodcaller('remaining_time')
        )
        try:
            return by_remaining[0]
        except IndexError:
            raise NoTimer

    @classmethod
    def cancel(cls, duration_sentence, reason):
        print("TimerManager.remaining_time", duration_sentence, reason)
        timer = cls._get_timer(duration_sentence, reason)
        return timer.cancel()

    @classmethod
    def remaining_time(cls, duration_sentence=None, reason=None):
        print("TimerManager.remaining_time", duration_sentence, reason)
        timer = cls._get_timer(duration_sentence, reason)
        return timer.remaining_time()

    @classmethod
    def callback(cls, duration_sentence, reason, callback):
        print("TimerManager.callback", duration_sentence, reason)
        timer = cls._get_timer(duration_sentence, reason)
        del cls.durations[duration_sentence]  # Should not fail
        cls.reasons.pop(reason, None)
        if not timer.cancelled:
            callback(duration_sentence, reason)
