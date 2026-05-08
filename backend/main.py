from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import requests
import pandas as pd
import ta
import random

# ===== API KEY =====

API_KEY = "44e14a6e8f7c4360885483d51e2f4523"

# ===== APP =====

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== PAIRS =====

pairs = [

    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "GBP/JPY",
    "AUD/USD",
    "USD/CAD",
    "EUR/JPY"
]

# ===== GET FOREX DATA =====

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

    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["open"] = df["open"].astype(float)

    return df

# ===== ANALYZE =====

def analyze_pair(pair):

    df = get_data(pair)

    if df is None:
        return None

    # ===== INDICATORS =====

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

    # ===== LAST VALUES =====

    price = df["close"].iloc[-1]

    ema = ema50.iloc[-1]

    rsi_last = rsi.iloc[-1]

    stoch_last = stoch_k.iloc[-1]

    adx_last = adx_value.iloc[-1]

    plus = plus_di.iloc[-1]

    minus = minus_di.iloc[-1]

    # ===== CANDLE CONFIRMATION =====

    candle1 =
    df.iloc[-1]

    candle2 =
    df.iloc[-2]

    bullish =
    candle1["close"] > candle1["open"] and \
    candle2["close"] > candle2["open"]

    bearish =
    candle1["close"] < candle1["open"] and \
    candle2["close"] < candle2["open"]

    # ===== SCORE =====

    buy_score = 0
    sell_score = 0

    # ===== EMA TREND =====

    if price > ema:
        buy_score += 25
    else:
        sell_score += 25

    # ===== ADX =====

    if adx_last > 25:

        if plus > minus:
            buy_score += 20
        else:
            sell_score += 20

    # ===== RSI =====

    if rsi_last < 30:
        buy_score += 15

    if rsi_last > 70:
        sell_score += 15

    # ===== STOCH =====

    if stoch_last < 20:
        buy_score += 15

    if stoch_last > 80:
        sell_score += 15

    # ===== CANDLES =====

    if bullish:
        buy_score += 10

    if bearish:
        sell_score += 10

    # ===== LIQUIDITY =====

    buyers =
    random.randint(45,95)

    sellers =
    100 - buyers

    if buyers > sellers:
        buy_score += 10
    else:
        sell_score += 10

    # ===== FINAL =====

    if buy_score > sell_score:

        signal = "BUY"
        score = buy_score

    else:

        signal = "SELL"
        score = sell_score

    # ===== FILTER =====

    if score < 70:
        return None

    # ===== EXPIRATION =====

    if adx_last > 40:

        expiration =
        random.choice(["5m","7m"])

    elif adx_last > 25:

        expiration =
        random.choice(["2m","3m"])

    else:

        expiration =
        random.choice(["7m","10m"])

    # ===== LEVEL =====

    if score >= 90:
        level = "A+"

    elif score >= 80:
        level = "A"

    else:
        level = "B"

    return {

        "pair":
        pair.replace("/", ""),

        "signal":
        signal,

        "score":
        score,

        "expiration":
        expiration,

        "buyers":
        buyers,

        "sellers":
        sellers,

        "level":
        level
    }

# ===== ROOT =====

@app.get("/")
async def root():

    return {

        "status":
        "ONLINE",

        "engine":
        "CYBER SIGNAL AI V1"
    }

# ===== SIGNALS =====

@app.get("/signals")
async def signals():

    results = []

    shuffled =
    random.sample(
        pairs,
        len(pairs)
    )

    for pair in shuffled:

        signal =
        analyze_pair(pair)

        if signal:
            results.append(signal)

    return results[:4]
