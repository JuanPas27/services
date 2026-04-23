from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
import uvicorn

app = FastAPI()

# Gestor de conexiones con WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Endpoint para la conexión de mente de CST (Java)
@app.websocket("/ws/sensors")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Endpoint para recibir datos de hardware físico y cámaras
@app.post("/sensor_update")
async def update_sensor(sensor_id: str, sensor_type: str, status: str):
    payload = json.dumps({
        "sensor_id": sensor_id,
        "type": sensor_type,
        "status": status
    })
    await manager.broadcast(payload)
    return {"msg": "Dato enviado a la mente CST"}

# Endpoint para ejecutar acciones o notificaciones
@app.post("/execute_action/{action_name}")
async def execute_action(action_name: str):
    print(f"CST ordenó ejecutar: {action_name}")
    return {"status": "success", "action": action_name}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)