"""LLM 入门实践包：封装 OpenAI 兼容接口调用与提示词模板。"""

from .client import LLMClient
from .config import ConfigError, Settings

__all__ = ["ConfigError", "LLMClient", "Settings"]
__version__ = "0.1.0"
