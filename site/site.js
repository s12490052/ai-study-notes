const byId = id => document.getElementById(id);
function showNote(note) {
  byId('note-title').textContent = note.title;
  byId('note-summary').textContent = note.summary;
  byId('key-points').replaceChildren(...note.key_points.map(point => {
    const li = document.createElement('li'); li.textContent = point; return li;
  }));
  byId('quiz-panel').replaceChildren(...note.quiz.map((item, index) => {
    const details = document.createElement('details');
    const question = document.createElement('summary'); question.textContent = (index + 1) + '. ' + item.question;
    const answer = document.createElement('p'); answer.textContent = item.answer;
    details.append(question, answer); return details;
  }));
}
const tabs = [...document.querySelectorAll('[role="tab"]')];
function selectTab(selected) {
  tabs.forEach(tab => {
    const active = tab === selected;
    tab.setAttribute('aria-selected', String(active)); tab.tabIndex = active ? 0 : -1;
    byId(tab.getAttribute('aria-controls')).hidden = !active;
  });
}
tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => selectTab(tab));
  tab.addEventListener('keydown', event => {
    let next;
    if (event.key === 'ArrowRight') next = tabs[(index + 1) % tabs.length];
    if (event.key === 'ArrowLeft') next = tabs[(index + tabs.length - 1) % tabs.length];
    if (event.key === 'Home') next = tabs[0];
    if (event.key === 'End') next = tabs.at(-1);
    if (next) { event.preventDefault(); selectTab(next); next.focus(); }
  });
});
async function loadExample() {
  try {
    const responses = await Promise.all([fetch('data/example.json'), fetch('data/article.txt')]);
    if (responses.some(response => !response.ok)) throw new Error('成果檔案載入失敗');
    const [result, source] = await Promise.all([responses[0].json(), responses[1].text()]);
    showNote(result.note);
    byId('source-text').replaceChildren(...source.trim().split(/\n\s*\n/).slice(1).map(text => {
      const p = document.createElement('p'); p.textContent = text; return p;
    }));
    byId('input-count').textContent = result.meta.input_characters + ' 字';
    byId('run-meta').textContent = result.meta.model + ' · ' + result.meta.duration_seconds + ' 秒';
  } catch (error) {
    byId('note-title').textContent = '成果暫時無法載入';
    byId('demo-error').hidden = false;
    byId('demo-error').textContent = '請透過 GitHub Pages 或本機 HTTP 伺服器開啟此頁。也可直接下載下方 JSON / Markdown。';
  }
}
loadExample();
