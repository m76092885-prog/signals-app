from aiogram import Bot, Dispatcher
from aiogram.types import Message, WebAppInfo
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio

TOKEN = "ТВОЙ_ТОКЕН"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text="🚀 Открыть сигналы",
                web_app=WebAppInfo(url="https://signals-app-yk11.onrender.com")
            )]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "Нажми кнопку ниже 👇",
        reply_markup=kb
    )

async def main():
    print("Bot started...")
    await dp.start_polling(bot)

asyncio.run(main())
