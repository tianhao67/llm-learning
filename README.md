# LLM Learning Lab

[![CI](https://github.com/tianhao67/llm-learning/actions/workflows/ci.yml/badge.svg)](https://github.com/tianhao67/llm-learning/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

一个面向初学者的 **LLM 应用实践**项目：用 OpenAI 兼容接口调用大模型，练习常见提示词模式，
并用 Streamlit 实现一个「学习需求问卷 → 个性化学习建议」的小应用。

> 说明：本项目是学习大模型基础课程时的练习整理，重点不是算法创新，而是把零散脚本
> 整理成**结构清晰、可测试、可复现**的小工程。阅读代码时请以学习参考为主，它不追求
> 生产可用。

---

## 功能

- **统一的模型客户端**：同一份代码通过 `OPENAI_BASE_URL` / `OPENAI_MODEL` 在
  DeepSeek、通义千问、OpenAI、Ollama 之间切换。
- **五种提示词模式**：文本分类、少样本示例、思维链、角色扮演、JSON 结构化输出。
- **结构化输出解析**：自动剥离 Markdown 代码块并做本地校验，不信任模型原始输出。
- **Streamlit 问卷应用**：填写 6 个问题，生成个性化学习建议，可查看完整 Prompt。
- **命令行工具**：`python -m llm_demo "你的问题"`，支持 `--json`、`--system` 等参数。
- **测试与 CI**：离线单元测试 + GitHub Actions（ruff + pytest，Python 3.10 / 3.12）。
- **密钥安全**：`.env` 已忽略，仓库只保留 `.env.example`，日志与界面统一打码。

## 目录结构

```text
.
├── app.py                     # Streamlit 问卷应用入口
├── llm_demo/
│   ├── __init__.py
│   ├── __main__.py            # 命令行入口（python -m llm_demo）
│   ├── client.py              # OpenAI 兼容客户端封装（chat / chat_json）
│   ├── config.py              # 读取 .env，校验配置，密钥打码
│   ├── prompts.py             # 问卷提示词 + 五种提示词模式
│   └── utils.py               # 从模型输出中提取 JSON
├── examples/
│   ├── 01_hello_llm.py        # 最小调用
│   ├── 02_prompt_patterns.py  # 五种模式对比
│   └── 03_json_output.py      # 结构化输出与校验
├── tests/                     # pytest 单元测试（不联网、不需要真实 Key）
├── docs/notes.md              # 学习笔记：接口原理、提示词技巧、报错排查
├── .github/workflows/ci.yml   # GitHub Actions
├── .env.example               # 环境变量模板
├── pyproject.toml             # 依赖、ruff、pytest 配置
└── LICENSE
```

## 快速开始

环境要求：Python 3.10+，可访问所选模型平台的网络。

```bash
# 1. 克隆项目
git clone https://github.com/tianhao67/llm-learning.git
cd llm-learning

# 2. 创建虚拟环境（Windows PowerShell）
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS / Linux
# python -m venv .venv && source .venv/bin/activate

# 3. 安装（-e 表示以可编辑模式安装本包）
pip install -e ".[dev]"

# 4. 配置密钥：复制模板并填入自己的值
copy .env.example .env        # macOS / Linux: cp .env.example .env

# 5. 跑第一个示例
python examples/01_hello_llm.py
```

### 运行示例

```bash
python examples/01_hello_llm.py                     # 最小调用
python examples/02_prompt_patterns.py               # 依次跑五种提示词模式
python examples/02_prompt_patterns.py -p json_output --text "我叫小明，在南京读书，会 Python"
python examples/03_json_output.py -o output/movies.json
```

### 运行 Web 应用

```bash
streamlit run app.py
```

浏览器打开终端提示的地址（默认 <http://localhost:8501>），填写问卷后点击「生成学习建议」，
侧边栏可以调整 `temperature`、查看当前模型与打码后的 Key。

### 命令行工具

```bash
python -m llm_demo "用一句话解释什么是 RAG"
python -m llm_demo "把下面这句话翻译成英文：今天天气很好"
python -m llm_demo --system "你是一个严谨的技术评审" "这段代码有什么问题：print(eval(input()))"
python -m llm_demo --json "用 JSON 返回：{'name': '小明', 'city': '南京'}"
```

## 配置项

| 变量 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | 是 | 无 | 平台签发的 API Key |
| `OPENAI_BASE_URL` | 否 | `https://api.deepseek.com` | OpenAI 兼容接口地址 |
| `OPENAI_MODEL` | 否 | `deepseek-chat` | 模型名称 |

修改 `.env` 后需要重新运行程序（Streamlit 需重启）。

## 支持的平台

| 平台 | `OPENAI_BASE_URL` | `OPENAI_MODEL` 示例 |
| --- | --- | --- |
| DeepSeek | `https://api.deepseek.com` | `deepseek-chat` |
| 阿里云百炼（通义千问） | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-turbo` / `qwen-plus` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| 本地 Ollama | `http://localhost:11434/v1` | `qwen2.5:7b` |

> 本地 Ollama 的 Key 可以随便填，但服务需要先 `ollama serve` 启动。

## 这个项目练到了什么

| 位置 | 涉及的知识点 |
| --- | --- |
| `llm_demo/config.py` | 环境变量管理、配置校验、敏感信息打码、dataclass |
| `llm_demo/client.py` | OpenAI 兼容接口、消息角色（system/user）、参数传递 |
| `llm_demo/prompts.py` | 提示词结构：指令 + 少样本 + 输入 + 约束 |
| `llm_demo/utils.py` | 模型输出的不确定性处理、JSON 提取与校验 |
| `app.py` | Streamlit 表单、`st.session_state`、`st.cache_resource`、错误提示 |
| `tests/` | pytest、monkeypatch、用假对象替身隔离网络调用 |
| `.github/workflows/ci.yml` | GitHub Actions 矩阵构建、依赖缓存、lint + test |

## 开发

```bash
pip install -e ".[dev]"

pytest -q          # 运行测试（不需要 API Key，不会联网）
ruff check .       # 代码检查
ruff format .      # 代码格式化
```

测试全部离线：配置读取用 `monkeypatch` 注入环境变量，客户端用假的 `chat.completions`
替身，不会产生任何 API 调用费用。

## 安全说明

- 仓库中**不包含任何真实密钥**，`.env` 与 `.streamlit/secrets.toml` 均被 `.gitignore` 忽略。
- 程序打印配置时统一使用 `mask_key()` 打码。
- 如果误提交了 Key，请立刻到平台控制台吊销并重新生成，同时清理 Git 历史
  （`git filter-repo` 或 GitHub 的 secret scanning 提示）。

## Roadmap

- [x] 统一客户端与配置管理
- [x] 五种提示词模式示例
- [x] Streamlit 问卷应用
- [x] 单元测试与 CI
- [ ] 增加多轮对话（保留上下文）示例
- [ ] 增加 RAG 小示例：用课程资料做检索问答
- [ ] 增加提示词版本对比与人工评分表（评测意识）
- [ ] 部署到 Streamlit Community Cloud，并在 README 附上在线地址
- [ ] 支持流式输出（`stream=True`），改善交互体验

## 已知局限

- 只做单轮对话，没有记忆和上下文管理；
- 提示词为固定模板，没有做 A/B 对比与量化评测；
- 未处理并发、重试与请求限流，不适合直接用于生产；
- 应用未做用户输入审核，仅作为学习演示。

## 许可证

本项目基于 [MIT License](LICENSE) 开源，欢迎参考与修改。
