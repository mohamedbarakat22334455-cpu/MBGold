import os, sqlite3, datetime, yt_dlp, shutil
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice

# --- [إعدادات  MBABت - MB GOLD ] ---
API_TOKEN = '8579385725:AAGZd2wDPxjFyBq7x6R3AMhMJT46tX6Ld5c'
ADMIN_ID = 123456789  # <--- حط الـ ID بتاعك هنا
CHANNEL_ID = "@MBABmbab"
CHANNEL_LINK = "https://t.me/MBABmbab"
MY_PRIVATE_LINK = "https://t.me/M_Barakat"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- [ قاعدة البيانات الشاملة ] ---
conn = sqlite3.connect('mb_gold_v7_final.db', check_same_thread=False)
db = conn.cursor()
db.execute('''CREATE TABLE IF NOT EXISTS users 
             (user_id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0, 
              invited_by INTEGER, last_active TEXT, banned INTEGER DEFAULT 0)''')
conn.commit()

# --- [ وظائف التحقق والفلترة ] ---
async def check_access(user_id):
    if user_id == ADMIN_ID: return True
    # فحص الحظر
    db.execute("SELECT banned FROM users WHERE user_id = ?", (user_id,))
    res = db.fetchone()
    if res and res[0] == 1: return "banned"
    # فحص الاشتراك
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

# --- [ أوامر الأدمن المتطورة ] ---
@dp.message_handler(commands=['setpoints']) # /setpoints [user_id] [points]
async def set_points(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        try:
            _, target_id, p_amount = message.text.split()
            db.execute("UPDATE users SET points = ? WHERE user_id = ?", (p_amount, target_id))
            conn.commit()
            await message.reply(f"✅ تم تحديث نقاط `{target_id}` إلى `{p_amount}`")
        except: await message.reply("⚠️ الاستخدام: `/setpoints ID النقاط`")

@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        db.execute("SELECT COUNT(*) FROM users")
        total = db.fetchone()[0]
        await message.reply(f"👑 **لوحة تحكم MB Gold**\n\n👤 الأعضاء: `{total}`\n📢 أرسل (نص/صورة) للنشر العام.")

# --- [ نظام البداية ] ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    access = await check_access(user_id)
    
    if access == "banned":
        return await message.reply("🚫 أنت محظور من استخدام البوت.")
    
    if not access:
        kb = InlineKeyboardMarkup().add(InlineKeyboardButton("✅ اشترك هنا", url=CHANNEL_LINK))
        kb.add(InlineKeyboardButton("🔄 تفعيل", callback_data="check"))
        return await message.reply("⚠️ **عذراً!** يجب الاشتراك في القناة أولاً.", reply_markup=kb)

    # تسجيل المستخدم
    db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if db.fetchone() is None:
        args = message.get_args()
        inviter = int(args) if args and args.isdigit() and int(args) != user_id else None
        db.execute("INSERT INTO users (user_id, invited_by, last_active) VALUES (?, ?, ?)", 
                   (user_id, inviter, str(datetime.datetime.now())))
        if inviter:
            db.execute("UPDATE users SET points = points + 1 WHERE user_id = ?", (inviter,))
            try: await bot.send_message(inviter, "🚀 مبروك! حصلت على +1 نقطة من إحالة.")
            except: pass
        conn.commit()

    kb = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("💰 رصيدي", callback_data="my_p"),
        InlineKeyboardButton("🏆 الأوائل", callback_data="top"),
        InlineKeyboardButton("💳 سحب (15ج)", callback_data="wd"),
        InlineKeyboardButton("⭐️ تواصل خاص (5 نجوم)", callback_data="stars")
    )
    
    bot_info = await bot.get_me()
    ref = f"https://t.me/{bot_info.username}?start={user_id}"
    await message.reply(f"🏆 **MB Gold**\n\n🎁 100 نقطة = 15 جنيه!\n🔗 رابط دعوتك: `{ref}`", reply_markup=kb)

# --- [ التحميل الاحترافي ] ---
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
        with open(f"{path}.{ext}", 'rb') as f:
            await (bot.send_video if type == 'v' else bot.send_audio)(call.message.chat.id, f, caption="✅ MB Gold")
        await wait.delete()
    except: await wait.edit_text("❌ خطأ في التحميل!")
    finally: shutil.rmtree(folder, ignore_errors=True)

# --- [ معالجة الأزرار والدفع ] ---
@dp.callback_query_handler(lambda c: True)
async def handle_all_clicks(call: types.CallbackQuery):
    uid = call.from_user.id
    if call.data == "check":
        if await check_access(uid): await start(call.message)
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
            await bot.send_message(ADMIN_ID, f"🚨 **طلب سحب!**\nالمستخدم: `{uid}`")
            await call.answer("✅ تم إرسال طلبك!", show_alert=True)
        else: await call.answer("❌ محتاج 100 نقطة.", show_alert=True)

    elif call.data == "stars":
        await bot.send_invoice(uid, title="تواصل خاص", description="5 نجوم لمراسلة محمد بركات",
            payload="pay", provider_token="", currency="XTR", prices=[LabeledPrice(label="5 Stars", amount=5)])

# --- [ معالجة الرسائل والإعلانات ] ---
@dp.message_handler(content_types=['text', 'photo'])
async def main_engine(message: types.Message):
    if not await check_access(message.from_user.id): return

    if message.from_user.id == ADMIN_ID and not (message.text and "http" in message.text):
        db.execute("SELECT user_id FROM users")
        for u in db.fetchall():
            try:
                if message.photo: await bot.send_photo(u[0], message.photo[-1].file_id, caption=message.caption)
                else: await bot.send_message(u[0], message.text)
            except: pass
        return await message.reply("✅ تم النشر بنجاح.")

    if message.text and "http" in message.text:
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("🎥 فيديو", callback_data=f"v|{message.text}"),
            InlineKeyboardButton("🎧 صوت MP3", callback_data=f"a|{message.text}")
        )
        await message.reply("اختر الصيغة:", reply_markup=kb)

@dp.pre_checkout_query_handler(lambda q: True)
async def pre_checkout(q: types.PreCheckoutQuery): await bot.answer_pre_checkout_query(q.id, ok=True)

@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def payment_success(m: types.Message):
    await m.reply(f"✅ تم الدفع! تواصل معي:\n{MY_PRIVATE_LINK}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
