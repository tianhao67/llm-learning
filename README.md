# LLM Learning Lab

[![CI](https://github.com/tianhao67/llm-learning/actions/workflows/ci.yml/badge.svg)](https://github.com/tianhao67/llm-learning/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

一个面向初学者的 **LLM 应用实践**项目：用 OpenAI 兼容接口调用大模型，练习提示词模式与
RAG 检索增强，并用 Streamlit 实现「学习需求问卷」和「课程笔记问答」两个小应用。
项目自带一套可复现的评测脚本，用来回答一个工程问题：**改了提示词之后，效果是变好还是变差？**

> 说明：本项目是学习大模型基础课程时的练习整理，重点不是算法创新，而是把零散脚本
> 整理成**结构清晰、可测试、可评测、可复现**的小工程。阅读代码时请以学习参考为主，
> 它不追求生产可用。

---

## 功能

- **统一的模型客户端**：同一份代码通过 `OPENAI_BASE_URL` / `OPENAI_MODEL` 在
  DeepSeek、通义千问、OpenAI、Ollama 之间切换。
- **五种提示词模式**：文本分类、少样本示例、思维链、角色扮演、JSON 结构化输出。
- **RAG 检索问答**：文档切分 → TF-IDF 检索 → 带编号的资料 → 强制引用 → 越界引用校验；
  语料目录可替换成自己的资料。
- **提示词版本对比**：同一套问卷支持 v1 / v2 / v3 三版提示词，用评测数据说明差异。
- **离线可复现的评测**：三套评测集（38 条分类、12 条问卷、15 条 RAG），
  输出 Markdown 报告到 `evals/results/`。
- **Streamlit 双页签应用**：问卷建议 + 课程笔记问答，可展开查看完整 Prompt 和检索片段。
- **命令行工具**：`python -m llm_demo "你的问题"`，支持 `--json`、`--system` 等参数。
- **测试与 CI**：52 个离线单元测试 + GitHub Actions（ruff + pytest，Python 3.10 / 3.12）。
- **密钥安全**：`.env` 已忽略，仓库只保留 `.env.example`，日志与界面统一打码。

## 评测结果

最近一次运行（2026-10-29，模型 `deepseek-flash`，`temperature=0`），完整报告见
[`evals/results/`](evals/results/)。

### 情感分类（38 条）

| 样本数 | 准确率 | 宏平均 F1 | 无法识别 |
| --- | --- | --- | --- |
| 38 | 1.000 | 1.000 | 0 |

其中 8 条是「没有明显情感词」的难例，例如「用了三天，已经挂闲鱼了」「排队两小时，值了」，
用来观察模型是否只会认情感词。结果仍然全部答对——**这说明这套样本对该模型已经饱和**，
指标到顶不代表任务简单，而是数据集需要升级（反讽、混合情感、长文本）。这一点已经写进
Roadmap，也是后续要补的评测工作。

### 提示词版本对比（12 条问卷）

| 版本 | 内容 | 关键词覆盖率 | 分点格式率 | 平均字数 | 通过率 |
| --- | --- | --- | --- | --- | --- |
| v1 | 只有指令 | 0.361 | 0.500 | 670 | 0.167 |
| v2 | 指令 + 少样本 | 0.917 | 0.917 | 1874 | 0.000 |
| v3 | 指令 + 少样本 + 约束 | 0.833 | 1.000 | 523 | 0.833 |

**结论**：少样本把要点覆盖率从 0.361 拉到 0.917，但模型开始「话痨」，平均 1874 字，
全部超出长度要求；加上约束后压到 523 字、分点格式 100%，覆盖率只回落 0.08。
说明**约束不是免费的**——它用少量覆盖率换来了可读性和长度可控，而长度本身就是
问卷建议这种场景的硬需求。

### RAG（15 条，top-k=3）

| 语料 chunk 数 | recall@3 | 答案关键词覆盖率 | 引用合法率 |
| --- | --- | --- | --- |
| 20 | 1.000 | 0.956 | 1.000 |

**结论**：检索全部命中；生成的 15 条回答里引用编号全部合法（没有出现不存在的 `[n]`），
但仍有一条回答没有覆盖到期望术语，说明「检索到了」不等于「用上了」。
局限也很明显：语料只有 5 篇、20 个 chunk，recall@3 偏容易，换成语义检索后需要重测。

复现方式：

```bash
python evals/run_eval.py --task classify
python evals/run_eval.py --task survey --variants v1,v2,v3
python evals/run_eval.py --task rag --top-k 3 --generate
```

## RAG 是怎么做的

1. **切分**：按 240 字、48 字重叠切块，尽量在句号/换行处断开，避免把一句话截断；
2. **检索**：中文按「单字 + 双字」切 token，英文按单词切，TF-IDF + 余弦相似度排序。
   没有用向量库，是为了零依赖、可解释、能离线测试；`Retriever` 的接口保持不变，
   之后要换 embedding 只需要替换内部索引；
3. **生成**：把检索结果编号成 `[1] [2]`，要求模型只依据资料回答、每条结论标注编号、
   资料不足时直接说「资料中没有提到」；
4. **校验**：解析回答里的引用编号，越界的编号会标记出来并在界面上提示，
   这是防止模型「编引用」的低成本手段。

语料放在 `data/corpus/`，目前是 5 篇自己整理的课程笔记；换成自己的资料后重跑评测即可。

## 目录结构

```text
.
├── app.py                     # Streamlit 入口：问卷 + RAG 双页签
├── data/corpus/               # RAG 语料（5 篇课程笔记）
├── evals/
│   ├── cases/                 # 评测集：classify / survey / rag
│   ├── results/               # 评测报告（Markdown，随代码提交）
│   └── run_eval.py            # 评测入口
├── llm_demo/
│   ├── __init__.py
│   ├── __main__.py            # 命令行入口（python -m llm_demo）
│   ├── client.py              # OpenAI 兼容客户端封装（chat / chat_json）
│   ├── config.py              # 读取 .env，校验配置，密钥打码
│   ├── evaluation.py          # 离线评分：分类指标、关键词覆盖、格式检查
│   ├── prompts.py             # 问卷提示词（v1/v2/v3）+ 五种提示词模式
│   ├── rag.py                 # 切分、TF-IDF 检索、引用解析
│   └── utils.py               # 从模型输出中提取 JSON
├── examples/
│   ├── 01_hello_llm.py        # 最小调用
│   ├── 02_prompt_patterns.py  # 五种模式对比
│   └── 03_json_output.py      # 结构化输出与校验
├── tests/                     # 52 个离线单元测试（不联网、不需要真实 Key）
├── docs/
│   ├── evaluation.md          # 评测方法、指标定义、复现步骤
│   ├── deploy.md              # Streamlit Cloud / HF Spaces 部署
│   └── notes.md               # 学习笔记：接口原理、提示词技巧、报错排查
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

浏览器打开终端提示的地址（默认 <http://localhost:8501>），可以切换「学习需求问卷」和
「课程笔记问答」两个页签；侧边栏可调整 `temperature`、查看当前模型与打码后的 Key，
RAG 问答可以展开查看检索到的片段和相似度。

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

## 部署

`app.py` 可以直接部署到 Streamlit Community Cloud 或 Hugging Face Spaces，步骤和注意事项
见 [docs/deploy.md](docs/deploy.md)。密钥只填在平台的 Secrets 里，不要提交任何配置文件。

## 这个项目练到了什么

| 位置 | 涉及的知识点 |
| --- | --- |
| `llm_demo/config.py` | 环境变量管理、配置校验、敏感信息打码、dataclass |
| `llm_demo/client.py` | OpenAI 兼容接口、消息角色（system/user）、参数传递 |
| `llm_demo/prompts.py` | 提示词结构：指令 + 少样本 + 输入 + 约束；版本化对比 |
| `llm_demo/rag.py` | 文本切分、TF-IDF 检索、引用编号与校验 |
| `llm_demo/evaluation.py` | 分类指标（准确率/F1）、关键词覆盖、格式合规 |
| `evals/run_eval.py` | 评测集组织、批量调用、报告自动生成 |
| `app.py` | Streamlit 表单、`st.session_state`、`st.cache_resource`、`st.tabs` |
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
替身，RAG 用真实语料做检索断言，不会产生任何 API 调用费用。

## 安全说明

- 仓库中**不包含任何真实密钥**，`.env` 与 `.streamlit/secrets.toml` 均被 `.gitignore` 忽略。
- 程序打印配置时统一使用 `mask_key()` 打码。
- RAG 的提示词要求模型在资料不足时说「资料中没有提到」，并对引用编号做越界校验。
- 如果误提交了 Key，请立刻到平台控制台吊销并重新生成，同时清理 Git 历史
  （`git filter-repo` 或 GitHub 的 secret scanning 提示）。

## Roadmap

- [x] 统一客户端与配置管理
- [x] 五种提示词模式示例
- [x] Streamlit 问卷应用
- [x] 单元测试与 CI
- [x] RAG 检索问答（切分 + 检索 + 引用校验）
- [x] 提示词版本对比与评测脚本
- [ ] 部署到 Streamlit Community Cloud，并在 README 附上在线地址
- [ ] 把 TF-IDF 换成 embedding 检索，并重跑 recall@k
- [ ] 扩充分类评测集（反讽、混合情感），解决指标饱和问题
- [ ] 增加多轮对话（保留上下文）示例
- [ ] 支持流式输出（`stream=True`），改善交互体验
- [ ] 用 FastAPI 提供 `/chat`、`/rag/query` 接口

## 已知局限

- 只做单轮对话，没有记忆和上下文管理；
- RAG 语料只有 5 篇、20 个 chunk，recall@3 的参考价值有限；
- 检索是 TF-IDF，没有语义泛化能力，同义改写可能检索不到；
- 评测的关键词覆盖是粗粒度代理指标，不代表建议质量，需要人工抽查；
- 未处理并发、重试与请求限流，不适合直接用于生产。

## 许可证

本项目基于 [MIT License](LICENSE) 开源，欢迎参考与修改。
