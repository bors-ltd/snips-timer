#!/usr/bin/env python3
from hermes_python.hermes import Hermes
from hermes_python.ontology import MqttOptions

import snips_common


class TimerError(Exception):
    pass


class ActionTimer(snips_common.ActionWrapper):
    reactions = {TimerError: "Désolée, je n'ai pas compris."}

    def __init__(self, hermes, intent_message):
        self.hermes = hermes
        self.intent_message = intent_message

    def action(self):
        duration = self.intent_message.Duration.first()
        reason = self.intent_message.Reason.first().value

        try:
            duration_as_sentence = snips_common.french_duration(duration)
        except Exception as exc:
            raise TimerError from exc

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
        hermes.subscribe_intent("borsltd:Minuteur", ActionTimer.callback).start()
