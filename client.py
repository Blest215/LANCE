import json
import asyncio
import aiomqtt

from datetime import datetime
from abc import ABC, abstractmethod

from settings import *


class Client(ABC):
    def __init__(self, session, id):
        self.session = session
        self.id = id
        self.requests = {}
        self.logs = []
        self.consequences = []
        self.is_connected = False
        
        # LANCE
        self.current_team_id = None
        self.team_messages = []

        self.client = None

    @abstractmethod
    async def connection_handler(self):
        pass

    @abstractmethod
    async def message_handler(self, topic, id, sender, message, request_id):
        pass

    async def on_message(self, topic, id, sender, message, request_id=""):
        try:
            await self.message_handler(topic, id, sender, message, request_id)
        except Exception as e:
            self.log(type(e).__name__)

    async def loop(self):
        self.client = aiomqtt.Client(MQTT_BROKER_ADDRESS)
        while True:
            try:
                async with self.client:
                    self.is_connected = True
                    
                    # Connection
                    await self.connection_handler()
                    await self.subscribe(MQTT_TOPIC_RESPONSE, self.id)
                    await self.publish(MQTT_TOPIC_ALIVE, self.id, "ALIVE")
                    
                    # Message
                    async for message in self.client.messages:
                        try:
                            payload = json.loads(message.payload.decode("utf-8"))
                            session, topic, id = str(message.topic).split("/")
                            if session == self.session:
                                sender, message, request_id = payload.get("sender", "UNKNOWN"), payload.get("message", "EMPTY"), payload.get("request_id", "")
                                asyncio.create_task(self.on_message(topic, id, sender, message, request_id))
                        except Exception as e:
                            if payload.get("request_id", ""):
                                await self.response(sender, request_id, type(e).__name__)
            
            # Connection lost
            except aiomqtt.MqttError:
                self.is_connected = False
                await asyncio.sleep(MQTT_RECONNECT_DELAY)

    def log(self, text, agent_id=None):
        self.logs.append(f"[{datetime.now().strftime('%Y%m%d_%H%M%S')}] {f'Agent {agent_id} ' if agent_id else ''}{text}")

    async def request(self, topic, agent_id, message):
        new_request_id = get_random_request_id()
        self.log(f"New request to agent {agent_id} {message}")
        self.requests[new_request_id] = {"status": "pending"}
        await self.client.publish(self.build_topic(topic, agent_id), json.dumps({"sender": self.id, "message": message, "request_id": new_request_id}))

        try:
            await asyncio.wait_for(self.wait_for_response(new_request_id), TIMEOUT_LIMIT)
        except asyncio.TimeoutError:
            self.requests[new_request_id]["status"] = "timeout"
            self.requests[new_request_id]["response"] = "timeout"
        
        self.log(f"Agent {agent_id} responded {self.requests[new_request_id]['response']}")
        return self.requests[new_request_id]["response"]
    
    async def wait_for_response(self, request_id):
        while self.requests[request_id]["status"] == "pending":
            await asyncio.sleep(TICK)

    async def response(self, sender, request_id, message):
        await self.client.publish(self.build_topic(MQTT_TOPIC_RESPONSE, sender), json.dumps({"sender": self.id, "message": str(message), "request_id": request_id}))

    async def publish(self, topic, id, message):
        await self.client.publish(self.build_topic(topic, id), json.dumps({"sender": self.id, "message": str(message)}))
    
    async def subscribe(self, topic, id):
        await self.client.subscribe(self.build_topic(topic, id))

    def build_topic(self, topic, id):
        return f"{self.session}/{topic}/{id}"
    
    def reset(self):
        self.requests = {}
        self.logs = []
        self.consequences = []
        self.current_team_id = None
        self.team_messages = []
