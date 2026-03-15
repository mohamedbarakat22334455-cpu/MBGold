import os
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- بياناتك يا محمد ---
API_TOKEN = '8533015825:AAGy7A-Abn3qqW8lwa7b93-Ii92wNTRP_cU'
PROFIT_URL = "https://exe.io/MBABgold"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    await message.reply("🏆 أهلاً بك في MB Gold\nابعت الرابط وهنزلهولك فوراً!")

@dp.message_handler()
async def main_handler(message: types.Message):
    if "http" in message.text:
        wait_msg = await message.answer("⏳ جاري التحميل.. ثواني")
        # اسم الملف المؤقت
        v_name = f"video_{message.from_user.id}.mp4"
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': v_name,
            'quiet': True,
            'no_warnings': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([message.text])
            
            # زرار الربح
            kb = InlineKeyboardMarkup().add(InlineKeyboardButton("🎁 رابط التحميل المباشر", url=PROFIT_URL))
            
            with open(v_name, 'rb') as video:
                await bot.send_video(message.chat.id, video, caption="✅ تم التحميل بواسطة MB Gold", reply_markup=kb)
            
            os.remove(v_name)
            await bot.delete_message(message.chat.id, wait_msg.message_id)
        except Exception as e:
            await message.reply(f"❌ حصل مشكلة: {str(e)[:50]}")
            if os.path.exists(v_name): os.remove(v_name)

if __name__ == '__main__':
    print("البوت بدأ يشتغل.. روح جربه دلوقتي!")
    executor.start_polling(dp, skip_updates=True)
