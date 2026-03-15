import os
import yt_dlp
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from flask import Flask
from threading import Thread
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- الإعدادات الأساسية ---
API_TOKEN = '8579385725:AAGZd2wDPxjFyBq7x6R3AMhMJT46tX6Ld5c'
ADMIN_ID = 123456789  # <--- حط الـ ID بتاعك هنا عشان لوحة التحكم تشتغل
MY_EARN_LINK = 'https://exe.io/MBABgold' 

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Flask('')

# --- إعداد قاعدة البيانات لحفظ المستخدمين ---
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
conn.commit()

@app.route('/')
def home():
    return "MB Gold is Active!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# حفظ المستخدم الجديد
def add_user(user_id):
    try:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
    except:
        pass

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    add_user(message.from_user.id)
    await message.reply("🏆 **MB Gold Downloader**\n\nأرسل رابط الفيديو للمشاهدة فوراً.\n\n✨ تطوير: محمد بركات", parse_mode="Markdown")

# لوحة تحكم الأدمن (Broadcast)
@dp.message_handler(commands=['broadcast'])
async def broadcast(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        msg_text = message.text.replace('/broadcast', '').strip()
        if not msg_text:
            return await message.reply("اكتب الرسالة بعد الأمر، مثال:\n/broadcast أهلاً بكم")
        
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        count = 0
        for user in users:
            try:
                await bot.send_message(user[0], msg_text)
                count += 1
            except:
                pass
        await message.reply(f"✅ تم إرسال الرسالة إلى {count} مستخدم.")

@dp.message_handler()
async def handle_video(message: types.Message):
    if "http" in message.text:
        status = await message.answer("⏳ جاري تجهيز الفيديو...")
        file_path = f"vid_{message.chat.id}.mp4"
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': file_path,
            'quiet': True,
            'no_warnings': True,
            'max_filesize': 48 * 1024 * 1024 # تليجرام بيسمح بـ 50 ميجا للبوتات العادية
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([message.text])
            
            if os.path.exists(file_path):
                with open(file_path, 'rb') as video:
                    await bot.send_video(
                        message.chat.id, 
                        video, 
                        caption="🎬 **مشاهدة ممتعة من MB Gold**",
                        supports_streaming=True,
                        parse_mode="Markdown"
                    )
                
                # إرسال رابط الأرباح مع زرار احترافي
                kb = InlineKeyboardMarkup().add(InlineKeyboardButton("📥 تحميل بجودة عالية", url=MY_EARN_LINK))
                await message.answer("لتحميل الفيديو بجودة أعلى ودعمنا، اضغط على الزر:", reply_markup=kb)
                
                os.remove(file_path)
                await status.delete()
            else:
                raise Exception("Fail")

        except Exception as e:
            await status.edit_text(f"❌ الفيديو كبير جداً أو محمي.\nيمكنك محاولة تحميله من هنا: {MY_EARN_LINK}")
            if os.path.exists(file_path): os.remove(file_path)

if __name__ == '__main__':
    Thread(target=run).start()
    print("🚀 MB Gold Bot IS FULLY ACTIVE...")
    executor.start_polling(dp, skip_updates=True)
