from time import time as py_time
from typing import NamedTuple

# Type to represent time in seconds since the Unix epoch (January 1, 1970).
type t_time = int


def time() -> t_time:
    return int(py_time())


class MinuteHourCounter:
    """Track the cumulative counts over the past minute and over the past hour.

    Useful, for example, to track recent bandwidth usage."""

    MINUTE_IN_SECONDS = 60
    HOUR_IN_SECONDS = 3600

    class Event(NamedTuple):
        count: int
        time: t_time

    def __init__(self):
        self.events: list[MinuteHourCounter.Event] = []

    def add(self, count: int):
        """
        Add a new data point (count >= 0).
        For the next minute, MinuteCount() will be larger by +count.
        For the next hour, HourCount() will be larger by +count.
        """
        self.events.append(self.Event(count, time()))

    def _count_since(self, cuttoff: t_time) -> int:
        count = 0
        for event in reversed(self.events):
            if event.time <= cuttoff:
                break
            count += event.count
        return count

    def minute_count(self) -> int:
        """Return the accumulated count over the past 60 seconds."""
        return self._count_since(time() - self.MINUTE_IN_SECONDS)

    def hour_count(self) -> int:
        """Return the accumulated count over the past 3600 seconds."""
        return self._count_since(time() - self.HOUR_IN_SECONDS)
