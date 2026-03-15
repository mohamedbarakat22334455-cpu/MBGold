import os, sqlite3, asyncio, yt_dlp, shutil
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# --- [ إعدادات MBAB ] ---
API_TOKEN = '8579385725:AAGZd2wDPxjFyBq7x6R3AMhMJT46tX6Ld5c'
ADMIN_ID = 123456789  # <--- حط الـ ID بتاعك هنا

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- [ قاعدة البيانات ] ---
conn = sqlite3.connect('mbab_master.db', check_same_thread=False)
db = conn.cursor()
db.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0)')
conn.commit()

# --- [ نظام البداية ] ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    await message.reply("🏆 **أهلاً بك في نظام MBAB**\n\nابعت أي رابط فيديو (يوتيوب، تيك توك، إنستا) وهبعتهولك فيديو بالصوت فوراً.")

# --- [ محرك التحميل الاحترافي ] ---
async def download_task(url, file_path):
    # إعدادات تضمن التحميل حتى لو السيرفر ضعيف
    ydl_opts = {
        'format': 'best[ext=mp4]/best', # بيجيب فيديو بصوت جاهز مدمج
        'outtmpl': file_path,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'cachedir': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: ydl.download([url]))

@dp.message_handler(lambda m: "http" in m.text)
async def handle_download(message: types.Message):
    url = message.text.strip()
    user_id = message.from_user.id
    wait_msg = await message.answer("⏳ **جاري التحميل بواسطة MBAB...**")
    
    file_path = f"video_{user_id}.mp4"

    try:
        # تنفيذ التحميل في خلفية البرنامج
        await download_task(url, file_path)

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'rb') as video:
                await bot.send_video(message.chat.id, video, caption="✅ تم بواسطة MBAB")
            await wait_msg.delete()
        else:
            await wait_msg.edit_text("❌ فشل التحميل. الرابط قد يكون خاصاً أو غير مدعوم.")
            
    except Exception as e:
        await wait_msg.edit_text("❌ حدث خطأ فني أثناء المعالجة.")
        print(f"ERROR: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# --- [ نظام الإعلانات للأدمن ] ---
@dp.message_handler(commands=['admin'])
async def admin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        db.execute("SELECT COUNT(*) FROM users")
        count = db.fetchone()[0]
        await message.reply(f"👑 **لوحة تحكم MBAB**\n\nعدد الأعضاء: {count}\nلإرسال إعلان، أرسل النص مباشرة.")

if __name__ == '__main__':
    print("MBAB SYSTEM IS ONLINE!")
    executor.start_polling(dp, skip_updates=True)
