import json
import paho.mqtt.client as mqtt

from utils import *
from settings import *

class Registry:
    def __init__(self):
        self.id = "REGISTRY"
        self.registry = {}

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(MQTT_BROKER_ADDRESS, 1883, 60)

    def loop_forever(self):
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        self.subscribe(MQTT_TOPIC_CENTRALIZED_REGISTER, "+")
        self.subscribe(MQTT_TOPIC_CENTRALIZED_DISCOVERY, "+")

    def on_message(self, client, userdata, message):
        topic, id = message.topic.split("/")
        payload = json.loads(message.payload.decode("utf-8"))
        
        if check_topic(topic, MQTT_TOPIC_CENTRALIZED_REGISTER):
            self.registry[payload['sender']] = payload['message']

        elif check_topic(topic, MQTT_TOPIC_CENTRALIZED_DISCOVERY):
            self.client.publish(MQTT_TOPIC_RESPONSE.format(id=payload["sender"]), json.dumps({"sender": self.id, "message": self.registry, "request_id": payload["request_id"]}))

    def subscribe(self, topic, id):
        self.client.subscribe(topic.format(id=id))

    def publish(self, topic, id, message):
        self.client.publish(topic.format(id=id), json.dumps({"sender": self.id, "message": message}))

def run_registry_process(queue):
    agent = Registry()
    queue.put(agent.id)
    agent.loop_forever()