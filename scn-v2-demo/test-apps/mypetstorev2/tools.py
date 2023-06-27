import time
import uuid

def current_millisecond_time() -> int:
    return int(time.time_ns()/1000)

def get_unique_id() -> int:
    return uuid.uuid1().int>>64