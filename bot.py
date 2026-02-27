import logging
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import database

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "notes.db")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я бот-записная книжка.\n"
        "Команды:\n"
        "  /remember <текст> — сохранить заметку\n"
        "  /remind — показать последнюю заметку\n"
        "  /remind <ключевое слово> — найти заметки по ключевому слову"
    )


async def remember(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Использование: /remember <текст заметки>")
        return
    database.save_note(DB_PATH, user_id, text)
    await update.message.reply_text("Заметка сохранена!")


async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    keyword = " ".join(context.args)

    if keyword:
        notes = database.search_notes(DB_PATH, user_id, keyword)
        if not notes:
            await update.message.reply_text(
                f"Заметки с ключевым словом «{keyword}» не найдены."
            )
        else:
            reply = "\n\n".join(f"• {n}" for n in notes)
            await update.message.reply_text(reply)
    else:
        note = database.get_last_note(DB_PATH, user_id)
        if note is None:
            await update.message.reply_text("У вас пока нет сохранённых заметок.")
        else:
            await update.message.reply_text(note)


def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN environment variable is not set")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("remember", remember))
    app.add_handler(CommandHandler("remind", remind))
    logger.info("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
