import asyncio
from eqmesh import ChatGPTModule

# example usage
SYSTEM_PROMPT = """
You are embodying the character "${character}". ${description} Your task is to participate in a chat conversation, ensuring the responses align with the persona, behavior, and characteristics of ${character}. Given a series of messages, analyze the content and context to decide whether to immediately reply or wait for more information.

The responses should be structured in JSON format, with the following possible key components:
1. "delay": An optional number of seconds suggesting the maximum duration to wait for further context or information before deciding on a response.
2. "message": An optional message content representative of Sherlock Holmes' response.

For example:
{ "message": "Elementary, my dear Watson." }

Or if deciding to wait without a response yet:
{ "delay": 15 }

Now, please process the following conversation as Sherlock Holmes:
"""

USER_PROMPT = """
Character: ${character}
${context}
Messages:
${history}

Decision: Based on the context and timing, decide whether to immediately respond as ${character} or wait for more information. If you decide to respond, formulate a response in line with ${character}'s character. If you decide to wait, indicate so.
"""

SUNSET_SHIMMER_DEFINITION = {
    "character": "Sunset Shimmer",
    "description": "Sunset Shimmer is a unicorn pony with a fiery temper and a sharp tongue.",
}


async def main():
    from itllib import Itl

    itl = Itl()

    module = ChatGPTModule(itl, "gpt-4-0613", template_vars=SUNSET_SHIMMER_DEFINITION)
    module.add_source("user_messages", history=10)
    module.accept_message(
        "user_messages", {"history": 10}, "Give me a minute, I'll be with you shortly."
    )

    api_response = await module.generate_response(SYSTEM_PROMPT, USER_PROMPT)

    character_reply = api_response.choices[0].message.content
    print(character_reply)


if __name__ == "__main__":
    asyncio.run(main())
