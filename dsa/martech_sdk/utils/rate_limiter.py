from martech_sdk.utils import logging
import time

class SingletonMeta(type):
    """SingleTon Meta"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        key = ('|'.join(args), '|'.join([f"{key}:{value if value else ''}" for key, value in kwargs.items()]))
        if key not in cls._instances:
            cls._instances[key] = super().__call__(*args, **kwargs)
        return cls._instances[key]

class RateLimiter(metaclass=SingletonMeta):
    """Ratelimiter Generator
        Args::
            name: | Optional
            mode: | Optional
            tps: | when mode is 'regular_interval'
            ceiling: | when mode is 'by_ceiling'
            time_window: | when mode is 'by_ceiling'
    """

    class RateLimiterModes:
        REGULAR_INTERVAL = 'regular_interval'
        BY_CEILING = "by_ceiling"

    mode = RateLimiterModes

    def __init__(self, name='ratelimiter', mode=mode.REGULAR_INTERVAL, tps=None, ceiling=None, time_window=None):
        self.name = name
        self.mode = mode

        if self.mode == RateLimiter.mode.BY_CEILING:

            if not (ceiling and time_window):
                ValueError("Either 'ceiling' or ''time_window' not provided.")

            self.strategy = self.next_by_ceiling
            self.freq = 0
            self.ceiling = ceiling
            self.start_time = time.time()
            self.time_window = time_window

        elif self.mode == RateLimiter.mode.REGULAR_INTERVAL:

            if not (tps): raise ValueError("'tps' not provided.")
            self.strategy = self.next_by_regular_interval
            self.time_window = (1/tps)

    def __iter__(self):
        return self

    def next_by_regular_interval(self):
        if delay:= ( time.time() - self.last_called - self.time_window ) > 0 :
            logging.info(f"wait for {delay} seconds")
            time.sleep(delay)
        self.last_called = time.time()

    def next_by_ceiling(self):
        self.freq += 1
        current_time = time.time()
        if current_time > self.start_time + self.time_window:
            self.start_time = current_time
            self.freq = 0

        if self.freq > self.ceiling:
            delay = self.start_time + self.time_window - current_time
            logging.info(f"Ceiling hit . Please wait for {delay} seconds")
            time.sleep(delay)

    def __next__(self):
        self.strategy()
        return True
