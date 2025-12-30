from utils import *
from settings import *
from client import Client


class Registry(Client):
    def __init__(self):
        super().__init__()

        self.id = "REGISTRY"
        self.registry = {}

    def connection_handler(self):
        self.subscribe(MQTT_TOPIC_CENTRALIZED_REGISTER, "+")
        self.subscribe(MQTT_TOPIC_CENTRALIZED_DISCOVERY, "+")

    def message_handler(self, topic, id, payload):        
        if check_topic(topic, MQTT_TOPIC_CENTRALIZED_REGISTER):
            self.registry[payload['sender']] = payload['message']

        elif check_topic(topic, MQTT_TOPIC_CENTRALIZED_DISCOVERY):
            self.response(payload["sender"], payload["request_id"], self.registry)

def run_registry_process(queue):
    registry = Registry()
    queue.put(registry.id)
    registry.loop_forever()
