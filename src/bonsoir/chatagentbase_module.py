from collections import defaultdict
from datetime import datetime, timedelta
import heapq
import json

from itllib import Itl

from .agentbase_module import AgentBaseModule


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


class ChatAgentBaseModule(AgentBaseModule):
    def __init__(self, itl: Itl, *args, **kwargs):
        super().__init__(itl, *args, **kwargs)
        self.messages = defaultdict(list)
        self._history = None
        self._last_timestamps = {}
        self._time_offset = timedelta(seconds=0)
        self._names = {}
        self._name_references = defaultdict(object)

    def accept_message(self, source: str, metadata: dict, message: str):
        self._names[source] = metadata.get("name", source)

        orig_timestamp = datetime.now() + self._time_offset
        self._last_timestamps[source] = orig_timestamp

        encoded_message = json.dumps(message)
        self.messages[source].append((orig_timestamp, source, encoded_message))

        if len(self.messages[source]) > metadata.get("history", 1):
            self.messages[source].pop(0)

        self._history = None

    def append_history(self, name, message):
        reference = self._name_references[name]
        self.accept_message(reference, {"name": name}, message)

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
            timestamp, source, message = heapq.heappop(candidates)
            relative_time = human_readable_timedelta(
                datetime.now() - timestamp + self._time_offset
            )
            name = self._names.get(source, source)
            # Note: putting the time info after the message seems to work much better than before
            chat_line = f"- [{name}]: {message} [Sent {relative_time} ago]"

            result.append(chat_line)
            if used_messages[source] < len(self.messages[source]):
                heapq.heappush(candidates, self.messages[source][used_messages[source]])
                used_messages[source] += 1

        self._history = "\n".join(result)
        return self._history

    def timeskip(self, interval: timedelta):
        self._time_offset += interval
