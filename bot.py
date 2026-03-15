from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# حط التوكن بتاعك هنا بدقة
TOKEN = '8533015825:AAGy7A-Abn3qqW8lwa7b93-Ii92wNTRP_cU'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def test(message: types.Message):
    await message.answer("أيوة يا محمد أنا سامعك وشغال! ✅")

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(f"أنت بعت: {message.text}")

if __name__ == '__main__':
    print("البوت بدأ يتصل بتليجرام... جرب تبعت /start")
    executor.start_polling(dp, skip_updates=True)
