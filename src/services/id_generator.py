from datetime import datetime, timezone

_counter = 0


def generate_request_id() -> str:
    global _counter
    _counter += 1
    year = datetime.now(timezone.utc).year
    return f"REQ-{year}-{_counter:04d}"


def reset_counter() -> None:
    global _counter
    _counter = 0