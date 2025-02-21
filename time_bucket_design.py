from collections import deque
from time import time as py_time

# Type to represent time in seconds since the Unix epoch (January 1, 1970).
type t_time = int


def time() -> t_time:
    return int(py_time())


class ConveyorQueue:
    """A queue with a maximum number of slots, where old data "falls off" the end."""

    def __init__(self, max_items: int):
        self.q: deque[int] = deque()
        self._max_items = max_items
        self._total_sum = 0

    def add_to_back(self, count: int):
        """Increment the value at the back of the queue."""
        if len(self.q) == 0:  # Make sure q has at least 1 item.
            self.shift(1)
        self.q[-1] += count
        self._total_sum += count

    def shift(self, num_shifted: int):
        """Each value in the queue is shifted forward by 'num_shifted'.
        New items are initialized to 0.
        Oldest items will be removed so there are <= max_items."""
        #  In case too many items shifted, just clear the queue.
        if num_shifted >= self._max_items:
            self.q.clear()
            self._total_sum = 0
            return

        # push all the nedded zeros
        while num_shifted > 0:
            self.q.append(0)
            num_shifted -= 1

        # pop the oldest items
        while len(self.q) > self._max_items:
            self._total_sum -= self.q.popleft()

    @property
    def total_sum(self) -> int:
        """Return the total value of all items currently in the queue."""
        return self._total_sum


class TrailingBucketCounter:
    """A class that keeps counts for the past N buckets of time.

    Example: TrailingBucketCounter(30, 60) tracks the last 30 minute-buckets of time.
    """

    def __init__(self, num_buckets: int, secs_per_bucket: int):
        self.buckets = ConveyorQueue(num_buckets)
        self.secs_per_bucket = secs_per_bucket
        self.last_update_time: t_time = 0

    def _update(self, now: t_time):
        """Calculate how many buckets of time have passed and Shift() accordingly."""
        current_bucket = now // self.secs_per_bucket
        last_update_bucket = self.last_update_time // self.secs_per_bucket

        self.buckets.shift(current_bucket - last_update_bucket)
        self.last_update_time = now

    def add(self, count: int, now: t_time):
        self._update(now)
        self.buckets.add_to_back(count)

    def trailing_count(self, now: t_time) -> int:
        """Return the total count over the last num_buckets worth of time."""
        self._update(now)
        return self.buckets.total_sum


class MinuteHourCounter:
    def __init__(self):
        self._minute_counts = TrailingBucketCounter(num_buckets=60, secs_per_bucket=1)
        self._hour_counts = TrailingBucketCounter(num_buckets=60, secs_per_bucket=60)

    def add(self, count: int):
        now = time()
        self._minute_counts.add(count, now)
        self._hour_counts.add(count, now)

    @property
    def minute_count(self) -> int:
        now = time()
        return self._minute_counts.trailing_count(now)

    @property
    def hour_count(self) -> int:
        now = time()
        return self._hour_counts.trailing_count(now)
