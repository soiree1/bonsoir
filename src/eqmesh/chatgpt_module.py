import asyncio
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import heapq
import json
import os
from string import Template


from itllib import Itl
import openai

from .chatbase_module import ChatBaseModule


DEFAULT_API_KEY = os.environ.get("OPENAI_API_KEY", None)


class ChatGPTModule(ChatBaseModule):
    def __init__(self, itl, model, api_key=None, template_vars={}, *args, **kwargs):
        super().__init__(itl, *args, **kwargs)

        if api_key is None:
            api_key = DEFAULT_API_KEY

        self.model = model
        self.api_key = api_key
        self.template_vars = template_vars
        self.executor = ThreadPoolExecutor(max_workers=1)

    async def generate_response(self, system_prompt, user_prompt):
        template_vars = {
            "history": self.history,
            "context": self.context,
        }
        template_vars.update(self.template_vars)

        system_prompt = Template(system_prompt).substitute(template_vars)
        user_prompt = Template(user_prompt).substitute(template_vars)

        orig_key = openai.api_key
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            openai.api_key = self.api_key
            loop = asyncio.get_running_loop()

            response = await loop.run_in_executor(
                self.executor,
                lambda: openai.ChatCompletion.create(
                    model=self.model, messages=messages
                ),
            )
        finally:
            openai.api_key = orig_key

        return response
