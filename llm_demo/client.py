"""对 ``openai`` SDK 的轻量封装。

``openai`` 只是 SDK 的包名，它实现的是「OpenAI 兼容接口规范」。
DeepSeek、通义千问、硅基流动、Ollama 等平台都实现了这套规范，
因此只要把 ``base_url`` 指向对应平台，就能用同一份代码调用不同厂商的模型。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from openai import OpenAI

from .config import Settings
from .utils import extract_json


@dataclass
class LLMClient:
    """最小可用的 LLM 客户端：一次请求，返回文本或解析后的 JSON。"""

    settings: Settings
    _client: OpenAI = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._client = OpenAI(
            api_key=self.settings.api_key,
            base_url=self.settings.base_url,
            timeout=self.settings.timeout,
        )

    def chat(
        self,
        prompt: str,
        *,
        system: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """发送一条用户消息，返回模型回复的纯文本。

        Args:
            prompt: 用户输入（也可以是拼接好的完整提示词）。
            system: 可选的系统提示词，用来设定角色和约束。
            model: 覆盖 ``settings.model``。
            temperature: 覆盖 ``settings.temperature``，0 表示输出最稳定。
            max_tokens: 限制回复长度，``None`` 表示使用平台默认值。
        """
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(
            model=model or self.settings.model,
            messages=messages,
            temperature=self.settings.temperature if temperature is None else temperature,
            max_tokens=max_tokens,
        )
        return (response.choices[0].message.content or "").strip()

    def chat_json(self, prompt: str, **kwargs: Any) -> Any:
        """要求模型输出 JSON，并自动去掉 ```json 代码块等包装后解析。"""
        return extract_json(self.chat(prompt, **kwargs))
