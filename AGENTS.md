# news-aggregator（專案藍圖）

> 本檔為跨 Agent 通用的專案藍圖（AGENTS.md 開放標準）。任何 Agent 的每個 session 都應先讀本檔＋`handoff.md`。

## 專案簡介
財經新聞多面向重點摘要與 Obsidian 知識庫整合分析系統（架構說明書：`財經知識系統.docx`）。
Python FastAPI 後端：手動發起即時分析，三層級 Prompt 鏈（宏觀經濟 → 台股資金流 → 個股＋Portfolio Pool，
Gemini `gemini-2.5-flash`），報告直寫 Obsidian Vault（`財經分析/`），歷史筆記可做 RAG 二次對比。
資料來源（只用已驗證端點）：Yahoo 台股 RSS、證交所 OpenAPI（BWIBBU／MI_INDEX／AVG）、Yahoo Finance 行情、
證交所三大法人 JSON（有就用、沒有就退回新聞法人報導）。CNN 貪婪指數被擋（418），暫以 VIX 代理。

## 關鍵時程
- 架構說明書建議 21 個工作天；首期以後端 MVP 為範圍（已完成），Vue 3 前端為第二刀

## 目標與路線圖
- [x] 後端 MVP：FastAPI 四支 API（trigger／obsidian/sync／portfolio/pool／query-ai）＋三層級分析＋Vault 直寫（2026-10-02 首跑成功，pool 4 檔）
- [ ] 第二刀：Vue 3 響應式前端（觸發分析、瀏覽報告＋Pool、歷史 RAG 問答）
- [ ] 第三刀：PostgreSQL（日誌／設定／快取）、排程每日自動分析、健康檢查告警

## 資料夾結構
```
news-aggregator/
├── AGENTS.md
├── handoff.md
├── .gitignore            # 含 .env（Gemini key＋Vault 路徑只放本機）
├── .env                  # 本機專用，不進 repo
├── 財經知識系統.docx      # 架構說明書原文
├── backend/
│   ├── requirements.txt  # fastapi／uvicorn／httpx
│   └── app/
│       ├── main.py       # 四支 API＋/health
│       ├── config.py     # .env 讀取
│       ├── schemas.py    # Trigger／Sync／QueryAI 模型
│       ├── providers.py  # Yahoo RSS／TWSE／Yahoo行情
│       ├── prompts.py    # 三層級 Prompt 鏈＋RAG
│       ├── llm.py        # Gemini REST
│       └── vault.py      # Vault 直寫＋Pool 解析
└── G:\我的雲端硬碟\2ndBrain\財經分析\   # 報告輸出地（Vault 外，不進 repo）
    └── YYYY-MM-DD_財經分析.md
```

## 同步層級（本專案初始化至第 3 層級）

| 層級 | 平台 | 位置 | 讀取時機 |
|------|------|------|---------|
| L1 | 本地（雲端硬碟資料夾） | `AGENTS.md`＋`handoff.md` | 每個 session |
| L2 | GitHub | wenwen88/news-aggregator（私有） | 指定時 |
| L3 | Obsidian | news-aggregator/專案工作流程.md | 有需要時 |

## 工作約定
- 任何 Agent、任何電腦：**開工先讀 `handoff.md`，收工必更新 `handoff.md`**
- 修改共用檔案前先讀最新內容，避免覆蓋其他 Agent 的變更
- 所有回應與文件使用繁體中文
- 修改前先確認計畫，優先保留原有資料結構

## 安全與隱私（不可違反）
- **不把 API key、密碼、憑證寫進 repo**，也不要貼進 `AGENTS.md`／`handoff.md`；一律放 `.env` 並列入 `.gitignore`
- **學生資料只用座號**，不出現姓名、學號、班級以外的個資、照片或聯絡方式
- 要公開分享前，先確認檔案裡沒有上述兩類內容
