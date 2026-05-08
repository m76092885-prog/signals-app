from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ===== CORS =====

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

# ===== TEST ROUTE =====

@app.get("/")

async def root():

    return {

        "status": "ONLINE",

        "engine": "CYBER SIGNAL AI",

        "version": "1.0"
    }

# ===== SIGNALS =====

@app.get("/signals")

async def get_signals():

    return [

        {

            "pair": "EURUSD",

            "signal": "BUY",

            "score": 91,

            "expiration": "3m",

            "buyers": 82,

            "sellers": 18
        },

        {

            "pair": "GBPJPY",

            "signal": "SELL",

            "score": 84,

            "expiration": "5m",

            "buyers": 31,

            "sellers": 69
        }
    ]