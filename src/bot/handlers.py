import io
import logging
import random
from functools import wraps

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from .. import db, personality
from ..config import ALLOWED_USER_IDS, ASSETS_DIR
from ..graphics.circle_image import get_or_create_circle_image
from ..graphics.practice_card import build_practice_card
from ..songs.library import load_songs
from ..songs.practice import generate_song_question
from ..theory import (
    COMMON_PROGRESSIONS,
    PROGRESSION_EXPLANATIONS,
    build_progression,
    generate_question,
    random_bpm,
    random_strum_pattern,
)
from ..theory.notes import NOTE_NAMES

logger = logging.getLogger(__name__)


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


@_allowed
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(personality.GREETING, parse_mode="Markdown")


@_allowed
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(personality.HELP_TEXT, parse_mode="Markdown")


@_allowed
async def circulo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path = get_or_create_circle_image(str(ASSETS_DIR))
    with open(path, "rb") as f:
        await update.effective_message.reply_photo(photo=f, caption="🎼 Círculo de quintas")


@_allowed
async def practicar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = generate_question()
    text = (
        f"🎸 Progresión *{question['progression_name']}* en *{question['origin_key']}*:\n"
        f"`{' - '.join(question['origin_chords'])}`\n\n"
        f"Transpórtala a *{question['target_key']}*. ¿Cuál es la opción correcta?"
    )
    if question["explanation"]:
        text += f"\n\n💡 _Por qué funciona:_ {question['explanation']}"
    buttons = []
    for i, option in enumerate(question["options"]):
        label = " - ".join(option)
        buttons.append(
            [InlineKeyboardButton(label, callback_data=f"ans|{i}|{question['correct_index']}")]
        )
    await update.effective_message.reply_text(
        text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons)
    )


@_allowed
async def practicar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, chosen_str, correct_str = query.data.split("|")
    chosen_index, correct_index = int(chosen_str), int(correct_str)
    is_correct = chosen_index == correct_index

    correct_label = None
    for row in query.message.reply_markup.inline_keyboard:
        for btn in row:
            if btn.callback_data == f"ans|{correct_index}|{correct_index}":
                correct_label = btn.text
    chosen_label = None
    for row in query.message.reply_markup.inline_keyboard:
        for btn in row:
            if btn.callback_data == query.data:
                chosen_label = btn.text

    stats = db.record_result(query.from_user.id, is_correct)

    if is_correct:
        result_line = f"{personality.correct_line()}\nTu respuesta: `{chosen_label}`"
    else:
        result_line = (
            f"{personality.incorrect_line()}\n"
            f"Tu respuesta: `{chosen_label}`\n"
            f"Correcta: `{correct_label}`"
        )

    result_line += f"\n\n🔥 Racha: {stats['streak']} (mejor: {stats['best_streak']})"

    await query.edit_message_text(
        text=query.message.text + "\n\n" + result_line,
        parse_mode="Markdown",
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
async def cancion_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, idx_str = query.data.split("|")
    songs = load_songs()
    song = songs[int(idx_str)]
    question = generate_song_question(song)

    text = (
        f"🎵 *{question['title']}* está en *{question['origin_key']}*:\n"
        f"`{' - '.join(question['origin_chords'])}`\n\n"
        f"Transpórtala a *{question['target_key']}*. ¿Cuál es la opción correcta?"
    )
    buttons = []
    for i, option in enumerate(question["options"]):
        label = " - ".join(option)
        buttons.append(
            [InlineKeyboardButton(label, callback_data=f"ans|{i}|{question['correct_index']}")]
        )
    await query.edit_message_text(
        text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons)
    )


@_allowed
async def tarjeta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name, degrees = random.choice(COMMON_PROGRESSIONS)
    key_root = random.randrange(12)
    chords = build_progression(key_root, degrees)
    bpm = random_bpm()
    strum_name, strum_pattern = random_strum_pattern()

    title = f"{name} en {NOTE_NAMES[key_root]}"
    img = build_practice_card(chords, bpm, strum_name, strum_pattern, title=title)
    caption = f"🎼 {title} — practica el cambio de acorde con este ritmo."
    explanation = PROGRESSION_EXPLANATIONS.get(name)
    if explanation:
        caption += f"\n\n💡 Por qué funciona: {explanation}"
    await update.effective_message.reply_photo(
        photo=_image_to_bytes(img),
        caption=caption,
    )


@_allowed
async def sesion_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    songs = load_songs()
    song = random.choice(songs)
    chords = song["unique_chords"][:6]
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
