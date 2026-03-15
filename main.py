import os, sqlite3, datetime, yt_dlp, shutil
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice

# --- [ إعدادات MBAB ] ---
API_TOKEN = '8579385725:AAGZd2wDPxjFyBq7x6R3AMhMJT46tX6Ld5c'
ADMIN_ID = 123456789  # <--- حط الـ ID بتاعك هنا
CHANNEL_LINK = "https://t.me/MBABmbab"
MY_PRIVATE_LINK = "https://t.me/M_Barakat" # رابط التواصل الخاص

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- [ قاعدة البيانات ] ---
conn = sqlite3.connect('mbab_system.db', check_same_thread=False)
db = conn.cursor()
db.execute('''CREATE TABLE IF NOT EXISTS users 
             (user_id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0, 
              invited_by INTEGER, last_active TEXT)''')
conn.commit()

# --- [ نظام البداية ] ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    args = message.get_args()
    
    # تسجيل المستخدم وحساب النقاط
    db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if db.fetchone() is None:
        inviter = int(args) if args and args.isdigit() and int(args) != user_id else None
        db.execute("INSERT INTO users (user_id, invited_by, last_active) VALUES (?, ?, ?)", 
                   (user_id, inviter, str(datetime.datetime.now())))
        if inviter:
            db.execute("UPDATE users SET points = points + 1 WHERE user_id = ?", (inviter,))
            try: await bot.send_message(inviter, "🚀 مبروك! حصلت على +1 نقطة من إحالة جديدة.")
            except: pass
        conn.commit()

    kb = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("💰 رصيدي", callback_data="p"),
        InlineKeyboardButton("🏆 المتصدرين", callback_data="top"),
        InlineKeyboardButton("💳 سحب (15ج)", callback_data="wd"),
        InlineKeyboardButton("⭐️ تواصل خاص (5 نجوم)", callback_data="stars"),
        InlineKeyboardButton("📢 قناة البوت (اختياري)", url=CHANNEL_LINK)
    )
    
    bot_me = await bot.get_me()
    ref = f"https://t.me/{bot_me.username}?start={user_id}"
    await message.reply(f"🏆 **أهلاً بك في بوت MBAB**\n\n"
                        f"هنا تقدر تحمل فيديوهات وتجمع نقاط!\n"
                        f"🎁 العرض: 100 نقطة = 15 جنيه.\n\n"
                        f"🔗 **رابط دعوتك:**\n`{ref}`", reply_markup=kb)

# --- [ إدارة النقاط والسحب ] ---
@dp.callback_query_handler(lambda c: c.data in ['p', 'top', 'wd', 'stars'])
async def actions(call: types.CallbackQuery):
    uid = call.from_user.id
    if call.data == 'p':
        db.execute("SELECT points FROM users WHERE user_id = ?", (uid,))
        await call.answer(f"رصيدك: {db.fetchone()[0]} نقطة", show_alert=True)
    
    elif call.data == 'top':
        db.execute("SELECT user_id, points FROM users ORDER BY points DESC LIMIT 5")
        msg = "🏆 **أعلى 5 مجمعين للنقاط في MBAB:**\n" + "\n".join([f"{i+1}. `{u[0]}`: {u[1]}pt" for i, u in enumerate(db.fetchall())])
        await bot.send_message(uid, msg, parse_mode="Markdown")
        
    elif call.data == 'wd':
        db.execute("SELECT points FROM users WHERE user_id = ?", (uid,))
        p = db.fetchone()[0]
        if p >= 100:
            db.execute("UPDATE users SET points = points - 100 WHERE user_id = ?", (uid,))
            conn.commit()
            await bot.send_message(ADMIN_ID, f"🚨 **طلب سحب جديد!**\nالمستخدم: `{uid}`")
            await call.answer("✅ تم إرسال الطلب! سيتم التواصل معك.", show_alert=True)
        else:
            await call.answer(f"❌ رصيدك {p}. محتاج 100 نقطة.", show_alert=True)
            
    elif call.data == 'stars':
        await bot.send_invoice(uid, title="تواصل خاص", description="دفع 5 نجوم لمراسلة مطور MBAB",
            payload="pay", provider_token="", currency="XTR", prices=[LabeledPrice(label="5 Stars", amount=5)])

# --- [ نظام التحميل والإعلانات ] ---
@dp.message_handler(content_types=['text', 'photo'])
async def handler(message: types.Message):
    # لوحة تحكم الأدمن لإرسال إعلانات
    if message.from_user.id == ADMIN_ID and not (message.text and "http" in message.text):
        db.execute("SELECT user_id FROM users")
        for u in db.fetchall():
            try:
                if message.photo: await bot.send_photo(u[0], message.photo[-1].file_id, caption=message.caption)
                else: await bot.send_message(u[0], message.text)
            except: pass
        return await message.reply("✅ تم نشر الإعلان.")

    # تحميل الفيديوهات
    if message.text and "http" in message.text:
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("🎥 فيديو", callback_data=f"v|{message.text}"),
            InlineKeyboardButton("🎧 صوت MP3", callback_data=f"a|{message.text}")
        )
        await message.reply("اختر الصيغة المطلوبة لـ MBAB:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith(('v|', 'a|')))
async def dl(call: types.CallbackQuery):
    t, url = call.data.split('|')
    wait = await bot.send_message(call.message.chat.id, "⏳ جاري التحميل بواسطة MBAB...")
    folder = f"dl_{call.from_user.id}"
    if not os.path.exists(folder): os.makedirs(folder)
    path = os.path.join(folder, "file")
    
    opts = {'format': 'best' if t == 'v' else 'bestaudio/best', 'outtmpl': path, 'quiet': True}
    if t == 'a': opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
    
    try:
        with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
        ext = "mp4" if t == 'v' else "mp3"
        await (bot.send_video if t == 'v' else bot.send_audio)(call.message.chat.id, open(f"{path}.{ext}", 'rb'), caption="✅ تم بواسطة MBAB")
        await wait.delete()
    except: await wait.edit_text("❌ خطأ في الرابط!")
    finally: shutil.rmtree(folder, ignore_errors=True)

# --- [ الدفع بالنجوم ] ---
@dp.pre_checkout_query_handler(lambda q: True)
async def pre_c(q: types.PreCheckoutQuery): await bot.answer_pre_checkout_query(q.id, ok=True)

@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def success(m: types.Message): await m.reply(f"✅ تم الدفع! يمكنك المراسلة هنا:\n{MY_PRIVATE_LINK}")

if __name__ == '__main__':
    print("🚀 MBAB Bot is LIVE (No Forced Join)!")
    executor.start_polling(dp, skip_updates=True)
