"""FastAPI 主程式：四支 API（對應架構說明書 2.3）＋健康檢查。"""
from datetime import date

from fastapi import FastAPI, HTTPException, Query

from . import config, llm, prompts, providers, vault
from .schemas import QueryAIRequest, SyncRequest, TriggerRequest

app = FastAPI(title="財經知識系統", version="0.1.0")


@app.get("/health")
def health():
    return {
        "ok": True,
        "vault_exists": bool(config.VAULT_PATH) and __import__("pathlib").Path(config.VAULT_PATH).exists(),
        "gemini_key_set": bool(config.GEMINI_API_KEY),
    }


@app.post("/api/v1/analysis/trigger")
def trigger(req: TriggerRequest):
    day = req.analysis_date or date.today().isoformat()
    try:
        data = providers.gather_all(day)
    except Exception as e:
        raise HTTPException(502, f"資料抓取失敗：{e}")
    if not data["rss"] and not any(v.get("last") for v in data["indices"].values()):
        raise HTTPException(502, "所有資料來源皆無回應，詳見後端日誌")
    try:
        macro = llm.generate(prompts.macro_prompt(data)) if req.source_scope in ("all", "macro") else ""
        flow = (
            llm.generate(prompts.flow_prompt(macro, data))
            if req.source_scope in ("all", "flow")
            else ""
        )
        stock = (
            llm.generate(prompts.stock_prompt(flow or macro, data), max_tokens=8192)
            if req.source_scope in ("all", "stocks")
            else ""
        )
    except llm.LLMError as e:
        raise HTTPException(502, str(e))
    macro, _ = vault.clean_section(macro)
    flow, _ = vault.clean_section(flow)
    stock, pool_truncated = vault.clean_section(stock)
    pool = vault.extract_pool(stock)
    md = (
        f"# {day} 財經三層級分析\n\n"
        f"標籤：#財經分析 #宏觀分析 #PortfolioPool\n\n"
        f"分析日期：{day}\n\n"
        f"## 一、宏觀層級\n\n{macro}\n\n"
        f"## 二、台股與產業層級\n\n{flow}\n\n"
        f"## 三、個股層級分析及潛力股\n\n{stock}\n"
    )
    try:
        fname = vault.write_report(day, md)
    except RuntimeError as e:
        raise HTTPException(500, str(e))
    return {
        "analysis_date": day,
        "report_file": fname,
        "pool_count": len(pool),
        "pool": pool,
        "pool_truncated": pool_truncated,
        "sources": {
            "rss": len(data["rss"]),
            "indices_ok": sum(1 for v in data["indices"].values() if v.get("last")),
            "screen": len(data["screen"]),
        },
    }


@app.post("/api/v1/mcp/obsidian/sync")
def sync(req: SyncRequest):
    try:
        fname = vault.write_raw(req.folder_path, req.filename, req.markdown_content)
    except RuntimeError as e:
        raise HTTPException(500, str(e))
    return {"ok": True, "file": fname}


@app.get("/api/v1/portfolio/pool")
def pool(
    filter_tag: str = Query(default="", description="關鍵字過濾"),
    min_confidence: float = Query(default=0.0, ge=0.0, le=1.0),
):
    try:
        items = vault.search_pool(tag=filter_tag, min_confidence=min_confidence)
    except RuntimeError as e:
        raise HTTPException(500, str(e))
    return {"count": len(items), "items": items}


@app.post("/api/v1/mcp/obsidian/query-ai")
def query_ai(req: QueryAIRequest):
    day_from, day_to = "", ""
    if "~" in req.date_range:
        day_from, day_to = [s.strip() for s in req.date_range.split("~", 1)]
    try:
        notes_meta = vault.list_notes(date_from=day_from, date_to=day_to)[: req.max_notes]
        notes = [
            {"name": n["name"], "content": vault.read_note(n["path"])} for n in notes_meta
        ]
    except RuntimeError as e:
        raise HTTPException(500, str(e))
    if not notes:
        raise HTTPException(404, "指定區間無歷史筆記")
    try:
        answer = llm.generate(prompts.rag_prompt(notes, req.query_prompt), max_tokens=2048)
    except llm.LLMError as e:
        raise HTTPException(502, str(e))
    return {"notes_used": [n["name"] for n in notes], "answer": answer}
