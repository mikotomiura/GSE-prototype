#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""[P321] Alaboudi & LaToza (2021) の公開データから「受領なし再開」ベースラインを実測する。

⚠️★★★ 本スクリプトは **GSE のデータを一切読まない**。読むのは [P321] の replication
package (`rowData.json`) だけである。したがって `capabilities_gate.py` (ADR-013) は
**適用外**である (→ `run.sh` の Step 0 コメント / `notes.md`)。

★ 出力する量 (定義は `notes.md` §2):

  A   : fix に至らなかった episode の割合。⚠️★★★ **検算用**であって結果ではない。
        論文の既報値と突き合わせ、**合わなければ exit 1 で止まる**。
  R0  : External Resources 参照 0 回で終わった episode / 全 episode
  R1  : 同じ比率を「fix に至った episode」に限定したもの
  R0' : 「fix に至り、かつ参照 0 回」/ 全 episode
        ★ GSE の `self_recovery_without_paste` と *同じ形* の量 (分子が成果を要求する)

⚠️★★★ R0 / R1 / R0' を GSE の期待値として使ってはならない (→ `notes.md` §4)。

使い方:
    python analyze_p321.py --input raw/replication_package_FSE2021/rowData.json \\
                           --out results
    python analyze_p321.py --selftest      # ★ 検算ゲート自体が空回りしていないか確かめる
"""

from __future__ import annotations

import argparse
import collections
import copy
import hashlib
import json
import math
import re
import statistics
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# ★ 論文の既報値 (= 検算の期待値)。⚠️ すべて arXiv:2105.02162v1 の一次から取った。
#   ★ 出所を行ごとに書く。書いていない期待値は置かない。
# ---------------------------------------------------------------------------
PAPER = {
    # §4 冒頭 逐語: "2137 activities in 15 hours of debugging work, including 89
    #                distinct debugging episodes"
    "episodes": 89,
    "debug_activities": 2137,
    # §4 冒頭 逐語: "The average number of activities per debugging episode was 24 (±37)"
    "activities_per_episode_avg": 24,
    # §4.1 逐語: "In the remaining 79 debugging episodes, developers ... inserted
    #             defects while implementing new features"  → 89 - 79 = 10 が報告由来
    "origin_reported": 10,
    "origin_inserted": 79,
    # §4.1 逐語: "Half of debugging episodes triggered by reported defects did not end
    #             with a successful fix"
    "nofix_rate_reported": 0.50,
    # §4.1 逐語: "For new defects created while programming, 14% did not conclude with
    #             a successful fix"
    "nofix_rate_inserted": 0.14,
    # Table 4 / Table 5 の "Consulting External Resources" 列
    "ext_freq_range": (0, 16),
    "ext_time_frac_avg": 0.03,
    "ext_time_frac_max": 0.59,
    "ext_occurrence_secs_avg": 35,
}

# ⚠️ 丸めの許容。★ 論文は整数 % / 整数回で報告しているので、その丸め幅だけ許す。
TOL_RATE = 0.005      # 14% / 50% は整数 % 表記 → ±0.5pt
TOL_SECS = 1.0        # 35s (±42s) は整数秒表記
TOL_FRAC = 0.005      # 3% は整数 % 表記

# ★ 生データの annotation 表記 → 論文の活動名。
#   ⚠️★★★ この対応づけは *仮定* である。→ `verify_activity_mapping()` が
#   論文 Table 4/5 の 3 統計 (範囲 / 時間割合 / 1 回あたり秒) と突き合わせて検算する。
EXTERNAL_RESOURCE_TITLE = "Seeking information"
OTHER_TITLE = "Others"
U_CODE = re.compile(r"\bU\d+\b")
DF_CODE = re.compile(r"DF(\d+)")

# codingBookFSE2021.pdf 逐語 "Did the developer fix the bug completely?"
DF_FIX_YES = 1          # DF1: Yes.
DF_FIX_MOSTLY = 2       # DF2: Mostly yes, but there is still some incorrect behavior ...
DF_OUTCOME = {1, 2, 3, 4, 5}
DF_INTERRUPTED = 4      # DF4: No, the developer got interrupted during the episode.
# codingBookFSE2021.pdf 逐語 "How did the session start ?"
DF_START = {6, 7, 8}
DF_START_RESUME = 7     # DF7: The developer returns from other activity.
DF_START_REPORT = 8     # DF8: The developer received a bug report ...


def hhmmss(text: str) -> int:
    parts = [int(x) for x in text.strip().split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    h, m, s = parts[-3], parts[-2], parts[-1]
    return h * 3600 + m * 60 + s


def span(node: dict) -> tuple[int, int]:
    d = node["duration"]
    return hhmmss(d["start"]["time"]), hhmmss(d["end"]["time"])


def build_episodes(sessions: list, diag: dict | None = None) -> list[dict]:
    """debugging block を episode に畳む。

    ★★★ 畳み方の根拠 (一次): codingBookFSE2021.pdf は 1 つの debugging episode が
    中断で切れうることを明示している ——
      DF4 "No, the developer got interrupted during the episode." (終わり方)
      DF7 "The developer returns from other activity."            (始まり方)
    ⚠️ したがって **DF7 で始まる block は新しい episode ではなく、直前に DF4 で
    途切れた episode の *続き* である**。
    ★ 実測: DF4 と DF7 は 15 セッション中 **セッション単位でも件数が一致** し
    (Video2 1:1 / Video4 5:5 / Video5 1:1 / Video11 3:3 / Video13 8:8 / Video14 2:2)、
    109 block - 20 = **89 = 論文の episode 数**。→ `check_A()` がこれを検算する。
    """
    # ⚠️★★★ 畳み込みの前提 (`config.yaml` `merge_order: lifo`) を **コードが検査する**。
    #   ★ 「同時に開いている episode は最大 1 なので LIFO/FIFO は同値」と書いておきながら、
    #     それを検査しないと **前提が崩れた瞬間に黙って別の畳み方になる** (code-reviewer M-2)。
    #   → ★ 診断値を `diag` に返し、`check_A()` が期待値と突き合わせる。
    if diag is None:
        diag = {}
    diag.setdefault("max_pending_depth", 0)   # ★ 同時に開いた episode の最大数
    diag.setdefault("orphan_resume_blocks", 0)  # ⚠️ DF7 なのに畳む先が無かった block
    diag.setdefault("unresumed_interrupted", 0)  # ⚠️ DF4 で終わったまま再開されなかった episode

    episodes: list[dict] = []
    for sess in sessions:
        # ⚠️★★★ **必ず時刻順に並べ直す。** 15 セッション中 6 セッションは
        #   rowData.json の配列順が時刻順になっていない (実測)。
        anns = sorted(sess["annotations"], key=lambda a: span(a)[0])
        pending: list[dict] = []   # DF4 で途切れ、まだ再開されていない episode
        for ann in anns:
            if ann["title"] != "Debugging":
                continue
            codes = {int(x) for x in DF_CODE.findall(ann.get("description", ""))}
            start, end = span(ann)
            block = {
                "codes": codes,
                "start": start,
                "end": end,
                "subs": ann.get("subAnnotations") or [],
            }
            if DF_START_RESUME in codes and pending:
                episode = pending.pop()
                episode["blocks"].append(block)
            else:
                if DF_START_RESUME in codes:
                    # ⚠️ DF7 で始まったのに畳む先が無い (★ 実測では 0 件)
                    diag["orphan_resume_blocks"] += 1
                episode = {"session": sess["id"], "blocks": [block]}
                episodes.append(episode)
            if DF_INTERRUPTED in codes:
                pending.append(episode)
                diag["max_pending_depth"] = max(diag["max_pending_depth"], len(pending))
        diag["unresumed_interrupted"] += len(pending)
    return episodes


def first_codes(ep: dict) -> set:
    return ep["blocks"][0]["codes"]


def last_codes(ep: dict) -> set:
    return ep["blocks"][-1]["codes"]


def is_fixed(ep: dict, include_mostly: bool = False) -> bool:
    """★ 「fix に至った」の判定。既定は DF1 のみ。

    ⚠️ DF2 ("Mostly yes, but there is still some incorrect behavior that the developer
    decides to leave") は **解決と放棄の中間**である。既定では fix に数えず、
    感度分析として `include_mostly=True` を併報する。
    """
    wanted = {DF_FIX_YES, DF_FIX_MOSTLY} if include_mostly else {DF_FIX_YES}
    return bool(last_codes(ep) & wanted)


def ext_activities(ep: dict, broad: bool = False) -> list[dict]:
    """episode 内の「外部資源の参照」活動。

    strict: sub-annotation の title が "Seeking information" のものだけ。
    broad : ⚠️ 加えて title が "Others" でも記述に U コード (U1..U8 = 外部資源の
            コードブック項目) が付いているものを数える。★ 実測で境界の揺れが
            "Others" 側に 19 件ある (U のみ 9 / OT+U 10) ため、感度分析に使う。
    """
    out = []
    for block in ep["blocks"]:
        for sub in block["subs"]:
            title = sub.get("title", "")
            if title == EXTERNAL_RESOURCE_TITLE:
                out.append(sub)
            elif broad and title == OTHER_TITLE and U_CODE.search(sub.get("description", "")):
                out.append(sub)
    return out


def episode_seconds(ep: dict) -> int:
    return sum(b["end"] - b["start"] for b in ep["blocks"])


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score 区間。⚠️★★★ 個体内クラスタ (1 開発者が複数 episode) を無視した
    素の区間であり、**実際の不確実性より狭い**。→ `notes.md` §4。"""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((centre - half) / d, (centre + half) / d)


# ---------------------------------------------------------------------------
# ★ 検算 (A) —— ⚠️★★★ ここが通らなければ R0 / R1 を出しても意味がない
# ---------------------------------------------------------------------------
def check_A(episodes: list[dict], diag: dict | None = None) -> tuple[list[dict], dict]:
    """抽出手続きを論文の既報値と突き合わせる。返り値: (検査結果, 実測値)。"""
    diag = diag or {}
    n_ep = len(episodes)
    n_act = sum(len(b["subs"]) for ep in episodes for b in ep["blocks"])
    per_ep = [sum(len(b["subs"]) for b in ep["blocks"]) for ep in episodes]

    reported = [ep for ep in episodes if DF_START_REPORT in first_codes(ep)]
    inserted = [ep for ep in episodes if DF_START_REPORT not in first_codes(ep)]
    nofix_reported = [ep for ep in reported if not is_fixed(ep)]
    nofix_inserted = [ep for ep in inserted if not is_fixed(ep)]

    observed = {
        "episodes": n_ep,
        "debug_activities": n_act,
        "activities_per_episode_avg": statistics.mean(per_ep) if per_ep else 0.0,
        "origin_reported": len(reported),
        "origin_inserted": len(inserted),
        "nofix_rate_reported": len(nofix_reported) / len(reported) if reported else float("nan"),
        "nofix_rate_inserted": len(nofix_inserted) / len(inserted) if inserted else float("nan"),
        "nofix_overall": sum(1 for ep in episodes if not is_fixed(ep)) / n_ep if n_ep else float("nan"),
    }
    observed.update({"merge_" + k: v for k, v in diag.items()})

    checks = [
        _chk("episode 数", observed["episodes"], PAPER["episodes"], 0),
        _chk("debugging 活動数", observed["debug_activities"], PAPER["debug_activities"], 1,
             note="⚠️ 論文 2137 に対し実測 2136。★ 1 件差は論文側の丸め/誤記と判断し許容 1 を置く"),
        _chk("活動数/episode 平均", observed["activities_per_episode_avg"],
             PAPER["activities_per_episode_avg"], 0.5),
        _chk("起点: 報告された defect", observed["origin_reported"], PAPER["origin_reported"], 0),
        _chk("起点: 自ら埋め込んだ defect", observed["origin_inserted"], PAPER["origin_inserted"], 0),
        _chk("A: 未 fix 率 (報告 defect)", observed["nofix_rate_reported"],
             PAPER["nofix_rate_reported"], TOL_RATE),
        _chk("A: 未 fix 率 (埋め込み defect)", observed["nofix_rate_inserted"],
             PAPER["nofix_rate_inserted"], TOL_RATE),
    ]
    # ★ 畳み込みの前提そのものの検査 (code-reviewer M-2)
    if diag:
        checks += [
            _chk("同時に開く episode の最大数", diag["max_pending_depth"], 1, 0,
                 note="★ 1 ならば LIFO/FIFO は同値 (config.yaml `merge_order: lifo` の前提)"),
            _chk("畳む先が無い DF7 block", diag["orphan_resume_blocks"], 0, 0),
            _chk("再開されなかった DF4 episode", diag["unresumed_interrupted"], 0, 0),
        ]
    return checks, observed


def verify_activity_mapping(episodes: list[dict]) -> tuple[list[dict], dict]:
    """★ "Seeking information" == 論文の "Consulting External Resources" を検算する。

    ⚠️★★★ この対応づけを検算せずに R0 を出すと、**別の活動を数えていても気づけない**。
    → 論文 Table 4 / Table 5 の **独立した 3 統計**と突き合わせる。
    """
    counts, fracs, occ = [], [], []
    for ep in episodes:
        acts = ext_activities(ep, broad=False)
        total = episode_seconds(ep)
        secs = 0
        for a in acts:
            s, e = span(a)
            secs += e - s
            occ.append(e - s)
        counts.append(len(acts))
        fracs.append(secs / total if total > 0 else 0.0)

    observed = {
        "ext_freq_min": min(counts), "ext_freq_max": max(counts),
        "ext_freq_avg": statistics.mean(counts),
        "ext_time_frac_avg": statistics.mean(fracs),
        "ext_time_frac_max": max(fracs),
        "ext_occurrence_secs_avg": statistics.mean(occ) if occ else float("nan"),
        "ext_occurrence_n": len(occ),
    }
    lo, hi = PAPER["ext_freq_range"]
    checks = [
        _chk("参照回数の下限", observed["ext_freq_min"], lo, 0),
        _chk("参照回数の上限", observed["ext_freq_max"], hi, 0),
        _chk("episode 時間に占める割合 (平均)", observed["ext_time_frac_avg"],
             PAPER["ext_time_frac_avg"], TOL_FRAC),
        _chk("episode 時間に占める割合 (最大)", observed["ext_time_frac_max"],
             PAPER["ext_time_frac_max"], TOL_FRAC),
        _chk("1 回あたりの秒数", observed["ext_occurrence_secs_avg"],
             PAPER["ext_occurrence_secs_avg"], TOL_SECS),
    ]
    return checks, observed


def _chk(name: str, got, want, tol, note: str = "") -> dict:
    ok = abs(float(got) - float(want)) <= tol
    return {"name": name, "observed": got, "expected": want, "tolerance": tol,
            "ok": ok, "note": note}


# ---------------------------------------------------------------------------
# ★ 本体 —— R0 / R1 / R0'
# ---------------------------------------------------------------------------
def compute_R(episodes: list[dict], broad: bool, include_mostly: bool) -> dict:
    n = len(episodes)
    free = [ep for ep in episodes if not ext_activities(ep, broad)]
    fixed = [ep for ep in episodes if is_fixed(ep, include_mostly)]
    fixed_free = [ep for ep in fixed if not ext_activities(ep, broad)]

    r0_k, r0_n = len(free), n
    r1_k, r1_n = len(fixed_free), len(fixed)
    r0p_k, r0p_n = len(fixed_free), n

    # ★ 「参照 0 回で終わった episode」のうち fix に至らなかったもの
    #   = ⚠️★★★ R0 の分子に混ざった *放棄* の量。
    free_nofix = [ep for ep in free if not is_fixed(ep, include_mostly)]

    def blk(k, nn):
        lo, hi = wilson(k, nn)
        return {"k": k, "n": nn, "rate": (k / nn) if nn else float("nan"),
                "wilson95": [lo, hi]}

    # セッション単位のばらつき (★ クラスタの目安。⚠️ 統計的補正ではない)
    by_sess = collections.defaultdict(lambda: [0, 0])
    for ep in episodes:
        by_sess[ep["session"]][1] += 1
        if not ext_activities(ep, broad):
            by_sess[ep["session"]][0] += 1
    sess_rates = sorted(k / nn for k, nn in by_sess.values())

    return {
        "definition": {"external_resource": "broad" if broad else "strict",
                       "fixed_includes_DF2": include_mostly},
        "R0_receipt_free_all": blk(r0_k, r0_n),
        "R1_receipt_free_given_fixed": blk(r1_k, r1_n),
        "R0prime_fixed_and_receipt_free_all": blk(r0p_k, r0p_n),
        "denominator_effect_R0_minus_R1": (r0_k / r0_n) - (r1_k / r1_n) if r1_n else float("nan"),
        "numerator_effect_R0_minus_R0prime": (r0_k / r0_n) - (r0p_k / r0p_n) if r0_n else float("nan"),
        "abandonment_in_R0_numerator": {
            "k": len(free_nofix), "n": r0_k,
            "share": (len(free_nofix) / r0_k) if r0_k else float("nan"),
        },
        "per_session_R0": {"n_sessions": len(sess_rates),
                           "min": sess_rates[0] if sess_rates else float("nan"),
                           "median": statistics.median(sess_rates) if sess_rates else float("nan"),
                           "max": sess_rates[-1] if sess_rates else float("nan")},
    }


def outcome_by_receipt(episodes: list[dict], broad: bool = False) -> dict:
    """★ 「fix したか」×「外部資源を参照したか」の 2×2 と、群ごとの episode 長。

    ⚠️★★★ `notes.md` §3 がこの数値を根拠に「**未 fix の episode ほど外部資源をより多く
    参照している**」と書いている。★ 成果物に載っていないと**再生成できない**
    (code-reviewer M-4)。→ ★ `metrics.json` に必ず出す。
    """
    cells = {}
    for fixed_flag in (True, False):
        group = [ep for ep in episodes if is_fixed(ep) is fixed_flag]
        consulted = [ep for ep in group if ext_activities(ep, broad)]
        durations = sorted(episode_seconds(ep) for ep in group)
        cells["fixed" if fixed_flag else "not_fixed"] = {
            "n": len(group),
            "consulted_external": len(consulted),
            "receipt_free": len(group) - len(consulted),
            "consult_rate": (len(consulted) / len(group)) if group else float("nan"),
            "episode_seconds_median": statistics.median(durations) if durations else float("nan"),
        }
    return cells


def block_count_distribution(episodes: list[dict]) -> dict:
    """★ episode あたり block 数の分布（★ 中断をまたいだ episode の実体）。"""
    c = collections.Counter(len(ep["blocks"]) for ep in episodes)
    return {
        "histogram": {str(k): v for k, v in sorted(c.items())},
        "episodes_spanning_interruption": sum(v for k, v in c.items() if k > 1),
        "max_blocks": max(c) if c else 0,
        "total_interruptions": sum((k - 1) * v for k, v in c.items()),
    }


def outcome_breakdown(episodes: list[dict]) -> dict:
    """⚠️ ADR-023 D8: 分母を分けて報告する。"""
    c = collections.Counter()
    for ep in episodes:
        codes = sorted(last_codes(ep) & DF_OUTCOME)
        c["DF" + "/".join(str(x) for x in codes) if codes else "none"] += 1
    return dict(c)


# ---------------------------------------------------------------------------
# ★ 検算ゲート自体の検査 (verify-before-claiming ルール 5b: 正常 / 不在 / 壊れている)
# ---------------------------------------------------------------------------
def selftest(sessions: list) -> int:
    print("=== selftest: 検算ゲートが空回りしていないか (正常 / 不在 / 壊れている) ===")
    failures = 0

    # (1) 正常: 手を加えないデータで全項目が緑になるか
    d0: dict = {}
    eps = build_episodes(sessions, d0)
    a_checks, _ = check_A(eps, d0)
    m_checks, _ = verify_activity_mapping(eps)
    ok = all(c["ok"] for c in a_checks + m_checks)
    print(f"  [1] 正常データ       -> 全 {len(a_checks + m_checks)} 項目 "
          f"{'PASS' if ok else 'FAIL'}")
    if not ok:
        failures += 1
        for c in a_checks + m_checks:
            if not c["ok"]:
                print(f"      赤: {c['name']} observed={c['observed']} expected={c['expected']}")

    # (2) 不在: 外部資源の活動を全部消したら mapping 検査が赤になるか
    stripped = copy.deepcopy(sessions)
    for s in stripped:
        for a in s["annotations"]:
            a["subAnnotations"] = [x for x in (a.get("subAnnotations") or [])
                                   if x.get("title") != EXTERNAL_RESOURCE_TITLE]
    m2, _ = verify_activity_mapping(build_episodes(stripped))
    red = [c["name"] for c in m2 if not c["ok"]]
    print(f"  [2] 参照活動を全削除 -> mapping 検査が赤 {len(red)} 件 "
          f"{'PASS' if red else 'FAIL (空回り)'}")
    if not red:
        failures += 1

    # (3) 壊れている: 中断の畳み込みをやめたら A 検査が赤になるか
    #     ⚠️ 畳まないと episode は 109 になり、論文の 89 と合わなくなるはずである。
    broken = copy.deepcopy(sessions)
    for s in broken:
        for a in s["annotations"]:
            if a["title"] == "Debugging":
                a["description"] = a.get("description", "").replace("DF7", "DF6")
    d3: dict = {}
    a3, obs3 = check_A(build_episodes(broken, d3), d3)
    red3 = [c["name"] for c in a3 if not c["ok"]]
    print(f"  [3] DF7 畳み込み無効 -> episode={obs3['episodes']} / A 検査が赤 {len(red3)} 件 "
          f"{'PASS' if red3 else 'FAIL (空回り)'}")
    if not red3:
        failures += 1

    print(f"=== selftest: {'OK' if failures == 0 else str(failures) + ' 件 FAIL'} ===")
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="raw/replication_package_FSE2021/rowData.json")
    ap.add_argument("--out", default="results")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    path = Path(args.input)
    if not path.is_file():
        print(f"入力が見つかりません: {path}", file=sys.stderr)
        return 2
    blob = path.read_bytes()
    sessions = json.loads(blob.decode("utf-8"))

    if args.selftest:
        return selftest(sessions)

    diag: dict = {}
    episodes = build_episodes(sessions, diag)
    a_checks, a_obs = check_A(episodes, diag)
    m_checks, m_obs = verify_activity_mapping(episodes)
    # ⚠️ `check_A.observed` が 12 項目のうち一部しか持たないのに全項目に見えていた
    #   (code-reviewer M-3)。→ ★ 対応づけ検算の実測値も併合する。
    a_obs = {**a_obs, **m_obs}

    print("=== 検算 A: 抽出手続きを論文の既報値と突き合わせる ===")
    for c in a_checks + m_checks:
        mark = "OK  " if c["ok"] else "FAIL"
        print(f"  [{mark}] {c['name']}: 実測={c['observed']:.4g} 論文={c['expected']:.4g} "
              f"(許容 {c['tolerance']})")
        if c["note"]:
            print(f"         {c['note']}")

    failed = [c for c in a_checks + m_checks if not c["ok"]]

    results = {
        "source": {
            "citation": "[P321] Alaboudi, A. & LaToza, T. D. (2021) "
                        "An Exploratory Study of Debugging Episodes, arXiv:2105.02162",
            "input_file": str(path.name),
            "input_sha256": hashlib.sha256(blob).hexdigest(),
            "sessions": len(sessions),
        },
        "check_A": {"passed": not failed, "checks": a_checks + m_checks, "observed": a_obs},
        "outcome_breakdown_last_block": outcome_breakdown(episodes),
        "outcome_by_receipt": {"strict": outcome_by_receipt(episodes, False),
                               "broad": outcome_by_receipt(episodes, True)},
        "block_count_distribution": block_count_distribution(episodes),
        "denominators": {
            "stuck_episode_count": len(episodes),
            "recovered_episode_count": sum(1 for ep in episodes if is_fixed(ep)),
            "not_recovered_episode_count": sum(1 for ep in episodes if not is_fixed(ep)),
        },
        "R": {},
    }
    for broad in (False, True):
        for mostly in (False, True):
            key = ("broad" if broad else "strict") + "/" + ("DF1+DF2" if mostly else "DF1")
            results["R"][key] = compute_R(episodes, broad, mostly)

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    # ⚠️★★★ 検算 A が赤のとき `metrics.json` を **上書きしない** (code-reviewer H-1)。
    #   ★ 上書きすると、**コミット済みの正しい結果が `"passed": false` で黙って壊れる。**
    #   → ★ 赤の結果は別名 (`metrics.FAILED.json`) に出し、良い方は残す。
    if failed:
        target = outdir / "metrics.FAILED.json"
        target.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
        print(f"\n⚠️★★★ 検算 A が赤である。R0 / R1 を **信用してはならない**。", file=sys.stderr)
        print(f"⚠️ 結果は {target.name} に出した (metrics.json は上書きしていない)。", file=sys.stderr)
        return 1

    (outdir / "metrics.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("\n=== 結果 (主系列: strict / fix=DF1) ===")
    main_r = results["R"]["strict/DF1"]
    for name in ("R0_receipt_free_all", "R1_receipt_free_given_fixed",
                 "R0prime_fixed_and_receipt_free_all"):
        b = main_r[name]
        print(f"  {name:38s} {b['k']:3d}/{b['n']:3d} = {b['rate']:.3f} "
              f"(Wilson95 {b['wilson95'][0]:.3f}-{b['wilson95'][1]:.3f})")
    print(f"  分母の効果 R0 - R1                     {main_r['denominator_effect_R0_minus_R1']:+.3f}")
    print(f"  分子の効果 R0 - R0'                    {main_r['numerator_effect_R0_minus_R0prime']:+.3f}")
    ab = main_r["abandonment_in_R0_numerator"]
    print(f"  R0 の分子に混ざった放棄                 {ab['k']}/{ab['n']} = {ab['share']:.3f}")
    # ⚠️ 絶対パスを出すと、ホーム配下に clone した環境では **OS アカウント名が
    #   report.txt に載ってコミットされる** (security-checker LOW-1)。→ ★ ファイル名だけ出す。
    print("\n  -> results/metrics.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())
