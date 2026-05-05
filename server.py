from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import asyncio
import random
import time
import json

app = FastAPI()

# 📁 Отдаём index.html
app.mount("/", StaticFiles(directory=".", html=True), name="static")

# 📡 клиенты WebSocket
clients = set()

# 💹 рынок
price = 1.1000
current_candle = None
candle_start = time.time()
candles = []

# 🎲 генерация цены
def tick():
    global price
    price += random.uniform(-0.0002, 0.0002)
    return round(price, 5)

# 🕯 новая свеча
def new_candle(p):
    return {
        "open": p,
        "high": p,
        "low": p,
        "close": p
    }

# 📡 WebSocket
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)

    global current_candle, candle_start

    try:
        while True:
            p = tick()
            now = time.time()

            # создаём свечу
            if current_candle is None:
                current_candle = new_candle(p)
                candle_start = now

            current_candle["high"] = max(current_candle["high"], p)
            current_candle["low"] = min(current_candle["low"], p)
            current_candle["close"] = p

            # каждые 10 секунд новая свеча
            if now - candle_start >= 10:
                candles.append(current_candle)
                current_candle = new_candle(p)
                candle_start = now

            data = {
                "price": p,
                "candles": candles[-60:]
            }

            # отправка всем
            dead = []
            for c in clients:
                try:
                    await c.send_text(json.dumps(data))
                except:
                    dead.append(c)

            for d in dead:
                clients.remove(d)

            await asyncio.sleep(1)

    except:
        clients.remove(ws)
