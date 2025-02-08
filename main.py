import io
import os
import filetype
from dotenv import load_dotenv
from PIL import Image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# .env fayldan TOKEN olish
load_dotenv()
TOKEN = os.getenv("8193848501:AAGo6vgyc4bXqSidjZNSSptbWb8T2zQQywk")
TOKEN = "8193848501:AAGo6vgyc4bXqSidjZNSSptbWb8T2zQQywk"



# Kanallar ro‘yxati
CHANNELS = ["@skromni3", "@qiziqlari_bizda"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Bot ishga tushganda foydalanuvchini kutib oladi"""
    keyboard = [
        [InlineKeyboardButton("🔗 Kanal 1", url=f"https://t.me/{CHANNELS[0][1:]}")],
        [InlineKeyboardButton("🔗 Kanal 2", url=f"https://t.me/{CHANNELS[1][1:]}")],
        [InlineKeyboardButton("✅ Tasdiqlash", callback_data="verify")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Salom! Rasm yuborish uchun siz quyidagi kanallarga a'zo bo‘lishingiz kerak:",
        reply_markup=reply_markup
    )

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tasdiqlash tugmasi bosilganda kanallarga a'zolikni tekshiradi"""
    query = update.callback_query
    user = query.from_user

    for channel in CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel, user.id)
            if member.status not in ["member", "administrator", "creator"]:
                await query.answer(f"🚨 Siz {channel} kanaliga a'zo emassiz!", show_alert=True)
                return
        except Exception:
            await query.answer(f"⚠ {channel} kanaliga tekshiruv muvaffaqiyatsiz!", show_alert=True)
            return

    await query.message.edit_text("✅ Siz muvaffaqiyatli tasdiqlandingiz! Endi rasm yuborishingiz mumkin.")

async def check_image(image_data):
    """Rasm formatini tekshiradi"""
    try:
        kind = filetype.guess(image_data)
        if kind is None or kind.mime.split("/")[0] != "image":
            return False

        image = Image.open(io.BytesIO(image_data))
        image.verify()
        return True
    except Exception:
        return False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Foydalanuvchi rasm yuborganda uni tekshiradi"""
    if update.message.photo:
        # Kutish xabari yuboriladi
        waiting_message = await update.message.reply_text('⏳ Iltimos, kuting...')

        # Rasmni olish
        file = await update.message.photo[-1].get_file()
        image_data = await file.download_as_bytearray()

        # Rasm tekshiriladi
        if await check_image(image_data):
            await waiting_message.edit_text('✅ Rasm muvaffaqiyatli tasdiqlandi!')
        else:
            await waiting_message.edit_text('❌ Xatolik! Iltimos, boshqa rasm yuboring.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Foydalanuvchiga yordam beruvchi qo‘llanma"""
    await update.message.reply_text(
        "ℹ️ Buyruqlar ro‘yxati:\n"
        "/start - Botni ishga tushirish\n"
        "/help - Yordam olish\n"
        "📸 Rasm yuboring va uni tekshiramiz!"
        "Bot yaratuvchi @just_a1one"
    )

def main() -> None:
    """Botni ishga tushurish"""
    if not TOKEN:
        raise ValueError("Bot token topilmadi! .env faylda TOKEN borligini tekshiring.")

    application = Application.builder().token(TOKEN).build()

    # Handlerlarni qo'shish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(verify, pattern="verify"))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))

    # Botni ishga tushirish
    application.run_polling()

if __name__ == '__main__':
    main()
