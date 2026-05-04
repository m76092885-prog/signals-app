from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random, time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

signals = []

symbols = ["EUR/USD", "USD/JPY", "GBP/USD", "AUD/USD"]

def generate_signal():
    return {
        "symbol": random.choice(symbols),
        "signal": random.choice(["BUY", "SELL"]),
        "probability": random.randint(70, 95),
        "time": time.time()
    }

@app.get("/")
def home():
    return {"status": "running"}

@app.get("/signals")
def get_signals():
    return signals[-10:]

@app.on_event("startup")
async def start():
    import asyncio
    async def loop():
        while True:
            signals.append(generate_signal())
            if len(signals) > 50:
                signals.pop(0)
            await asyncio.sleep(5)

    asyncio.create_task(loop())
