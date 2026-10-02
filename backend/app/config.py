"""環境設定：讀取專案根目錄 .env（只放本機，不進 repo）。"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # D:\news-aggregator


def _load_env(path: Path | None = None) -> None:
    p = Path(path) if path else ROOT / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


_load_env()

GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
VAULT_PATH: Path = Path(os.environ.get("VAULT_PATH", ""))
OBSIDIAN_FOLDER: str = os.environ.get("OBSIDIAN_FOLDER", "財經分析")
PORT: int = int(os.environ.get("PORT", "8000"))
