"""作業の記録の読み込みと窓への当て方の単体テスト（python3 -I -m unittest test_evaluate_diary）。

実データでしか通らない経路（Markdown の表・日の見出し・行の終わり・PC の名前）を、小さな文字列で確かめる
（code-reviewer HIGH・判断 16）。
"""

import importlib.util
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
_spec = importlib.util.spec_from_file_location("act_evaluate", HERE / "evaluate.py")
ev = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ev)

PCS = ev.diary_pcs({"diary_pcs": {"Mac": ["mac", "macbook"], "G-GEAR": ["ggear"], "なし": ["離席"]}})


def parse(text):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "diary.md"
        p.write_text(text, encoding="utf-8")
        return ev.parse_diary_md(p, PCS)


def ms(s):
    return int(datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=ev.TZ).timestamp() * 1000)


HEADER = "| 時刻 | 作業 | PC | 後で |\n|---|---|---|---|\n"


class ParseTest(unittest.TestCase):
    def test_heading_with_suffix_and_fullwidth_time(self):
        d = parse("# 題\n\n## 2026-11-22（土）\n\n" + HEADER + "| ０９：１０ | 論文 | MacBook |  |\n|  |  |  |  |\n")
        self.assertEqual(len(d["entries"]), 1)
        e = d["entries"][0]
        self.assertEqual(e["start_ms"], ms("2026-11-22 09:10"))
        self.assertEqual(e["pc"], "Mac")
        self.assertFalse(e["late"])

    def test_late_mark(self):
        d = parse("## 2026-11-22\n" + HEADER + "| 9:10 | 論文 | Mac | 後 |\n")
        self.assertTrue(d["entries"][0]["late"])

    def test_bad_heading_stops(self):
        with self.assertRaises(SystemExit):
            parse("## 11月22日\n" + HEADER + "| 9:10 | 論文 | Mac | |\n")

    def test_unreadable_time_stops(self):
        with self.assertRaises(SystemExit):
            parse("## 2026-11-22\n" + HEADER + "| 9時10分 | 論文 | Mac | |\n")

    def test_empty_task_stops(self):
        with self.assertRaises(SystemExit):
            parse("## 2026-11-22\n" + HEADER + "| 9:10 |  | Mac | |\n")

    def test_unknown_pc_stops(self):
        with self.assertRaises(SystemExit):
            parse("## 2026-11-22\n" + HEADER + "| 9:10 | 論文 | 自宅の Mac | |\n")

    def test_row_before_heading_stops(self):
        with self.assertRaises(SystemExit):
            parse(HEADER + "| 9:10 | 論文 | Mac | |\n")

    def test_entries_sorted_across_days(self):
        d = parse("## 2026-11-23\n" + HEADER + "| 9:00 | B | Mac | |\n## 2026-11-22\n" + HEADER
                  + "| 22:00 | A | Mac | |\n")
        self.assertEqual([e["task"] for e in d["entries"]], ["A", "B"])


class Win:
    def __init__(self, starts):
        self.start_ms = np.array(starts, dtype=np.int64)
        self.end_ms = self.start_ms + 180_000


class PerWindowTest(unittest.TestCase):
    def setUp(self):
        self.diary = {"entries": [
            {"start_ms": ms("2026-11-22 09:00"), "task": "A", "pc": "Mac"},
            {"start_ms": ms("2026-11-22 10:00"), "task": "B", "pc": "G-GEAR"},
            {"start_ms": ms("2026-11-22 11:00"), "task": "A", "pc": "Mac"},
            {"start_ms": ms("2026-11-23 10:00"), "task": "A", "pc": "Mac"},
        ], "end_ms": None}

    def _at(self, *times):
        return Win([ms(t) for t in times])

    def test_outside_mac_is_one_name(self):
        lab, pc, blk = ev.per_window_diary(self._at("2026-11-22 09:30", "2026-11-22 10:30"), self.diary,
                                           "task_or_outside")
        self.assertEqual(lab, ["A", "（Mac の外）"])
        self.assertEqual(pc, ["Mac", "G-GEAR"])
        self.assertNotEqual(blk[0], blk[1])

    def test_mac_only_drops_outside(self):
        lab, _, _ = ev.per_window_diary(self._at("2026-11-22 10:30"), self.diary, "mac_only")
        self.assertEqual(lab, [None])

    def test_next_entry_spans_night(self):
        lab, _, _ = ev.per_window_diary(self._at("2026-11-23 08:00"), self.diary, "task_or_outside", "next_entry")
        self.assertEqual(lab, ["A"])

    def test_day_end_cuts_at_midnight(self):
        w = self._at("2026-11-23 08:00", "2026-11-22 23:00", "2026-11-23 10:30")
        lab, _, blk = ev.per_window_diary(w, self.diary, "task_or_outside", "day_end")
        self.assertEqual(lab, [None, "A", "A"])
        self.assertNotEqual(blk[1], blk[2])  # 日をまたいだら同じ名前でも別のブロック

    def test_after_last_day_is_none(self):
        lab, _, _ = ev.per_window_diary(self._at("2026-11-24 01:00", "2026-11-22 08:00"), self.diary,
                                        "task_or_outside")
        self.assertEqual(lab, [None, None])


if __name__ == "__main__":
    unittest.main()
