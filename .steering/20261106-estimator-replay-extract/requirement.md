# estimator-replay-extract —— 推定器と replay の切り出し（論文 1 の公開物）

## 背景

公開データの知見の論文 1 の attack-me（manuscript）round 2 で、4/4 が止める理由に「推定器と replay が未公開で外から再現できない」を挙げた。判断 37（`.steering/20261105-public-data-findings-paper/decisions.md`）で、推定器と replay だけを HMM 0.5.0 の時点で固定して切り出し、版と SHA-256 つきで別の公開 repo＋Zenodo に出すと決まった。入力のフック・logger・介入・O1 は出さない。GSE 本体の OSS と JOSS は未踏の後のまま。

論文で使った gse-replay は SHA-256 `26cae610383fb6de01651cc904895efa72a691c3dd1e27689a14a4ca51c33bb3`（`~/gse-public-data/klicke/bin/gse-replay`）。ソースは origin/main `24767c7e`（`experiments/20261101-klicke-early-stall-trigger/env.md`）。

## ゴール

`analysis/` の OS 非依存の部分と、引数なしの経路（1 段目・推定の行）と `--features`（onset と観測区間）だけを持つ薄い replay を、独立の crate に組む。論文が replay に通した 3 つのデータ（CS1 2019 年版・CoAuthor・KLiCKe）の見た書き手の全課題で、今の gse-replay と出力がバイトで全件一致する。

## スコープ

### 含むもの
- 24767c7e のソースを逐語で写し、入力の層（`crate::input`）への参照と、使わない経路（metrics・介入・較正・snapshot 比較）だけを外す最小の差分。元との差分の一覧。
- 置き場は GSE の枝の中の独立 crate（workspace に入れない）。
- 全件一致の門のスクリプト（3 データの見た書き手の全課題・引数なしと `--features` の両方）。
- ライセンス表記 MIT OR Apache-2.0。

### 含まないもの
- 入力のフック・logger・介入・O1・Tauri の部分。
- 取り置きの書き手（開けない）。
- 公開 repo の組み立て・GitHub と Zenodo への公開（次のタスク・引き継ぎ §2 の 3）。
- 推定器の挙動の変更（HMM_VERSION 0.5.0 のまま）。

## 受け入れ条件

- [x] crate が GSE の workspace の外で `cargo build --release` でき、`cargo test` が緑。
- [x] 元（24767c7e）とのファイルごとの差分の一覧があり、外した部分が使わない経路と入力の層への参照だけである。
- [x] 門: 3 データの見た書き手の全課題で、引数なしの出力と `--features` の出力が今の gse-replay とバイトで一致（件数と不一致 0 を記録）。陽性対照（1 か所変えた版で不一致が出る）つき。
- [x] 取り置きを開けていない（一覧のファイルを読む処理が除外だけ）。
- [x] code-reviewer と /cross-review を通す。

## 関連ドキュメント

- `.steering/20261105-public-data-findings-paper/decisions.md` 判断 35〜37
- `.steering/_handoff/next-session-gse-public-data-findings-paper-11.md`
- `experiments/20261105-findings-paper1-prefreeze/`・`experiments/20261106-findings-paper1-exploration/`

## 運用メモ
- /reimagine 適用: No
- 理由: 切り出し方（逐語で写し最小の差分）と置き場・門の範囲は研究者が AskUserQuestion で決めた（2026-11-06）。挙動を変えない写しで、設計の選択肢が残っていない。
