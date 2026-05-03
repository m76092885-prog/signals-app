from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
import asyncio
import time

app = FastAPI()

signals = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SYMBOLS = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "EUR/JPY"]

# =====================
# ГЕНЕРАЦИЯ СИГНАЛА
# =====================

def generate_signal():
    symbol = random.choice(SYMBOLS)

    rsi = random.uniform(10, 90)

    signal = "BUY" if rsi < 50 else "SELL"

    strength = random.randint(60, 95)

    return {
        "symbol": symbol,
        "signal": signal,
        "probability": strength,
        "time": time.time()
    }

# =====================
# АВТО-ГЕНЕРАТОР
# =====================

async def auto_generator():
    while True:
        if len(signals) > 50:
            signals.pop(0)

        new_signal = generate_signal()
        signals.append(new_signal)

        print("NEW SIGNAL:", new_signal)

        await asyncio.sleep(60)  # каждые 60 сек

# =====================
# API
# =====================

@app.on_event("startup")
async def startup():
    asyncio.create_task(auto_generator())

@app.get("/")
def home():
    return {"status": "auto server running"}

@app.get("/signals")
def get_signals():
    return signals
