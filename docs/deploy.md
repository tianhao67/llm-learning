# 部署说明

静态展示和接口调用都可以白嫖免费额度，下面是两条最常见的路径。

## 方案一：Streamlit Community Cloud（推荐）

适合把 Streamlit 应用直接变成可访问的链接，附在简历或 README 上。

1. 用 GitHub 账号登录 <https://share.streamlit.io/>；
2. 选择 **New app**，仓库选 `llm-learning`，主文件填 `app.py`；
3. 在 **Advanced settings → Secrets** 里填：

   ```toml
   OPENAI_API_KEY = "sk-..."
   OPENAI_BASE_URL = "https://api.deepseek.com"
   OPENAI_MODEL = "deepseek-chat"
   ```

4. 点击 Deploy，等一两分钟即可拿到 `https://<app-name>.streamlit.io` 地址。

注意事项：

- 仓库根目录的 `requirements.txt` 是给云端安装依赖用的，本地开发仍以 `pyproject.toml`
  为准（`pip install -e ".[dev]"`），两边依赖要保持一致；
- **密钥只填在 Secrets 里**，不要写进代码或 `.env` 后提交；
- 免费实例会休眠，第一次打开可能较慢，这是正常现象；
- 如果部署失败，先看构建日志里的依赖错误，再本地执行 `pip install -r requirements.txt`
  复现。

## 方案二：Hugging Face Spaces

1. 新建一个 **Streamlit** Space；
2. 把仓库文件复制进去（或在 Space 里直接 clone 本仓库）；
3. 在 **Settings → Variables and secrets** 添加同名的三个变量；
4. Space 会自动重启并给出访问地址。

适合想顺便展示在 Hugging Face 社区的场景，国内访问速度一般。

## 本地验证部署配置

部署前先在本地用「只读环境变量」的方式跑一遍，确认不依赖 `.env` 文件：

```bash
# PowerShell
$env:OPENAI_API_KEY="sk-..."
$env:OPENAI_BASE_URL="https://api.deepseek.com"
$env:OPENAI_MODEL="deepseek-chat"
streamlit run app.py
```

## 上线前检查清单

- [ ] `git ls-files | findstr /i ".env"` 只看到 `.env.example`；
- [ ] 仓库里搜索不到 `sk-` 开头的真实 Key；
- [ ] README 顶部的在线地址、截图已经补上；
- [ ] 关闭调试输出，错误信息不回显完整异常栈给用户；
- [ ] 在手机浏览器上打开一次，确认布局没有崩。

## 成本控制

- 免费额度通常够演示用，但公开链接可能被人刷，建议在平台侧设置预算提醒；
- 应用里已经限制 `max_tokens`，并在侧边栏暴露 `temperature`，不要开放任意长度的输入；
- 如果要长期公开，考虑加一个简单的访问口令或改用本地 Ollama。

## 以后要接后端时

当前项目是纯 Streamlit。需要对接到自己的网站或小程序时，可以：

1. 用 FastAPI 包一层 `POST /chat` 和 `POST /rag/query`；
2. 用 `uvicorn` 启动，Dockerfile 基于 `python:3.12-slim`；
3. 把模型调用放到服务端，前端只传问题和会话 id。

这部分还没有实现，属于 Roadmap 里的内容。
