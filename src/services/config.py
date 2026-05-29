import os
from typing import Optional

class ConfigError(ValueError):
    pass

_OPENAI_API_KEY: Optional[str] = None


def load_openai_api_key():
    global _OPENAI_API_KEY
    _OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    if not _OPENAI_API_KEY:
        raise ConfigError("OPENAI_API_KEY environment variable is not set")


def get_openai_api_key() -> str:
    if _OPENAI_API_KEY is None:
        load_openai_api_key()
    return _OPENAI_API_KEY