#!/usr/bin/env python3
"""G1 統制タスク実験 — ブロック単位の特徴量抽出と、凍結された判定パイプライン。

★ **判定基準の単一真実源は `preregistration.md §3`（凍結）である。**
   本スクリプトはそれを実装するだけで、変更しない。齟齬があれば `preregistration.md` が正。

実装している凍結事項:
  §2.9  ブロック水準の最小打鍵（適格性ゲート・**モデル当てはめより前**に評価する）
  §3.1  L2 罰則つきロジスティック回帰 / λ=1.0 固定 / 学習 fold のみで z 標準化 /
        被験者内 leave-one-block-pair-out / out-of-fold AUC
  §3.2  FS-A（F1/F3/F4/F5/F6）と FS-B（＋Tier 0/1）の 2 本のみ。3 本目を作らない
  §3.3  主判定 = 個人内の並べ替え検定（p<0.05）＋ 補助 = AUC 中央値 ≥0.70 / ≥80% が AUC>0.60
  §3.4  見る順序: 操作チェック → positive control → FS-A/FS-B
  §3.5  産出量交絡の報告義務（条件別産出量・標準化係数・`keys` 単独 AUC）
  §3.9  並べ替えは**全数列挙**（G1: C(8,4)=70 / positive control: C(10,2)=45）→ seed 非依存
  §5.1  分散ゼロ特徴は標準化後 0 とし、必ず報告する

依存: **Python 標準ライブラリのみ**（`requirements.txt` を作らない・`env.md` の方針）。

使い方:
    python3 analyze.py --verify-blocks --dataset ~/gse-dataset --subject P015
        → ★ ラベルを一切読まない。ブロック長と打鍵数だけを出す（実施当日の検算用）。
    python3 analyze.py --dataset ~/gse-dataset --blocks-dir blocks --out results/metrics.json
    python3 analyze.py --selftest

⚠️ 出力にセッション日時・ファイル名を出さない（本 repo は一時 public 化の運用がある）。
⚠️ 被験者が書いた本文は入力にも出力にも存在しない（content-free 原則）。
"""
from __future__ import annotations

import argparse
import datetime
import itertools
import json
import math
import pathlib
import re
import statistics
import sys

# ---------------------------------------------------------------------------
# 事前登録から来る定数（preregistration.md / config.json のミラー。ここで変えない）
# ---------------------------------------------------------------------------
# ★ この実装が従っている事前登録の版。**結果ファイルに刻まれる**。
#   ⚠️ `selftest()` が `config.json` の `revision.version` と一致することを検査する。
#   このプロジェクトでは「文書だけ改訂して実装が追随しない」事故が 2 回起きており
#   （E-6: §2.5 の分岐 / E-7: §3.4 の見る順序）、★ **この定数自体も第 4 版で 3 のまま
#   取り残されていた**（第 5 版で発見）。番号がずれたら selftest が赤になるようにして、
#   人が気づくかどうかに依存させない。
PREREG_REVISION = 20

LAMBDA = 1.0                     # §3.1 L2 罰則（z 標準化後）・事前固定・チューニングしない
SILENCE_MS = 2000                # §3.2 silence = IKI >= 2000ms（現行 F5 の閾値に揃える）
MIN_KEYDOWNS_PER_BLOCK = 100     # §2.9 適格性ゲート
AUC_MEDIAN_MIN = 0.70            # §3.3-2
AUC_PER_SUBJECT_MIN = 0.60       # §3.3-3
AUC_PER_SUBJECT_FRACTION = 0.80  # §3.3-3
ALPHA = 0.05                     # §3.3-1
MANIPULATION_CHECK_MIN = 0.70    # §2.6
CORRECTION_CATEGORIES = {"backspace", "delete"}

FS_A = ["f1", "f3", "f4", "f5", "f6"]
TIER0 = ["keys", "bs_rate", "external_paste_chars", "ime_dwell_med"]
TIER1 = ["silence_p50", "silence_p90", "silence_max", "burst_p50", "burst_p90"]
FS_B = FS_A + TIER0 + TIER1                       # §3.2: 14 特徴量
FEATURE_SETS = {"FS_A": FS_A, "FS_B": FS_B}
KEYS_ALONE = ["keys"]                             # §3.5: 3 本目のセットではなく記述統計

MAX_NEWTON_ITERS = 50
NEWTON_TOL = 1e-8


# ---------------------------------------------------------------------------
# NDJSON → ブロック特徴量
# ---------------------------------------------------------------------------
def _pct(sorted_vals: list[float], p: float) -> float:
    """最近傍順位法の分位点（同 repo の 20260802-within-person-scope-detector と同じ定義）。"""
    if not sorted_vals:
        return 0.0
    k = min(len(sorted_vals) - 1, max(0, int(round(p * (len(sorted_vals) - 1)))))
    return float(sorted_vals[k])


def prereg_revision_from_doc(path: pathlib.Path) -> int | None:
    """`preregistration.md` の見出しから**最新の改訂番号**を読む（★ SSOT を直接見る）。

    ⚠️★★ **なぜ要るか**: 版一致検査は長らく `analyze.py ↔ config.json` だけを見ていた。
    ★ **両方が同じだけ遅れていれば緑になる**——実際に文書が第 13 版まで進んだのに
    どちらも 10 のまま緑だった（2026-08-10 に実測）。
    → 検査は**文書そのもの**を読まなければ、遅れを検出できない。

    見出しの形: `## ★ 改訂履歴 — 第 13 版（2026-08-08・...）`
    ★ 見出し行 (`#` 始まり) に限って探す（本文中の「第 3 版」に引っ張られないため）。
    ★ 最大値を採る（履歴の並び順に依存しない）。
    """
    best: int | None = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("#"):
            continue
        m = re.search(r"改訂履歴.*?第\s*(\d+)\s*版", line)
        if m:
            v = int(m.group(1))
            best = v if best is None else max(best, v)
    return best


ROSTER_KINDS = ("confirmatory", "pilot", "shakedown")


def check_subject_matches_filename(stem: str, spec: dict) -> str | None:
    """割付ファイル名と中身の `subject` が一致するかを見る。→ エラー文言 or `None`。

    ⚠️★★ **なぜ要るか**（`/cross-review` 2026-08-10・Claude と Codex が一致して指摘）:
    `sample_roster` は **ファイル名**（`p.stem`）で被験者を許可するのに、
    結果に刻まれるのは **`spec["subject"]`** である。
    ★ 両者がずれると **roster が許可していない被験者の結果が確証解析に載る**。
    ⚠️ `validate_blocks.py:590` は同じ検査を持っていたが、`analyze.py` には無かった——
    ★ 「誰が確証標本かを実装で強制する」という本改訂の目的そのものに穴が開いていた。
    """
    subj = spec.get("subject")
    if subj == stem:
        return None
    return (f"[NG] blocks/{stem}.json: ファイル名と subject が一致しない (subject={subj!r})。"
            f"★ sample_roster はファイル名で許可するので、中身とずれると"
            f"**許可していない被験者の結果が確証解析に載る**")


def evaluate_recruitment_closed(roster: dict | None) -> tuple[bool, str | None]:
    """`sample_roster.recruitment_closed` を厳密に評価する。→ `(closed, エラー文言 or None)`。

    ⚠️★★★ 2026-09-27 修正（Codex / security-checker / code-reviewer の 3 系統が独立に指摘・実測で確認）:
    旧実装は `bool(rc.get("closed"))` という素の型変換で、JSON に `"closed": "false"`（文字列）や
    `"closed": 1` のような値が入ると **Python では真になり**、n 未達 NG（optional stopping の禁止・
    §2.4-4）が意図せず緩んでいた。★ ここでは `closed is True` の厳密一致だけを「締めた」とし、
    それ以外の型は `[NG]` にして黙認しない（`registered_k` の型検査と同じ規律）。
    ⚠️ 加えて `closed=True` のときだけ `date`（YYYY-MM-DD 形式の文字列）と
    `decided_before_seeing_results is True` を必須にする —— これが欠けたまま緩めると、
    「結果を見たあとに closed=true を書く」という optional stopping の抜け道を機械が止められない
    （security-checker 指摘）。既定（キー無し・false）は 1 ビットも変えない。
    """
    rc = roster.get("recruitment_closed") if isinstance(roster, dict) else None
    if rc is None:
        return False, None
    if not isinstance(rc, dict):
        return False, f"[NG] sample_roster.recruitment_closed が object でない: {rc!r}"
    closed = rc.get("closed")
    if closed is False or closed is None:
        return False, None
    if closed is not True:
        return False, (f"[NG] sample_roster.recruitment_closed.closed が真偽値でない: {closed!r}。"
                        f"★ 文字列/数値では締めたと解釈しない（fail-closed）")
    date = rc.get("date")
    # ⚠️★★★ 2026-09-27 修正（Codex / code-reviewer 2 巡目・両方指摘）: 正規表現
    # `\d{4}-\d{2}-\d{2}` は書式だけを見るので `"2026-99-99"` のような実在しない日付も通る。
    # `date.fromisoformat()` は書式と実在の両方を検証する（うるう年等も正しく扱う）。
    if not isinstance(date, str):
        return False, (f"[NG] recruitment_closed.closed=true だが date が文字列でない: {date!r}")
    try:
        datetime.date.fromisoformat(date)
    except ValueError:
        return False, (f"[NG] recruitment_closed.closed=true だが date が実在する YYYY-MM-DD "
                        f"日付になっていない: {date!r}")
    if rc.get("decided_before_seeing_results") is not True:
        return False, ("[NG] recruitment_closed.closed=true だが "
                        "decided_before_seeing_results が true でない（結果を見る前に締めたと"
                        "自己申告されていない。optional stopping の抜け道になる）")
    return True, None


def resolve_sample(roster: dict | None, n_subjects, subjects_present: list[str]
                   ) -> tuple[list[str], list[dict], list[str], list[str]]:
    """★ **誰を確証標本として解析するか**を決める（`§2.4` / `§2.8`）。

    戻り値 `(解析する被験者, 外した被験者と理由, エラー文言, NOTE文言)`。
    エラーが 1 件でもあれば呼び出し側は**止める**。NOTE は止めない
    （前提条件 8 / A-2・2026-09-27: `recruitment_closed.closed=true` で n 未達の NG を緩めた時に出す）。

    ⚠️★★ **なぜ要るか（2026-08-10 に実測）**: それまで `analyze.py` は割付ファイルの
    `confirmatory` フラグを**一度も見ていなかった**うえ、glob `P*.json` は
    `PILOT-mac.json` / `PILOT-win.json` まで拾っていた。
    ★ パイロットが確証解析から外れていたのは **「dataset に NDJSON を置いていないから」**
    であって、**コードが保証していたわけではない**。
    → 「誰が確証標本か」は主張そのものを決めるので、**実行時に強制する**。

    ★ **単一の正は `config.json` の `sample_roster`**（git 管理下）。
    ⚠️ `blocks/*.json` は `blocks/.gitignore` が `*.json` を除外しており、
    **研究者の 1 台にしか無く、レビューも履歴も残らない**。だからそちらには置かない。
    ⚠️ ★ 両方に書いて突き合わせる案も却下した——本日の教訓
    「**鏡どうしを比べても、両方が同じだけずれていれば緑になる**」（`notes.md §10-7`）。

    ★ **純関数**（ファイルも I/O も触らない）。境界をテストで直接固定できる。
    """
    errors: list[str] = []
    excluded: list[dict] = []
    notes: list[str] = []

    # ⚠️★ 境界 1: キーが無い。「古い config なら全員」と読むと**保護が黙って消える**。
    if not isinstance(roster, dict):
        return [], [], [
            "[NG] config.json に sample_roster が無い。★ 誰が確証標本かを決められないので解析しない"
            "（preregistration.md §2.4 / §2.8）。"
            'sample_roster: {"confirmatory": [...], "pilot": [...], "shakedown": [...]} を書く'], []

    lists: dict[str, list[str]] = {}
    for kind in ROSTER_KINDS:
        v = roster.get(kind, [])
        if not isinstance(v, list) or any(not isinstance(x, str) for x in v):
            errors.append(f"[NG] sample_roster.{kind} が文字列のリストでない")
            v = []
        lists[kind] = v

    # ⚠️★ 境界 6: 同じ被験者が 2 つのリストに居る。分類が曖昧なまま進まない。
    seen: dict[str, str] = {}
    for kind in ROSTER_KINDS:
        for s in lists[kind]:
            if s in seen:
                where = (f"{seen[s]} の中に 2 回" if seen[s] == kind
                         else f"{seen[s]} と {kind} の両方に")
                errors.append(f"[NG] sample_roster: {s} が {where}ある。"
                              f"★ どちらの標本かが決まらない"
                              f"（★ 同一リスト内の重複は len(confirmatory) を水増しし、"
                              f"n の判定を誤らせる）")
            else:
                seen[s] = kind

    conf = lists["confirmatory"]
    # ⚠️★ 境界 2: 空を「全員」と読まない（roster 導入前の挙動に黙って戻さない）。
    if not conf:
        errors.append("[NG] sample_roster.confirmatory が空。★ 確証標本が 0 名では解析できない")

    # ⚠️★ 境界 7（前提条件 8 / A-2・2026-09-27）: registered_k の矛盾は NG。
    #   ★ registered_k（名簿に載せた人数・台帳の値）が confirmatory の人数より小さいと、
    #     台帳と config がずれている ＝ **黙認しない**（台帳は issue 004 の仕様書が持つ）。
    registered_k = roster.get("registered_k")
    if registered_k is not None:
        if not isinstance(registered_k, int) or isinstance(registered_k, bool):
            errors.append(f"[NG] sample_roster.registered_k が整数でない: {registered_k!r}")
        elif registered_k < len(conf):
            errors.append(
                f"[NG] sample_roster.registered_k の矛盾: registered_k={registered_k} が "
                f"confirmatory の人数 {len(conf)} より小さい。★ 台帳（募集した人数）と "
                f"config のずれを黙認しない")

    present = set(subjects_present)
    # ⚠️★ 境界 3: roster に居るのに割付ファイルが無い ＝ **欠員**。黙って n-1 で解析しない。
    missing = [s for s in conf if s not in present]
    if missing:
        errors.append(f"[NG] 確証標本に欠員がある（割付ファイルが無い）: {missing}。"
                      f"★ 収集が完了するまで解析結果を見ない（§2.4-4）")

    # ⚠️★★ 境界 5: 収集済みが n に達していない。**§2.4-4（optional stopping の禁止）の機械化**。
    #   ★ これまで「凍結した n 分が揃うまで見ない」は努力目標だった
    #     （`§5.3` の封印が `§3.4` を機械化したのと同じ形をここにも入れる）。
    #   ★ 前提条件 8 / A-2（2026-09-27）: `recruitment_closed.closed=true`（募集を締めた）
    #     ときに限り、この NG を [NOTE] に緩める。⚠️ 既定（キー無し・false）は 1 ビットも変えない
    #     （preregistration.md 第 20 版 (i)(ii) の規則を実行する。事前登録の改訂ではない）。
    recruitment_closed, rc_err = evaluate_recruitment_closed(roster)
    if rc_err:
        errors.append(rc_err)
    if isinstance(n_subjects, int) and not isinstance(n_subjects, bool):
        if len(conf) < n_subjects:
            if recruitment_closed:
                notes.append(
                    f"[NOTE] 確証標本が {len(conf)} 名で、凍結した n={n_subjects} に達していないが、"
                    f"募集を締めた（sample_roster.recruitment_closed.closed=true）ため"
                    f"収集完了として続行する（preregistration.md 第 20 版 (i)(ii)）。")
            else:
                errors.append(
                    f"[NG] 確証標本が {len(conf)} 名で、凍結した n={n_subjects} に達していない。"
                    f"★ 揃うまで解析結果を見ない（§2.4-4 optional stopping の禁止）")
    else:
        errors.append(f"[NG] config.json の design.n_subjects が数値で凍結されていない "
                      f"(実際: {n_subjects!r})。★ 確証データより前に凍結する（§2.4-2）")

    # ⚠️★ 境界 4: roster のどこにも無い割付ファイル。**報告して外す**（黙って落とさない・D-5）。
    #   ★ 止めはしない: 将来の被験者の割付を先に置く運用（protocol.md §6）を壊さないため。
    for s in sorted(present):
        kind = seen.get(s)
        if kind is None:
            excluded.append({"subject": s, "reason": "not_in_roster"})
        elif kind != "confirmatory":
            excluded.append({"subject": s, "reason": kind})

    analysed = [s for s in conf if s in present]
    return analysed, excluded, errors, notes


def check_zero_analysed(analysed_m: int) -> str | None:
    """★ 完了者が 0 名になったら確証解析は行えない（preregistration.md 第 20 版 (ii)(c)）。

    `analysed_m` は `cohort_verdict()` が出す `n_subjects_analysed`（主判定が skip でない被験者数）。
    ⚠️ `resolve_sample` の n 未達ゲート（境界 5）とは別の問い: `recruitment_closed` で
    その NG を緩めても、**主判定が 1 件も出せる被験者がいなければ解析にならない**。
    ★ 純関数（NG 文言または None を返すだけ）。
    """
    if analysed_m == 0:
        return ("[NG] 確証解析の対象（解析 m = n_subjects_analysed）が 0 名。"
                "★ 完了者が 0 名になったら確証解析は行えない（preregistration.md 第 20 版 (ii)(c)）。")
    return None


def session_starts(path: pathlib.Path) -> tuple[int, list[int]]:
    """`session_start` 行を読み、**(構造上の本数, cutoff に使える時刻の列)** を返す。

    ⚠️★★ **2 つを分ける理由**（2026-08-10 の `/cross-review` で Codex が指摘・実測で再現）:
    以前はこの関数が「`t` が有効な `int` である行」だけを数えていた。⚠️ ところが
    `validate_blocks.py::scan_ndjson` は **`type` だけで数える**。
    ★ 2 本目の `session_start` の `t` が壊れていると、
    **validate_blocks は 2 本と数えて FAIL するのに、こちらは 1 本と数えて黙って混ぜた**。
    ★ 本タスクが塞ごうとした「沈黙して間違った結果を出す」経路が、狭い条件で開いたままだった。

    → ★ **「壊れているか」を見る数え方**（`type` のみ・validate_blocks と同じ基準）と、
      **「どこから読むか」を決める時刻**（有効な `int` のみ）は**別の問い**である。混ぜない。

    ⚠️ ★ `meta` 行も `"session_start"` を**キーとして**持つ（`{"type":"meta","session_start":0,...}`）
    ので、文字列一致だけでは meta を数えてしまう。★ `type` で必ず絞る。

    ★ 行が 0 本なのは異常ではない: アプリが `session_start` 行を書く前の版のログがある。
    「0 本 = 判断材料が無い」であって「壊れている」ではない。
    """
    n = 0
    ts: list[int] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if '"session_start"' not in line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        if o.get("type") != "session_start":
            continue
        n += 1                                    # ★ 構造の本数は type だけで数える
        t = o.get("t")
        if isinstance(t, int) and not isinstance(t, bool):
            ts.append(t)
    return n, ts


def read_block(path: pathlib.Path, from_last_session: bool = False) -> dict:
    """匿名化 NDJSON 1 ファイル（= 1 ブロック）からブロック特徴量を計算する。

    ⚠️★★ `from_last_session=True` のとき、**最後の `session_start` 以降の行だけ**を読む
    （2026-08-10 の P010 block07・`notes.md §10-3`）。

    ★ なぜ「最後」なのか: 「開始する」の押し直しは `engine.reset()` と `SESSION_START_MS` の
    引き直しを伴う（`lib.rs:1948` / `:2019`）ので、**アプリにとって最後のセッションが
    「そのブロック」**である。自動終了もそこから 5 分で閉じる
    （P010 block07 で 568.5s 予測 vs 569.05s 実測）。

    ⚠️ ★ **この関数は止まらない。** セッションが 2 本あることは `n_session_starts` として
    返すだけで、赤にするかどうかは呼び出し側が決める（`--verify-blocks` は情報提示専用で
    常に 0 を返す契約があり、ここで止めると道連れで死ぬ）。

    入力は `analysis/anonymize.rs` を通した形式を前提とする:
      key        {t(相対ms), category, press}   ← vk は匿名化で category に置き換わっている
      paste      {t, external_paste_chars}
      ime_shadow {t, dwell_ms, nav, abandon}
      feat       {t, f1, f3, f4, f5, f6, ...}   ← FS-A の出所（§3.2 / design D-2）
    生の `vk` を持つ未匿名 NDJSON も受け付ける（`vk` から category を導けるため）。

    ★ **cutoff が依存している前提**（`/cross-review` 2026-08-10 の指摘 2・★ 実装で確認した）:
    `t` は**再開始をまたいで単調**である。`analysis/anonymize.rs::find_session_start` は
    **キー `session_start` を持つ最初の行（＝ `meta` 行 1 本だけ）**を返し、
    `anonymize_ndjson` がその 1 つの値を**ファイル全体**の相対化基点に使うので、
    2 本目の `session_start` が来ても `t` は 0 に戻らない。
    ⚠️ ★ **この不変条件が崩れたら**（相対化をセッションごとに行うようになったら）**cutoff は壊れる。**

    ⚠️ ★ **`malformed_lines` は cutoff より前の行も数える**（同・指摘 1）。
    ★ パースできなかった行には `t` が無いので、**どちらのセッションに属するか原理的に決められない**。
    → 落とさずに数え、この事実を書いておく（★ 黙って正確なふりをしない）。
    """
    keydowns: list[int] = []
    corrections = 0
    paste_chars = 0
    dwells: list[int] = []
    feats: list[dict] = []
    malformed = 0

    n_starts, start_ts = session_starts(path)
    # ★ セッションが 1 本（または 0 本＝旧版のログ）なら cutoff は立てない。
    #   ⚠️ フラグを付けても**正常なファイルの結果は 1 ビットも変わらない**
    #   （selftest が対照でこれを固定している）。
    # ⚠️★ セッションが 2 本以上なのに有効な `t` が 2 本揃わないなら **cutoff を決められない**。
    #   ★ ここでは止めず (`--verify-blocks` の契約)、`restart_cutoff_applied` で呼び出し側に伝える。
    cutoff = start_ts[-1] if (from_last_session and n_starts > 1 and len(start_ts) > 1) else None

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            o = json.loads(line)
        except Exception:
            malformed += 1
            continue
        if cutoff is not None:
            ot = o.get("t")
            # ⚠️ `t` を持たない行 (meta / session_meta) は落とさない。
            #   ★ 落とすのは「前の試行に属する観測行」だけである。
            # ⚠️ `bool` は `int` の派生なので明示的に除く（`t: true` を 1 と読まない）。
            if isinstance(ot, (int, float)) and not isinstance(ot, bool) and ot < cutoff:
                continue
        t = o.get("type")
        if t == "key":
            if o.get("press") is not True:
                continue
            keydowns.append(int(o["t"]))
            cat = o.get("category")
            if cat is None and "vk" in o:          # 未匿名ログのフォールバック
                cat = {0x08: "backspace", 0x2E: "delete"}.get(int(o["vk"]))
            if cat in CORRECTION_CATEGORIES:
                corrections += 1
        elif t == "paste":
            v = o.get("external_paste_chars")
            if isinstance(v, int):
                paste_chars += v
        elif t == "ime_shadow":
            v = o.get("dwell_ms")
            if isinstance(v, int):
                dwells.append(v)
        elif t == "feat":
            feats.append(o)

    keydowns.sort()
    n = len(keydowns)
    # §3.2: ブロックの計測は最初の keydown から最後の keydown まで
    span_ms = (keydowns[-1] - keydowns[0]) if n >= 2 else 0
    ikis = [b - a for a, b in zip(keydowns, keydowns[1:]) if b >= a]

    silences = sorted(x for x in ikis if x >= SILENCE_MS)
    # §3.2: silence が 0 個のブロックは 3 値とも 0（欠測にしない・事前宣言）
    bursts: list[int] = []
    run = 1
    for x in ikis:
        if x >= SILENCE_MS:
            bursts.append(run)
            run = 1
        else:
            run += 1
    if n > 0:
        bursts.append(run)
    bursts_sorted = sorted(bursts)

    # §3.2 / design D-2: FS-A は `feat` 行の中央値（最初の keydown 以降の行のみ）
    t0 = keydowns[0] if keydowns else 0
    rows = [f for f in feats if int(f.get("t", 0)) >= t0]
    fs_a = {}
    for k in FS_A:
        vals = [float(f[k]) for f in rows if isinstance(f.get(k), (int, float))]
        fs_a[k] = statistics.median(vals) if vals else 0.0

    return {
        "n_keydowns": n,
        "span_ms": span_ms,
        "n_feat_rows": len(rows),
        "malformed_lines": malformed,
        # ★ 数えて返すだけ。判断は呼び出し側（`load_subject_blocks` / `cmd_verify_blocks`）。
        "n_session_starts": n_starts,
        # ⚠️★ 「最終セッションだけを読めたか」。`from_last_session=True` を指定したのに
        #   これが False なら、★ **起点が決められなかった**＝全行読んでいる。
        #   呼び出し側はここを見て止める（黙って混ぜたものを「最終セッション」と刻ませない）。
        "restart_cutoff_applied": cutoff is not None,
        "features": dict(fs_a, **{
            "keys": float(n),
            "bs_rate": (corrections / n) if n else 0.0,
            "external_paste_chars": float(paste_chars),
            "ime_dwell_med": float(statistics.median(dwells)) if dwells else 0.0,
            "silence_p50": _pct(silences, 0.50),
            "silence_p90": _pct(silences, 0.90),
            "silence_max": float(silences[-1]) if silences else 0.0,
            "burst_p50": _pct(bursts_sorted, 0.50),
            "burst_p90": _pct(bursts_sorted, 0.90),
        }),
        "n_silences": len(silences),
        "ime_shadow_rows": len(dwells),
    }


# ---------------------------------------------------------------------------
# L2 罰則つきロジスティック回帰（§3.1・標準ライブラリのみ）
# ---------------------------------------------------------------------------
def _solve(A: list[list[float]], b: list[float]) -> list[float] | None:
    """部分ピボット選択つき Gauss 消去。特異なら None。"""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-12:
            return None
        M[c], M[p] = M[p], M[c]
        piv = M[c][c]
        for r in range(n):
            if r == c:
                continue
            f = M[r][c] / piv
            if f == 0.0:
                continue
            for k in range(c, n + 1):
                M[r][k] -= f * M[c][k]
    return [M[i][n] / M[i][i] for i in range(n)]


def fit_l2_logistic(X: list[list[float]], y: list[int]) -> dict:
    """切片つき L2 罰則ロジスティック回帰。切片は罰則しない。

    目的: Σ log(1+exp(-ỹ f(x))) + (λ/2)||w||²   （ỹ ∈ {-1,+1}, w は切片を除く係数）
    ⚠️ λ は事前固定（§3.1）。データから選ばない。
    """
    n = len(X)
    d = len(X[0]) if n else 0
    beta = [0.0] * (d + 1)          # beta[0] = 切片
    for _ in range(MAX_NEWTON_ITERS):
        g = [0.0] * (d + 1)
        H = [[0.0] * (d + 1) for _ in range(d + 1)]
        for i in range(n):
            z = beta[0] + sum(beta[j + 1] * X[i][j] for j in range(d))
            p = 1.0 / (1.0 + math.exp(-max(-35.0, min(35.0, z))))
            r = p - y[i]
            w = max(p * (1.0 - p), 1e-10)
            xi = [1.0] + X[i]
            for a in range(d + 1):
                g[a] += r * xi[a]
                for b in range(d + 1):
                    H[a][b] += w * xi[a] * xi[b]
        for j in range(1, d + 1):
            g[j] += LAMBDA * beta[j]
            H[j][j] += LAMBDA
        H[0][0] += 1e-8             # 切片の数値安定化のみ（罰則ではない）
        step = _solve(H, [-v for v in g])
        if step is None:
            break
        beta = [b + s for b, s in zip(beta, step)]
        if max(abs(s) for s in step) < NEWTON_TOL:
            break

    # 学習側で完全分離したか（§3.1 の診断値）
    perfect = all(
        (beta[0] + sum(beta[j + 1] * X[i][j] for j in range(d)) > 0) == (y[i] == 1)
        for i in range(n)
    ) if n else False
    return {"beta": beta, "perfect_training_separation": perfect}


def _score(beta: list[float], x: list[float]) -> float:
    return beta[0] + sum(beta[j + 1] * x[j] for j in range(len(x)))


def standardize(train: list[list[float]], rows: list[list[float]]) -> tuple[list[list[float]], list[int]]:
    """§3.1: 学習 fold のみで z 標準化。§5.1: 分散ゼロ特徴は 0 に潰し、その添字を返す。

    標準偏差は**母標準偏差**（分母 = 学習 fold の標本数）を使う。事前登録は ddof を指定して
    いないため、罰則の強さと係数尺度が実装差で動かないようにここで固定する。
    λ=1.0 が事前固定であることと合わせて、**選択の余地を残さない**ためである。
    """
    d = len(train[0])
    out_rows = [row[:] for row in rows]
    degenerate: list[int] = []
    for j in range(d):
        col = [r[j] for r in train]
        mu = sum(col) / len(col)
        var = sum((v - mu) ** 2 for v in col) / len(col)
        sd = math.sqrt(var)
        if sd < 1e-12:
            degenerate.append(j)
            for r in out_rows:
                r[j] = 0.0
        else:
            for r in out_rows:
                r[j] = (r[j] - mu) / sd
    return out_rows, degenerate


def cv_auc(rows: list[list[float]], labels: list[int]) -> dict:
    """§3.1: 被験者内 leave-one-block-pair-out の out-of-fold AUC。

    fold = (held-out 陽性ブロック 1 個, held-out 陰性ブロック 1 個) の全組合せ。
    out-of-fold AUC = 「held-out 陽性が held-out 陰性より高いスコアを得た fold の割合」
    （同値は 0.5）。これは held-out 対上の AUC の定義そのもの（design D-3）。
    """
    pos = [i for i, v in enumerate(labels) if v == 1]
    neg = [i for i, v in enumerate(labels) if v == 0]
    wins = 0.0
    folds = 0
    max_abs_coef = 0.0
    perfect_folds = 0
    degenerate_counts: dict[int, int] = {}
    for i in pos:
        for j in neg:
            tr_idx = [k for k in range(len(rows)) if k not in (i, j)]
            train_raw = [rows[k] for k in tr_idx]
            all_std, degen = standardize(train_raw, rows)
            for jj in degen:
                degenerate_counts[jj] = degenerate_counts.get(jj, 0) + 1
            model = fit_l2_logistic([all_std[k] for k in tr_idx], [labels[k] for k in tr_idx])
            beta = model["beta"]
            max_abs_coef = max(max_abs_coef, max(abs(b) for b in beta[1:]) if len(beta) > 1 else 0.0)
            perfect_folds += 1 if model["perfect_training_separation"] else 0
            si, sj = _score(beta, all_std[i]), _score(beta, all_std[j])
            wins += 1.0 if si > sj else (0.5 if si == sj else 0.0)
            folds += 1
    return {
        "auc": wins / folds if folds else float("nan"),
        "n_folds": folds,
        "max_abs_coefficient": max_abs_coef,
        "folds_with_perfect_training_separation": perfect_folds,
        "degenerate_feature_folds": degenerate_counts,
    }


def full_fit_coefficients(rows: list[list[float]], labels: list[int], names: list[str]) -> dict:
    """§3.5: 各特徴の標準化係数（全ブロックで 1 回当てはめた記述統計）。

    ⚠️ **これは in-sample の当てはめである**（全ブロックで標準化し、全ブロックで当てはめる）。
    どの特徴がどちら向きに効いたかを読むためだけに出す。**性能の指標ではない**——
    性能は out-of-fold AUC（`cv_auc`）と並べ替え検定でのみ判断する（§3.3）。
    """
    std_rows, degen = standardize(rows, rows)
    model = fit_l2_logistic(std_rows, labels)
    beta = model["beta"]
    return {
        "IN_SAMPLE_descriptive_only": True,
        "intercept": round(beta[0], 4),
        "standardized_coefficients": {n: round(beta[k + 1], 4) for k, n in enumerate(names)},
        "degenerate_features": [names[j] for j in degen],
        "perfect_training_separation": model["perfect_training_separation"],
    }


# ---------------------------------------------------------------------------
# 並べ替え検定（§3.9: 全数列挙・seed 非依存）
# ---------------------------------------------------------------------------
def exact_permutation_test(rows: list[list[float]], labels: list[int]) -> dict:
    n = len(labels)
    k = sum(labels)
    observed = cv_auc(rows, labels)
    obs_auc = observed["auc"]
    perm_aucs = []
    for combo in itertools.combinations(range(n), k):
        perm = [1 if i in combo else 0 for i in range(n)]
        perm_aucs.append(cv_auc(rows, perm)["auc"])
    total = len(perm_aucs)
    ge = sum(1 for a in perm_aucs if a >= obs_auc - 1e-12)

    # ★ 到達可能な最小 p（**ラベルに依存しない診断値**）
    #   帰無分布の最大値に何通りの割付が並ぶかで決まる。並びが多いほど、
    #   **完全に分離していても p を小さくできない**。1/total（理論上の最小）と混同しないこと。
    #   ⚠️ Phase1 実データの疑似ブロックで測ると、この床が 0.05 を超える被験者が実在した
    #      （.steering/20260802-g1-implementation/decisions.md D-5）。
    max_auc = max(perm_aucs)
    n_at_max = sum(1 for a in perm_aucs if a >= max_auc - 1e-12)
    floor_p = n_at_max / total
    return {
        "observed_auc": round(obs_auc, 4),
        "n_permutations": total,
        "enumeration": "EXHAUSTIVE (not sampled) -> seed-independent",
        "n_ge_observed": ge,
        "p_value": round(ge / total, 6),
        "theoretical_min_p": round(1.0 / total, 6),
        "attainable_min_p_for_this_subject": round(floor_p, 6),
        "attainable_min_p_note": "LABEL-FREE diagnostic: the largest AUC any label assignment can reach is "
                                 f"{round(max_auc, 4)}, and {n_at_max}/{total} assignments tie there. "
                                 "No labelling, however perfect, can produce a p below this floor.",
        "test_can_reject_at_all": floor_p < ALPHA,
        "null_auc_median": round(sorted(perm_aucs)[total // 2], 4),
        "null_auc_p95": round(sorted(perm_aucs)[min(total - 1, int(0.95 * (total - 1)))], 4),
        "alpha": ALPHA,
        "significant": (ge / total) < ALPHA,
        "one_sided": "larger AUC = more separation",
        "max_abs_coefficient": round(observed["max_abs_coefficient"], 4),
        "folds_with_perfect_training_separation": observed["folds_with_perfect_training_separation"],
        "n_folds": observed["n_folds"],
    }


def fisher_combine(pvals: list[float]) -> dict:
    """§3.3-1 / §3.9: Fisher 統合。n>=2 のときのみ使う。"""
    if len(pvals) < 2:
        return {"applied": False,
                "reason": "n<2: Fisher is applied only for n>=2 (preregistration.md 3.9); "
                          "the single within-subject p is reported as-is"}
    stat = -2.0 * sum(math.log(max(p, 1e-300)) for p in pvals)
    k = len(pvals)                       # 自由度 2k → 偶数なので閉形式で上側確率が出る
    x = stat / 2.0
    term = 1.0
    s = 1.0
    for i in range(1, k):
        term *= x / i
        s += term
    p = math.exp(-x) * s
    return {
        "applied": True,
        "k": k,
        "chi2": round(stat, 4),
        "df": 2 * k,
        "p_value": round(min(1.0, p), 6),
        "significant": p < ALPHA,
        "known_limitation": "within-subject p-values are discrete (min 1/70), so the combined p is "
                            "CONSERVATIVE. Frozen knowingly (preregistration.md 3.3).",
    }


# ---------------------------------------------------------------------------
# 適格性ゲート（§2.9・**モデル当てはめより前**）
# ---------------------------------------------------------------------------
def eligibility(blocks: list[dict]) -> dict:
    g1 = [b for b in blocks if b["condition"] in ("HI", "LO")]
    copy = [b for b in blocks if b["condition"] == "copy"]
    low_g1 = [b["block"] for b in g1 if b["n_keydowns"] < MIN_KEYDOWNS_PER_BLOCK]
    low_all = [b["block"] for b in (g1 + copy) if b["n_keydowns"] < MIN_KEYDOWNS_PER_BLOCK]
    return {
        "threshold_keydowns_per_block": MIN_KEYDOWNS_PER_BLOCK,
        "evaluated": "BEFORE any model is fitted (preregistration.md 2.9)",
        "keydowns_per_block": {b["block"]: b["n_keydowns"] for b in blocks},
        "blocks_below_threshold_g1": low_g1,
        "blocks_below_threshold_any": low_all,
        "eligible_for_primary": not low_g1,
        "eligible_for_positive_control": not low_all,
        "note": "Blocks are never dropped; the SUBJECT is excluded so that HI4/LO4 and C(8,4)=70 survive. "
                "Excluded subjects are not replaced (preregistration.md 2.4-7).",
    }


# ---------------------------------------------------------------------------
# 被験者 1 名分の解析
# ---------------------------------------------------------------------------
def analyse_subject(subject: str, blocks: list[dict]) -> dict:
    if not blocks:
        return {"subject": subject, "error": "no blocks in the assignment file"}
    elig = eligibility(blocks)
    g1 = [b for b in blocks if b["condition"] in ("HI", "LO")]
    order = sorted(blocks, key=lambda b: b["block"])

    result: dict = {
        "subject": subject,
        "arrangement": blocks[0].get("arrangement"),
        "n_blocks": len(blocks),
        "eligibility": elig,
        "block_summary": [
            {"block": b["block"], "condition": b["condition"], "topic_id": b.get("topic_id"),
             "n_keydowns": b["n_keydowns"], "span_ms": b["span_ms"],
             "n_feat_rows": b["n_feat_rows"], "produced_chars": b.get("produced_chars")}
            for b in order
        ],
    }

    # §3.5: 産出量交絡の報告（条件別の実産出量）
    def _summary(cond: str) -> dict:
        vals = [b["n_keydowns"] for b in blocks if b["condition"] == cond]
        chars = [b["produced_chars"] for b in blocks
                 if b["condition"] == cond and isinstance(b.get("produced_chars"), int)]
        return {
            "n_blocks": len(vals),
            "keys_median": statistics.median(vals) if vals else None,
            "keys_min": min(vals) if vals else None,
            "keys_max": max(vals) if vals else None,
            "produced_chars_median": statistics.median(chars) if chars else None,
            "produced_chars_reported": len(chars),
        }

    result["production_by_condition"] = {c: _summary(c) for c in ("HI", "LO", "copy")}
    if not any(isinstance(b.get("produced_chars"), int) for b in blocks):
        result["production_by_condition"]["warning"] = (
            "produced_chars not supplied. preregistration.md 3.5 requires reporting the realised "
            "output per condition (block `keys` AND final character count). The app never stores the "
            "written text (content-free), so the experimenter must record the character count on the "
            "recording sheet (protocol.md 2.2) and put it into the blocks file.")

    # --- positive control（§2.5・§3.4 で FS-A/FS-B より先に見る） ---
    if elig["eligible_for_positive_control"] and len(order) == 10:
        rows = [[b["features"][f] for f in FS_B] for b in order]
        labels = [1 if b["condition"] == "copy" else 0 for b in order]
        pc = exact_permutation_test(rows, labels)
        pc["labels"] = "copy(2) vs writing(8)"
        pc["known_limitation"] = ("copy blocks are position-fixed, so this separation is confounded with "
                                  "position. FLOOR CHECK on instrument health only; no effect size is claimed.")
        pc["passed"] = bool(pc["significant"])
    else:
        pc = {"skipped": True,
              "reason": "subject ineligible for the positive control, or the session does not have 10 blocks"}
    result["positive_control"] = pc

    # --- 主判定（§3.3） ---
    if not elig["eligible_for_primary"]:
        result["primary"] = {"skipped": True, "reason": "ineligible under the 2.9 gate"}
        return result
    if len(g1) != 8 or sum(1 for b in g1 if b["condition"] == "HI") != 4:
        result["primary"] = {"skipped": True,
                             "reason": f"expected 8 G1 blocks with HI4/LO4, got {len(g1)}"}
        return result

    g1_order = sorted(g1, key=lambda b: b["block"])
    labels = [1 if b["condition"] == "HI" else 0 for b in g1_order]
    primary: dict = {}
    for name, feats in FEATURE_SETS.items():
        rows = [[b["features"][f] for f in feats] for b in g1_order]
        primary[name] = exact_permutation_test(rows, labels)
        primary[name]["n_features"] = len(feats)
        primary[name]["coefficients"] = full_fit_coefficients(rows, labels, feats)
    # §3.5: `keys` 単独 AUC（3 本目の特徴量セットではない・descriptive）
    rows_keys = [[b["features"][f] for f in KEYS_ALONE] for b in g1_order]
    primary["keys_alone_DESCRIPTIVE"] = dict(
        cv_auc(rows_keys, labels),
        note="single-feature descriptive statistic (preregistration.md 3.5), NOT a third feature set. "
             "If FS_B's AUC does not substantially exceed this, the separation may be attributable to "
             "output volume and must be reported as such.")
    result["primary"] = primary
    return result


# ---------------------------------------------------------------------------
# 操作チェック（§2.6）
# ---------------------------------------------------------------------------
def manipulation_check(blocks: list[dict], answers: list[dict]) -> dict:
    """answers: [{"block": 3, "harder": 2}, ...]  harder = より詰まったと選ばれたブロック番号。"""
    cond = {b["block"]: b["condition"] for b in blocks}
    cross, hi_chosen, same = 0, 0, 0
    for a in answers:
        cur, prev = a.get("block"), a.get("block", 0) - 1
        if cur not in cond or prev not in cond:
            continue
        if cond[cur] not in ("HI", "LO") or cond[prev] not in ("HI", "LO"):
            continue
        if cond[cur] == cond[prev]:
            same += 1                     # §2.6: 同条件ペアは分母に入れない
            continue
        cross += 1
        if cond.get(a.get("harder")) == "HI":
            hi_chosen += 1
    rate = (hi_chosen / cross) if cross else None
    return {
        "n_answers": len(answers),
        "n_cross_condition_pairs_DENOMINATOR": cross,
        "n_same_condition_pairs_excluded": same,
        "hi_chosen_as_harder": hi_chosen,
        "rate": round(rate, 4) if rate is not None else None,
        "threshold": MANIPULATION_CHECK_MIN,
        "passed": (rate is not None and rate >= MANIPULATION_CHECK_MIN),
        "note": "Denominator is cross-condition pairs only (preregistration.md 2.6). "
                "This is NOT part of the verdict, but it is read FIRST (3.4).",
    }


# ---------------------------------------------------------------------------
# §3.4 の見る順序 ＋ §2.5（第 3 版）の分岐
# ---------------------------------------------------------------------------
def interpretability(mchecks: dict, pcs: list[dict]) -> tuple[str, bool, str]:
    """`§3.4` の見る順序（操作チェック → positive control）を 1 か所に閉じる。

    ★ **第 3 版の変更点**: positive control が `✗` のときの扱いを、**ラベル非依存**の
    診断値 `test_can_reject_at_all` で分ける（`preregistration.md §2.5`）:

      - `✗` かつ **true**  -> `G1_VOID`（計器故障の疑い・**第 2 版から不変**）
      - `✗` かつ **false** -> `VERDICT_WITHHELD`（**検出力不足であって計器故障ではない**）

    ⚠️ **どちらの枝でも `§3.3` の判定を読まない**（`interpretable=False`）。
       したがってこれは**判定を緩める分岐ではない**——「分離できた」と言える経路は
       1 本も増えていない。分岐変数は帰無分布の形だけで決まるので、
       **結果を見てから枝を選ぶことができない**。

    ★ 落ちた被験者が複数いる場合、**1 名でも `true` で落ちていれば `G1_VOID`** とする
      （計器故障の疑いを検出力不足で薄めない・保守側）。

    戻り値: (status, interpretable, reason)
    """
    if not mchecks:
        return ("MANIPULATION_CHECK_NOT_SUPPLIED", False,
                "manipulation check not supplied. Per 3.4 the separation result must not be "
                "interpreted until the manipulation check has been read and passed.")
    if not all(m["passed"] for m in mchecks.values()):
        return ("MANIPULATION_CHECK_FAILED", False,
                "manipulation check FAILED (2.6): the friction was not manipulated; redesign the task.")
    if not pcs:
        return ("POSITIVE_CONTROL_NOT_RUN", False,
                "positive control could not be run (no eligible 10-block subject).")

    failed = [p for p in pcs if not p.get("passed")]
    if any(p.get("test_can_reject_at_all") for p in failed):
        return ("G1_VOID", False,
                "positive control FAILED with test_can_reject_at_all=true: G1 IS VOID (2.5). "
                "Instrument/pipeline fault suspected. Do NOT read a negative result as a property "
                "of the world. Diagnose and re-run.")
    if failed:
        return ("VERDICT_WITHHELD", False,
                "positive control FAILED, but test_can_reject_at_all=false for every failing subject: "
                "VERDICT WITHHELD (2.5, revision 3). This is UNDERPOWER, not an instrument fault - "
                "even perfect separation could not have reached p<alpha for these subjects. "
                "Do NOT diagnose the instrument and do NOT doubt the axis; re-run with a design "
                "that raises attainability (e.g. more blocks).")
    return ("INTERPRETABLE", True,
            "manipulation check passed and positive control passed (3.4 order satisfied).")


# ---------------------------------------------------------------------------
# ★ 見る順序の強制 — 判定の封印（§5.3・第 4 版）
# ---------------------------------------------------------------------------
#: ★ **ラベルに依存しない**診断値（`§5.2`）。封印しない。
#  帰無分布の形だけで決まるので、見ても事後の自由度にならない。むしろ
#  「検出力不足で落ちたのか計器が壊れて落ちたのか」の判断に必要である。
LABEL_FREE_KEYS = frozenset({
    "n_permutations", "enumeration", "theoretical_min_p",
    "attainable_min_p_for_this_subject", "attainable_min_p_note",
    "test_can_reject_at_all", "null_auc_median", "null_auc_p95",
    "alpha", "one_sided", "n_features",
})

SEAL_NOTE = (
    "SEALED: the 3.4 viewing order was not satisfied (see interpretability_reason). "
    "Label-dependent results are withheld so that a corrected re-run remains CONFIRMATORY. "
    "Re-run with --unseal to look anyway; doing so stamps confirmatory_status_forfeited=true."
)


def seal_verdict(result: dict) -> dict:
    """`§3.4` の見る順序を**実装で強制する**（`§5.3`・第 4 版）。

    ★ **なぜ要るか**: `§3.4-1` は「操作チェックが不合格なら `§3.3` の結果を**解釈しない**」と
    凍結しているが、第 3 版までの実装は `interpretable=False` でも `separated` / `median_auc` /
    `fisher_p` をそのまま出していた。**文書が禁じたものをツールが目の前に出していた。**

    ★ **なぜ封印が判定を緩めないか**: 封印は**情報を減らす**方向の変更である。
    「分離できた」と言える経路は 1 本も増えていない。むしろ
    **偽の不合格（`§2.6` の操作チェックは、操作が真に 80% 効いていても 18〜35% で落ちる）を
    引いたときに、数値を見ずに済むので再実施が確証的なまま**でいられる
    （`§2.8` が「見てから変えたら確証性を放棄」と定めているのと同じ構造）。

    封印するもの / しないもの:

    - 封印する: `3_verdict` のラベル依存量、`per_subject[].primary` のラベル依存量
    - ★ 封印しない: `1_manipulation_check` / `2_positive_control`（`§3.4` の順序で**先に見る**もの）、
      適格性（`§2.9`・打鍵数のみ）、ブロックの記述統計、
      および **ラベル非依存の到達可能性診断**（`§5.2`・`LABEL_FREE_KEYS`）
    """
    def seal_test(d: dict) -> dict:
        kept = {k: v for k, v in d.items() if k in LABEL_FREE_KEYS}
        kept["sealed"] = True
        kept["sealed_note"] = SEAL_NOTE
        return kept

    verdict = result.get("3_verdict", {})
    result["3_verdict"] = {
        "interpretable": verdict.get("interpretable"),
        "interpretability_reason": verdict.get("interpretability_reason"),
        "sealed": True,
        "sealed_note": SEAL_NOTE,
    }
    for s in result.get("per_subject", []):
        primary = s.get("primary")
        if isinstance(primary, dict) and "skipped" not in primary:
            s["primary"] = {
                name: (seal_test(v) if isinstance(v, dict) else v)
                for name, v in primary.items()
            }
    return result


# ---------------------------------------------------------------------------
# コホート水準の判定（§3.3）
# ---------------------------------------------------------------------------
def cohort_verdict(per_subject: list[dict], interpretable: bool, reason: str) -> dict:
    out: dict = {"interpretable": interpretable, "interpretability_reason": reason}
    for name in FEATURE_SETS:
        usable = [s for s in per_subject if "skipped" not in s.get("primary", {"skipped": True})]
        aucs = [s["primary"][name]["observed_auc"] for s in usable]
        pvals = [s["primary"][name]["p_value"] for s in usable]
        n = len(usable)
        need = math.ceil(AUC_PER_SUBJECT_FRACTION * n) if n else 0
        above = sum(1 for a in aucs if a > AUC_PER_SUBJECT_MIN)
        fisher = fisher_combine(pvals)
        primary_sig = (fisher["p_value"] < ALPHA) if fisher["applied"] else (
            pvals[0] < ALPHA if pvals else False)
        median_auc = statistics.median(aucs) if aucs else None
        out[name] = {
            "n_subjects_analysed": n,
            "per_subject_auc": [round(a, 4) for a in aucs],
            "per_subject_p": pvals,
            "fisher": fisher,
            "criterion_1_primary_permutation_significant": primary_sig,
            "criterion_2_median_auc": round(median_auc, 4) if median_auc is not None else None,
            "criterion_2_met": (median_auc is not None and median_auc >= AUC_MEDIAN_MIN),
            "criterion_3_subjects_above_0_60": f"{above}/{n} (need >= {need})",
            "criterion_3_met": (n > 0 and above >= need),
            "separated": bool(
                interpretable and primary_sig
                and median_auc is not None and median_auc >= AUC_MEDIAN_MIN
                and n > 0 and above >= need),
            "note": "'separated' requires ALL THREE criteria (preregistration.md 3.3). "
                    "A high AUC without permutation significance is NOT separation.",
        }
        if n == 1:
            out[name]["n_equals_1_caveat"] = (
                "With n=1 the descriptive criteria carry little practical meaning (preregistration.md 3.9), "
                "and topic-by-condition counterbalancing does not exist (2.7): topic confounding is NOT excluded.")
    return out


# ---------------------------------------------------------------------------
# 入出力
# ---------------------------------------------------------------------------
def load_subject_blocks(spec: dict, dataset: pathlib.Path,
                        from_last_session: bool = False) -> list[dict]:
    """割付ファイル（assign.py の JSON に `file` を書き足したもの）を読み、特徴量を付ける。

    ⚠️★★ **1 ファイルに `session_start` が 2 本以上あれば止まる**
    （2026-08-10 の P010 block07・`notes.md §10-3`）。

    ★ 黙って最終セッションを採ってはならない。どのデータが解析に入ったかが結果から見えなくなり、
    `protocol.md §1` が (b) を却下した「**沈黙して間違った結果を出す**」と同型になる。
    → `from_last_session=True`（CLI では `--last-session-on-restart`）を**明示したときだけ**通し、
    使った事実は結果に刻む（`--unseal` の `confirmatory_status_forfeited` と同じ作法）。
    """
    subject = spec["subject"]
    out = []
    for b in spec["blocks"]:
        if "file" not in b:
            raise SystemExit(f"[NG] {subject} block {b['block']}: 'file' が無い "
                             f"(記録用紙の NDJSON ファイル名を書き足すこと・protocol.md §2.2)")
        p = dataset / "raw" / subject / b["file"]
        if not p.is_file():
            raise SystemExit(f"[NG] {subject} block {b['block']}: NDJSON が見つからない")
        # ★ `read_block` は止まらないので、**先に読んでから**判断する。
        #   ⚠️ ここで `session_starts` を別に呼ぶとファイルを 3 回読むことになる。
        blk = read_block(p, from_last_session=from_last_session)
        n_starts = blk["n_session_starts"]
        if n_starts > 1 and not from_last_session:
            raise SystemExit(
                f"[NG] {subject} block {b['block']}: この NDJSON に session_start が "
                f"{n_starts} 本ある。1 ブロック = 1 セッション (protocol.md §1) が破れており、"
                f"★ **このまま読むと前の試行の打鍵と空白が混入する**。\n"
                f"     ブロックの途中で「開始する」が押し直されたときに起きる"
                f"（アプリはこのときログを切り替えない）。\n"
                f"     ★ 最終セッションだけを採るなら --last-session-on-restart を付ける"
                f"（採った事実は結果に restart_handling として刻まれる・preregistration.md §3.10）。")
        # ⚠️★★ フラグを付けても、**最終セッションの起点が決められないなら止める**。
        #   ★ ここで黙って全行読むと、`restart_handling` に「最終セッションを採った」と
        #   刻まれるのに実際は混ざっている ＝ **結果そのものが嘘をつく**。
        #   （2 本目の `session_start` に有効な `t` が無いときに起きる）
        if n_starts > 1 and from_last_session and not blk["restart_cutoff_applied"]:
            raise SystemExit(
                f"[NG] {subject} block {b['block']}: session_start が {n_starts} 本あるが、"
                f"★ **最終セッションの起点が決められない**"
                f"（session_start 行に有効な t が 2 本揃っていない）。\n"
                f"     ⚠️ このまま読むと全行が混ざるのに restart_handling には"
                f"「最終セッションを採った」と刻まれる ＝ 結果が嘘をつく。\n"
                f"     ★ NDJSON を人が確認すること（preregistration.md §3.10）。")
        blk.update({"block": b["block"], "condition": b["condition"],
                    "topic_id": b.get("topic_id"), "arrangement": spec.get("arrangement"),
                    "produced_chars": b.get("produced_chars")})
        out.append(blk)
    return out


def cmd_verify_blocks(dataset: pathlib.Path, subject: str) -> int:
    """★ ラベルを一切読まない。ブロック長と打鍵数だけを出す（protocol.md §2.3-3）。

    これを走らせても「解析結果を見た」ことにならない（条件を読んでいないため）。
    """
    d = dataset / "raw" / subject
    if not d.is_dir():
        print(f"[NG] {d} が無い")
        return 1
    files = sorted(d.glob("*.ndjson"))
    if not files:
        print(f"[NG] {subject} の NDJSON が 1 本も無い")
        return 1
    print(f"[verify-blocks] {subject}: {len(files)} セッション"
          f"（★ 条件ラベルは読んでいない。長さと打鍵数だけ）")
    print("  #  | 打鍵数 | 長さ(mm:ss) | feat行 | 適格(>=100)")
    print("-----+--------+-------------+--------+------------")
    ok = True
    restarted: list[tuple[int, int]] = []
    for i, f in enumerate(files, start=1):
        b = read_block(f)                       # ファイル名は出力しない（日時が入るため）
        secs = b["span_ms"] / 1000.0
        good = b["n_keydowns"] >= MIN_KEYDOWNS_PER_BLOCK
        ok = ok and good
        if b["n_session_starts"] > 1:
            restarted.append((i, b["n_session_starts"]))
        mmss = f"{int(secs)//60:d}:{int(secs)%60:02d}"
        print(f" {i:3d} | {b['n_keydowns']:6d} | {mmss:>11s} "
              f"| {b['n_feat_rows']:6d} | {'○' if good else '× ★要記録'}"
              f"{'  ⚠️ 再開始あり' if b['n_session_starts'] > 1 else ''}")
    print()
    # ⚠️★★ 再開始は**表示するが赤にしない**（`protocol.md §7` / decisions D-3）。
    #   ★ ここを 0 以外で返すと、当日の実験者が「その場でやり直させる」誘因を持つ。
    #   それは §3.6（事後除外の禁止）を実質的に迂回する経路になる。
    if restarted:
        for i, k in restarted:
            print(f"  ⚠️★ {i} 本目に session_start が {k} 本ある = ブロックの途中で"
                  f"「開始する」が押し直された（アプリはログを切り替えない）。")
        print("  ★ ここでは何もしない（当日その場で対処しない・protocol.md §7）。")
        print("     解析時に analyze.py が止まる。--last-session-on-restart の判断はそのとき行う。")
        print()
    print("  ★ 5 分ブロックなら長さは 4:00〜5:00 に収まるはず。大きく外れたら起動/停止の取り違えを疑う。")
    print("  ★ 打鍵数を記録用紙に転記する。閾値割れでも **その場でやり直さない**（protocol.md §7）。")
    if len(files) not in (4, 10):
        print(f"  ⚠️ セッション数が {len(files)} 本。確証デザインは 10 本 / パイロット P-1 は 4 本。")
    if not ok:
        print("  ⚠️ 閾値割れのブロックがある。§2.9 の適格性ゲートに掛かる可能性が高い。")
    # ★ 常に 0 を返す。ここは**情報提示専用**であり、赤にすると
    #   「当日その場で対処する」誘因が生まれる（＝結果を見た後の介入になる・protocol.md §7）。
    return 0


def main() -> int:
    here = pathlib.Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="~/gse-dataset")
    ap.add_argument("--blocks-dir", default=str(here / "blocks"),
                    help="assign.py の JSON に NDJSON ファイル名を書き足したものを置くディレクトリ")
    ap.add_argument("--subject", help="--verify-blocks で対象にする被験者")
    ap.add_argument("--verify-blocks", action="store_true",
                    help="★ ラベルを読まずにブロック長と打鍵数だけを出す（実施当日の検算）")
    ap.add_argument("--out", default=str(here / "results" / "metrics.json"))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--unseal", action="store_true",
                    help="★ §3.4 の見る順序を満たしていないのに判定を見る。"
                         "使うと confirmatory_status_forfeited=true が結果に刻まれ、"
                         "その回は探索的として報告することになる (§5.3)")
    ap.add_argument("--last-session-on-restart", action="store_true",
                    help="★ 1 ファイルに session_start が 2 本以上あるブロックで、"
                         "**最後のセッションだけ**を読む (§3.10)。使うと restart_handling が"
                         "結果に刻まれる。⚠️ 確証ステータスは失わない"
                         "（規則は結果を見る前に凍結されている・§3.10）")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    dataset = pathlib.Path(a.dataset).expanduser()
    if a.verify_blocks:
        if not a.subject:
            ap.error("--verify-blocks には --subject が要る")
        return cmd_verify_blocks(dataset, a.subject)

    bdir = pathlib.Path(a.blocks_dir)
    specs = sorted(bdir.glob("P*.json")) if bdir.is_dir() else []
    if not specs:
        print(f"[NG] {bdir} に割付ファイル（P0xx.json）が無い。")
        print("     手順: python3 assign.py --subject P0xx --json > blocks/P0xx.json")
        print("           → 各 block に \"file\"（NDJSON 名）と \"produced_chars\" を書き足す")
        return 1

    # ⚠️★★ 誰が確証標本かを **config.json の sample_roster で強制する**（§2.4 / §2.8）。
    #   ★ ここが無かったので、パイロットが確証解析から外れていたのは
    #     「dataset に NDJSON が無いから」であって**コードの保証ではなかった**（2026-08-10 実測）。
    cfg_all = json.loads((here / "config.json").read_text(encoding="utf-8"))
    # ⚠️★★ roster は**ファイル名**で許可するので、中身の `subject` とずれていたら先に止める
    #   （`/cross-review` 2026-08-10・両者一致 HIGH）。★ ずれたまま進むと
    #   **roster が許可していない被験者の結果が確証解析に載る**。
    specs_loaded = []
    for p in specs:
        spec_ = json.loads(p.read_text(encoding="utf-8"))
        msg = check_subject_matches_filename(p.stem, spec_)
        if msg is not None:
            print(msg)
            return 1
        specs_loaded.append((p, spec_))
    roster_cfg = cfg_all.get("sample_roster")
    analysed, excluded, roster_errors, roster_notes = resolve_sample(
        roster_cfg,
        cfg_all.get("design", {}).get("n_subjects"),
        [p.stem for p in specs])
    if roster_errors:
        for m in roster_errors:
            print(m)
        print("     ★ 単一の正は config.json の sample_roster（blocks/*.json ではない）。")
        return 1
    # ★ 前提条件 8 / A-2（2026-09-27）: 募集を締めた（recruitment_closed.closed=true）ため
    #   n 未達の NG を続行に緩めたことを **[NOTE] で必ず可視化する**（黙って緩めない）。
    for note in roster_notes:
        print(note)
    # ⚠️★★★ 2026-09-27 修正（code-reviewer MEDIUM）: `bool(rc.get("closed"))` の素の型変換を
    #   `resolve_sample()` と ここで別々に持っていた（片方だけ直すと乖離する）。
    #   ★ `evaluate_recruitment_closed()` に一本化する（`resolve_sample` 側で既に roster_errors に
    #   出ているので、ここへ到達している時点で well-formed であることは検証済みだが、
    #   **値の導出ロジックは 1 か所だけに保つ**ため再計算せず同じ関数を呼ぶ）。
    recruitment_closed, _ = evaluate_recruitment_closed(roster_cfg)
    registered_k = roster_cfg.get("registered_k") if isinstance(roster_cfg, dict) else None
    # ⚠️ 外した被験者は**黙って消さない**（decisions D-5）。理由つきで出し、結果にも刻む。
    for e in excluded:
        print(f"[warn] {e['subject']} を確証解析から外した（sample_roster: {e['reason']}）")
    keep = set(analysed)
    specs_loaded = [(p, s) for p, s in specs_loaded if p.stem in keep]

    per_subject = []
    mchecks = {}
    # ★ 再開始のあったブロックを結果に刻む（§3.10・報告義務）。
    #   ⚠️ フラグ無しならここに到達する前に load_subject_blocks が止まるので、
    #   **中身が入るのは --last-session-on-restart を使ったときだけ**である。
    restarted_blocks: list[dict] = []
    for _path, spec in specs_loaded:
        blocks = load_subject_blocks(spec, dataset,
                                     from_last_session=a.last_session_on_restart)
        for b in blocks:
            if b.get("n_session_starts", 0) > 1:
                restarted_blocks.append({"subject": spec["subject"], "block": b["block"],
                                         "n_session_starts": b["n_session_starts"]})
        if spec.get("manipulation_check_answers"):
            mchecks[spec["subject"]] = manipulation_check(blocks, spec["manipulation_check_answers"])
        per_subject.append(analyse_subject(spec["subject"], blocks))

    errored = [s for s in per_subject if "error" in s]
    per_subject = [s for s in per_subject if "error" not in s]
    if errored:
        print(f"[warn] 割付ファイルが不正な被験者 {len(errored)} 名を解析から外した: "
              f"{[s['subject'] for s in errored]}")
    if not per_subject:
        print("[NG] 解析できる被験者が 1 名もいない")
        return 1

    # §3.4 の見る順序: 1. 操作チェック → 2. positive control → 3. FS-A / FS-B
    # ★ 分岐は interpretability() に閉じている（§2.5 第 3 版の 2 枝を含む）
    pcs = [s["positive_control"] for s in per_subject if not s["positive_control"].get("skipped")]
    status, interp, why = interpretability(mchecks, pcs)

    verdict = cohort_verdict(per_subject, interp, why)
    # ★ 解析 m = n_subjects_analysed（feature set 間で同じ値。§20 版 (ii)(c) のゲート）。
    #   ⚠️★★★ 2026-09-27 修正（code-reviewer HIGH・実測で再現）: `verdict` は
    #   `{"interpretable": bool, "interpretability_reason": str, "FS_A": {...}, "FS_B": {...}}`
    #   の順で、`next(iter(verdict.values()))` は先頭の `interpretable`（bool）を返すため
    #   `["n_subjects_analysed"]` で必ず TypeError になっていた（`--selftest` は
    #   `check_zero_analysed()` を直接叩くだけで `main()` を通らないため見逃していた）。
    #   ★ FEATURE_SETS の先頭キー（"FS_A"）を名指しで引く（feature set 間で同値という
    #   `cohort_verdict` の前提はコメントのとおり）。
    analysed_m = verdict[next(iter(FEATURE_SETS))]["n_subjects_analysed"] if verdict else 0
    # ⚠️★★★ 2026-09-27 修正（code-reviewer 2 巡目 Medium）: `assert` は (a) `python3 -O` で消える、
    #   (b) 発火時に本ファイルの他の門と違う例外形（AssertionError）になり [NG]/return 1 の
    #   規約から外れる、という理由で他の検査と揃えて print+return に書き換える。
    #   ⚠️ 現状の `cohort_verdict()` では `n = len(usable)` が feature set 間で共通の式なので
    #   この分岐は実際には発火しない（死んだ検査）。それでも将来 `cohort_verdict()` が
    #   feature set ごとに異なる母集団を使うよう変わったときの回帰検知として残す。
    _m_mismatch = [(k, v["n_subjects_analysed"]) for k, v in verdict.items()
                   if k in FEATURE_SETS and v["n_subjects_analysed"] != analysed_m]
    if _m_mismatch:
        print(f"[NG] 解析 m が feature set 間で不一致（前提が壊れている）: {_m_mismatch}")
        return 1
    m_gate = check_zero_analysed(analysed_m)
    if m_gate:
        print(m_gate)
        return 1

    result = {
        "experiment": "20260801-controlled-friction-task",
        "gate": "G1",
        "preregistration": "preregistration.md (frozen; authoritative over this output)",
        "preregistration_revision": PREREG_REVISION,
        "decision_status": status,
        "decision_status_values": {
            "INTERPRETABLE": "3.4 order satisfied; read the 3.3 verdict",
            "MANIPULATION_CHECK_NOT_SUPPLIED": "3.4-1 not read yet",
            "MANIPULATION_CHECK_FAILED": "2.6 failed; do not interpret separation",
            "POSITIVE_CONTROL_NOT_RUN": "no eligible 10-block subject",
            "G1_VOID": "2.5: positive control failed AND the test could have rejected -> instrument fault suspected",
            "VERDICT_WITHHELD": "2.5 (since revision 3): positive control failed but the test could NOT have "
                                "rejected for any failing subject -> underpower, NOT an instrument fault",
        },
        # ⚠️★★ §3.10: 1 ファイルに複数セッションがあったブロックの扱いを**必ず刻む**
        #   （2026-08-10 の P010 block07）。★ 規則は結果を見る**前**に凍結したので
        #   確証ステータスは失わない。刻むのは「どのデータが解析に入ったか」を残すためである。
        "restart_handling": {
            "rule": "last session only (preregistration.md 3.10; frozen before any analysis run)",
            "flag_used": bool(a.last_session_on_restart),
            "blocks": restarted_blocks,
        },
        # ⚠️★★ 誰を確証標本として解析し、誰をなぜ外したかを**必ず刻む**（§2.4 / §2.8）。
        #   ★ 「絞る」実装は必ず「黙って落とす」危険を連れてくるので、結果から追えるようにする。
        "sample_roster_applied": {
            "source": "config.json sample_roster (single source of truth; blocks/*.json is NOT consulted)",
            "n_subjects_frozen": cfg_all.get("design", {}).get("n_subjects"),
            "analysed": analysed,
            "excluded": excluded,
        },
        # ⚠️★★ 前提条件 8 / A-2（2026-09-27）: 登録 k / 解析 m を締めの宣言と一緒に必ず刻む。
        #   ★ 内訳（未完了・やめた・削除の求め）は書かない（preregistration.md 第 20 版「公表物の書き方」）。
        "sample_counts": {
            "registered_k": registered_k,
            "analysed_m": analysed_m,
            "recruitment_closed": recruitment_closed,
            "note": "内訳（未完了・やめた・削除の求め）は書かない（preregistration.md 第 20 版「公表物の書き方」）",
        },
        "reading_order_3_4": ["1_manipulation_check", "2_positive_control", "3_feature_sets"],
        "1_manipulation_check": mchecks or {"supplied": False},
        "2_positive_control": {s["subject"]: s["positive_control"] for s in per_subject},
        "3_verdict": verdict,
        "per_subject": per_subject,
        "subjects_with_invalid_assignment_files": errored,
        "constants": {"lambda": LAMBDA, "silence_ms": SILENCE_MS,
                      "min_keydowns_per_block": MIN_KEYDOWNS_PER_BLOCK,
                      "auc_median_min": AUC_MEDIAN_MIN, "alpha": ALPHA},
        "hmm_version": "TO_BE_STAMPED_AT_EXECUTION (env.md)",
        "privacy": "no session timestamps, no file names, no written text appear in this output",
    }
    # ★ §5.3（第 4 版）: §3.4 の見る順序を実装で強制する。
    #   interpretable=False なら、明示的に --unseal しない限り判定を出さない。
    sealed = (not interp) and not a.unseal
    if sealed:
        result = seal_verdict(result)
    result["verdict_sealed"] = sealed
    if a.unseal and not interp:
        result["confirmatory_status_forfeited"] = True
        result["confirmatory_status_forfeited_note"] = (
            "The 3.4 viewing order was NOT satisfied and --unseal was used. "
            "This run must be reported as EXPLORATORY (preregistration.md 5.3).")

    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[ok] {out}  status={status} interpretable={interp}")
    if not interp:
        print(f"       {why}")
    if sealed:
        print("  [SEALED] §3.4 の見る順序を満たしていないため、§3.3 の判定を出力していない。")
        print("           ラベル非依存の到達可能性診断 (§5.2) は per_subject に残してある。")
        print("           どうしても見るなら --unseal（その回は探索的になる・§5.3）。")
        return 0
    if a.unseal and not interp:
        print("  [UNSEALED] ★ 確証性を放棄した。この回は探索的として報告すること (§5.3)。")
    for name in FEATURE_SETS:
        v = result["3_verdict"][name]
        print(f"  {name}: separated={v['separated']} median_auc={v['criterion_2_median_auc']} "
              f"fisher_p={v['fisher'].get('p_value')}")
    return 0


# ---------------------------------------------------------------------------
# 自己検証
# ---------------------------------------------------------------------------
def _synthetic(sep: float, n: int = 8, d: int = 14, seed: int = 0) -> tuple[list[list[float]], list[int]]:
    """再現可能な合成データ（乱数を使わず決定的に作る）。sep が大きいほど分離しやすい。"""
    labels = [1, 0] * (n // 2)
    rows = []
    for i, y in enumerate(labels):
        row = []
        for j in range(d):
            base = math.sin((i + 1) * (j + 1) * 1.7 + seed)   # 決定的な「雑音」
            row.append(base + (sep if (y == 1 and j == 0) else 0.0))
        rows.append(row)
    return rows, labels


def selftest() -> int:
    fails: list[str] = []

    # 0) ★ 版の一致（E-6 / E-7 の教訓を機械化する）
    #    事前登録を改訂したら、その規則を実行するスクリプトが同じ版になっているか。
    #    ⚠️ この検査が無かったため、PREREG_REVISION は第 4 版のあいだ 3 のまま残っていた。
    here_ = pathlib.Path(__file__).resolve().parent
    cfg_path = here_ / "config.json"
    try:
        cfg_rev = json.loads(cfg_path.read_text(encoding="utf-8"))["revision"]["version"]
    except Exception as e:                                  # noqa: BLE001 - 検査そのものを落とさない
        fails.append(f"config.json の revision.version を読めない: {e}")
    else:
        if cfg_rev != PREREG_REVISION:
            fails.append(
                f"★ 事前登録の版と実装の版が食い違っている: config.json={cfg_rev} / "
                f"analyze.py PREREG_REVISION={PREREG_REVISION}。"
                f"文書を改訂したら、その規則を実行するスクリプトを同じ版にすること")

    # ⚠️★★ **単一真実源そのもの**（`preregistration.md`）と突き合わせる（2026-08-10 追加）。
    #   ★ 上の検査は `analyze.py ↔ config.json` しか見ていなかった。
    #   ⚠️ **両方が同じだけ遅れていれば緑になる**——実際に、文書が第 13 版まで進んだのに
    #   config.json と PREREG_REVISION が **10 のまま 3 版遅れて緑だった**（実測）。
    #   ★ これは「名前で引く対策は 1 つの真実源の中でしか効かない」と同じ型である:
    #   ★★ **検査は「どちら側を見ているか」を問わなければならない。**
    try:
        doc_rev = prereg_revision_from_doc(here_ / "preregistration.md")
    except OSError as e:                                    # noqa: BLE001 - 検査そのものを落とさない
        fails.append(f"preregistration.md を読めない（版の検査ができない）: {e}")
        doc_rev = PREREG_REVISION          # ★ 下の比較を二重に赤くしない
    if doc_rev is None:
        fails.append("★ preregistration.md から改訂番号を読めない"
                     "（見出しの書式が変わった? 検査が空回りする）")
    elif doc_rev != PREREG_REVISION:
        fails.append(
            f"★★ 事前登録**文書**の版と実装の版が食い違っている: "
            f"preregistration.md=第 {doc_rev} 版 / analyze.py PREREG_REVISION={PREREG_REVISION}。"
            f"⚠️ config.json だけを合わせても意味が無い（両方が同じだけ遅れうる）")

    # 1) 明確に分離する合成データ -> AUC 1.0 / p = 1/70
    rows, labels = _synthetic(sep=50.0)
    r = exact_permutation_test(rows, labels)
    if r["n_permutations"] != 70:
        fails.append(f"並べ替えが全数列挙になっていない: {r['n_permutations']} != 70")
    if r["observed_auc"] < 0.999:
        fails.append(f"分離する合成データで AUC={r['observed_auc']} (期待 1.0)")
    # ⚠️ p が厳密に 1/70 になるとは限らない。8 点 × 14 次元では**別のラベル割付でも**
    #    線形分離できてしまう（帰無分布の上端が縮退する）。ここで見るのは
    #    「有意に到達できること」と「最小 p が 1/70 として計算されていること」である。
    if not r["significant"] or r["p_value"] >= ALPHA:
        fails.append(f"分離する合成データで有意にならない: p={r['p_value']}")
    if abs(r["theoretical_min_p"] - 1 / 70) > 1e-6:
        fails.append(f"理論上の最小 p が違う: {r['theoretical_min_p']} != {1/70:.6f}")
    if not (r["theoretical_min_p"] <= r["attainable_min_p_for_this_subject"] <= 1.0):
        fails.append("到達可能な最小 p が理論最小を下回っている（診断値の定義違反）")
    if "test_can_reject_at_all" not in r:
        fails.append("test_can_reject_at_all が出力されていない (D-5 の診断)")

    # 2) ラベルが無情報 -> 有意にならない
    rows2, labels2 = _synthetic(sep=0.0)
    r2 = exact_permutation_test(rows2, labels2)
    if r2["p_value"] < ALPHA:
        fails.append(f"無情報ラベルで p={r2['p_value']} < {ALPHA}（偽陽性）")

    # 3) 分散ゼロ特徴が潰れ、例外にならない（§5.1）
    rows3 = [row[:] for row in rows]
    for row in rows3:
        row[3] = 7.0                       # ime_dwell_med 相当を定数にする
    c = cv_auc(rows3, labels)
    if 3 not in c["degenerate_feature_folds"]:
        fails.append("分散ゼロ特徴が degenerate として報告されていない (§5.1)")
    if c["degenerate_feature_folds"].get(3) != c["n_folds"]:
        fails.append("分散ゼロ特徴が全 fold で潰れていない")

    # 4) positive control の並べ替えは C(10,2)=45
    rows4, _ = _synthetic(sep=50.0, n=10)
    lab4 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    r4 = exact_permutation_test(rows4, lab4)
    if r4["n_permutations"] != 45:
        fails.append(f"positive control の並べ替えが {r4['n_permutations']} != 45")

    # 5) Fisher は n<2 で適用されない（§3.9）
    if fisher_combine([0.01])["applied"]:
        fails.append("n=1 で Fisher が適用されている (§3.9 違反)")
    f = fisher_combine([0.014, 0.014])
    if not (0.0 < f["p_value"] < 0.01):
        fails.append(f"Fisher の値が異常: {f}")

    # 5b) ★ §2.5（第 3 版）: positive control ✗ の扱いが到達可能性で分岐する
    mc_pass = {"P001": {"passed": True}}
    pc_pass = {"passed": True, "test_can_reject_at_all": True}
    pc_fail_attainable = {"passed": False, "test_can_reject_at_all": True}
    pc_fail_unattainable = {"passed": False, "test_can_reject_at_all": False}

    st, it, _ = interpretability(mc_pass, [pc_pass])
    if st != "INTERPRETABLE" or not it:
        fails.append(f"positive control 合格なのに status={st} interpretable={it}")

    st, it, why = interpretability(mc_pass, [pc_fail_attainable])
    if st != "G1_VOID" or it:
        fails.append(f"✗ かつ到達可能なのに G1_VOID にならない: status={st} (§2.5)")

    st, it, why = interpretability(mc_pass, [pc_fail_unattainable])
    if st != "VERDICT_WITHHELD" or it:
        fails.append(f"✗ かつ到達不能なのに判定保留にならない: status={st} (§2.5 第 3 版)")
    if "IS VOID" in why:
        fails.append("判定保留の説明文に 'IS VOID' が混ざっている（計器故障と誤診させる）")

    # ★ 1 名でも到達可能で落ちていれば G1_VOID（検出力不足で薄めない・保守側）
    st, _, _ = interpretability(mc_pass, [pc_fail_unattainable, pc_fail_attainable])
    if st != "G1_VOID":
        fails.append(f"到達可能な失敗が混ざっているのに G1_VOID にならない: status={st}")

    # ★ どちらの枝でも §3.3 を読まない = 判定は緩んでいない
    for pc in (pc_fail_attainable, pc_fail_unattainable):
        if interpretability(mc_pass, [pc])[1]:
            fails.append("positive control ✗ なのに interpretable=True になっている（判定が緩んでいる）")

    # ★ 見る順序（§3.4）: 操作チェックが先。positive control が合格でも止まる
    if interpretability({}, [pc_pass])[0] != "MANIPULATION_CHECK_NOT_SUPPLIED":
        fails.append("操作チェック未提出なのに先に進んでいる (§3.4-1)")
    if interpretability({"P001": {"passed": False}}, [pc_pass])[0] != "MANIPULATION_CHECK_FAILED":
        fails.append("操作チェック不合格なのに先に進んでいる (§3.4-1)")

    # 5c) ★ §5.3（第 4 版）: 見る順序を満たさないとき判定が封印される
    fake = {
        "1_manipulation_check": {"P001": {"passed": False}},
        "2_positive_control": {"P001": {"passed": True, "p_value": 0.02}},
        "3_verdict": {
            "interpretable": False, "interpretability_reason": "manipulation check FAILED",
            "FS_A": {"separated": True, "criterion_2_median_auc": 0.99,
                     "fisher": {"p_value": 0.001}},
        },
        "per_subject": [{
            "subject": "P001",
            "eligibility": {"eligible_for_primary": True},
            "positive_control": {"passed": True, "p_value": 0.02},
            "primary": {"FS_A": {"p_value": 0.001, "observed_auc": 0.99,
                                 "max_abs_coefficient": 3.1,
                                 "test_can_reject_at_all": True,
                                 "attainable_min_p_for_this_subject": 0.0143,
                                 "null_auc_p95": 0.9375}},
        }],
    }
    sealed = seal_verdict(json.loads(json.dumps(fake)))

    if "FS_A" in sealed["3_verdict"]:
        fails.append("封印後も 3_verdict に特徴量セットの判定が残っている (§5.3)")
    if sealed["3_verdict"].get("interpretable") is not False:
        fails.append("封印で interpretable まで消えている（止まった理由が読めなくなる）")
    if not sealed["3_verdict"].get("interpretability_reason"):
        fails.append("封印で止まった理由まで消えている")

    sp = sealed["per_subject"][0]["primary"]["FS_A"]
    for k in ("p_value", "observed_auc", "max_abs_coefficient"):
        if k in sp:
            fails.append(f"封印後も per_subject.primary に {k} が残っている (§5.3)")
    # ★ ラベル非依存の診断値（§5.2 の報告義務）は封印しない
    for k in ("test_can_reject_at_all", "attainable_min_p_for_this_subject", "null_auc_p95"):
        if k not in sp:
            fails.append(f"ラベル非依存の診断値 {k} まで封印している (§5.2 の報告義務違反)")

    # ★ §3.4 で「先に見る」ものは封印しない
    if sealed["per_subject"][0]["positive_control"].get("p_value") != 0.02:
        fails.append("positive control を封印している (§3.4 の順序で先に見るもの)")
    if sealed["1_manipulation_check"]["P001"]["passed"] is not False:
        fails.append("操作チェックを封印している (§3.4 の順序で先に見るもの)")
    if sealed["2_positive_control"]["P001"].get("p_value") != 0.02:
        fails.append("2_positive_control を封印している (§3.4 の順序で先に見るもの)")

    # 6) 適格性ゲートは打鍵数だけで判定し、ブロックを落とさない（§2.9）
    blks = [{"block": i, "condition": ("HI" if i % 2 else "LO"), "n_keydowns": 500} for i in range(2, 10)]
    blks += [{"block": 1, "condition": "copy", "n_keydowns": 500},
             {"block": 10, "condition": "copy", "n_keydowns": 500}]
    e = eligibility(blks)
    if not (e["eligible_for_primary"] and e["eligible_for_positive_control"]):
        fails.append("十分な打鍵で不適格になっている")
    blks[0]["n_keydowns"] = 9              # P014 型
    e2 = eligibility(blks)
    if e2["eligible_for_primary"]:
        fails.append("9 打鍵のブロックがあるのに適格になっている (§2.9)")
    if len(e2["keydowns_per_block"]) != 10:
        fails.append("適格性ゲートがブロックを落としている（落としてはいけない）")

    # 7) ブロック特徴量: silence 0 個なら 3 値とも 0（§3.2 の事前宣言）
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "b.ndjson"
        lines = [json.dumps({"type": "meta", "session_start": 0, "hmm_version": "x"})]
        for i in range(120):               # 100ms 間隔 -> silence なし
            lines.append(json.dumps({"type": "key", "t": i * 100, "category": "alphabetic", "press": True}))
            lines.append(json.dumps({"type": "key", "t": i * 100 + 40, "category": "alphabetic", "press": False}))
        lines.append(json.dumps({"type": "key", "t": 500, "category": "backspace", "press": True}))
        lines.append(json.dumps({"type": "feat", "t": 1000, "f1": 100.0, "f3": 0.1, "f4": 5.0,
                                 "f5": 0.0, "f6": 0.0}))
        lines.append(json.dumps({"type": "paste", "t": 2000, "external_paste_chars": 12}))
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        b = read_block(p)
        ft = b["features"]
        if b["n_keydowns"] != 121:
            fails.append(f"keydown 数が違う: {b['n_keydowns']} != 121")
        if not (ft["silence_p50"] == ft["silence_p90"] == ft["silence_max"] == 0.0):
            fails.append("silence 0 個なのに 3 値が 0 でない (§3.2)")
        if abs(ft["bs_rate"] - 1 / 121) > 1e-9:
            fails.append(f"bs_rate が違う: {ft['bs_rate']}")
        if ft["external_paste_chars"] != 12.0:
            fails.append("external_paste_chars を拾えていない")
        if ft["ime_dwell_med"] != 0.0:
            fails.append("ime_shadow が無いのに ime_dwell_med が 0 でない (macOS 実施の想定・§5.1)")
        if ft["f1"] != 100.0:
            fails.append("FS-A が feat 行から取れていない (design D-2)")

        # silence / burst が定義どおり出るか
        p2 = pathlib.Path(td) / "c.ndjson"
        ts = [0, 100, 200, 5000, 5100, 12000]      # silence: 4800ms, 6900ms
        p2.write_text("\n".join(
            json.dumps({"type": "key", "t": t, "category": "alphabetic", "press": True}) for t in ts
        ) + "\n", encoding="utf-8")
        f2 = read_block(p2)["features"]
        if f2["silence_max"] != 6900.0:
            fails.append(f"silence_max が違う: {f2['silence_max']} != 6900")
        if f2["burst_p90"] != 3.0:
            fails.append(f"burst_p90 が違う: {f2['burst_p90']} != 3 (バースト長 [3,2,1])")

    # ⚠️★★ 8) 1 ファイルに 2 セッション（2026-08-10 の P010 block07・`notes.md §10-3`）
    #    ★ `read_block` はファイル全体を 1 ブロックとして読むので、**黙って前の試行を混ぜる**。
    #      `protocol.md §1` が (b) を却下した「沈黙して間違った結果を出す」そのものである。
    #    → 解析経路は既定で止まり、`--last-session-on-restart` を明示したときだけ通す。
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)

        def _sess(start_t: int, keys: list[int]) -> str:
            out = [json.dumps({"type": "session_start", "t": start_t})]
            for t in keys:
                out.append(json.dumps({"type": "key", "t": t, "category": "alphabetic",
                                       "press": True}))
            return "\n".join(out) + "\n"

        head = json.dumps({"type": "meta", "session_start": 0, "hmm_version": "x",
                           "g1_mode": "marker"}) + "\n"
        # 第 1 セッション = 失敗した試行（打鍵 3 件）／第 2 セッション = 本番（打鍵 5 件）
        two = head + _sess(0, [10, 20, 30]) + _sess(1000, [1010, 1020, 1030, 1040, 1050])
        one = head + _sess(0, [10, 20, 30, 40, 50])

        p_two = d / "two.ndjson"
        p_two.write_text(two, encoding="utf-8")
        p_one = d / "one.ndjson"
        p_one.write_text(one, encoding="utf-8")

        # ★ read_block は**数えて返すだけ**（ここで止めない → decisions D-3）。
        #   ⚠️ 止めると --verify-blocks が道連れで死ぬ。
        b2 = read_block(p_two)
        if b2.get("n_session_starts") != 2:
            fails.append(f"read_block が session_start を数えていない: {b2.get('n_session_starts')}")
        if b2["n_keydowns"] != 8:
            fails.append(f"既定の read_block は全行を読むこと: {b2['n_keydowns']} != 8")
        # ★ 対照: 1 セッションなら 1 と数える（0 や None にしない）
        b1 = read_block(p_one)
        if b1.get("n_session_starts") != 1:
            fails.append(f"1 セッションを 1 と数えていない: {b1.get('n_session_starts')}")

        # ★★ from_last_session=True で**最終セッションだけ**を読む
        b2l = read_block(p_two, from_last_session=True)
        if b2l["n_keydowns"] != 5:
            fails.append(f"最終セッションだけを読めていない: {b2l['n_keydowns']} != 5")
        if b2l["span_ms"] != 40:
            fails.append(f"最終セッションの span が違う: {b2l['span_ms']} != 40")
        # ⚠️ ★ 対照: **1 セッションのファイルはフラグの有無で結果が変わらない**。
        #   これが無いと、フラグが正常なブロックまで削っていても気づけない。
        if read_block(p_one, from_last_session=True)["n_keydowns"] != b1["n_keydowns"]:
            fails.append("★ 1 セッションのファイルでフラグの有無が結果を変えている")

        # ★★ 解析経路は既定で**止まる**（黙って混ぜない）
        spec = {"subject": "PX", "arrangement": "A",
                "blocks": [{"block": 1, "condition": "copy", "topic_id": "copy",
                            "file": "two.ndjson"}]}
        raw = d / "raw" / "PX"
        raw.mkdir(parents=True)
        (raw / "two.ndjson").write_text(two, encoding="utf-8")
        (raw / "one.ndjson").write_text(one, encoding="utf-8")
        try:
            load_subject_blocks(spec, d)
            fails.append("★ 2 セッションのファイルを既定で解析に通してはならない (protocol.md §1)")
        except SystemExit as e:
            if "session_start" not in str(e):
                fails.append(f"止まる理由が session_start だと分からない: {e}")
        # ★ フラグを明示したら通り、最終セッションだけを採る
        try:
            got = load_subject_blocks(spec, d, from_last_session=True)
            if got[0]["n_keydowns"] != 5:
                fails.append(f"フラグ付きで最終セッションを採れていない: {got[0]['n_keydowns']}")
        except SystemExit as e:
            fails.append(f"--last-session-on-restart を付けても止まった: {e}")
        # ⚠️ ★ 対照: 1 セッションだけの被験者は**フラグ無しでも通る**
        spec1 = dict(spec, blocks=[dict(spec["blocks"][0], file="one.ndjson")])
        try:
            load_subject_blocks(spec1, d)
        except SystemExit as e:
            fails.append(f"1 セッションのファイルで止まってはならない: {e}")

        # ⚠️★★ **2 つの「数え方」がずれていた**（2026-08-10 の /cross-review で Codex が指摘・再現済み）。
        #   `validate_blocks.py::scan_ndjson` は `type` だけで数えるのに、
        #   旧 `session_start_ts`（現 `session_starts`）は「`t` が有効な int」まで要求していた。
        #   ★ 2 本目の `session_start` の `t` が壊れていると、
        #   **validate_blocks は 2 と数えて FAIL するのに analyze は 1 と数えて黙って混ぜた**（実測）。
        #   ⚠️ 本タスクが塞ごうとした「沈黙して間違った結果を出す」経路が、狭い条件で開いたままだった。
        #   → ★ **構造の数え方（type のみ）と、cutoff に使う時刻（有効な int）を分ける。**
        broken_t = (head
                    + json.dumps({"type": "session_start", "t": 0}) + "\n"
                    + json.dumps({"type": "key", "t": 10, "category": "alphabetic",
                                  "press": True}) + "\n"
                    + json.dumps({"type": "session_start", "t": "1000"}) + "\n"   # ⚠️ 壊れた t
                    + json.dumps({"type": "key", "t": 1010, "category": "alphabetic",
                                  "press": True}) + "\n")
        p_bt = d / "broken_t.ndjson"
        p_bt.write_text(broken_t, encoding="utf-8")
        (raw / "broken_t.ndjson").write_text(broken_t, encoding="utf-8")
        if read_block(p_bt)["n_session_starts"] != 2:
            fails.append("★ session_start の数え方が validate_blocks と揃っていない"
                         "（t が壊れていても 2 本は 2 本と数えること）")
        spec_bt = dict(spec, blocks=[dict(spec["blocks"][0], file="broken_t.ndjson")])
        try:
            load_subject_blocks(spec_bt, d)
            fails.append("★★ 2 本目の t が壊れていても、2 セッションなら止めること"
                         "（黙って混ぜる経路が残っている）")
        except SystemExit:
            pass
        # ★★ フラグを付けても、**起点が決められないなら止める**。
        #   ⚠️ ここで黙って全行読むと、restart_handling に「最終セッションを採った」と
        #   刻まれるのに実際は混ざっている ＝ **結果が嘘をつく**。
        try:
            load_subject_blocks(spec_bt, d, from_last_session=True)
            fails.append("★★ 最終セッションの起点が決められないのに通してはならない"
                         "（restart_handling が嘘になる）")
        except SystemExit as e:
            if "起点" not in str(e):
                fails.append(f"止まる理由が「起点が決められない」だと分からない: {e}")

    # ⚠️★★ 9) 確証標本の roster（`§2.4` / `§2.8`・2026-08-10 追加）
    #    ★ **誰が確証標本か**をコードで強制する。それまで `analyze.py` は
    #      `confirmatory` フラグを**一度も見ておらず**、glob `P*.json` は `PILOT-*` まで拾っていた。
    #      ⚠️ パイロットが確証解析から外れていたのは「dataset に NDJSON が無いから」であって
    #      **コードの保証ではなかった**（実測で確認）。
    #    ★ 純関数なので、境界をファイル無しで直接固定できる。
    ROSTER = {"confirmatory": ["P011", "P012", "P013"],
              "pilot": ["PILOT-mac", "PILOT-win"],
              "shakedown": ["P010"]}
    PRESENT = ["P010", "P011", "P012", "P013", "PILOT-mac", "PILOT-win"]

    # ★ 正常系: confirmatory の 3 名だけが解析に入る
    got, exc, errs, _notes = resolve_sample(ROSTER, 3, PRESENT)
    if errs:
        fails.append(f"★ 正常な roster でエラーになった: {errs[0]}")
    if got != ["P011", "P012", "P013"]:
        fails.append(f"★ confirmatory だけを解析対象にしていない: {got}")
    # ⚠️ 外した人は**黙って消さず**、理由つきで返す（decisions D-5）
    by_subj = {e["subject"]: e["reason"] for e in exc}
    if by_subj.get("P010") != "shakedown" or by_subj.get("PILOT-mac") != "pilot":
        fails.append(f"★ 外した被験者と理由を返していない: {exc}")

    # ⚠️★ 境界 1: `sample_roster` キー自体が無い → 止まる
    #    （「古い config なら全員」と読むと保護が黙って消える）
    if not resolve_sample(None, 3, PRESENT)[2]:
        fails.append("★ sample_roster が無いのに通してはならない")
    # ⚠️★ 境界 2: confirmatory が空 → 止まる（空を「全員」と読まない）
    if not resolve_sample(dict(ROSTER, confirmatory=[]), 3, PRESENT)[2]:
        fails.append("★ confirmatory が空なのに通してはならない")
    # ⚠️★ 境界 3: roster に居るが割付ファイルが無い（欠員）→ 止まる
    #    ★ 黙って n-1 で解析しない
    if not resolve_sample(ROSTER, 3, ["P011", "P012", "PILOT-mac"])[2]:
        fails.append("★ 確証標本に欠員があるのに通してはならない")
    # ⚠️★ 境界 4: roster のどこにも無い割付ファイル → **報告して除外**（止めはしない）
    got4, exc4, errs4, _notes4 = resolve_sample(ROSTER, 3, PRESENT + ["P099"])
    if errs4:
        fails.append(f"★ 未登録の割付ファイルで止めてはならない（報告して外す）: {errs4[0]}")
    if {e["subject"]: e["reason"] for e in exc4}.get("P099") != "not_in_roster":
        fails.append("★ 未登録の割付ファイルを黙って落としている（報告すること・D-5）")
    # ⚠️★ 境界 5: 収集済みが n に達していない → 止まる（§2.4-4 optional stopping の禁止）
    if not resolve_sample(dict(ROSTER, confirmatory=["P011", "P012"]), 3, PRESENT)[2]:
        fails.append("★★ n 未達で解析を通してはならない（§2.4-4 の機械化）")

    # ⚠️★★ 境界 5 の拡張（前提条件 8 / A-2・2026-09-27）: 募集を締めたか否かで
    #   n 未達の扱いが分岐する（preregistration.md 第 20 版 (i)(ii) の規則の機械化）。
    # ★ negative control: 締めていなければ n 未達は NG のまま（既定を緩めない）
    _, _, errs_open, notes_open = resolve_sample(
        dict(ROSTER, confirmatory=["P011", "P012"], recruitment_closed={"closed": False}),
        3, PRESENT)
    if not errs_open:
        fails.append("★★ 締めていなければ n 未達は NG のまま、のはずが通してしまった"
                     "（closed=false で保護が緩んだ）")
    if notes_open:
        fails.append("★ 締めていないのに NOTE を出している（NG のときに NOTE は要らない）")
    # ★ 締めた後は n=1 でも解析する（NG を出さず、NOTE を出して続行する）
    #   ⚠️ 2026-09-27: 厳密化に伴い date / decided_before_seeing_results も必須になった。
    RC_CLOSED_VALID = {"closed": True, "date": "2026-09-27", "decided_before_seeing_results": True}
    _, _, errs_closed, notes_closed = resolve_sample(
        dict(ROSTER, confirmatory=["P011"], recruitment_closed=RC_CLOSED_VALID),
        3, PRESENT)
    if errs_closed:
        fails.append(f"★ 締めた後は n 未達を NG にしてはならない: {errs_closed}")
    if not notes_closed:
        fails.append("★ 締めた後に n 未達で続行するときは NOTE を出すこと（黙って緩めない）")

    # ⚠️★★★ 2026-09-27 追加（Codex / security-checker / code-reviewer 3 系統の指摘・fail-open の再発防止）:
    #   `closed` が真偽値でない・`date` / `decided_before_seeing_results` が欠けている場合は
    #   **緩めてはならない**（NG のまま・NOTE を出さない）。
    for bad_label, bad_rc in [
        ("closed が文字列 \"false\"", {"closed": "false"}),
        ("closed が文字列 \"true\"", {"closed": "true"}),
        ("closed が数値 1", {"closed": 1}),
        ("date が欠落", {"closed": True, "decided_before_seeing_results": True}),
        ("date が不正な形式", {"closed": True, "date": "2026/09/27",
                              "decided_before_seeing_results": True}),
        ("date が実在しない日付（書式は正しい）", {"closed": True, "date": "2026-99-99",
                                          "decided_before_seeing_results": True}),
        ("decided_before_seeing_results が欠落", {"closed": True, "date": "2026-09-27"}),
        ("decided_before_seeing_results が false",
         {"closed": True, "date": "2026-09-27", "decided_before_seeing_results": False}),
    ]:
        _, _, errs_bad, notes_bad = resolve_sample(
            dict(ROSTER, confirmatory=["P011"], recruitment_closed=bad_rc), 3, PRESENT)
        if not errs_bad:
            fails.append(f"★★ fail-open の再発: {bad_label} なのに n 未達を NG にしなかった")
        if notes_bad:
            fails.append(f"★★ fail-open の再発: {bad_label} なのに NOTE で緩めてしまった")
    # ⚠️★ registered_k の矛盾は NG（台帳と config のずれを黙認しない）
    if not resolve_sample(dict(ROSTER, registered_k=2), 3, PRESENT)[2]:
        fails.append("★ registered_k(2) < confirmatory 人数(3) の矛盾を NG にしていない")
    if resolve_sample(dict(ROSTER, registered_k=3), 3, PRESENT)[2]:
        fails.append("★ registered_k(3) == confirmatory 人数(3) は矛盾でないのに NG にしている")
    if not resolve_sample(dict(ROSTER, registered_k="2"), 3, PRESENT)[2]:
        fails.append("★ registered_k が文字列なのに NG にしていない（数値である契約）")

    # ⚠️★★ 完了者 0 名なら確証解析は行えない（preregistration.md 第 20 版 (ii)(c)・m=0 ゲート）
    if check_zero_analysed(0) is None:
        fails.append("★★ 解析 m=0 なのに NG にしていない（第 20 版 (ii)(c)）")
    if check_zero_analysed(1) is not None:
        fails.append("★ 解析 m>=1 なのに NG にしている（過剰検査）")

    # ⚠️★ 境界 6: 同じ被験者が 2 つのリストに居る → 止まる（分類が曖昧なまま進まない）
    if not resolve_sample(dict(ROSTER, shakedown=["P010", "P011"]), 3, PRESENT)[2]:
        fails.append("★ 被験者が 2 つのリストに重複しているのに通してはならない")
    # ⚠️★ 境界 6b: **同じリスト内**の重複でも止まる（`len(conf)` を水増しさせない）。
    #    ★ /cross-review 2026-08-10 で Codex が「現状エラーにならない」と述べたが、
    #      実測では**エラーになった**（seen が同一 kind でも累積するため）。
    #      ⚠️ ただし専用の検査が無かったので、ここで固定する。
    e6b = resolve_sample(dict(ROSTER, confirmatory=["P011", "P011", "P012"]), 3, PRESENT)[2]
    if not e6b:
        fails.append("★ 同一リスト内の重複でも止めること（len(confirmatory) の水増しを防ぐ）")
    elif "confirmatory と confirmatory" in e6b[0]:
        fails.append("★ 同一リスト内の重複のメッセージが「confirmatory と confirmatory」になっている"
                     "（読み手に何が起きたか伝わらない）")

    # ⚠️★★ 割付ファイル名と中身の `subject` の一致（`/cross-review` 2026-08-10・両者一致 HIGH）
    #    ★ roster は**ファイル名**で許可するのに、結果に刻まれるのは `spec["subject"]` である。
    #      ⚠️ 両者がずれると、**許可していない被験者の結果が確証解析に載る**。
    #      `validate_blocks.py:590` は同じ検査を持っているが、`analyze.py` には無かった。
    if check_subject_matches_filename("P011", {"subject": "P011"}) is not None:
        fails.append("★ 一致しているのにエラーにしてはならない")
    if check_subject_matches_filename("P011", {"subject": "P099"}) is None:
        fails.append("★★ ファイル名と subject がずれているのに通してはならない"
                     "（roster が許可した ID と結果の ID が食い違う）")
    if check_subject_matches_filename("P011", {}) is None:
        fails.append("★ subject が無い割付ファイルを通してはならない")

    if fails:
        print("[NG] analyze.py selftest 失敗:")
        for f_ in fails:
            print(f"  - {f_}")
        return 1
    print("[OK] analyze.py selftest 緑 "
          "(全数列挙 70/45・分離/非分離・分散ゼロ・Fisher・★§2.5 第 3 版の分岐・★§5.3 判定の封印・"
          "見る順序 §3.4・適格性ゲート・特徴量定義)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
