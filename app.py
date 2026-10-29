"""Streamlit 应用：学习需求问卷 + 课程笔记问答（RAG）。

本地运行：
    streamlit run app.py
"""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from llm_demo import ConfigError, LLMClient, Settings
from llm_demo.prompts import SURVEY_QUESTIONS, build_survey_prompt
from llm_demo.rag import Retriever, answer_question

ROOT = Path(__file__).resolve().parent
CORPUS_DIR = ROOT / "data" / "corpus"

#: 需要从 Streamlit Secrets 注入环境变量的配置项
SECRET_KEYS = ("OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL")

SAMPLE_ANSWERS: dict[str, str] = {
    "city_job": "在南京读大三，信息安全专业，目前没有实习经历。",
    "awareness": "会调用大模型 API，了解 Transformer 的基本结构，但没有训练过模型。",
    "goal": "希望找一份大模型应用开发的暑期实习。",
    "programming": "熟悉 Python，写过爬虫和 Django 小项目，会用 Git。",
    "time": "每天 2 小时左右，晚上 8 点到 10 点。",
    "extra": "想知道面试一般会问哪些内容。",
}


def apply_streamlit_secrets() -> None:
    """把 Streamlit Cloud 的 Secrets 注入环境变量。

    本地开发用 ``.env``；云端没有 ``.env`` 文件，配置放在 ``st.secrets`` 里。
    这里统一成环境变量，``Settings.from_env()`` 只需要维护一套读取逻辑。

    注意：没有 ``secrets.toml`` 时，``st.secrets`` 的取值会抛 ``FileNotFoundError``，
    所以整段都包在 try 里，本地运行时直接跳过即可。
    """
    try:
        secrets = st.secrets
        for key in SECRET_KEYS:
            if key in secrets and not os.environ.get(key):
                os.environ[key] = str(secrets[key])
    except Exception:  # noqa: BLE001 - 本地没有 secrets.toml 属于正常情况
        return


@st.cache_resource(show_spinner=False)
def load_settings() -> Settings:
    """整个会话只读取一次配置。"""
    apply_streamlit_secrets()
    return Settings.from_env()


@st.cache_resource(show_spinner=False)
def load_retriever() -> Retriever:
    """课程笔记的检索索引，构建一次后复用。"""
    return Retriever.from_directory(CORPUS_DIR)


@st.cache_resource(show_spinner=False)
def get_client(settings: Settings) -> LLMClient:
    """缓存客户端，避免每次交互都新建连接。"""
    return LLMClient(settings)


def chunk_preview(text: str) -> str:
    """把检索片段转成适合展示的正文。

    语料是 Markdown，片段里可能带着 ``##`` 标题标记；直接渲染会变成大标题，
    这里去掉行首的 ``#``，并用 Markdown 硬换行保留段落和列表结构。
    """
    lines = [line.lstrip("#").strip() for line in text.splitlines()]
    return "  \n".join(line for line in lines if line)


def render_survey(client: LLMClient, temperature: float) -> None:
    st.markdown("填写 6 个问题，模型会给出个性化的学习路径建议。可展开查看完整提示词，方便调试。")

    with st.form("survey_form"):
        answers: dict[str, str] = {}
        for question in SURVEY_QUESTIONS:
            answers[question["key"]] = st.text_area(
                question["label"],
                key=question["key"],
                placeholder=question["placeholder"],
                height=80,
            )
        submitted = st.form_submit_button("生成学习建议", type="primary", use_container_width=True)

    if not submitted:
        return
    if not any(value.strip() for value in answers.values()):
        st.warning("请至少填写一个问题。")
        return

    prompt = build_survey_prompt(answers)
    with st.expander("查看发送给模型的完整提示词"):
        st.code(prompt, language="text")

    try:
        with st.spinner("正在请求大模型，请稍候……"):
            result = client.chat(prompt, temperature=temperature)
    except Exception as exc:  # noqa: BLE001 - 界面需要展示任何调用错误
        st.error(f"调用失败：{exc}")
        return

    st.subheader("学习建议")
    st.markdown(result)


def render_rag(client: LLMClient, temperature: float) -> None:
    st.markdown(
        "先从 `data/corpus` 的课程笔记里检索相关片段，再让模型**只依据检索结果**回答，"
        "并要求标注引用。可以展开看检索到了哪些内容。"
    )

    question = st.text_input(
        "输入问题",
        placeholder="例如：chunk 大小一般怎么选？块之间要重叠多少？",
        key="rag_question",
    )
    top_k = st.slider("检索片段数 top-k", min_value=1, max_value=5, value=3)
    asked = st.button("提问", type="primary", key="rag_ask")

    if not asked:
        return
    if not question.strip():
        st.warning("请输入问题。")
        return

    try:
        with st.spinner("正在检索并生成回答……"):
            result = answer_question(
                client, question, load_retriever(), top_k=top_k, temperature=temperature
            )
    except Exception as exc:  # noqa: BLE001 - 界面需要展示任何调用错误
        st.error(f"调用失败：{exc}")
        return

    st.subheader("回答")
    st.markdown(result.answer)
    if result.invalid_citations:
        st.warning(f"模型给出了不存在的引用编号：{list(result.invalid_citations)}")

    with st.expander(f"检索到的资料（top-{len(result.hits)}）"):
        for number, hit in enumerate(result.hits, start=1):
            st.markdown(f"**[{number}] {hit.chunk.title}** · 相似度（TF-IDF）{hit.score:.3f}")
            st.markdown(chunk_preview(hit.chunk.text))


def main() -> None:
    st.set_page_config(page_title="LLM Learning Lab", page_icon="🧪", layout="centered")
    st.title("🧪 LLM Learning Lab")
    st.caption("一个用于练习大模型应用开发的小项目：提示词、RAG、评测。学习示例，不是生产系统。")

    try:
        settings = load_settings()
    except ConfigError as exc:
        st.error(f"未配置 API Key：{exc}")
        st.info(
            "**本地运行**：把 `.env.example` 复制为 `.env` 并填入 Key；"
            "**Streamlit Cloud**：在 App 右下角 Manage app → Settings → Secrets "
            "里配置 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL`，保存后 Reboot。"
        )
        st.stop()

    with st.sidebar:
        st.subheader("当前配置")
        st.write(f"**接口**：`{settings.base_url}`")
        st.write(f"**模型**：`{settings.model}`")
        st.write(f"**密钥**：`{settings.masked_api_key}`")
        temperature = st.slider("temperature（越低越稳定）", 0.0, 1.0, 0.0, 0.1)
        if st.button("问卷填入示例数据", use_container_width=True):
            for question in SURVEY_QUESTIONS:
                st.session_state[question["key"]] = SAMPLE_ANSWERS[question["key"]]
            st.rerun()

    client = get_client(settings)
    survey_tab, rag_tab = st.tabs(["📝 学习需求问卷", "📚 课程笔记问答（RAG）"])
    with survey_tab:
        render_survey(client, temperature)
    with rag_tab:
        render_rag(client, temperature)


if __name__ == "__main__":
    main()
