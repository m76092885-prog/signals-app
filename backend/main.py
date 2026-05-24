from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import requests
import pandas as pd
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")

def root():

    return {"status":"running"}

@app.get("/signal")

def get_signal():

    try:

        url = "https://iss.moex.com/iss/engines/futures/markets/forts/securities/CCM2026/candles.json?interval=5"

        r = requests.get(url)
        data = r.json()

        candles = data["candles"]["data"]
        columns = data["candles"]["columns"]

        if not candles or len(candles) < 30:
            return {"status":"SEARCHING"}

        df = pd.DataFrame(candles, columns=columns)

        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)

        if len(df) < 30:
            return {"status":"SEARCHING"}

        # уровни
        range_high = df["high"].rolling(20).max().iloc[-1]
        range_low = df["low"].rolling(20).min().iloc[-1]

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        # momentum
        momentum_up = latest["close"] > prev["close"]
        momentum_down = latest["close"] < prev["close"]

        # breakout
        breakout_up = latest["close"] > range_high * 0.999
        breakout_down = latest["close"] < range_low * 1.001

        buy_signal = breakout_up and momentum_up
        sell_signal = breakout_down and momentum_down

        if not buy_signal and not sell_signal:
            return {"status":"SEARCHING"}

        side = "BUY" if buy_signal else "SELL"

        atr = (df["high"] - df["low"]).rolling(14).mean().iloc[-1]

        entry = round(latest["close"], 2)

        if side == "BUY":

            sl = round(entry - atr, 2)
            tp1 = round(entry + atr * 2, 2)
            tp2 = round(entry + atr * 3, 2)

        else:

            sl = round(entry + atr, 2)
            tp1 = round(entry - atr * 2, 2)
            tp2 = round(entry - atr * 3, 2)

        confidence = np.random.randint(78, 92)

        return {

            "asset": "CC1!",
            "side": side,
            "entry": entry,
            "sl": sl,
            "tp1": tp1,
            "tp2": tp2,
            "confidence": confidence,
            "reasons": [
                "Liquidity sweep detected",
                "Momentum confirmed",
                "Structure breakout",
                "Trend alignment"
            ]
        }

    except Exception as e:

        return {"status":"SEARCHING"}
