import random

DURATIONS = [
    "30 minutes",
    "15 secondes",
    "3 minutes et 30 secondes",
    "3 minutes 30",
    "5 heures 37",
    "30 secondes",
    "2 minutes 46",
    "5 minutes 30",
    "8 minutes 45",
    "3 minutes 23",
    "3 minutes 10",
    "1 heure 30",
    "1 heure et 45 minutes",
    "34 minutes",
    "une heure",
    "trois minutes",
    "une heure trente",
    "vingt minutes",
    "40 minutes",
    "5 minutes",
    "trois heures",
    "10 minutes",
    "4 minutes",
    "une minute",
    "20 minutes",
]

REASONS = [
    "arrêter l'infusion",
    "boire mon thé",
    "boire le thé",
    "préchauffer le four",
    "étaler le pain",
    "mettre le pain au four",
    "sortir le pain du four",
    "téléphoner",
    "sortir le plat du congélateur",
    "aller faire les courses",
    "aller au lit",
    "aller dormir",
    "faire dodo",
    "y aller",
    "décoller",
]


TIMERS_ONLY = [
    "Mets un minuteur de [{duration}](Duration)",
    "Mets un taillemeur de [{duration}](Duration)",
    "Programme un minuteur de [{duration}](Duration)",
    "Programme un taillemeur de [{duration}](Duration)",
    "Sonne dans [{duration}](Duration)",
    "Réveille-moi dans [{duration}](Duration)",
]

TIMERS_AND_REASONS = [
    "Sonne dans [{duration}](Duration) pour [{reason}](Reason)",
    "Rappelle-moi dans [{duration}](Duration) de [{reason}](Reason)",
    "Rappelle-moi de [{reason}](Reason) dans [{duration}](Duration)",
    "Fais-moi penser à [{reason}](Reason) dans [{duration}](Duration)",
    "Je dois [{reason}](Reason) dans [{duration}](Duration)",
    "Dans [{duration}](Duration) je dois [{reason}](Reason)",
]

REMAINING_TIMERS = [
    "Dans combien de temps le minuteur va sonner ?",
    "Dans combien de temps le taillemeur va sonner ?",
    "Dans combien de temps tu vas sonner ?",
    "Il reste encore longtemps avant de sonner ?",
    "Il reste encore longtemps au minuteur ?",
    "Il reste encore longtemps au taillemeur ?",
]

REMAINING_REASONS = [
    "Combien de temps il reste pour [{reason}](Reason) ?",
    "Dans combien de temps je dois [{reason}](Reason) ?",
    "Je dois [{reason}](Reason) quand ?",
    "Je dois [{reason}](Reason) encore longtemps ?",
    "Je dois [{reason}](Reason) bientôt ?",
    "Tu me fais toujours penser à [{reason}](Reason) ?",
    "Tu n'as pas oublié de me rappeller de [{reason}](Reason) ?",
    "Tu vas sonner quand pour [{reason}](Reason) ?",
    "Dans combien de temps je dois [{reason}](Reason) ?",
    "Il reste combien de temps avant de [{reason}](Reason) ?",
    "Combien de temps avant de [{reason}](Reason) ?",
]

REMAINING_DURATIONS = [
    "Peux-tu me dire combien il reste au minuteur de [{duration}](Duration) ?",
    "Aurais-tu la gentillesse de me dire quand va sonner le taillemeur de [{duration}](Duration) ?",
    "Quand va sonner le minuteur de [{duration}](Duration) ?",
    "Quand va sonner le taillemeur [{duration}](Duration) ?",
    "Le taillemeur de [{duration}](Duration) va sonner bientôt ?",
    "Dans combien de temps va sonner le taillemeur de [{duration}](Duration) ?",
    "Où en est le taillemeur de [{duration}](Duration) ?",
    "Il reste combien au minuteur de [{duration}](Duration) ?",
    "Il reste combien de temps au minuteur de [{duration}](Duration) ?",
    "Dans combien de temps le minuteur de [{duration}](Duration) va sonner ?",
    "Combien de temps il reste au minuteur de [{duration}](Duration) ?",
]


def elision(sentence):
    return (
        sentence.replace("de [a", "[d'a")
        .replace("de [e", "[d'e")
        .replace("de [i", "[d'i")
        .replace("de [o", "[d'o")
        .replace("de [u", "[d'u")
        .replace("de [y", "[d'y")
    )


def generate_timer(fp):
    for sentence in TIMERS_ONLY:
        # Pick a single duration, assume this built-in slot is already well trained
        duration = random.choice(DURATIONS)
        fp.write(sentence.format(duration=duration) + "\n")

    for sentence in TIMERS_AND_REASONS:
        for reason in REASONS:
            # Pick a single duration, assume this built-in slot is already well trained
            duration = random.choice(DURATIONS)
            fp.write(elision(sentence.format(duration=duration, reason=reason)) + "\n")


def generate_remaining_time(fp):
    for sentence in REMAINING_TIMERS:
        fp.write(sentence + "\n")
    for sentence in REMAINING_DURATIONS:
        # Pick a single duration, assume this built-in slot is already well trained
        duration = random.choice(DURATIONS)
        fp.write(sentence.format(duration=duration) + "\n")
    for sentence in REMAINING_REASONS:
        for reason in REASONS:
            fp.write(elision(sentence.format(reason=reason)) + "\n")


if __name__ == '__main__':
    with open('intent-MinuteurContextuel.txt', 'w') as fp:
        generate_timer(fp)

    with open('intent-TempsRestant.txt', 'w') as fp:
        generate_remaining_time(fp)
