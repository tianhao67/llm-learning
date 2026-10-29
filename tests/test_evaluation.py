"""离线评分函数的测试。"""

from __future__ import annotations

import pytest

from llm_demo.evaluation import (
    classification_metrics,
    has_bullet_points,
    keyword_coverage,
    length_ok,
    normalize_label,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("正面", "正面"),
        (" 正面。", "正面"),
        ("Positive", "正面"),
        ("负面", "负面"),
        ("neutral", "中性"),
        ("我无法判断", ""),
        ("", ""),
    ],
)
def test_normalize_label(raw, expected):
    assert normalize_label(raw) == expected


def test_keyword_coverage():
    text = "建议先学 Python，再做一个项目。"
    assert keyword_coverage(text, ["Python", "项目"]) == 1.0
    assert keyword_coverage(text, ["Python", "实习"]) == 0.5
    assert keyword_coverage(text, []) == 1.0


def test_length_ok():
    assert length_ok("x" * 100)
    assert not length_ok("短")
    assert not length_ok("x" * 1000)


def test_has_bullet_points():
    assert has_bullet_points("- 第一条\n- 第二条")
    assert has_bullet_points("1. 第一条\n2. 第二条")
    assert not has_bullet_points("只有一段普通的话。")


def test_classification_metrics_perfect():
    metrics = classification_metrics(["正面", "负面", "中性"], ["正面", "负面", "中性"])

    assert metrics.accuracy == 1.0
    assert metrics.macro_f1 == 1.0
    assert metrics.invalid == 0


def test_classification_metrics_counts_invalid_predictions():
    metrics = classification_metrics(["正面", "负面"], ["正面", ""])

    assert metrics.accuracy == 0.5
    assert metrics.invalid == 1
    assert metrics.per_label["负面"]["f1"] == 0.0


def test_classification_metrics_rejects_length_mismatch():
    with pytest.raises(ValueError):
        classification_metrics(["正面"], ["正面", "负面"])
