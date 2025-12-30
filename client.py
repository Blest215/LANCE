import json
import asyncio
import paho.mqtt.client as mqtt

from abc import ABC, abstractmethod

from utils import *
from settings import *


class Client(ABC):
    def __init__(self):
        self.requests = {}
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(MQTT_BROKER_ADDRESS, 1883, 60)

    def on_connect(self, client, userdata, flags, reason_code, properties):
        self.connection_handler()

    def on_message(self, client, userdata, message):
        topic, id = message.topic.split("/")
        payload = json.loads(message.payload.decode("utf-8"))
        self.message_handler(topic, id, payload)

    @abstractmethod
    def connection_handler(self):
        pass

    @abstractmethod
    def message_handler(self, topic, id, payload):
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
        self.requests[new_request_id] = {"status": "pending"}
        self.client.publish(topic.format(id=agent_id), json.dumps({"sender": self.id, "message": message, "request_id": new_request_id}))
        # TODO TIMEOUT
        while self.requests[new_request_id]["status"] == "pending":
            await asyncio.sleep(0.1)
        return self.requests[new_request_id]["response"]
    
    def response(self, sender, request_id, message):
        self.client.publish(MQTT_TOPIC_RESPONSE.format(id=sender), json.dumps({"sender": self.id, "message": message, "request_id": request_id}))
    
    def subscribe(self, topic, id):
        self.client.subscribe(topic.format(id=id))

    def publish(self, topic, id, message):
        self.client.publish(topic.format(id=id), json.dumps({"sender": self.id, "message": message}))
