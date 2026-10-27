import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("churn", Path(__file__).with_name("churn.py"))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class ChurnTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.calls = []
        self.env = patch.dict(os.environ, {"GH_TOKEN": "fixture-secret"})
        self.env.start()
        self.addCleanup(self.env.stop)

    def ok(self, endpoint, headers):
        self.calls.append((endpoint, headers))
        release = {"tag_name": "v1", "assets": [{"name": "a", "download_count": 1}]}
        body = release if endpoint.endswith("latest") else [release]
        return 200, {"etag": '"fixture"'}, c.encode(body)

    def test_three_rounds_and_offline_analysis(self):
        base = self.root / "base"
        c.collect(base, "baseline", request=self.ok)
        self.assertEqual(len(self.calls), 6)

        def unchanged(endpoint, headers):
            self.assertEqual(headers["If-None-Match"], '"fixture"')
            return 304, {}, b""

        hour, day = self.root / "hour", self.root / "day"
        c.collect(hour, "hour", base, request=unchanged)
        c.collect(day, "day", hour, request=unchanged)
        result = c.analyze(day)
        self.assertFalse(any(v["body_changed"] for v in result["changes"]["day"].values()))
        self.assertGreater(result["layouts"]["exact"]["pack_and_index_bytes"], 0)
        self.assertNotIn("fixture-secret", str(list(day.rglob("*"))))
        for path in day.rglob("*.json"):
            self.assertNotIn("fixture-secret", path.read_text())

    def test_errors_stop_without_retry_and_preserve_partial_metadata(self):
        for status in (301, 403, 404, 429, 500):
            with self.subTest(status=status):
                calls = []

                def error(endpoint, headers):
                    calls.append(endpoint)
                    return status, {}, b"{}"

                output = self.root / str(status)
                with self.assertRaises(RuntimeError):
                    c.collect(output, "baseline", request=error)
                self.assertEqual(len(calls), 1)
                meta = json.loads((output / "baseline/observation.json").read_text())
                self.assertFalse(meta["complete"])

    def test_oversize_bad_json_and_unconditional_304_stop(self):
        for label, response in (("large", (200, {}, b"x" * (c.BODY_CAP + 1))),
                                ("json", (200, {}, b"bad")),
                                ("304", (304, {}, b"")),
                                ("quota", (200, {"x-ratelimit-remaining": "0"}, b"[]"))):
            with self.subTest(label=label), self.assertRaises(RuntimeError):
                c.collect(self.root / label, "baseline", request=lambda *args: response)

    def test_corrupted_prior_prevents_requests(self):
        base = self.root / "base"
        c.collect(base, "baseline", request=self.ok)
        (base / "baseline/obsidian-list.json").write_text("[]")
        self.calls.clear()
        with self.assertRaises(ValueError):
            c.collect(self.root / "hour", "hour", base, request=self.ok)
        self.assertEqual(self.calls, [])

    def test_projection_and_paths_expose_counter_changes(self):
        a = [{"tag_name": "v1", "assets": [{"name": "a", "download_count": 1}]}]
        b = [{"tag_name": "v1", "assets": [{"name": "a", "download_count": 2}]}]
        self.assertEqual(c.project(a), c.project(b))
        self.assertEqual(c.changed_paths(a, b), ['$[0]["assets"][0]["download_count"]'])

    def test_description_url_and_last_match_are_visible(self):
        body = c.encode([{"body": "https://example.test/description.AppImage",
                          "assets": [{"browser_download_url": "https://example.test/asset.AppImage"}]}])
        self.assertEqual(c.diagnostic_filter("obsidian-list", body),
                         "https://example.test/description.AppImage")
        self.assertEqual(c.diagnostic_filter("obsidian-list", c.encode(c.project(json.loads(body)))),
                         "https://example.test/asset.AppImage")
        body = b'["https://example.test/nightly-one.AppImage","https://example.test/nightly-two.AppImage"]'
        self.assertEqual(c.diagnostic_filter("wezterm-list", body),
                         "https://example.test/nightly-two.AppImage")

    def test_transport_failure_has_no_secret_in_metadata(self):
        def error(*args):
            raise OSError("fixture-secret")
        output = self.root / "error"
        with self.assertRaises(RuntimeError):
            c.collect(output, "baseline", request=error)
        self.assertNotIn("fixture-secret", (output / "baseline/observation.json").read_text())

    def test_http_redirect_evidence_without_following(self):
        from email.message import Message
        from unittest.mock import Mock
        headers = Message()
        destination = "https://api.github.com/repositories/120568143/releases?per_page=100"
        headers["Location"] = destination
        headers["Set-Cookie"] = "not-for-evidence"
        body = b'{"message":"Moved Permanently"}'
        error = c.urllib.error.HTTPError("https://api.github.com/old", 301,
                                        "Moved", headers, io.BytesIO(body))
        opener = Mock()
        opener.open.side_effect = error
        output = self.root / "redirect"
        with patch.object(c.urllib.request, "build_opener", return_value=opener) as build:
            with self.assertRaises(RuntimeError):
                c.collect(output, "baseline", request=c.fetch)
        self.assertIsInstance(build.call_args.args[0], c.NoRedirect)
        self.assertIsNone(c.NoRedirect().redirect_request(None, None, None, None, None, None))
        self.assertEqual(opener.open.call_count, 1)
        meta = json.loads((output / "baseline/observation.json").read_text())
        entry = meta["responses"]["obsidian-list"]
        self.assertEqual(entry["status"], 301)
        self.assertEqual(entry["headers"]["location"], destination)
        self.assertNotIn("set-cookie", entry["headers"])
        self.assertEqual((output / "baseline" / entry["error_body_file"]).read_bytes(), body)
        self.assertEqual(entry["error_body_sha256"], c.digest(body))
        self.assertFalse(meta["complete"])


if __name__ == "__main__":
    unittest.main()
