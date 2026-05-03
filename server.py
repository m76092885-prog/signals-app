from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# =====================
# ХРАНИЛИЩЕ СИГНАЛОВ
# =====================
signals = []

# =====================
# CORS (для Mini App)
# =====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================
# HEALTH CHECK
# =====================
@app.get("/")
def home():
    return {"status": "ok", "signals": len(signals)}

# =====================
# ПОЛУЧИТЬ СИГНАЛЫ
# =====================
@app.get("/signals")
def get_signals():
    return signals

# =====================
# ДОБАВИТЬ СИГНАЛ
# =====================
@app.post("/add_signal")
def add_signal(data: dict):
    signals.append(data)

    # ограничим память (последние 200)
    if len(signals) > 200:
        signals.pop(0)

    return {
        "status": "added",
        "total": len(signals)
    }

# =====================
# 📊 СТАТИСТИКА WINRATE
# =====================
@app.get("/stats")
def stats():

    total = len(signals)

    if total == 0:
        return {
            "winrate": 0,
            "wins": 0,
            "losses": 0,
            "total": 0
        }

    wins = 0
    losses = 0

    # простая логика оценки результата
    for s in signals:

        prob = s.get("probability", 0)

        # WIN если вероятность >= 70
        if prob >= 70:
            wins += 1
        else:
            losses += 1

    winrate = round((wins / total) * 100, 2)

    return {
        "winrate": winrate,
        "wins": wins,
        "losses": losses,
        "total": total
    }
