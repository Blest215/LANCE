import sys

from settings import *
from client import Client


class Registry(Client):
    def __init__(self, session, id):
        super().__init__(session, id)
        self.registry = {}

    async def connection_handler(self):
        await self.subscribe(MQTT_TOPIC_CENTRALIZED_REGISTER, "+")
        await self.subscribe(MQTT_TOPIC_CENTRALIZED_DISCOVERY, "+")

        await self.subscribe(MQTT_TOPIC_NATURAL_AGENT, "+")
        await self.subscribe(MQTT_TOPIC_CENTRALIZED_CONTROL, "+")

    async def message_handler(self, topic, id, sender, message, request_id=""):
        if check_topic(topic, MQTT_TOPIC_CENTRALIZED_REGISTER):
            self.registry[sender] = message

        elif check_topic(topic, MQTT_TOPIC_CENTRALIZED_DISCOVERY):
            await self.response(sender, request_id, self.registry)
            
        elif check_topic(topic, MQTT_TOPIC_NATURAL_AGENT) or check_topic(topic, MQTT_TOPIC_CENTRALIZED_CONTROL):
            if id not in self.registry:
                await self.response(sender, request_id, "INVALID AGENT ID")

def run_registry_process(session, id):
    if sys.platform.lower() == "win32" or os.name.lower() == "nt":
        from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
        set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    asyncio.run(Registry(session, id).loop())
