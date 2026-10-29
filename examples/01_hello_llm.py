"""示例 1：最小可用的模型调用。

运行（先执行 ``pip install -e .``）：
    python examples/01_hello_llm.py
"""

from __future__ import annotations

import sys

from llm_demo import ConfigError, LLMClient, Settings


def main() -> int:
    try:
        settings = Settings.from_env()
    except ConfigError as exc:
        print(f"配置错误：{exc}", file=sys.stderr)
        return 1

    client = LLMClient(settings)
    print(f"[模型] {settings.model}")
    print(f"[接口] {settings.base_url}")
    print(f"[密钥] {settings.masked_api_key}")

    question = "用一句话解释什么是大语言模型（LLM），并举一个生活中的应用例子。"
    print(f"\n[提问] {question}\n")
    print("[回答]", client.chat(question))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
