import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
import random
import yaml

from transformers.tools import OpenAiAgent
from itllib import Itl

LOOP = os.environ.get("LOOP_ID", random.randbytes(32).hex())
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)


def create_itl(write_fn: str):
    # itl = "in-the-loop". It represents a node in the mesh that can send and receive
    # messages.
    itl = Itl()

    streams = [
        {
            "name": "one-off-requests",
            "source": f"ws://streams.thatone.ai:30000/api/connect/{LOOP}/one-off-requests",
        },
        {
            "name": "chat-requests",
            "source": f"ws://streams.thatone.ai:30000/api/connect/{LOOP}/chat-requests",
        },
        {
            "name": "reset-chat",
            "source": f"ws://streams.thatone.ai:30000/api/connect/{LOOP}/reset-chat",
        },
        {
            "name": "responses",
            "source": f"ws://streams.thatone.ai:30000/api/connect/{LOOP}/responses",
        },
    ]

    # Add one stream for user messages and one for the agent's responses.
    itl.update_streams(streams)

    with open(write_fn, "w") as outp:
        yaml.safe_dump({"streams": streams}, outp)

    return itl


itl = create_itl("config-assistant.yaml")
itl.start_thread()

executor = ThreadPoolExecutor(max_workers=1)
agent = OpenAiAgent(model="gpt-4-0613", api_key=OPENAI_API_KEY)
loop = asyncio.get_event_loop()


@itl.ondata("one-off-requests")
async def handle_one_off_request(request):
    response = await loop.run_in_executor(executor, agent.run, request)
    await itl.stream_send("responses", response)


@itl.ondata("chat-requests")
async def handle_chat_request(request):
    response = await loop.run_in_executor(executor, agent.chat, request)
    await itl.stream_send("responses", response)


@itl.ondata("reset-chat")
async def handle_reset_chat(*args, **kwargs):
    agent.prepare_for_new_chat()
