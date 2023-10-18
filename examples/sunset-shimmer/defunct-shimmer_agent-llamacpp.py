raise Exception(
    "The chat modules have been refactored since this script was last updated."
)

import asyncio
import os
import yaml

from llama_cpp import Llama
from eqmesh import LlamaCppModule
from itllib import Itl


# example usage
PROMPT = """<s>[INST]<<SYS>>
You are embodying the character "${character}". ${description} Your task is to participate in a chat conversation, ensuring the responses align with the persona, behavior, and characteristics of ${character}. Given a series of messages, analyze the content and context, especially the time that has elapsed since the last user's message, to decide whether to immediately reply or wait for more information.

Given the following exchanges, decide how ${character} would proceed. You must pick ONE option:
1. Wait for more information, and specify the number of seconds to wait. To take this option, specify EXACTLY the following, including the triple backticks: "```delay:{number of seconds to delay}```".
2. Respond immediately, and specify the exact words ${character} would say next. To take this option, provide ${character}'s EXACT response in triple backticks.

Make sure to conclude with one of these responses.<</SYS>>
Conversation:
${history}
[/INST]
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

    # module = ChatGPTModule(itl, "gpt-4-0613", template_vars=SUNSET_SHIMMER_DEFINITION)
    llm = Llama(
        model_path="/home/ubuntu/models/wizardlm-13b-v1.2.Q8_0.gguf",
        n_gpu_layers=99,
        main_gpu=0,
    )
    module = LlamaCppModule(itl, llm, template_vars=SUNSET_SHIMMER_DEFINITION)
    module.add_upstream("user-messages", history=10, name="Anonymous")
    module.add_upstream("sunset-shimmer", history=10, name="Sunset Shimmer")
    module.add_reactive_response("user-messages", "sunset-shimmer", PROMPT)

    itl.start_thread()
    while True:
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
