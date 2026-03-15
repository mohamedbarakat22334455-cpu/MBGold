import os
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

# --- الإعدادات (تأكد من التوكن والرابط) ---
API_TOKEN = '8579385725:AAGZd2wDPxjFyBq7x6R3AMhMJT46tX6Ld5c'
MY_EARN_LINK = 'https://exe.io/MBABgold' 

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Flask('')

@app.route('/')
def home():
    return "Bot is Live!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("🏆 **MB Gold Downloader**\n\nأرسل رابط الفيديو الآن للمشاهدة والتحميل.\n\n✨ تطوير: محمد بركات", parse_mode="Markdown")

@dp.message_handler()
async def handle_video(message: types.Message):
    if "http" in message.text:
        # رسالة واحدة فقط مؤقتة
        wait_msg = await message.answer("⏳ جاري المعالجة... انتظر ثواني")
        
        # اسم ملف فريد لكل عملية عشان الكود ما يهنقش
        file_name = f"video_{message.chat.id}.mp4"
        
        try:
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': file_name,
                'quiet': True,
                'no_warnings': True,
                'max_filesize': 45 * 1024 * 1024
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([message.text])
            
            if os.path.exists(file_name):
                # إنشاء زر التحميل (رابط الأرباح)
                kb = InlineKeyboardMarkup().add(InlineKeyboardButton("📥 تحميل الفيديو (جودة عالية)", url=MY_EARN_LINK))
                
                with open(file_name, 'rb') as video:
                    await bot.send_video(
                        message.chat.id, 
                        video, 
                        caption="🎬 **تم التجهيز للمشاهدة بنجاح!**\n\nاضغط على الزر أدناه للتحميل المباشر 👇",
                        reply_markup=kb,
                        supports_streaming=True,
                        parse_mode="Markdown"
                    )
                
                os.remove(file_name)
                await wait_msg.delete() # مسح رسالة الانتظار
            else:
                raise Exception("Fail")

        except Exception as e:
            # لو فشل التحميل، نبعت الرابط مباشرة عشان نضمن الربح
            kb = InlineKeyboardMarkup().add(InlineKeyboardButton("🔗 اضغط هنا للمشاهدة والتحميل", url=MY_EARN_LINK))
            await wait_msg.edit_text("❌ الفيديو كبير أو الرابط محمي، شاهده هنا:", reply_markup=kb)

if __name__ == '__main__':
    Thread(target=run).start()
    executor.start_polling(dp, skip_updates=True)
