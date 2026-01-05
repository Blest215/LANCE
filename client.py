import json
import asyncio
import paho.mqtt.client as mqtt

from abc import ABC, abstractmethod

from utils import *
from settings import *


class Client(ABC):
    def __init__(self, session, id):
        self.session = session
        self.id = id
        self.requests = {}

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(MQTT_BROKER_ADDRESS, 1883, 60)

    def on_connect(self, client, userdata, flags, reason_code, properties):
        self.connection_handler()
        self.subscribe(MQTT_TOPIC_RESPONSE, self.id)
        self.publish(MQTT_TOPIC_ALIVE, self.id, "ALIVE")

    def on_message(self, client, userdata, message):
        try:
            session, topic, id = message.topic.split("/")
            assert session == self.session
            payload = json.loads(message.payload.decode("utf-8"))
            sender, message, request_id = payload.get("sender", "UNKNOWN"), payload.get("message", "EMPTY"), payload.get("request_id", "")
            asyncio.run(self.message_handler(topic, id, sender, message, request_id))
        except Exception as e:
            self.log(type(e).__name__)
            if payload.get("request_id", ""):
                self.response(sender, request_id, type(e).__name__)

    @abstractmethod
    def connection_handler(self):
        pass

    @abstractmethod
    async def message_handler(self, topic, id, sender, message, request_id=""):
        pass

    def loop_start(self):
        self.client.loop_start()

    def loop_forever(self):
        self.client.loop_forever()

    def is_connected(self):
        return self.client.is_connected()

    def log(self, text):
        self.publish(MQTT_TOPIC_LOG, self.id, text)

    async def request(self, topic, agent_id, message):
        new_request_id = get_random_request_id()
        self.log(f"New request {new_request_id} to {agent_id}: {message}")
        self.requests[new_request_id] = {"status": "pending"}
        self.client.publish(self.build_topic(topic, agent_id), json.dumps({"sender": self.id, "message": message, "request_id": new_request_id}))

        try:
            await asyncio.wait_for(self.wait_for_response(new_request_id), TIMEOUT_LIMIT)
        except asyncio.TimeoutError:
            self.requests[new_request_id]["status"] = "timeout"
            self.requests[new_request_id]["response"] = "timeout"
        
        self.log(f"Request {new_request_id} resulted {self.requests[new_request_id]['response']}")
        return self.requests[new_request_id]["response"]
    
    async def wait_for_response(self, request_id):
        while self.requests[request_id]["status"] == "pending":
            await asyncio.sleep(TICK)

    def response(self, sender, request_id, message):
        self.client.publish(self.build_topic(MQTT_TOPIC_RESPONSE, sender), json.dumps({"sender": self.id, "message": message, "request_id": request_id}))

    def publish(self, topic, id, message):
        self.client.publish(self.build_topic(topic, id), json.dumps({"sender": self.id, "message": message}))
    
    def subscribe(self, topic, id):
        self.client.subscribe(self.build_topic(topic, id))

    def build_topic(self, topic, id):
        return f"{self.session}/{topic}/{id}"
