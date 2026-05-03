from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
import asyncio
import time

app = FastAPI()

# =====================
# STORAGE
# =====================
signals = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SYMBOLS = [
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "AUD/USD",
    "USD/CAD",
    "EUR/JPY"
]

# =====================
# GENERATE SIGNAL
# =====================
def generate_signal():
    symbol = random.choice(SYMBOLS)

    probability = random.randint(60, 95)

    signal = "BUY" if random.random() > 0.5 else "SELL"

    return {
        "symbol": symbol,
        "signal": signal,
        "probability": probability,
        "time": time.time()
    }

# =====================
# AUTO LOOP
# =====================
async def auto_signals():
    while True:

        new_signal = generate_signal()

        signals.append(new_signal)

        # ограничим память
        if len(signals) > 100:
            signals.pop(0)

        print("NEW SIGNAL:", new_signal)

        await asyncio.sleep(10)  # каждые 10 секунд

# =====================
# STARTUP
# =====================
@app.on_event("startup")
async def startup():
    asyncio.create_task(auto_signals())

# =====================
# API
# =====================
@app.get("/")
def home():
    return {"status": "live", "signals": len(signals)}

@app.get("/signals")
def get_signals():
    return signals

@app.get("/stats")
def stats():

    if not signals:
        return {
            "winrate": 0,
            "wins": 0,
            "losses": 0,
            "total": 0
        }

    wins = 0
    losses = 0

    for s in signals:
        if s["probability"] >= 70:
            wins += 1
        else:
            losses += 1

    total = wins + losses
    winrate = round((wins / total) * 100, 2)

    return {
        "winrate": winrate,
        "wins": wins,
        "losses": losses,
        "total": total
    }
