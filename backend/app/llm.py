"""Gemini LLM 呼叫（REST generateContent，不需額外 SDK）。"""
import httpx

from . import config


class LLMError(RuntimeError):
    pass


def generate(prompt: str, temperature: float = 0.3, max_tokens: int = 4096) -> str:
    if not config.GEMINI_API_KEY:
        raise LLMError("GEMINI_API_KEY 未設定（請寫入 .env）")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{config.GEMINI_MODEL}:generateContent?key={config.GEMINI_API_KEY}"
    )
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
    }
    try:
        with httpx.Client(timeout=90) as client:
            r = client.post(url, json=body)
            r.raise_for_status()
            data = r.json()
    except httpx.HTTPError as e:
        raise LLMError(f"Gemini 呼叫失敗：{e}") from e
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as e:
        raise LLMError(f"Gemini 回傳格式異常：{str(data)[:300]}") from e
