import json
import threading
import unittest
from functools import partial
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from server import Handler, SITE
from test_studynote import NOTE


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(SITE)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_health_and_static_page(self):
        with urlopen(self.base + "/api/health") as response:
            self.assertEqual(json.load(response)["mode"], "local")
        with urlopen(self.base + "/") as response:
            self.assertIn("拾頁", response.read().decode("utf-8"))
        with self.assertRaises(HTTPError) as error:
            urlopen(self.base + "/../studynote.py")
        self.assertEqual(error.exception.code, 404)

    @patch("server.generate_note", return_value={"note": NOTE, "meta": {"model": "mock"}})
    def test_post_is_connected_to_generation(self, mock):
        request = Request(self.base + "/api/analyze", json.dumps({"text": "原" * 40}).encode(),
                          {"Content-Type": "application/json", "Origin": self.base})
        with urlopen(request) as response:
            self.assertEqual(json.load(response)["note"], NOTE)
        mock.assert_called_once_with("原" * 40, model=None)

    def test_external_origin_and_malformed_payload_are_rejected(self):
        for data, headers, expected in [
            (b"{}", {"Content-Type": "application/json", "Origin": "https://example.com"}, 403),
            (b"{", {"Content-Type": "application/json"}, 400),
            (b"[]", {"Content-Type": "application/json"}, 400),
            (b"{}", {"Content-Type": "text/plain"}, 415),
        ]:
            with self.subTest(expected=expected), self.assertRaises(HTTPError) as error:
                urlopen(Request(self.base + "/api/analyze", data, headers))
            self.assertEqual(error.exception.code, expected)


if __name__ == "__main__":
    unittest.main()
