import asyncio
from collections import defaultdict
from datetime import datetime

from itllib import Itl


async def nop_postprocessor(module, source, message):
    return message


async def nop_preprocessor(module, source, message):
    return message


class GPTBaseModule:
    def __init__(
        self,
        itl: Itl,
        preprocessor=nop_preprocessor,
        postprocessor=nop_postprocessor,
    ):
        self.itl = itl
        self.preprocessor = preprocessor
        self.postprocessor = postprocessor

        self.source_metadata = defaultdict(dict)  # type: dict[str, int]

    def add_source(self, source: str, **kwargs):
        if source in self.source_metadata:
            raise ValueError(f"Source {source} already exists")
        self.source_metadata[source] = kwargs

        @self.itl.ondata(source)
        async def receive_message(data):
            data = await self.preprocessor(self, source, data)
            if data != None:
                metadata = self.source_metadata[source]
                self.accept_message(source, metadata, data)

    def add_reactive_response(self, upstream: str, downstream: str, *args, **kwargs):
        @self.itl.ondata(upstream)
        async def respond(data):
            response = await self.generate_response(*args, **kwargs)
            data = await self.postprocessor(self, downstream, response)
            if data != None:
                await self.itl.stream_send(downstream, data)

    def add_periodic_response(self, seconds: float, downstream: str, *args, **kwargs):
        async def response_task():
            while True:
                await asyncio.sleep(seconds)
                response = self.generate_response(*args, **kwargs)
                data = await self.postprocessor(self, downstream, response)
                if data != None:
                    await self.itl.stream_send(downstream, data)

        asyncio.create_task(response_task())

    async def generate_response(self, *args, **kwargs):
        raise NotImplementedError()

    def accept_message(self, source: str, metadata: dict, message: str):
        raise NotImplementedError()
