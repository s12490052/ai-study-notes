"""CLI entry point: uv run python main.py --input examples/article.txt"""

import argparse
import sys
from pathlib import Path

from studynote import StudyNoteError, generate_note, save_result, to_markdown


def main():
    parser = argparse.ArgumentParser(description="拾頁：使用本機 Ollama 整理讀書筆記")
    parser.add_argument("--input", type=Path, help="UTF-8 文章檔案")
    parser.add_argument("--output", type=Path, default=Path("results/notes"), help="輸出路徑（自動產生 .json 與 .md）")
    parser.add_argument("--model", help="Ollama 模型，預設 qwen3:1.7b")
    parser.add_argument("--serve", action="store_true", help="開啟本機網頁介面")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.serve:
        from server import serve
        serve(args.port, args.model)
        return 0
    if not args.input:
        parser.error("請提供 --input 文章.txt，或使用 --serve")
    try:
        text = args.input.read_text(encoding="utf-8-sig")
        print("正在呼叫本機 Ollama，首次載入模型可能需要幾分鐘…", file=sys.stderr)
        result = generate_note(text, model=args.model)
        save_result(result, args.output)
        print(to_markdown(result))
        print(f"已儲存：{args.output.with_suffix('.json')} 與 {args.output.with_suffix('.md')}", file=sys.stderr)
        return 0
    except (StudyNoteError, OSError, UnicodeError) as error:
        print(f"錯誤：{error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
