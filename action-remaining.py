#!/usr/bin/env python3
import datetime
import operator
import threading
import time

from hermes_python.hermes import Hermes
from hermes_python.ontology import MqttOptions
import snips_common

from exceptions import NoTimer, UnknownDuration, UnknownReason
from timers import TimerManager


class ActionRemainingTime(snips_common.ActionWrapper):
    intent = "borsltd:TempsRestant"
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
    ActionRemainingTime.main()
