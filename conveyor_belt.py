from collections import deque
from dataclasses import dataclass
from time import time as py_time

# Type to represent time in seconds since the Unix epoch (January 1, 1970).
type t_time = int


def time() -> t_time:
    return int(py_time())


class MinuteHourCounter:
    """Track the cumulative counts over the past minute and over the past hour.

    Useful, for example, to track recent bandwidth usage."""

    MINUTE_IN_SECONDS = 60
    HOUR_IN_SECONDS = 3600

    @dataclass(frozen=True)
    class Event:
        count: int
        time: t_time

    def __init__(self) -> None:
        self.minute_events: deque[MinuteHourCounter.Event] = deque()
        self.hour_events: deque[MinuteHourCounter.Event] = deque()

        self._minute_count = 0
        self._hour_count = 0

    def add(self, count: int):
        """
        Add a new data point (count >= 0).
        For the next minute, MinuteCount() will be larger by +count.
        For the next hour, HourCount() will be larger by +count.
        """
        now_secs = time()
        self.shift_old_events(now_secs)

        # Feed into the minute list (not into the hour list--that will happen later)
        self.minute_events.append(self.Event(count, now_secs))

        self._minute_count += count
        self._hour_count += count

    @property
    def minute_count(self) -> int:
        """Return the accumulated count over the past 60 seconds."""
        self.shift_old_events(time())
        return self._minute_count

    @property
    def hour_count(self) -> int:
        """Return the accumulated count over the past 3600 seconds."""
        self.shift_old_events(time())
        return self._hour_count

    def shift_old_events(self, now_secs: t_time):
        minute_ago = now_secs - self.MINUTE_IN_SECONDS
        hour_ago = now_secs - self.HOUR_IN_SECONDS

        # Move events more than one minute old from 'minute_events' into 'hour_events'
        # (Events older than one hour will be removed in the second loop.)
        FRONT = 0
        while self.minute_events and self.minute_events[FRONT].time <= minute_ago:
            self._minute_count -= self.minute_events[FRONT].count
            self.hour_events.append(self.minute_events.popleft())

        # Remove events more than one hour old from 'hour_events'
        while self.hour_events and self.hour_events[FRONT].time <= hour_ago:
            self._hour_count -= self.hour_events[FRONT].count
            self.hour_events.popleft()
