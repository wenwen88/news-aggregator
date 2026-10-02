"""資料抓取 providers：只用已驗證可用的端點，失敗回空值不中斷全流程。"""
import xml.etree.ElementTree as ET

import httpx

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NewsKB/1.0"}
TWSE = "https://openapi.twse.com.tw/v1/exchangeReport"
YAHOO_RSS = "https://tw.stock.yahoo.com/rss?category=tw-market"
CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=5d"
SYMBOLS = {
    "^TWII": "加權指數",
    "^GSPC": "S&P500",
    "^DJI": "道瓊",
    "^IXIC": "NASDAQ",
    "^SOX": "費半",
    "^TNX": "美10年債殖利率",
    "^VIX": "VIX",
}


def _get_json(client: httpx.Client, url: str):
    try:
        r = client.get(url, timeout=25)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def fetch_yahoo_rss(client: httpx.Client, limit: int = 30) -> list[dict]:
    """Yahoo 台股 RSS（已驗證）：title/link/pubDate/description。"""
    try:
        r = client.get(YAHOO_RSS, timeout=25)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        items = []
        for it in root.iter("item"):
            t = lambda tag: (it.findtext(tag) or "").strip()  # noqa: E731
            items.append({
                "title": t("title"),
                "link": t("link"),
                "pubDate": t("pubDate"),
                "desc": t("description")[:200],
            })
            if len(items) >= limit:
                break
        return items
    except Exception:
        return []


def fetch_indices(client: httpx.Client) -> dict:
    """美股＋台股指數近 5 日收盤與漲跌（Yahoo chart，已驗證）。"""
    out = {}
    for sym, name in SYMBOLS.items():
        try:
            r = client.get(CHART.format(sym=sym), timeout=25)
            r.raise_for_status()
            res = (r.json().get("chart", {}).get("result") or [{}])[0]
            meta = res.get("meta", {})
            closes = ((res.get("indicators", {}).get("quote") or [{}])[0].get("close")) or []
            closes = [c for c in closes if c]
            prev = meta.get("chartPreviousClose") or (closes[-2] if len(closes) > 1 else None)
            last = meta.get("regularMarketPrice") or (closes[-1] if closes else None)
            chg = round((last - prev) / prev * 100, 2) if last and prev else None
            out[name] = {"last": last, "prev": prev, "chg_pct": chg}
        except Exception:
            out[name] = {"last": None, "prev": None, "chg_pct": None}
    return out


def fetch_twse_fund(client: httpx.Client, date_yyyymmdd: str) -> dict | None:
    """三大法人買賣超（證交所網站 JSON，未保證，先試，失敗回 None）。"""
    url = f"https://www.twse.com.tw/rwd/zh/fund/TWT38U?response=json&date={date_yyyymmdd}"
    data = _get_json(client, url)
    if isinstance(data, dict) and data.get("stat") == "OK":
        return {"fields": data.get("fields"), "data": (data.get("data") or [])[:10]}
    return None


def fetch_mi_index(client: httpx.Client, top: int = 12) -> list[dict]:
    """各類指數收盤（已驗證），取漲跌幅最大的幾列。"""
    data = _get_json(client, f"{TWSE}/MI_INDEX")
    if not isinstance(data, list):
        return []
    rows = []
    for d in data:
        try:
            rows.append({
                "指數": d.get("指數"),
                "收盤": d.get("收盤指數"),
                "漲跌點數": d.get("漲跌點數"),
                "漲跌幅": float(str(d.get("漲跌百分比") or 0)),
            })
        except (ValueError, TypeError):
            continue
    rows.sort(key=lambda x: abs(x["漲跌幅"]), reverse=True)
    return rows[:top]


def screen_stocks(client: httpx.Client, top: int = 15) -> list[dict]:
    """個股篩選：收盤 vs 月均乖離（BWIBBU_d＋STOCK_DAY_AVG_ALL，均已驗證）。"""
    base = _get_json(client, f"{TWSE}/BWIBBU_d")
    avg = _get_json(client, f"{TWSE}/STOCK_DAY_AVG_ALL")
    if not isinstance(base, list) or not isinstance(avg, list):
        return []
    amap = {d.get("Code"): d for d in avg if isinstance(d, dict)}
    out = []
    for d in base:
        a = amap.get(d.get("Code"))
        if not a:
            continue
        try:
            close = float(str(a.get("ClosingPrice") or 0).replace(",", ""))
            ma = float(str(a.get("MonthlyAveragePrice") or 0).replace(",", ""))
            if not ma:
                continue
            out.append({
                "code": d.get("Code"),
                "name": d.get("Name"),
                "close": close,
                "bias_pct": round((close - ma) / ma * 100, 2),
                "pe": d.get("PEratio"),
                "pb": d.get("PBratio"),
                "yield": d.get("DividendYield"),
            })
        except (ValueError, TypeError):
            continue
    out.sort(key=lambda x: x["bias_pct"], reverse=True)
    return out[:top]


def gather_all(analysis_date: str) -> dict:
    """一次抓齊，任一來源失敗不影響其他。"""
    ymd = analysis_date.replace("-", "")
    with httpx.Client(headers=UA, follow_redirects=True) as client:
        fund = fetch_twse_fund(client, ymd)
        if fund is None:  # 非交易日或改版時退回前一天格式檢查由呼叫端決定
            fund = {"note": "三大法人當日檔缺（可能非交易日或端點異動），請以新聞內法人報導為準"}
        return {
            "analysis_date": analysis_date,
            "rss": fetch_yahoo_rss(client),
            "indices": fetch_indices(client),
            "fund": fund,
            "mi_index": fetch_mi_index(client),
            "screen": screen_stocks(client),
        }
