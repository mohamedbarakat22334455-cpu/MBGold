import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from flask import Flask
from threading import Thread

# --- التوكن الجديد بتاعك ---
API_TOKEN = '8635678610:AAFsa5P0mGupDE0ZbXNhatXZ6QyAicnhDa0'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Flask('')

@app.route('/')
def home():
    return "MB Gold Bot is Online!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- أوامر البوت ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("🏆 أهلاً بك في MB Gold Downloader\n\nابعتلي أي رابط فيديو وهجيبهولك فوراً.\n\n✨ تطوير: محمد بركات")

@dp.message_handler()
async def download(message: types.Message):
    if "http" in message.text:
        await message.reply("⏳ جاري التحميل... انتظر ثواني يا بطل")
        # هنا تقدر تضيف كود الـ yt_dlp لاحقاً، المهم نتأكد إنه بيرد

if __name__ == '__main__':
    # تشغيل سيرفر الويب في Thread منفصل
    server_thread = Thread(target=run)
    server_thread.start()
    
    # تشغيل البوت
    executor.start_polling(dp, skip_updates=True)
