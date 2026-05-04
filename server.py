from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import random
import time
import asyncio
import os

app = FastAPI()

# --- CORS (чтобы фронт работал) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- данные ---
signals = []

symbols = ["EUR/USD", "USD/JPY", "GBP/USD", "AUD/USD", "EUR/JPY"]

# --- генерация сигнала ---
def generate_signal():
    return {
        "symbol": random.choice(symbols),
        "signal": random.choice(["BUY", "SELL"]),
        "probability": random.randint(70, 95),
        "time": time.time()
    }

# --- ОТДАЁМ HTML (ГЛАВНОЕ) ---
@app.get("/", response_class=HTMLResponse)
def home():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>index.html not found</h1>"

# --- API сигналов ---
@app.get("/signals")
def get_signals():
    return signals[-10:]

# --- генератор сигналов ---
@app.on_event("startup")
async def start():
    async def loop():
        while True:
            signals.append(generate_signal())

            # ограничение
            if len(signals) > 50:
                signals.pop(0)

            await asyncio.sleep(5)

    asyncio.create_task(loop())
