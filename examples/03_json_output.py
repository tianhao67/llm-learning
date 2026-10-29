"""示例 3：要求模型输出结构化 JSON，并在本地校验、排版、落盘。

运行：
    python examples/03_json_output.py
    python examples/03_json_output.py -o output/movies.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from llm_demo import ConfigError, LLMClient, Settings

MOVIE_PROMPT = """请生成 10 部经典电影的数据，评分使用 0-10 分制。
严格按以下 JSON 结构输出，不要输出任何解释文字：

{
  "movies": [
    {"title": "肖申克的救赎", "year": 1994, "rating": 9.7}
  ]
}
"""


def validate_movies(data: Any) -> list[dict[str, Any]]:
    """简单的结构校验：确保拿到的是电影列表，并补齐缺失字段。"""
    if not isinstance(data, dict) or not isinstance(data.get("movies"), list):
        raise ValueError("模型返回的 JSON 缺少 movies 数组。")
    movies = [item for item in data["movies"] if isinstance(item, dict)]
    if not movies:
        raise ValueError("movies 数组为空。")
    return movies


def print_table(movies: list[dict[str, Any]]) -> None:
    print(f"{'序号':<4}{'电影':<28}{'年份':>6}{'评分':>6}")
    print("-" * 46)
    for index, movie in enumerate(movies, start=1):
        title = str(movie.get("title", "未知"))[:24]
        year = str(movie.get("year", "-"))
        rating = str(movie.get("rating", "-"))
        print(f"{index:<4}{title:<28}{year:>6}{rating:>6}")


def main() -> int:
    parser = argparse.ArgumentParser(description="结构化输出示例")
    parser.add_argument("-o", "--output", type=Path, help="把结果保存为 JSON 文件")
    args = parser.parse_args()

    try:
        settings = Settings.from_env()
    except ConfigError as exc:
        print(f"配置错误：{exc}", file=sys.stderr)
        return 1

    client = LLMClient(settings)
    try:
        data = client.chat_json(MOVIE_PROMPT)
        movies = validate_movies(data)
    except ValueError as exc:
        print(f"解析失败：{exc}", file=sys.stderr)
        return 1

    print_table(movies)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n已保存到 {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
