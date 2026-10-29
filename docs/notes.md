# 学习笔记

这份笔记记录了做这个项目时真正弄明白的几个问题，方便以后回看，也方便面试时复述。

---

## 1. `openai` 是 SDK 的名字，不是模型的名字

`openai` 这个 Python 包最早是 OpenAI 官方写的客户端，它定义了一套请求/响应的格式，
后来被称为 **OpenAI 兼容接口规范**。DeepSeek、通义千问、硅基流动、Ollama 等平台
都实现了这套格式，所以：

```python
client = OpenAI(api_key=..., base_url="https://api.deepseek.com")
```

请求实际发给了 `base_url` 指向的平台，和 GPT 没有任何关系。换平台只需改
`base_url` 和 `model` 两个值，业务代码不用动 —— 这就是本项目把配置抽到
`.env` 的原因。

## 2. 三个环境变量

| 变量 | 作用 | 示例 |
| --- | --- | --- |
| `OPENAI_API_KEY` | 身份凭证 | `sk-...` |
| `OPENAI_BASE_URL` | 请求发往哪里 | `https://api.deepseek.com` |
| `OPENAI_MODEL` | 用哪个模型 | `deepseek-chat` |

密钥只放在 `.env`（已被 `.gitignore` 忽略），仓库里只保留 `.env.example`。

## 3. 提示词的四个要素

1. **角色**：让模型站在某个身份上回答，例如「你是一位有十年经验的技术面试官」。
2. **任务**：明确要做什么，动词尽量具体（分类、抽取、改写、评分）。
3. **示例**：给 1~3 组「输入 → 期望输出」，比长篇描述更能约束格式和风格（少样本）。
4. **约束**：长度、语言、输出格式、不允许做的事。

没有约束时，模型倾向于「多说一点」，这在做结构化输出时尤其致命。

## 4. 五种常用模式（对应 `examples/02_prompt_patterns.py`）

| 模式 | 适用场景 | 关键点 |
| --- | --- | --- |
| `classify` | 情感 / 意图 / 垃圾内容分类 | 只让模型输出类别词，减少废话 |
| `few_shot` | 格式固定、需要模仿风格 | 示例要覆盖边界情况 |
| `chain_of_thought` | 数学、逻辑、多步推理 | 「一步一步思考」+ 给出中间步骤 |
| `role_play` | 模拟面试、写作、评审 | 角色 + 评价标准一起给 |
| `json_output` | 下游要程序处理 | 给出 JSON 结构 + 本地校验 |

## 5. 结构化输出要自己校验

模型不保证返回合法 JSON，常见情况：

- 包在 ` ```json ... ``` ` 代码块里；
- 前后多一句「好的，以下是结果」；
- 字段名被改写、数组被写成字符串。

所以 `llm_demo/utils.py` 里做了三层兜底提取，`examples/03_json_output.py` 还会
检查 `movies` 数组是否存在。**永远不要直接把模型输出 `eval` 或当成可信数据。**

## 6. 参数怎么调

- `temperature=0`：输出最稳定，适合分类、抽取、需要复现的场景；
- `temperature=0.7~1.0`：适合头脑风暴、文案；
- `max_tokens`：限制回复长度，能省钱也能防止跑偏；
- `stream=True`：边生成边显示，改善交互体验（本项目暂未使用）。

## 7. 常见报错对照

| 报错 | 可能原因 | 处理 |
| --- | --- | --- |
| `AuthenticationError 401` | Key 错误、过期、或平台不匹配 | 检查 `.env` 里的 Key 与 `base_url` 是否属于同一平台 |
| `NotFoundError 404 model not found` | 模型名写错 / 该平台没有这个模型 | 用平台文档里的模型名，如 `deepseek-chat`、`qwen-turbo` |
| `RateLimitError 429` | 触发限流或余额不足 | 降低频率、检查账户余额 |
| `APITimeoutError` | 网络或代理问题 | 提高 `timeout`，检查代理设置 |
| 中文乱码 | Windows 终端编码不是 UTF-8 | 执行 `chcp 65001`，或使用 Windows Terminal |

## 8. 参考

- OpenAI 兼容接口文档：<https://platform.openai.com/docs/api-reference>
- DeepSeek API 文档：<https://api-docs.deepseek.com/>
- 阿里云百炼（通义千问）兼容模式：<https://help.aliyun.com/zh/model-studio/>
- Streamlit 文档：<https://docs.streamlit.io/>
