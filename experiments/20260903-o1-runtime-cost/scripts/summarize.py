#!/usr/bin/env python3
"""results/ の samples.tsv をまとめ、README の判定表に照らす。

⚠️★★★ 「測れていない」を「合格」と読ませない。
★ 行が足りない / 対照が無い / 列が空 のときは **判定しない** (DataInsufficient)。
  memory: silent-success-is-not-visible / 成功は肯定形で、根拠は実測。
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
RESULTS = HERE / "results"

# ★ README の判定表。⚠️ 測った後に動かさない。
# ⚠️★★★ **battery_drop_pt_per_8h は入れない。** ★ README が 2026-09-04 に取り下げた
#   (AC 運転では放電を測れず、対照も原理的に無意味だった)。→ ★ 参考値として印字はするが、
#   ⚠️ **判定には一切入れない**（★ 閾値表に無い名前を verdict() に渡すと KeyError で落ちる = 気づける）。
THRESHOLDS = {
    "cpu_mean_pct": (1.0, 3.0),
    "cpu_max_pct": (15.0, 30.0),
    "rss_slope_mb_per_h": (5.0, 20.0),
    "rss_final_mb": (300.0, None),
    "ndjson_mb_per_day": (30.0, 48.0),
}
# ★ 8 時間ぶんを埋めるのに要る最小サンプル数 (間隔 30s の 8h = 960)。
#   ⚠️ 半分を切ったら「測れていない」とみなす。
MIN_SAMPLES = 480
# ★ 起動コストの読み方に添える注意書き用（⚠️ 実効間隔は top を 2 回叩くぶん延びる）。
INTERVAL_HINT_S = 35


def parse_threads(v: str) -> int:
    """スレッド数。⚠️★★★ macOS の `top` は `#TH` を **`31/1`（総数/実行中）**で出すことがある。

    ★ 2026-09-04 に実測: 880 行中 **21 行**がこの形で、⚠️ 旧実装は `int(float("31/1"))` が
    ValueError になり **その行を丸ごと捨てていた**（CPU も RSS も一緒に消えた）。
    → ★ 先頭の数だけ採る。
    """
    return int(str(v).split("/")[0] or 0)


def load(run: str):
    d = RESULTS / run
    tsv = d / "samples.tsv"
    if not tsv.is_file():
        return None
    rows = []
    skipped = []
    for i, line in enumerate(tsv.read_text().splitlines()):
        if i == 0 or not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 5:
            # ⚠️★★ **列不足も「捨てた行」に数える。** ★ 2026-09-04 の陽性対照で発覚:
            #   ValueError だけ数えていたので、⚠️ **列が足りない行は報告に出ないまま消えた**
            #   （★ 検査を書いたのに、その検査が空回りしていた）。
            skipped.append(line)
            continue
        try:
            rows.append(
                {
                    "t": int(parts[0]),
                    "cpu": float(parts[1] or 0),
                    "rss_kb": float(parts[2] or 0),
                    "threads": parse_threads(parts[3]),
                    "batt": float(parts[4]) if parts[4].strip() else None,
                    "rss_alt_kb": float(parts[5]) if len(parts) > 5 and parts[5].strip() else None,
                    # ⚠️★★★ 2026-09-04 (PR #157) で 7・8 列目が増えた。★ 古い 6 列の
                    #   samples.tsv も読めるようにする（⚠️ 落とすと 1 回目の実測が読めなくなる）。
                    "energy": float(parts[6]) if len(parts) > 6 and parts[6].strip() else None,
                    "ref_energy": float(parts[7]) if len(parts) > 7 and parts[7].strip() else None,
                }
            )
        except ValueError:
            # ⚠️★★★ **捨てた行を黙って無かったことにしない。**
            #   ★ 2026-09-04 に実測: `31/1` の 21 行が丸ごと落ち、
            #   ⚠️ **CPU も RSS も一緒に消えていた**（★ 幸い平均は動かなかったが、
            #   偏っていたら結論が変わっていた）。→ ★ 数えて報告する。
            skipped.append(line)
            continue
    meta = {}
    if (d / "meta.json").is_file():
        meta = json.loads((d / "meta.json").read_text())
    return {"rows": rows, "meta": meta, "dir": d, "skipped": skipped}


def slope_mb_per_h(rows) -> float | None:
    """RSS の傾き (最小二乗)。⚠️ 2 点未満なら None (★ 0 と書かない)。"""
    pts = [(r["t"], r["rss_kb"] / 1024.0) for r in rows if r["rss_kb"] > 0]
    n = len(pts)
    if n < 2:
        return None
    t0 = pts[0][0]
    xs = [(t - t0) / 3600.0 for t, _ in pts]
    ys = [y for _, y in pts]
    mx = sum(xs) / n
    my = sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den


def battery_drop_per_8h(rows) -> float | None:
    """8 時間あたりのバッテリー低下 (pt)。

    ⚠️★★★ **充電中 / AC 運転なら `None`（測れていない）を返す。**
    ★ 2026-09-04 に実測: AC で回したら 75% → 100% になり、低下が **-25.03** と出て、
    ⚠️ 判定関数の `value < good` に当たって **`PASS` と表示された** ——
    ★ 「測っていない」を「合格」と読ませる、まさに本 repo が嫌う型だった。
    → ⚠️ **低下していない = この条件では測れていない**、と倒す。
    """
    pts = [(r["t"], r["batt"]) for r in rows if r["batt"] is not None]
    if len(pts) < 2:
        return None
    hours = (pts[-1][0] - pts[0][0]) / 3600.0
    if hours <= 0:
        return None
    drop = (pts[0][1] - pts[-1][1]) / hours * 8.0
    if drop <= 0:
        return None  # ★ 充電中 / 変化なし = 放電を測れていない
    return drop


def ndjson_mb_per_day(run_dir: pathlib.Path) -> float | None:
    tsv = run_dir / "ndjson-size.tsv"
    if not tsv.is_file():
        return None
    total = 0
    n = 0
    for i, line in enumerate(tsv.read_text().splitlines()):
        if i == 0 or not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        try:
            total += int(parts[1])
            n += 1
        except ValueError:
            continue
    if n == 0:
        return None
    # ★ 1 ファイル = 1 日 (ROTATE_AFTER_MS = 24h)。⚠️ 平均を採る。
    return total / n / (1024 * 1024)


def energy_report(rows) -> tuple[str, bool]:
    """★ エネルギー影響 (`top -stats power`)。

    ⚠️★★★ **閾値を置かない。** ★ Apple 内部の無次元の合成指標 (CPU / wakeup / GPU / ディスク) で、
    ⚠️ ワットでもバッテリー時間でもない。→ ★ **参照プロセス (Finder) との比**で報告するだけにする。
    戻り値: (印字する文字列, 測れたか)。
    """
    pairs = [(r["energy"], r["ref_energy"]) for r in rows
             if r["energy"] is not None]
    if not pairs:
        return ("⚠️★★★ energy_impact の列が無い（★ 2026-09-04 より前の samples.tsv）"
                " → **エネルギー影響は測れていない**", False)
    e = [a for a, _ in pairs]
    if max(e) == 0:
        return ("⚠️★★★ energy_impact が **全行 0** —— ★ 測定器が壊れている疑い"
                "（`top -stats power` の列がずれていないか確かめること）", False)
    e_mean = sum(e) / len(e)
    e_max = max(e)
    # ⚠️★★ **参照が 0 の行では比を採らない。** ★ Finder はアイドルだと 0 を返す
    #   (2026-09-04 のスモークで実測: 4 行中 2 行が 0)。⚠️ 0 で割ると落ちるし、
    #   0 を混ぜて平均を採ると「参照が小さい = GSE が重い」と読める偽の比が出る。
    both = [(a, b) for a, b in pairs if b is not None and b > 0]
    lines = [f"★ エネルギー影響 (⚠️ 無次元・閾値なし): GSE 平均 {e_mean:.2f} / 最大 {e_max:.2f}"]
    if both:
        r_mean = sum(b for _, b in both) / len(both)
        a_mean = sum(a for a, _ in both) / len(both)
        ratio = (a_mean / r_mean) if r_mean > 0 else None
        lines.append(f"  ★ 参照 (Finder) が動いていた {len(both)}/{len(pairs)} 行での比較: "
                     f"GSE {a_mean:.2f} / Finder {r_mean:.2f}"
                     + (f" ＝ **{ratio:.2f} 倍**" if ratio is not None else ""))
    else:
        lines.append("  ⚠️ 参照 (Finder) が全行 0 —— ★ 比は採れない（★ 単独の数値には意味が無い）")
    lines.append("  ⚠️ 「ワット」「バッテリー何時間ぶん」には**換算できない**。")
    return ("\n".join(lines), True)


def startup_report(all_rows, present_rows, n_head: int = 5) -> tuple[str, bool]:
    """★ 起動時のコスト。⚠️ 「GSE 不在の行が先頭にある」ことが**測れた条件**である。

    ⚠️★★★ 起動後から測り始めた samples.tsv では**原理的に測れない**（★ 2026-09-04 の 1 回目）。
    → ★ 基線が無ければ「測れていない」と倒す（⚠️ 黙って定常値を起動値として出さない）。
    """
    if not all_rows or not present_rows:
        return ("⚠️ 行が無い → 起動コストは測れていない", False)
    n_absent = len(all_rows) - len(present_rows)
    if n_absent == 0:
        return ("⚠️★★★ **起動前の基線が無い**（★ 先頭から GSE が居る）"
                " → **起動時のコストは測れていない**。"
                "★ 測るならサンプラを先に起こしてから GSE を起動すること。", False)
    head = present_rows[:n_head]
    tail = present_rows[n_head:]
    h_cpu = sum(r["cpu"] for r in head) / len(head)
    lines = [f"★ 起動時のコスト: 起動前の基線 {n_absent} 行（★ 全列 0 = 計測器の陰性対照）"]
    lines.append(f"  ★ 起動直後 {len(head)} サンプルの CPU 平均: {h_cpu:.2f} %")
    if tail:
        t_cpu = sum(r["cpu"] for r in tail) / len(tail)
        lines.append(f"  ★ 以降（定常）の CPU 平均: {t_cpu:.2f} %  → 差 {h_cpu - t_cpu:+.2f} pt")
    h_rss = [r["rss_kb"] / 1024.0 for r in head if r["rss_kb"] > 0]
    if h_rss:
        lines.append(f"  ★ 起動直後の RSS: {h_rss[0]:.1f} MB")
    lines.append(f"  ⚠️ サンプル間隔は約 {INTERVAL_HINT_S} s なので、"
                 "★ **それより短い山は取りこぼす**（★ 孤児回収の走査を含む）。")
    return ("\n".join(lines), True)


def verdict(name: str, value):
    good, bad = THRESHOLDS[name]
    if value is None:
        return "DataInsufficient", "⚠️ 測れていない"
    if value < good:
        return "PASS", "★ 合格"
    if bad is not None and value >= bad:
        return "FAIL", "⚠️ 要対処"
    return "MARGINAL", "⚠️ 判定表の合格域を外れている"


def main() -> int:
    # ★ run はコマンドラインで選べる（⚠️ 既定は with-gse）。
    #   ★ 1 回目の実測を退避してあるので、`results/with-gse-20260904-steady` も読めること。
    run = sys.argv[1] if len(sys.argv) > 1 else "with-gse"
    with_gse = load(run)
    if with_gse is None:
        print(f"⚠️ results/{run}/samples.tsv が無い。★ まだ測っていない。")
        return 1
    all_rows = with_gse["rows"]
    # ⚠️★★★ **GSE 不在の行を判定に混ぜない。** ★ サンプラは GSE が居ないと全列 0 を書く。
    #   ★ 2026-09-04 の 2 回目は「起動前の基線」を意図して取っているので、
    #   ⚠️ 混ぜると CPU 平均が**下振れ**し、RSS 最終行が 0 になる。
    rows = [r for r in all_rows if r["rss_kb"] > 0 or r["threads"] > 0]
    n_absent = len(all_rows) - len(rows)
    print(f"★ 対象: results/{run}")
    print(f"★ サンプル数: {len(rows)} (最小 {MIN_SAMPLES})"
          + (f"  ＋ GSE 不在の行 {n_absent}（★ 判定から除外）" if n_absent else ""))
    # ⚠️★★ **読めなかった行は必ず出す。** ★ 黙って捨てると「測れた行だけ」で判定してしまう。
    n_skipped = len(with_gse.get("skipped", []))
    if n_skipped:
        print(f"⚠️★★★ 読めずに捨てた行: {n_skipped} 行 —— ★ 原因を確かめること"
              f"（例: {with_gse['skipped'][0][:70]!r}）")
    # ⚠️★★★ **サンプルが足りないなら 1 指標も PASS にしない。**
    #   ★ 2026-09-03 に自分の測定器で実測した欠陥: 100 サンプルでも個別欄が PASS と出た。
    #   → ⚠️ memory `measurement-instrument-false-positives` と同型。
    enough = len(rows) >= MIN_SAMPLES
    if not enough:
        print("⚠️★★★ サンプルが足りない。**1 指標も判定しない**（★ 短時間の観測で「軽い」と言わない）。")
    cpus = [r["cpu"] for r in rows]
    metrics = {
        "cpu_mean_pct": (sum(cpus) / len(cpus)) if cpus else None,
        "cpu_max_pct": max(cpus) if cpus else None,
        "rss_slope_mb_per_h": slope_mb_per_h(rows),
        "rss_final_mb": (rows[-1]["rss_kb"] / 1024.0) if rows else None,
        "ndjson_mb_per_day": ndjson_mb_per_day(with_gse["dir"]),
    }
    print()
    worst = "PASS"
    order = {"PASS": 0, "MARGINAL": 1, "DataInsufficient": 2, "FAIL": 3}
    for k, v in metrics.items():
        v_, why = verdict(k, v) if enough else ("DataInsufficient", "⚠️ サンプル不足")
        shown = "—" if v is None else f"{v:.2f}"
        print(f"  {k:26s} {shown:>10s}  {v_:<16s} {why}")
        if order[v_] > order[worst]:
            worst = v_
    print()

    # ★ 指標 3: エネルギー影響（⚠️ 閾値は置かない = 判定表に載せない）。
    txt, ok_energy = energy_report(rows)
    print(txt)
    print()
    # ★ 指標 5: 起動時のコスト。
    txt, ok_startup = startup_report(all_rows, rows)
    print(txt)
    print()

    # ⚠️★★★ バッテリーは **2026-09-04 に指標として取り下げた**（README）。
    #   ★ 参考値としてだけ印字し、⚠️ **判定 (worst) には一切効かせない**。
    #   ★ 対照 (without-gse) も同時に廃止した —— ⚠️ CPU / RSS / NDJSON は GSE のプロセスを
    #   測るので、GSE が居ない条件では全列が 0 になり、対照は原理的に何も足さない。
    b = battery_drop_per_8h(rows)
    print("★ バッテリー低下 (参考・⚠️ 2026-09-04 に指標として取り下げ): "
          + (f"{b:.2f} pt/8h" if b is not None else "— （★ AC 運転 / 変化なし = 放電を測れていない）"))
    print()

    # ⚠️★★★ **測れていないものがあるなら総合を PASS にしない。**
    #   ★ 「6 指標中 5 つ実測」を「合格」と読ませないための門である。
    if not enough and worst != "FAIL":
        worst = "DataInsufficient"
    missing = [n for n, ok in (("エネルギー影響", ok_energy), ("起動時のコスト", ok_startup)) if not ok]
    if missing and worst in ("PASS", "MARGINAL"):
        print(f"⚠️★★ 未測定が残っている: {' / '.join(missing)} → **総合は PASS にしない**。")
        worst = "DataInsufficient"
    print(f"総合: {worst}")
    if worst != "PASS":
        print("⚠️ ★ notes.md に、どの指標がなぜ外れたかを書くこと。")
    return 0 if worst == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
