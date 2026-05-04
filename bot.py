import asyncio
import requests
from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import os

TOKEN = os.getenv("8355508722:AAEgH0tfnjxh7G1ke_gGsmt7TdwvZNkw8uk")
CHAT_ID = os.getenv("8706285601")

API_URL = "https://signals-app-yk11.onrender.com/signals"
WEB_APP_URL = "https://signals-app-yk11.onrender.com"

bot = Bot(token=TOKEN)
dp = Dispatcher()

sent_signals = set()

def get_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📊 Открыть панель",
                web_app=WebAppInfo(url=WEB_APP_URL)
            )
        ]
    ])

async def send_signal(signal):
    text = f"""
🚨 СИГНАЛ

{signal['symbol']} {signal['signal']}
📊 {signal['probability']}%
"""

    await bot.send_message(
        chat_id=CHAT_ID,
        text=text,
        reply_markup=get_keyboard()
    )

async def check_signals():
    while True:
        try:
            res = requests.get(API_URL, timeout=10)
            data = res.json()

            for s in data:
                key = f"{s['symbol']}_{s['time']}"

                if key not in sent_signals:
                    sent_signals.add(key)
                    await send_signal(s)

        except Exception as e:
            print("Ошибка:", e)

        await asyncio.sleep(5)

async def main():
    print("BOT STARTED")

    await asyncio.gather(
        dp.start_polling(bot),
        check_signals()
    )

if __name__ == "__main__":
    asyncio.run(main())
