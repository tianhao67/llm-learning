"""评测脚本：把「感觉还行」变成可复现的数字。

三种任务：

- ``classify``：情感分类准确率 / 宏平均 F1；
- ``survey``：对比 v1 / v2 / v3 三版提示词的关键词覆盖率、分点格式率和通过率；
- ``rag``：检索 recall@k，可选 ``--generate`` 同时检查引用是否合法。

示例::

    python evals/run_eval.py --task survey --variants v1,v2,v3
    python evals/run_eval.py --task classify
    python evals/run_eval.py --task rag --top-k 3 --generate

结果会打印到终端，并写入 ``evals/results/<task>.md``。脚本会产生真实的 API 调用费用，
先跑 ``--limit 5`` 试一下是个好习惯。
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from llm_demo import ConfigError, LLMClient, Settings
from llm_demo.evaluation import (
    classification_metrics,
    has_bullet_points,
    keyword_coverage,
    length_ok,
    normalize_label,
)
from llm_demo.prompts import build_survey_prompt, render_pattern
from llm_demo.rag import Retriever, answer_question

ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = ROOT / "evals" / "cases"
CORPUS_DIR = ROOT / "data" / "corpus"
RESULTS_DIR = ROOT / "evals" / "results"


def load_cases(name: str, limit: int = 0) -> list[dict]:
    """读取 jsonl 评测集，``limit`` 大于 0 时只取前若干条。"""
    path = CASES_DIR / f"{name}.jsonl"
    if not path.is_file():
        raise SystemExit(f"找不到评测集：{path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    cases = [json.loads(line) for line in lines if line.strip()]
    if not cases:
        raise SystemExit(f"评测集为空：{path}")
    return cases[:limit] if limit > 0 else cases


def run_classify(
    client: LLMClient, limit: int, temperature: float
) -> tuple[list[str], dict]:
    cases = load_cases("classify", limit)
    golds: list[str] = []
    predictions: list[str] = []
    details: list[dict] = []
    for case in cases:
        answer = client.chat(
            render_pattern("classify", case["text"]), temperature=temperature, max_tokens=512
        )
        prediction = normalize_label(answer)
        golds.append(case["label"])
        predictions.append(prediction)
        details.append(
            {
                "id": case["id"],
                "text": case["text"],
                "gold": case["label"],
                "raw": answer,
                "pred": prediction,
            }
        )
    return golds, {"details": details, "predictions": predictions}


def run_survey(
    client: LLMClient, variants: list[str], limit: int, temperature: float
) -> list[dict]:
    cases = load_cases("survey", limit)
    rows: list[dict] = []
    for variant in variants:
        coverages: list[float] = []
        format_hits = 0
        lengths: list[int] = []
        passed = 0
        for case in cases:
            answer = client.chat(
                build_survey_prompt(case["answers"], variant=variant),
                temperature=temperature,
                max_tokens=2000,
            )
            coverage = keyword_coverage(answer, case["must_include"])
            coverages.append(coverage)
            format_hits += int(has_bullet_points(answer))
            lengths.append(len(answer))
            if coverage >= 0.6 and length_ok(answer, min_chars=80, max_chars=900):
                passed += 1
        total = len(cases)
        rows.append(
            {
                "variant": variant,
                "coverage": sum(coverages) / total,
                "format_rate": format_hits / total,
                "avg_chars": sum(lengths) / total,
                "pass_rate": passed / total,
            }
        )
    return rows


def run_rag(
    client: LLMClient | None,
    top_k: int,
    generate: bool,
    limit: int,
    temperature: float,
) -> tuple[list[dict], dict]:
    retriever = Retriever.from_directory(CORPUS_DIR)
    cases = load_cases("rag", limit)
    details: list[dict] = []
    hit_count = 0
    term_scores: list[float] = []
    citation_ok = 0
    generated = 0

    for case in cases:
        hits = retriever.search(case["question"], top_k=top_k)
        hit_docs = [hit.chunk.doc_id for hit in hits]
        hit = case["expected_doc"] in hit_docs
        hit_count += int(hit)
        record = {
            "id": case["id"],
            "question": case["question"],
            "expected_doc": case["expected_doc"],
            "top_docs": hit_docs,
            "hit": hit,
        }
        if generate and hits and client is not None:
            result = answer_question(
                client, case["question"], retriever, top_k=top_k, temperature=temperature
            )
            generated += 1
            record["answer"] = result.answer
            record["citations"] = list(result.citations)
            record["invalid_citations"] = list(result.invalid_citations)
            term_scores.append(keyword_coverage(result.answer, case["expected_terms"]))
            if result.citations and not result.invalid_citations:
                citation_ok += 1
        details.append(record)

    summary = {
        "n": len(cases),
        "top_k": top_k,
        "recall": hit_count / len(cases),
        "generated": generated,
        "term_coverage": sum(term_scores) / len(term_scores) if term_scores else None,
        "citation_rate": citation_ok / generated if generated else None,
        "chunks": len(retriever.chunks),
    }
    return details, summary


def build_report(task: str, summary: dict, extra: dict) -> str:
    lines = [
        f"# 评测结果：{task}",
        "",
        f"- 时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"- 模型：`{extra['model']}`",
        f"- 接口：`{extra['base_url']}`",
        f"- 样本数：{summary.get('n', '-')}",
        f"- temperature：{extra['temperature']}",
        "",
    ]
    if task == "classify":
        metrics = summary["metrics"]
        lines += [
            "## 指标",
            "",
            "| 样本数 | 准确率 | 宏平均 F1 | 无法识别 | 正面 F1 | 中性 F1 | 负面 F1 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            f"| {metrics.n} | {metrics.accuracy:.3f} | {metrics.macro_f1:.3f} | "
            f"{metrics.invalid} | {metrics.per_label['正面']['f1']:.3f} | "
            f"{metrics.per_label['中性']['f1']:.3f} | {metrics.per_label['负面']['f1']:.3f} |",
            "",
            "## 错误样本",
            "",
        ]
        errors = [item for item in summary["details"] if item["gold"] != item["pred"]]
        if errors:
            lines += ["| id | 文本 | 标注 | 预测 | 原始输出 |", "| --- | --- | --- | --- | --- |"]
            for item in errors:
                raw = item["raw"].replace("\n", " ")[:40]
                lines.append(
                    f"| {item['id']} | {item['text']} | {item['gold']} | {item['pred']} | {raw} |"
                )
        else:
            lines.append("无。")
    elif task == "survey":
        lines += [
            "## 指标",
            "",
            "| 版本 | 关键词覆盖率 | 分点格式率 | 平均字数 | 通过率 |",
            "| --- | --- | --- | --- | --- |",
        ]
        for row in summary["rows"]:
            lines.append(
                f"| {row['variant']} | {row['coverage']:.3f} | {row['format_rate']:.3f} | "
                f"{row['avg_chars']:.0f} | {row['pass_rate']:.3f} |"
            )
    else:
        s = summary
        lines += [
            "## 指标",
            "",
            "| 指标 | 值 |",
            "| --- | --- |",
            f"| 语料 chunk 数 | {s['chunks']} |",
            f"| recall@{s['top_k']} | {s['recall']:.3f} |",
        ]
        if s["generated"]:
            lines.append(f"| 答案关键词覆盖率 | {s['term_coverage']:.3f} |")
            lines.append(f"| 引用合法率 | {s['citation_rate']:.3f} |")
        lines += ["", "## 逐题结果", "", "| id | 是否命中 | 检索到的文档 |", "| --- | --- | --- |"]
        for item in summary["details"]:
            docs = ", ".join(item["top_docs"]) or "-"
            lines.append(f"| {item['id']} | {'✅' if item['hit'] else '❌'} | {docs} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="运行项目评测")
    parser.add_argument("--task", choices=["classify", "survey", "rag"], required=True)
    parser.add_argument("--variants", default="v3", help="survey 任务要对比的版本，逗号分隔")
    parser.add_argument("--limit", type=int, default=0, help="每个任务只用前 N 条（0 表示全部）")
    parser.add_argument("--top-k", type=int, default=3, help="RAG 检索返回的 chunk 数")
    parser.add_argument("--generate", action="store_true", help="RAG 任务同时生成答案并校验引用")
    parser.add_argument("--model", default=None, help="覆盖 .env 里的模型名")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--no-save", action="store_true", help="只打印，不写 results 文件")
    args = parser.parse_args(argv)

    try:
        settings = Settings.from_env()
    except ConfigError as exc:
        print(f"配置错误：{exc}", file=sys.stderr)
        return 1

    client = LLMClient(settings)
    model = args.model or settings.model
    started = time.perf_counter()

    if args.task == "classify":
        golds, details = run_classify(client, args.limit, args.temperature)
        metrics = classification_metrics(golds, details["predictions"])
        summary = {"n": metrics.n, "metrics": metrics, "details": details["details"]}
    elif args.task == "survey":
        variants = [item.strip() for item in args.variants.split(",") if item.strip()]
        rows = run_survey(client, variants, args.limit, args.temperature)
        summary = {"n": len(load_cases("survey", args.limit)), "rows": rows}
    else:
        details, rag_summary = run_rag(
            client, args.top_k, args.generate, args.limit, args.temperature
        )
        summary = {**rag_summary, "details": details}

    elapsed = time.perf_counter() - started
    report = build_report(
        args.task,
        summary,
        {
            "model": model,
            "base_url": settings.base_url,
            "temperature": args.temperature,
        },
    )
    report += f"\n耗时：{elapsed:.1f} 秒\n"
    print(report)
    if not args.no_save:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        output = RESULTS_DIR / f"{args.task}.md"
        output.write_text(report, encoding="utf-8")
        print(f"已写入 {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
