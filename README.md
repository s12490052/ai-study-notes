# 拾頁 StudyNote｜AI 讀書筆記整理器

作者：林子堯 · GitHub：[`s12490052`](https://github.com/s12490052)

以 **Python + uv + 本地 Ollama** 將文章整理成摘要、三個重點與三題附答案的自我測驗。提供命令列、本機網頁及 JSON / Markdown 匯出。

- 預定作品網址：<https://s12490052.github.io/ai-study-notes/>（完成上傳與部署後才會生效）
- 預定儲存庫：<https://github.com/s12490052/ai-study-notes>
- 初次上傳：[手動上線步驟](MANUAL_STEPS.md)

## 做了什麼

把「讀過」的短文變成可複習的筆記，利用問題練習主動回想。

本專案使用作業要求的 **結構化輸出**：Python 將文章與 JSON Schema 送往 Ollama `/api/chat`，使用 `format` 限定回傳欄位、字數與陣列長度；再以 `json.loads` 解析並驗證型別與結構，合格後才能顯示或匯出。

全程使用 Python 標準函式庫，不需要 API 金鑰或額外 Python 套件。`uv.lock` 記錄專案環境，Ollama 另行安裝。

## 怎麼執行

### 1. 環境

安裝 [Python 3.10+](https://www.python.org/downloads/)、[uv](https://docs.astral.sh/uv/getting-started/installation/)、[Ollama](https://ollama.com/download) 與 [Git](https://git-scm.com/downloads)。已安裝 Python 的 Windows 也可執行 `python -m pip install uv`。

開啟 Ollama，下載模型：

```powershell
ollama pull qwen3:1.7b
ollama list
```

若 Ollama 未提供服務，可另開終端機執行 `ollama serve`；若連接埠已占用，通常代表服務已啟動。

### 2. 取得程式

```powershell
git clone https://github.com/s12490052/ai-study-notes.git
cd ai-study-notes
uv sync --locked
```

本次交付已在 `C:\Users\USER\Documents\New project\ai-study-notes`，不用再次 clone。若 `uv` 不在 PATH，可用 `..\.tools\bin\uv.exe` 取代指令中的 `uv`。

### 3. 本機網頁

```powershell
uv run python main.py --serve
```

開啟 <http://127.0.0.1:8000/app.html>，貼上 30–6,000 字文章並按「整理成筆記」。首次載入可能較慢，完成後可展開答案及下載。按 `Ctrl+C` 結束。Windows 也可雙擊 `start.cmd`。

### 4. 命令列與匯出

```powershell
uv run python main.py --input examples/article.txt --output results/notes
```

產生 `results/notes.json` 與 `results/notes.md`。自己的文章存為 UTF-8 純文字後，替換 `--input` 路徑。

```powershell
uv run python main.py --input 我的文章.txt --output results/my-notes
uv run python main.py --serve --port 8080
```

`--model` 或 `OLLAMA_MODEL` 可指定已下載的模型。`OLLAMA_HOST` 預設 `http://127.0.0.1:11434`，僅接受本機 HTTP 位址。本程式不讀 `.env`，也不使用金鑰。

## 執行結果

示範文章：[主動回想與間隔複習](examples/article.txt)，由 Codex 為本作業撰寫。

2026-11-08 在交付電腦實際執行：

| 項目 | 實測結果 |
| --- | --- |
| 模型 | `qwen3:1.7b` |
| 輸入 | 275 字（去除頭尾空白後） |
| 模型回報耗時 | 35.58 秒，依硬體與載入狀態不同 |
| 輸出 | 摘要、3 個重點、3 題測驗 |
| Python 格式檢查 | 通過 |

完整未人工改寫的輸出：[JSON](site/data/example.json)、[Markdown](site/data/example.md)。本機網頁另一次實測耗時 32.26 秒。

摘要節錄：

> 本文介紹主動回想與間隔複習兩種學習方法。主動回想是指合上教材後用自己的話回答問題，再對照原文修正錯誤；間隔複習則是分散時間複習，避免考前一次性讀完。

**內容檢查：** 摘要涵蓋主要方法，但模型補入原文未明確陳述的「提高記憶效果」，第三題混合兩種方法的概念。結構化輸出能約束格式，不能保證內容正確，仍須對照原文。範例保留原始結果以呈現此限制。

## 測試

```powershell
uv run python -m unittest discover -s tests -v
uv run python scripts/check_site.py
```

10 項測試已通過，涵蓋輸入邊界、輸出驗證、連線與逾時錯誤、UTF-8 匯出、本機 API 串接與請求檢查。自動測試使用 mock，無需模型；上方範例另由真實 Ollama 執行。網站檢查涵蓋連結、錨點、範例格式及原文一致性。

瀏覽器實測涵蓋成果載入、測驗切換、答案展開、填入文章、生成筆記及窄版溢出修正。遠端 Actions 是否成功，須於上傳後確認。

## GitHub Actions 與 Pages

工作流程：[`.github/workflows/pages.yml`](.github/workflows/pages.yml)。推送 `main` 或手動啟動後，會安裝 uv、同步鎖定環境、執行測試、檢查作品頁、上傳 `site/`，再以 `pages: write`、`id-token: write` 權限部署。

GitHub Pages 是靜態展示，不執行 Ollama。雲端測試不呼叫模型；AI 功能在本機執行。首次請將 Settings → Pages → Source 設為 GitHub Actions，詳見手動步驟。

## 專案結構

```text
.github/workflows/pages.yml  測試與部署
main.py                     命令列入口
studynote.py                模型、Schema、驗證與匯出
server.py                   本機網頁 API
start.cmd                   Windows 啟動
pyproject.toml / uv.lock    uv 環境
examples/article.txt        示範輸入
tests/                      自動測試
scripts/check_site.py       靜態作品檢查
site/                       作品頁、本機介面與真實結果
MANUAL_STEPS.md             上傳與繳交步驟
```

`.gitignore` 忽略 `.env`、虛擬環境、快取及個人 `results/`。`site/data/` 是刻意公開的示範，請勿放私人文章。

## AI 使用說明

| 工具 | 使用位置 |
| --- | --- |
| Codex | 協助規劃、程式、網頁、測試、文件、Actions 與除錯 |
| Ollama / qwen3:1.7b | 執行時生成結構化筆記 |

由 Codex 完成的修改與驗證：JSON Schema 與 Python 格式檢查、錯誤處理、本機介面、10 項測試、網頁操作、窄版溢出修正，以及實際模型呼叫。開發提交作者標示 Codex，不冒充學生自行完成的歷史。

### 我的修改與驗證紀錄（林子堯提交前自行補寫）

請依真實操作填寫，完成後移除此提示；先用自己的文章試跑，再對照原文核對。

- 我實際修改了：＿＿＿＿
- 我使用哪篇文章、如何驗證：＿＿＿＿
- 我發現的錯誤或限制，以及如何修正：＿＿＿＿

## 技術參考

- [Ollama Structured Outputs](https://docs.ollama.com/capabilities/structured-outputs)
- [Ollama Chat API](https://docs.ollama.com/api/chat)
- [uv in GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/)
- [GitHub Pages workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

