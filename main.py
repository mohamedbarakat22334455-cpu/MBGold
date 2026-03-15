import os, sqlite3, datetime, yt_dlp, shutil, asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- [ إعدادات MBAB ] ---
API_TOKEN = '8579385725:AAGZd2wDPxjFyBq7x6R3AMhMJT46tX6Ld5c'
ADMIN_ID = 123456789  # <--- حط الـ ID بتاعك هنا
CHANNEL_LINK = "https://t.me/MBABmbab"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- [ قاعدة البيانات ] ---
conn = sqlite3.connect('mbab_pro.db', check_same_thread=False)
db = conn.cursor()
db.execute('''CREATE TABLE IF NOT EXISTS users 
             (user_id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0, last_active TEXT)''')
conn.commit()

# --- [ نظام التشغيل ] ---
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    db.execute("INSERT OR IGNORE INTO users (user_id, last_active) VALUES (?, ?)", 
               (user_id, str(datetime.datetime.now())))
    conn.commit()
    
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("💰 رصيدي", callback_data="p"),
        InlineKeyboardButton("📢 القناة", url=CHANNEL_LINK)
    )
    await message.reply(f"🏆 **مرحباً بك في بوت MBAB للتحميل**\n\nابعت أي رابط فيديو دلوقتي وهيتحمل فوراً بالصوت والصورة.", reply_markup=kb)

# --- [ المحرك اللي هيشغل الخدمات فعلياً ] ---
@dp.message_handler(lambda message: "http" in message.text)
async def downloader_service(message: types.Message):
    url = message.text.strip()
    wait_msg = await message.reply("⏳ جاري سحب الفيديو... ثواني يا بطل")
    
    user_folder = f"temp_{message.from_user.id}"
    if not os.path.exists(user_folder): os.makedirs(user_folder)
    
    # الإعدادات دي هي اللي بتخلي الخدمة "تشتغل" فعلاً
    ydl_opts = {
        'format': 'best',  # اختيار أفضل جودة مدمجة جاهزة عشان ميحتاجش FFmpeg لو مش عندك
        'outtmpl': f'{user_folder}/video.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    try:
        loop = asyncio.get_event_loop()
        # استخراج المعلومات والتحميل
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True))
        filename = yt_dlp.YoutubeDL(ydl_opts).prepare_filename(info)

        if os.path.exists(filename):
            with open(filename, 'rb') as video:
                await bot.send_video(message.chat.id, video, caption="✅ تم التحميل بواسطة MBAB")
            await wait_msg.delete()
        else:
            await wait_msg.edit_text("❌ الخدمة مشغولة حالياً أو الرابط غير مدعوم.")
            
    except Exception as e:
        await wait_msg.edit_text("❌ حدث خطأ في معالجة الرابط. تأكد أن الفيديو عام وليس خاص.")
        print(f"Error: {e}")
    finally:
        shutil.rmtree(user_folder, ignore_errors=True)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
