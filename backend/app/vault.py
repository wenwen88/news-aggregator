"""Obsidian Vault 直寫＋檢索（簡化直寫方案：後端直接寫 Markdown 檔）。"""
import json
import re
from datetime import date
from pathlib import Path

from . import config

POOL_RE = re.compile(r"```pool\s*\n(.*?)```", re.S)


def vault_dir(folder: str = "") -> Path:
    if not config.VAULT_PATH or not Path(config.VAULT_PATH).exists():
        raise RuntimeError(f"VAULT_PATH 不存在：{config.VAULT_PATH}（請檢查 .env）")
    d = Path(config.VAULT_PATH) / (folder or config.OBSIDIAN_FOLDER)
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_report(analysis_date: str, markdown: str) -> str:
    """寫入 Vault，回傳檔名。"""
    d = vault_dir()
    fname = f"{analysis_date}_財經分析.md"
    (d / fname).write_text(markdown, encoding="utf-8")
    return fname


def write_raw(folder: str, filename: str, markdown: str) -> str:
    d = vault_dir(folder)
    safe = "".join(c for c in filename if c not in '<>:"/\\|?*') or f"note_{date.today()}.md"
    if not safe.endswith(".md"):
        safe += ".md"
    (d / safe).write_text(markdown, encoding="utf-8")
    return safe


def list_notes(folder: str = "", date_from: str = "", date_to: str = "") -> list[dict]:
    """列出 Vault 內報告（檔名 YYYY-MM-DD 開頭），可按日期區間過濾。"""
    d = vault_dir(folder)
    notes = []
    for p in sorted(d.glob("*.md"), reverse=True):
        m = re.match(r"(\d{4}-\d{2}-\d{2})", p.name)
        day = m.group(1) if m else ""
        if date_from and day < date_from:
            continue
        if date_to and day > date_to:
            continue
        notes.append({"name": p.name, "date": day, "path": str(p)})
    return notes


def read_note(path: str, limit: int = 8000) -> str:
    return Path(path).read_text(encoding="utf-8")[:limit]


def extract_pool(markdown: str) -> list[dict]:
    """從報告取出 ```pool JSON 陣列，失敗回空。"""
    m = POOL_RE.search(markdown)
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def search_pool(tag: str = "", min_confidence: float = 0.0, files: int = 10) -> list[dict]:
    """彙整最近若干報告的 Pool，可按信心分數過濾。"""
    out = []
    for n in list_notes()[:files]:
        for item in extract_pool(read_note(n["path"])):
            try:
                conf = float(item.get("confidence", 0))
            except (ValueError, TypeError):
                conf = 0.0
            if conf < min_confidence:
                continue
            if tag and tag not in json.dumps(item, ensure_ascii=False):
                continue
            out.append({**item, "report": n["name"]})
    return out
