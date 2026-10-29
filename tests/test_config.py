"""配置读取与密钥打码的测试（不需要网络和真实 Key）。"""

from __future__ import annotations

import pytest

from llm_demo.config import DEFAULT_BASE_URL, DEFAULT_MODEL, ConfigError, Settings, mask_key


def test_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ConfigError, match="OPENAI_API_KEY"):
        Settings.from_env(env_file=None)


def test_reads_values_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-12345678")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.com/v1/")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")

    settings = Settings.from_env(env_file=None)

    assert settings.api_key == "sk-test-12345678"
    assert settings.base_url == "https://example.com/v1"  # 末尾斜杠会被去掉
    assert settings.model == "test-model"


def test_defaults_when_only_key_is_set(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)

    settings = Settings.from_env(env_file=None)

    assert settings.base_url == DEFAULT_BASE_URL
    assert settings.model == DEFAULT_MODEL
    assert settings.temperature == 0.0


@pytest.mark.parametrize("raw", ["short", "sk-1234567890abcdef", "sk-abcdefghijkl"])
def test_mask_key_hides_middle_part(raw):
    masked = mask_key(raw)

    if len(raw) <= 8:
        assert masked == "*" * len(raw)
    else:
        assert masked == f"{raw[:4]}{'*' * (len(raw) - 8)}{raw[-4:]}"
    assert raw not in masked


def test_mask_key_empty():
    assert mask_key("") == "<empty>"


def test_masked_api_key_property():
    settings = Settings(api_key="sk-abcdefghijkl")
    assert settings.masked_api_key == "sk-a*******ijkl"
