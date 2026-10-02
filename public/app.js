// public/app.js
document.addEventListener('DOMContentLoaded', () => {
  const qEl = document.getElementById('q');
  const startEl = document.getElementById('start');
  const endEl = document.getElementById('end');
  const searchBtn = document.getElementById('searchBtn');
  const exportBtn = document.getElementById('exportBtn');
  const listEl = document.getElementById('list');
  const infoEl = document.getElementById('info');

  // Defaults: last 5 days
  const toDate = new Date();
  const fromDate = new Date();
  fromDate.setDate(toDate.getDate() - 4);
  startEl.value = fromDate.toISOString().slice(0,10);
  endEl.value = toDate.toISOString().slice(0,10);

  searchBtn.addEventListener('click', async () => {
    const q = qEl.value.trim() || '台股';
    const start = startEl.value;
    const end = endEl.value;
    if (!start || !end) { alert('請輸入起訖日期'); return; }
    infoEl.textContent = `搜尋中…（關鍵字：${q}，日期：${start} ~ ${end}）`;
    listEl.innerHTML = '';
    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(q)}&start=${start}&end=${end}`);
      if (!res.ok) throw new Error('伺服器錯誤');
      const data = await res.json();
      infoEl.textContent = `找到 ${data.count} 筆結果（${data.start} → ${data.end}）`;
      if (!data.results || data.results.length === 0) {
        listEl.innerHTML = '<div class="empty">無符合條件的新聞。</div>';
        return;
      }
      const frag = document.createDocumentFragment();
      data.results.forEach(item => {
        const div = document.createElement('div');
        div.className = 'result-item';
        div.innerHTML = `
          <div style="flex:1">
            <div class="title"><a href="${item.url}" target="_blank" rel="noopener">${escapeHtml(item.title)}</a></div>
            <div class="meta">${item.source} • ${item.date || ''}</div>
            <div style="margin-top:6px;"><a href="${item.url}" target="_blank">閱讀原文</a></div>
          </div>
        `;
        frag.appendChild(div);
      });
      listEl.appendChild(frag);
    } catch (e) {
      infoEl.textContent = '搜尋失敗：' + e.message;
      listEl.innerHTML = '<div class="empty">搜尋錯誤，請查看後端日誌。</div>';
    }
  });

  exportBtn.addEventListener('click', () => {
    const q = qEl.value.trim() || '台股';
    const start = startEl.value;
    const end = endEl.value;
    if (!start || !end) { alert('請輸入起訖日期'); return; }
    const url = `/api/export.csv?q=${encodeURIComponent(q)}&start=${start}&end=${end}`;
    window.location.href = url;
  });

  // simple escape
  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }
});