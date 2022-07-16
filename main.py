from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import RPi.GPIO as GPIO
import asyncio
import time
 
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

TL1RED = 15
TL1YELLOW = 13
TL1GREEN = 11

TL2RED = 12
TL2YELLOW = 3
TL2GREEN = 5
 
app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

GPIO.setup(TL2YELLOW, GPIO.OUT)
GPIO.output(TL2YELLOW, GPIO.LOW)

GPIO.setup(TL2RED, GPIO.OUT)
GPIO.output(TL2RED, GPIO.LOW)

GPIO.setup(TL2GREEN, GPIO.OUT)
GPIO.output(TL2GREEN, GPIO.LOW)

GPIO.setup(TL1GREEN, GPIO.OUT)
GPIO.output(TL1GREEN, GPIO.LOW)

GPIO.setup(TL1YELLOW, GPIO.OUT)
GPIO.output(TL1YELLOW, GPIO.LOW)

GPIO.setup(TL1RED, GPIO.OUT)
GPIO.output(TL1RED, GPIO.LOW)

""" green = {
        GPIO.output(TL1GREEN, GPIO.HIGH)
    }

    green = {
        GPIO.output(TL2GREEN, GPIO.HIGH)
    }

    yellow = {
        GPIO.output(TL1YELLOW, GPIO.HIGH)
    }

    yellow = {
        GPIO.output(TL2YELLOW, GPIO.HIGH)
    }

    red = {
        GPIO.output(TL1RED, GPIO.HIGH)
    }

    red = {
        GPIO.output(TL2RED, GPIO.HIGH)
    }

    redyellow = {
        GPIO.output(TL1YELLOW, GPIO.HIGH)
        GPIO.output(TL1RED, GPIO.HIGH)
    }

    redyellow = {
        GPIO.output(TL2YELLOW, GPIO.HIGH)
        GPIO.output(TL2RED, GPIO.HIGH)
    }

"""

 
class SetGPIO(BaseModel):
    on: bool

state = {
            "timestamp": time.time(),
            "zebra": False,
            "lights": [
                {
                    "id": 0,
                    "state": "red",
                },
                {
                    "id": 1,
                    "state": "green",
                    "hasCar": False,
                },
            ],
        }

@app.get("/get")
def read_root():
    """
    PIKACHU
    """
    # GPIO.setup(gpio, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    return state

@app.patch("/set/{gpio}")
def read_item(gpio: int, value: SetGPIO):
    if value.on:
        GPIO.setup(gpio, GPIO.OUT, initial=GPIO.HIGH)
    else:
        GPIO.setup(gpio, GPIO.OUT, initial=GPIO.LOW)
    state["timestamp"] = time.time()
    return {"gpio": gpio, "on": value.on}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(state)
            oldTimeStamp = state["timestamp"]
            await asyncio.sleep(1)
            print("Sending")
            while oldTimeStamp == state["timestamp"]:
                await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Websocket terminated abruptly", flush=True)