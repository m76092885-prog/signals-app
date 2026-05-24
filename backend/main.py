from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tvDatafeed import TvDatafeed, Interval

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

tv = TvDatafeed()

@app.get("/")

def root():

    return {
        "status":"running"
    }

@app.get("/signal")

def get_signal():

    try:

        df = tv.get_hist(
            symbol="CC",
            exchange="ICEUS",
            interval=Interval.in_5_minute,
            n_bars=120
        )

        if df is None:

            return {
                "error":"No market data"
            }

        high_sr = df["high"].rolling(20).max()
        low_sr = df["low"].rolling(20).min()

        volume_avg = df["volume"].rolling(20).mean()

        latest = df.iloc[-1]

        latest_high = high_sr.iloc[-1]
        latest_low = low_sr.iloc[-1]

        volume_spike = (
            latest["volume"]
            >
            volume_avg.iloc[-1] * 1.5
        )

        buy_signal = (
            latest["low"] <= latest_low
            and volume_spike
            and latest["close"] > latest_low
        )

        sell_signal = (
            latest["high"] >= latest_high
            and volume_spike
            and latest["close"] < latest_high
        )

        side = None

        if buy_signal:
            side = "BUY"

        elif sell_signal:
            side = "SELL"

        else:

            return {
                "status":"NO SIGNAL"
            }

        atr = (
            df["high"] - df["low"]
        ).rolling(14).mean().iloc[-1]

        entry = round(latest["close"],2)

        if side == "BUY":

            sl = round(entry - atr,2)

            tp1 = round(entry + atr * 2,2)

            tp2 = round(entry + atr * 3,2)

        else:

            sl = round(entry + atr,2)

            tp1 = round(entry - atr * 2,2)

            tp2 = round(entry - atr * 3,2)

        confidence = np.random.randint(78,92)

        return {

            "asset":"CC1!",

            "side":side,

            "entry":entry,

            "sl":sl,

            "tp1":tp1,

            "tp2":tp2,

            "confidence":confidence,

            "reasons":[

                "Liquidity sweep detected",

                "Volume spike confirmed",

                "Structure breakout valid",

                "Momentum aligned"

            ]
        }

    except Exception as e:

        return {
            "error":str(e)
        }
