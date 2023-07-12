from typing import Union
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from route import manage, wayline
from fastapi.responses import HTMLResponse

app = FastAPI()

# http(api)
app.include_router(manage.router)
app.include_router(wayline.router)


@app.get("/back")
def check_connect():
    try:
        code = 0
        message = "connected"
        data = ""
    except:
        code = 500
        message = "fail to connect"
        data = ""
    return {"code": code, "message": message, "data": data}


# Websocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# 같은 서버에 웹소켓도 열어두기
# wireshark로 드론별 메세지 송수신 어떻게 하는지 파악하기
@app.websocket("/back/api/v1/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")