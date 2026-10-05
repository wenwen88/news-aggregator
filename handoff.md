# 交接檔（handoff.md）

> 任何 Agent、任何電腦接手前**必讀**；收工時**必更新**。本檔只放交接必需的精簡資訊，詳細脈絡放 Obsidian（若有 L3）。

## ⏯️ 目前做到哪
skill 方向啟動完成並已推（35d41f0）：trigger 多存 `*_data.json`、新建 report-page skill、
首版一頁式網頁（`page/`）已產出並驗證可載入。新 prompt（無標籤推薦原則）已實跑驗證通過
（2026-10-06 報告，pool 6 檔）。測試服務（8000／8080）已停。

## 🚦 目前狀態
- 可運行：`python -m uvicorn backend.app.main:app --port 8000`；靜態頁：`page/`（發佈目錄）
- trigger 回傳多 `data_file`；skill 在 `~/.config/opencode/skills/report-page/`（全域，不在 repo）
- 已知缺口：CNN 貪婪指數 418 被擋（VIX 代理）、TWSE 三大法人 JSON 端點未定；同日報告覆寫無版本保留

## ➡️ 下一步
1. Netlify 連 wenwen88/news-aggregator，發佈目錄設 `page`（首次需手動連，之後 push 自動部署）
2. 之後：排程每日自動分析、PostgreSQL、健康檢查告警

## ⚠️ 注意事項
- `.env`（Gemini key＋Vault 路徑）只放本機，絕不 commit（已在 .gitignore）
- Gemini 免費額度今日被連打多次觸發 429，已加退避重試；單日多次 trigger 仍可能撞牆，驗證跑一次就好
- 勿在 trigger 後用舊程式碼的 server（port 8000 殘留行程曾導致舊碼執行，已清；重啟前先確認 port 淨空）

## 🕐 最後更新
- 時間：2026-10-03 08:30
- 更新者：OpenCode @ DESKTOP-UUJ9PN5
- Git push：✅ 已推（db34fa3，含 handoff 待推）
