import os
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- الإعدادات (تعديل بسيط) ---
API_TOKEN = '8533015825:AAGy7A-Abn3qqW8lwa7b93-Ii92wNTRP_cU'
PROFIT_URL = "https://exe.io/MBABgold"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply(f"🏆 أهلاً بك يا بطل في MB Gold Downloader\n\nابعتلي أي رابط فيديو وهحملهولك فوراً.")

@dp.message_handler()
async def download(message: types.Message):
    if "http" in message.text:
        msg = await message.answer("⏳ جاري التحميل.. ثواني يا محمد")
        file_path = "video.mp4"
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': file_path,
            'quiet': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([message.text])
            
            # زرار الربح بتاعك
            kb = InlineKeyboardMarkup().add(InlineKeyboardButton("🎁 ادعمني هنا", url=PROFIT_URL))
            
            with open(file_path, 'rb') as video:
                await bot.send_video(message.chat.id, video, caption="✅ تم بواسطة MB Gold", reply_markup=kb)
            
            os.remove(file_path) # مسح الفيديو عشان الجهاز ما يتمليش
            await bot.delete_message(message.chat.id, msg.message_id)
        except:
            await message.reply("❌ فيه مشكلة في الرابط ده يا بطل.")

if __name__ == '__main__':
    print("البوت شغال دلوقتي.. روح جربه في تليجرام!")
    executor.start_polling(dp, skip_updates=True)
