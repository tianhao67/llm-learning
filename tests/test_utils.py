"""JSON 提取与客户端消息组装测试，全部离线运行。"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from llm_demo.client import LLMClient
from llm_demo.config import Settings
from llm_demo.utils import extract_json


def test_extract_plain_json():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_fenced_json():
    text = '好的，结果如下：\n```json\n{"name": "小明", "skills": ["Python"]}\n```\n希望有帮助。'
    assert extract_json(text) == {"name": "小明", "skills": ["Python"]}


def test_extract_json_array_with_surrounding_text():
    assert extract_json("结果：[1, 2, 3] 以上。") == [1, 2, 3]


@pytest.mark.parametrize("bad", ["", "   ", "抱歉，我无法回答。"])
def test_extract_json_rejects_non_json(bad):
    with pytest.raises(ValueError):
        extract_json(bad)


class _FakeCompletions:
    """模拟 ``client.chat.completions``，记录请求参数并返回固定回复。"""

    def __init__(self) -> None:
        self.kwargs: dict = {}

    def create(self, **kwargs):
        self.kwargs = kwargs
        message = SimpleNamespace(content="  你好，世界  ")
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class _FakeOpenAI:
    def __init__(self) -> None:
        self.chat = SimpleNamespace(completions=_FakeCompletions())


def test_chat_builds_messages_and_strips_output(monkeypatch):
    client = LLMClient(Settings(api_key="sk-test", model="demo-model"))
    fake = _FakeOpenAI()
    monkeypatch.setattr(client, "_client", fake)

    result = client.chat("你好", system="你是助手", temperature=0.3)

    assert result == "你好，世界"
    sent = fake.chat.completions.kwargs
    assert sent["model"] == "demo-model"
    assert sent["temperature"] == 0.3
    assert sent["messages"] == [
        {"role": "system", "content": "你是助手"},
        {"role": "user", "content": "你好"},
    ]


def test_chat_uses_settings_temperature_by_default(monkeypatch):
    client = LLMClient(Settings(api_key="sk-test", temperature=0.0))
    fake = _FakeOpenAI()
    monkeypatch.setattr(client, "_client", fake)

    client.chat("你好")

    assert fake.chat.completions.kwargs["temperature"] == 0.0
    assert fake.chat.completions.kwargs["messages"] == [{"role": "user", "content": "你好"}]
