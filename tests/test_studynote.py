import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from studynote import StudyNoteError, generate_note, save_result, validate_input, validate_note

NOTE = {"title": "學習方法", "summary": "主動回想並分散複習。", "key_points": ["合上書回想", "分散練習", "核對答案"],
        "quiz": [{"question": f"問題{i}", "answer": "參考答案"} for i in range(3)]}


class NotesTests(unittest.TestCase):
    def test_schema_rejects_missing_extra_and_wrong_fields(self):
        for key in NOTE:
            bad = copy.deepcopy(NOTE)
            del bad[key]
            with self.assertRaises(StudyNoteError):
                validate_note(bad)
        for changes in [{"extra": 1}, {"title": " "}, {"summary": "x" * 501},
                        {"key_points": ["only one"]}, {"quiz": []},
                        {"quiz": [{"question": "Q"}] * 3}, {"key_points": [1, 2, 3]}]:
            with self.subTest(changes=changes), self.assertRaises(StudyNoteError):
                validate_note({**NOTE, **changes})

    def test_input_bounds_and_type(self):
        for text in [None, 2, " ", "字" * 29, "字" * 6001]:
            with self.assertRaises(StudyNoteError):
                validate_input(text)
        self.assertEqual(validate_input("字" * 30), "字" * 30)
        self.assertEqual(len(validate_input("字" * 6000)), 6000)

    @patch("studynote.urlopen")
    def test_real_request_contract_and_validated_response(self, mocked):
        mocked.return_value.__enter__.return_value.read.return_value = json.dumps({
            "message": {"content": json.dumps(NOTE)}, "total_duration": 1250000000
        }).encode()
        result = generate_note("原" * 40)
        payload = json.loads(mocked.call_args.args[0].data)
        self.assertEqual(payload["format"]["type"], "object")
        self.assertFalse(payload["stream"])
        self.assertFalse(payload["think"])
        self.assertEqual(result["note"], NOTE)
        self.assertEqual(result["meta"]["duration_seconds"], 1.25)

    @patch("studynote.urlopen")
    def test_connection_and_missing_model_errors(self, mocked):
        for error, message in [(URLError("offline"), "無法連線"),
                               (HTTPError("url", 404, "missing", {}, None), "ollama pull"),
                               (TimeoutError(), "逾時")]:
            mocked.side_effect = error
            with self.assertRaisesRegex(StudyNoteError, message):
                generate_note("原" * 40)

    @patch("studynote.urlopen")
    def test_invalid_model_json_is_not_published(self, mocked):
        for content in ["not json", json.dumps({"title": "缺少欄位"})]:
            mocked.return_value.__enter__.return_value.read.return_value = json.dumps({
                "message": {"content": content}
            }).encode()
            with self.assertRaises(StudyNoteError):
                generate_note("原" * 40)

    def test_remote_host_is_rejected(self):
        with self.assertRaisesRegex(StudyNoteError, "本機"):
            generate_note("原" * 40, host="http://example.com:11434")

    def test_unicode_exports(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder) / "notes"
            save_result({"note": NOTE, "meta": {"model": "test"}}, base)
            self.assertEqual(json.loads(base.with_suffix(".json").read_text(encoding="utf-8"))["note"], NOTE)
            self.assertIn("參考答案", base.with_suffix(".md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
