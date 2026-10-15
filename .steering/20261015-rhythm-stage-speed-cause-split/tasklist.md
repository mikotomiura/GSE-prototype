# tasklist —— 揺れの world の `res=sub` の赤の原因の切り分け

- [x] requirement.md・decisions.md 判断 1（研究者・2026-10-15）
- [x] design.md の下書き
- [ ] design の承認（研究者・§9 の細部を含む）
- [ ] 前のタスクの計器の SHA-256 と、e13.json を作った計器との差（`git diff 654db2b2 6710078d`・`7d38df98 6710078d`）を確かめて design に書く
- [ ] 計器: `SEED`・`config.json`・`run.sh`・`requirements.txt`・`env.md`・`data.md`
- [ ] `scripts/split.py`（作り直しの照合・`lrbin`・落とす組・読み）
- [ ] `scripts/selftest_split.py`（design §3.6）・0 件の失敗・変異を捕まえる
- [ ] 固定の前の `/cross-review` 1 巡目（design と計器）・対応を decisions に
- [ ] 固定の前の `/cross-review` 2 巡目（足した規則の境界）・対応を decisions に
- [ ] 固定（design と計器をコミット・push）
- [ ] 回す前に `gh run list` と `Get-CimInstance Win32_Process` を一次で確かめる（a4_keytar が終わるまで待つ）
- [ ] c100: スモーク → 本番（照合の門 → (a)・(b)）
- [ ] c200: スモーク → 本番
- [ ] notes.md（実行の記録・結果・読み・逸脱）
- [ ] notes の `/cross-review`
- [ ] 引き継ぎ（次: L60 の格子のタスク・揺れの形の world）
- [ ] PR（前のタスクと 1 本・計測が終わってから）
