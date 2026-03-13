import os
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from flask import Flask
from threading import Thread

# --- التوكن بتاعك يا بطل ---
API_TOKEN ='8635678610:AAHtZTMIkSICFyP-a-gAy5WPtPVphXWc6o4'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- سيرفر صغير عشان Railway ميفصلش البوت ---
app = Flask('')

@app.route('/')
def home():
    return "MB Gold Bot is Online!"

def run():
    # بنقرأ الـ Port اللي Railway بيديهولنا تلقائي
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- أوامر البوت الأساسية ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("🏆 أهلاً بك في MB Gold Downloader\n\n"
                       "ابعتلي أي رابط فيديو (تيك توك، إنستجرام، يوتيوب) وهجيبهولك فوراً.\n\n"
                       "تطوير: MB  ت")

@dp.message_handler()
async def download(message: types.Message):
    if "http" in message.text:
        status_msg = await message.answer("⏳ جاري التحميل... انتظر ثواني يا بطل")
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'video.mp4',
                'quiet': True,
                'no_warnings': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([message.text])
            
            with open('video.mp4', 'rb') as video:
                await bot.send_video(message.chat.id, video, caption="✅ تم التحميل بنجاح بواسطة MB Gold")
            
            os.remove('video.mp4')
            await bot.delete_message(message.chat.id, status_msg.message_id)
        except Exception as e:
            await message.reply("❌ الرابط ده فيه مشكلة أو مش مدعوم حالياً.")
            if os.path.exists("video.mp4"): os.remove("video.mp4")

if __name__ == '__main__':
    keep_alive() # تشغيل السيرفر في الخلفية
    executor.start_polling(dp, skip_updates=True)
