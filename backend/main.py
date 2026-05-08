```python id="8p8tbd"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    return {"status": "online"}

@app.get("/signals")
async def signals():

    return [
        {
            "pair": "EURUSD",
            "signal": "BUY",
            "score": 91,
            "expiration": "3m",
            "buyers": 82,
            "sellers": 18
        }
    ]
```
