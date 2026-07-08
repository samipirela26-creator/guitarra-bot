import logging

from telegram import BotCommand
from telegram.ext import Application, ApplicationBuilder, CallbackQueryHandler, CommandHandler

from src.bot.handlers import (
    cancion_build_callback,
    cancion_callback,
    canciones_command,
    circulo_callback,
    circulo_command,
    circulo_mode_callback,
    estilo_callback,
    estilo_command,
    help_command,
    letra_callback,
    letra_command,
    plan_callback,
    plan_command,
    practicar_build_callback,
    practicar_command,
    puntaje_command,
    sesion_command,
    start_command,
    tarjeta_command,
)
from src.config import TELEGRAM_BOT_TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_COMMANDS = [
    BotCommand("practicar", "Transportar una progresión de acordes"),
    BotCommand("canciones", "Practicar transportando una canción real"),
    BotCommand("letra", "Ver la letra completa de una canción con acordes"),
    BotCommand("sesion", "Rutina de práctica guiada completa"),
    BotCommand("tarjeta", "Tarjeta de práctica con acordes y ritmo al azar"),
    BotCommand("estilo", "Practicar acordes y ritmo de un género (rock, pop, jazz...)"),
    BotCommand("circulo", "Ver el círculo de quintas"),
    BotCommand("plan", "Rutina de práctica adaptativa según tu tiempo"),
    BotCommand("puntaje", "Ver tu racha y estadísticas"),
    BotCommand("help", "Ver ayuda sobre el bot"),
]


async def _post_init(app: Application) -> None:
    await app.bot.set_my_commands(BOT_COMMANDS)


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise SystemExit("Falta TELEGRAM_BOT_TOKEN en .env")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).post_init(_post_init).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("circulo", circulo_command))
    app.add_handler(CommandHandler("practicar", practicar_command))
    app.add_handler(CommandHandler("canciones", canciones_command))
    app.add_handler(CommandHandler("letra", letra_command))
    app.add_handler(CommandHandler("tarjeta", tarjeta_command))
    app.add_handler(CommandHandler("estilo", estilo_command))
    app.add_handler(CommandHandler("sesion", sesion_command))
    app.add_handler(CommandHandler("plan", plan_command))
    app.add_handler(CommandHandler("puntaje", puntaje_command))
    app.add_handler(CallbackQueryHandler(practicar_build_callback, pattern=r"^pbld\|"))
    app.add_handler(CallbackQueryHandler(cancion_callback, pattern=r"^song\|"))
    app.add_handler(CallbackQueryHandler(letra_callback, pattern=r"^letra\|"))
    app.add_handler(CallbackQueryHandler(cancion_build_callback, pattern=r"^cbld\|"))
    app.add_handler(CallbackQueryHandler(circulo_callback, pattern=r"^circ\|"))
    app.add_handler(CallbackQueryHandler(circulo_mode_callback, pattern=r"^circmode\|"))
    app.add_handler(CallbackQueryHandler(estilo_callback, pattern=r"^estl"))
    app.add_handler(CallbackQueryHandler(plan_callback, pattern=r"^plan\|"))

    logger.info("Trivilín está en línea 🐶🎷🎸")
    app.run_polling()


if __name__ == "__main__":
    main()
