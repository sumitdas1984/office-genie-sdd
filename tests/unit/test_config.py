import pytest
import os


def test_api_key_loaded_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
    # Need to reload module to pick up env var
    import importlib
    import src.services.config as config
    importlib.reload(config)
    assert config.get_openai_api_key() == "sk-test-key"


def test_api_key_missing_raises():
    import os
    os.environ.pop("OPENAI_API_KEY", None)
    import importlib
    import src.services.config as config
    importlib.reload(config)
    try:
        config.get_openai_api_key()
        assert False, "Should raise ConfigError"
    except ValueError as e:
        assert "OPENAI_API_KEY" in str(e)