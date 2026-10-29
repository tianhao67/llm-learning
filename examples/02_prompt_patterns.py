"""示例 2：五种常用提示词模式，对比不同写法对输出的影响。

运行：
    python examples/02_prompt_patterns.py                 # 依次跑全部模式
    python examples/02_prompt_patterns.py -p json_output   # 只跑某一种
    python examples/02_prompt_patterns.py -p classify --text "这家店服务太差了"
"""

from __future__ import annotations

import argparse
import sys

from llm_demo import ConfigError, LLMClient, Settings
from llm_demo.prompts import PROMPT_PATTERNS, render_pattern

#: 每种模式搭配的默认输入
DEFAULT_TEXT: dict[str, str] = {
    "classify": "这次假期玩得很开心，下次还想再来。",
    "few_shot": "15、32、5、13、82、7、1",
    "chain_of_thought": "我去市场买了 10 个苹果，给了邻居 2 个、修理工 2 个，"
    "然后吃了 1 个，又去买了 5 个。我还剩几个苹果？",
    "role_play": "熟悉 Python，用 Streamlit 做过一个问卷分析小应用，了解 OpenAI 兼容接口。",
    "json_output": "我叫田小满，在南京读书，会 Python 和 SQL，也写过一个 RAG demo。",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="运行提示词模式示例")
    parser.add_argument(
        "-p", "--pattern", choices=[*PROMPT_PATTERNS, "all"], default="all", help="要运行的模式"
    )
    parser.add_argument("--text", help="自定义输入文本；默认使用内置样例")
    args = parser.parse_args()

    try:
        settings = Settings.from_env()
    except ConfigError as exc:
        print(f"配置错误：{exc}", file=sys.stderr)
        return 1

    client = LLMClient(settings)
    names = list(PROMPT_PATTERNS) if args.pattern == "all" else [args.pattern]

    for name in names:
        text = args.text or DEFAULT_TEXT[name]
        prompt = render_pattern(name, text)
        print(f"\n{'=' * 60}\n模式：{name}\n{'=' * 60}")
        print(f"[提示词]\n{prompt}\n")
        print(f"[回答]\n{client.chat(prompt)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
