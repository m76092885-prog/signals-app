from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
import time
import threading
import time as t

app = FastAPI()

signals = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SYMBOLS = ["EUR/USD","GBP/USD","USD/JPY","AUD/USD","USD/CAD","EUR/JPY"]

# =====================
# SIGNAL GENERATOR
# =====================
def generate_signal():
    return {
        "symbol": random.choice(SYMBOLS),
        "signal": "BUY" if random.random() > 0.5 else "SELL",
        "probability": random.randint(60, 95),
        "time": time.time()
    }

# =====================
# BACKGROUND LOOP (SAFE)
# =====================
def loop():
    while True:
        try:
            signals.append(generate_signal())

            if len(signals) > 100:
                signals.pop(0)

            print("NEW SIGNAL ADDED")

        except Exception as e:
            print("ERROR:", e)

        t.sleep(10)

# =====================
# START THREAD
# =====================
@app.on_event("startup")
def start():
    thread = threading.Thread(target=loop, daemon=True)
    thread.start()

# =====================
# API
# =====================
@app.get("/")
def home():
    return {"status": "running"}

@app.get("/signals")
def get_signals():
    return signals

@app.get("/stats")
def stats():

    if not signals:
        return {"winrate": 0, "wins": 0, "losses": 0, "total": 0}

    wins = sum(1 for s in signals if s["probability"] >= 70)
    losses = len(signals) - wins

    return {
        "winrate": round(wins / len(signals) * 100, 2),
        "wins": wins,
        "losses": losses,
        "total": len(signals)
    }
