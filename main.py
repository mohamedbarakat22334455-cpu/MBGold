import os
import yt_dlp
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- الإعدادات (برمجة محمد بركات) ---
API_TOKEN = '8533015825:AAGy7A-Abn3qqW8lwa7b93-Ii92wNTRP_cU'
ADMIN_ID = 123456789  # حط الـ ID بتاعك هنا
PROFIT_URL = "https://exe.io/MBABgold"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# إنشاء مجلد للتحميلات إذا لم يكن موجوداً
if not os.path.exists('downloads'):
    os.makedirs('downloads')

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    user_name = message.from_user.first_name
    await message.reply(f"🏆 أهلاً بك يا {user_name} في MB Gold Downloader\n\n"
                        "🚀 أنا أسرع بوت لتحميل الفيديوهات من:\n"
                        "• TikTok (بدون علامة مائية)\n"
                        "• Instagram (Reels & Story)\n"
                        "• YouTube (All Qualities)\n\n"
                        "فقط أرسل الرابط واترك الباقي عليّ!")

@dp.message_handler(commands=['broadcast'])
async def broadcast(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        msg_text = message.text.replace('/broadcast', '')
        if msg_text:
            # هنا يمكنك إضافة نظام لقاعدة البيانات لإرسال للكل
            await message.reply("📢 جاري إرسال الإعلان لجميع المستخدمين...")
        else:
            await message.reply("الرجاء كتابة نص الرسالة بعد الأمر.")

@dp.message_handler()
async def download_video(message: types.Message):
    url = message.text
    if not url.startswith("http"):
        return

    status_msg = await message.answer("🔍 جاري فحص الرابط ومعالجته...")

    # إعدادات التحميل الاحترافية
    file_path = f"downloads/{message.from_user.id}.mp4"
    ydl_opts = {
        'format': 'best',
        'outtmpl': file_path,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'Video')

        # إنشاء أزرار الربح والتحميل
        keyboard = InlineKeyboardMarkup(row_width=1)
        btn_profit = InlineKeyboardButton(text="🎁 ادعمني بالضغط هنا (رابط العيدية)", url=PROFIT_URL)
        keyboard.add(btn_profit)

        # إرسال الفيديو للمستخدم
        await message.answer_chat_action("upload_video")
        with open(file_path, 'rb') as video:
            await bot.send_video(
                message.chat.id, 
                video, 
                caption=f"✅ تم التحميل بنجاح بواسطة MB Gold\n📌 {video_title}",
                reply_markup=keyboard
            )
        
        # حذف الملف بعد الإرسال لتوفير مساحة السيرفر
        os.remove(file_path)
        await bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        await message.reply("❌ عذراً، حدث خطأ أثناء التحميل. تأكد من صحة الرابط.")
        if os.path.exists(file_path):
            os.remove(file_path)
        print(f"Error: {e}")

if __name__ == '__main__':
    print("🚀 MB Gold Bot IS RUNNING...")
    executor.start_polling(dp, skip_updates=True)
