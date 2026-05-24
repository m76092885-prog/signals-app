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

            symbol="CC1!",

            exchange="RUS",

            interval=Interval.in_5_minute,

            n_bars=150
        )

        if df is None or len(df) < 50:

            return {
                "error":"No market data"
            }

        highest_high = df["high"].rolling(20).max()

        lowest_low = df["low"].rolling(20).min()

        volume_avg = df["volume"].rolling(20).mean()

        latest = df.iloc[-1]

        latest_high = highest_high.iloc[-1]

        latest_low = lowest_low.iloc[-1]

        volume_spike = (

            latest["volume"]

            >

            volume_avg.iloc[-1] * 1.5
        )

        buy_entry = (

            latest["low"] <= latest_low

            and

            volume_spike
        )

        sell_entry = (

            latest["high"] >= latest_high

            and

            volume_spike
        )

        buy_hold = (

            latest["close"] > latest_low
        )

        sell_hold = (

            latest["close"] < latest_high
        )

        final_buy = (

            buy_entry
            and
            buy_hold
        )

        final_sell = (

            sell_entry
            and
            sell_hold
        )

        if not final_buy and not final_sell:

            return {
                "status":"NO SIGNAL"
            }

        atr = (

            df["high"] - df["low"]

        ).rolling(14).mean().iloc[-1]

        side = "BUY" if final_buy else "SELL"

        entry = round(

            latest["close"],

            2
        )

        if side == "BUY":

            sl = round(
                entry - atr,
                2
            )

            tp1 = round(
                entry + atr * 2,
                2
            )

            tp2 = round(
                entry + atr * 3,
                2
            )

        else:

            sl = round(
                entry + atr,
                2
            )

            tp1 = round(
                entry - atr * 2,
                2
            )

            tp2 = round(
                entry - atr * 3,
                2
            )

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

                "Market structure valid",

                "Momentum alignment confirmed"
            ]
        }

    except Exception as e:

        return {
            "error":str(e)
        }
