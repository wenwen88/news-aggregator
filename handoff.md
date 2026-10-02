# 交接檔（handoff.md）

> 任何 Agent、任何電腦接手前**必讀**；收工時**必更新**。本檔只放交接必需的精簡資訊，詳細脈絡放 Obsidian（若有 L3）。

## ⏯️ 目前做到哪
報告格式迭代＋強健性修補完成並已推（db34fa3）：去大標題／重複標題／開場白／次標題、第三節改名、
截斷防護、429 退避重試。Gemini key 已換新（AQ 開頭那把，.env 本機）。測試服務已停。

## 🚦 目前狀態
- 可運行：`python -m uvicorn backend.app.main:app --port 8000`，`/health` 正常
- 四支 API 皆實測通過（trigger／sync／pool／query-ai）；最新版 prompt（無標籤推薦原則）**尚未實跑驗證**（被 429 擋下）
- 已知缺口：CNN 貪婪指數 418 被擋（VIX 代理）、TWSE 三大法人 JSON 端點未定；同日報告覆寫無版本保留

## ➡️ 下一步
1. （優先）額度重置後跑一次 trigger，驗證無標籤推薦原則版報告＋pool 解析
2. 待定：是否做一頁式報告網頁（Obsidian＋圖表→Netlify，需 trigger 多存 data.json）／是否寫成 skill（免 key 但需手動觸發）
3. 之後：排程每日自動分析、PostgreSQL、健康檢查告警

## ⚠️ 注意事項
- `.env`（Gemini key＋Vault 路徑）只放本機，絕不 commit（已在 .gitignore）
- Gemini 免費額度今日被連打多次觸發 429，已加退避重試；單日多次 trigger 仍可能撞牆，驗證跑一次就好
- 勿在 trigger 後用舊程式碼的 server（port 8000 殘留行程曾導致舊碼執行，已清；重啟前先確認 port 淨空）

## 🕐 最後更新
- 時間：2026-10-03 08:30
- 更新者：OpenCode @ DESKTOP-UUJ9PN5
- Git push：✅ 已推（db34fa3，含 handoff 待推）
