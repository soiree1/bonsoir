import asyncio
import os
import yaml

from eqmesh import ChatGPTModule
from itllib import Itl

# example usage
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

SUNSET_SHIMMER_DEFINITION = {
    "character": "Sunset Shimmer",
    "description": "Sunset Shimmer is a unicorn pony with a fiery temper and a sharp tongue.",
}


def create_itl():
    itl = Itl()

    path = os.path.dirname(__file__)
    with open(os.path.join(path, "config.yaml"), "r") as f:
        config = yaml.safe_load(f)

    itl.apply_config(config, os.path.join(path, "secrets"))

    return itl


async def main():
    itl = create_itl()

    module = ChatGPTModule(itl, "gpt-4-0613", template_vars=SUNSET_SHIMMER_DEFINITION)
    module.add_source("user-messages", history=10, name="Anonymous")
    module.add_source("sunset-shimmer", history=10, name="Sunset Shimmer")
    module.add_reactive_response(
        "user-messages", "sunset-shimmer", SYSTEM_PROMPT, USER_PROMPT
    )

    itl.start_thread()
    while True:
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
