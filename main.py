# -*- coding: utf-8 -*-

import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
    ChatMember,
    ChatMemberUpdated,

)
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    ContextTypes,
    filters,
)

from game import Game
import settings
import groups
from api_server import start_api_server, set_bot_application
from chat_member_handler import track_my_chat_member

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
        "/sincabsozu - Oyunu başlat\n"
        "/dayansincab - Oyunu dayandır\n"
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
    
    # Söz tipi seçimi təklif et
    keyboard = [
        [
            InlineKeyboardButton("📝 Sözlər", callback_data="start_words"),
            InlineKeyboardButton("👤 İnsan adları", callback_data="start_names"),
        ]
    ]
    
    await update.message.reply_text(
        "<b>🐿️ SÖZ USTASI</b>\n\n"
        "<i>Zəhmət olmasa, oynamaq istədiyiniz kateqoriyanı seçin:</i>\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )


async def command_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Oyunu məcburi dayandır"""
    chat_id = update.effective_chat.id
    game = get_or_create_game(chat_id)
    
    if not game.is_game_started():
         await update.message.reply_text("⚠️ Oyun onsuz da aktiv deyil.")
         return

    game.stop()
    await update.message.reply_text("🛑 Oyun dayandırıldı. /sincabsozu yazaraq yenidən başlada bilərsiniz.")


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
        await update.message.reply_text("⚠️ Oyun hələ başlamayıb! /sincabsozu yazaraq başlayın.")
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
    rating = game.get_str_rating()
    if not rating:
        await update.message.reply_text("📭 Reytinq cədvəli boşdur.")
    else:
        await update.message.reply_text(f"🏆 *Reytinq:*\n\n{rating}", parse_mode=ParseMode.MARKDOWN)


# -------------------------------------------------
# CALLBACK BUTTONS (GERİ BİLDİRİMLİ)
# -------------------------------------------------

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user = query.from_user
    user = query.from_user
    chat_id = query.message.chat.id

    game = get_or_create_game(chat_id)

    # ---- OYUN BAŞLAT: SÖZLƏR ----
    if query.data == "start_words":
        await query.answer()
        game.start(word_type='words')
        await query.edit_message_text("🟢 Oyun başladı! (📝 Sözlər)")
        await start_game_with_master(query, context, game, user)
        return

    # ---- OYUN BAŞLAT: İNSAN ADLARI ----
    if query.data == "start_names":
        await query.answer()
        game.start(word_type='names')
        await query.edit_message_text("🟢 Oyun başladı! (👤 İnsan adları)")
        await start_game_with_master(query, context, game, user)
        return

    # ---- SÖZƏ BAX ----
    if query.data == "show_word":
        if game.is_master(user_id):
            word = game.get_word(user_id)
            current_category = "Sözlər" if game._word_type == 'words' else "İnsan adları"
            
            alert_text = (
                f"━━━━━━━━━━━━━━━━\n\n"
                f"     ✨  {word.upper()}  ✨\n\n"
                f"━━━━━━━━━━━━━━━━\n"
            )
            await query.answer(alert_text, show_alert=True)
        else:
            await query.answer("⛔ Bu düymə yalnız aparıcı üçündür!", show_alert=True)
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


async def start_game_with_master(query, context, game, user):
    """Oyun seçildikdən sonra master təyin et"""
    game.set_master(user.id)

    keyboard = [
        [InlineKeyboardButton("Sözə bax 🐿️", callback_data="show_word")],
        [InlineKeyboardButton("Sözü dəyiş ↺", callback_data="change_word")],
    ]

    await query.message.reply_text(
        f"[{user.full_name}](tg://user?id={user.id}) sözü başa salır",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN,
    )

# -------------------------------------------------
# GAME LOGIC
# -------------------------------------------------

async def is_word_answered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
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

async def track_my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot qrupa əlavə olunanda və ya çıxarılanda işə düşür"""
    result = update.my_chat_member
    if not result:
        return

    new_status = result.new_chat_member.status
    chat_id = result.chat.id
    chat_title = result.chat.title

    # Bot qrupdan çıxarıldı (left) və ya atıldı (kicked)
    if new_status in [ChatMember.LEFT, ChatMember.BANNED]:
        groups.remove_group(chat_id)
    
    # Bot qrupa əlavə edildi
    elif new_status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR]:
        pass  # Artıq track_my_chat_member handler tərəfindən işlənilir


async def check_inactive_games(context: ContextTypes.DEFAULT_TYPE):
    """Zamanı bitmiş oyunları yoxla və dayandır"""
    for chat_id, game in list(games.items()):
        if game.is_inactive(minutes=15):
            game.stop()
            await context.bot.send_message(
                chat_id=chat_id,
                text="⏳ Uzun müddət aktivlik olmadığı üçün oyun dayandırıldı.\n"
                     "/sincabsozu yazaraq yenidən başlada bilərsiniz."
            )

async def post_init(application):
    await application.bot.set_my_commands([
        BotCommand("sincabsozu", "Oyunu başlat 🎮"),
        BotCommand("dayansincab", "Oyunu dayandır 🛑"),
        BotCommand("master", "Aparıcı ol 🎤"),
        BotCommand("master", "Aparıcı ol 🎤"),
        BotCommand("sincab_rating", "Reytinq cədvəli 🏆"),
        BotCommand("help", "Kömək ℹ️"),
        BotCommand("ping", "Bot statusu 📡"),
    ])

def main():
    setup_logger()

    # API server-i başlat (health check + KontrolBot API)
    start_api_server(settings.API_PORT)

    app = ApplicationBuilder().token(settings.TOKEN).post_init(post_init).build()
    
    # Bot instance-ı API server-ə bağla
    set_bot_application(app)

    # JobQueue: Hər 60 saniyədən bir yoxla
    if app.job_queue:
        app.job_queue.run_repeating(check_inactive_games, interval=60, first=60)

    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("start", command_start))
    app.add_handler(CommandHandler("sincabsozu", command_start))
    app.add_handler(CommandHandler("dayansincab", command_stop))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("master", command_master))
    app.add_handler(CommandHandler("sincab_rating", command_sincab_rating))

    app.add_handler(ChatMemberHandler(track_my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, is_word_answered))

    app.run_polling()


if __name__ == "__main__":
    main()
