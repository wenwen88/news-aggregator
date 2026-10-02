// server.js
const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const cors = require('cors');
const dayjs = require('dayjs');
const { stringify } = require('csv-stringify/sync');

const app = express();
app.use(cors());
app.use(express.static('public'));

const USER_AGENT = 'Mozilla/5.0 (compatible; NewsAggBot/1.0; +https://example.com)';

// --- helper: normalize date string to YYYY-MM-DD if possible
function normalizeDate(str) {
  if (!str) return null;
  str = str.replace(/[\n\t]/g, ' ').trim();
  // try parse common formats: "2025-11-27", "2025/11/27", "27 Nov 2025", "2025年11月27日"
  // Use dayjs with custom parsing attempts
  const attempts = [
    'YYYY-MM-DD','YYYY/MM/DD','YYYY.MM.DD','YYYY年MM月DD日',
    'DD MMM YYYY','MMM DD, YYYY','YYYY MM DD'
  ];
  for (const fmt of attempts) {
    const d = dayjs(str, fmt);
    if (d.isValid()) return d.format('YYYY-MM-DD');
  }
  // fallback: extract yyyy-mm-dd pattern
  const m = str.match(/(20\d{2})[\/\-.年]*(\d{1,2})[\/\-.月]*(\d{1,2})/);
  if (m) {
    return dayjs(`${m[1]}-${m[2]}-${m[3]}`).format('YYYY-MM-DD');
  }
  return null;
}

// --- Search functions for each source
// NOTE: selectors may need updates if site layout changes.

async function searchYahoo(query) {
  // Yahoo news search: https://tw.news.yahoo.com/search?p=...
  const url = `https://tw.news.yahoo.com/search?p=${encodeURIComponent(query)}`;
  const res = await axios.get(url, { headers: { 'User-Agent': USER_AGENT }});
  const $ = cheerio.load(res.data);
  const results = [];

  $('li div div a').each((i, el) => {
    const a = $(el);
    let href = a.attr('href');
    let title = a.text().trim();
    const parent = a.closest('li');
    if (!href || !title) return;
    // Yahoo link may be relative; ensure absolute
    if (href.startsWith('/')) href = 'https://tw.news.yahoo.com' + href;
    // find date in sibling
    const timeText = parent.find('time').text() || parent.find('.svelte-1s2z0sd time').text();
    const date = normalizeDate(timeText);
    results.push({ source: 'Yahoo', title, url: href, date, summary: '' });
  });
  return results;
}

async function searchUDN(query) {
  // 經濟日報 / 聯合新聞網 money.udn.com search
  const url = `https://money.udn.com/search/tag/1001/${encodeURIComponent(query)}?s=1`;
  try {
    const res = await axios.get(url, { headers: { 'User-Agent': USER_AGENT }});
    const $ = cheerio.load(res.data);
    const list = [];
    $('.story-list__news').each((i, el) => {
      const item = $(el);
      const a = item.find('h2 a');
      const title = a.text().trim();
      const href = a.attr('href');
      const dateText = item.find('.story-list__time').text().trim() || item.find('.meta').text();
      const date = normalizeDate(dateText);
      let fullUrl = href;
      if (href && href.startsWith('/')) fullUrl = 'https://money.udn.com' + href;
      list.push({ source: '經濟日報', title, url: fullUrl, date, summary: ''});
    });
    return list;
  } catch (e) {
    return [];
  }
}

async function searchCTEE(query) {
  // 工商時報 (ctee) – use site search
  const url = `https://www.ctee.com.tw/search?keyword=${encodeURIComponent(query)}`;
  try {
    const res = await axios.get(url, { headers: { 'User-Agent': USER_AGENT }});
    const $ = cheerio.load(res.data);
    const list = [];
    $('.post-list li').each((i, el) => {
      const a = $(el).find('a').first();
      const title = a.text().trim();
      const href = a.attr('href');
      const dateText = $(el).find('.time, .meta').text().trim();
      const date = normalizeDate(dateText);
      let fullUrl = href;
      if (href && href.startsWith('/')) fullUrl = 'https://www.ctee.com.tw' + href;
      list.push({ source: '工商時報', title, url: fullUrl, date, summary: '' });
    });
    return list;
  } catch (e) {
    return [];
  }
}

async function searchCMoney(query) {
  // CMoney news search (simple)
  const url = `https://www.cmoney.tw/finance/NewsList?keyword=${encodeURIComponent(query)}`;
  try {
    const res = await axios.get(url, { headers: { 'User-Agent': USER_AGENT }});
    const $ = cheerio.load(res.data);
    const list = [];
    $('.news-list .news-li').each((i, el) => {
      const a = $(el).find('a').first();
      const title = a.text().trim();
      const href = a.attr('href');
      const dateText = $(el).find('.date').text().trim();
      const date = normalizeDate(dateText);
      let fullUrl = href;
      if (href && href.startsWith('/')) fullUrl = 'https://www.cmoney.tw' + href;
      list.push({ source: 'CMoney', title, url: fullUrl, date, summary: '' });
    });
    return list;
  } catch (e) {
    return [];
  }
}

// --- Aggregate endpoint
// Query parameters: q (search keyword), start (YYYY-MM-DD), end (YYYY-MM-DD)
app.get('/api/search', async (req, res) => {
  const q = req.query.q || '台股';
  const start = req.query.start;
  const end = req.query.end;
  if (!start || !end) {
    return res.status(400).json({ error: '請提供 start 與 end，格式 YYYY-MM-DD' });
  }

  const startD = dayjs(start);
  const endD = dayjs(end);
  if (!startD.isValid() || !endD.isValid()) {
    return res.status(400).json({ error: '日期格式錯誤，請使用 YYYY-MM-DD' });
  }

  try {
    // call each source concurrently
    const [y, u, ctee, cmoney] = await Promise.all([
      searchYahoo(q),
      searchUDN(q),
      searchCTEE(q),
      searchCMoney(q)
    ]);

    const all = [...y, ...u, ...ctee, ...cmoney]
      .map(it => {
        // ensure date as string or null
        return { ...it, date: it.date || null };
      })
      // filter date between start and end (inclusive) — if date is null, exclude
      .filter(it => {
        if (!it.date) return false;
        const d = dayjs(it.date);
        return d.isValid() && (d.isSame(startD) || d.isSame(endD) || (d.isAfter(startD) && d.isBefore(endD)));
      })
      // dedupe by url or title
      .reduce((acc, cur) => {
        if (!acc.find(x => x.url === cur.url || x.title === cur.title)) acc.push(cur);
        return acc;
      }, [])
      // sort by date desc
      .sort((a,b) => (a.date < b.date ? 1 : -1));

    res.json({ query: q, start, end, count: all.length, results: all });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: '伺服器抓取發生錯誤', details: err.message });
  }
});

// CSV export
app.get('/api/export.csv', async (req, res) => {
  // expects query params same as /api/search
  const q = req.query.q || '台股';
  const start = req.query.start;
  const end = req.query.end;
  if (!start || !end) return res.status(400).send('missing start/end');

  // reuse search logic (call /api/search internally)
  try {
    const searchRes = await axios.get(`http://localhost:${process.env.PORT || 3000}/api/search`, { params: { q, start, end }});
    const data = searchRes.data.results || [];
    const csv = stringify(data.map(r => [r.source, r.date, r.title, r.url]));
    res.header('Content-Type', 'text/csv');
    res.attachment(`news_${start}_${end}.csv`);
    res.send(csv);
  } catch (e) {
    res.status(500).send('CSV export error: ' + e.message);
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));