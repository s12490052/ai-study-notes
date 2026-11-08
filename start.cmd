@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 拾頁 StudyNote - 本機讀書筆記整理器
echo 請開啟 Ollama，再瀏覽 http://127.0.0.1:8000/app.html
echo 作品頁在 http://127.0.0.1:8000/
echo.
where uv >nul 2>nul
if %errorlevel%==0 (
  uv run --locked python main.py --serve
) else if exist "..\.tools\bin\uv.exe" (
  "..\.tools\bin\uv.exe" run --locked --offline --cache-dir "..\.tools\uv-cache" python main.py --serve
) else (
  echo 未找到 uv，改用 Python；程式無額外 Python 套件依賴。
  python main.py --serve
)
pause
