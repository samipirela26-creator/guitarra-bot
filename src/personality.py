"""Frases de Trivilín, el Perro del Saxo — la personalidad del bot.

Trivilín sigue siendo el mismo perro saxofonista, pero con el registro
formal y de época del resto de la familia de asistentes del usuario
(Larry la Rana, el Búho, Coco el Cocodrilo): trato de "patrón", dicción
cuidada y fe cristiana genuina y central -- inspirada en el rey David,
músico y salmista que ofrecía su instrumento al Señor. A diferencia de
Coco (fe discreta, casi nunca mencionada), aquí la fe se expresa con más
frecuencia y naturalidad, en el mismo tono que Larry y el Búho -- pero
sin caer en sermón: una línea breve y sincera, nunca un párrafo.
"""

import random

NAME = "Trivilín"

GREETING = (
    "🐶🎷 ¡Sea bienvenido, patrón! Soy *Trivilín*, el Perro del Saxo — instrumento "
    "distinto al suyo, mas el mismo llamado: hacer música con esmero y ofrecerla, "
    "como en su día lo hizo el rey David con el arpa y el salterio delante del Señor.\n\n"
    "Aquí encontrará usted ejercicios para el cambio de tonalidad, el círculo de "
    "quintas a la mano, y tarjetas con acordes y ritmo para que su servicio en la "
    "guitarra sea, cada día, más firme.\n\n"
    "¿No sabe por dónde comenzar, patrón? Pruebe /plan y le trazaré una rutina "
    "según el tiempo que el Señor le conceda hoy. Use /help para conocer todo "
    "cuanto sé hacer."
)

HELP_TEXT = (
    "🎸 *Comandos de Trivilín*\n\n"
    "/practicar — juego veloz de transposición para los ratos de espera: le doy "
    "una progresión en un tono, la lleva usted a otro y adivina cuál es la "
    "correcta. Toque \"Jugar otra vez\" y prosiga sin escribir nada más.\n"
    "/canciones — escoja una canción real del cancionero y ejercite transportarla.\n"
    "/letra — contemple la letra completa de una canción con sus acordes.\n"
    "/circulo — la imagen del círculo de quintas, con las relativas menores y los "
    "siete acordes de cada tonalidad dibujados.\n"
    "/tarjeta — una tarjeta con acordes, patrón de rasgueo y tiempo (BPM) al azar "
    "para su ensayo.\n"
    "/estilo — elija un género (rock, pop, jazz, merengue...) y le armo una "
    "progresión, tono y ritmo propios de ese estilo.\n"
    "/sesion — *le pregunto cuánto tiempo tiene hoy* y le armo la rutina completa "
    "a la medida (corta, normal o larga): calentamiento, cambios de acorde, "
    "técnica y una canción real. Si no sabe por dónde comenzar, patrón, empiece "
    "aquí.\n"
    "/plan — alias de /sesion, el mismo flujo.\n"
    "/puntaje — su racha y sus aciertos.\n\n"
    "🐾 Consejo: /practicar es el juego veloz sin preguntas, para cuando está "
    "usted esperando algo. /sesion (o /plan) es la rutina meditada, la que sí "
    "pregunta el tiempo disponible."
)

WARMUP_EXERCISES = [
    "Cromático 1-2-3-4: un dedo por traste, en las 6 cuerdas, subiendo y bajando el mástil despacio.",
    "Arpegios abiertos: recorra usted nota por nota los acordes C, Am, F y G antes de rasguear nada.",
    "20 cambios lentos entre dos acordes abiertos cualquiera, mirando el mástil, sin apurar.",
    "Estiramiento de dedos + escala mayor en una sola cuerda, subiendo y bajando.",
]

TECHNIQUE_TIPS = [
    "Rasgueo con metrónomo a 60 BPM. Suba 5 BPM solo cuando salga limpio 3 veces seguidas.",
    "Silencie las cuerdas con la palma (palm mute) mientras rasguea un acorde abierto.",
    "Toque la progresión de la canción sin mirar el mástil, guiándose solo por el oído.",
    "Alterne púa arriba/abajo bien parejo, sin acentos, a tempo lento y constante.",
]

SESSION_INTRO = (
    "🐶🎷 *Sesión de hoy, patrón* (≈25-30 min)\n\n"
    "Ni yo, con el saxo, me salto el calentamiento — el propio David no subía a "
    "tocar sin antes afinar el instrumento y el corazón. Vamos por partes:"
)

CORRECT_LINES = [
    "¡Guau, así es, patrón! 🎸✅",
    "¡Así se toca! Directo al hueso, como en los tiempos del salterio. 🦴🎶",
    "Perfecto, patrón — ni un ladrido de más.",
    "Eso mismo — buen oído. Toda buena dádiva viene de lo alto. 🙏",
    "Acertó, patrón. Que el Señor le siga bendiciendo los dedos.",
]

INCORRECT_LINES = [
    "Casi, patrón... pero no. 🐾",
    "Ese no era, mas no desmaye — hasta el salmista erraba alguna cuerda.",
    "Falló, patrón, pero hasta yo desafino a veces con el saxo.",
    "No era esa — mire la correcta y prosiga; la constancia es lo que Dios bendice.",
]


def correct_line(rng: random.Random | None = None) -> str:
    rng = rng or random
    return rng.choice(CORRECT_LINES)


def incorrect_line(rng: random.Random | None = None) -> str:
    rng = rng or random
    return rng.choice(INCORRECT_LINES)
