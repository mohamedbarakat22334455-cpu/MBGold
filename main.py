import os, sqlite3, datetime, yt_dlp, shutil
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice

# --- [ إعدادات MBAB ] ---
API_TOKEN = '8579385725:AAGZd2wDPxjFyBq7x6R3AMhMJT46tX6Ld5c'
ADMIN_ID = 123456789  # <--- حط الـ ID بتاعك هنا
CHANNEL_LINK = "https://t.me/MBABmbab"
MY_PRIVATE_LINK = "https://t.me/M_Barakat"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- [ قاعدة البيانات ] ---
conn = sqlite3.connect('mbab_pro.db', check_same_thread=False)
db = conn.cursor()
db.execute('''CREATE TABLE IF NOT EXISTS users 
             (user_id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0, 
              invited_by INTEGER, last_active TEXT)''')
conn.commit()

# --- [ نظام البداية والإحالة ] ---
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
        InlineKeyboardButton("📢 القناة", url=CHANNEL_LINK)
    )
    
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    await message.reply(f"🏆 **أهلاً بك في MBAB**\n\n"
                        f"أرسل رابط الفيديو الآن لتحميله مباشرة!\n\n"
                        f"🎁 100 نقطة = 15 جنيه.\n"
                        f"🔗 رابطك: `{ref_link}`", reply_markup=kb)

# --- [ معالجة الروابط - الحل النهائي ] ---
@dp.message_handler(lambda message: "http" in message.text)
async def handle_links(message: types.Message):
    # تجاهل أوامر التشغيل لو فيها رابط
    if message.text.startswith('/start'): return

    url = message.text.strip()
    # صنعنا كولباك داتا ذكي يخزن الرابط مؤقتاً في رسالة البوت
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🎥 فيديو MP4", callback_data=f"dl_v"),
        InlineKeyboardButton("🎧 صوت MP3", callback_data=f"dl_a")
    )
    await message.reply(f"📥 **تم استلام الرابط بنجاح!**\nاختر الصيغة التي تفضلها لـ MBAB:", reply_markup=kb)

# --- [ محرك التحميل ] ---
@dp.callback_query_handler(lambda c: c.data.startswith('dl_'))
async def process_download(call: types.CallbackQuery):
    media_type = call.data.split('_')[1] # v أو a
    # الرابط موجود في نص الرسالة اللي البوت رد بيها
    url = call.message.reply_to_message.text 
    
    wait_msg = await bot.send_message(call.message.chat.id, "⏳ جاري المعالجة والتحميل... انتظر قليلاً")
    
    folder = f"temp_{call.from_user.id}"
    if not os.path.exists(folder): os.makedirs(folder)
    file_path = os.path.join(folder, f"MBAB_{call.from_user.id}")

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' if media_type == 'v' else 'bestaudio/best',
        'outtmpl': f"{file_path}.%(ext)s",
        'quiet': True,
        'no_warnings': True,
    }
    
    if media_type == 'a':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if media_type == 'a': 
                filename = filename.rsplit('.', 1)[0] + '.mp3'

        with open(filename, 'rb') as f:
            if media_type == 'v':
                await bot.send_video(call.message.chat.id, f, caption="✅ تم بواسطة MBAB")
            else:
                await bot.send_audio(call.message.chat.id, f, caption="🎧 تم بواسطة MBAB")
        
        await bot.delete_message(call.message.chat.id, wait_msg.message_id)
    except Exception as e:
        await bot.edit_message_text(f"❌ حدث خطأ! قد يكون الرابط غير مدعوم أو خاص.", call.message.chat.id, wait_msg.message_id)
    finally:
        shutil.rmtree(folder, ignore_errors=True)

# --- [ باقي الوظائف ] ---
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
            await bot.send_message(ADMIN_ID, f"🚨 طلب سحب من `{uid}`")
            await call.answer("✅ تم إرسال طلبك!", show_alert=True)
        else: await call.answer("❌ رصيدك غير كافٍ (محتاج 100).", show_alert=True)
    elif call.data == 'stars':
        await bot.send_invoice(uid, title="تواصل", description="5 نجوم لمراسلة مطور MBAB",
            payload="p", provider_token="", currency="XTR", prices=[LabeledPrice(label="Stars", amount=5)])

@dp.pre_checkout_query_handler(lambda q: True)
async def pre_c(q: types.PreCheckoutQuery): await bot.answer_pre_checkout_query(q.id, ok=True)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
