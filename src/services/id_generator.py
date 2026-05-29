import threading
from datetime import datetime, timezone

_counter = 0
_lock = threading.Lock()


def reset_counter():
    global _counter
    with _lock:
        _counter = 0


def generate_request_id() -> str:
    global _counter
    year = datetime.now(timezone.utc).year
    with _lock:
        _counter += 1
        return f"REQ-{year}-{_counter:04d}"