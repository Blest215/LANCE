import asyncio
import multiprocessing

from agent import *
from user import UserAgent

agent_configuration = {"model": "qwen3:8b", "reasoning": True, "temperature": 0.8, "num_predict": 2048}
device_informations = [l for l in open("example.txt", "r", encoding="utf-8")]

async def main(mode: str):
    assert mode in ALLOWED_MODES

    # Set the user agent as a coordinator
    user = UserAgent(configuration=agent_configuration)

    # Set the device agents
    queue = multiprocessing.Queue()
    processes = []
    for d in device_informations:
        device_information = json.loads(d)
        agent_id = device_information["deviceId"] if "deviceId" in device_information else get_random_device_id()
        p = multiprocessing.Process(target=run_agent_process, args=(queue, agent_id, agent_configuration, device_information))
        processes.append(p)
        p.start()

        if queue.get() == agent_id:
            continue

    # Start a simulation
    await user.ask(mode=mode, user_command="It's too dark, and I need to focus on reading.")

    print("\n".join(user.logs))

    # Wrap up
    for p in processes:
        p.terminate()

if __name__ == "__main__":
    asyncio.run(main(mode="LANCE"))
