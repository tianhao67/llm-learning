"""命令行入口：``python -m llm_demo "你的问题"``。"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from .client import LLMClient
from .config import ConfigError, Settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="llm-demo",
        description="在终端里调用大模型（任何 OpenAI 兼容接口都可以）",
    )
    parser.add_argument("prompt", nargs="?", help="要问模型的问题；省略时从标准输入读取")
    parser.add_argument("-m", "--model", help="覆盖 .env 里的 OPENAI_MODEL")
    parser.add_argument("-t", "--temperature", type=float, help="采样温度，默认 0（最稳定）")
    parser.add_argument("--system", help="系统提示词，用来设定角色")
    parser.add_argument("--json", action="store_true", help="把模型输出当作 JSON 解析并美化打印")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    prompt = args.prompt or sys.stdin.read().strip()
    if not prompt:
        example = 'python -m llm_demo "用一句话解释什么是 RAG"'
        print(f"请输入要发送给模型的内容，例如：{example}", file=sys.stderr)
        return 2

    try:
        settings = Settings.from_env()
    except ConfigError as exc:
        print(f"配置错误：{exc}", file=sys.stderr)
        return 1

    client = LLMClient(settings)
    print(f"# model={args.model or settings.model} key={settings.masked_api_key}", file=sys.stderr)

    options = {
        "model": args.model,
        "temperature": args.temperature,
        "system": args.system,
    }
    try:
        if args.json:
            result = client.chat_json(prompt, **options)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(client.chat(prompt, **options))
    except Exception as exc:  # noqa: BLE001 - CLI 需要把任何 SDK 异常转成友好提示
        print(f"调用失败：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
