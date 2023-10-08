from collections import defaultdict
from datetime import datetime
import heapq
import json
import os

from .gptbase_module import GPTBaseModule


def human_readable_timedelta(td):
    minutes, seconds = divmod(td.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days = td.days

    # Create a list of non-zero time components and their names
    components = [
        (days, "day", "days"),
        (hours, "hour", "hours"),
        (minutes, "minute", "minutes"),
        (seconds, "second", "seconds"),
    ]

    # Build the human-readable string
    strings = []
    for value, singular, plural in components:
        if value == 1:
            strings.append(f"{value} {singular}")
        elif value > 1:
            strings.append(f"{value} {plural}")

    # Combine the components using commas and "and" as appropriate
    if strings:
        return ", ".join(strings)
    else:
        return "Just now"


class ChatBaseModule(GPTBaseModule):
    def __init__(self, itl, *args, **kwargs):
        super().__init__(itl, *args, **kwargs)
        self.messages = defaultdict(list)
        self._history = None
        self._last_timestamps = {}

    def accept_message(self, source: str, metadata: dict, message: str):
        orig_timestamp = datetime.now()
        self._last_timestamps[source] = orig_timestamp

        chat_time = orig_timestamp.replace(microsecond=0)
        encoded_time = chat_time.isoformat()
        encoded_message = json.dumps(message)

        chat_line = f"- [{encoded_time}] [{source}]: {encoded_message}"
        self.messages[source].append((orig_timestamp, source, chat_line))

        if len(self.messages[source]) > metadata["history"]:
            self.messages[source].pop(0)

        self._history = None

    @property
    def history(self):
        if self._history != None:
            return self._history

        used_messages = defaultdict(lambda: 0)
        candidates = []
        result = []

        # Initialize candidates with the oldest message from each source
        for source in self.messages:
            source_history = self.messages[source]
            if source_history:
                candidates.append(source_history[0])
                used_messages[source] = 1
        heapq.heapify(candidates)

        # Keep adding the oldest message to the history
        while candidates:
            _, source, chat_line = heapq.heappop(candidates)
            result.append(chat_line)
            if used_messages[source] < len(self.messages[source]):
                heapq.heappush(candidates, self.messages[source][used_messages[source]])
                used_messages[source] += 1

        self._history = "\n".join(result)
        return self._history

    @property
    def context(self):
        result = []

        for stream in self.source_metadata:
            key = f"Time Since Last {stream} Message"
            if stream in self._last_timestamps:
                value = human_readable_timedelta(
                    datetime.now() - self._last_timestamps[stream]
                )
            else:
                value = "No previous message"
            result.append(f"{key}: {value}")

        return "\n".join(result)
