"""离线评分工具：不调用模型，保证评测可复现、可单元测试。

模型输出的打分方式尽量选「确定性规则」（标签匹配、关键词覆盖、格式检查），
这样同一份回答每次得分相同；需要主观判断的部分，交给人工抽查或另写 judge。
"""

from __future__ import annotations

from dataclasses import dataclass

LABELS = ("正面", "中性", "负面")

_LABEL_SYNONYMS: dict[str, set[str]] = {
    "正面": {"正面", "positive", "积极", "好评"},
    "中性": {"中性", "neutral", "中立"},
    "负面": {"负面", "negative", "消极", "差评"},
}


def normalize_label(raw: str) -> str:
    """把模型输出归一化成三种标签，识别失败时返回空字符串。"""
    text = (raw or "").strip().lower().strip("。.!！:：")
    for label, words in _LABEL_SYNONYMS.items():
        if any(word in text for word in words):
            return label
    return ""


def keyword_coverage(text: str, keywords: list[str]) -> float:
    """回答覆盖了多少个期望关键词，返回 0~1 的比例。"""
    if not keywords:
        return 1.0
    lowered = (text or "").lower()
    hits = sum(1 for keyword in keywords if keyword.lower() in lowered)
    return hits / len(keywords)


def length_ok(text: str, min_chars: int = 60, max_chars: int = 800) -> bool:
    """回答长度是否在合理区间内。"""
    return min_chars <= len(text or "") <= max_chars


def has_bullet_points(text: str) -> bool:
    """是否使用了分点格式（以 ``-``、``*`` 或数字编号开头的行）。"""
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    return sum(
        1
        for line in lines
        if line.startswith(("-", "*", "•")) or (line[0].isdigit() and line[1:3] in {". ", "、 "})
    ) >= 2


@dataclass(frozen=True)
class ClassificationMetrics:
    """分类任务的常用指标。"""

    n: int
    accuracy: float
    macro_f1: float
    per_label: dict[str, dict[str, float]]
    invalid: int

    def as_row(self) -> str:
        return (
            f"{self.n} | {self.accuracy:.3f} | {self.macro_f1:.3f} | "
            f"{self.invalid} | {self.per_label['正面']['f1']:.3f} | "
            f"{self.per_label['中性']['f1']:.3f} | {self.per_label['负面']['f1']:.3f}"
        )


def classification_metrics(golds: list[str], preds: list[str]) -> ClassificationMetrics:
    """计算准确率与宏平均 F1。

    无法识别的预测（``normalize_label`` 返回空串）计为错误，并单独统计数量。
    """
    if len(golds) != len(preds):
        raise ValueError("golds 与 preds 长度不一致")

    pairs = list(zip(golds, preds, strict=True))
    per_label: dict[str, dict[str, float]] = {}
    f1_scores: list[float] = []
    for label in LABELS:
        true_positive = sum(1 for gold, pred in pairs if gold == label and pred == label)
        false_positive = sum(1 for gold, pred in pairs if gold != label and pred == label)
        false_negative = sum(1 for gold, pred in pairs if gold == label and pred != label)
        precision = true_positive / (true_positive + false_positive) if true_positive else 0.0
        recall = true_positive / (true_positive + false_negative) if true_positive else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_label[label] = {"precision": precision, "recall": recall, "f1": f1}
        f1_scores.append(f1)

    total = len(pairs) or 1
    accuracy = sum(1 for gold, pred in pairs if gold == pred) / total
    return ClassificationMetrics(
        n=len(golds),
        accuracy=accuracy,
        macro_f1=sum(f1_scores) / len(f1_scores),
        per_label=per_label,
        invalid=sum(1 for pred in preds if pred not in LABELS),
    )
