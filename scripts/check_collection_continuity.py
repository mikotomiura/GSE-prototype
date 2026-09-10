#!/usr/bin/env python3
"""受領した O1 / G1 セッション NDJSON が「静かに止まっていないか」を見る。

⚠️★★★ **なぜ要るか** —— 2026-09-10 に `gse-next` が **SIGSEGV で無言終了**した
(`.steering/20260910-measurement-binary-rebuild/sigsegv-finding.md`)。
★ そのとき起きたこと:

  - ⚠️ 終了ログが出ない。★ tray アイコンが消えるだけ。
  - ⚠️ 収集は止まったまま。★ 被験者は**気づかない**。
  - ★ 唯一の痕跡は「次に起動したとき」の孤児回収 WARN 1 行だけ
    (`o1.rs`「the app did not shut down cleanly last time」)。

→ ★ **落ちたことに気づく最後の砦は「受け取った NDJSON を見ること」**である。
⚠️ 本 script はその事後検知 (引き継ぎ `distribution-gap.md` の案 D)。

## ⚠️ プライバシー

★ **型と時刻と数値フィールドしか読まない** (`data-privacy` Skill)。
⚠️ 打鍵内容は NDJSON に存在しないが、★ 本 script は文字列フィールドを 1 つも出力しない
(★ `app_version` / `hmm_version` を除く —— これは版の同定に要る)。

## 使い方

    python3 scripts/check_collection_continuity.py <file-or-dir> [...]
    python3 scripts/check_collection_continuity.py --self-test

## 終了コード

    0 = すべて健全   3 = 問題あり   2 = ⚠️ **判定しない** (入力が無い / 読めない)
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ★ `feat` は 1 Hz で出る。⚠️ 30 秒超の穴は `starve_window` の閾値と同じ意味を持つ。
FEAT_GAP_WARN_S = 30.0
# ⚠️★★★ **「ファイル mtime と最後のイベント時刻を比べる」検査は入れない。**
#   ★ 最初は入れたが、自己検査で**健全な fixture を誤検出した**(2026-09-10)。
#   ⚠️ 受領ファイルは **コピー / 復号 / 転送で mtime が書き換わる**ので、
#   ★ mtime は「書き手がいつ消えたか」の資料にならない。
#   → ★ 誤爆する検査は、研究者に**検査そのものを無視させる**ので置かない。
#   ★ 「静かに止まった」は `session_end` の欠落と穴で見る (⚠️ どちらもファイル内の資料)。
# ⚠️ 行数がこれ未満のファイルは**判定しない** (★ 0 件マッチの空振り対策)。
MIN_LINES_TO_JUDGE = 10


@dataclass
class Report:
    path: Path
    lines: int = 0
    broken: int = 0
    types: dict = field(default_factory=dict)
    has_session_start: bool = False
    has_session_end: bool = False
    app_version: str | None = None
    hmm_version: str | None = None
    max_gap_s: float = 0.0
    gaps_over_warn: int = 0
    hook_dropped_total: int = 0
    hook_alive_false: int = 0
    starve_windows: int = 0
    problems: list = field(default_factory=list)
    judged: bool = True


def scan(path: Path) -> Report:
    r = Report(path=path)
    ts: list[int] = []
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:  # ⚠️ 読めないなら「健全」ではなく「判定しない」
        r.judged = False
        r.problems.append(f"⚠️ 読めない: {e.__class__.__name__}")
        return r

    for line in raw.splitlines():
        if not line.strip():
            continue
        r.lines += 1
        try:
            o = json.loads(line)
        except Exception:
            r.broken += 1
            continue
        t = o.get("type")
        r.types[t] = r.types.get(t, 0) + 1
        if t == "meta":
            if o.get("session_start") is not None:
                r.has_session_start = True
                r.app_version = o.get("app_version")
                r.hmm_version = str(o.get("hmm_version"))
            if o.get("session_end") is not None:
                r.has_session_end = True
        elif t == "hook_health":
            r.hook_dropped_total += int(o.get("dropped") or 0)
            if o.get("alive") is False:
                r.hook_alive_false += 1
        elif t == "starve_window":
            r.starve_windows += 1
        v = o.get("t")
        if isinstance(v, (int, float)):
            ts.append(int(v))

    # ⚠️★★★ 行が少なすぎるなら**判定しない**。★ 「0 件だから健全」を出さない。
    if r.lines < MIN_LINES_TO_JUDGE:
        r.judged = False
        r.problems.append(f"⚠️ 行が {r.lines} 本しかない (★ {MIN_LINES_TO_JUDGE} 未満) → **判定しない**")
        return r

    feat_ts = sorted(t for t in ts) if ts else []
    if len(feat_ts) >= 2:
        gaps = [(feat_ts[i] - feat_ts[i - 1]) / 1000.0 for i in range(1, len(feat_ts))]
        r.max_gap_s = max(gaps)
        r.gaps_over_warn = sum(1 for g in gaps if g > FEAT_GAP_WARN_S)

    # --- 判定 ---
    if r.broken:
        r.problems.append(f"⚠️ 壊れた行 {r.broken} 本")
    if not r.has_session_start:
        r.problems.append("⚠️ `session_start` が無い (★ 先頭が欠けている)")
    if not r.has_session_end:
        # ★★★ これが SIGSEGV / 強制終了の主要な足跡である。
        r.problems.append(
            "⚠️★★★ **`session_end` が無い** ＝ ★ 正常終了していない"
            " (★ クラッシュ / 強制終了 / 収集中のいずれか)"
        )
    if r.gaps_over_warn:
        r.problems.append(
            f"⚠️ {FEAT_GAP_WARN_S:.0f} 秒超の穴が {r.gaps_over_warn} 個 (★ 最大 {r.max_gap_s:.0f} 秒)"
        )
    if r.hook_dropped_total:
        r.problems.append(f"⚠️★★★ **フックが取りこぼした: dropped={r.hook_dropped_total}**")
    if r.hook_alive_false:
        r.problems.append(f"⚠️ `hook_health.alive=false` が {r.hook_alive_false} 件")
    return r


def render(r: Report) -> None:
    print(f"★ {r.path.name}")
    if not r.judged:
        for p in r.problems:
            print(f"    {p}")
        return
    ver = f"app={r.app_version} hmm={r.hmm_version}"
    print(f"    行 {r.lines} / {ver} / 型 {dict(sorted(r.types.items(), key=lambda kv: -kv[1]))}")
    print(
        f"    最大の穴 {r.max_gap_s:.0f} 秒 / {FEAT_GAP_WARN_S:.0f} 秒超 {r.gaps_over_warn} 個"
        f" / starve_window {r.starve_windows} / dropped {r.hook_dropped_total}"
    )
    if r.problems:
        for p in r.problems:
            print(f"    {p}")
    else:
        print("    ✅ ★ 健全")


def collect(args: list[str]) -> list[Path]:
    out: list[Path] = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            out.extend(sorted(p.glob("*.ndjson")))
        elif p.is_file():
            out.append(p)
    return out


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    files = collect(argv)
    if not files:
        # ⚠️★★★ 入力ゼロを「健全」にしない (★ memory: 0 件マッチの空振り)。
        print("⚠️★★★ NDJSON が 1 本も見つからない → **判定しない**")
        return 2

    reports = [scan(f) for f in files]
    print("=" * 60)
    for r in reports:
        render(r)
    print("=" * 60)

    judged = [r for r in reports if r.judged]
    unjudged = len(reports) - len(judged)
    bad = [r for r in judged if r.problems]
    print(f"★ {len(reports)} 本中 {len(judged)} 本を判定、⚠️ 判定しなかった {unjudged} 本")
    if bad:
        print(f"⚠️★★★ **問題あり {len(bad)} 本**:")
        for r in bad:
            print(f"    - {r.path.name}: {len(r.problems)} 件")
        return 3
    if not judged:
        print("⚠️ 判定できた本が 1 本も無い → **判定しない**")
        return 2
    print("✅ ★ 判定できた全本が健全")
    return 0


# --------------------------------------------------------------------------
# ★ 自己検査 —— ⚠️ 検査が空回りしていないことを対照で確かめる
# --------------------------------------------------------------------------
def _selftest() -> int:
    import tempfile

    fails = 0

    def w(d: Path, name: str, rows: list[dict]) -> Path:
        p = d / name
        p.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        return p

    def check(label: str, cond: bool, detail: str = "") -> None:
        nonlocal fails
        if not cond:
            print(f"  ✗ {label} {detail}")
            fails += 1

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        base = 1_700_000_000_000

        # ① ★ 陰性対照: 健全なファイル → 問題ゼロ
        good = [{"type": "meta", "session_start": base, "app_version": "0.1.34", "hmm_version": 7}]
        good += [{"type": "feat", "t": base + i * 1000} for i in range(60)]
        good += [{"type": "hook_health", "t": base + 30000, "alive": True, "dropped": 0}]
        good += [{"type": "meta", "session_end": base + 60000}]
        r = scan(w(d, "good.ndjson", good))
        check("① 健全なファイルは問題ゼロ", r.judged and not r.problems, f"→ {r.problems}")

        # ② ⚠️ 陽性対照: session_end が無い（★ SIGSEGV の足跡）
        r = scan(w(d, "noend.ndjson", [x for x in good if "session_end" not in x]))
        check(
            "② session_end 欠落を捕まえる",
            any("session_end` が無い" in p for p in r.problems),
            f"→ {r.problems}",
        )

        # ③ ⚠️ 陽性対照: 30 秒超の穴
        holed = good[:30] + [{"type": "feat", "t": base + 300_000}] + good[-2:]
        r = scan(w(d, "hole.ndjson", holed))
        check("③ 穴を捕まえる", r.gaps_over_warn >= 1, f"→ max_gap={r.max_gap_s}")

        # ④ ⚠️ 陽性対照: dropped > 0
        drop = list(good)
        drop.insert(2, {"type": "hook_health", "t": base + 1000, "alive": True, "dropped": 5})
        r = scan(w(d, "drop.ndjson", drop))
        check("④ dropped を捕まえる", r.hook_dropped_total == 5, f"→ {r.hook_dropped_total}")

        # ⑤ ⚠️ 陽性対照: 壊れた行
        p = w(d, "broken.ndjson", good)
        p.write_text(p.read_text(encoding="utf-8") + "{not json\n", encoding="utf-8")
        r = scan(p)
        check("⑤ 壊れた行を捕まえる", r.broken == 1, f"→ {r.broken}")

        # ⑥ ⚠️★★★ 「判定しない」対照: 行が少なすぎる
        r = scan(w(d, "tiny.ndjson", good[:3]))
        check("⑥ 行が少なければ判定しない", not r.judged, f"→ judged={r.judged}")

        # ⑦ ⚠️★★★ 「判定しない」対照: 入力ゼロで rc=2（★ 健全にしない）
        empty = d / "empty-dir"
        empty.mkdir()
        check("⑦ 入力ゼロは rc=2", main([str(empty)]) == 2)

        # ⑧ ★ 全体の rc: 健全のみ → 0 / 問題込み → 3
        only_good = d / "only-good"
        only_good.mkdir()
        w(only_good, "good.ndjson", good)
        check("⑧a 健全のみは rc=0", main([str(only_good)]) == 0)
        check("⑧b 問題があれば rc=3", main([str(d)]) == 3)

    total = 9  # ★ check の呼び出し回数を数えて書く（⚠️ 網羅性を誤らせない）
    if fails:
        print(f"[NG] check_collection_continuity --self-test: {fails}/{total} 件失敗")
        return 1
    print(f"[OK] check_collection_continuity --self-test 緑（{total} 項目・★ 陽性対照 5 / 判定しない 2）")
    print("     ⚠️ これは fixture の中の緑である。★ 実物の NDJSON に当てること。")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        raise SystemExit(_selftest())
    raise SystemExit(main(sys.argv[1:]))
