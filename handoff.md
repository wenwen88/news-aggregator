# 交接檔（handoff.md）

> 任何 Agent、任何電腦接手前**必讀**；收工時**必更新**。本檔只放交接必需的精簡資訊，詳細脈絡放 Obsidian（若有 L3）。

## ⏯️ 目前做到哪
舊架構已捨棄：`server.js`、`public/` 已刪（commit 5f2b4ce），等待使用者提供新想法。舊程式可從 git 歷史找回（df09fed 以前）。

## 🚦 目前狀態
- 不可運行：後端與前端皆已清空，僅剩 `package.json`／`package-lock.json`（依賴清單）＋藍圖文件
- API 契約：舊 `/api/search`、`/api/export.csv` 已作廢，不需相容
- 診斷結論保留：HTML 爬蟲四來源全滅（見 Obsidian 踩坑筆記），新架構應避開此路線

## ➡️ 下一步
1. 等使用者提供新想法（已確認：RSS 主力或另提）
2. 依新想法重寫架構＋程式，更新 AGENTS.md 路線圖

## ⚠️ 注意事項
- 勿從舊爬蟲複製 selector（已證實全失效）
- 新架構決定前不要重裝依賴，`package.json` 到時一併重整

## 🕐 最後更新
- 時間：2026-10-02 08:00
- 更新者：OpenCode @ DESKTOP-UUJ9PN5
- Git push：✅ 已推（main → origin/main，5f2b4ce，含 handoff 待推）
