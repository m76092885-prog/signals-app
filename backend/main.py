from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import requests
import pandas as pd
import ta
import random
import json
import asyncio

from datetime import datetime

# ==========================================
# API KEY
# ==========================================

API_KEY = "44e14a6e8f7c4360885483d51e2f4523"

# ==========================================
# APP
# ==========================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# FOREX PAIRS
# ==========================================

pairs = [
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "GBP/JPY",
    "AUD/USD",
    "USD/CAD",
    "EUR/JPY",
]

# ==========================================
# SAVE SIGNAL HISTORY
# ==========================================

def save_signal(signal_data):

    try:

        with open("history.json", "r") as f:
            history = json.load(f)

    except:
        history = []

    history.append(signal_data)

    with open("history.json", "w") as f:
        json.dump(history, f, indent=2)

# ==========================================
# SAVE RESULT
# ==========================================

def save_result(result_data):

    try:

        with open("results.json", "r") as f:
            results = json.load(f)

    except:
        results = []

    results.append(result_data)

    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)

# ==========================================
# GET MARKET DATA
# ==========================================

def get_data(pair):

    url = (
        f"https://api.twelvedata.com/time_series?"
        f"symbol={pair}"
        f"&interval=1min"
        f"&outputsize=120"
        f"&apikey={API_KEY}"
    )

    response = requests.get(url).json()

    values = response.get("values")

    if not values:
        return None

    df = pd.DataFrame(values)

    df = df.iloc[::-1]

    df["open"] = df["open"].astype(float)
    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)

    return df

# ==========================================
# AUTO RESULT CHECKER
# ==========================================

async def check_signal_result(signal_data, entry_price):

    expiration = signal_data["expiration"]

    minutes = int(
        expiration.replace("m", "")
    )

    await asyncio.sleep(minutes * 60)

    pair = signal_data["pair"]

    formatted_pair = (
        pair[:3] + "/" + pair[3:]
    )

    df = get_data(formatted_pair)

    if df is None:
        return

    current_price = df["close"].iloc[-1]

    signal = signal_data["signal"]

    result = "LOSS"

    if signal == "BUY":

        if current_price > entry_price:
            result = "WIN"

    else:

        if current_price < entry_price:
            result = "WIN"

    result_data = {

        "pair": pair,

        "signal": signal,

        "score": signal_data["score"],

        "expiration": expiration,

        "entry_price": entry_price,

        "close_price": current_price,

        "result": result,

        "time": str(datetime.now())
    }

    save_result(result_data)

# ==========================================
# ANALYZE PAIR
# ==========================================

def analyze_pair(pair):

    df = get_data(pair)

    if df is None:
        return None

    # ==========================================
    # INDICATORS
    # ==========================================

    ema50 = ta.trend.EMAIndicator(
        close=df["close"],
        window=50
    ).ema_indicator()

    rsi = ta.momentum.RSIIndicator(
        close=df["close"],
        window=14
    ).rsi()

    stoch = ta.momentum.StochasticOscillator(
        high=df["high"],
        low=df["low"],
        close=df["close"]
    )

    stoch_k = stoch.stoch()

    adx = ta.trend.ADXIndicator(
        high=df["high"],
        low=df["low"],
        close=df["close"]
    )

    adx_value = adx.adx()

    plus_di = adx.adx_pos()

    minus_di = adx.adx_neg()

    # ==========================================
    # LAST VALUES
    # ==========================================

    price = df["close"].iloc[-1]

    ema = ema50.iloc[-1]

    rsi_last = rsi.iloc[-1]

    stoch_last = stoch_k.iloc[-1]

    adx_last = adx_value.iloc[-1]

    plus = plus_di.iloc[-1]

    minus = minus_di.iloc[-1]

    # ==========================================
    # CANDLE CONFIRMATION
    # ==========================================

    candle1 = df.iloc[-1]
    candle2 = df.iloc[-2]

    bullish = (
        candle1["close"] > candle1["open"]
        and candle2["close"] > candle2["open"]
    )

    bearish = (
        candle1["close"] < candle1["open"]
        and candle2["close"] < candle2["open"]
    )

    # ==========================================
    # REAL LIQUIDITY ENGINE
    # ==========================================

    last_5 = df.tail(5)

    green = 0
    red = 0

    for _, row in last_5.iterrows():

        if row["close"] > row["open"]:
            green += 1
        else:
            red += 1

    if green > red:

        buyers = 50 + (green * 8)

        buyers += int(adx_last / 2)

        if plus > minus:
            buyers += 10

    else:

        buyers = 50 - (red * 8)

        buyers -= int(adx_last / 2)

        if minus > plus:
            buyers -= 10

    buyers = max(5, min(95, buyers))

    sellers = 100 - buyers

    # ==========================================
    # SCORE SYSTEM
    # ==========================================

    buy_score = 0
    sell_score = 0

    if price > ema:
        buy_score += 25
    else:
        sell_score += 25

    if adx_last > 25:

        if plus > minus:
            buy_score += 20
        else:
            sell_score += 20

    if rsi_last < 30:
        buy_score += 15

    if rsi_last > 70:
        sell_score += 15

    if stoch_last < 20:
        buy_score += 15

    if stoch_last > 80:
        sell_score += 15

    if bullish:
        buy_score += 10

    if bearish:
        sell_score += 10

    if buyers > sellers:
        buy_score += 10
    else:
        sell_score += 10

    # ==========================================
    # FINAL SIGNAL
    # ==========================================

    if buy_score > sell_score:

        signal = "BUY"
        score = buy_score

    else:

        signal = "SELL"
        score = sell_score

    # ==========================================
    # FILTER
    # ==========================================

    if score < 55:
        return None

    # ==========================================
    # SMART EXPIRATION AI
    # ==========================================

    volatility = abs(
        candle1["close"] - candle1["open"]
    )

    if adx_last > 40 and volatility > 0.0015:

        expiration = random.choice([
            "5m",
            "7m"
        ])

    elif adx_last > 25:

        expiration = random.choice([
            "2m",
            "3m"
        ])

    else:

        expiration = random.choice([
            "7m",
            "10m"
        ])

    # ==========================================
    # LEVELS
    # ==========================================

    if score >= 90:
        level = "A+"

    elif score >= 80:
        level = "A"

    else:
        level = "B"

    # ==========================================
    # RESULT
    # ==========================================

    result = {

        "pair": pair.replace("/", ""),

        "signal": signal,

        "score": score,

        "expiration": expiration,

        "buyers": buyers,

        "sellers": sellers,

        "level": level,

        "adx": round(adx_last, 1),

        "rsi": round(rsi_last, 1),

        "time": str(datetime.now())
    }

    save_signal(result)

    asyncio.create_task(
        check_signal_result(
            result,
            price
        )
    )

    return result

# ==========================================
# ROOT
# ==========================================

@app.get("/")
async def root():

    return {
        "status": "ONLINE",
        "engine": "CYBER SIGNAL AI V4"
    }

# ==========================================
# SIGNALS
# ==========================================

@app.get("/signals")
async def signals():

    results = []

    shuffled = random.sample(
        pairs,
        len(pairs)
    )

    for pair in shuffled:

        signal = analyze_pair(pair)

        if signal:
            results.append(signal)

    return results[:4]

# ==========================================
# HISTORY
# ==========================================

@app.get("/history")
async def history():

    try:

        with open("history.json", "r") as f:
            history = json.load(f)

        return history[-50:]

    except:
        return []

# ==========================================
# RESULTS
# ==========================================

@app.get("/results")
async def results():

    try:

        with open("results.json", "r") as f:
            results = json.load(f)

        return results[-50:]

    except:
        return []
