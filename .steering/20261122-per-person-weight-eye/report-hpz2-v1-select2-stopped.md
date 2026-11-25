# HP Z2 の報告: handoff-hpz2-v1-select2 は手順 2 で止めた

> 作成: 2026-11-25（HP Z2 のセッション）。手順書は `handoff-hpz2-v1-select2.md`。手順 3〜6（V1・P-XMACH・select2・results の commit）は回していない。コード・results には触れていない。

## 環境

- 枝 `exp/gse-per-person-weight-eye`、HEAD `49a90d8b`（c7645298 からの差分は文書だけで、コードは同じ）
- worktree: `C:\Users\SDS02\GSE-prototype-weight-eye`
- Python 3.11.9・numpy 2.4.4
- npz は既定の置き場にある（中身は開いていない）

## 1. 1 回目の赤（P-HASH）—— 改行の変換が原因で、環境側で直した

`core.autocrlf=true` のまま worktree を作ると、`code_hash()` の前に P-HASH が例外で止まった:

```
SHA-256 が条件の値と違う（P-HASH）: {'...\\experiments\\20261110-per-person-sensitivity\\scripts\\synth.py': '04a06c98ffaecc80a34edf146bf0972b983b5b3a9a9595ceda3ef72d52672d45', '...\\experiments\\20261110-per-person-sensitivity\\scripts\\pinned.py': '6e801ee14d0a00001e9b79027d4b1bbab3b5db250dcf2d1dcd1b1330455861b8', '...\\experiments\\20261110-per-person-sensitivity\\results\\calibration.json': 'b6ea937eda88632b05e02badaf8ce83fd91d20f34bc4d3e06f4d0287f19e6be4'}
```

worktree を `git -c core.autocrlf=false worktree add ...` で作り直したところ、P-HASH は通った。手順書の手順 1 にこの指定を足すとよい。

## 2. 残った赤（code_hash が Mac と違う）—— コードの問題なので止めた

- HP Z2: `67f43b66f975fa16bf9d22f15d480ace58b6e0b501bd49cb4c5b1cac655681be`
- Mac（`results/v1/selftest.json`）: `646328e370c9a00f2cee78b7788876dce9305db0ea58619be886f62bbe21a44a`

原因は `experiments/20261122-per-person-weight-eye/scripts/run_eye.py:33` の `os.path.relpath(p, GN.EXP)`。Windows では `\` 区切りのパスが返り、その文字列がハッシュに入る。

確認: コードは変えずに、同じ計算で `relpath(...).replace(os.sep, "/")` にして計算し直すと、`646328e370c9a00f…` で Mac と一致した。ファイルの中身は一致していて、違うのはパスの区切り文字だけ。

`run.sh:36` の `pinned={os.path.relpath(p, exp): v ...}` も同じ書き方。ハッシュには入らないが、manifest に記録されるパスも Windows では `\` 区切りになる。

## 研究者が決めること

- `relpath(...).replace(os.sep, "/")` に直せば、どの機械でも同じハッシュになる。ただし `run_eye.py` 自体がハッシュの対象なので、直すと code_hash が変わる。そのときは Mac で V1 を回し直して新しい `selftest.json` をコミットし、HP Z2 で手順をもう一度行う。
- 直すかどうかと、decisions.md への残し方は研究者が決める。HP Z2 のセッションは何も決めていない。
