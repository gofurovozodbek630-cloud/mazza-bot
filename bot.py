import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = "8963777053:AAE2FuQAsSjoM0-1q6TRtzfQYVKf8I9cUxE"

def is_valid_url(text):
    return text.startswith("http://") or text.startswith("https://")

async def start(update, ctx):
    await update.message.reply_text("🎵 Mazza Bot ga xush kelibsiz!\n\nVideo yoki musiqa havolasini yuboring!")

async def handle_url(update, ctx):
    url = update.message.text.strip()
    if not is_valid_url(url):
        await update.message.reply_text("❌ Havola yuboring!")
        return
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎬 Video", callback_data="video"),
        InlineKeyboardButton("🎵 MP3", callback_data="audio")
    ]])
    ctx.user_data["url"] = url
    await update.message.reply_text("✅ Topildi! Formatni tanlang:", reply_markup=keyboard)

async def handle_callback(update, ctx):
    query = update.callback_query
    await query.answer()
    url = ctx.user_data.get("url")
    fmt = query.data
    await query.edit_message_text("⏳ Yuklanmoqda...")
    chat_id = query.message.chat_id
    os.makedirs(f"dl/{chat_id}", exist_ok=True)
    if fmt == "audio":
        opts = {"format":"bestaudio/best","outtmpl":f"dl/{chat_id}/%(id)s.%(ext)s","postprocessors":[{"key":"FFmpegExtractAudio","preferredcodec":"mp3","preferredquality":"192"}],"quiet":True}
    else:
        opts = {"format":"best[filesize<50M]/best","outtmpl":f"dl/{chat_id}/%(id)s.%(ext)s","quiet":True}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            vid_id = info.get("id","file")
            path = f"dl/{chat_id}/{vid_id}.mp3" if fmt=="audio" else f"dl/{chat_id}/{vid_id}.{info.get('ext','mp4')}"
        with open(path,"rb") as f:
            if fmt=="audio":
                await ctx.bot.send_audio(chat_id=chat_id, audio=f, caption="🎵 @MazzaUzbekbot")
            else:
                await ctx.bot.send_video(chat_id=chat_id, video=f, caption="🎬 @MazzaUzbekbot")
        await query.delete_message()
        os.remove(path)
    except Exception as e:
        await query.edit_message_text(f"❌ Xato: {str(e)[:100]}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    print("🎵 Mazza Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
  
