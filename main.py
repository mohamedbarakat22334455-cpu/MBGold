import os, sqlite3, datetime, yt_dlp, shutil, asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice

# --- [ إعدادات MBAB النهائية ] ---
API_TOKEN = '8579385725:AAGZd2wDPxjFyBq7x6R3AMhMJT46tX6Ld5c'
ADMIN_ID = 123456789  # <--- حط الـ ID بتاعك هنا
CHANNEL_LINK = "https://t.me/MBABmbab"
MY_PRIVATE_LINK = "https://t.me/M_Barakat"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- [ قاعدة البيانات ] ---
conn = sqlite3.connect('mbab_ultra.db', check_same_thread=False)
db = conn.cursor()
db.execute('''CREATE TABLE IF NOT EXISTS users 
             (user_id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0, 
              invited_by INTEGER, last_active TEXT)''')
conn.commit()

# --- [ نظام البداية ] ---
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    args = message.get_args()
    
    db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if db.fetchone() is None:
        inviter = int(args) if args and args.isdigit() and int(args) != user_id else None
        db.execute("INSERT INTO users (user_id, invited_by, last_active) VALUES (?, ?, ?)", 
                   (user_id, inviter, str(datetime.datetime.now())))
        if inviter:
            try:
                db.execute("UPDATE users SET points = points + 1 WHERE user_id = ?", (inviter,))
                conn.commit()
                await bot.send_message(inviter, "🚀 مبروك! حصلت على +1 نقطة من إحالة جديدة.")
            except: pass
        conn.commit()

    kb = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("💰 رصيدي", callback_data="p"),
        InlineKeyboardButton("💳 سحب (15ج)", callback_data="wd"),
        InlineKeyboardButton("⭐️ تواصل (5 نجوم)", callback_data="stars"),
        InlineKeyboardButton("📢 قناة MBAB", url=CHANNEL_LINK)
    )
    
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    await message.reply(f"🏆 **مرحباً بك في MBAB**\n\n"
                        f"أرسل رابط الفيديو الآن (تيك توك، يوتيوب، إنستا) وسأرسله لك فوراً بالصوت والصورة!\n\n"
                        f"🎁 100 نقطة = 15 جنيه.\n"
                        f"🔗 رابطك: `{ref_link}`", reply_markup=kb)

# --- [ محرك التحميل المباشر (فيديو + صوت) ] ---
@dp.message_handler(lambda message: "http" in message.text and not message.text.startswith('/'))
async def auto_downloader(message: types.Message):
    url = message.text.strip()
    wait_msg = await message.reply("⏳ جاري معالجة الرابط وتحميل الفيديو بالصوت... انتظر قليلاً")
    
    # تحديد مسار فريد لكل مستخدم لمنع تداخل الملفات
    user_folder = f"dl_{message.from_user.id}"
    if not os.path.exists(user_folder): 
        os.makedirs(user_folder)
    
    file_path = os.path.join(user_folder, "video.mp4")

    # إعدادات تحميل الفيديو بجودة عالية مع دمج الصوت تلقائياً
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': file_path,
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
    }

    try:
        # تشغيل التحميل في "خلفية" البرنامج عشان البوت ميهنجش
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([url]))

        if os.path.exists(file_path):
            with open(file_path, 'rb') as video:
                await bot.send_video(message.chat.id, video, caption="✅ تم التحميل بنجاح بواسطة MBAB")
            await wait_msg.delete()
        else:
            await wait_msg.edit_text("❌ لم أتمكن من تحميل الفيديو، تأكد أن الرابط عام وليس خاص.")
            
    except Exception as e:
        await wait_msg.edit_text("❌ حدث خطأ أثناء التحميل. حاول مع رابط آخر.")
        print(f"Error: {e}")
    finally:
        # تنظيف فوري للمجلد بعد الإرسال
        shutil.rmtree(user_folder, ignore_errors=True)

# --- [ الأزرار والعمليات الأخرى ] ---
@dp.callback_query_handler(lambda c: c.data in ['p', 'wd', 'stars'])
async def user_btns(call: types.CallbackQuery):
    uid = call.from_user.id
    if call.data == 'p':
        db.execute("SELECT points FROM users WHERE user_id = ?", (uid,))
        await call.answer(f"رصيدك: {db.fetchone()[0]} نقطة", show_alert=True)
    elif call.data == 'wd':
        db.execute("SELECT points FROM users WHERE user_id = ?", (uid,))
        p = db.fetchone()[0]
        if p >= 100:
            db.execute("UPDATE users SET points = points - 100 WHERE user_id = ?", (uid,))
            conn.commit()
            await bot.send_message(ADMIN_ID, f"🚨 طلب سحب جديد من: `{uid}`")
            await call.answer("✅ تم إرسال طلبك! سيصلك الرصيد قريباً.", show_alert=True)
        else: 
            await call.answer(f"❌ رصيدك {p}.. تحتاج لـ 100 نقطة للسحب.", show_alert=True)
    elif call.data == 'stars':
        await bot.send_invoice(uid, title="تواصل خاص", description="دفع 5 نجوم لمراسلة MBAB",
            payload="contact", provider_token="", currency="XTR", prices=[LabeledPrice(label="5 Stars", amount=5)])

# --- [ إعدادات الأدمن للإعلانات ] ---
@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        db.execute("SELECT COUNT(*) FROM users")
        total = db.fetchone()[0]
        await message.reply(f"👑 **لوحة تحكم MBAB**\n\n👤 الأعضاء: `{total}`\n📢 أرسل (نص/صورة) للنشر العام.")

@dp.pre_checkout_query_handler(lambda q: True)
async def pre_c(q: types.PreCheckoutQuery): 
    await bot.answer_pre_checkout_query(q.id, ok=True)

@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def success_pay(m: types.Message):
    await m.reply(f"✅ تم الدفع بنجاح! راسلني هنا:\n{MY_PRIVATE_LINK}")

if __name__ == '__main__':
    print("🚀 MBAB System is Running perfectly!")
    executor.start_polling(dp, skip_updates=True)
