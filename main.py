from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from models.SetSemaphoreSchema import SetSemaphoreSchema
import logic.semaphores as semaphores

print(semaphores.SEMAPHORE_PINS)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.patch("/set")
async def set_main_light(bg: BackgroundTasks, value: SetSemaphoreSchema):
    bg.add_task(semaphores.set_semaphore, value.state)
    return {"msg": "Light changes will be applied"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(semaphores.state)
            oldTimeStamp = semaphores.state["timestamp"]
            print("Send json")
            while oldTimeStamp == semaphores.state["timestamp"]:
                await asyncio.sleep(1)
                print(f"{oldTimeStamp}, {semaphores.state['timestamp']}")
    except WebSocketDisconnect:
        print("Websocket terminated abruptly", flush=True)
