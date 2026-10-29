"""RAG 模块测试：切分、检索、引用解析、提示词构造，全部离线。"""

from __future__ import annotations

from pathlib import Path

import pytest

from llm_demo.rag import (
    Retriever,
    answer_question,
    build_rag_prompt,
    chunk_text,
    load_documents,
    parse_citations,
    tokenize,
)

CORPUS_DIR = Path(__file__).resolve().parent.parent / "data" / "corpus"


def test_tokenize_keeps_chinese_bigrams_and_english_words():
    tokens = tokenize("RAG 检索增强")
    assert "rag" in tokens
    assert "检索" in tokens
    assert "索增" in tokens


def test_chunk_text_respects_size_and_overlap():
    text = "这是第一句话。这是第二句话。这是第三句话。" * 10

    chunks = chunk_text(text, size=60, overlap=15)

    assert len(chunks) > 1
    assert all(len(chunk) <= 60 for chunk in chunks)
    assert chunks[0].startswith("这是第一句话")


def test_chunk_text_rejects_bad_arguments():
    with pytest.raises(ValueError):
        chunk_text("内容", size=0)
    with pytest.raises(ValueError):
        chunk_text("内容", size=10, overlap=10)


def test_chunk_text_returns_empty_for_blank_input():
    assert chunk_text("   ") == []


def test_load_documents_reads_titles():
    documents = load_documents(CORPUS_DIR)

    assert len(documents) >= 5
    titles = {document.title for document in documents}
    assert "大模型基础" in titles


def test_retriever_finds_expected_document():
    retriever = Retriever.from_directory(CORPUS_DIR)

    hits = retriever.search("chunk 大小一般怎么选？块之间要重叠多少？", top_k=3)

    assert hits
    assert hits[0].chunk.doc_id == "03-RAG检索增强"


def test_retriever_scores_are_sorted_desc():
    retriever = Retriever.from_directory(CORPUS_DIR)

    hits = retriever.search("上下文窗口是什么？超出会怎样？", top_k=3)

    scores = [hit.score for hit in hits]
    assert scores == sorted(scores, reverse=True)
    assert hits[0].chunk.doc_id == "01-大模型基础"


def test_parse_citations_handles_duplicates_and_out_of_range():
    text = "结论一[1]，结论二[2]，再引用一次[1]，越界[9]。"

    citations, invalid = parse_citations(text, max_index=3)

    assert citations == [1, 2]
    assert invalid == [9]


def test_build_rag_prompt_contains_numbered_sources():
    retriever = Retriever.from_directory(CORPUS_DIR)
    hits = retriever.search("什么是幻觉", top_k=2)

    prompt = build_rag_prompt("什么是幻觉？", hits)

    assert "[1]" in prompt
    assert "什么是幻觉？" in prompt
    assert "资料中没有提到" in prompt


def test_build_rag_prompt_requires_hits():
    with pytest.raises(ValueError):
        build_rag_prompt("问题", [])


class _FakeClient:
    """只实现 chat 的假客户端，避免测试联网。"""

    def __init__(self, reply: str) -> None:
        self.reply = reply
        self.prompts: list[str] = []

    def chat(self, prompt: str, **kwargs) -> str:
        self.prompts.append(prompt)
        return self.reply


def test_answer_question_returns_citations():
    retriever = Retriever.from_directory(CORPUS_DIR)
    client = _FakeClient("幻觉是模型编造事实[1]，可以通过引用资料缓解[2]。")

    result = answer_question(client, "什么是幻觉？", retriever, top_k=2)

    assert result.citations == (1, 2)
    assert result.invalid_citations == ()
    assert len(result.hits) == 2
    assert client.prompts


def test_answer_question_marks_invalid_citation():
    retriever = Retriever.from_directory(CORPUS_DIR)
    client = _FakeClient("这是一个不存在的引用[9]。")

    result = answer_question(client, "什么是幻觉？", retriever, top_k=2)

    assert result.citations == ()
    assert result.invalid_citations == (9,)
