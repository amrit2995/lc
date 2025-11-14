from kuber_data_sync.configs import CommonConfigs
from delta_sdk.utils import logging
from datetime import datetime
import threading
import gc
import pytz

class PeriodicGC:
    def __init__(self):
        self.timer = None
        self.cancelled = False
        self.running = False

    def start(self):
        """Start GC loop"""
        if self.running:
            logging.warning("Garbage Collection Service is already running.")
            return

        self.running = True
        self.cancelled = False
        logging.info(f"Garbage Collection Service Started at: {datetime.now(tz=pytz.timezone(CommonConfigs.TIMEZONE)).strftime(CommonConfigs.DATE_TIME_FORMAT)}.")
        logging.info(f"Interval: {CommonConfigs.GC_INTERVAL} seconds")
        self.schedule_next_gc()

    def schedule_next_gc(self):
        """Trigger GC in regular intervals"""
        try:
            gc.collect()
            logging.info(f"Garbage Collection Service Triggered at: {datetime.now(tz=pytz.timezone(CommonConfigs.TIMEZONE)).strftime(CommonConfigs.DATE_TIME_FORMAT)}.")

            if not self.cancelled:
                self.timer = threading.Timer(CommonConfigs.GC_INTERVAL, self.schedule_next_gc)
                self.timer.start()
        except Exception as e:
            logging.error(f"Error in GC: {type(e).__name__}: {e}")

    def cancel(self):
        """Cancel GC loop"""
        if not self.running:
            logging.warning("Garbage Collection Service is not running.")
            return

        self.cancelled = True  # Ensure no new timers are scheduled
        self.running = False

        if self.timer is not None:
            self.timer.cancel()
            self.timer = None  # Clean up timer reference

        logging.info(f"Garbage Collection cancelled at: {datetime.now(tz=pytz.timezone(CommonConfigs.TIMEZONE)).strftime(CommonConfigs.DATE_TIME_FORMAT)}.")
