from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
import asyncio

from models.SetSemaphoreSchema import SetSemaphoreSchema
import logic.semaphores as semaphores

app = FastAPI()

runner = semaphores.BackgroundRunner()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def app_startup():
    asyncio.create_task(runner.run_main())


@app.post("/set")
async def set_main_light(bg: BackgroundTasks, value: SetSemaphoreSchema):
    if semaphores.in_animation:
        raise HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail="The backend server is not ready.",
        )

    bg.add_task(semaphores.set_semaphore, value.state)
    return {"msg": "Light changes will be applied"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(semaphores.get_state())
            await asyncio.sleep(0.5)
            oldTimeStamp = semaphores.timestamp
            while oldTimeStamp == semaphores.timestamp:
                await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        print("Websocket terminated abruptly", flush=True)
