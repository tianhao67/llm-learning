"""极简 RAG：文档切分、TF-IDF 检索、带引用的回答生成。

设计取舍
--------
- 不引入向量数据库：TF-IDF 零依赖、结果可解释、能完全离线跑测试；
- 中文按「单字 + 双字」切分，英文/数字按单词切分，避免依赖分词库；
- 检索结果结构与 embedding 方案保持一致，之后要换成向量检索时只需要替换
  :class:`Retriever` 内部的索引，上层代码不用改。

如果想换成 embedding 检索，实现同样的 ``search(query, top_k)`` 接口即可。
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .client import LLMClient

_CJK_RUN = re.compile(r"[\u4e00-\u9fff]+")
_WORD = re.compile(r"[a-z0-9]+")
_SENTENCE_ENDS = "。！？!?；;\n"
_CITATION = re.compile(r"[\[【](\d+)[\]】]")

RAG_SYSTEM = (
    "你是一个严谨的知识库问答助手。你只能依据用户提供的资料回答问题，"
    "不能使用资料以外的知识，也不能编造事实。"
)


@dataclass(frozen=True)
class Document:
    """一篇原始文档。"""

    doc_id: str
    title: str
    text: str
    source: str

    @classmethod
    def from_file(cls, path: Path) -> Document:
        text = path.read_text(encoding="utf-8").strip()
        title = next(
            (line.lstrip("# ").strip() for line in text.splitlines() if line.startswith("# ")),
            path.stem,
        )
        return cls(doc_id=path.stem, title=title, text=text, source=path.name)


@dataclass(frozen=True)
class Chunk:
    """切分后的一段文本。"""

    chunk_id: str
    doc_id: str
    title: str
    text: str
    source: str
    position: int


@dataclass(frozen=True)
class SearchHit:
    """一条检索结果。"""

    chunk: Chunk
    score: float


@dataclass(frozen=True)
class RAGAnswer:
    """一次 RAG 问答的结果，保留检索片段和引用信息便于排查。"""

    answer: str
    hits: tuple[SearchHit, ...]
    citations: tuple[int, ...]
    invalid_citations: tuple[int, ...]


def tokenize(text: str) -> list[str]:
    """把文本切成检索用的 token。

    中文同时保留单字和双字（bi-gram），既照顾单字查询，也能匹配「切分」「检索」
    这类两字词；英文和数字统一小写后按单词切分。
    """
    tokens: list[str] = []
    for run in _CJK_RUN.findall(text):
        tokens.extend(run)
        tokens.extend(run[index : index + 2] for index in range(len(run) - 1))
    tokens.extend(_WORD.findall(text.lower()))
    return tokens


def chunk_text(text: str, size: int = 240, overlap: int = 48) -> list[str]:
    """按字符长度切分文本，并尽量在句子边界处断开。

    Args:
        text: 原始文本。
        size: 每块最多包含的字符数。
        overlap: 相邻块之间重叠的字符数，用于避免语义被截断。

    Raises:
        ValueError: ``size`` 非正数，或 ``overlap`` 不在 ``[0, size)`` 区间内。
    """
    text = (text or "").strip()
    if size <= 0:
        raise ValueError("size 必须是正整数")
    if not 0 <= overlap < size:
        raise ValueError("overlap 必须满足 0 <= overlap < size")
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            cut = max(text.rfind(char, start, end) for char in _SENTENCE_ENDS)
            if cut > start + size // 2:
                end = cut + 1
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def load_documents(directory: Path) -> list[Document]:
    """读取目录下的所有 ``.md`` 文件，按文件名排序保证结果稳定。"""
    directory = Path(directory)
    if not directory.is_dir():
        raise FileNotFoundError(f"语料目录不存在：{directory}")
    documents = [Document.from_file(path) for path in sorted(directory.glob("*.md"))]
    if not documents:
        raise ValueError(f"语料目录中没有 .md 文件：{directory}")
    return documents


def build_chunks(
    documents: list[Document], size: int = 240, overlap: int = 48
) -> list[Chunk]:
    """把文档列表切分成带位置信息的 chunk。"""
    chunks: list[Chunk] = []
    for document in documents:
        for position, piece in enumerate(chunk_text(document.text, size, overlap)):
            chunks.append(
                Chunk(
                    chunk_id=f"{document.doc_id}-{position:03d}",
                    doc_id=document.doc_id,
                    title=document.title,
                    text=piece,
                    source=document.source,
                    position=position,
                )
            )
    return chunks


class TfidfIndex:
    """TF-IDF + 余弦相似度的内存索引。"""

    def __init__(self, chunks: list[Chunk]) -> None:
        if not chunks:
            raise ValueError("索引至少需要一个 chunk")
        self.chunks = list(chunks)

        tokenized = [tokenize(chunk.text) for chunk in self.chunks]
        document_frequency: Counter[str] = Counter()
        for tokens in tokenized:
            document_frequency.update(set(tokens))

        total = len(self.chunks)
        self._idf = {
            token: math.log((total + 1) / (frequency + 1)) + 1
            for token, frequency in document_frequency.items()
        }
        self._vectors = [self._vectorize(tokens) for tokens in tokenized]

    def _vectorize(self, tokens: list[str]) -> dict[str, float]:
        counts = Counter(tokens)
        vector = {
            token: (1 + math.log(count)) * self._idf[token]
            for token, count in counts.items()
            if token in self._idf
        }
        norm = math.sqrt(sum(value * value for value in vector.values())) or 1.0
        return {token: value / norm for token, value in vector.items()}

    def search(self, query: str, top_k: int = 3) -> list[SearchHit]:
        """返回与查询最相似的 ``top_k`` 个 chunk。"""
        if top_k <= 0:
            raise ValueError("top_k 必须是正整数")
        query_vector = self._vectorize(tokenize(query))
        if not query_vector:
            return []

        scored = [
            (sum(value * query_vector.get(token, 0.0) for token, value in vector.items()), chunk)
            for vector, chunk in zip(self._vectors, self.chunks, strict=True)
        ]
        scored.sort(key=lambda item: (-item[0], item[1].chunk_id))
        return [SearchHit(chunk=chunk, score=score) for score, chunk in scored[:top_k] if score > 0]


class Retriever:
    """把「语料目录 → 切分 → 索引 → 检索」串起来。"""

    def __init__(self, chunks: list[Chunk], index: TfidfIndex | None = None) -> None:
        self.chunks = list(chunks)
        self._index = index or TfidfIndex(self.chunks)

    @classmethod
    def from_directory(
        cls, directory: Path, size: int = 240, overlap: int = 48
    ) -> Retriever:
        return cls(build_chunks(load_documents(directory), size=size, overlap=overlap))

    def search(self, query: str, top_k: int = 3) -> list[SearchHit]:
        return self._index.search(query, top_k=top_k)


def format_context(hits: tuple[SearchHit, ...] | list[SearchHit]) -> str:
    """把检索结果格式化成带编号的资料块。"""
    blocks = []
    for number, hit in enumerate(hits, start=1):
        blocks.append(f"[{number}] 《{hit.chunk.title}》\n{hit.chunk.text}")
    return "\n\n".join(blocks)


def build_rag_prompt(question: str, hits: tuple[SearchHit, ...] | list[SearchHit]) -> str:
    """拼出「资料 + 问题 + 引用要求」的提示词。"""
    if not hits:
        raise ValueError("没有检索到任何资料，无法构造提示词")
    return (
        "请严格依据下面的资料回答问题。\n\n"
        f"资料：\n{format_context(hits)}\n\n"
        f"问题：{question}\n\n"
        "要求：\n"
        "- 只使用资料中的信息，不要使用资料以外的知识；\n"
        "- 每个结论后面用 [编号] 标注来源，例如 [1]；\n"
        "- 资料不足以回答时，直接回答「资料中没有提到」，不要编造；\n"
        "- 用简体中文回答，控制在 300 字以内。"
    )


def parse_citations(answer: str, max_index: int) -> tuple[list[int], list[int]]:
    """解析回答里的引用编号。

    Returns:
        ``(合法引用, 越界引用)``，均按首次出现顺序去重。
    """
    citations: list[int] = []
    invalid: list[int] = []
    for raw in _CITATION.findall(answer):
        number = int(raw)
        if not 1 <= number <= max_index:
            if number not in invalid:
                invalid.append(number)
        elif number not in citations:
            citations.append(number)
    return citations, invalid


def answer_question(
    client: LLMClient,
    question: str,
    retriever: Retriever,
    top_k: int = 3,
    temperature: float = 0.0,
) -> RAGAnswer:
    """检索 + 生成，返回带引用校验的结果。"""
    hits = tuple(retriever.search(question, top_k=top_k))
    if not hits:
        return RAGAnswer(answer="资料中没有提到。", hits=(), citations=(), invalid_citations=())

    answer = client.chat(
        build_rag_prompt(question, hits),
        system=RAG_SYSTEM,
        temperature=temperature,
    )
    citations, invalid = parse_citations(answer, max_index=len(hits))
    return RAGAnswer(
        answer=answer, hits=hits, citations=tuple(citations), invalid_citations=tuple(invalid)
    )
