```python id="jlwm5n"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():

    return {
        "status":"running"
    }

@app.get("/signal")
async def get_signal(

    asset:str="CC1!",
    timeframe:str="5m",
    trend_only:bool=False

):

    await asyncio.sleep(5)

    side = random.choice([
        "BUY",
        "SELL"
    ])

    confidence = random.randint(70,92)

    entry = round(
        random.uniform(1200,1400),
        2
    )

    sl = round(
        entry - random.uniform(10,25),
        2
    )

    tp1 = round(
        entry + random.uniform(15,35),
        2
    )

    tp2 = round(
        entry + random.uniform(40,70),
        2
    )

    reasons = [

        "Liquidity sweep detected",

        "Volume spike confirmed",

        "Strong momentum candle",

        "Trend continuation structure",

        "Smart money confirmation"
    ]

    return {

        "asset":asset,

        "timeframe":timeframe,

        "side":side,

        "confidence":confidence,

        "entry":entry,

        "sl":sl,

        "tp1":tp1,

        "tp2":tp2,

        "trend_only":trend_only,

        "reasons":random.sample(
            reasons,
            4
        )
    }
```
