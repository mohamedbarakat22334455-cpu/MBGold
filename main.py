import os, sqlite3, asyncio, yt_dlp, shutil, datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice

# --- [ إعدادات MBAB الرئيسية ] ---
API_TOKEN = '8579385725:AAGZd2wDPxjFyBq7x6R3AMhMJT46tX6Ld5c'
ADMIN_ID = 123456789  # <--- حط الـ ID بتاعك هنا
CHANNEL_LINK = "https://t.me/MBABmbab"
MY_PRIVATE_LINK = "https://t.me/M_Barakat"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- [ قاعدة البيانات ] ---
conn = sqlite3.connect('mbab_final_pro.db', check_same_thread=False)
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
        InlineKeyboardButton("💳 سحب (15ج)", callback_data="wd"),
        InlineKeyboardButton("⭐️ مراسلة (3 نجوم)", callback_data="stars"),
        InlineKeyboardButton("📢 قناة MBAB", url=CHANNEL_LINK)
    )
    
    bot_info = await bot.get_me()
    ref = f"https://t.me/{bot_info.username}?start={user_id}"
    await message.reply(f"🏆 **أهلاً بك في MBAB**\n\nابعت أي رابط فيديو وهنزلهولك فوراً.\n\n🎁 100 نقطة = 15 جنيه.\n🔗 رابط دعوتك: `{ref}`", reply_markup=kb)

# --- [ محرك التحميل الشغال ] ---
async def download_video(url, path):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': path,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: ydl.download([url]))

@dp.message_handler(lambda m: "http" in m.text and not m.text.startswith('/'))
async def handle_dl(message: types.Message):
    url = message.text.strip()
    wait = await message.answer("⏳ **جاري التحميل بواسطة MBAB...**")
    file_path = f"vid_{message.from_user.id}.mp4"

    try:
        await download_video(url, file_path)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as video:
                await bot.send_video(message.chat.id, video, caption="✅ تم بواسطة MBAB")
            await wait.delete()
            os.remove(file_path)
        else:
            await wait.edit_text("❌ فشل التحميل، الرابط غير مدعوم.")
    except:
        await wait.edit_text("❌ حدث خطأ فني.")

# --- [ نظام الخدمات (رصيد، سحب، نجوم) ] ---
@dp.callback_query_handler(lambda c: c.data in ['p', 'wd', 'stars'])
async def tools(call: types.CallbackQuery):
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
            await bot.send_message(ADMIN_ID, f"🚨 طلب سحب من: `{uid}`")
            await call.answer("✅ تم طلب السحب!", show_alert=True)
        else:
            await call.answer("❌ محتاج 100 نقطة للسحب.", show_alert=True)

    elif call.data == 'stars':
        await bot.send_invoice(uid, title="مراسلة خاصة", description="دفع 3 نجوم لمراسلة مطور MBAB",
            payload="contact", provider_token="", currency="XTR", prices=[LabeledPrice(label="3 Stars", amount=3)])

# --- [ نظام الدفع والأدمن ] ---
@dp.pre_checkout_query_handler(lambda q: True)
async def pre_c(q: types.PreCheckoutQuery): await bot.answer_pre_checkout_query(q.id, ok=True)

@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def pay_ok(m: types.Message):
    await m.reply(f"✅ تم الدفع! تواصل معي هنا:\n{MY_PRIVATE_LINK}")

@dp.message_handler(commands=['admin'])
async def admin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        db.execute("SELECT COUNT(*) FROM users")
        await message.reply(f"👑 **لوحة تحكم MBAB**\nالأعضاء: {db.fetchone()[0]}")

if __name__ == '__main__':
    print("MBAB FULL SYSTEM ONLINE!")
    executor.start_polling(dp, skip_updates=True)
