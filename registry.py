import sys

from settings import *
from client import Client


class Registry(Client):
    def __init__(self):
        super().__init__(id=REGISTRY_ID)
        self.registry = {}

    async def connection_handler(self):
        await self.subscribe(MQTT_TOPIC_CENTRALIZED_REGISTER, "+")
        await self.subscribe(MQTT_TOPIC_CENTRALIZED_DISCOVERY, "+")

        await self.subscribe(MQTT_TOPIC_NATURAL_CONTROL, "+")
        await self.subscribe(MQTT_TOPIC_STRUCTURED_CONTROL, "+")

    async def message_handler(self, topic, id, sender, message, request_id):
        if check_topic(topic, MQTT_TOPIC_RESET):
            self.registry = {}

        elif check_topic(topic, MQTT_TOPIC_CENTRALIZED_REGISTER):
            self.registry[sender] = message

        elif check_topic(topic, MQTT_TOPIC_CENTRALIZED_DISCOVERY):
            await self.response(sender, request_id, self.registry)
            
        elif check_topic(topic, MQTT_TOPIC_NATURAL_CONTROL) or check_topic(topic, MQTT_TOPIC_STRUCTURED_CONTROL):
            if id not in self.registry:
                await self.response(sender, request_id, str([dict(Response(agent_id=id, request=message, success=False, message="INVALID AGENT ID"))]))
