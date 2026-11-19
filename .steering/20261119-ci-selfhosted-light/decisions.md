# 判断

## 判断 1: /cross-review 1 巡目の採否（2026-11-19・Codex 47,214 トークン）

- 採る（HIGH・両者一致）: 「下げられなくても警告だけ」が実装と合っていなかった。Actions は powershell に ErrorActionPreference=stop を、bash に -e -o pipefail を付ける。→ powershell は try/catch と最後の exit 0、bash は set +e +o pipefail と exit 0。ps が空なら抜ける。親たどりに深さの上限 16。陰性対照（Worker なし・CIM の例外・ps が空・確かめの不一致）を手元で回し、どれも警告を出して rc=0 を確かめた。
- 採る（docs）: `.claude/skills/git-workflow/SKILL.md` ルール 6 の 4 と `docs/architecture/gse-design-map.md` R1 の「`feature/*` は self-hosted の CI が走る」を直した。
- 採る（記録だけ・Codex）: CPU の優先度はメモリ・I/O を抑えない。ci.yml の注に書いた。
- 保留（Codex・MEDIUM）: 優先度を下げると、研究者の計算と重なったときに 30 分の timeout に当たるかもしれない。G-GEAR で実測してから決める（tasklist）。
- 採らない（LOW）: macOS の `taskpolicy -b`。子に継ぐかが別問題で、実測が先。

## 判断 2: self-hosted の Windows の check の上限を 45 分にする（2026-11-19）

- 実測: 優先度を下げた G-GEAR の check は 21.5 分（run 44478550904・登録し直した後の初回）と 20.1 分（2 回目）。2026-10 の G-GEAR（通常の優先度）は 13〜14 分（main の 4 run）。
- 30 分の上限まで 10 分しか残らず、研究者の計算が重いときに赤になりうる（判断 1 で保留した Codex の MEDIUM）。→ self-hosted の Windows を 45 分にした。hosted へ回ったときの 60 分・Mac の 30 分は変えない。
