import os, sqlite3, datetime, yt_dlp, shutil, asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice

# --- [ إعدادات MBAB الرئيسية ] ---
API_TOKEN = '8579385725:AAGZd2wDPxjFyBq7x6R3AMhMJT46tX6Ld5c'
ADMIN_ID = 123456789  # <--- ضع الـ ID الخاص بك هنا
CHANNEL_LINK = "https://t.me/MBABmbab"
MY_PRIVATE_LINK = "https://t.me/M_Barakat"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- [ إعداد قاعدة البيانات الاحترافية ] ---
conn = sqlite3.connect('mbab_mega_system.db', check_same_thread=False)
db = conn.cursor()
db.execute('''CREATE TABLE IF NOT EXISTS users 
             (user_id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0, 
              invited_by INTEGER, last_active TEXT, is_banned INTEGER DEFAULT 0)''')
conn.commit()

# --- [ وظائف المساعدة ] ---
def get_user(user_id):
    db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return db.fetchone()

# --- [ أوامر الأدمن (لوحة التحكم) ] ---
@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        db.execute("SELECT COUNT(*) FROM users")
        total_users = db.fetchone()[0]
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("📢 إذاعة للكل", callback_data="bc"),
            InlineKeyboardButton("📊 إحصائيات", callback_data="stats")
        )
        await message.reply(f"👑 **مرحباً مطور MBAB**\n\nعدد المستخدمين: `{total_users}`\nتحكم في البوت من هنا:", reply_markup=kb)

# --- [ نظام التشغيل والتحميل ] ---
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    if user and user[4] == 1: return await message.reply("🚫 أنت محظور من استخدام البوت.")

    if not user:
        args = message.get_args()
        inviter = int(args) if args and args.isdigit() and int(args) != user_id else None
        db.execute("INSERT INTO users (user_id, invited_by, last_active) VALUES (?, ?, ?)", 
                   (user_id, inviter, str(datetime.datetime.now())))
        if inviter:
            db.execute("UPDATE users SET points = points + 1 WHERE user_id = ?", (inviter,))
            try: await bot.send_message(inviter, "🚀 مبروك! دخل مستخدم جديد من رابطك (+1 نقطة)")
            except: pass
        conn.commit()

    kb = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("💰 رصيدي", callback_data="p"),
        InlineKeyboardButton("💳 سحب رصيد", callback_data="wd"),
        InlineKeyboardButton("⭐️ تواصل", callback_data="stars"),
        InlineKeyboardButton("📢 القناة الرسمية", url=CHANNEL_LINK)
    )
    
    await message.reply(f"🏆 **أهلاً بك في نظام MBAB المتطور**\n\nأرسل رابط أي فيديو وسأقوم بتحميله لك فوراً بأعلى جودة مدمجة بالصوت.\n\n🎁 نظام النقاط: 100 نقطة = 15 جنيه.", reply_markup=kb)

# --- [ المحرك الشامل للتحميل ] ---
@dp.message_handler(lambda message: "http" in message.text)
async def pro_downloader(message: types.Message):
    if message.text.startswith('/'): return
    
    url = message.text.strip()
    wait_msg = await message.reply("⏳ جاري سحب الفيديو ومعالجة الصوت... انتظر قليلاً")
    
    user_folder = f"temp_{message.from_user.id}"
    if not os.path.exists(user_folder): os.makedirs(user_folder)
    file_path = os.path.join(user_folder, "MBAB_Video.mp4")

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': file_path,
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
    }

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([url]))

        if os.path.exists(file_path):
            with open(file_path, 'rb') as video:
                await bot.send_video(message.chat.id, video, caption="✅ تم التحميل بواسطة MBAB")
            await wait_msg.delete()
        else:
            await wait_msg.edit_text("❌ لم نجد فيديو بالصوت لهذا الرابط، تأكد أنه ليس خاصاً.")
            
    except Exception as e:
        await wait_msg.edit_text("❌ فشل التحميل. يرجى التأكد من تحديث yt-dlp على السيرفر.")
    finally:
        shutil.rmtree(user_folder, ignore_errors=True)

# --- [ معالجة الكولباك (الإذاعة والبيانات) ] ---
@dp.callback_query_handler(lambda c: True)
async def callback_handler(call: types.CallbackQuery):
    uid = call.from_user.id
    
    if call.data == "p":
        db.execute("SELECT points FROM users WHERE user_id = ?", (uid,))
        await call.answer(f"رصيدك الحالي: {db.fetchone()[0]} نقطة", show_alert=True)
    
    elif call.data == "stats" and uid == ADMIN_ID:
        db.execute("SELECT COUNT(*) FROM users")
        total = db.fetchone()[0]
        await call.message.answer(f"📊 إحصائيات MBAB:\nعدد الأعضاء: {total}")

    elif call.data == "bc" and uid == ADMIN_ID:
        await call.message.answer("📢 أرسل الآن الرسالة (نص فقط) التي تريد إذاعتها للجميع:")
        # ملاحظة: في النسخة الكاملة يتم استخدام الـ FSM لتخزين الحالة، هنا سنستخدم معالج رسائل بسيط.

    elif call.data == "wd":
        db.execute("SELECT points FROM users WHERE user_id = ?", (uid,))
        p = db.fetchone()[0]
        if p >= 100:
            db.execute("UPDATE users SET points = points - 100 WHERE user_id = ?", (uid,))
            conn.commit()
            await bot.send_message(ADMIN_ID, f"🚨 طلب سحب جديد من المستخدم: `{uid}`")
            await call.answer("✅ تم إرسال طلب السحب للأدمن!", show_alert=True)
        else:
            await call.answer(f"❌ رصيدك {p}.. تحتاج 100 نقطة للسحب.", show_alert=True)

# --- [ تشغيل البوت ] ---
if __name__ == '__main__':
    print("🚀 MBAB Mega System is LIVE!")
    executor.start_polling(dp, skip_updates=True)
