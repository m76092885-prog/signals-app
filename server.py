from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import asyncio, random, time, json

app = FastAPI()

clients = set()

price = 1.1000
candles = []
current_candle = None
candle_start = int(time.time())

# генерация цены
def tick():
    global price
    price += random.uniform(-0.0002, 0.0002)
    return round(price, 5)

# создаём стартовые свечи С ВРЕМЕНЕМ
now = int(time.time()) - 600
for i in range(60):
    p = tick()
    candles.append({
        "time": now + i * 10,
        "open": p,
        "high": p,
        "low": p,
        "close": p
    })

@app.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    clients.add(ws)

    global current_candle, candle_start

    try:
        while True:
            p = tick()
            now = int(time.time())

            if current_candle is None:
                current_candle = {
                    "time": now,
                    "open": p,
                    "high": p,
                    "low": p,
                    "close": p
                }
                candle_start = now

            current_candle["high"] = max(current_candle["high"], p)
            current_candle["low"] = min(current_candle["low"], p)
            current_candle["close"] = p

            if now - candle_start >= 10:
                candles.append(current_candle)
                current_candle = {
                    "time": now,
                    "open": p,
                    "high": p,
                    "low": p,
                    "close": p
                }
                candle_start = now

            data = {
                "price": p,
                "candles": candles[-60:]
            }

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

app.mount("/", StaticFiles(directory=".", html=True), name="static")
