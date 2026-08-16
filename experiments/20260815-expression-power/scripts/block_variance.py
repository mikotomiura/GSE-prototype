#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""実測アンカー — 「δ = 1.0 は GSE の実データで何を意味するか」を 1 本だけ出す。

★ 検出力計算 (power_calc.py) はブロック水準 SD = 1 の単位で答えを出す。
  ⚠️ その単位が実データで何 keys/min なのかを知らないと、δ80 = 0.89 が
  「届きうる効果」なのか「あり得ない効果」なのか判断できない。→ 本スクリプトがその 1 本。

⚠️★★★ プライバシー (data-privacy Skill):
  * 入力は gse-dataset の生 NDJSON（★ 本リポジトリにコミットしない）。
  * 出力は **集計統計量のみ**。★ セッション名・ファイル名・時刻は 1 つも書き出さない
    （S5C-D8 / S5C-D10 の教訓: 「事故を説明するために実例を書く」ことが漏洩そのものだった）。
  * 打鍵の**内容**は元データに無い（VK コードのみ）。本スクリプトは vk の値を読まない。

⚠️ 標準ライブラリのみ。
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

STUCK_THRESHOLD = 0.70  # intervention-design / spec §6 の Wall トリガ水準


def _mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def _sd(xs):
    """標本標準偏差 (n-1)。"""
    if len(xs) < 2:
        return float("nan")
    m = _mean(xs)
    return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5


def _median(xs):
    if not xs:
        return float("nan")
    s = sorted(xs)
    h = len(s) // 2
    return s[h] if len(s) % 2 else (s[h - 1] + s[h]) / 2.0


def session_windows(path: str, window_minutes: int):
    """1 セッションを window_minutes の窓に切り、窓ごとの指標を返す。

    返すのは (打鍵数/分, p_stuck>閾値 の割合) の列。★ 時刻は返さない。
    """
    win_ms = window_minutes * 60 * 1000
    t0 = None
    keys: dict[int, int] = {}
    feat_total: dict[int, int] = {}
    feat_stuck: dict[int, int] = {}
    last_t = None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            typ = o.get("type")
            t = o.get("t")
            if typ == "meta" and t0 is None:
                t0 = o.get("session_start")
                continue
            if t is None:
                continue
            if t0 is None:
                t0 = t
            idx = int((t - t0) // win_ms)
            if idx < 0:
                continue
            last_t = t
            if typ == "key" and o.get("press") is True:
                keys[idx] = keys.get(idx, 0) + 1
            elif typ == "feat":
                feat_total[idx] = feat_total.get(idx, 0) + 1
                if float(o.get("p_stuck", 0.0)) > STUCK_THRESHOLD:
                    feat_stuck[idx] = feat_stuck.get(idx, 0) + 1
    if t0 is None or last_t is None:
        return [], []
    n_full = int((last_t - t0) // win_ms)  # 最後の欠けた窓は捨てる
    rates = []
    stuck = []
    for i in range(n_full):
        rates.append(keys.get(i, 0) / window_minutes)
        tot = feat_total.get(i, 0)
        if tot > 0:
            stuck.append(feat_stuck.get(i, 0) / tot)
    return rates, stuck


def _input_manifest(paths):
    """入力集合の来歴ダイジェスト。★ ファイル名を含めない（S5C-D10）。"""
    import hashlib

    rows = []
    for p in paths:
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        rows.append((os.path.getsize(p), h.hexdigest()))
    rows.sort()
    agg = hashlib.sha256()
    for size, digest in rows:
        agg.update(f"{size}:{digest}\n".encode())
    return {
        "files": len(rows),
        "total_bytes": sum(s for s, _ in rows),
        "manifest_sha256": agg.hexdigest(),
    }


def session_summary(path: str):
    """1 セッション全体の要約。★ spec §8 逐語「1 ブロック = 1 セッション = NDJSON 1 ファイル」。

    → ブロック水準の分散 ＝ セッション間分散である。★ ここが本アンカーの主経路。
    """
    t0 = None
    last = None
    keys = 0
    feat_total = 0
    feat_stuck = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            typ = o.get("type")
            t = o.get("t")
            if typ == "meta" and t0 is None:
                t0 = o.get("session_start")
                continue
            if t is None:
                continue
            if t0 is None:
                t0 = t
            last = t
            if typ == "key" and o.get("press") is True:
                keys += 1
            elif typ == "feat":
                feat_total += 1
                if float(o.get("p_stuck", 0.0)) > STUCK_THRESHOLD:
                    feat_stuck += 1
    if t0 is None or last is None or last <= t0:
        return None
    minutes = (last - t0) / 60000.0
    return {
        "minutes": minutes,
        "rate": keys / minutes,
        "stuck_fraction": (feat_stuck / feat_total) if feat_total else None,
    }


def window_counts(path: str, window_minutes: int):
    """連続する window_minutes 窓ごとの keydown 総数（★ 最後の欠けた窓は捨てる）。

    ★ G1 事前登録 §2.9 が「P010–P014・360 個の連続 5 分窓」で中央値 261 / 第 1 四分位 61 /
      100 未満 29% を出している。★ 同じ量を再計算して突き合わせる（= 窓の切り方の検証）。
    """
    win_ms = window_minutes * 60 * 1000
    t0 = None
    last = None
    keys: dict[int, int] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            typ = o.get("type")
            t = o.get("t")
            if typ == "meta" and t0 is None:
                t0 = o.get("session_start")
                continue
            if t is None:
                continue
            if t0 is None:
                t0 = t
            last = t
            if typ == "key" and o.get("press") is True:
                keys[int((t - t0) // win_ms)] = keys.get(int((t - t0) // win_ms), 0) + 1
    if t0 is None or last is None:
        return []
    n_full = int((last - t0) // win_ms)
    return [keys.get(i, 0) for i in range(n_full)]


def _quantile(xs, q):
    if not xs:
        return float("nan")
    s = sorted(xs)
    pos = q * (len(s) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(s) - 1)
    frac = pos - lo
    return s[lo] * (1 - frac) + s[hi] * frac


def cohort_mode(flat_dir: str, window_minutes: int, out_path: str) -> int:
    """★ 参加者複数（P010–P014）の平置きディレクトリから、ブロック水準分散を出す。

    ⚠️★★★ 出力にファイル名を 1 つも入れない（S5C-D8: 実セッション名 `Pnnn_gse_...` の混入事故）。
    """
    files = sorted(glob.glob(os.path.join(flat_dir, "**", "*.ndjson"), recursive=True))
    if not files:
        sys.stderr.write(f"no sessions under {flat_dir}\n")
        return 2
    by_pid: dict[str, list[str]] = {}
    for p in files:
        base = os.path.basename(p)
        pid = base.split("_", 1)[0] if "_" in base else "UNKNOWN"
        by_pid.setdefault(pid, []).append(p)

    # ★ 参加者ごとの窓を 1 度だけ抽出して使い回す
    windows_by_pid = {}
    for pid in sorted(by_pid):
        wins = []
        for p in by_pid[pid]:
            wins.extend(window_counts(p, window_minutes))
        if wins:
            windows_by_pid[pid] = wins

    per_participant = []
    all_windows = []
    for pid, wins in windows_by_pid.items():
        all_windows.extend(wins)
        rates = [w / window_minutes for w in wins]
        per_participant.append({
            "participant": pid,
            "sessions": len(by_pid[pid]),
            "windows": len(wins),
            "keydown_per_window_median": round(_median(wins), 1),
            "rate_mean": round(_mean(rates), 2),
            "rate_sd": round(_sd(rates), 2),
            "rate_cv": round(_sd(rates) / _mean(rates), 4) if _mean(rates) > 0 else None,
        })

    # ⚠️★★★ 研究者の指摘（2026-08-15）:
    #   「これらのデータは打鍵以外のノイズなども入っている。G1 で純粋な打鍵データを集めている」
    # → ★ **G1 自身が事前登録した適格性ゲート（ブロックあたり keydown >= 100）**を窓に適用し、
    #   「非打鍵ノイズ（読解・離席・別作業）が CV のどれだけを占めるか」を数字にする。
    #   ★ 閾値は事後に決めたものではない（G1 事前登録 §2.9 で凍結済み）。
    gates = []
    for min_kd in (0, 1, 100, 200):
        rows = []
        for pid, wins in windows_by_pid.items():
            kept = [w for w in wins if w >= min_kd]
            if len(kept) < 3:
                continue
            rates = [w / window_minutes for w in kept]
            m = _mean(rates)
            rows.append({
                "participant": pid,
                "windows_kept": len(kept),
                "windows_dropped": len(wins) - len(kept),
                "rate_mean": round(m, 2),
                "rate_sd": round(_sd(rates), 2),
                "rate_cv": round(_sd(rates) / m, 4) if m > 0 else None,
            })
        cvs_g = [r["rate_cv"] for r in rows if r["rate_cv"] is not None]
        total_kept = sum(r["windows_kept"] for r in rows)
        gates.append({
            "min_keydown_per_window": min_kd,
            "source": ("G1 事前登録 §2.9 の適格性ゲート（凍結）" if min_kd == 100 else "参考"),
            "participants": len(rows),
            "windows_kept": total_kept,
            "windows_dropped": len(all_windows) - total_kept,
            "within_participant_cv_median": round(_median(cvs_g), 4) if cvs_g else None,
            "within_participant_cv_min": round(min(cvs_g), 4) if cvs_g else None,
            "within_participant_cv_max": round(max(cvs_g), 4) if cvs_g else None,
            "per_participant": rows,
        })

    # 参加者内 CV の中央値 ＝ 被験者内設計で使うべき σ/μ
    cvs = [p["rate_cv"] for p in per_participant if p["rate_cv"] is not None]
    means = [p["rate_mean"] for p in per_participant]
    out = {
        "schema": "expression-power-anchor-cohort/v1",
        "note": "集計統計量のみ。★ ファイル名・セッション名・時刻・vk は 1 つも含まない。",
        "window_minutes": window_minutes,
        "input_manifest": _input_manifest(files),
        "participants": len(per_participant),
        "windows_total": len(all_windows),
        "per_participant": per_participant,
        "within_participant_cv": {
            "median": round(_median(cvs), 4),
            "min": round(min(cvs), 4) if cvs else None,
            "max": round(max(cvs), 4) if cvs else None,
        },
        "activity_gates": gates,
        "activity_gates_note": (
            "⚠️ Phase1 は自然ログで、打鍵以外（読解・離席・別作業）が窓に入る。"
            "G1 は統制下で純粋な打鍵を集める。→ G1 の適格性ゲート(keydown>=100)を当てて"
            "『非打鍵ノイズが CV のどれだけを占めるか』を測る。★ ゲート値は事前登録で凍結済み"
        ),
        "between_participant": {
            "sd_of_participant_means": round(_sd(means), 2),
            "mean_of_participant_means": round(_mean(means), 2),
        },
        "prereg_cross_check": {
            "_source": "experiments/20260801-controlled-friction-task/preregistration.md §2.9",
            "recorded_median": 261,
            "recorded_q1": 61,
            "recorded_frac_below_100": 0.29,
            "recorded_windows": 360,
            "recomputed_median": round(_median(all_windows), 1),
            "recomputed_q1": round(_quantile(all_windows, 0.25), 1),
            "recomputed_frac_below_100": round(
                sum(1 for w in all_windows if w < 100) / len(all_windows), 4),
            "recomputed_windows": len(all_windows),
        },
    }
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    sys.stdout.write(f"wrote {out_path}\n")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=os.environ.get("GSE_DATASET", "C:/gse-dataset"))
    ap.add_argument("--flat-dir", default=None,
                    help="Pnnn_gse_*.ndjson が平置きされたディレクトリ（★ 参加者複数モード）")
    ap.add_argument("--participant", default="P000")
    ap.add_argument("--window-minutes", type=int, default=1,
                    help="副経路（セッション内の細かい窓）の窓長")
    ap.add_argument("--min-windows", type=int, default=3,
                    help="セッション内 SD を出すのに要る最小窓数")
    ap.add_argument("--min-session-minutes", type=float, default=3.0,
                    help="主経路（セッション = ブロック）に入れる最小セッション長")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if args.flat_dir:
        return cohort_mode(args.flat_dir, 5, args.out)

    pattern = os.path.join(args.dataset, "raw", args.participant, "*.ndjson")
    files = sorted(glob.glob(pattern))
    if not files:
        sys.stderr.write(f"no sessions under {pattern}\n")
        return 2

    # ⚠️ gse-dataset の raw/ は git 管理外なので commit hash では入力を固定できない。
    # → ★ (サイズ, sha256) の並びを 1 つのダイジェストに畳んで来歴とする（★ ファイル名は入れない）。
    manifest = _input_manifest(files)

    # --- 主経路: セッション = ブロック（spec §8）---
    summaries = [s for s in (session_summary(p) for p in files) if s]
    kept = [s for s in summaries if s["minutes"] >= args.min_session_minutes]
    rates_all = [s["rate"] for s in summaries]
    rates_kept = [s["rate"] for s in kept]
    stuck_kept = [s["stuck_fraction"] for s in kept if s["stuck_fraction"] is not None]

    # --- 副経路: セッション内の細かい窓（★ 自己相関があるので 5 分へは外挿しない）---
    within_sd_rate, within_mean_rate, within_cv_rate = [], [], []
    total_windows = 0
    for path in files:
        wrates, _ = session_windows(path, args.window_minutes)
        total_windows += len(wrates)
        if len(wrates) >= args.min_windows:
            m, s = _mean(wrates), _sd(wrates)
            within_sd_rate.append(s)
            within_mean_rate.append(m)
            if m > 0:
                within_cv_rate.append(s / m)

    out = {
        "schema": "expression-power-anchor/v2",
        "note": "集計統計量のみ。セッション名・時刻・vk は 1 つも含まない。",
        "primary_unit": "session (= 1 block; spec §8 逐語『1 ブロック = 1 セッション = NDJSON 1 ファイル』)",
        "input_manifest": manifest,
        "stuck_threshold": STUCK_THRESHOLD,
        "sessions_found": len(files),
        "sessions_summarized": len(summaries),
        "min_session_minutes": args.min_session_minutes,
        "sessions_kept": len(kept),
        "session_minutes": {
            "min": round(min((s["minutes"] for s in summaries), default=float("nan")), 2),
            "median": round(_median([s["minutes"] for s in summaries]), 2),
            "max": round(max((s["minutes"] for s in summaries), default=float("nan")), 2),
            "total": round(sum(s["minutes"] for s in summaries), 1),
        },
        "block_level_keystroke_rate_per_min": {
            "n_blocks": len(rates_kept),
            "mean": round(_mean(rates_kept), 2),
            "sd": round(_sd(rates_kept), 2),
            "cv": round(_sd(rates_kept) / _mean(rates_kept), 4) if rates_kept else None,
            "median": round(_median(rates_kept), 2),
            "sd_all_sessions_unfiltered": round(_sd(rates_all), 2),
            "mean_all_sessions_unfiltered": round(_mean(rates_all), 2),
        },
        "block_level_p_stuck_fraction": {
            "n_blocks": len(stuck_kept),
            "mean": round(_mean(stuck_kept), 4) if stuck_kept else None,
            "sd": round(_sd(stuck_kept), 4) if len(stuck_kept) > 1 else None,
        },
        "secondary_within_session_windows": {
            "window_minutes": args.window_minutes,
            "windows_total": total_windows,
            "sessions_usable": len(within_sd_rate),
            "within_session_sd_median": round(_median(within_sd_rate), 3),
            "within_session_mean_median": round(_median(within_mean_rate), 3),
            "within_session_cv_median": round(_median(within_cv_rate), 4),
            "caveat": "打鍵は自己相関を持つので、この窓長の SD を 1/sqrt(T) で 5 分へ外挿してはならない",
        },
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    sys.stdout.write(f"wrote {args.out}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
