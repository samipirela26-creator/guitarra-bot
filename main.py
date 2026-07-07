import logging

from telegram import BotCommand
from telegram.ext import Application, ApplicationBuilder, CallbackQueryHandler, CommandHandler

from src.bot.handlers import (
    cancion_callback,
    canciones_command,
    circulo_command,
    help_command,
    practicar_callback,
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
    BotCommand("sesion", "Rutina de práctica guiada completa"),
    BotCommand("tarjeta", "Tarjeta de práctica con acordes y ritmo al azar"),
    BotCommand("circulo", "Ver el círculo de quintas"),
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
    app.add_handler(CommandHandler("tarjeta", tarjeta_command))
    app.add_handler(CommandHandler("sesion", sesion_command))
    app.add_handler(CommandHandler("puntaje", puntaje_command))
    app.add_handler(CallbackQueryHandler(practicar_callback, pattern=r"^ans\|"))
    app.add_handler(CallbackQueryHandler(cancion_callback, pattern=r"^song\|"))

    logger.info("Trivilín está en línea 🐶🎷🎸")
    app.run_polling()


if __name__ == "__main__":
    main()
