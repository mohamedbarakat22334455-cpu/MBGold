import os
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

# --- إعدادات محمد بركات ---
API_TOKEN = '8579385725:AAGZd2wDPxjFyBq7x6R3AMhMJT46tX6Ld5c'
MY_EARN_LINK = 'https://shrinkme.click/h3CBu' 

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Flask('')

@app.route('/')
def home():
    return "MB Gold Pro is Active!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # شكل ترحيبي احترافي
    welcome_text = (
        "🏆 **أهلاً بك في MB Gold Pro**\n\n"
        "أنا بوت التحميل الأسرع على تليجرام.\n"
        "فقط أرسل لي رابط الفيديو (TikTok, Reels, Shorts).\n\n"
        "✨*MBتطوير:** ت"
    )
    await message.reply(welcome_text, parse_mode="Markdown")

@dp.message_handler()
async def handle_video(message: types.Message):
    if "http" in message.text:
        # رسالة جاري التحميل بيمسحها البوت فوراً
        status_msg = await message.answer("⏳ **جاري جلب الفيديو للمشاهدة...**", parse_mode="Markdown")
        
        try:
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': 'video.mp4',
                'quiet': True,
                'no_warnings': True,
                'max_filesize': 48 * 1024 * 1024
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([message.text])
            
            if os.path.exists('video.mp4'):
                # إنشاء زرار تحميل احترافي تحت الفيديو
                keyboard = InlineKeyboardMarkup()
                btn_download = InlineKeyboardButton("📥 تحميل بجودة عالية (Direct)", url=MY_EARN_LINK)
                keyboard.add(btn_download)

                with open('video.mp4', 'rb') as video:
                    await bot.send_video(
                        message.chat.id, 
                        video, 
                        caption="🎬 **مشاهدة ممتعة من MB Gold**\n\nلتحميل الفيديو على جهازك اضغط على الزر أدناه 👇",
                        reply_markup=keyboard,
                        supports_streaming=True,
                        parse_mode="Markdown"
                    )
                
                os.remove('video.mp4')
                await status_msg.delete() # مسح رسالة التحميل فوراً
            else:
                raise Exception("Error")

        except Exception:
            # لو الفيديو فشل نبعت زرار الأرباح مباشرة
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("🔗 مشاهدة وتحميل عبر الرابط", url=MY_EARN_LINK))
            await status_msg.edit_text("❌ **الفيديو كبير أو الرابط محمي.**\nاستخدم الرابط المدعوم أدناه:", reply_markup=keyboard, parse_mode="Markdown")

if __name__ == '__main__':
    Thread(target=run).start()
    executor.start_polling(dp, skip_updates=True)
