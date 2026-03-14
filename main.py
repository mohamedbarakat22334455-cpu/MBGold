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
    return "MB Gold Bot is Online!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("🏆 أهلاً بك في MB Gold\nابعتلي رابط فيديو قصير (تيك توك، ريلز، يوتيوب) وهجيبهولك فوراً.\n\n✨ تطوير: MBت")

@dp.message_handler()
async def handle_video(message: types.Message):
    if "http" in message.text:
        # إرسال رابط الأرباح أولاً كدعم
        await message.answer(f"⏳ جاري تجهيز الفيديو.. لدعمنا اضغط هنا:\n🔗 {MY_EARN_LINK}")
        
        status_msg = await message.answer("🚀 جاري التحميل الآن...")
        
        try:
            # إعدادات مخصصة للفيديوهات القصيرة (تيك توك وريلز)
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': 'video.mp4',
                'quiet': True,
                'no_warnings': True,
                'max_filesize': 45 * 1024 * 1024
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([message.text])
            
            # إرسال الفيديو كملف مرئي (مشاهدة مباشرة)
            if os.path.exists('video.mp4'):
                with open('video.mp4', 'rb') as video:
                    await bot.send_video(
                        message.chat.id, 
                        video, 
                        caption="✅ تم التحميل بواسطة MB Gold\n\n✨ شكراً لمشاهدتك",
                        timeout=300 # وقت كافٍ للرفع
                    )
                os.remove('video.mp4')
                await bot.delete_message(message.chat.id, status_msg.message_id)
        
        except Exception as e:
            await message.reply("❌ عذراً، لم أستطع تحميل هذا الفيديو كملف.\nيمكنك مشاهدته عبر رابط الدعم:")
            await message.answer(f"🔗 {MY_EARN_LINK}")
            if os.path.exists("video.mp4"): os.remove("video.mp4")

if __name__ == '__main__':
    Thread(target=run).start()
    executor.start_polling(dp, skip_updates=True)
