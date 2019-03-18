#!/usr/bin/env python3
import snips_common

from exceptions import TimerError
from timers import TimerManager


class ActionTimer(snips_common.ActionWrapper):
    intent = "borsltd:MinuteurContextuel"
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

        duration_as_timedelta = snips_common.duration_to_timedelta(
            duration_slot)
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


if __name__ == "__main__":
    ActionTimer.main()
