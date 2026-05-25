import pytest


class TestConfigValidation:
    """Test OPENAI_API_KEY environment variable validation."""

    def test_missing_api_key_raises_config_error(self, monkeypatch):
        """When OPENAI_API_KEY is not set, ConfigError is raised."""
        import os
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        from src.services.llm_service import load_api_key, ConfigError
        with pytest.raises(ConfigError) as exc_info:
            load_api_key()
        assert "OPENAI_API_KEY" in str(exc_info.value)

    def test_api_key_loaded_successfully(self, monkeypatch):
        """When OPENAI_API_KEY is set, it is returned without error."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-123")
        from src.services.llm_service import load_api_key
        key = load_api_key()
        assert key == "sk-test-key-123"