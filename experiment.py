import asyncio
import multiprocessing

from agent import *
from user import UserAgent

agent_configuration = {"model": "qwen3:8b", "reasoning": True, "temperature": 0.8, "num_predict": 2048}
device_informations = [l for l in open("example.txt", "r", encoding="utf-8")]

async def main():
    processes = []
    for device in device_informations:
        p = multiprocessing.Process(target=run_agent_process, args=(agent_configuration, device))
        p.start()
        processes.append(p)

    await asyncio.sleep(1)

    user = UserAgent(agent_configuration)
    await user.ask("It's too dark, and I need to focus on reading.")

    for p in processes:
        p.terminate()

if __name__ == "__main__":
    asyncio.run(main())
