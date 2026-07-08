"""Frases de Trivilín, el Perro del Saxo — la personalidad del bot."""

import random

NAME = "Trivilín"

GREETING = (
    "🐶🎷 ¡Guau! Soy *Trivilín*, el Perro del Saxo — ya sé, mi instrumento es el saxo, "
    "pero para música todo se me da, así que hoy te ayudo con la *guitarra*.\n\n"
    "Aquí practicamos cambios de tonalidad, tienes el círculo de quintas a mano, "
    "y te mando tarjetas con acordes y ritmo para ensayar.\n\n"
    "¿No sabes por dónde arrancar? Prueba /plan y te armo una rutina según el "
    "tiempo que tengas. Usa /help para ver todo lo que sé hacer."
)

HELP_TEXT = (
    "🎸 *Comandos de Trivilín*\n\n"
    "/practicar — juego rápido de transposición para ratos de espera: te doy una "
    "progresión en un tono, la cambias a otro y adivinas cuál es la correcta. Le "
    "das a \"Jugar otra vez\" y sigues sin escribir nada.\n"
    "/canciones — elige una canción real del cancionero y practica transportarla.\n"
    "/letra — mira la letra completa de una canción con sus acordes.\n"
    "/circulo — la imagen del círculo de quintas, con las relativas menores y los "
    "7 acordes de la tonalidad dibujados.\n"
    "/tarjeta — una tarjeta con acordes, patrón de rasgueo y tiempo (BPM) al azar para ensayar.\n"
    "/estilo — elige un género (rock, pop, jazz, merengue...) y te armo una "
    "progresión, tono y ritmo típicos de ese estilo.\n"
    "/sesion — una rutina completa de práctica de hoy: calentamiento, cambios de acorde, "
    "técnica y una canción real con su círculo armónico y tempo.\n"
    "/plan — *esta es la que pregunta cuánto tiempo tienes hoy* y te arma una rutina "
    "a la medida (corta, normal o larga). Si no sabes por dónde arrancar, empieza aquí.\n"
    "/puntaje — tu racha y tus aciertos.\n\n"
    "🐾 Tip: /practicar es el juego rápido sin preguntas, para cuando estás esperando "
    "algo. /plan es la rutina pensada, la que sí te pregunta el tiempo disponible."
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
