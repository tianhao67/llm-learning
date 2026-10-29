"""配置管理：从 ``.env`` 或系统环境变量读取 API 配置。

项目统一使用 OpenAI 兼容接口的三件套环境变量：

- ``OPENAI_API_KEY``：平台签发的 API Key
- ``OPENAI_BASE_URL``：平台兼容接口的地址
- ``OPENAI_MODEL``：要调用的模型名称

这样同一份代码可以在 DeepSeek、通义千问、OpenAI、Ollama 等平台之间切换，
而不需要改动任何业务代码。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

#: 默认平台（DeepSeek），需要换平台时改 ``.env`` 即可
DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"

#: 仓库根目录下的 ``.env``
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class ConfigError(RuntimeError):
    """配置缺失或不合法时抛出，便于上层给出友好的提示。"""


def mask_key(key: str, keep: int = 4) -> str:
    """把 API Key 打码，用于日志和界面展示，避免密钥出现在截图或日志里。"""
    key = key or ""
    if not key:
        return "<empty>"
    if len(key) <= keep * 2:
        return "*" * len(key)
    return f"{key[:keep]}{'*' * (len(key) - keep * 2)}{key[-keep:]}"


@dataclass(frozen=True)
class Settings:
    """一次对话所需的全部配置。"""

    api_key: str
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    temperature: float = 0.0
    timeout: float = 60.0

    @classmethod
    def from_env(cls, env_file: Path | str | None = ENV_FILE) -> Settings:
        """从环境变量构造配置，找不到 Key 时抛出 :class:`ConfigError`。"""
        if env_file is not None and Path(env_file).is_file():
            # override=False：真实环境变量优先于 .env，方便 CI / 部署时注入
            load_dotenv(env_file, override=False)

        api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
        if not api_key:
            raise ConfigError(
                "未找到 OPENAI_API_KEY。请把 .env.example 复制为 .env，并填入你自己的 API Key。"
            )

        base_url = (os.getenv("OPENAI_BASE_URL") or DEFAULT_BASE_URL).strip().rstrip("/")
        model = (os.getenv("OPENAI_MODEL") or DEFAULT_MODEL).strip()
        return cls(api_key=api_key, base_url=base_url, model=model)

    @property
    def masked_api_key(self) -> str:
        """打码后的 Key，适合直接打印到终端或页面上。"""
        return mask_key(self.api_key)
