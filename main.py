```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import requests
import pandas as pd
import ta

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
    "GBP/JPY",
    "USD/JPY",
    "GBP/USD",
    "AUD/USD"
]

# ===== GET FOREX DATA =====

def get_data(pair):

    url = f"https://api.twelvedata.com/time_series?symbol={pair}&interval=1min&outputsize=100&apikey={API_KEY}"

    response = requests.get(url).json()

    values = response.get("values", [])

    if not values:
        return None

    df = pd.DataFrame(values)

    df = df.iloc[::-1]

    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)

    return df

# ===== SIGNAL ENGINE =====

def analyze_pair(pair):

    df = get_data(pair)

    if df is None:
        return None

    # ===== EMA =====

    ema50 =
    ta.trend.EMAIndicator(
        close=df["close"],
        window=50
    ).ema_indicator()

    # ===== RSI =====

    rsi =
    ta.momentum.RSIIndicator(
        close=df["close"],
        window=14
    ).rsi()

    # ===== STOCH =====

    stoch =
    ta.momentum.StochasticOscillator(

        high=df["high"],
        low=df["low"],
        close=df["close"]

    )

    stoch_k =
    stoch.stoch()

    # ===== ADX =====

    adx =
    ta.trend.ADXIndicator(

        high=df["high"],
        low=df["low"],
        close=df["close"]

    )

    adx_value =
    adx.adx()

    plus_di =
    adx.adx_pos()

    minus_di =
    adx.adx_neg()

    # ===== LAST VALUES =====

    price =
    df["close"].iloc[-1]

    ema =
    ema50.iloc[-1]

    rsi_last =
    rsi.iloc[-1]

    stoch_last =
    stoch_k.iloc[-1]

    adx_last =
    adx_value.iloc[-1]

    plus =
    plus_di.iloc[-1]

    minus =
    minus_di.iloc[-1]

    # ===== SCORE =====

    buy_score = 0
    sell_score = 0

    # ===== TREND =====

    if price > ema:
        buy_score += 25
    else:
        sell_score += 25

    # ===== ADX =====

    if adx_last > 25:

        if plus > minus:
            buy_score += 25
        else:
            sell_score += 25

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

    # ===== RESULT =====

    if buy_score > sell_score:

        signal = "BUY"
        score = buy_score

    else:

        signal = "SELL"
        score = sell_score

    # ===== EXPIRATION =====

    if adx_last > 40:
        expiration = "5m"

    elif adx_last > 25:
        expiration = "3m"

    else:
        expiration = "7m"

    # ===== BUYERS SELLERS =====

    buyers =
    min(95, int(buy_score * 1.2))

    sellers =
    min(95, int(sell_score * 1.2))

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
        sellers
    }

# ===== ROOT =====

@app.get("/")

async def root():

    return {

        "status":
        "ONLINE",

        "engine":
        "CYBER SIGNAL AI"
    }

# ===== SIGNALS =====

@app.get("/signals")

async def signals():

    results = []

    for pair in pairs:

        signal =
        analyze_pair(pair)

        if signal:

            if signal["score"] >= 70:

                results.append(signal)

    return results
```
