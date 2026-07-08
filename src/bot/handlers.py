import io
import logging
import random
from functools import wraps

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.ext import ContextTypes

from .. import db, personality
from ..config import ALLOWED_USER_IDS, ASSETS_DIR
from ..graphics.chord_row import build_chord_row
from ..graphics.circle_image import get_or_create_circle_image
from ..graphics.practice_card import build_practice_card
from ..songs.library import load_songs
from ..songs.practice import generate_song_question, song_origin_chords
from ..theory import (
    CIRCLE_MAJOR_ORDER,
    COMMON_PROGRESSIONS,
    PROGRESSION_EXPLANATIONS,
    RELATIVE_MINOR,
    STYLE_PROGRESSIONS,
    build_progression,
    build_progression_ext,
    generate_question,
    harmonic_circle,
    harmonic_circle_minor,
    random_bpm,
    random_strum_pattern,
    random_style_progression,
)
from ..theory.chord_shapes import CHORD_SHAPES, simplify_chord_name
from ..theory.notes import NOTE_NAMES, parse_chord, semitone_distance, transpose_progression

logger = logging.getLogger(__name__)

# Universo de acordes del picker "arma la respuesta" (sin opciones múltiples: se
# muestran TODOS los acordes posibles, ordenados alfabéticamente, y el jugador
# construye la progresión transportada tocándolos uno por uno — pensado para
# jugarlo mientras se hace otra cosa, sin apuro). /practicar solo necesita
# tríadas básicas (las progresiones diatónicas nunca usan calidad extendida);
# /canciones usa el catálogo completo de 72 porque los acordes reales sí las traen.
ALL_BASIC_CHORDS = sorted(NOTE_NAMES + [n + "m" for n in NOTE_NAMES])
ALL_EXTENDED_CHORDS = sorted(CHORD_SHAPES.keys())

# Sentinel que viaja como si fuera "el acorde tocado" en el callback_data, pero
# en vez de agregarse a la selección hace que el handler borre el último acorde
# ya elegido (permite corregir un toque equivocado sin reiniciar la pregunta).
UNDO_MARK = "⌫"


def _allowed(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if ALLOWED_USER_IDS and (user is None or user.id not in ALLOWED_USER_IDS):
            logger.warning("Acceso bloqueado para user_id=%s", user.id if user else None)
            if update.effective_message:
                await update.effective_message.reply_text("No estás autorizado a usar este bot.")
            return
        return await func(update, context)

    return wrapper


def _image_to_bytes(img) -> io.BytesIO:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def _chords_keyboard(
    chords: list[str], data_prefix: str, columns: int, show_undo: bool = False
) -> InlineKeyboardMarkup:
    """Teclado con TODOS los acordes posibles (sin filtrar los ya usados — una
    progresión puede repetir un acorde, ej. I-IV-I-V). data_prefix ya trae todo
    el estado necesario (índice de progresión/canción, tono destino, selección
    acumulada); cada botón solo le agrega '|<acorde>' al tocarlo. Si show_undo
    es True (hay al menos un acorde ya elegido) se agrega una fila final para
    borrar el último toque sin perder el resto de la selección."""
    rows = []
    row = []
    for chord in chords:
        row.append(InlineKeyboardButton(chord, callback_data=f"{data_prefix}|{chord}"))
        if len(row) == columns:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    if show_undo:
        rows.append([InlineKeyboardButton("⌫ Borrar último", callback_data=f"{data_prefix}|{UNDO_MARK}")])
    return InlineKeyboardMarkup(rows)


def _progress_line(total: int, selections: list[str]) -> str:
    padded = selections + ["?"] * (total - len(selections))
    return " → ".join(f"`{c}`" for c in padded[:total])


def _result_line(is_correct: bool, selections: list[str], correct_chords: list[str], stats: dict) -> str:
    if is_correct:
        line = f"{personality.correct_line()}\nTu respuesta: `{' - '.join(selections)}`"
    else:
        line = (
            f"{personality.incorrect_line()}\n"
            f"Tu respuesta: `{' - '.join(selections)}`\n"
            f"Correcta: `{' - '.join(correct_chords)}`"
        )
    line += f"\n\n🔥 Racha: {stats['streak']} (mejor: {stats['best_streak']})"
    return line


@_allowed
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(personality.GREETING, parse_mode="Markdown")


@_allowed
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(personality.HELP_TEXT, parse_mode="Markdown")


def _circulo_keyboard(mode: str = "M") -> InlineKeyboardMarkup:
    """Un botón por tonalidad (mayor o menor, según `mode`), mismo orden que el
    círculo de quintas de la imagen, en grid de 4 columnas. callback_data lleva
    la pitch class y el modo: "circ|{root_pc}|{mode}". Al final se agrega un
    botón para alternar entre tonalidades mayores y menores."""
    rows = []
    row = []
    labels = CIRCLE_MAJOR_ORDER if mode == "M" else RELATIVE_MINOR
    for key in labels:
        root_pc, _, _ = parse_chord(key)
        row.append(InlineKeyboardButton(key, callback_data=f"circ|{root_pc}|{mode}"))
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    other_mode = "m" if mode == "M" else "M"
    toggle_label = "🔁 Ver tonalidades menores" if mode == "M" else "🔁 Ver tonalidades mayores"
    rows.append([InlineKeyboardButton(toggle_label, callback_data=f"circmode|{other_mode}")])
    return InlineKeyboardMarkup(rows)


def _circulo_armonico(root_pc: int, mode: str = "M") -> tuple[str, str, list[tuple[str, str, str]]]:
    """Devuelve (nombre de la tonalidad, título, círculo armónico) para el modo pedido."""
    if mode == "M":
        key_name = NOTE_NAMES[root_pc]
        circle = harmonic_circle(root_pc)
        title = f"🎼 *Círculo armónico de {key_name} mayor*"
    else:
        key_name = f"{NOTE_NAMES[root_pc]}m"
        circle = harmonic_circle_minor(root_pc)
        title = f"🎼 *Círculo armónico de {key_name} (menor natural)*"
    return key_name, title, circle


def _circulo_armonico_text(root_pc: int, mode: str = "M") -> str:
    _key_name, title, circle = _circulo_armonico(root_pc, mode)
    lines = [
        title,
        "Estos son los acordes que combinan naturalmente en esta tonalidad:\n",
    ]
    for roman, chord, function in circle:
        lines.append(f"*{roman}* → `{chord}` — {function}")
    lines.append("\nToca otra tonalidad para verla.")
    return "\n".join(lines)


@_allowed
async def circulo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path = get_or_create_circle_image(str(ASSETS_DIR))
    with open(path, "rb") as f:
        await update.effective_message.reply_photo(
            photo=f,
            caption="🎼 Círculo de quintas. Toca una tonalidad para ver su círculo armónico "
            "(los acordes que combinan en esa tonalidad y para qué sirve cada uno). "
            "También puedes ver las tonalidades menores.",
            reply_markup=_circulo_keyboard("M"),
        )


@_allowed
async def circulo_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, root_pc_s, mode = query.data.split("|")
    root_pc = int(root_pc_s)
    key_name, _title, circle = _circulo_armonico(root_pc, mode)
    text = _circulo_armonico_text(root_pc, mode)
    await query.edit_message_caption(
        caption=text, parse_mode="Markdown", reply_markup=_circulo_keyboard(mode)
    )

    labels = [roman for roman, _chord, _function in circle]
    chords = [chord for _roman, chord, _function in circle]
    img = build_chord_row(chords, labels, title=f"Acordes de {key_name}")
    await query.message.reply_photo(
        photo=_image_to_bytes(img),
        caption=f"🎸 Los 7 acordes de {key_name} para tocar mientras miras el círculo armónico.",
    )


@_allowed
async def circulo_mode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, mode = query.data.split("|")
    caption = (
        "🎼 Círculo de quintas. Toca una tonalidad para ver su círculo armónico "
        "(los acordes que combinan en esa tonalidad y para qué sirve cada uno). "
        "También puedes ver las tonalidades mayores."
        if mode == "m"
        else "🎼 Círculo de quintas. Toca una tonalidad para ver su círculo armónico "
        "(los acordes que combinan en esa tonalidad y para qué sirve cada uno). "
        "También puedes ver las tonalidades menores."
    )
    await query.edit_message_caption(
        caption=caption, reply_markup=_circulo_keyboard(mode)
    )


def _practicar_header(
    name: str, origin_key: str, origin_chords: list[str], target_key: str, explanation: str | None
) -> str:
    text = (
        f"🎸 Progresión *{name}* en *{origin_key}*:\n"
        f"`{' - '.join(origin_chords)}`\n\n"
        f"Transpórtala a *{target_key}*."
    )
    if explanation:
        text += f"\n\n💡 _Por qué funciona:_ {explanation}"
    return text


# Botón para encadenar rondas sin volver a escribir /practicar — pensado para
# jugar en ratos muertos (una fila de espera, antes de empezar el ensayo...):
# tocarlo reemplaza el mensaje de resultado por una pregunta nueva al toque.
_JUGAR_OTRA_VEZ = InlineKeyboardMarkup([[InlineKeyboardButton("🎲 Jugar otra vez", callback_data="pagain")]])


def _practicar_question_msg() -> tuple[str, InlineKeyboardMarkup]:
    """Arma el texto + teclado de una pregunta nueva de "jugar a transportar"
    (usado tanto por /practicar como por el botón "Jugar otra vez")."""
    question = generate_question()
    total = len(question["origin_chords"])
    header = _practicar_header(
        question["progression_name"],
        question["origin_key"],
        question["origin_chords"],
        question["target_key"],
        question["explanation"],
    )
    text = header + f"\n\nArma la respuesta acorde por acorde (1/{total}):\n{_progress_line(total, [])}"
    prefix = f"pbld|{question['prog_idx']}|{question['origin_pc']}|{question['target_pc']}|"
    markup = _chords_keyboard(ALL_BASIC_CHORDS, prefix, columns=4)
    return text, markup


@_allowed
async def practicar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, markup = _practicar_question_msg()
    await update.effective_message.reply_text(text, parse_mode="Markdown", reply_markup=markup)


@_allowed
async def practicar_again_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """El botón "🎲 Jugar otra vez" del resultado: arma una ronda nueva en el
    mismo mensaje, para poder encadenar varias sin escribir /practicar de nuevo."""
    query = update.callback_query
    await query.answer()
    text, markup = _practicar_question_msg()
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)


@_allowed
async def practicar_build_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, prog_idx_s, origin_pc_s, target_pc_s, sel_csv, chord = query.data.split("|")
    prog_idx, origin_pc, target_pc = int(prog_idx_s), int(origin_pc_s), int(target_pc_s)
    prev_selections = sel_csv.split(",") if sel_csv else []
    if chord == UNDO_MARK:
        selections = prev_selections[:-1]
    else:
        selections = prev_selections + [chord]

    name, degrees = COMMON_PROGRESSIONS[prog_idx]
    total = len(degrees)
    origin_key = NOTE_NAMES[origin_pc]
    target_key = NOTE_NAMES[target_pc]
    origin_chords = build_progression(origin_pc, degrees)
    explanation = PROGRESSION_EXPLANATIONS.get(name)
    header = _practicar_header(name, origin_key, origin_chords, target_key, explanation)

    if len(selections) < total:
        new_sel_csv = ",".join(selections)
        text = (
            header
            + f"\n\nArma la respuesta acorde por acorde ({len(selections) + 1}/{total}):\n"
            + _progress_line(total, selections)
        )
        prefix = f"pbld|{prog_idx}|{origin_pc}|{target_pc}|{new_sel_csv}"
        markup = _chords_keyboard(ALL_BASIC_CHORDS, prefix, columns=4, show_undo=bool(selections))
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)
        return

    correct_chords = build_progression(target_pc, degrees)
    is_correct = selections == correct_chords
    stats = db.record_result(query.from_user.id, is_correct)
    text = header + "\n\n" + _result_line(is_correct, selections, correct_chords, stats)
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=_JUGAR_OTRA_VEZ)

    bpm = random_bpm()
    strum_name, strum_pattern = random_strum_pattern()
    img = build_practice_card(correct_chords, bpm, strum_name, strum_pattern, title=f"{name} en {target_key}")
    await query.message.reply_photo(
        photo=_image_to_bytes(img),
        caption=f"🎸 Diagramas para practicar la progresión correcta en {target_key}.",
    )


@_allowed
async def canciones_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    songs = load_songs()
    buttons = []
    row = []
    for i, song in enumerate(songs):
        row.append(InlineKeyboardButton(song["title"], callback_data=f"song|{i}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    await update.effective_message.reply_text(
        "🎵 Elige una canción del cancionero para practicar transportarla:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@_allowed
async def letra_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    songs = load_songs()
    buttons = []
    row = []
    for i, song in enumerate(songs):
        row.append(InlineKeyboardButton(song["title"], callback_data=f"letra|{i}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    await update.effective_message.reply_text(
        "📄 Elige una canción para ver su letra completa con los acordes, tal como "
        "está en el cancionero:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@_allowed
async def letra_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, idx_str = query.data.split("|")
    song_idx = int(idx_str)
    songs = load_songs()
    song = songs[song_idx]
    text = f"🎼 *{song['title']}* — tono *{song['tono']}*\n```\n{song['lyrics']}\n```"
    await query.edit_message_text(text, parse_mode="Markdown")


def _cancion_header(title: str, origin_key: str, origin_chords: list[str], target_key: str) -> str:
    return (
        f"🎵 *{title}* está en *{origin_key}*:\n"
        f"`{' - '.join(origin_chords)}`\n\n"
        f"Transpórtala a *{target_key}*."
    )


@_allowed
async def cancion_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, idx_str = query.data.split("|")
    song_idx = int(idx_str)
    songs = load_songs()
    song = songs[song_idx]
    question = generate_song_question(song)

    total = len(question["origin_chords"])
    header = _cancion_header(
        question["title"], question["origin_key"], question["origin_chords"], question["target_key"]
    )
    text = header + f"\n\nArma la respuesta acorde por acorde (1/{total}):\n{_progress_line(total, [])}"
    prefix = f"cbld|{song_idx}|{question['target_pc']}|"
    markup = _chords_keyboard(ALL_EXTENDED_CHORDS, prefix, columns=6)
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)


@_allowed
async def cancion_build_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, song_idx_s, target_pc_s, sel_csv, chord = query.data.split("|")
    song_idx, target_pc = int(song_idx_s), int(target_pc_s)
    prev_selections = sel_csv.split(",") if sel_csv else []
    if chord == UNDO_MARK:
        selections = prev_selections[:-1]
    else:
        selections = prev_selections + [chord]

    songs = load_songs()
    song = songs[song_idx]
    origin_chords = song_origin_chords(song)
    total = len(origin_chords)
    origin_pc, _, _ = parse_chord(song["tono"])
    target_key = NOTE_NAMES[target_pc]
    header = _cancion_header(song["title"], song["tono"], origin_chords, target_key)

    if len(selections) < total:
        new_sel_csv = ",".join(selections)
        text = (
            header
            + f"\n\nArma la respuesta acorde por acorde ({len(selections) + 1}/{total}):\n"
            + _progress_line(total, selections)
        )
        prefix = f"cbld|{song_idx}|{target_pc}|{new_sel_csv}"
        markup = _chords_keyboard(ALL_EXTENDED_CHORDS, prefix, columns=6, show_undo=bool(selections))
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)
        return

    semitones = semitone_distance(origin_pc, target_pc)
    raw_correct = transpose_progression(origin_chords, semitones)
    # Normaliza al acorde alcanzable más cercano (mismo criterio que resolve_diagram):
    # si la canción real trae una calidad no soportada o bajo alterado, se acepta
    # la forma base — el picker nunca ofrece slash chords como botón.
    correct_chords = [simplify_chord_name(c) for c in raw_correct]
    is_correct = selections == correct_chords
    stats = db.record_result(query.from_user.id, is_correct)
    text = header + "\n\n" + _result_line(is_correct, selections, correct_chords, stats)
    await query.edit_message_text(text, parse_mode="Markdown")

    bpm = random_bpm()
    strum_name, strum_pattern = random_strum_pattern()
    img = build_practice_card(
        correct_chords, bpm, strum_name, strum_pattern, title=f"{song['title']} en {target_key}"
    )
    await query.message.reply_photo(
        photo=_image_to_bytes(img),
        caption=f"🎸 Diagramas para practicar {song['title']} en {target_key}.",
    )


@_allowed
async def tarjeta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    style, name, degree_qualities = random_style_progression()
    key_root = random.randrange(12)
    chords = build_progression_ext(key_root, degree_qualities)
    bpm = random_bpm(style=style)
    strum_name, strum_pattern = random_strum_pattern(style=style)

    title = f"{name} ({style}) en {NOTE_NAMES[key_root]}"
    img = build_practice_card(chords, bpm, strum_name, strum_pattern, title=title)
    caption = f"🎼 {title} — practica el cambio de acorde con este ritmo."
    await update.effective_message.reply_photo(
        photo=_image_to_bytes(img),
        caption=caption,
    )


def _estilo_keyboard() -> InlineKeyboardMarkup:
    """Un botón por estilo musical (ver theory.progressions.STYLE_PROGRESSIONS),
    en grid de 2 columnas. callback_data: "estl|{estilo}"."""
    rows = []
    row = []
    for style in STYLE_PROGRESSIONS:
        row.append(InlineKeyboardButton(style, callback_data=f"estl|{style}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(rows)


def _estilo_result_keyboard(style: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔄 Otra progresión", callback_data=f"estl|{style}")],
            [InlineKeyboardButton("🎵 Cambiar de estilo", callback_data="estlmenu")],
        ]
    )


@_allowed
async def estilo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "🎸 Elige un estilo y te armo una progresión, tono y ritmo típicos de ese "
        "género para practicar:",
        reply_markup=_estilo_keyboard(),
    )


@_allowed
async def estilo_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "estlmenu":
        await query.message.reply_text(
            "🎸 Elige un estilo y te armo una progresión, tono y ritmo típicos de ese "
            "género para practicar:",
            reply_markup=_estilo_keyboard(),
        )
        return

    _, style = query.data.split("|")
    name, degree_qualities = random.choice(STYLE_PROGRESSIONS[style])
    key_root = random.randrange(12)
    chords = build_progression_ext(key_root, degree_qualities)
    bpm = random_bpm(style=style)
    strum_name, strum_pattern = random_strum_pattern(style=style)

    title = f"{name} ({style}) en {NOTE_NAMES[key_root]}"
    img = build_practice_card(chords, bpm, strum_name, strum_pattern, title=title)
    caption = f"🎸 Estilo *{style}* — {title}.\nAcordes: `{' - '.join(chords)}`"
    keyboard = _estilo_result_keyboard(style)

    if query.message.photo:
        # Ya veníamos de una tarjeta de este flujo (toque de "otra progresión" o
        # de otro estilo): reemplaza la foto en el mismo mensaje, sin ensuciar el chat.
        await query.edit_message_media(
            media=InputMediaPhoto(_image_to_bytes(img), caption=caption, parse_mode="Markdown"),
            reply_markup=keyboard,
        )
    else:
        # Primer toque desde el menú de texto: no se puede convertir un mensaje de
        # texto en foto, así que se manda una foto nueva.
        await query.message.reply_photo(
            photo=_image_to_bytes(img), caption=caption, parse_mode="Markdown", reply_markup=keyboard
        )


@_allowed
async def sesion_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    songs = load_songs()
    song = random.choice(songs)
    # Todos los acordes reales de la canción — antes se cortaba a los primeros 6,
    # lo que dejaba canciones como "Gracias, Dios" (15 acordes únicos) incompletas
    # tanto en el texto como en la tarjeta de práctica. A diferencia de /canciones,
    # aquí no hay un picker con callback_data que limite el total (es solo texto +
    # una foto de referencia), así que no hace falta ningún tope.
    chords = song["unique_chords"]
    bpm = random_bpm()
    strum_name, strum_pattern = random_strum_pattern()

    warmup = random.choice(personality.WARMUP_EXERCISES)
    technique = random.choice(personality.TECHNIQUE_TIPS)
    pair_a, pair_b = (chords[0], chords[1]) if len(chords) >= 2 else (chords[0], chords[0])

    text = (
        f"{personality.SESSION_INTRO}\n\n"
        "1️⃣ *Calentamiento* (5 min)\n"
        f"{warmup}\n\n"
        "2️⃣ *Cambios de acorde* (5-8 min)\n"
        f"Alterna `{pair_a}` ↔ `{pair_b}` con metrónomo. Empieza lento, sube el tempo "
        "solo cuando el cambio salga limpio.\n\n"
        "3️⃣ *Técnica* (5 min)\n"
        f"{technique}\n\n"
        f"4️⃣ *Canción real: {song['title']}* (10-15 min)\n"
        f"Toma este círculo armónico con estos acordes en *{bpm} BPM*, practícalos:\n"
        f"`{' - '.join(chords)}`"
    )
    await update.effective_message.reply_text(text, parse_mode="Markdown")

    circle_path = get_or_create_circle_image(str(ASSETS_DIR))
    with open(circle_path, "rb") as f:
        await update.effective_message.reply_photo(photo=f, caption="🎼 Círculo de quintas de referencia.")

    img = build_practice_card(chords, bpm, strum_name, strum_pattern, title=song["title"])
    await update.effective_message.reply_photo(
        photo=_image_to_bytes(img),
        caption=f"🎵 {song['title']} en {song['tono']} — {bpm} BPM, rasgueo {strum_name}.",
    )


# Rutina adaptativa según el tiempo disponible (no un horario fijo): pensada para
# guitarristas de iglesia que ya saben tocar el repertorio pero les cuesta cambiar
# de tono y ser constantes. Cada nivel prioriza /practicar (el ejercicio correctivo
# para el cambio de tono: pensar en numerales romanos en vez de nombres de nota,
# el mismo "Sistema Nashville" que usan las bandas de adoración) y siempre cierra
# recordando revisar la racha en /puntaje (el "no rompas la cadena" de los hábitos).
_PLAN_INTRO = (
    "📅 *Plan de práctica adaptativo*\n"
    "No es un horario fijo — elige según el tiempo que tengas *hoy*. La idea es "
    "que nunca falles un día entero, aunque sea la versión corta:"
)

_PLAN_TIERS = {
    "corto": (
        "⏱️ Poco tiempo (5-10 min)",
        "⏱️ *Día apurado (5-10 min)*\n\n"
        "1️⃣ 2 min de calentamiento: /tarjeta o /estilo → Adoración.\n"
        "2️⃣ 5-8 min: /practicar — arma 2-3 progresiones de transposición. Este es "
        "tu ejercicio prioritario (el cambio de tono), no lo saltes aunque el día "
        "esté corto.\n\n"
        "✅ Con esto ya cumpliste el día. Revisa tu racha en /puntaje.",
    ),
    "normal": (
        "🕐 Tiempo normal (15-20 min)",
        "🕐 *Día normal (15-20 min)*\n\n"
        "1️⃣ 3 min calentamiento: /tarjeta.\n"
        "2️⃣ 8-10 min: /practicar + /circulo — toca la tonalidad que te salga y "
        "piensa el numeral romano (I, IV, V...) de cada acorde antes que el "
        "nombre de la nota.\n"
        "3️⃣ 5-7 min: una canción real con /canciones o /letra, intentando "
        "transportarla de oído.\n\n"
        "✅ Revisa tu racha en /puntaje.",
    ),
    "largo": (
        "⏳ Tengo tiempo (30-45 min)",
        "⏳ *Día con tiempo (30-45 min)*\n\n"
        "1️⃣ Corre /sesion completo (calentamiento → cambios de acorde → técnica "
        "→ canción real).\n"
        "2️⃣ +10 min extra de /practicar, enfocado solo en cambios de tono.\n\n"
        "✅ Revisa tu racha en /puntaje — y recuerda: si un día no tocas, no pasa "
        "nada, pero al día siguiente sí o sí (nunca falles dos veces seguidas).",
    ),
}


def _plan_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(label, callback_data=f"plan|{key}")] for key, (label, _text) in _PLAN_TIERS.items()]
    )


@_allowed
async def plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        _PLAN_INTRO, parse_mode="Markdown", reply_markup=_plan_keyboard()
    )


@_allowed
async def plan_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, tier = query.data.split("|")
    _label, text = _PLAN_TIERS[tier]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=_plan_keyboard())


@_allowed
async def puntaje_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = db.get_stats(update.effective_user.id)
    total = stats["correct"] + stats["incorrect"]
    pct = (stats["correct"] / total * 100) if total else 0
    text = (
        f"📊 *Tu puntaje*\n"
        f"Aciertos: {stats['correct']} / {total} ({pct:.0f}%)\n"
        f"Racha actual: {stats['streak']}\n"
        f"Mejor racha: {stats['best_streak']}"
    )
    await update.effective_message.reply_text(text, parse_mode="Markdown")
