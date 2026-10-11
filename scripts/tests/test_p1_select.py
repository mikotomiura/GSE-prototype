"""Tests for scripts/p1_select.py (grouped nested CV の fold と、fold × 一式 × 極の 3 metric 表・issue 005).

⚠️★★★ **表まで。選ばない。** fold をまたぐ集約・同点の崩し方・最終選択は実装しない (判断 18)。
→ ★ 出力に選択の結果を表すキーが無いこと・列が固定であることを `test_no_selection_output` が見る。

- fold: N 人 → outer N 個 (LOPO)・inner は `min(5, N − 1)` 個の grouped k-fold。決定的で、seed は凍結 JSON から読む。
- 3 metric の素の値 (主: 最小 episode 数と `≥ L`・副: 転帰カテゴリの件数と数・第 3: `pstdev / mean`) を手計算と突き合わせる。
- 規則 (d) の除外は表に入らず `excluded` に載る。ラベルの食い違いは `label_mismatch` に数える。
- PG-1 は転帰を見ない → 未宣言なら、ラベルの中身も格子の中身も読む前に exit 6。

⚠️ 本 module は実データも Rust も読まない。入力は `tempfile` に作る合成の格子出力 (封筒の最小形・`grid_manifest.json` つき) と合成ラベル。
封筒の形は `scripts/p1_features_io.py` の検査 (`check_envelope`) を通る最小のもの。

⚠️★ テスト名の行に `... ok` が同じ行に出ることを acceptance が見る。→ ★ テストに docstring を付けない
(verbose 出力が 2 行に割れる)。★ 標準出力・標準エラーは必ず捕捉する (行の途中に混ざると `... ok` が崩れる)。

実行方法:
    cd GSE-prototype
    PYTHONUTF8=1 python -m unittest scripts.tests.test_p1_select -v
"""

import contextlib
import hashlib
import io
import json
import math
import statistics
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent
REPO_ROOT = SCRIPTS.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import p1_bounds  # noqa: E402
import p1_select as sel  # noqa: E402

POLES = p1_bounds.POLES
FROZEN_PREREG = REPO_ROOT / "src-tauri" / "prereg" / "p1-episode.json"
_ABSENT = object()

WARMUP = {"0.99": 100, "0.995": 200, "0.999": 1000}  # ★ 事前宣言 v1.1 (5) の対応表 (規則 (d) の合成データ用)
# (一式 ID, manifest の kind, q)。⚠️ 実物の格子 (33 一式) ではなく、選択 2 ＋ 感度 1 の小さな合成
CONFIGS = [
    ("sel__q=0.99__hole_gap_ms=2000__t1a_window_ms=30000", "selection", "0.99"),
    ("sel__q=0.995__hole_gap_ms=2000__t1a_window_ms=30000", "selection", "0.995"),
    ("ofat__w_ms=15000", "sensitivity", "0.99"),
]
LABEL_HEADER = "config_id,participant_id,session_id,pole,t0_ms,outcome"
ROW_KEYS = {
    "outer_fold", "inner_fold", "side", "config_id", "role", "pole",
    "n_participants", "n_participants_without_applicable_sessions", "n_participants_lost_to_rule_d",
    "n_not_applicable_sessions", "n_excluded_sessions",
    "min_episodes", "meets_min_episodes", "n_episodes", "n_episodes_unlabeled",
    "outcome_counts", "n_outcome_categories", "episodes_cv",
}  # fmt: skip


def people_of(n):
    return [f"P{i:02d}" for i in range(1, n + 1)]


def layout_n(n, sessions=("s1",)):
    return {participant: list(sessions) for participant in people_of(n)}


def make_envelope(pole, q, warmup, onsets, applicable=True):
    rows = [{"stall_onset": {"is_onset": False}}]
    for t0_ms in onsets:
        rows.append({"stall_onset": {"is_onset": True, "s_ms": max(t0_ms - 500, 0), "t0_ms": t0_ms}})
        rows.append({"stall_onset": {"is_onset": False}})
    return {
        "provenance": {"hmm_version": "0.5.0"},
        "config": {
            "w_ms": 30000, "q": float(q), "b_ms": 30000, "hole_gap_ms": 2000, "warmup_count": warmup, "t1a_window_ms": 30000,
            "pole": pole, "pole_applicable": applicable,
            "pole_not_applicable_reason": None if applicable else "no_modifier_instrument",
            "prereg_id": "p1-episode", "prereg_version": "1.0.0", "prereg_sha256_prefix": "0123456789abcdef",
            "config_source": "frozen", "overrides": [], "hmm_version": "0.5.0",
        },
        "rows": rows,
    }  # fmt: skip


def write_grid(
    directory, layout, onsets_fn=None, applicable_fn=None, warmup_fn=None, excluded=(), configs=CONFIGS,
    envelope_edit=None, manifest_edit=None,
):  # fmt: skip
    """`layout` = `{P-ID: [session, ...]}`。`*_fn(config_id, participant, session, pole)` で単位ごとの中身を振る。

    `excluded` = `[(config_id, participant, session, pole, [reason, ...])]` (manifest の `excluded_rule_d` に載せる)。
    `envelope_edit(config_id, participant, session, pole, envelope)` / `manifest_edit(manifest)` は書く前に中身を直す (sha256 は直した後で取る)。
    """
    directory = Path(directory)
    directory.mkdir(parents=True)
    outputs = []
    for config_id, _kind, q in configs:
        for participant, sessions in layout.items():
            for session in sessions:
                for pole in POLES:
                    key = (config_id, participant, session, pole)
                    onsets = onsets_fn(*key) if onsets_fn else [1000, 2000]
                    applicable = applicable_fn(*key) if applicable_fn else True
                    warmup = warmup_fn(*key) if warmup_fn else None
                    envelope = make_envelope(pole, q, WARMUP[q] if warmup is None else warmup, onsets, applicable)
                    if envelope_edit:
                        envelope_edit(*key, envelope)
                    relative = f"{config_id}/{participant}/{session}/{pole}.json"
                    path = directory / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    data = json.dumps(envelope).encode("utf-8")
                    path.write_bytes(data)
                    outputs.append({"path": relative, "sha256": hashlib.sha256(data).hexdigest()})
    sessions_list = sorted((participant, session) for participant, sessions in layout.items() for session in sessions)
    manifest = {
        "tool": "p1_run_grid",
        "complete": True,
        "prereg_source": "file",
        "prereg_sha256_prefix": "aaaaaaaaaaaaaaaa",
        "envelope_identity": {"prereg_version": "1.0.0", "hmm_version": "0.5.0", "config_source": "frozen"},
        "n_participants": len(layout),
        "n_sessions": len(sessions_list),
        "sessions": [{"participant": participant, "session": session} for participant, session in sessions_list],
        "configs": [{"id": config_id, "kind": kind, "params": {"q": float(q)}} for config_id, kind, q in configs],
        "excluded_rule_d": [
            {"config_id": c, "participant": p, "session": s, "pole": pole, "reasons": reasons, "mismatch": {}}
            for c, p, s, pole, reasons in excluded
        ],
        "outputs": outputs,
    }
    if manifest_edit:
        manifest_edit(manifest)
    (directory / "grid_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return directory


def write_prereg(directory, name, pg1=3, seed=None, mutate=None):
    """凍結 JSON に `pg1` を足しただけの合成の prereg (`pg1=_ABSENT` なら足さない)。"""
    data = json.loads(FROZEN_PREREG.read_text(encoding="utf-8"))
    if pg1 is not _ABSENT:
        data["pg1"] = {"min_episodes_per_participant": pg1}
    if seed is not None:
        data["search_protocol"]["seed"] = seed
    if mutate is not None:
        mutate(data)
    path = Path(directory) / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def unit(outcomes, usable=1, not_applicable=0, excluded=0):
    return {
        "usable_sessions": usable,
        "not_applicable_sessions": not_applicable,
        "excluded_sessions": excluded,
        "outcomes": outcomes,
    }


class SelectCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)  # ★ system の temp の下 (git 管理外)
        self._n = 0

    def new_path(self, name):
        self._n += 1
        return self.tmp / f"{self._n}-{name}"

    def make_grid(self, layout, **kwargs):
        return write_grid(self.new_path("grid"), layout, **kwargs)

    def run_cli(self, argv):
        """CLI を同じプロセスで回し `(exit code, stdout, stderr)` を返す。⚠️ 標準出力・標準エラーは必ず捕捉する。"""
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                rc = sel.main(argv)
            except SystemExit as e:  # argparse の引数不備は exit 2
                rc = e.code
        return rc, stdout.getvalue(), stderr.getvalue()

    def run_select(
        self, grid_dir, label_rows=(), pg1=3, seed=None, mutate=None, labels_text=None, default_prereg=False, out=None,
    ):  # fmt: skip
        """`(rc, 出力 JSON or None, stderr, out のパス)`。`labels_text` を渡すとラベルの CSV をそのまま書く。"""
        labels = self.new_path("labels.csv")
        if labels_text is None:
            labels_text = LABEL_HEADER + "\n" + "".join(",".join(str(v) for v in row) + "\n" for row in label_rows)
        labels.write_text(labels_text, encoding="utf-8", newline="\n")
        out = Path(out) if out is not None else self.new_path("out.json")
        argv = ["--grid-out", str(grid_dir), "--labels", str(labels), "--out", str(out)]
        if not default_prereg:
            prereg = write_prereg(self.tmp, self.new_path("prereg.json").name, pg1, seed, mutate)
            argv += ["--prereg", str(prereg)]
        rc, _stdout, stderr = self.run_cli(argv)
        # ⚠️ 成功したときだけ読む (拒否した run が既存のファイルを上書きしていないことを別に確かめるため)
        result = json.loads(out.read_text(encoding="utf-8")) if rc == 0 and out.exists() else None
        return rc, result, stderr, out

    def ok(self, grid_dir, **kwargs):
        rc, result, stderr, _out = self.run_select(grid_dir, **kwargs)
        self.assertEqual(rc, 0, stderr)
        return result

    def rows(self, result, config_id=None, pole=None, side=None):
        return [
            row
            for row in result["table"]
            if (config_id is None or row["config_id"] == config_id)
            and (pole is None or row["pole"] == pole)
            and (side is None or row["side"] == side)
        ]

    def outer_test_row(self, result, participant, config_id, pole):
        outer = next(fold["outer_fold"] for fold in result["folds"] if fold["test"] == [participant])
        (row,) = [
            r for r in self.rows(result, config_id, pole, "test") if r["outer_fold"] == outer and r["inner_fold"] == "outer_test"
        ]
        return row


class FoldTest(unittest.TestCase):
    def test_folds_structure(self):
        for n, expected_k in ((3, 2), (7, 5), (4, 3), (12, 5)):
            with self.subTest(n=n):
                people = people_of(n)
                folds = sel.make_folds(people, 1)
                self.assertEqual(sel.k_inner(n), expected_k)
                self.assertEqual(len(folds), n)
                # ★ outer は N 個・各 1 人が test (leave-one-participant-out)
                self.assertEqual([fold["test"] for fold in folds], [[p] for p in people])
                for fold in folds:
                    (test,) = fold["test"]
                    self.assertEqual(fold["train"], [p for p in people if p != test])
                    self.assertEqual(len(fold["inner_folds"]), expected_k)
                    validations = []
                    for inner in fold["inner_folds"]:
                        self.assertTrue(inner["train"] and inner["validation"], "空の側がある")
                        # ★ 1 人の参加者が 2 つの側にまたがらない・test の 1 人は inner に一切現れない
                        self.assertFalse(set(inner["train"]) & set(inner["validation"]))
                        self.assertEqual(set(inner["train"]) | set(inner["validation"]), set(fold["train"]))
                        self.assertNotIn(test, inner["train"] + inner["validation"])
                        validations += inner["validation"]
                    # ★ 訓練側の全員がちょうど 1 つの fold の検証側に入る (group が fold をまたがない)
                    self.assertEqual(sorted(validations), fold["train"])
                    sizes = [len(inner["validation"]) for inner in fold["inner_folds"]]
                    self.assertLessEqual(max(sizes) - min(sizes), 1)
        # ⚠️ 3 人未満・重複・整数でない seed は組まない (判断 21)
        for people in (["P01"], ["P01", "P02"], []):
            with self.subTest(people=people):
                with self.assertRaises(sel.InputError):
                    sel.make_folds(people, 1)
        with self.assertRaises(sel.InputError):
            sel.make_folds(["P01", "P02", "P02"], 1)
        for seed in (True, "1", 1.5, None):
            with self.subTest(seed=seed):
                with self.assertRaises(sel.InputError):
                    sel.make_folds(people_of(4), seed)

    def test_folds_deterministic(self):
        people = people_of(7)
        first = sel.make_folds(people, 11)
        self.assertEqual(sel.make_folds(people, 11), first)
        # ★ 入力の並びに依らない
        self.assertEqual(sel.make_folds(list(reversed(people)), 11), first)
        # ★ seed を変えると inner の割り当てが変わる (outer は seed に依らない)
        other = sel.make_folds(people, 12)
        self.assertEqual([fold["test"] for fold in other], [fold["test"] for fold in first])
        self.assertNotEqual([fold["inner_folds"] for fold in other], [fold["inner_folds"] for fold in first])
        # ★ 割り当ては sha256 の並び (`random` の実装に依らない): 版・OS が変わっても同じ fold になることを 1 つ固定する
        self.assertEqual(
            sel.make_folds(["P01", "P02", "P03"], 7)[0]["inner_folds"],
            [
                {"inner_fold": 0, "train": ["P02"], "validation": ["P03"]},
                {"inner_fold": 1, "train": ["P03"], "validation": ["P02"]},
            ],
        )


class MetricsTest(unittest.TestCase):
    def test_metrics_values(self):
        per = {
            "P01": unit(["a", "a", "b", "b"]),  # 4 episode
            "P02": unit(["a", None, "b"]),  # 3 episode (1 つはラベル無し)
            "P03": unit(["b", "b"], not_applicable=1),  # 2 episode
        }
        m = sel.metrics_for(per, ["P01", "P02", "P03"], 3)
        self.assertEqual(m["n_participants"], 3)
        self.assertEqual(m["n_participants_without_applicable_sessions"], 0)
        self.assertEqual(m["n_not_applicable_sessions"], 1)
        # ★ 主: 最小は 2 (P03)・L = 3 には届かない。L = 2 なら「以上」なので届く (境界)
        self.assertEqual(m["min_episodes"], 2)
        self.assertIs(m["meets_min_episodes"], False)
        self.assertIs(sel.metrics_for(per, ["P01", "P02", "P03"], 2)["meets_min_episodes"], True)
        # ★ 副: a = 2 + 1 = 3・b = 2 + 1 + 2 = 5・ラベル無し 1・全 9 episode・カテゴリ 2
        self.assertEqual(m["outcome_counts"], {"a": 3, "b": 5})
        self.assertEqual(m["n_outcome_categories"], 2)
        self.assertEqual((m["n_episodes"], m["n_episodes_unlabeled"]), (9, 1))
        # ★ 第 3: 数 [4, 3, 2]・平均 3・母標準偏差 √(2/3) → 変動係数 √(2/3) / 3
        self.assertAlmostEqual(m["episodes_cv"], math.sqrt(2 / 3) / 3, places=12)

        # ★ 使えるセッションを持たない参加者は metric に入れず、別に数える (⚠️ 0 として最小値を引き下げない)
        per["P04"] = unit([], usable=0, not_applicable=2)
        m4 = sel.metrics_for(per, ["P01", "P02", "P03", "P04"], 3)
        self.assertEqual((m4["n_participants"], m4["n_participants_without_applicable_sessions"]), (4, 1))
        self.assertEqual((m4["min_episodes"], m4["n_not_applicable_sessions"]), (2, 3))
        self.assertAlmostEqual(m4["episodes_cv"], m["episodes_cv"], places=12)
        # 除外されたセッションも数える (episode には入らない)
        per["P05"] = unit([], usable=0, excluded=1)
        self.assertEqual(sel.metrics_for(per, ["P05"], 3)["n_excluded_sessions"], 1)
        # ⚠️ 規則 (d) の除外で使えるセッションを失った参加者は、適用不可だけの参加者と別に数える（★ 最小値からは外れたまま・裁定待ち）
        m5 = sel.metrics_for(per, ["P01", "P04", "P05"], 3)
        self.assertEqual(
            (m5["n_participants_without_applicable_sessions"], m5["n_participants_lost_to_rule_d"], m5["min_episodes"]),
            (2, 1, 4),
        )
        self.assertEqual(m["n_participants_lost_to_rule_d"], 0)

        # ★ 参加者 1 人: 変動係数は None (0 で埋めない)。最小値はその人の数
        one = sel.metrics_for(per, ["P01"], 3)
        self.assertIsNone(one["episodes_cv"])
        self.assertEqual((one["min_episodes"], one["meets_min_episodes"]), (4, True))
        # ★ 平均 0 (episode 0 本の参加者だけ): 変動係数は None。主 metric の最小は 0 で届かない
        zero = sel.metrics_for({"Pa": unit([]), "Pb": unit([])}, ["Pa", "Pb"], 1)
        self.assertIsNone(zero["episodes_cv"])
        self.assertEqual((zero["min_episodes"], zero["meets_min_episodes"], zero["n_episodes"]), (0, False, 0))
        self.assertEqual((zero["outcome_counts"], zero["n_outcome_categories"]), ({}, 0))
        # ★ 数える参加者が 0 人: 最小・真偽・変動係数はすべて None (欠測を 0 で埋めない)
        nobody = sel.metrics_for({"Pa": unit([], usable=0, not_applicable=1)}, ["Pa"], 1)
        self.assertEqual((nobody["min_episodes"], nobody["meets_min_episodes"], nobody["episodes_cv"]), (None, None, None))
        self.assertEqual(nobody["n_participants_without_applicable_sessions"], 1)
        # ★ カテゴリが 1 つだけ = 退化 (件数とカテゴリ数を載せるだけ。判定は載せない)
        degenerate = sel.metrics_for({"Pa": unit(["x", "x"]), "Pb": unit(["x"])}, ["Pa", "Pb"], 1)
        self.assertEqual((degenerate["outcome_counts"], degenerate["n_outcome_categories"]), ({"x": 3}, 1))


class TableTest(SelectCase):
    def test_metrics_in_table_match_hand_computation(self):
        counts = {"P01": 4, "P02": 3, "P03": 2, "P04": 0, "P05": 6, "P06": 5, "P07": 4}
        config_id = CONFIGS[0][0]
        grid_dir = self.make_grid(
            layout_n(7),
            onsets_fn=lambda c, p, s, pole: [1000 * (i + 1) for i in range(counts[p])],
        )
        # ★ ラベルは (一式 0・baseline) だけ。偶数番目は "a"・奇数番目は "b"。P05 の最後の 1 本 (6 本目) はラベルを付けない
        labels = [
            (config_id, p, "s1", "baseline", 1000 * (i + 1), "a" if i % 2 == 0 else "b")
            for p, count in counts.items()
            for i in range(count)
            if not (p == "P05" and i == 5)
        ]
        result = self.ok(grid_dir, label_rows=labels, pg1=3)
        self.assertEqual(result["provenance"]["pg1_min_episodes_per_participant"], 3)

        def expected_outcomes(participant):
            a = sum(1 for i in range(counts[participant]) if i % 2 == 0)
            b = sum(1 for i in range(counts[participant]) if i % 2 == 1)
            if participant == "P05":
                b -= 1
            return a, b

        folds = {fold["outer_fold"]: fold for fold in result["folds"]}
        checked = 0
        for row in self.rows(result, config_id, "baseline"):
            fold = folds[row["outer_fold"]]
            if row["inner_fold"] == "outer_test":
                members = fold["test"]
            else:
                members = fold["inner_folds"][row["inner_fold"]][row["side"]]
            numbers = [counts[p] for p in members]
            self.assertEqual(row["n_participants"], len(members))
            self.assertEqual(row["min_episodes"], min(numbers))
            self.assertIs(row["meets_min_episodes"], min(numbers) >= 3)
            self.assertEqual(row["n_episodes"], sum(numbers))
            a, b = sum(expected_outcomes(p)[0] for p in members), sum(expected_outcomes(p)[1] for p in members)
            self.assertEqual(row["outcome_counts"], {k: v for k, v in (("a", a), ("b", b)) if v})
            self.assertEqual(row["n_outcome_categories"], sum(1 for v in (a, b) if v))
            self.assertEqual(row["n_episodes_unlabeled"], 1 if "P05" in members else 0)
            if len(numbers) < 2 or statistics.mean(numbers) == 0:
                self.assertIsNone(row["episodes_cv"])
            else:
                self.assertAlmostEqual(row["episodes_cv"], statistics.pstdev(numbers) / statistics.mean(numbers), places=12)
            checked += 1
        self.assertEqual(checked, 7 * (2 * 5 + 1))
        # ★ 手で決まる 2 行: P04 (episode 0 本) と P05 (6 本・1 本ラベル無し)
        p04 = self.outer_test_row(result, "P04", config_id, "baseline")
        self.assertEqual((p04["min_episodes"], p04["meets_min_episodes"], p04["n_episodes"]), (0, False, 0))
        self.assertEqual((p04["outcome_counts"], p04["n_outcome_categories"], p04["episodes_cv"]), ({}, 0, None))
        p05 = self.outer_test_row(result, "P05", config_id, "baseline")
        self.assertEqual((p05["min_episodes"], p05["meets_min_episodes"], p05["n_episodes"]), (6, True, 6))
        self.assertEqual((p05["outcome_counts"], p05["n_episodes_unlabeled"]), ({"a": 3, "b": 2}, 1))
        # ★ ラベルは (一式, 極) ごとの鍵: ラベルを付けていない別の一式・別の極では、同じ episode でも全部ラベル無し
        for other_id, other_pole in ((CONFIGS[1][0], "baseline"), (config_id, "pointer_b")):
            other = self.outer_test_row(result, "P05", other_id, other_pole)
            self.assertEqual((other["n_episodes"], other["n_episodes_unlabeled"], other["outcome_counts"]), (6, 6, {}))

    def test_no_selection_output(self):
        grid_dir = self.make_grid(layout_n(7))
        result = self.ok(grid_dir, label_rows=[(CONFIGS[0][0], "P01", "s1", "baseline", 1000, "a")])
        self.assertEqual(set(result), {"provenance", "folds", "table", "excluded", "label_mismatch"})
        self.assertEqual(len(result["table"]), 7 * (2 * 5 + 1) * len(CONFIGS) * len(POLES))
        # ★ 列は固定 (集約・順位・選択の列が紛れ込まない)
        for row in result["table"]:
            self.assertEqual(set(row), ROW_KEYS)
        # ⚠️★★★ 選択の結果を表すキー・値を持たない (キーにも値にも)
        banned = ("selected", "best", "winner", "chosen")
        strings = []

        def walk(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    strings.append(str(key).lower())
                    walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)
            elif isinstance(value, str):
                strings.append(value.lower())

        walk(result)
        self.assertGreater(len(strings), 100)  # ★ 空の走査で緑にならない
        for text in strings:
            for word in banned:
                self.assertNotIn(word, text)
        # ★ `role` 列で、感度の一式は選択の一式と区別される (選択に入れないことが表の上で見える)
        roles = {row["config_id"]: row["role"] for row in result["table"]}
        self.assertEqual(roles, {CONFIGS[0][0]: "selection", CONFIGS[1][0]: "selection", CONFIGS[2][0]: "sensitivity_only"})
        # provenance は seed と PG-1 の値と fold の数を刻む
        provenance = result["provenance"]
        self.assertEqual((provenance["tool"], provenance["k_inner"], provenance["n_participants"]), ("p1_select", 5, 7))
        self.assertEqual(provenance["prereg_source"], "file")
        self.assertRegex(provenance["prereg_sha256_prefix"], r"^[0-9a-f]{16}$")

    def test_exclusions_and_label_mismatch(self):
        cfg0, cfg1, cfg2 = (config[0] for config in CONFIGS)
        layout = layout_n(3)
        grid_dir = self.make_grid(
            layout,
            # (1) 一式 1 (q=0.995 → warmup 200) で P01 の baseline だけ warmup が 100: 規則 (d) に反し、manifest にも載る
            # (3) 一式 2 (q=0.99) の P03 modifier_m_plus は warmup が 200: 規則 (d) に反するが manifest に載っていない
            warmup_fn=lambda c, p, s, pole: 100 if (c, p, pole) == (cfg1, "P01", "baseline") else (
                200 if (c, p, pole) == (cfg2, "P03", "modifier_m_plus") else None
            ),
            # (2) 一式 0 の P02 pointer_b は封筒が有効だが、manifest が param_mismatch で載せている
            excluded=[
                (cfg1, "P01", "s1", "baseline", ["rule_d"]),
                (cfg0, "P02", "s1", "pointer_b", ["param_mismatch"]),
            ],
        )
        labels = [
            (cfg0, "P01", "s1", "baseline", 1000, "a"),  # ★ 対応する episode がある
            (cfg0, "P01", "s1", "baseline", 2000, "b"),  # ★ 同上
            (cfg0, "P01", "s1", "baseline", 9999, "a"),  # ⚠️ onset の無い時刻
            (cfg1, "P01", "s1", "baseline", 1000, "a"),  # ⚠️ 除外された実行の episode は episode ではない
            ("no-such-config", "P01", "s1", "baseline", 1000, "a"),  # ⚠️ 格子に無い一式
        ]
        result = self.ok(grid_dir, label_rows=labels)

        # ★ 除外は表に入らず `excluded` に載る (manifest に載ったもの 2 件 ＋ 封筒から独立に判定し直して見つけた 1 件)
        excluded = {
            (e["config_id"], e["participant"], e["session"], e["pole"]): (e["reasons"], e["listed_in_manifest"])
            for e in result["excluded"]
        }
        self.assertEqual(
            excluded,
            {
                (cfg1, "P01", "s1", "baseline"): (["rule_d"], True),
                (cfg0, "P02", "s1", "pointer_b"): (["param_mismatch"], True),
                (cfg2, "P03", "s1", "modifier_m_plus"): (["rule_d"], False),
            },
        )
        self.assertEqual(len(result["excluded"]), 3)
        keys = [(e["config_id"], e["participant"], e["session"], e["pole"]) for e in result["excluded"]]
        self.assertEqual(keys, sorted(keys), "excluded が決定的な順でない")
        for participant, config_id, pole in (("P01", cfg1, "baseline"), ("P02", cfg0, "pointer_b"), ("P03", cfg2, "modifier_m_plus")):
            row = self.outer_test_row(result, participant, config_id, pole)
            self.assertEqual((row["n_episodes"], row["n_excluded_sessions"]), (0, 1), (participant, config_id, pole))
            self.assertEqual(row["n_participants_without_applicable_sessions"], 1)
            self.assertEqual((row["min_episodes"], row["meets_min_episodes"], row["episodes_cv"]), (None, None, None))
        # 除外されていない同じ参加者・別の一式・別の極は普通に数える
        normal = self.outer_test_row(result, "P01", cfg0, "baseline")
        self.assertEqual((normal["n_episodes"], normal["n_excluded_sessions"], normal["outcome_counts"]), (2, 0, {"a": 1, "b": 1}))
        self.assertEqual(self.outer_test_row(result, "P01", cfg1, "pointer_b")["n_excluded_sessions"], 0)

        # ★ ラベルの食い違いを数える (黙って捨てない)。有効な episode = 3 一式 × 3 極 × 3 人 − 除外 3 = 24 単位 × 2 本 = 48・ラベルは 2 本が対応
        mismatch = result["label_mismatch"]
        self.assertEqual((mismatch["n_labels"], mismatch["labels_without_episode"], mismatch["episodes_without_label"]), (5, 3, 46))
        by = {(item["config_id"], item["pole"]): item for item in mismatch["by_config_pole"]}
        self.assertEqual((by[(cfg0, "baseline")]["labels_without_episode"], by[(cfg0, "baseline")]["episodes_without_label"]), (1, 4))
        self.assertEqual((by[(cfg1, "baseline")]["labels_without_episode"], by[(cfg1, "baseline")]["episodes_without_label"]), (1, 4))
        self.assertEqual(
            (by[("no-such-config", "baseline")]["labels_without_episode"], by[("no-such-config", "baseline")]["episodes_without_label"]),
            (1, 0),
        )
        self.assertEqual(sum(item["labels_without_episode"] for item in mismatch["by_config_pole"]), 3)
        self.assertEqual(sum(item["episodes_without_label"] for item in mismatch["by_config_pole"]), 46)

    def test_folds_shared_and_zero_episode_included(self):
        layout = layout_n(7)
        grid_dir = self.make_grid(layout, onsets_fn=lambda c, p, s, pole: [] if p == "P04" else [1000, 2000])
        # ★ fold は 1 回だけ作る (全一式・全極で同じ fold)
        with mock.patch.object(sel, "make_folds", wraps=sel.make_folds) as spy:
            result = self.ok(grid_dir, pg1=2)  # L = 2: P04 (0 本) を含まない集合だけが下限を満たす
        self.assertEqual(spy.call_count, 1)
        self.assertEqual(spy.call_args.args[0], people_of(7))
        folds = {fold["outer_fold"]: fold for fold in result["folds"]}
        groups = {}
        for row in result["table"]:
            groups.setdefault((row["outer_fold"], row["inner_fold"], row["side"]), []).append(row)
        self.assertEqual(len(groups), 7 * (2 * 5 + 1))
        for (outer, inner, side), rows in groups.items():
            members = folds[outer]["test"] if inner == "outer_test" else folds[outer]["inner_folds"][inner][side]
            # ★ 一式・極が違っても同じ参加者の集合 (行数 = 一式 × 極)
            self.assertEqual(len(rows), len(CONFIGS) * len(POLES))
            self.assertEqual({row["n_participants"] for row in rows}, {len(members)})
            # ★ onset が 0 本の参加者 (P04) も fold に入り、その集合の主 metric の最小値は 0 になる (episode から母集団を作らない)
            self.assertEqual({row["min_episodes"] for row in rows}, {0 if "P04" in members else 2}, (outer, inner, side))
            self.assertEqual({row["meets_min_episodes"] for row in rows}, {"P04" not in members})
        self.assertIn(["P04"], [fold["test"] for fold in result["folds"]])
        p04 = self.outer_test_row(result, "P04", CONFIGS[0][0], "baseline")
        self.assertEqual((p04["min_episodes"], p04["n_participants_without_applicable_sessions"]), (0, 0))

    def test_poles_independent(self):
        cfg = CONFIGS[0][0]
        layout = {"P01": ["s1", "s2"], "P02": ["s1"], "P03": ["s1"]}

        def onsets(pointer_b):
            return lambda c, p, s, pole: pointer_b if pole == "pointer_b" else [1000, 2000]

        def applicable(c, p, s, pole):
            # 修飾キー軸は全部非適用 (⚠️ 実物の出力は baseline と恒等で、onset は載っている)・P01 の s2 だけポインタ軸も非適用
            return pole == "baseline" or (pole == "pointer_b" and (p, s) != ("P01", "s2"))

        first = self.ok(
            self.make_grid(layout, configs=CONFIGS[:1], onsets_fn=onsets([1000, 2000, 3000, 4000, 5000]), applicable_fn=applicable)
        )
        second = self.ok(
            self.make_grid(layout, configs=CONFIGS[:1], onsets_fn=onsets([7000]), applicable_fn=applicable)
        )
        # ★ 極ごとに独立: ポインタ軸の極の入力だけを変えると、その極の行だけが変わる
        for pole in ("baseline", "modifier_m_plus"):
            self.assertEqual(self.rows(first, cfg, pole), self.rows(second, cfg, pole), pole)
        self.assertNotEqual(self.rows(first, cfg, "pointer_b"), self.rows(second, cfg, "pointer_b"))

        base = self.outer_test_row(first, "P02", cfg, "baseline")
        pointer = self.outer_test_row(first, "P02", cfg, "pointer_b")
        self.assertEqual((base["n_episodes"], base["min_episodes"]), (2, 2))
        self.assertEqual((pointer["n_episodes"], pointer["min_episodes"]), (5, 5))
        # ⚠️ 非適用の極は episode 0 本ではなく「使えるセッションなし」: onset が載っていても数えず、件数を別に数える
        modifier = self.outer_test_row(first, "P02", cfg, "modifier_m_plus")
        self.assertEqual((modifier["n_episodes"], modifier["n_not_applicable_sessions"]), (0, 1))
        self.assertEqual(modifier["n_participants_without_applicable_sessions"], 1)
        self.assertEqual((modifier["min_episodes"], modifier["meets_min_episodes"], modifier["episodes_cv"]), (None, None, None))
        # ★ セッションの一部だけが非適用なら、適用可のセッションだけを数え、参加者は残る (P01: s1 = 適用可 5 本・s2 = 非適用)
        p01 = self.outer_test_row(first, "P01", cfg, "pointer_b")
        self.assertEqual((p01["n_episodes"], p01["n_not_applicable_sessions"], p01["n_participants_without_applicable_sessions"]), (5, 1, 0))
        # 同じ参加者の baseline は 2 セッションとも適用可 (2 本ずつ)
        self.assertEqual(self.outer_test_row(first, "P01", cfg, "baseline")["n_episodes"], 4)

        # ★ ラベルも極ごと: pointer_b にだけある時刻のラベルは、baseline では対応する episode が無い
        labels = [
            (cfg, "P02", "s1", "pointer_b", 3000, "a"),  # 対応する
            (cfg, "P02", "s1", "baseline", 3000, "a"),  # baseline に 3000 の onset は無い
            (cfg, "P02", "s1", "modifier_m_plus", 1000, "a"),  # 非適用の極の onset は episode ではない
        ]
        result = self.ok(self.make_grid(layout, configs=CONFIGS[:1], onsets_fn=onsets([1000, 2000, 3000, 4000, 5000]), applicable_fn=applicable), label_rows=labels)
        by = {(item["config_id"], item["pole"]): item["labels_without_episode"] for item in result["label_mismatch"]["by_config_pole"]}
        self.assertEqual(by.get((cfg, "baseline")), 1)
        self.assertEqual(by.get((cfg, "modifier_m_plus")), 1)
        self.assertEqual(by.get((cfg, "pointer_b"), 0), 0)
        self.assertEqual(self.outer_test_row(result, "P02", cfg, "pointer_b")["outcome_counts"], {"a": 1})

    def test_seed_from_prereg(self):
        frozen_seed = json.loads(FROZEN_PREREG.read_text(encoding="utf-8"))["search_protocol"]["seed"]
        people = people_of(7)
        grid_dir = self.make_grid(layout_n(7))
        # ★ seed は prereg の `search_protocol.seed` から読む (書き写さない)
        first = self.ok(grid_dir)
        self.assertEqual(first["provenance"]["seed"], frozen_seed)
        self.assertEqual(first["folds"], sel.make_folds(people, frozen_seed))
        # ★ prereg の seed を変えると追従する
        changed = self.ok(grid_dir, seed=424242)
        self.assertEqual(changed["provenance"]["seed"], 424242)
        self.assertEqual(changed["folds"], sel.make_folds(people, 424242))
        self.assertNotEqual(
            [fold["inner_folds"] for fold in changed["folds"]], [fold["inner_folds"] for fold in first["folds"]]
        )

        def drop_seed(data):
            del data["search_protocol"]["seed"]

        def null_seed(data):
            data["search_protocol"]["seed"] = None

        # ⚠️ 読めない seed は既定値で埋めずに拒否する (exit 3)
        for label, kwargs in (
            ("無い", {"mutate": drop_seed}),
            ("null", {"mutate": null_seed}),
            ("bool", {"seed": True}),
            ("小数", {"seed": 2026.5}),
            ("文字列", {"seed": "20260921"}),
        ):
            with self.subTest(seed=label):
                rc, result, stderr, _out = self.run_select(grid_dir, **kwargs)
                self.assertEqual(rc, 3, stderr)
                self.assertIsNone(result)


class GuardTest(SelectCase):
    def refused(self, rc_expected, grid_dir, label, **kwargs):
        rc, result, stderr, out = self.run_select(grid_dir, **kwargs)
        self.assertEqual(rc, rc_expected, f"{label}: {stderr}")
        self.assertFalse(out.exists(), f"{label}: 拒否したのに出力が作られた")
        self.assertIsNone(result)
        return stderr

    def test_guards(self):
        grid3 = self.make_grid(layout_n(3))
        self.assertEqual(self.run_select(grid3)[0], 0)  # ★ 対照: 同じ入力が通る (下の拒否が別の理由で落ちていないことの裏づけ)

        # ⚠️ PG-1 未宣言 (型・範囲の不正を含む) → 6
        for label, pg1 in (
            ("無い", _ABSENT), ("0", 0), ("-1", -1), ("bool", True), ("文字列", "3"), ("小数", 2.5), ("整数値の小数", 3.0), ("null", None),
        ):  # fmt: skip
            with self.subTest(pg1=label):
                self.refused(6, grid3, f"pg1={label}", pg1=pg1)
        # ★ 現行の凍結 JSON (pg1 無し) は既定では必ず 6
        self.refused(6, grid3, "既定の凍結 JSON", default_prereg=True)
        # ⚠️★★★ PG-1 は転帰を見ない: ラベルの中身が壊れていても・格子が空でも、未宣言なら中身を読む前に 6
        self.refused(6, grid3, "壊れたラベル", pg1=_ABSENT, labels_text="not,a,label,file\n1,2,3,4\n")
        empty_grid = self.new_path("empty-grid")
        empty_grid.mkdir()
        self.refused(6, empty_grid, "空の格子", pg1=_ABSENT)

        # ⚠️ ラベル無し → 2 (引数の不備は argparse の 2)・読めない → 2
        out = self.new_path("no-labels.json")
        rc, _, _ = self.run_cli(["--grid-out", str(grid3), "--out", str(out)])
        self.assertEqual(rc, 2)
        self.assertFalse(out.exists())
        for label, target in (("存在しない", self.new_path("missing.csv")), ("ディレクトリ", self.tmp)):
            with self.subTest(labels=label):
                out = self.new_path("out.json")
                rc, _, err = self.run_cli(["--grid-out", str(grid3), "--labels", str(target), "--out", str(out)])
                self.assertEqual(rc, 2, err)
                self.assertFalse(out.exists())
        # `--grid-out` がディレクトリでない・`--prereg` を読めない → 2 / JSON でない → 3
        labels = self.new_path("labels.csv")
        labels.write_text(LABEL_HEADER + "\n", encoding="utf-8")
        for label, argv, expected in (
            ("grid がファイル", ["--grid-out", str(labels), "--prereg", str(write_prereg(self.tmp, "p-ok.json"))], 2),
            ("prereg が無い", ["--grid-out", str(grid3), "--prereg", str(self.new_path("missing.json"))], 2),
        ):
            with self.subTest(argv=label):
                out = self.new_path("out.json")
                rc, _, err = self.run_cli([*argv, "--labels", str(labels), "--out", str(out)])
                self.assertEqual(rc, expected, err)
                self.assertFalse(out.exists())
        bad_json = self.new_path("bad.json")
        bad_json.write_text("{not json", encoding="utf-8")
        out = self.new_path("out.json")
        rc, _, err = self.run_cli(["--grid-out", str(grid3), "--labels", str(labels), "--prereg", str(bad_json), "--out", str(out)])
        self.assertEqual(rc, 3, err)

        # ⚠️ 参加者が 3 人未満 → 3 (1 人・2 人。手続きを発明しない)
        for n in (1, 2):
            with self.subTest(participants=n):
                self.refused(3, self.make_grid(layout_n(n)), f"{n} 人")

        # ⚠️ `--out` が git の作業ツリーの中 → 2 (何も作らない)・既にあるファイルは上書きしない
        repo = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)  # ★ Windows は .git の読み取り専用で消せないことがある
        self.addCleanup(repo.cleanup)
        repo_dir = Path(repo.name)
        subprocess.run(["git", "init", "-q", str(repo_dir)], check=True, capture_output=True)
        for label, target in (("直下", repo_dir / "o.json"), ("まだ無いディレクトリの下", repo_dir / "a" / "b" / "o.json")):
            with self.subTest(out=label):
                self.refused(2, grid3, f"--out {label}", out=target)
        self.assertFalse((repo_dir / "a").exists())  # ★ 拒否するときにディレクトリを作らない
        existing = self.new_path("existing.json")
        existing.write_text("keep", encoding="utf-8")
        rc, _, _err, _ = self.run_select(grid3, out=existing)
        self.assertEqual(rc, 2)
        self.assertEqual(existing.read_text(encoding="utf-8"), "keep")

    def test_guards_grid_manifest(self):
        layout = layout_n(3)
        # ⚠️ manifest が complete: true でない → 3
        self.refused(3, self.make_grid(layout, manifest_edit=lambda m: m.update(complete=False)), "complete: false")
        self.refused(3, self.make_grid(layout, manifest_edit=lambda m: m.update(complete="true")), "complete が bool でない")
        self.refused(3, self.make_grid(layout, manifest_edit=lambda m: m.update(tool="other")), "別の tool")
        missing = self.make_grid(layout)
        (missing / "grid_manifest.json").unlink()
        self.refused(3, missing, "manifest が無い")
        # ⚠️ 列挙されたファイルの sha256 が合わない / ファイルが無い → 3
        tampered = self.make_grid(layout)
        target = tampered / CONFIGS[0][0] / "P01" / "s1" / "baseline.json"
        target.write_text(json.dumps(make_envelope("baseline", "0.99", 100, [1000, 2000, 3000])), encoding="utf-8")
        self.refused(3, tampered, "sha256 不一致")
        removed = self.make_grid(layout)
        (removed / CONFIGS[1][0] / "P02" / "s1" / "pointer_b.json").unlink()
        self.refused(3, removed, "列挙されたファイルが無い")
        # ⚠️ 列挙が configs × sessions × 極と一致しない / 参加者数が合わない → 3
        self.refused(3, self.make_grid(layout, manifest_edit=lambda m: m["outputs"].pop()), "列挙が欠けている")
        self.refused(3, self.make_grid(layout, manifest_edit=lambda m: m["outputs"].append({"path": "x/y.json", "sha256": "0" * 64})), "余分な列挙")
        self.refused(3, self.make_grid(layout, manifest_edit=lambda m: m.update(n_participants=4)), "n_participants が合わない")
        # ⚠️ manifest の事前宣言の欄は形を検査する（frozen / file・16 桁の 16 進）
        self.refused(3, self.make_grid(layout, manifest_edit=lambda m: m.update(prereg_source="other")), "prereg_source が知らない値")
        self.refused(3, self.make_grid(layout, manifest_edit=lambda m: m.update(prereg_sha256_prefix=None)), "prereg_sha256_prefix が null")
        self.refused(3, self.make_grid(layout, manifest_edit=lambda m: m.update(prereg_sha256_prefix="XYZ")), "prereg_sha256_prefix の形が違う")
        # ⚠️★★★ 格子を repo の凍結 JSON で回した（frozen）のに、別の hash の事前宣言で評価するのは拒否する（出力は書かれない）
        self.refused(3, self.make_grid(layout, manifest_edit=lambda m: m.update(prereg_source="frozen")), "frozen の格子を別の事前宣言で評価")
        # ★ 対照: 同じバイト列の事前宣言（run_select が既定で書くもの）なら frozen でも通る（上の拒否が別の理由でないことの裏づけ）
        same_sha = sel.grid.load_prereg(write_prereg(self.tmp, "same-sha.json", 3))[1]
        frozen_ok = self.make_grid(layout, manifest_edit=lambda m: m.update(prereg_source="frozen", prereg_sha256_prefix=same_sha))
        result = self.ok(frozen_ok)
        self.assertEqual(result["provenance"]["grid_prereg_source"], "frozen")
        self.refused(
            3,
            self.make_grid(layout, excluded=[("no-such-config", "P01", "s1", "baseline", ["rule_d"])]),
            "知らない実行を除外している",
        )

        # ★ 列挙されていないファイルは読まない: 壊れた封筒・余計なファイルが格子の中にあっても、結果は変わらない
        clean = self.ok(self.make_grid(layout))
        noisy_dir = self.make_grid(layout)
        (noisy_dir / CONFIGS[0][0] / "P01" / "s1" / "extra.json").write_text("{not json", encoding="utf-8")
        (noisy_dir / CONFIGS[0][0] / "P01" / "s1" / ".all-poles.lock").write_text("", encoding="utf-8")
        (noisy_dir / "junk.txt").write_text("garbage", encoding="utf-8")
        self.assertEqual(self.ok(noisy_dir)["table"], clean["table"])

        # ⚠️ 封筒の中身: onset なのに t0_ms が無い・整数でない・重複している → 3
        def edit_onset(mutation):
            def edit(config_id, participant, session, pole, envelope):
                if (config_id, participant, pole) == (CONFIGS[0][0], "P01", "baseline"):
                    mutation(envelope["rows"][1]["stall_onset"])

            return edit

        for label, mutation in (
            ("t0_ms が無い", lambda onset: onset.pop("t0_ms")),
            ("t0_ms が小数", lambda onset: onset.update(t0_ms=1000.5)),
            ("t0_ms が bool", lambda onset: onset.update(t0_ms=True)),
            ("t0_ms が負", lambda onset: onset.update(t0_ms=-1)),
            ("t0_ms が重複", lambda onset: onset.update(t0_ms=2000)),
        ):
            with self.subTest(envelope=label):
                self.refused(3, self.make_grid(layout, envelope_edit=edit_onset(mutation)), label)

    def test_guards_labels(self):
        grid3 = self.make_grid(layout_n(3))
        key = (CONFIGS[0][0], "P01", "s1", "baseline", 1000)
        # ⚠️ 同じキーの行が 2 本以上 → 3 (outcome が同じでも違っても)。t0_ms の表記ゆれ (007 と 7) も同じキー
        self.refused(3, grid3, "同じ outcome の重複", label_rows=[(*key, "a"), (*key, "a")])
        self.refused(3, grid3, "違う outcome の重複", label_rows=[(*key, "a"), (*key, "b")])
        self.refused(3, grid3, "t0_ms の表記ゆれ", label_rows=[(*key[:4], "1000", "a"), (*key[:4], "01000", "b")])
        # ★ キーの一部が違えば別の episode (一式・参加者・セッション・極・時刻のどれかが違う)
        distinct = [(*key, "a"), (CONFIGS[1][0], *key[1:], "a"), (key[0], "P02", *key[2:], "a"), (*key[:3], "pointer_b", 1000, "a"), (*key[:4], 2000, "a")]
        self.assertEqual(self.ok(grid3, label_rows=distinct)["label_mismatch"]["n_labels"], 5)
        # ⚠️ ヘッダ・列数・空の項目・t0_ms の形が違う → 3
        for label, text in (
            ("ヘッダが違う", "config_id,participant_id,session_id,pole,t0_ms\nx,P01,s1,baseline,1000\n"),
            ("空のファイル", ""),
            ("列が多い", LABEL_HEADER + f"\n{CONFIGS[0][0]},P01,s1,baseline,1000,a,extra\n"),
            ("列が少ない", LABEL_HEADER + f"\n{CONFIGS[0][0]},P01,s1,baseline,1000\n"),
            ("outcome が空", LABEL_HEADER + f"\n{CONFIGS[0][0]},P01,s1,baseline,1000,\n"),
            ("t0_ms が小数", LABEL_HEADER + f"\n{CONFIGS[0][0]},P01,s1,baseline,1000.5,a\n"),
            ("t0_ms が負", LABEL_HEADER + f"\n{CONFIGS[0][0]},P01,s1,baseline,-1,a\n"),
            ("t0_ms が空", LABEL_HEADER + f"\n{CONFIGS[0][0]},P01,s1,baseline,,a\n"),
        ):
            with self.subTest(labels=label):
                self.refused(3, grid3, label, labels_text=text)
        # 空行・BOM つきは許す / 見出しだけ (ラベル 0 本) も許す (全 episode がラベル無しになる)
        self.assertEqual(self.ok(grid3, labels_text="﻿" + LABEL_HEADER + "\n\n")["label_mismatch"]["n_labels"], 0)


if __name__ == "__main__":
    unittest.main()
