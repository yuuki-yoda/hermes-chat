# Hermes Chat

一个极简的本地 Web 聊天界面：FastAPI 后端直连 DeepSeek API，静态页面开箱即用。
当时是为了绕开各种客户端，给自家 AI 助手做一个「随手能聊」的网页入口。

## 特性

- 单文件后端 `server.py`（FastAPI + httpx），无数据库
- 按 `session_id` 把对话存成 `history/<session_id>.json`，刷新不丢
- 前端纯 HTML/CSS/JS，无构建步骤
- 支持 CORS，方便嵌到别的页面里

## 运行

```bash
pip install fastapi uvicorn httpx
export DEEPSEEK_API_KEY=sk-xxxx
export HERMES_CHAT_MODEL=deepseek-chat      # 可选，默认 deepseek-v4-pro
uvicorn server:app --host 127.0.0.1 --port 8088
```

打开 <http://127.0.0.1:8088/>。

## 环境变量

| 变量 | 说明 |
|---|---|
| `DEEPSEEK_API_KEY` | 必填 |
| `DEEPSEEK_API_URL` | 可选，默认 `https://api.deepseek.com/v1/chat/completions` |
| `HERMES_CHAT_MODEL` | 可选，默认 `deepseek-v4-pro` |

## 目录

```
server.py       后端
static/         前端页面
history/        对话记录（运行时生成，已 gitignore）
```

## License

MIT
