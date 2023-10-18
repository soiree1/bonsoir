import asyncio
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import heapq
import json
import os
from string import Template

from itllib import Itl

from .chatagentbase_module import ChatAgentBaseModule


class LlamaCppModule(ChatAgentBaseModule):
    def __init__(self, itl: Itl, llm, template_vars={}, *args, **kwargs):
        super().__init__(itl, *args, **kwargs)
        self.llm = llm
        self.template_vars = template_vars
        self.executor = ThreadPoolExecutor(max_workers=1)

    async def generate_response(self, prompt):
        template_vars = {
            "history": self.history,
        }
        template_vars.update(self.template_vars)

        prompt = Template(prompt).substitute(template_vars)

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            self.executor,
            lambda: self.llm(prompt),
        )

        return response["choices"][0]["text"]
