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
conn = sqlite3.connect('mbab_system.db', check_same_thread=False)
db = conn.cursor()
db.execute('''CREATE TABLE IF NOT EXISTS users 
             (user_id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0, 
              invited_by INTEGER, last_active TEXT)''')
conn.commit()

# --- [ نظام البداية والإحالة ] ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    args = message.get_args() # الكلمات اللي بعد كلمة start
    
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
        InlineKeyboardButton("🏆 المتصدرين", callback_data="top"),
        InlineKeyboardButton("💳 سحب (15ج)", callback_data="wd"),
        InlineKeyboardButton("⭐️ تواصل خاص (5 نجوم)", callback_data="stars"),
        InlineKeyboardButton("📢 قناة البوت", url=CHANNEL_LINK)
    )
    
    await message.reply(f"🏆 **أهلاً بك في بوت MBAB**\n\n"
                        f"ابعت أي رابط فيديو (تيك توك، إنستجرام، يوتيوب) وهنزلهولك فوراً.\n\n"
                        f"🎁 العرض: 100 نقطة = 15 جنيه.\n"
                        f"🔗 رابط دعوتك كبطل:\n`https://t.me/{(await bot.get_me()).username}?start={user_id}`", 
                        reply_markup=kb, parse_mode="Markdown")

# --- [ محرك التحميل الذكي ] ---
@dp.message_handler(lambda message: message.text and "http" in message.text)
async def link_catcher(message: types.Message):
    # تجاهل أي رابط لو كان جوه أمر start
    if message.text.startswith('/start'): return

    url = message.text
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🎥 فيديو MP4", callback_data=f"v|{url}"),
        InlineKeyboardButton("🎧 صوت MP3", callback_data=f"a|{url}")
    )
    await message.reply("⚡️ تم استلام الرابط! اختر الصيغة المطلوبة لـ MBAB:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith(('v|', 'a|')))
async def download_logic(call: types.CallbackQuery):
    data_split = call.data.split('|')
    media_type = data_split[0]
    # التأكد من دمج الرابط بالكامل لو فيه علامات |
    url = "|".join(data_split[1:])
    
    wait_msg = await bot.send_message(call.message.chat.id, "⏳ جاري التحميل... ثواني يا بطل")
    
    folder = f"dl_{call.from_user.id}"
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

        with open(filename, 'rb') as media_file:
            if media_type == 'v':
                await bot.send_video(call.message.chat.id, media_file, caption="✅ تم بواسطة MBAB")
            else:
                await bot.send_audio(call.message.chat.id, media_file, caption="🎧 تم بواسطة MBAB")
        
        await bot.delete_message(call.message.chat.id, wait_msg.message_id)
    except Exception as e:
        await bot.edit_message_text(f"❌ عذراً، الرابط غير مدعوم حالياً أو حدث خطأ فني.", call.message.chat.id, wait_msg.message_id)
        print(f"Error: {e}")
    finally:
        shutil.rmtree(folder, ignore_errors=True)

# --- [ الأنظمة الإضافية ] ---
@dp.callback_query_handler(lambda c: c.data in ['p', 'top', 'wd', 'stars'])
async def handle_actions(call: types.CallbackQuery):
    uid = call.from_user.id
    if call.data == 'p':
        db.execute("SELECT points FROM users WHERE user_id = ?", (uid,))
        await call.answer(f"رصيدك الحالي: {db.fetchone()[0]} نقطة", show_alert=True)
    elif call.data == 'wd':
        db.execute("SELECT points FROM users WHERE user_id = ?", (uid,))
        p = db.fetchone()[0]
        if p >= 100:
            db.execute("UPDATE users SET points = points - 100 WHERE user_id = ?", (uid,))
            conn.commit()
            await bot.send_message(ADMIN_ID, f"🚨 طلب سحب رصيد من المستخدم: `{uid}`")
            await call.answer("✅ تم إرسال طلبك للأدمن!", show_alert=True)
        else:
            await call.answer(f"❌ رصيدك {p}.. محتاج 100 نقطة للسحب.", show_alert=True)
    elif call.data == 'stars':
        await bot.send_invoice(uid, title="تواصل خاص", description="دفع 5 نجوم لمراسلة مطور MBAB",
            payload="pay", provider_token="", currency="XTR", prices=[LabeledPrice(label="5 Stars", amount=5)])

@dp.pre_checkout_query_handler(lambda q: True)
async def pre_c(q: types.PreCheckoutQuery): await bot.answer_pre_checkout_query(q.id, ok=True)

if __name__ == '__main__':
    print("🚀 MBAB Bot is Online and Ready!")
    executor.start_polling(dp, skip_updates=True)
