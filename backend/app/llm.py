"""Gemini LLM 呼叫（REST generateContent，不需額外 SDK）。"""
import time

import httpx

from . import config


class LLMError(RuntimeError):
    pass


def generate(
    prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 4096,
    retries: int = 3,
) -> str:
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
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with httpx.Client(timeout=120) as client:
                r = client.post(url, json=body)
                r.raise_for_status()
                data = r.json()
            break
        except httpx.HTTPStatusError as e:
            last_err = e
            if e.response.status_code == 429 and attempt < retries:
                time.sleep(60 * (attempt + 1))  # 免費額度每分鐘重置，逐次加長等待
                continue
            raise LLMError(f"Gemini 呼叫失敗：{e}") from e
        except httpx.HTTPError as e:
            raise LLMError(f"Gemini 呼叫失敗：{e}") from e
    else:
        raise LLMError(f"Gemini 呼叫失敗（已重試 {retries} 次）：{last_err}")
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as e:
        raise LLMError(f"Gemini 回傳格式異常：{str(data)[:300]}") from e
