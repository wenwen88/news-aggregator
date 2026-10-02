# 交接檔（handoff.md）

> 任何 Agent、任何電腦接手前**必讀**；收工時**必更新**。本檔只放交接必需的精簡資訊，詳細脈絡放 Obsidian（若有 L3）。

## ⏯️ 目前做到哪
專案初始化完成。Express 新聞聚合服務骨架已存在（server.js＋public/），尚未驗證四來源 selector 是否有效。

## 🚦 目前狀態
- 可運行：`npm start` 啟動於 PORT 3000（`node server.js`），`/api/search?q=&start=&end=`、`/api/export.csv`
- 待驗證：Yahoo／UDN／CTEE／CMoney 搜尋 selector 可能因版面異動失效
- 依賴已安裝：node_modules 存在

## ➡️ 下一步
1. 跑 `npm start` 並打一次 `/api/search?q=台股&start=2026-09-01&end=2026-10-02` 驗證各來源回傳
2. 修失效的 selector，補錯誤處理與日誌

## ⚠️ 注意事項
- `/api/export.csv` 內部打 `http://localhost:${PORT}/api/search`，部署時若 PORT 不同要注意
- 爬蟲記得帶 User-Agent，勿高頻打來源站

## 🕐 最後更新
- 時間：2026-10-02 08:00
- 更新者：OpenCode @ DESKTOP-UUJ9PN5
- Git push：—（初始化中，待推 L2）
