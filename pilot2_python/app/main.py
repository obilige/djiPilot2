from typing import Annotated, Union
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status, WebSocketException, Query, Depends, Cookie
from route import manage, wayline, storage
from fastapi.responses import HTMLResponse
from time import time
import json

app = FastAPI()

# http(api)
app.include_router(manage.router)
app.include_router(wayline.router)
app.include_router(storage.router)


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
            with await websocket.receive_text() as data: # 서버가 컨트롤러로부터 메시지를 받으면 아래 코드 진행
                data = eval(data) if type(data) == str else data
                print(data)
                if data['bizCode'] == "device_update_topo":
                    await manager.send_personal_message(str({"biz_code": "device_update_topo", "timestamp": str(time()), "data": {}}))
                elif data['bizCode'] == "device_online1" | "device_online2":
                    await manager.send_personal_message(str({"biz_code": f"{data['bizCode']}"}))
                    await manager.send_personal_message(str({"biz_code": "device_update_topo", "timestamp": str(time()), "data": {}}))
                elif data['bizCode'] == "device_offline1" | "device_offline2":
                    await manager.send_personal_message(str({"biz_code": f"{data['bizCode']}"}))
                    await manager.send_personal_message(str({"biz_code": "device_update_topo", "timestamp": str(time()), "data": {}}))
                elif data['bizCode'] == "device_osd":
                    await manager.send_personal_message(str({"biz_code": f"{data['bizCode']}"}))
                elif data['bizCdoe'] == "gateway_osd":
                    await manager.send_personal_message(str({"biz_code": f"{data['bizCode']}"}))
                elif data['bizCdoe'] == "osd":
                    await manager.send_personal_message(str({"biz_code": f"{data['bizCode']}"}))                
            # await manager.broadcast(f"Client #{client_id} says: {data}") # broadcast code
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
    finally:
        pass # 에러 생겨도 서버 죽지않도록
    