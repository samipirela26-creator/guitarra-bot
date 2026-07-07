"""Frases de Trivilín, el Perro del Saxo — la personalidad del bot."""

import random

NAME = "Trivilín"

GREETING = (
    "🐶🎷 ¡Guau! Soy *Trivilín*, el Perro del Saxo — ya sé, mi instrumento es el saxo, "
    "pero para música todo se me da, así que hoy te ayudo con la *guitarra*.\n\n"
    "Aquí practicamos cambios de tonalidad, tienes el círculo de quintas a mano, "
    "y te mando tarjetas con acordes y ritmo para ensayar.\n\n"
    "Usa /help para ver todo lo que sé hacer."
)

HELP_TEXT = (
    "🎸 *Comandos de Trivilín*\n\n"
    "/practicar — juego de transposición: te doy una progresión en un tono, "
    "la cambias a otro tono y adivinas cuál es la correcta.\n"
    "/canciones — elige una canción real del cancionero y practica transportarla.\n"
    "/circulo — la imagen del círculo de quintas, con las relativas menores.\n"
    "/tarjeta — una tarjeta con acordes, patrón de rasgueo y tiempo (BPM) para ensayar.\n"
    "/sesion — una rutina completa de práctica de hoy: calentamiento, cambios de acorde, "
    "técnica y una canción real con su círculo armónico y tempo.\n"
    "/puntaje — tu racha y tus aciertos.\n"
)

WARMUP_EXERCISES = [
    "Cromático 1-2-3-4: un dedo por traste, en las 6 cuerdas, subiendo y bajando el mástil despacio.",
    "Arpegios abiertos: recorre nota por nota los acordes C, Am, F y G antes de rasguear nada.",
    "20 cambios lentos entre dos acordes abiertos cualquiera, mirando el mástil, sin apurar.",
    "Estiramiento de dedos + escala mayor en una sola cuerda, subiendo y bajando.",
]

TECHNIQUE_TIPS = [
    "Rasgueo con metrónomo a 60 BPM. Solo sube 5 BPM cuando salga limpio 3 veces seguidas.",
    "Silencia las cuerdas con la palma (palm mute) mientras rasgueas un acorde abierto.",
    "Toca la progresión de la canción sin mirar el mástil, solo guiándote por el oído.",
    "Alterna púa arriba/abajo bien parejo, sin acentos, a tempo lento y constante.",
]

SESSION_INTRO = (
    "🐶🎷 *Sesión de práctica de hoy* (≈25-30 min)\n\n"
    "Ni con el saxo me salto el calentamiento — vamos por partes:"
)

CORRECT_LINES = [
    "¡Guau, eso es! 🎸✅",
    "¡Así se toca! Directo al hueso. 🦴🎶",
    "Perfecto, ni un ladrido de más.",
    "Eso mismo — buen oído.",
]

INCORRECT_LINES = [
    "Casi... pero no. 🐾",
    "Ese no era, pero no te rindas.",
    "Fallaste, pero hasta yo desafino a veces.",
    "No era esa — mira la correcta y sigue.",
]


def correct_line(rng: random.Random | None = None) -> str:
    rng = rng or random
    return rng.choice(CORRECT_LINES)


def incorrect_line(rng: random.Random | None = None) -> str:
    rng = rng or random
    return rng.choice(INCORRECT_LINES)
