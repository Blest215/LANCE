import asyncio
import json
import sys
import os
import argparse

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

from settings import *
from model import Model
from user import UserAgent
from registry import Registry

class MessageRequest(BaseModel):
    message: str

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        try:
            self.active_connections.remove(websocket)
        except ValueError:
            pass

    async def send(self, message: str):
        if not message:
            return
        
        for connection in list(self.active_connections):
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                await self.disconnect(connection)

@app.get('/')
async def index():
    return FileResponse('templates/index.html')

@app.post('/ask')
async def ask(request_data: MessageRequest):
    user_message = request_data.message.strip()

    try:
        user.requests = {}
        user.consequences = []
        user.set_agents(eval(await user.request(MQTT_TOPIC_CENTRALIZED_DISCOVERY, REGISTRY_ID, "")).keys())

        proposals = await user.recruit(user_message, True)
        await manager.send(proposals)

        plan = await user.plan(user.natural, user_message, proposals)
        for tool_call in plan.tool_calls:
            await manager.send(f"{tool_call['args']['agent_id']}: {tool_call['args']['instruction']}")

        await user.control(MQTT_TOPIC_NATURAL_CONTROL, plan)
        for consequence in user.consequences:
            await manager.send(f"[{'**success**' if consequence['success'] else '**failed**'}] {consequence['agent_id']}: {consequence['request']}")

        return {}

    except Exception as e:
        import traceback
        await manager.send(f"{str(e)}\n{traceback.format_exc()}")
        return {}

@app.post('/clear')
async def clear():
    return {'status': 'cleared'}

@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            _ = await websocket.receive_text()
    except Exception:
        pass
    finally:
        await manager.disconnect(websocket)


async def main(broker_address: str, session: str):    
    registry_task = asyncio.create_task(registry.loop(broker_address))
    user_task = asyncio.create_task(user.loop(broker_address))
    
    while not registry.is_connected or not user.is_connected:
        await asyncio.sleep(TICK)
    
    await user.reset(session)
    await registry.reset(session)
    
    config = uvicorn.Config(app=app, host='0.0.0.0', port=5000, log_level='info', lifespan='off')
    server = uvicorn.Server(config)
    server_task = asyncio.create_task(server.serve())
    
    try:
        await asyncio.gather(registry_task, user_task, server_task)
    except KeyboardInterrupt:
        print("Shutting down...")
        server.should_exit = True
        registry_task.cancel()
        user_task.cancel()


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--model", type=str, required=False, default="qwen3:4b-instruct-2507-q8_0")
    argument_parser.add_argument("--broker", type=str, required=False, default="192.168.0.2")
    argument_parser.add_argument("--session", type=str, required=False, default="0000000000000000")
    args = argument_parser.parse_args()
    
    if sys.platform.lower() == "win32" or os.name.lower() == "nt":
        from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
        set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    manager = ConnectionManager()

    registry = Registry()
    user = UserAgent(id="COORDINATOR", model=Model(args.model))
    
    asyncio.run(main(args.broker, args.session))
