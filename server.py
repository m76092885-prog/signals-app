from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import time
import random

app = FastAPI()

# =========================
# ХРАНЕНИЕ СИГНАЛОВ
# =========================
signals = []

# =========================
# ГЕНЕРАЦИЯ СИГНАЛОВ
# =========================
symbols = ["EUR/USD", "USD/JPY", "GBP/USD", "AUD/USD", "USD/CAD"]

def generate_signal():
    return {
        "symbol": random.choice(symbols),
        "signal": random.choice(["BUY", "SELL"]),
        "probability": random.randint(60, 95),
        "time": time.time()
    }

# =========================
# АВТО-СИГНАЛЫ
# =========================
import threading

def auto_signals():
    while True:
        signals.append(generate_signal())

        # ограничение списка
        if len(signals) > 50:
            signals.pop(0)

        time.sleep(10)

threading.Thread(target=auto_signals, daemon=True).start()

# =========================
# ГЛАВНАЯ СТРАНИЦА (MINI APP)
# =========================
@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# =========================
# API СИГНАЛОВ
# =========================
@app.get("/signals")
def get_signals():
    return signals

# =========================
# ПРОВЕРКА СЕРВЕРА
# =========================
@app.get("/status")
def status():
    return {"status": "running"}
