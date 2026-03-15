import os, sqlite3, datetime, yt_dlp, shutil
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice

# --- [ إعدادات محمد بركات - MB GOLD ] ---
API_TOKEN = '8579385725:AAGZd2wDPxjFyBq7x6R3AMhMJT46tX6Ld5c'
ADMIN_ID = 123456789  # <--- حط الـ ID بتاعك هنا ضروري جداً
CHANNEL_ID = "@MBABmbab"
CHANNEL_LINK = "https://t.me/MBABmbab"
MY_PRIVATE_LINK = "https://t.me/M_Barakat"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- [ قاعدة البيانات الاحترافية ] ---
conn = sqlite3.connect('mb_gold_master.db', check_same_thread=False)
db = conn.cursor()
db.execute('''CREATE TABLE IF NOT EXISTS users 
             (user_id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0, 
              invited_by INTEGER, last_active TEXT, total_stars INTEGER DEFAULT 0)''')
conn.commit()

# --- [ وظائف النظام ] ---
async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

def update_user(user_id, inviter=None):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if db.fetchone() is None:
        db.execute("INSERT INTO users (user_id, invited_by, last_active) VALUES (?, ?, ?)", (user_id, inviter, now))
    else:
        db.execute("UPDATE users SET last_active = ? WHERE user_id = ?", (now, user_id))
    conn.commit()

# --- [ أوامر الأدمن ] ---
@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        db.execute("SELECT COUNT(*), SUM(points) FROM users")
        stats = db.fetchone()
        await message.reply(f"🟡 **لوحة تحكم MB Gold**\n\n👤 المستخدمين: `{stats[0]}`\n💰 النقاط المتداولة: `{stats[1]}`\n\n📢 أرسل إعلانك الآن.")

# --- [ نظام البداية والاشتراك ] ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    args = message.get_args()
    
    if not await is_subscribed(user_id):
        kb = InlineKeyboardMarkup().add(InlineKeyboardButton("✅ اشترك في القناة", url=CHANNEL_LINK))
        kb.add(InlineKeyboardButton("🔄 تفعيل البوت", callback_data="recheck"))
        return await message.reply("⚠️ **عذراً!** يجب الاشتراك أولاً لاستخدام خدمات MB Gold.", reply_markup=kb)

    # حساب نقاط الإحالة
    db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if db.fetchone() is None:
        inviter = int(args) if args and args.isdigit() and int(args) != user_id else None
        update_user(user_id, inviter)
        if inviter:
            db.execute("UPDATE users SET points = points + 1 WHERE user_id = ?", (inviter,))
            conn.commit()
            try: await bot.send_message(inviter, "🚀 مبروك! حصلت على +1 نقطة من دعوة جديدة.")
            except: pass
    else:
        update_user(user_id)

    kb = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("💰 رصيدي", callback_data="my_p"),
        InlineKeyboardButton("🏆 الترتيب", callback_data="top"),
        InlineKeyboardButton("💳 سحب (15ج)", callback_data="wd"),
        InlineKeyboardButton("⭐️ تواصل خاص (5 نجوم)", callback_data="stars")
    )
    
    bot_info = await bot.get_me()
    ref = f"https://t.me/{bot_info.username}?start={user_id}"
    await message.reply(f"🏆 **أهلاً بك في MB Gold**\n\n🎁 اجمع 100 نقطة واكسب 15 جنيه!\n🔗 رابط دعوتك: `{ref}`", reply_markup=kb)

# --- [ التعامل مع الأزرار والدفع ] ---
@dp.callback_query_handler(lambda c: True)
async def handle_clicks(call: types.CallbackQuery):
    uid = call.from_user.id
    
    if call.data == "recheck":
        if await is_subscribed(uid):
            await call.message.delete()
            await start(call.message)
        else: await call.answer("❌ اشترك أولاً!", show_alert=True)

    elif call.data == "my_p":
        db.execute("SELECT points FROM users WHERE user_id = ?", (uid,))
        await call.answer(f"رصيدك: {db.fetchone()[0]} نقطة", show_alert=True)

    elif call.data == "wd":
        db.execute("SELECT points FROM users WHERE user_id = ?", (uid,))
        p = db.fetchone()[0]
        if p >= 100:
            db.execute("UPDATE users SET points = points - 100 WHERE user_id = ?", (uid,))
            conn.commit()
            await bot.send_message(ADMIN_ID, f"🚨 **طلب سحب!**\nالمستخدم: `{uid}` طلب 15 جنيه.")
            await call.answer("✅ تم إرسال الطلب!", show_alert=True)
        else: await call.answer("❌ تحتاج 100 نقطة.", show_alert=True)

    elif call.data == "stars":
        await bot.send_invoice(uid, title="تواصل خاص", description="دفع 5 نجوم لمراسلة محمد بركات",
            payload="pay", provider_token="", currency="XTR", prices=[LabeledPrice(label="5 Stars", amount=5)])

# --- [ التحميل الاحترافي ] ---
@dp.message_handler(content_types=['text', 'photo'])
async def process_all(message: types.Message):
    if not await is_subscribed(message.from_user.id): return
    
    # الإعلانات
    if message.from_user.id == ADMIN_ID and not (message.text and "http" in message.text):
        db.execute("SELECT user_id FROM users")
        for u in db.fetchall():
            try:
                if message.photo: await bot.send_photo(u[0], message.photo[-1].file_id, caption=message.caption)
                else: await bot.send_message(u[0], message.text)
            except: pass
        return await message.reply("✅ تم النشر.")

    # روابط التحميل
    if message.text and "http" in message.text:
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("🎥 فيديو", callback_data=f"v|{message.text}"),
            InlineKeyboardButton("🎧 صوت MP3", callback_data=f"a|{message.text}")
        )
        await message.reply("اختر ما تريد تحميله:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith(('v|', 'a|')))
async def downloader(call: types.CallbackQuery):
    type, url = call.data.split('|')
    wait = await bot.send_message(call.message.chat.id, "⏳ جاري التحميل...")
    
    folder = f"dl_{call.from_user.id}"
    if not os.path.exists(folder): os.makedirs(folder)
    path = os.path.join(folder, "file")
    
    opts = {'format': 'best' if type == 'v' else 'bestaudio/best', 'outtmpl': path, 'quiet': True}
    if type == 'a': opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
    
    try:
        with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
        ext = "mp4" if type == 'v' else "mp3"
        final_file = f"{path}.{ext}"
        with open(final_file, 'rb') as f:
            if type == 'v': await bot.send_video(call.message.chat.id, f, caption="✅ MB Gold")
            else: await bot.send_audio(call.message.chat.id, f, caption="🎧 MB Gold")
        await wait.delete()
    except: await wait.edit_text("❌ خطأ!")
    finally: shutil.rmtree(folder, ignore_errors=True) # تنظيف فوري للملفات

# --- [ الدفع ] ---
@dp.pre_checkout_query_handler(lambda q: True)
async def checkout(q: types.PreCheckoutQuery): await bot.answer_pre_checkout_query(q.id, ok=True)

@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def success(m: types.Message): await m.reply(f"✅ تم الدفع! راسلني هنا:\n{MY_PRIVATE_LINK}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
