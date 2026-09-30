"""fetch_abstracts.get() の URL の柵と再試行（ネットワークに出ない・decisions.md 判断 12・15）。

使い方: このディレクトリで `python -m unittest test_fetch`
"""
import datetime
import email.message
import email.utils
import io
import unittest
import urllib.error
import urllib.request
from unittest import mock

import fetch_abstracts as F

REAL_OPENER_FOR = F._opener_for  # setUp で塞ぐ前の本物（柵の中身を確かめる検査で使う）
ZEN = "https://zenodo.org/api/"
FENCE_PREFIX = "許していない先へのリダイレクト"  # common.guarded_opener の例外の文言（get() がこれで柵の失敗を見分ける）


class _FakeOpener:
    """open() が決まった例外を投げるか、JSON を返す opener。呼ばれた回数を数える。"""

    def __init__(self, exc=None, body=b"{}"):
        self.exc, self.body, self.calls = exc, body, 0

    def open(self, req, timeout=None):
        self.calls += 1
        if self.exc is not None:
            raise self.exc
        return io.BytesIO(self.body)


def _http_error(code, retry_after=None):
    h = email.message.Message()
    if retry_after is not None:
        h["Retry-After"] = retry_after
    return urllib.error.HTTPError("https://api.crossref.org/works/x", code, "err", h, None)


def _guard(op):
    return next(h for h in op.handlers if isinstance(h, urllib.request.HTTPRedirectHandler))


class FenceTest(unittest.TestCase):
    def setUp(self):
        # 柵が壊れていても本物のネットワークに出ないように、既定では opener を作れないようにする
        p = mock.patch.object(F, "_opener_for", side_effect=AssertionError("柵の前で止まるはずが opener を作ろうとした"))
        self.addCleanup(p.stop)
        p.start()

    def test_empty_allowed_rejects_everything(self):
        with self.assertRaises(F.FenceError):
            F.get(F.CR + "works/10.1/x", allowed=[])

    def test_url_outside_allowed(self):
        for url in ["https://evil.example/works", "https://api.crossref.org.evil.example/works",
                    "http://api.crossref.org/works/x", "https://user@api.crossref.org/works/x"]:
            with self.subTest(url=url):
                with self.assertRaises(F.FenceError):
                    F.get(url)

    def test_allowed_narrows_default(self):
        # 既定の 4 つに入る URL でも、渡した一覧に無ければ拒む
        with self.assertRaises(F.FenceError):
            F.get(F.CR + "works/x", allowed=[ZEN])

    def test_get_builds_opener_from_the_given_list(self):
        # get() は、渡された一覧そのもので opener を作る（既定の一覧で作ると、狭い一覧の柵が崩れる）
        fake = _FakeOpener()
        with mock.patch.object(F, "_opener_for", return_value=fake) as of:
            F.get(ZEN + "records/1", allowed=[ZEN])
        of.assert_called_once_with([ZEN])
        with mock.patch.object(F, "_opener_for", return_value=fake) as of:
            F.get(F.CR + "works/x")
        of.assert_called_once_with(F.ALLOWED)

    def test_opener_is_built_from_the_same_list(self):
        self.assertIs(REAL_OPENER_FOR([ZEN]), REAL_OPENER_FOR([ZEN]))
        self.assertIsNot(REAL_OPENER_FOR([ZEN]), REAL_OPENER_FOR(F.ALLOWED))

    def test_real_guard_rejects_redirect_outside(self):
        # common.guarded_opener の柵が、許していない先へのリダイレクトを要求の前に止め、get() が見分ける文言で知らせる
        req = urllib.request.Request(F.CR + "works/x")
        with self.assertRaises(urllib.error.URLError) as cm:
            _guard(REAL_OPENER_FOR(F.ALLOWED)).redirect_request(req, None, 302, "Found", {}, "https://evil.example/")
        self.assertTrue(str(cm.exception.reason).startswith(FENCE_PREFIX))

    def test_guard_uses_the_given_list(self):
        # 渡した一覧で作った opener の柵は、その一覧の外（既定の 4 つの中でも）へのリダイレクトを止める
        guard = _guard(REAL_OPENER_FOR([ZEN]))
        req = urllib.request.Request(ZEN + "records/1")
        with self.assertRaises(urllib.error.URLError):
            guard.redirect_request(req, None, 302, "Found", {}, F.CR + "works/x")
        self.assertIsNotNone(guard.redirect_request(req, None, 302, "Found", {}, ZEN + "records/2"))

    def test_redirect_outside_is_not_retried(self):
        fake = _FakeOpener(urllib.error.URLError(FENCE_PREFIX + ": https://evil.example/"))
        with mock.patch.object(F, "_opener_for", return_value=fake), mock.patch.object(F.time, "sleep") as sl:
            with self.assertRaises(F.FenceError):
                F.get(F.CR + "works/x")
        self.assertEqual(fake.calls, 1)
        sl.assert_not_called()


class RetryTest(unittest.TestCase):
    def test_404_is_none_without_retry(self):
        fake = _FakeOpener(_http_error(404))
        with mock.patch.object(F, "_opener_for", return_value=fake), mock.patch.object(F.time, "sleep") as sl:
            self.assertIsNone(F.get(F.CR + "works/x"))
        self.assertEqual(fake.calls, 1)
        sl.assert_not_called()

    def test_429_retries_and_does_not_sleep_after_last(self):
        fake = _FakeOpener(_http_error(429, "2"))
        with mock.patch.object(F, "_opener_for", return_value=fake), mock.patch.object(F.time, "sleep") as sl:
            with self.assertRaises(urllib.error.HTTPError):
                F.get(F.CR + "works/x", tries=3)
        self.assertEqual(fake.calls, 3)
        self.assertEqual([c.args[0] for c in sl.call_args_list], [2, 2])

    def test_tries_must_be_positive(self):
        with mock.patch.object(F, "_opener_for", side_effect=AssertionError("opener を作る前に止まるはず")):
            with self.assertRaises(ValueError):
                F.get(F.CR + "works/x", tries=0)

    def test_retry_after_forms(self):
        self.assertEqual(F.retry_after_seconds("5", 0), 5)
        self.assertEqual(F.retry_after_seconds("999", 0), 60)
        self.assertEqual(F.retry_after_seconds(None, 1), 16)
        self.assertEqual(F.retry_after_seconds("not-a-number", 0), 8)
        self.assertEqual(F.retry_after_seconds("-5", 1), 16)  # 負の値は既定に回す
        self.assertEqual(F.retry_after_seconds("Wed, 21 Oct 2015 07:28:00 GMT", 0), 0)  # 過去の日付

    def test_retry_after_future_dates(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        future = email.utils.format_datetime(now + datetime.timedelta(seconds=30), usegmt=True)
        self.assertTrue(25 <= F.retry_after_seconds(future, 0) <= 30)
        # タイムゾーンの無い日付（-0000）は UTC とみなす（ローカル時刻と比べない）
        naive = (now + datetime.timedelta(seconds=30)).strftime("%a, %d %b %Y %H:%M:%S -0000")
        self.assertTrue(25 <= F.retry_after_seconds(naive, 0) <= 30)

    def test_json_is_returned(self):
        fake = _FakeOpener(body=b'{"a": 1}')
        with mock.patch.object(F, "_opener_for", return_value=fake):
            self.assertEqual(F.get(F.CR + "works/x"), {"a": 1})


if __name__ == "__main__":
    unittest.main()
