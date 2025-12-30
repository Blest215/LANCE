import json
import asyncio
import multiprocessing

from utils import *
from settings import *
from registry import run_registry_process
from agent import run_agent_process
from user import UserAgent

agent_configuration = {"model": "qwen3:8b", "reasoning": True, "temperature": 0.8, "num_predict": 2048}
device_informations = [l for l in open("example.txt", "r", encoding="utf-8")]

async def main(mode: str):
    assert mode in ALLOWED_MODES
    queue = multiprocessing.Queue()

    # Set the registry
    registry = multiprocessing.Process(target=run_registry_process, args=(queue, ))
    registry.start()
    if queue.get() == "REGISTRY":
        pass

    # Set the device agents
    processes = []
    for d in device_informations:
        device_information = json.loads(d)
        agent_id = device_information["deviceId"] if "deviceId" in device_information else get_random_device_id()
        p = multiprocessing.Process(target=run_agent_process, args=(queue, agent_id, agent_configuration, device_information))
        processes.append(p)
        p.start()
        if queue.get() == agent_id:
            pass

    # Start a simulation
    user = UserAgent(configuration=agent_configuration)
    while not user.is_connected():
        await asyncio.sleep(0.1)
    await user.command(mode=mode, user_command="It's too dark, and I need to focus on reading.")

    # Wrap up
    registry.terminate()
    for p in processes:
        p.terminate()

if __name__ == "__main__":
    asyncio.run(main(mode="NATURAL"))
