# news-aggregator（專案藍圖）

> 本檔為跨 Agent 通用的專案藍圖（AGENTS.md 開放標準）。任何 Agent 的每個 session 都應先讀本檔＋`handoff.md`。

## 專案簡介
Node.js + Express 新聞聚合服務：依關鍵字＋日期區間（start/end）聚合經濟日報（money.udn.com）、工商時報（ctee.com.tw）、Yahoo 奇摩（tw.news.yahoo.com）、CMoney 的新聞，支援 JSON 查詢與 CSV 匯出。

## 關鍵時程
<!-- 目前無指定時程 -->

## 目標與路線圖
- [ ] 階段一：驗證各來源搜尋 selector 可用性，修復失效的解析（server.js 內有 NOTE 提醒版面異動需更新）
- [ ] 階段二：前端 public/ 搜尋＋日期篩選＋CSV 下載體驗完善
- [ ] 階段三：錯誤處理、日誌、部署（PORT 環境變數已支援）

## 資料夾結構
```
news-aggregator/
├── AGENTS.md
├── handoff.md
├── .gitignore
├── package.json          # name: news-aggregator，依賴 express/axios/cheerio/cors/csv-stringify/dayjs
├── package-lock.json
├── server.js            # Express 主程式：/api/search、/api/export.csv，四個來源爬蟲＋日期過濾＋去重＋排序
├── public/
│   ├── index.html
│   └── app.js
└── node_modules/
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
