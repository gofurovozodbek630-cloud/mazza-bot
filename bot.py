opts = {"format": "best[filesize<50M]/best", "outtmpl": f"dl/{chat_id}/%(id)s.%(ext)s", "quiet": True}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            vid_id = info.get("id", "file")
            path = f"dl/{chat_id}/{vid_id}.mp3" if fmt == "audio" else f"dl/{chat_id}/{vid_id}.{info.get('ext', 'mp4')}"
        with open(path, "rb") as f:
            if fmt == "audio":
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
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    print("Mazza Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
