import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from flask import Flask
from threading import Thread

# التوكن الجديد بتاعك
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
    await message.reply("🏆 أهلاً بك في MB Gold Downloader (النسخة الجديدة)\n\nابعتلي أي رابط فيديو وهجيبهولك فوراً.\n\n✨Mتطوير: Bت")

if __name__ == '__main__':
    Thread(target=run).start()
    executor.start_polling(dp, skip_updates=True)
