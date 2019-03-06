#!/usr/bin/env python3
import datetime
import operator
import threading
import time

from hermes_python.hermes import Hermes
from hermes_python.ontology import MqttOptions

import snips_common


class TimerError(Exception):
    pass


class UnknownDuration(TimerError):
    pass


class UnknownReason(TimerError):
    pass


class NoTimer(TimerError):
    pass


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


class ActionTimer(snips_common.ActionWrapper):
    reactions = {TimerError: "Désolée, je n'ai pas compris quelle durée."}

    def timer_callback(self, duration_sentence, reason):
        print("timer_callback", duration_sentence, reason)
        sentence = "Bip ! bip ! bip ! "
        if reason:
            sentence += "Vous devez " + reason
        else:
            sentence += "Le minuteur de " + duration_sentence + " est terminé."
        print("sentence", sentence)
        # FIXME nothing said with publish_start_session_notification
        # So I must start a session and snips will listen for another intent
        # or repeat the timer sentence again and again, until you say "cancel".
        # At least it serves as a reminder if you didn't hear the sentence!
        # Stop the timer with more words like "thank you"?
        self.hermes.publish_start_session_action(
            site_id=self.intent_message.site_id,
            session_init_text=sentence,
            session_init_intent_filter=['borsltd:Confirmer'],
            session_init_can_be_enqueued=False,
            session_init_send_intent_not_recognized=False,
            custom_data=None,
        )

    def action(self):
        slots = self.intent_message.slots
        duration_slot = slots.Duration.first()
        reason = slots.Reason.first().value if len(slots.Reason) else None

        duration_as_timedelta = snips_common.duration_to_timedelta(duration_slot)
        duration_sentence = snips_common.french_duration(duration_slot)
        if not duration_sentence:
            raise TimerError

        print("duration_sentence", duration_sentence)
        print("reason", reason)

        interval = duration_as_timedelta.total_seconds()
        TimerManager.start_timer(
            interval, duration_sentence, reason, self.timer_callback
        )

        if reason:
            message = "D'accord, je vous rappelle dans %s de %s" % (
                duration_sentence,
                reason,
            )
        else:
            message = "D'accord, j'ai lancé un minuteur de " + duration_sentence

        self.end_session(message)


class ActionRemainingTime(snips_common.ActionWrapper):
    reactions = {
        UnknownDuration: "Désolée, je n'ai aucun minuteur de {}.",
        UnknownReason: "Désolée, je ne sais pas quand vous devez {}.",
        NoTimer: "Désolée mais aucun minuteur n'est en cours.",
    }

    def action(self):
        slots = self.intent_message.slots
        print("slots", slots)
        try:
            duration_slot = slots.Duration.first()
        except (AttributeError, TypeError):
            duration_slot = None
        try:
            reason = slots.Reason.first().value
        except (AttributeError, TypeError):
            reason = None

        duration_sentence = (
            snips_common.french_duration(duration_slot) if duration_slot else None
        )
        print("duration_slot", duration_slot)
        print("duration_sentence", duration_sentence)
        print("reason", reason)

        remaining_time = TimerManager.remaining_time(duration_sentence, reason)
        # TODO convert extra seconds to minutes, etc.
        delta = datetime.timedelta(seconds=remaining_time)
        print('remaining_time', remaining_time, delta)
        delta_sentence = snips_common.french_timedelta(delta)
        if reason:
            sentence = "Vous devez {} dans {}.".format(reason, delta_sentence)
        elif duration_sentence:
            sentence = "Il reste {} au minuteur de {}.".format(
                delta_sentence, duration_sentence
            )
        else:
            sentence = "Le prochain minuteur va sonner dans {}.".format(delta_sentence)

        print('sentence', sentence)
        self.end_session(sentence)


if __name__ == "__main__":
    mqtt_opts = MqttOptions()

    with Hermes(mqtt_options=mqtt_opts) as hermes:
        hermes.subscribe_intent(
            "borsltd:MinuteurContextuel", ActionTimer.callback
        ).subscribe_intent("borsltd:TempsRestant", ActionRemainingTime.callback).start()

