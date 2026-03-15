import os
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from flask import Flask
from threading import Thread

# --- الإعدادات الأساسية ---
API_TOKEN = '8579385725:AAGZd2wDPxjFyBq7x6R3AMhMJT46tX6Ld5c'
MY_EARN_LINK = 'https://shrinkme.click/h3CBu' 

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Flask('')

@app.route('/')
def home():
    return "MB Gold is Active!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("🏆 **MB Gold Downloader**\n\nأرسل رابط الفيديو للمشاهدة فوراً.\n\n✨ تطوير: محمد بركات", parse_mode="Markdown")

@dp.message_handler()
async def handle_video(message: types.Message):
    if "http" in message.text:
        # رسالة مؤقتة واحدة
        status = await message.answer("⏳ جاري تجهيز الفيديو للمشاهدة...")
        
        # اسم ملف فريد عشان نمنع تداخل الفيديوهات
        file_path = f"vid_{message.chat.id}.mp4"
        
        try:
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': file_path,
                'quiet': True,
                'max_filesize': 45 * 1024 * 1024
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([message.text])
            
            if os.path.exists(file_path):
                # 1. إرسال الفيديو للمشاهدة أولاً
                with open(file_path, 'rb') as video:
                    await bot.send_video(
                        message.chat.id, 
                        video, 
                        caption="🎬 **مشاهدة ممتعة من MB Gold**",
                        supports_streaming=True,
                        parse_mode="Markdown"
                    )
                
                # 2. إرسال رابط الأرباح للتحميل في رسالة تانية (زي ما طلبت)
                await message.answer(
                    f"📥 **لتحميل الفيديو بجودة عالية ودعمنا:**\n🔗 {MY_EARN_LINK}",
                    parse_mode="Markdown"
                )
                
                # تنظيف: مسح الفيديو ورسالة الانتظار
                os.remove(file_path)
                await status.delete()
            else:
                raise Exception("Fail")

        except Exception:
            await status.edit_text(f"❌ الفيديو كبير أو الرابط محمي.\nشاهده هنا: {MY_EARN_LINK}")

if __name__ == '__main__':
    Thread(target=run).start()
    executor.start_polling(dp, skip_updates=True)
