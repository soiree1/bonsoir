import asyncio
from datetime import timedelta
import json
import os
import random
import yaml

from eqmesh import ChatGPTModule
from itllib import Itl


CHARACTER_DEFINITION = {
    "character": "Sunset Shimmer",
    "description": "Sunset Shimmer is a unicorn pony with a fiery temper and a sharp tongue.",
}

LOOP = os.environ.get("LOOP_ID", random.randbytes(32).hex())

SYSTEM_PROMPT = """
You are embodying the character "${character}". ${description} Your task is to participate in a chat conversation, ensuring the responses align with the persona, behavior, and characteristics of ${character}. Given a series of messages, analyze the content and context, especially the time that has elapsed since the last user's message, to decide whether to immediately reply or wait for more information.

The responses should be structured in JSON format, with the following possible key components:
1. "delay": An optional number of seconds suggesting the maximum duration to wait for further context or information before deciding on a response.
2. "message": An optional message content representative of Sherlock Holmes' response.

For example:
{ "message": "Elementary, my dear Watson." }

Or if deciding to wait without a response yet:
{ "delay": 15 }

Now, please process the following conversation as ${character}:
"""

USER_PROMPT = """
Character: ${character}
Messages:
${history}

Decision: Based on the context and timing, decide whether to immediately respond as ${character} or wait for more information. If you decide to respond, formulate a response in line with ${character}'s character. If you decide to wait, indicate so.
"""


def create_itl(write_fn: str):
    # itl = "in-the-loop". It represents a node in the mesh that can send and receive
    # messages.
    itl = Itl()

    streams = [
        {
            "name": "user-messages",
            "source": f"ws://streams.thatone.ai:30000/api/connect/{LOOP}/user-messages",
        },
        {
            "name": "sunset-shimmer",
            "source": f"ws://streams.thatone.ai:30000/api/connect/{LOOP}/sunset-shimmer",
        },
    ]

    # Add one stream for user messages and one for the agent's responses.
    itl.update_streams(streams)

    with open(write_fn, "w") as outp:
        yaml.safe_dump({"streams": streams}, outp)

    return itl


async def postprocessor(module: ChatGPTModule, downstream, message):
    try:
        message = json.loads(message)

        if "message" in message:
            valid_generation = True
            result = message["message"]
            module.append_history("Sunset Shimmer", result)
        elif "delay" in message:
            valid_generation = True
            result = None

            delay = timedelta(seconds=int(message["delay"]))
            module.delayed_maybe_respond(downstream, delay)
            print("retrying after delay:", delay)

        if valid_generation:
            return result
    except Exception as e:
        print("exception:", e)
        raise

    print("invalid generation (trying again):", message)
    await module.maybe_respond(downstream)
    return None


async def main():
    itl = create_itl("config.yaml")

    module = ChatGPTModule(
        itl,
        "gpt-4-0613",
        template_vars=CHARACTER_DEFINITION,
        postprocessor=postprocessor,
    )

    module.add_upstream("user-messages", history=10, name="Anonymous")
    module.add_downstream(
        "sunset-shimmer",
        system_prompt=SYSTEM_PROMPT,
        user_prompt=USER_PROMPT,
    )
    module.add_reaction("user-messages", "sunset-shimmer")
    await module.set_generate_interval("sunset-shimmer", timedelta(seconds=60))

    itl.start_thread()

    try:
        while True:
            await asyncio.sleep(10)
    except asyncio.exceptions.CancelledError:
        pass
    finally:
        itl.stop_itl()


if __name__ == "__main__":
    asyncio.run(main())
