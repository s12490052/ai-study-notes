# 林子堯｜手動上線與繳交

程式、作品頁、README、uv 環境及 Actions 已完成，本機模型與測試已執行。目前已上傳 GitHub 並成功部署 Pages，個人實測截圖也已收錄於 README 與作品頁。以下保留首次上線及後續更新的操作方式。

## 1. 先看成品

開啟 `C:\Users\USER\Documents\New project\ai-study-notes`，雙擊 `start.cmd`，保持終端機開啟。

- 作品頁：<http://127.0.0.1:8000/>
- 本機 AI 介面：<http://127.0.0.1:8000/app.html>

若 8000 已占用，可能原本預覽仍在執行，可直接開網址；也可用 `python main.py --serve --port 8080` 改用 8080。

## 2. 建立公開 repo

1. 登入 [GitHub](https://github.com/)，確認帳號 **s12490052**。
2. 開啟 [新增儲存庫](https://github.com/new)，名稱填 **ai-study-notes**。
3. 選 **Public**。
4. **不要勾選** README、`.gitignore` 或 License，避免遠端先有其他 commit。
5. 按 **Create repository**。

若同名 repo 已存在且有內容，先不要覆蓋，將網址交給 Codex 檢查。

## 3. 上傳全部 commit

在專案資料夾空白處按右鍵，選「在終端機中開啟」，貼上：

```powershell
cd "C:\Users\USER\Documents\New project\ai-study-notes"
git remote -v
git log --oneline
git push -u origin main
```

`origin` 已設定為 `https://github.com/s12490052/ai-study-notes.git`。出現登入視窗時，依 Git Credential Manager 的瀏覽器流程，用 `s12490052` 登入授權。不要把 GitHub 密碼當成終端機密碼輸入。

**不要只用 GitHub 網頁 Upload files**，那樣不會帶上本機的多個 commit，無法保留「至少 5 個 commit」的歷史。

若使用交付 zip，先完整解壓並保留隱藏 `.git` 資料夾，在解壓後專案路徑執行命令。不要上傳 `.venv` 或父層 `.tools`。

## 4. 開啟 Pages 自動部署

1. 到 repo 的 **Settings → Pages**。
2. **Build and deployment → Source** 選 **GitHub Actions**。
3. 到 **Actions → Test and deploy GitHub Pages**。
4. 若第一次 push 因 Pages 尚未開啟失敗，按 **Run workflow → main → Run workflow**。
5. 等 `test-and-build` 和 `deploy` 都出現綠色勾勾。
6. 打開部署工作提供的網址，通常為 <https://s12490052.github.io/ai-study-notes/>。

設定依據：[GitHub 官方文件](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。

## 5. 補自己的驗證紀錄

1. 在本機介面貼上自己的教材，生成並下載筆記。
2. 對照原文檢查摘要、重點與測驗，記下至少一項具體觀察；若有錯誤，寫出正確內容。
3. 編輯 README 的「我的修改與驗證紀錄」，如實填入自己做的事。
4. 修改 `site/index.html` 的「學生自行確認」那段，改成自己的實際經驗。
5. 保存後提交：

```powershell
git config user.name "林子堯"
git config user.email "s12490052@users.noreply.github.com"
git add README.md site/index.html
git commit -m "docs: record my own testing and review"
git push
```

若要讓 commit 正確連結帳號，可到 GitHub Settings → Emails 複製自己的 noreply email 取代。不要把 Codex 的驗證直接寫成自己做過。

## 6. 繳交前檢查

- [ ] Repo 為 Public，程式、README、`.gitignore` 與 workflow 都在。
- [ ] GitHub commit 至少 5 個（本機已建立多個分階段 commit）。
- [ ] Actions 有綠色成功紀錄。
- [ ] Pages 可開啟，四項內容齊全。
- [ ] 已補個人真實修改與驗證紀錄。
- [ ] 沒有金鑰、密碼或 `.env`（本專案不需金鑰）。

建議繳交：

```text
GitHub Repo：https://github.com/s12490052/ai-study-notes
GitHub Pages：https://s12490052.github.io/ai-study-notes/
```

是否還需截圖，請依課堂平台欄位要求；提供的兩張截圖沒有列出其他繳交格式。

