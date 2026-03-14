
import os
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from flask import Flask
from threading import Thread

# --- إعدادات البوت ---
API_TOKEN = '8579385725:AAGZd2wDPxjFyBq7x6R3AMhMJT46tX6Ld5c'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Flask('')

@app.route('/')
def home():
    return "MB Gold Bot is Online!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("🏆 أهلاً بك في MB Gold Downloader\n\nابعتلي أي رابط فيديو (تيك توك، يوتيوب، إنستجرام) وهجيبهولك فوراً.\n\n✨ MBAتطوير: ت")

@dp.message_handler()
async def download_video(message: types.Message):
    if "http" in message.text:
        status_msg = await message.reply("⏳ جاري التحميل... انتظر ثواني يا بطل")
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
    Thread(target=run).start()
    executor.start_polling(dp, skip_updates=True)
