const el = id => document.getElementById(id);
let currentResult = null;
el('generate').disabled = true;
const status = (message, error = false) => {
  el('status').textContent = message; el('status').classList.toggle('error', error);
};
async function checkLocal() {
  try {
    const response = await fetch('api/health');
    if (!response.ok || (await response.json()).mode !== 'local') throw new Error();
    status('本機服務就緒。首次載入模型可能需要幾分鐘。');
    el('generate').disabled = false;
  } catch {
    status('請先執行 uv run python main.py --serve，再開啟 http://127.0.0.1:8000/app.html。GitHub Pages 不提供 AI 推論。', true);
  }
}
checkLocal();
el('article').addEventListener('input', () => {
  el('counter').textContent = [...el('article').value].length + ' / 6,000 字';
});
el('load-example').addEventListener('click', async () => {
  try {
    const response = await fetch('data/article.txt');
    if (!response.ok) throw new Error();
    el('article').value = await response.text();
    el('article').dispatchEvent(new Event('input'));
  } catch { status('示範文章載入失敗，請自行貼上文章。', true); }
});
el('note-form').addEventListener('submit', async event => {
  event.preventDefault();
  el('generate').disabled = true;
  status('正在整理中…請等候本機模型回覆（最多約 3 分鐘）。');
  try {
    const response = await fetch('api/analyze', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text: el('article').value}), signal: AbortSignal.timeout(200000)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || '生成失敗，請稍後重試。');
    currentResult = result;
    const note = result.note;
    el('result-title').textContent = note.title;
    el('result-summary').textContent = note.summary;
    el('result-points').replaceChildren(...note.key_points.map(point => {
      const li = document.createElement('li'); li.textContent = point; return li;
    }));
    el('result-quiz').replaceChildren(...note.quiz.map((item, index) => {
      const details = document.createElement('details');
      const summary = document.createElement('summary'); summary.textContent = (index + 1) + '. ' + item.question;
      const p = document.createElement('p'); p.textContent = item.answer;
      details.append(summary, p); return details;
    }));
    el('result-meta').textContent = result.meta.model + ' · ' + result.meta.duration_seconds + ' 秒';
    el('empty').hidden = true; el('result').hidden = false;
    status('筆記完成。請對照原文檢查，再下載保存。');
  } catch (error) {
    status(error.name === 'TimeoutError' ? '等候逾時，請縮短文章後再試。' : (error.message || '連線失敗，請確認本機服務。'), true);
  } finally { el('generate').disabled = false; }
});
function download(text, type, name) {
  const url = URL.createObjectURL(new Blob([text], {type}));
  const a = document.createElement('a'); a.href = url; a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
el('download-json').addEventListener('click', () => {
  if (currentResult) download(JSON.stringify(currentResult, null, 2), 'application/json', 'studynote.json');
});
el('download-md').addEventListener('click', () => {
  if (!currentResult) return;
  const n = currentResult.note;
  const text = ['# ' + n.title, '', '## 摘要', '', n.summary, '', '## 三個重點', '',
    ...n.key_points.map((p, i) => (i + 1) + '. ' + p), '', '## 自我測驗', '',
    ...n.quiz.flatMap((q, i) => ['### ' + (i + 1) + '. ' + q.question, '', '參考答案：' + q.answer, '']),
    '模型：' + currentResult.meta.model, '', 'AI 產生內容，請對照原文核對。', ''].join('\n');
  download(text, 'text/markdown;charset=utf-8', 'studynote.md');
});
