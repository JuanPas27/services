from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Modelos de datos de sensores
class PressureData(BaseModel):
    deviceID: str
    Parametros: str

class BedData(BaseModel):
    deviceID: str
    Parametros: str

class CameraData(BaseModel):
    cameraId: str
    Parametros: str

# Gestor de conexiones con WebSockets (El puente hacia Java CST)
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Endpoint para que la Mente CST (Java) se conecte a escuchar
@app.websocket("/ws/cst_mind")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- ENDPOINTS PARA LOS ESP32 ---

@app.post("/api/pressure")
async def receive_pressure(data: PressureData):
    print(data)
    # Formateamos el dato para que CST lo entienda
    payload = json.dumps({
        "type": "chair_pressure",
        "sensor_id": data.deviceID,
        "status": data.Parametros
    })
    await manager.broadcast(payload) # Empujamos a CST
    return {"status": "success", "msg": "Dato de silla enviado a la mente"}

@app.post("/api/bed")
async def receive_bed(data: BedData):
    print(data)
    payload = json.dumps({
        "type": "bed_pressure",
        "sensor_id": data.deviceID,
        "status": data.Parametros
    })
    await manager.broadcast(payload)
    return {"status": "success", "msg": "Dato de cama enviado a la mente"}

@app.post("/api/camera")
async def receive_camera(data: CameraData):
    payload = json.dumps({
        "type": "camera", # table_cam o bed_cam dependiendo del cameraId
        "sensor_id": data.cameraId,
        "status": data.Parametros
    })
    await manager.broadcast(payload)
    return {"status": "success", "msg": "Inferencia de cámara enviada a la mente"}