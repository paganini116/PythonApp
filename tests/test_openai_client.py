from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from date_spot_cli import openai_client


def test_build_prompt_contains_inputs():
    prompt = openai_client.build_prompt("sushi", "tacos", "Seattle", 120)

    assert "sushi" in prompt
    assert "tacos" in prompt
    assert "Seattle" in prompt
    assert "$120" in prompt


def test_get_api_key_raises_when_missing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY is not set"):
        openai_client.get_api_key()


def test_suggest_date_spots_calls_openai(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    create_mock = Mock(
        return_value=SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="1. Place A\n2. Place B\n3. Place C")
                )
            ]
        )
    )
    client_mock = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create_mock))
    )
    with patch("date_spot_cli.openai_client.OpenAI", return_value=client_mock):
        result = openai_client.suggest_date_spots("sushi", "tacos", "Seattle", 120)

    assert result == "1. Place A\n2. Place B\n3. Place C"
    create_mock.assert_called_once()
