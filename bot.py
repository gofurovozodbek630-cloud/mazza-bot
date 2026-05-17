import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = "8963777053:AAE2FuQAsSjoM0-1q6TRtzfQYVKf8I9cUxE"
USERS = set()

def is_valid_url(text):
    return text.startswith("http://") or text.startswith("https://")

def _search_sync(query):
    opts = {"quiet": True, "skip_download": True, "noplaylist": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"ytsearch5:{query}", download=False)
        return info.get("entries", [])

def _download_sync(url, fmt, chat_id):
    os.makedirs(f"dl/{chat_id}", exist_ok=True)
    if fmt == "audio":
        opts = {"format": "bestaudio/best", "outtmpl": f"dl/{chat_id}/%(id)s.%(ext)s", "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}], "quiet": True}
    else:
        opts = {"format": "best[filesize<50M]/best", "outtmpl": f"dl/{chat_id}/%(id)s.%(ext)s", "quiet": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        vid_id = info.get("id", "file")
        ext = "mp3" if fmt == "audio" else info.get("ext", "mp4")
        return f"dl/{chat_id}/{vid_id}.{ext}", info.get("title", "")

async def start(update, ctx):
    user = update.effective_user
    USERS.add(user.id)
    await update.message.reply_text(f"🎵 Mazza Bot ga xush kelibsiz, {user.first_name}!\n\n📎 Havola yuboring — video yoki MP3 yuklayman\n🔍 Qoshiq nomi yozing — topib beraman!")

async def stats(update, ctx):
    await update.message.reply_text(f"📊 Statistika:\n\n👥 Foydalanuvchilar: {len(USERS)} ta")

async def help_cmd(update, ctx):
    await update.message.reply_text("📖 Yordam:\n\n1. Havola yuboring → Video yoki MP3\n2. Qoshiq nomi yozing → Topib beraman\n\nMisol: Shaxriyor Umirov Xayol")

async def about(update, ctx):
    await update.message.reply_text("🤖 Mazza Bot\n\nYouTube, TikTok, Instagram va boshqa saytlardan video va musiqa yuklab beruvchi bot!\n\n@MazzaUzbekbot")

async def handle_url(update, ctx):
    user = update.effective_user
    USERS.add(user.id)
    text = update.message.text.strip()
    if is_valid_url(text):
        ctx.user_data["url"] = text
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Video", callback_data="video"), InlineKeyboardButton("🎵 MP3", callback_data="audio")]])
        await update.message.reply_text("✅ Topildi! Formatni tanlang:", reply_markup=keyboard)
    else:
        msg = await update.message.reply_text("🔍 Qidirilmoqda...")
        try:
            loop = asyncio.get_event_loop()
            entries = await loop.run_in_executor(None, lambda: _search_sync(text))
            if not entries:
                await msg.edit_text("❌ Hech narsa topilmadi!")
                return
            buttons = []
            for i, entry in enumerate(entries[:5]):
                title = entry.get("title", "Noma'lum")[:35]
                dur = entry.get("duration", 0)
                m, s = divmod(dur, 60)
                buttons.append([InlineKeyboardButton(f"🎵 {title} ({m}:{s:02d})", callback_data=f"s_{i}")])
            ctx.user_data["results"] = entries[:5]
            await msg.edit_text("🎵 Natijalar:", reply_markup=InlineKeyboardMarkup(buttons))
        except Exception as e:
            await msg.edit_text(f"❌ Xato: {str(e)[:100]}")

async def handle_callback(update, ctx):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id
    loop = asyncio.get_event_loop()
    if data.startswith("s_"):
        idx = int(data[2:])
        entries = ctx.user_data.get("results", [])
        entry = entries[idx]
        url = entry.get("webpage_url") or f"https://youtube.com/watch?v={entry.get('id')}"
        ctx.user_data["url"] = url
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Video", callback_data="video"), InlineKeyboardButton("🎵 MP3", callback_data="audio")]])
        await query.edit_message_text(f"✅ {entry.get('title','')[:50]}\n\nFormatni tanlang:", reply_markup=keyboard)
        return
    url = ctx.user_data.get("url")
    fmt = data
    await query.edit_message_text("⏳ Yuklanmoqda...")
    try:
        path, title = await loop.run_in_executor(None, lambda: _download_sync(url, fmt, chat_id))
        with open(path, "rb") as f:
            if fmt == "audio":
                await ctx.bot.send_audio(chat_id=chat_id, audio=f, title=title, caption="🎵 @MazzaUzbekbot")
            else:
                await ctx.bot.send_video(chat_id=chat_id, video=f, caption="🎬 @MazzaUzbekbot")
        await query.delete_message()
        os.remove(path)
    except Exception as e:
        await query.edit_message_text(f"❌ Xato: {str(e)[:100]}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    print("Mazza Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
