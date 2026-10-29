"""通用小工具。"""

from __future__ import annotations

import json
import re
from typing import Any

_FENCED_JSON = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_json(text: str) -> Any:
    """从模型回复中提取 JSON。

    模型经常会把 JSON 包在 Markdown 代码块里，或者在 JSON 前后加一句解释，
    这里依次尝试：直接解析 → 取代码块内容 → 截取第一个 ``{`` / ``[`` 到最后一个
    ``}`` / ``]``。全部失败时抛出 :class:`ValueError`。

    >>> extract_json('```json\\n{"a": 1}\\n```')
    {'a': 1}
    """
    if not text or not text.strip():
        raise ValueError("模型返回内容为空，无法解析 JSON。")

    candidates = [text.strip()]

    fenced = _FENCED_JSON.search(text)
    if fenced:
        candidates.append(fenced.group(1).strip())

    for opener, closer in (("{", "}"), ("[", "]")):
        start, end = text.find(opener), text.rfind(closer)
        if start != -1 and end > start:
            candidates.append(text[start : end + 1])

    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    preview = text.strip()[:200]
    raise ValueError(f"模型返回的内容不是合法 JSON：{preview!r}")
