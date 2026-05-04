from fastapi import FastAPI
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
last_signal_time = {}

# ===== DATA =====

def get_data(symbol):
try:
url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={TIMEFRAME}&apikey={API_KEY}&outputsize=100"
r = requests.get(url, timeout=10).json()

```
    if "values" not in r:
        print("API ERROR:", r)
        return None

    df = pd.DataFrame(r["values"])
    df = df[["open","high","low","close"]]
    df = df.astype(float)
    df = df.iloc[::-1]

    return df
except Exception as e:
    print("DATA ERROR:", e)
    return None
```

# ===== INDICATORS =====

def RSI(df):
return ta.momentum.RSIIndicator(df['close'], 7).rsi()

def CCI(df):
return ta.trend.CCIIndicator(df['high'], df['low'], df['close'], 20).cci()

def WR(df):
return ta.momentum.WilliamsRIndicator(df['high'], df['low'], df['close'], 14).williams_r()

def EMA(df, period):
return ta.trend.EMAIndicator(df['close'], period).ema_indicator()

# ===== TREND =====

def detect_trend(df):
ema50 = EMA(df, 50).iloc[-1]
ema200 = EMA(df, 200).iloc[-1]

```
if ema50 > ema200:
    return "up"
elif ema50 < ema200:
    return "down"
return "flat"
```

# ===== SCORE =====

def calculate_score(df):
rsi = RSI(df)
cci = CCI(df)
wr = WR(df)

```
rsi_prev, rsi_now = rsi.iloc[-2], rsi.iloc[-1]
cci_prev, cci_now = cci.iloc[-2], cci.iloc[-1]
wr_prev, wr_now = wr.iloc[-2], wr.iloc[-1]

score_buy = 0
score_sell = 0
reasons = []

# RSI
if rsi_prev < 30 and rsi_now > 30:
    score_buy += 2
    reasons.append("RSI oversold → up")
if rsi_prev > 70 and rsi_now < 70:
    score_sell += 2
    reasons.append("RSI overbought → down")

# CCI
if cci_prev < -100 and cci_now > -100:
    score_buy += 2
    reasons.append("CCI breakout up")
if cci_prev > 100 and cci_now < 100:
    score_sell += 2
    reasons.append("CCI breakout down")

# WR
if wr_prev < -80 and wr_now > -80:
    score_buy += 2
    reasons.append("Williams %R buy zone")
if wr_prev > -20 and wr_now < -20:
    score_sell += 2
    reasons.append("Williams %R sell zone")

return score_buy, score_sell, reasons
```

# ===== ANALYZE =====

def analyze_symbol(df):
score_buy, score_sell, reasons = calculate_score(df)
trend = detect_trend(df)

```
if trend == "up":
    score_buy += 1
    reasons.append("Trend up")
if trend == "down":
    score_sell += 1
    reasons.append("Trend down")

max_score = 7

prob_buy = int((score_buy / max_score) * 100)
prob_sell = int((score_sell / max_score) * 100)

entry_price = df['close'].iloc[-1]

if prob_buy >= 55 and prob_buy > prob_sell:
    return "BUY", prob_buy, entry_price, ", ".join(reasons)

elif prob_sell >= 55 and prob_sell > prob_buy:
    return "SELL", prob_sell, entry_price, ", ".join(reasons)

return None, 0, None, None
```

# ===== SIGNAL ENGINE =====

def generate_signals():
global signals

```
while True:
    print("=== CHECK ===")

    for symbol in SYMBOLS:
        df = get_data(symbol)
        if df is None or len(df) < 50:
            continue

        signal, prob, price, reason = analyze_symbol(df)

        if signal:
            now = time.time()

            # анти-спам (3 минуты)
            if symbol in last_signal_time:
                if now - last_signal_time[symbol] < 180:
                    continue

            last_signal_time[symbol] = now

            signals.append({
                "symbol": symbol,
                "signal": signal,
                "probability": prob,
                "time": now,
                "entry_price": round(price, 5),
                "reason": reason
            })

            if len(signals) > 50:
                signals = signals[-50:]

            print("SIGNAL:", symbol, signal, prob)

        time.sleep(2)

    time.sleep(30)
```

# ===== API =====

@app.get("/signals")
def get_signals():
return signals

@app.get("/status")
def status():
return {"status": "running"}

# ===== START =====

threading.Thread(target=generate_signals, daemon=True).start()


