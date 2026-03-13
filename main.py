import os
import yt_dlp
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

# --- إعدادات السيرفر لإبقاء البوت حياً (Keep Alive) ---
app = Flask('')

@app.route('/')
def home():
    return "MB Gold Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- إعدادات البوت الخاصة بك يا محمد ---
API_TOKEN = '8635678610:AAHtZTMIkSICFyP-a-gAy5WPtPVphXWc6o4'
MY_WALLET = 'UQBS4-2MIVdF1jDxJK0YkDO5z8Y-5vHIk3gQwzZ7egE1PC_'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

ydl_opts = {
    'format': 'best',
    'outtmpl': 'video_%(id)s.mp4',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
}

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    share_button = InlineKeyboardButton(text="📢 مشاركة البوت", switch_inline_query="جرب أفضل بوت تحميل فيديوهات! 🏆")
    keyboard.add(share_button)

    welcome_text = (
        "🏆 **أهلاً بك في MB Gold Downloader**\n\n"
        "أنا بوتك الذكي لتحميل الفيديوهات من:\n"
        "✨ TikTok | Instagram | YouTube\n\n"
        "🚀 **فقط أرسل رابط الفيديو الآن!**\n\n"
        "--- --- --- --- ---\n"
        "👑 **تطوير:** محمد بركات\n"
        "💰 **لدعم المشروع (TON):**\n"
        f"`{MY_WALLET}`"
    )
    await message.reply(welcome_text, parse_mode='Markdown', reply_markup=keyboard)

@dp.message_handler()
async def handle_download(message: types.Message):
    url = message.text
    if not url.startswith("http"):
        return

    status_msg = await message.answer("⏳ **جاري معالجة الرابط... انتظر ثواني**")
    video_file = f"video_{message.from_user.id}.mp4"
    
    try:
        current_opts = ydl_opts.copy()
        current_opts['outtmpl'] = video_file
        
        with yt_dlp.YoutubeDL(current_opts) as ydl:
            ydl.download([url])
        
        with open(video_file, 'rb') as video:
            await bot.send_chat_action(message.chat.id, 'upload_video')
            await message.answer_video(
                video, 
                caption="✅ **تم التحميل بنجاح بواسطة MB Gold**",
                parse_mode='Markdown'
            )
        
        os.remove(video_file)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit("❌ **عذراً، الرابط غير مدعوم أو الحساب خاص.**")
        if os.path.exists(video_file):
            os.remove(video_file)

if __name__ == '__main__':
    print("🚀 MB Gold Bot is starting...")
    keep_alive()  # تشغيل سيرفر الويب الصغير
    executor.start_polling(dp, skip_updates=True)
