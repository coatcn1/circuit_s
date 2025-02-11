from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import json
import cv2
import os

app = FastAPI(title="Circuit Server")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket 连接池
connections = {}

@app.get("/api/v1/devices", response_model=list)
async def get_connected_devices():
    return list(connections.keys())

@app.websocket("/api/v1/devices/commands")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    device_id = None
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # 处理心跳包（包含 device_id）
            if message.get("cmd") == "heartbeat":
                device_id = message.get("device_id")
                if device_id:
                    connections[device_id] = websocket
                    print(f"Device {device_id} registered via heartbeat")
                else:
                    print("Heartbeat received without device_id")

            # 处理开始巡检消息
            elif message.get("cmd") == "start_inspection":
                target_device_id = message.get("inspection_id")
                if target_device_id:
                    print(f"Forwarding start_inspection to {target_device_id}")
                    await forward_to_device(target_device_id, data)
                else:
                    print("No inspection_id found in start_inspection message")

            # 处理停止巡检消息
            elif message.get("cmd") == "stop_inspection":
                target_device_id = message.get("inspection_id")
                if target_device_id:
                    print(f"Forwarding stop_inspection to {target_device_id}")
                    await forward_to_device(target_device_id, data)
                else:
                    print("No inspection_id found in stop_inspection message")

            print(f"Received data from {device_id}: {data}")
    except WebSocketDisconnect:
        print(f"Device {device_id} disconnected")
        if device_id in connections:
            connections.pop(device_id, None)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

async def forward_to_device(device_id: str, message: str):
    if device_id:
        device_websocket = connections.get(device_id)
        if device_websocket:
            await device_websocket.send_text(message)
            print(f"Message forwarded to device {device_id}")
        else:
            print(f"No active connection for device {device_id}")
    else:
        print("No device_id provided for forwarding")

# 挂载静态文件目录（模板目录）
app.mount("/static", StaticFiles(directory="app/templates"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/web", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


