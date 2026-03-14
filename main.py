import os
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
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
    return "MB Gold is Ready!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("🏆 أهلاً بك في MB Gold\nابعت رابط الفيديو وهجهزهولك للمشاهدة فوراً.\n\n✨ تطوير: محمد بركات")

@dp.message_handler()
async def handle_video(message: types.Message):
    if "http" in message.text:
        # رسالة واحدة فقط طول العملية
        status_msg = await message.answer("⏳ جاري التحميل للمشاهدة... انتظر ثواني يا بطل")
        
        try:
            ydl_opts = {
                # إعدادات لضمان المشاهدة المباشرة على تيليجرام
                'format': 'best[ext=mp4]/best',
                'outtmpl': 'video.mp4',
                'quiet': True,
                'no_warnings': True,
                'max_filesize': 45 * 1024 * 1024
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([message.text])
            
            if os.path.exists('video.mp4'):
                with open('video.mp4', 'rb') as video:
                    # نرسل الفيديو ونمسح رسالة "جاري التحميل" عشان ميبقاش فيه رسائل كتير
                    await bot.send_video(
                        message.chat.id, 
                        video, 
                        caption=(
                            f"✅ الفيديو جاهز للمشاهدة!\n\n"
                            f"📥 للتحميل بجودة عالية ودعمنا:\n"
                            f"🔗 {MY_EARN_LINK}\n\n"
                            f"✨ تطوير: محمد بركات"
                        ),
                        supports_streaming=True # أهم سطر للمشاهدة المباشرة
                    )
                os.remove('video.mp4')
                await status_msg.delete() # مسح الرسالة القديمة
            else:
                raise Exception("Error")

        except Exception as e:
            await status_msg.edit_text(f"❌ الفيديو طويل أو الرابط غير مدعوم.\n\nشاهده هنا مباشرة: {MY_EARN_LINK}")

if __name__ == '__main__':
    Thread(target=run).start()
    executor.start_polling(dp, skip_updates=True)
