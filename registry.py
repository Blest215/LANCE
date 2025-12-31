from utils import *
from settings import *
from client import Client


class Registry(Client):
    def __init__(self, session, id):
        super().__init__(session, id)
        self.registry = {}

    def connection_handler(self):
        self.subscribe(MQTT_TOPIC_CENTRALIZED_REGISTER, "+")
        self.subscribe(MQTT_TOPIC_CENTRALIZED_DISCOVERY, "+")

    async def message_handler(self, topic, id, sender, message, request_id=""):
        if check_topic(topic, MQTT_TOPIC_CENTRALIZED_REGISTER):
            self.registry[sender] = message

        elif check_topic(topic, MQTT_TOPIC_CENTRALIZED_DISCOVERY):
            self.response(sender, request_id, self.registry)

def run_registry_process(session, id):
    Registry(session, id).loop_forever()
