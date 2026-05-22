```python id="jlwm3n"
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
async def signal(

    asset:str="CC1!",
    timeframe:str="5m",
    trend_only:bool=False

):

    await asyncio.sleep(4)

    side = random.choice([
        "BUY",
        "SELL"
    ])

    entry = round(
        random.uniform(1200,1400),
        2
    )

    sl = round(
        entry - random.uniform(10,20),
        2
    )

    tp1 = round(
        entry + random.uniform(20,40),
        2
    )

    tp2 = round(
        entry + random.uniform(50,80),
        2
    )

    confidence = random.randint(
        74,
        92
    )

    return {

        "asset":asset,

        "side":side,

        "entry":entry,

        "sl":sl,

        "tp1":tp1,

        "tp2":tp2,

        "confidence":confidence,

        "reasons":[

            "Liquidity sweep detected",

            "Volume spike confirmed",

            "Trend continuation structure",

            "Momentum confirmation"
        ]
    }
```
