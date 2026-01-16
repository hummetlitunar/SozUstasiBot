# -*- coding: utf-8 -*-

import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from game import Game
import settings

# -------------------------------------------------
# GLOBALS
# -------------------------------------------------

games = {}

# -------------------------------------------------
# HELPERS
# -------------------------------------------------

def get_or_create_game(chat_id: int) -> Game:
    if chat_id not in games:
        games[chat_id] = Game()
    return games[chat_id]


def setup_logger():
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

# -------------------------------------------------
# COMMANDS
# -------------------------------------------------

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("pong")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Əmrlər:\n"
        "/basla - Oyunu başlat\n"
        "/master - Aparıcı ol\n"
        "/sincab_rating - Reytinq\n"
        "/ping - Test"
    )


async def command_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        keyboard = [
            [InlineKeyboardButton("Qrupa əlavə edin!", url="https://t.me/SozUstasiBot?startgroup=a")]
        ]
        await update.message.reply_text(
            "Bu oyun yalnız qruplarda oynanır.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    chat_id = update.effective_chat.id
    user = update.effective_user

    game = get_or_create_game(chat_id)
    game.start()

    await update.message.reply_text("🟢 Oyun başladı!")
    await set_master(update, context)


async def set_master(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    game = get_or_create_game(chat_id)
    game.set_master(user.id)

    keyboard = [
        [InlineKeyboardButton("Sözə bax 🐿️", callback_data="show_word")],
        [InlineKeyboardButton("Sözü dəyiş ↺", callback_data="change_word")],
    ]

    await update.message.reply_text(
        f"[{user.full_name}](tg://user?id={user.id}) sözü başa salır",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN,
    )


async def command_master(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    game = get_or_create_game(chat_id)

    if not game.is_game_started():
        return

    if not game.is_master_time_left():
        await update.message.reply_text(
            f"Aparıcı olmaq üçün {game.get_master_time_left()} saniyə qalıb"
        )
        return

    await set_master(update, context)


async def command_sincab_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    game = get_or_create_game(chat_id)
    await update.message.reply_text(game.get_str_rating())


# -------------------------------------------------
# CALLBACK BUTTONS (GERİ BİLDİRİMLİ)
# -------------------------------------------------

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat.id

    game = get_or_create_game(chat_id)

    # ---- SÖZƏ BAX ----
    if query.data == "show_word":
        if game.is_master(user_id):
            await query.answer(game.get_word(user_id), show_alert=True)
        else:
            await query.answer("Bu düymə yalnız aparıcı üçündür.", show_alert=True)
        return

    # ---- SÖZÜ DƏYİŞ ----
    if query.data == "change_word":
        if not game.is_master(user_id):
            await query.answer("Bu düymə yalnız aparıcı üçündür.", show_alert=True)
            return

        new_word = game.change_word(user_id)

        if new_word:
            await query.answer(
                f"{new_word}\n\nQalan dəyişmə haqqı: {game.get_word_change_left()}",
                show_alert=True
            )
        else:
            await query.answer(
                "❌ Sözü artıq dəyişə bilməzsən.\n"
                "Maksimum 3 dəyişmə haqqın var.",
                show_alert=True
            )
        return


# -------------------------------------------------
# GAME LOGIC
# -------------------------------------------------

async def is_word_answered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    text = update.message.text

    game = get_or_create_game(chat_id)

    if game.is_word_answered(user.id, text):
        await update.message.reply_text(
            f"*{game.get_current_word()}* sözünü "
            f"[{user.full_name}](tg://user?id={user.id}) tapdı 🎉",
            parse_mode=ParseMode.MARKDOWN,
        )
        game.update_rating(user.id, user.full_name)
        await set_master(update, context)


# -------------------------------------------------
# MAIN
# -------------------------------------------------

def main():
    setup_logger()

    app = ApplicationBuilder().token(settings.TOKEN).build()

    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("start", command_start))
    app.add_handler(CommandHandler("basla", command_start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("master", command_master))
    app.add_handler(CommandHandler("sincab_rating", command_sincab_rating))

    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, is_word_answered))

    app.run_polling()


if __name__ == "__main__":
    main()
