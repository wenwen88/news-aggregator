"""三層級 Prompt 鏈（對應架構說明書 2.2）：宏觀 → 資金流 → 個股＋Pool。"""
import json


def _fmt_indices(indices: dict) -> str:
    lines = []
    for name, v in indices.items():
        lines.append(f"- {name}：最新 {v['last']}，前收 {v['prev']}，漲跌 {v['chg_pct']}%")
    return "\n".join(lines)


def _fmt_rss(rss: list[dict]) -> str:
    return "\n".join(f"- {n['title']}（{n['pubDate']}）：{n['desc']}" for n in rss)


def macro_prompt(data: dict) -> str:
    return f"""你是財經總體分析師。根據以下今日市場數據，輸出「宏觀層級」摘要（300-500 字繁體中文，條列重點）。
分析日期：{data['analysis_date']}

【美股與情緒指標】
{_fmt_indices(data['indices'])}

【相關新聞標題】
{_fmt_rss(data['rss'][:12])}

要求：
1. 評估全球總體經濟與市場情緒（美股、美債殖利率、VIX）。
2. 點出對台股的傳導路徑（外部環境偏多/偏空及其理由）。
3. 用 Markdown 條列，不要寒暄。"""


def flow_prompt(macro_summary: str, data: dict) -> str:
    mi = "\n".join(
        f"- {r['指數']}：{r['收盤']}（{r['漲跌點數']}，{r['漲跌幅']}%）" for r in data["mi_index"]
    )
    fund = json.dumps(data["fund"], ensure_ascii=False)[:1500]
    return f"""你是台股資金流向分析師。延續以下宏觀結論，輸出「台股與產業層級」摘要（300-500 字繁體中文）。

【宏觀結論】
{macro_summary}

【台股數據】
加權指數：{data['indices'].get('加權指數')}
各類指數異動：
{mi}

【三大法人】
{fund}

【相關新聞標題】
{_fmt_rss(data['rss'][12:25])}

要求：
1. 分析三大法人資金流向與主流族群（半導體/AI/傳產/金融）。
2. 指出量能與結構是否健康。
3. 用 Markdown 條列，不要寒暄。"""


def stock_prompt(flow_summary: str, data: dict) -> str:
    scr = "\n".join(
        f"- {s['code']} {s['name']}：收盤 {s['close']}，乖離月線 {s['bias_pct']}%，PE {s['pe']}，PB {s['pb']}，殖利率 {s['yield']}%"
        for s in data["screen"]
    )
    return f"""你是個股基本面＋技術面分析師。延續以下資金流結論，輸出「個股層級」分析與 Portfolio Pool。

【資金流結論】
{flow_summary}

【乖離篩選候選（收盤 vs 月均）】
{scr}

【相關新聞標題】
{_fmt_rss(data['rss'][:25])}

要求：
1. 挑 3-8 檔潛在利多個股，以「1. 代碼 名稱」編號條列，直接從第 1 檔開始，不寫盤面解析前言。
2. 每檔 2-4 句，理由必須直接引用前述分析內容作為依據（資金流結論的族群/籌碼觀點、乖離數據、新聞標題中的具體事件），並附信心分數（0-1）。
3. 不要寫任何標題（含 ##、### 與次標題）、不要寫開場白（如「好的，作為…分析師」「以下為…摘要」）。
4. 文末必須附一個 fenced 程式碼區塊，語言標記為 pool，內容為 JSON 陣列，格式：
```pool
[{{"code": "2330", "name": "台積電", "confidence": 0.85, "reason": "…"}}]
```
5. 前面分析用繁體中文 Markdown，JSON 務必合法。"""


def rag_prompt(notes: list[dict], query: str) -> str:
    ctx = "\n\n".join(f"--- 筆記：{n['name']} ---\n{n['content'][:4000]}" for n in notes)
    return f"""你是投資策略檢討助手。根據以下歷史分析筆記，回答使用者的跨期對比問題（繁體中文，條列結論＋數據依據；若資料不足就明說）。

【歷史筆記】
{ctx}

【使用者問題】
{query}"""
