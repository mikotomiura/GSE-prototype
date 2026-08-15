#!/usr/bin/env python3
"""引用整合の機械検算 (citation-ssot の規約をコードで守る)。

`docs/references.md` を SSOT として、以下を検査する:

1. **未登録参照** — docs/ 本文の `[Pn]`/`[Vn]` が references.md に無い
2. **同一名前空間内の key 重複** — DOI / arXiv / 正規化 URL の二重登録 (ルール 4 違反)
   ※ 名前空間跨ぎ (`[P2]`=`[V9]` 型) は規約上허容なので検出しない
3. **tombstone の引用** — 撤回済み ID が本文で使われていないか (説明目的の言及は要目視)
4. **欠番** — append-only なのに番号が飛んでいないか
5. **件数** — `_index.md` などに手書きされた件数の照合材料 (実測値を出す)

なぜ要るか: 件数の手書きは **2026-08-16 に 1 日で 2 回陳腐化した**。
重複登録も同日に `[P130]` (誤って気付いた) と `[V45]`/`[V51]` (気付いていなかった) の 2 件あった。
→ 目視では追随できないので機械で検算する。

使い方:
    PYTHONUTF8=1 python scripts/check_citations.py [repo_root]

exit code:
    0 = 違反なし / 1 = 違反あり (未登録参照 or 同一名前空間内 key 重複)
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROW = re.compile(r'^\|\s*\[([PV])(\d+)\]\s*\|')
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


def collect_citations(docs_dir: Path, root: Path):
    """docs/ 配下 (references.md 以外) の inline 引用を集める。"""
    cited: dict[str, list[str]] = defaultdict(list)
    for path in sorted(docs_dir.rglob('*.md')):
        if path.name == 'references.md':
            continue
        text = path.read_text(encoding='utf-8', errors='replace')
        for lineno, line in enumerate(text.splitlines(), 1):
            for m in CITE.finditer(line):
                cited[f'[{m.group(1)}{m.group(2)}]'].append(
                    f'{path.relative_to(root).as_posix()}:{lineno}')
    return cited


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
    rows, key_to_ids, violations = load_references(root / 'docs' / 'references.md')
    cited = collect_citations(root / 'docs', root)

    print(f'=== references.md: {len(rows)} 行 ===')
    for ns in ('P', 'V'):
        ns_rows = [v for v in rows.values() if v['ns'] == ns]
        nums = sorted(v['n'] for v in ns_rows)
        holes = sorted(set(range(1, max(nums) + 1)) - set(nums)) if nums else []
        tombs = sorted(v['n'] for v in ns_rows if 'tombstone' in v['state'])
        print(f'  {ns}1..{ns}{max(nums)} / 実数 {len(nums)} / 欠番 {holes or "なし"} '
              f'/ tombstone {[f"{ns}{t}" for t in tombs] or "なし"}')
        if holes:
            violations.append(f'{ns} 名前空間に欠番 {holes} (append-only なら起きない)')

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
        linked = [i for i in live
                  if any(sib[1:-1] in rows[i]['dup'] for sib in live if sib != i)]
        if len(linked) >= len(live) - 1:
            print(f'  [参考] key={key} の重複は相互リンク済み (ルール 4 の例外) -> {live}')
        else:
            violations.append(
                f'{ns} 名前空間内で key={key} が重複し、「重複」列の相互リンクが無い '
                f'-> {live} (citation-ssot ルール 4)')

    unregistered = {i: v for i, v in cited.items() if i not in rows}
    for ident, locs in sorted(unregistered.items()):
        violations.append(f'{ident} が未登録 ({len(locs)} 箇所) 例: {locs[:3]}')

    print(f'\n=== docs/ 内の引用: {len(cited)} 種 ===')
    tomb_cited = {i: v for i, v in cited.items()
                  if i in rows and 'tombstone' in rows[i]['state']}
    if tomb_cited:
        print('  [要目視] tombstone が引用されている '
              '(撤回の説明そのものなら正常・有効な出典として使っていたら違反):')
        for ident, locs in sorted(tomb_cited.items()):
            print(f'    {ident}: {locs}')

    never = sorted(i for i in rows if i not in cited)
    if never:
        print(f'  [参考] 登録済みだが docs/ 本文で未引用: {len(never)} 件 {never}')

    print()
    if violations:
        print(f'=== VIOLATION {len(violations)} 件 ===')
        for v in violations:
            print(f'  - {v}')
        return 1
    print('=== 違反なし ===')
    return 0


if __name__ == '__main__':
    sys.exit(main())
