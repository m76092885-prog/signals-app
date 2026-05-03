from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
import pandas as pd
import ta
import time
import threading

app = FastAPI()

API_KEY = "44e14a6e8f7c4360885483d51e2f4523"

SYMBOLS = [
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "AUD/USD",
    "USD/CAD"
]

TIMEFRAME = "5min"

signals = []

# ===== ЗАГРУЗКА ДАННЫХ =====
def get_data(symbol):
    try:
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={TIMEFRAME}&apikey={API_KEY}&outputsize=100"
        r = requests.get(url, timeout=10).json()

        if "values" not in r:
            return None

        df = pd.DataFrame(r["values"])
        df = df[["open", "high", "low", "close"]].astype(float)
        df = df.iloc[::-1]

        return df
    except:
        return None

# ===== ИНДИКАТОРЫ =====
def RSI(df):
    return ta.momentum.RSIIndicator(df['close'], 7).rsi()

def CCI(df):
    return ta.trend.CCIIndicator(df['high'], df['low'], df['close'], 20).cci()

def WR(df):
    return ta.momentum.WilliamsRIndicator(df['high'], df['low'], df['close'], 14).williams_r()

def EMA(df, period):
    return ta.trend.EMAIndicator(df['close'], period).ema_indicator()

# ===== ТРЕНД =====
def detect_trend(df):
    ema50 = EMA(df, 50).iloc[-1]
    ema200 = EMA(df, 200).iloc[-1]

    if ema50 > ema200:
        return "up"
    elif ema50 < ema200:
        return "down"
    return "flat"

# ===== СКОРИНГ =====
def calculate_score(df):
    rsi = RSI(df)
    cci = CCI(df)
    wr = WR(df)

    rsi_prev, rsi_now = rsi.iloc[-2], rsi.iloc[-1]
    cci_prev, cci_now = cci.iloc[-2], cci.iloc[-1]
    wr_prev, wr_now = wr.iloc[-2], wr.iloc[-1]

    score_buy = 0
    score_sell = 0

    if rsi_prev < 30 and rsi_now > 30:
        score_buy += 2
    if rsi_prev > 70 and rsi_now < 70:
        score_sell += 2

    if cci_prev < -100 and cci_now > -100:
        score_buy += 2
    if cci_prev > 100 and cci_now < 100:
        score_sell += 2

    if wr_prev < -80 and wr_now > -80:
        score_buy += 2
    if wr_prev > -20 and wr_now < -20:
        score_sell += 2

    return score_buy, score_sell

# ===== ORDER BLOCK =====
def detect_order_block(df):
    last = df.iloc[-1]
    recent = df.iloc[-12:]

    bullish_ob = None
    bearish_ob = None

    for i in range(len(recent) - 3):
        c1 = recent.iloc[i]
        c2 = recent.iloc[i+1]
        c3 = recent.iloc[i+2]

        # bullish OB
        if c1['close'] < c1['open'] and c2['close'] > c2['open'] and c3['close'] > c3['open']:
            bullish_ob = c1['low']

        # bearish OB
        if c1['close'] > c1['open'] and c2['close'] < c2['open'] and c3['close'] < c3['open']:
            bearish_ob = c1['high']

    price = last['close']

    near_buy = bullish_ob and abs(price - bullish_ob) / price < 0.002
    near_sell = bearish_ob and abs(price - bearish_ob) / price < 0.002

    return near_buy, near_sell

# ===== АНАЛИЗ =====
def analyze(df):
    score_buy, score_sell = calculate_score(df)
    trend = detect_trend(df)
    ob_buy, ob_sell = detect_order_block(df)

    # тренд
    if trend == "up":
        score_buy += 1
    if trend == "down":
        score_sell += 1

    # order block (сильный фактор)
    if ob_buy:
        score_buy += 3
    if ob_sell:
        score_sell += 3

    max_score = 10

    prob_buy = int((score_buy / max_score) * 100)
    prob_sell = int((score_sell / max_score) * 100)

    if prob_buy >= 65 and prob_buy > prob_sell:
        return "BUY", prob_buy
    elif prob_sell >= 65 and prob_sell > prob_buy:
        return "SELL", prob_sell

    return None, 0

# ===== АВТО СИГНАЛЫ =====
def auto_signals():
    while True:
        for symbol in SYMBOLS:
            df = get_data(symbol)
            if df is None or len(df) < 50:
                continue

            signal, prob = analyze(df)

            if signal:
                signals.append({
                    "symbol": symbol,
                    "signal": signal,
                    "probability": prob,
                    "time": time.time()
                })

                if len(signals) > 50:
                    signals.pop(0)

        time.sleep(60)

threading.Thread(target=auto_signals, daemon=True).start()

# ===== UI =====
@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# ===== API =====
@app.get("/signals")
def get_signals():
    return signals

@app.get("/status")
def status():
    return {"status": "running"}
