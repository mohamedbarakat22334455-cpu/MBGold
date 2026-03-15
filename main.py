import os
import sqlite3
import datetime
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- الإعدادات (برمجة محمد بركات) ---
API_TOKEN = '8579385725:AAGZd2wDPxjFyBq7x6R3AMhMJT46tX6Ld5c'
ADMIN_ID = 123456789  # <--- حط الـ ID بتاعك هنا (مهم جداً)
MY_EARN_LINK = 'https://exe.io/MBABgold'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- نظام قاعدة البيانات ---
conn = sqlite3.connect('mb_gold.db', check_same_thread=False)
db = conn.cursor()
db.execute('''CREATE TABLE IF NOT EXISTS users 
             (user_id INTEGER PRIMARY KEY, last_seen TEXT)''')
conn.commit()

def update_user(user_id):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.execute("INSERT OR REPLACE INTO users (user_id, last_seen) VALUES (?, ?)", (user_id, now))
    conn.commit()

# --- لوحة تحكم الأدمن (محمد بركات فقط) ---

@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        # إحصائيات الزوار
        db.execute("SELECT COUNT(*) FROM users")
        total_users = db.fetchone()[0]
        
        # إحصائيات المتصلين (آخر 24 ساعة مثلاً)
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        db.execute("SELECT COUNT(*) FROM users WHERE last_seen > ?", (yesterday,))
        active_today = db.fetchone()[0]
        
        text = (f"👑 **أهلاً بك يا محمد في لوحة التحكم**\n\n"
                f"📊 إجمالي الزوار (الكل): `{total_users}`\n"
                f"🟢 المتصلين آخر 24 ساعة: `{active_today}`\n\n"
                f"📢 للارسال للكل استخدم: `/broadcast` متبوعاً بنص الرسالة")
        await message.reply(text, parse_mode="Markdown")

@dp.message_handler(commands=['broadcast'])
async def broadcast_cmd(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        msg_text = message.text.replace('/broadcast', '').strip()
        if not msg_text:
            return await message.reply("❌ اكتب الرسالة بعد الأمر! مثال:\n`/broadcast كل سنة وأنتم طيبين`")
        
        db.execute("SELECT user_id FROM users")
        all_users = db.fetchall()
        
        success = 0
        await message.answer(f"⏳ جاري الإرسال لـ {len(all_users)} مستخدم...")
        
        for user in all_users:
            try:
                await bot.send_message(user[0], msg_text)
                success += 1
            except:
                pass
        
        await message.answer(f"✅ تم الإرسال بنجاح لـ `{success}` مستخدم.")

# --- نظام التحميل العام ---

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    update_user(message.from_user.id)
    await message.reply(f"🏆 **MB Gold Downloader**\n\nأهلاً بك يا {message.from_user.first_name}\nأرسل رابط الفيديو للتحميل فوراً.\n\n✨ المطور: محمد بركات")

@dp.message_handler()
async def dl_handler(message: types.Message):
    update_user(message.from_user.id) # تحديث وقت التواجد
    
    if "http" in message.text:
        status = await message.answer("⏳ جاري المعالجة...")
        file_name = f"video_{message.from_user.id}.mp4"
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': file_name,
            'quiet': True,
            'max_filesize': 45 * 1024 * 1024
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([message.text])
            
            with open(file_name, 'rb') as video:
                # أزرار احترافية
                kb = InlineKeyboardMarkup().add(InlineKeyboardButton("📥 رابط التحميل المباشر", url=MY_EARN_LINK))
                await bot.send_video(message.chat.id, video, caption="✅ تم بواسطة MB Gold", reply_markup=kb)
            
            os.remove(file_name)
            await status.delete()
        except Exception:
            await status.edit_text(f"❌ عذراً، الرابط غير مدعوم أو الحجم كبير.\nجرب هنا: {MY_EARN_LINK}")
            if os.path.exists(file_name): os.remove(file_name)

if __name__ == '__main__':
    print("🚀 البوت شغال يا محمد ولوحة التحكم جاهزة!")
    executor.start_polling(dp, skip_updates=True)
