# 設計

手本は `mikotomiura/stall-runup-equivalence`（組み方の記録は GSE-prototype-paper2 の `.steering/20261106-public-repo-assembly/`）。

## 判断 1 の要点（2026-11-20・研究者の選択）
コードと記録は書いたときのまま（日本語）出す。英訳しない。理由: 各ディレクトリが互いのスクリプトと集計を SHA-256 で
固定して読み込む（pinned*.py・provenance.json）ので、1 バイトでも変えると results を出したコードと別物になる。
英語は README と docs/conditions-summary.md で補う。

## 置き方（GSE のパスのまま）
```
per-person-keystroke-models/
  README.md / README.ja.md / LICENSE-MIT / LICENSE-APACHE / LICENSE-docs / CITATION.cff / .zenodo.json / .gitignore
  experiments/<13 の解析と確かめ>/          ← 枝 docs/gse-paper3-per-person-learning の HEAD（追跡済み）
  experiments/20261107-structure-deficit-test/ ← origin/main（この枝に無い・S8 の確かめ 2）
  experiments/20261031-*・20261101-*・20261102-* ← 依存先。scripts・run*.sh・conditions*・data.md・env.md・SEED だけ
  kit/symbols/                               ← papers/per-person-learning/kit/symbols
  paper/                                     ← main.tex・supplement.tex（\journalline を空に）・references.bib・figdata/
  docs/conditions-summary.md・docs/media/
  tools/  check_release.py・control_check_release.sh・check_pins.py・verify.sh
  gse-commits.tsv・gse-source.tsv
```
- 推定器（gse-replay）は写さない。stall-runup-equivalence 0.2.2（10.5281/zenodo.24026278）の estimator/ を指す（同じ build の SHA-256 26cae610…）。
- 様式（sn-jnl.cls・sn-basic.bst）は LPPL だが手本に倣い入れず、paper/BUILD.md で入手先を書く。outline.md は入れない（投稿先と内部の状態）。
- 書き換えるのは 2 ファイルだけ: objective-and-pause/results/summary.json（pause の min/max 6 個を外す・indent=1 で書き直す）と paper/supplement.tex（\journalline を空に）。README に明記。

## 検査
1. check_release.py（手本の形の検査）＋ kit の 2 つの CSV と conformance の .json.gz を名指しで許可（理由を docstring に）。--private で取り置きの一覧と外した 6 個の値を探す。
2. check_pins.py: 8 本の pinned*.py を import して SHA-256 の鎖が公開物の中で閉じることを確かめる（壊して赤も見る）。
3. kit: selftest.py と conformance/check.py。
4. 陽性対照: control_check_release.sh。

## テスト・レビュー
verify.sh が 0。security-checker（公開物の全体）と /cross-review（tools・README・assemble.sh。データの値は Codex に送らない）。
