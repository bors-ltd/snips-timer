#!/usr/bin/env python3
import threading
import time

from hermes_python.hermes import Hermes
from hermes_python.ontology import MqttOptions

import snips_common


class TimerError(Exception):
    pass


class ActionTimer(snips_common.ActionWrapper):
    reactions = {TimerError: "Désolée, je n'ai pas compris quelle durée."}

    def timer_callback(self, duration, reason):
        print("timer_callback", duration, reason)
        sentence = "Bip ! bip ! bip ! "
        if reason:
            sentence += "Vous devez " + reason
        else:
            sentence += "Le minuteur de " + duration + " est terminé."
        print("timer sentence", sentence)
        # FIXME nothing said with publish_start_session_notification
        # So I must start a session and snips with listen for another intent
        # or repeat the timer sentence again and again, until you say "cancel".
        # At least it serves as a reminder if you didn't hear the sentence!
        # Stop the timer with more words like "thank you"?
        self.hermes.publish_start_session_action(
            site_id=self.intent_message.site_id,
            session_init_text=sentence,
            session_init_intent_filter=[],
            session_init_can_be_enqueued=False,
            session_init_send_intent_not_recognized=False,
            custom_data=None,
        )

    def action(self):
        slots = self.intent_message.slots
        duration = slots.Duration.first()
        reason = slots.Reason.first().value if len(slots.Reason) else None

        duration_as_timedelta = snips_common.duration_to_timedelta(duration)
        duration_as_sentence = snips_common.french_duration(duration)
        if not duration_as_sentence:
            raise TimerError

        interval = duration_as_timedelta.total_seconds()
        timer = threading.Timer(
            interval, self.timer_callback, args=(duration_as_sentence, reason)
        )
        timer.start()

        if reason:
            message = "D'accord, je vous rappelle dans %s de %s" % (
                duration_as_sentence,
                reason,
            )
        else:
            message = "D'accord, j'ai lancé un minuteur de " + duration_as_sentence

        self.end_session(message)


if __name__ == "__main__":
    mqtt_opts = MqttOptions()

    with Hermes(mqtt_options=mqtt_opts) as hermes:
        hermes.subscribe_intent(
            "borsltd:MinuteurContextuel", ActionTimer.callback
        ).start()
