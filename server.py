from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
import asyncio
import random

app = FastAPI()

price = 100.0

@app.get("/")
async def root():
    return FileResponse("index.html")

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):

    global price

    await ws.accept()

    while True:

        # fake realtime market
        price += random.uniform(-0.3, 0.3)

        await ws.send_json({
            "price": round(price, 2)
        })

        await asyncio.sleep(0.05)
app.mount("/", StaticFiles(directory=".", html=True), name="static")
