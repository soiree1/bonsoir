import asyncio
from collections import defaultdict
from datetime import datetime, timedelta

from itllib import Itl


async def nop_postprocessor(module, downstream, message):
    return message


async def nop_preprocessor(module, upstream, message):
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
        self.dest_metadata = defaultdict(dict)  # type: dict[str, int]
        self._last_attempted_response = defaultdict(
            datetime.now
        )  # type: dict[str, datetime]
        self._pending_generations = defaultdict(int)  # type: dict[str, int]
        self._default_interval_response = defaultdict(
            lambda: None
        )  # type: dict[str, timedelta]
        self._current_interval_response = defaultdict(lambda: None)
        self._active_cycles = defaultdict(int)

    def add_upstream(self, upstream: str, **kwargs):
        if upstream in self.source_metadata:
            raise ValueError(f"Upstream {upstream} already exists")
        self.source_metadata[upstream] = kwargs

        @self.itl.ondata(upstream)
        async def receive_message(data):
            data = await self.preprocessor(self, upstream, data)
            if data != None:
                metadata = self.source_metadata[upstream]
                self.accept_message(upstream, metadata, data)

    def add_downstream(self, downstream: str, **kwargs):
        if downstream in self.dest_metadata:
            raise ValueError(f"Downstream {downstream} already exists")
        self.dest_metadata[downstream] = kwargs

    def add_reaction(self, upstream, downstream):
        if downstream not in self.dest_metadata:
            raise ValueError(f"Downstream {downstream} does not exist. Make sure to call add_downstream first.")

        @self.itl.ondata(upstream)
        async def receive_message(*unused_args, **unused_kwargs):
            await self.maybe_respond(downstream)

    async def maybe_respond(self, downstream):
        print("generating a response for", downstream)
        dest_metadata = self.dest_metadata[downstream]

        self._last_attempted_response[downstream] = datetime.now()
        self._pending_generations[downstream] += 1
        self._current_interval_response[
            downstream
        ] = self._default_interval_response.get(downstream)
        response = await self.generate_response(**dest_metadata)

        data = await self.postprocessor(self, downstream, response)
        self._pending_generations[downstream] -= 1

        if data != None:
            await self.itl.stream_send(downstream, data)

    async def add_periodic_response(
        self, seconds: float, downstream: str, *args, **kwargs
    ):
        async def response_task():
            while True:
                await asyncio.sleep(seconds)
                await self.maybe_respond(downstream)

        asyncio.create_task(response_task())

    def delayed_maybe_respond(self, downstream: str, interval: timedelta):
        self._current_interval_response[downstream] = interval

    async def set_generate_interval(self, downstream: str, new_interval: timedelta):
        if downstream not in self.dest_metadata:
            raise ValueError(f"Downstream {downstream} does not exist")

        self._default_interval_response[downstream] = new_interval
        if downstream not in self._current_interval_response:
            self._current_interval_response[downstream] = new_interval
        self._active_cycles[downstream] += 1
        current_cycle = self._active_cycles[downstream]

        async def default_response_task():
            while True:
                if self._pending_generations[downstream] > 0:
                    print("pending generation")
                    await asyncio.sleep(1)
                    continue

                # Stop if a new cycle has started
                if self._active_cycles[downstream] != current_cycle:
                    print("not my cycle")
                    return

                # Get the latest interval for this cycle
                current_interval = self._current_interval_response[downstream]

                # Check if enough time has passed
                time_passed = datetime.now() - self._last_attempted_response[downstream]
                if time_passed > current_interval:
                    # If so, generate a new response
                    await self.maybe_respond(downstream)
                    # current interval might have changed, so get it again
                    current_interval = self._current_interval_response[downstream]
                    remaining_seconds = current_interval.total_seconds()
                else:
                    remaining_seconds = (current_interval - time_passed).total_seconds()

                await asyncio.sleep(remaining_seconds)

        asyncio.create_task(default_response_task())

    async def generate_response(self, **metadata):
        raise NotImplementedError()

    def accept_message(self, source: str, metadata: dict, message: str):
        raise NotImplementedError()
