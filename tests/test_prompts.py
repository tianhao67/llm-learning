"""提示词模板的测试：题目、空答案处理、模式渲染。"""

from __future__ import annotations

import pytest

from llm_demo.prompts import (
    PROMPT_PATTERNS,
    SURVEY_QUESTIONS,
    build_survey_prompt,
    render_pattern,
)


def test_all_questions_appear_in_prompt():
    answers = {question["key"]: "测试回答" for question in SURVEY_QUESTIONS}

    prompt = build_survey_prompt(answers)

    assert len(SURVEY_QUESTIONS) == 6
    for question in SURVEY_QUESTIONS:
        assert question["label"] in prompt
    assert prompt.count("测试回答") == 6
    assert "限制：" in prompt


def test_blank_answers_are_rendered_as_placeholder():
    answers = {question["key"]: "   " for question in SURVEY_QUESTIONS}

    prompt = build_survey_prompt(answers)

    assert "未填写" in prompt
    assert prompt.count("未填写") == len(SURVEY_QUESTIONS)


def test_prompt_contains_instruction_and_examples():
    prompt = build_survey_prompt({})
    assert "大模型辅导老师" in prompt
    assert "示例1" in prompt
    assert "示例2" in prompt


@pytest.mark.parametrize("name", sorted(PROMPT_PATTERNS))
def test_render_pattern_replaces_text(name):
    prompt = render_pattern(name, "一段示例文本")
    assert "一段示例文本" in prompt
    assert "{text}" not in prompt


def test_unknown_pattern_raises():
    with pytest.raises(KeyError, match="未知的提示词模式"):
        render_pattern("not-exist", "x")
