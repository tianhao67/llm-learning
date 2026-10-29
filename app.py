"""Streamlit 应用：填写学习需求问卷，生成个性化学习建议。

本地运行：
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from llm_demo import ConfigError, LLMClient, Settings
from llm_demo.prompts import SURVEY_QUESTIONS, build_survey_prompt

SAMPLE_ANSWERS: dict[str, str] = {
    "city_job": "在南京读大三，信息安全专业，目前没有实习经历。",
    "awareness": "会调用大模型 API，了解 Transformer 的基本结构，但没有训练过模型。",
    "goal": "希望找一份大模型应用开发的暑期实习。",
    "programming": "熟悉 Python，写过爬虫和 Django 小项目，会用 Git。",
    "time": "每天 2 小时左右，晚上 8 点到 10 点。",
    "extra": "想知道面试一般会问哪些内容。",
}


@st.cache_resource(show_spinner=False)
def load_settings() -> Settings:
    """整个会话只读取一次配置。"""
    return Settings.from_env()


def main() -> None:
    st.set_page_config(page_title="大模型学习需求调查", page_icon="📝", layout="centered")
    st.title("📝 大模型学习需求调查")
    st.caption("填写 6 个问题，模型会给出个性化的学习路径建议。这是一个学习示例，不是生产系统。")

    try:
        settings = load_settings()
    except ConfigError as exc:
        st.error(f"未配置 API Key：{exc}")
        st.info("复制 `.env.example` 为 `.env` 并填入 Key，然后重启应用。")
        st.stop()

    with st.sidebar:
        st.subheader("当前配置")
        st.write(f"**接口**：`{settings.base_url}`")
        st.write(f"**模型**：`{settings.model}`")
        st.write(f"**密钥**：`{settings.masked_api_key}`")
        temperature = st.slider("temperature（越低越稳定）", 0.0, 1.0, 0.0, 0.1)
        if st.button("填入示例数据", use_container_width=True):
            for question in SURVEY_QUESTIONS:
                st.session_state[question["key"]] = SAMPLE_ANSWERS[question["key"]]
            st.rerun()

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
            result = LLMClient(settings).chat(prompt, temperature=temperature)
    except Exception as exc:  # noqa: BLE001 - 界面需要展示任何调用错误
        st.error(f"调用失败：{exc}")
        return

    st.subheader("学习建议")
    st.markdown(result)


if __name__ == "__main__":
    main()
