#!/usr/bin/env python3
"""引用整合の機械検算 (citation-ssot の規約をコードで守る)。

`docs/references.md` を SSOT として、以下を検査する:

1. **未登録参照** — docs/ と experiments/ 本文の `[Pn]`/`[Vn]` が references.md に無い
2. **同一名前空間内の key 重複** — DOI / arXiv / 正規化 URL の二重登録 (ルール 4 違反)
   ※ 名前空間跨ぎ (`[P2]`=`[V9]` 型) は規約上許容なので検出しない
3. **tombstone の引用** — 撤回済み ID が本文で使われていないか (説明目的の言及は要目視)
4. **欠番** — append-only なのに番号が飛んでいないか
   （★ 2026-11-26: 未マージの枝が使う区画を references.md の予約の表に書けば、その区画の欠番は違反にしない。
    予約の区画に登録の行がある・予約どうしが重なる・予約の書式が壊れている、は違反）
5. **件数** — `_index.md` などに手書きされた件数の照合材料 (実測値を出す)

なぜ要るか: 件数の手書きは **2026-08-16 に 1 日で 2 回陳腐化した**。
重複登録も同日に `[P130]` (誤って気付いた) と `[V45]`/`[V51]` (気付いていなかった) の 2 件あった。
→ 目視では追随できないので機械で検算する。

使い方:
    PYTHONUTF8=1 python scripts/check_citations.py [repo_root]
    PYTHONUTF8=1 python scripts/check_citations.py --self-test   # 予約の扱いの陽性対照

exit code:
    0 = 違反なし / 1 = 違反あり (未登録参照・同一名前空間内 key 重複・予約で埋まらない欠番・予約の違反)
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROW = re.compile(r'^\|\s*\[([PV])(\d+)\]\s*\|')
# 予約の表の行: `| V399-V412 | 枝の名前 | ... |`（角括弧なし・ROW とは当たらない）
RESERVE = re.compile(r'^\|\s*([PV])(\d+)\s*-\s*([PV])(\d+)\s*\|\s*([^|]*?)\s*\|')
# 予約らしいが書式が崩れた行（全角のダッシュ・片側の名前空間の欠け）を黙って読み落とさない
RESERVE_LOOSE = re.compile(r'^\|\s*[PV]?\d+\s*[-‐‑‒–—―−－〜~]\s*[PV]?\d+\s*\|')
# 予約の表の見出しの行。表はここから次の空行まで（表の外の予約らしい行は予約として読まない）
RESERVE_HEADER = re.compile(r'^\|\s*区画\s*\|')
SEPARATOR = re.compile(r'^\|[\s:|-]+\|\s*$')
CITE = re.compile(r'\[([PV])(\d+)\]')


def load_references(ref_path: Path):
    """references.md の表から id -> {ns, n, key, state} を作る。"""
    rows: dict[str, dict] = {}
    key_to_ids: dict[tuple[str, str], list[str]] = defaultdict(list)
    violations: list[str] = []

    for lineno, line in enumerate(ref_path.read_text(encoding='utf-8').splitlines(), 1):
        m = ROW.match(line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        ident = f'[{m.group(1)}{m.group(2)}]'
        key = cells[1] if len(cells) > 1 else ''
        state = cells[-1] if cells else ''
        # 末尾から 2 番目が「重複」列 (相互リンク)。列が欠けている行では空扱いにする。
        dup_cell = cells[-2] if len(cells) >= 3 else ''
        if ident in rows:
            violations.append(
                f'{ident} が references.md に 2 回登録 (line {lineno} / {rows[ident]["line"]})')
        rows[ident] = {'ns': m.group(1), 'n': int(m.group(2)), 'key': key,
                       'state': state, 'dup': dup_cell, 'line': lineno}
        if key and key != '—':
            key_to_ids[(m.group(1), key)].append(ident)
    return rows, key_to_ids, violations


def load_reservations(ref_path: Path):
    """references.md の予約の表から (ns, lo, hi, 枝, line) の列と、書式の違反を返す。

    予約として読むのは、見出しの行（`| 区画 | ...`）から次の空行までの表の中だけ。
    表の外で予約らしい行は予約として効かせず違反にする（例やコードブロックの行で欠番を埋めない）。
    表の中の行は、見出し・区切りの他はどれも `| V399-V412 | 枝 | ... |` の形でなければ違反。
    """
    res, violations = [], []
    in_table = False
    in_code = False
    tables = 0
    for lineno, line in enumerate(ref_path.read_text(encoding='utf-8').splitlines(), 1):
        # コードブロックの中は例なので読まない（見出しつきの例が本物の予約として効かないように）
        if line.lstrip().startswith('```'):
            in_code = not in_code
            in_table = False
            continue
        if in_code:
            continue
        if RESERVE_HEADER.match(line):
            in_table = True
            tables += 1
            continue
        if in_table and not line.strip():
            in_table = False
            continue
        if in_table and not line.strip().startswith('|'):
            # 表は空行で閉じる。先頭の | が欠けた行を黙って表の終わりにしない
            violations.append(f'予約の表の中に表の行でない行がある (line {lineno}): 表は空行で閉じる')
            continue
        m = RESERVE.match(line)
        if not in_table:
            if m or RESERVE_LOOSE.match(line):
                violations.append(f'予約の表の外に予約の形の行がある (line {lineno}): 予約は「| 区画 |」の表の中に書く')
            continue
        if SEPARATOR.match(line):
            continue
        if not m:
            violations.append(f'予約の行の書式が違う (line {lineno}): `| V399-V412 | 枝 | ... |` の形で書く（半角のハイフン）')
            continue
        ns, lo, ns2, hi, branch = m.group(1), int(m.group(2)), m.group(3), int(m.group(4)), m.group(5)
        if ns != ns2 or lo < 1 or lo > hi or not branch:
            violations.append(f'予約の行が不正 (line {lineno}): 名前空間の一致・1 ≦ 下限 ≦ 上限・枝の名前が要る')
            continue
        res.append((ns, lo, hi, branch, lineno))
    if tables > 1:
        violations.append(f'予約の表が {tables} つある: 1 つにまとめる')
    return res, violations


def collect_citations(roots, root: Path):
    """指定ルート配下 (references.md 以外) の inline 引用を集める。

    ⚠️ 初版は docs/ しか見ていなかったが、experiments/ の notes.md にも
    reproducibility-discipline ルール 5 が借用手法の [n] を義務づけており、
    そこの未登録参照が検出できていなかった。
    """
    cited: dict[str, list[str]] = defaultdict(list)
    for base in roots:
        if not base.exists():
            continue
        for path in sorted(base.rglob('*.md')):
            if path.name == 'references.md':
                continue
            text = path.read_text(encoding='utf-8', errors='replace')
            for lineno, line in enumerate(text.splitlines(), 1):
                for m in CITE.finditer(line):
                    cited[f'[{m.group(1)}{m.group(2)}]'].append(
                        f'{path.relative_to(root).as_posix()}:{lineno}')
    return cited


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == '--self-test':
        return self_test()
    root = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
    return check(root)


def check(root: Path) -> int:
    rows, key_to_ids, violations = load_references(root / 'docs' / 'references.md')
    reservations, res_viol = load_reservations(root / 'docs' / 'references.md')
    violations += res_viol
    # 走査ルート: docs/ (本文 SSOT) と experiments/ (notes.md の借用手法 [n])。
    # .steering/ はタスク単位の作業記録で本文ではないため既定では見ない。
    scan_roots = [root / 'docs', root / 'experiments']
    cited = collect_citations(scan_roots, root)

    print(f'=== references.md: {len(rows)} 行 ===')
    for ns in ('P', 'V'):
        ns_rows = [v for v in rows.values() if v['ns'] == ns]
        nums = sorted(v['n'] for v in ns_rows)
        # 予約の検査は登録の行の有無によらず行う（区間のまま判定し、大きな区間でも集合を作らない）
        ns_res = sorted((lo, hi, br, ln) for (n2, lo, hi, br, ln) in reservations if n2 == ns)
        for i, (lo, hi, br, ln) in enumerate(ns_res):
            for (lo2, hi2, br2, ln2) in ns_res[i + 1:]:
                if lo2 <= hi:
                    violations.append(f'予約 {ns}{lo}-{ns}{hi} (line {ln}) と {ns}{lo2}-{ns}{hi2} (line {ln2}) が重なる')
            taken = [n for n in nums if lo <= n <= hi]
            if taken:
                violations.append(
                    f'予約 {ns}{lo}-{ns}{hi} ({br}・line {ln}) に登録の行がある {taken[:5]}'
                    f'{"…" if len(taken) > 5 else ""}: 枝が入ったら、区画が全部埋まれば予約の行を消し、'
                    f'一部なら残りの区画に縮める')
            print(f'  [参考] 予約 {ns}{lo}-{ns}{hi}: {br}')
        if not nums:
            continue
        holes = sorted(set(range(1, max(nums) + 1)) - set(nums))
        tombs = sorted(v['n'] for v in ns_rows if 'tombstone' in v['state'])
        open_holes = [h for h in holes if not any(lo <= h <= hi for (lo, hi, _, _) in ns_res)]
        print(f'  {ns}1..{ns}{max(nums)} / 実数 {len(nums)} / 欠番 {open_holes or "なし"} '
              f'(予約で埋まる欠番 {len(holes) - len(open_holes)}) '
              f'/ tombstone {[f"{ns}{t}" for t in tombs] or "なし"}')
        if open_holes:
            violations.append(f'{ns} 名前空間に欠番 {open_holes} (append-only なら起きない・'
                              f'未マージの枝の区画なら予約の表に書く)')

    for (ns, key), ids in sorted(key_to_ids.items()):
        # tombstone 済みの行は「重複を撤回した結果」なので違反に数えない
        # (tombstone は規約が定める重複の *是正手段* そのもの)。
        live = [i for i in ids if 'tombstone' not in rows[i]['state']]
        if len(live) <= 1:
            if len(ids) > 1:
                print(f'  [参考] key={key} の重複は tombstone で是正済み -> {ids}')
            continue
        # ルール 4 の例外 (2026-08-16): 同一文献の *別主張* は別 ID を許すが、
        # 「重複」列での相互リンクが必須。リンクの無い同一 key は「気付かずに
        # 二重登録した事故」であり違反 ([P130] がその型)。
        #
        # ⚠️ 初版は len(linked) >= len(live) - 1 で **片方向リンクを通していた**
        #    (規約が掲げる模範例 [V45]/[V51] 自体が片方向だった)。「相互」を要求する
        #    以上、全行がリンクを持つことを求める。
        # ⚠️ 部分文字列一致もやめる —— 裸表記 `=V45` に対し `V4` が誤ヒットする。
        unlinked = []
        for ident in live:
            dup_cell = rows[ident]['dup']
            if not any(re.search(rf'{sib[1]}{sib[2:-1]}(?!\d)', dup_cell)
                       for sib in live if sib != ident):
                unlinked.append(ident)
        if not unlinked:
            print(f'  [参考] key={key} の重複は相互リンク済み (ルール 4 の例外) -> {live}')
        else:
            violations.append(
                f'{ns} 名前空間内で key={key} が重複し、「重複」列の相互リンクが片側だけ '
                f'-> リンクが無い行: {unlinked} / 重複群: {live} (citation-ssot ルール 4)')

    unregistered = {i: v for i, v in cited.items() if i not in rows}
    for ident, locs in sorted(unregistered.items()):
        violations.append(f'{ident} が未登録 ({len(locs)} 箇所) 例: {locs[:3]}')

    print(f'\n=== docs/ + experiments/ の引用: {len(cited)} 種 ===')
    tomb_cited = {i: v for i, v in cited.items()
                  if i in rows and 'tombstone' in rows[i]['state']}
    if tomb_cited:
        print('  [要目視] tombstone が引用されている '
              '(撤回の説明そのものなら正常・有効な出典として使っていたら違反):')
        for ident, locs in sorted(tomb_cited.items()):
            print(f'    {ident}: {locs}')

    never = sorted(i for i in rows if i not in cited)
    if never:
        print(f'  [参考] 登録済みだが本文で未引用: {len(never)} 件 {never}')

    print()
    if violations:
        print(f'=== VIOLATION {len(violations)} 件 ===')
        for v in violations:
            print(f'  - {v}')
        return 1
    print('=== 違反なし ===')
    return 0


def self_test() -> int:
    """予約の扱いの陽性対照。小さな references.md を作って、違反の有無が期待どおりかを見る。"""
    import tempfile

    def row(n):
        return f'| [V{n}] | doi:10.0/{n} | 著者 — 題 | active |'

    H = '| 区画 | 枝 | 用途 |'

    cases = [
        ('欠番があり予約が無い → 違反', [row(1), row(2), row(5)], 1),
        ('欠番を予約が埋める → 違反なし', [row(1), row(2), row(5), H, '| V3-V4 | docs/x | 論文 |'], 0),
        ('予約の区画に登録の行がある → 違反', [row(1), row(2), row(3), row(5), H, '| V3-V4 | docs/x | 論文 |'], 1),
        ('予約どうしが重なる → 違反', [row(1), row(9), H, '| V2-V5 | docs/x | a |', '| V5-V8 | docs/y | b |'], 1),
        ('en dash（U+2013）の予約の行 → 違反（欠番が無くても読み落とさない）', [row(1), row(2), H, '| V3–V4 | docs/x | 論文 |'], 1),
        ('全角のハイフン（U+FF0D）の予約の行 → 違反', [row(1), row(2), H, '| V3－V4 | docs/x | 論文 |'], 1),
        ('左の名前空間が欠けた予約の行 → 違反', [row(1), row(2), H, '| 3-V4 | docs/x | 論文 |'], 1),
        ('表の外の予約の形の行は欠番を埋めない → 違反', [row(1), row(4), '', '| V2-V3 | example | e |'], 1),
        ('表の外の崩れた予約の形の行（欠番なし） → 違反', [row(1), row(2), '', '| V3–V4 | example | e |'], 1),
        ('登録の行が無い名前空間でも予約の重なりを見る → 違反', [row(1), H, '| P2-P5 | docs/x | a |', '| P4-P8 | docs/y | b |'], 1),
        ('大きな区間の予約でも落ちない → 違反なし', [row(1), row(2), H, '| V3-V900000000 | docs/x | 論文 |'], 0),
        ('予約が欠番の一部しか埋めない → 違反', [row(1), row(6), H, '| V2-V4 | docs/x | 論文 |'], 1),
        ('下限が上限より大きい予約の行 → 違反', [row(1), row(2), H, '| V5-V4 | docs/x | 論文 |'], 1),
        ('名前空間が食い違う予約の行 → 違反', [row(1), row(2), H, '| V3-P4 | docs/x | 論文 |'], 1),
        ('予約の表が 2 つ → 違反', [row(1), row(5), H, '| V2-V3 | docs/x | a |', '', H, '| V4-V4 | docs/y | b |'], 1),
        ('コードブロックの中の見出しつきの例は効かない → 違反', [row(1), row(4), '```', H, '| V2-V3 | x | a |', '```'], 1),
        ('表の最後の行の先頭の | が欠けた → 違反', [row(1), row(2), H, ' V3-V4 | docs/x | 論文 |'], 1),
        ('下限が 0 の予約の行 → 違反', [row(1), row(2), H, '| V0-V0 | docs/x | 論文 |'], 1),
    ]
    failed = 0
    for name, lines, want in cases:
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / 'docs').mkdir()
            (Path(d) / 'docs' / 'references.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
            import contextlib, io
            with contextlib.redirect_stdout(io.StringIO()):
                got = check(Path(d))
        ok = got == want
        failed += not ok
        print(f'  [{"ok" if ok else "NG"}] {name} (exit {got}・期待 {want})')
    print('=== self-test ' + ('OK' if not failed else f'NG {failed} 件') + ' ===')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
