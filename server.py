"""Hermes Web Chat - Direct DeepSeek API"""
import json, uuid, os, httpx
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

HISTORY_DIR = Path(__file__).parent / "history"
HISTORY_DIR.mkdir(exist_ok=True)

API_KEY = os.environ.get("DEEPSEEK_API_KEY")
API_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
MODEL = os.environ.get("HERMES_CHAT_MODEL", "deepseek-v4-pro")

class ChatRequest(BaseModel):
    message: str
    session_id: str = ""

class ChatResponse(BaseModel):
    reply: str
    session_id: str

@app.post("/api/hermes-chat")
def chat(req: ChatRequest):
    if not API_KEY:
        raise HTTPException(500, "DEEPSEEK_API_KEY is not configured")
    if not req.message.strip():
        raise HTTPException(400, "message required")
    sid = req.session_id or str(uuid.uuid4())[:8]
    try:
        resp = httpx.post(API_URL, json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You are Hermes Agent, an AI assistant by Nous Research. Be helpful and direct. Respond in the same language as the user. Never pretend to be someone else."},
                {"role": "user", "content": req.message}
            ],
            "temperature": 0.7,
            "max_tokens": int(os.environ.get("HERMES_CHAT_MAX_TOKENS", "4096")),
        }, headers={"Authorization": f"Bearer {API_KEY}"}, timeout=60)
        if resp.status_code >= 400:
            raise HTTPException(resp.status_code, f"upstream error: {resp.text[:500]}")
        data = resp.json()
        message = data["choices"][0].get("message", {})
        reply = (message.get("content") or "").strip()
        if not reply:
            raise HTTPException(502, f"model {MODEL} returned empty content; try again or increase max_tokens")
        (HISTORY_DIR / f"{sid}.json").write_text(
            json.dumps({"session_id": sid, "message": req.message, "reply": reply}, ensure_ascii=False, indent=2))
        return ChatResponse(reply=reply, session_id=sid)
    except httpx.TimeoutException:
        return ChatResponse(reply="(请求超时，请重试)", session_id=sid)
    except Exception as e:
        raise HTTPException(500, str(e))

app.mount("/", StaticFiles(directory=str(Path(__file__).parent / "static"), html=True), name="static")
