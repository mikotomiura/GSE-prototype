# 設計

## 実装アプローチ

GSE の repo の外に `~/stall-runup-equivalence`（新しい git repo）を作り、組み立てのスクリプト
`assemble.sh`（この .steering に置く・GSE の worktree から読む）で写す。手で写さず、写す一覧をスクリプトに書いて
何度でも作り直せるようにする（一覧そのものが公開物の範囲の記録になる）。

置き方は GSE のパスのまま（研究者の選択）。GSE の docs・.steering・src-tauri は入れない（判断 2）:

```
stall-runup-equivalence/
  README.md / README.ja.md / LICENSE-MIT / LICENSE-APACHE / LICENSE-docs / CITATION.cff
  estimator/                         ← papers/public-data-findings/kit/estimator/（target/・__pycache__ を除く）
  experiments/20261104-cs1-landscape/            ← 一式（scripts・条件・記録・results）
  experiments/20261105-findings-paper1-prefreeze/ ← 一式（results_holdout.failed.* も経緯として）
  experiments/20261106-findings-paper1-exploration/ ← 一式
  experiments/20261031-coauthor-pre-request-signal/scripts/{convert,add_feat}.py
  experiments/20261101-klicke-early-stall-trigger/scripts/{analyze_item2,build_work}.py
  experiments/20261102-public-data-landscape/scripts/analyze_landscape.py
  paper/                             ← papers/public-data-findings/manuscript/（原稿の tex）
  tools/  check_release.py（漏れの検査）・readme_media.py（README の図）
  docs/media/  README の図
```

依存先の実験から写すのは、論文の計算が読み込むスクリプトだけ（その results は入れない。例: CoAuthor の
`onsets_by_writer.json` は書き手ごとの値）。写す前に、論文の 3 ディレクトリのスクリプトが他に何を import・呼び出し
するかを grep で確かめ、一覧の漏れを門（`shasum -c`）と別に検査する。

## 写した先で通す検査

1. `tools/check_manifest.py`: manifest の SHA-256 が 2 回目の開始の記録の値（c821ae03…）で、公開物の 15 件が一致し、GSE の文書と .steering の 6 件は「公開しない」と出す（判断 2）。
2. `cd estimator && cargo test --locked`・`python3 -I provenance/check_provenance.py --self`。
3. `python3 -I tools/check_release.py`: 書き手の id の形（CS1 の `u` ＋数字など、データごとの形）・長い数の配列・
   取り置きの id の一覧の SHA-256 と一致するファイル・データの生のファイル（csv・zip・ndjson）・秘密の形を探す。
   陽性対照: 一時ディレクトリに写した repo へ偽の id の一覧を足して検出することを確かめる。
4. 論文の計算のスクリプトの中の絶対パス（`/Users/johnd/...`）とメールアドレスを探して報告する（写した中身は
   書き換えないので、README に「環境変数・引数で与える」と書く。書き換えが要るなら止めて相談）。

## README

- 英語 `README.md` と日本語 `README.ja.md`。手本は Affective-Tactility-Works-public（バッジ・図・何が論文のどこから来るか・
  再現の手順・ライセンス）。
- 書くこと: 論文と OSF の登録・中身の地図・データの入手（CS1 は著者へ申請・CoAuthor と KLiCKe の公開先）・
  再現の手順（crate の build、論文のスクリプトを replay を差し替えて回す）・推定器の一致の門・GSE 本体が非公開で
  `24767c7e` は著者の手元の照合のためにだけ書くこと・出さないもの（推定の行・取り置きの id・書き手ごとの値）と理由・
  係数を学んだのではないこと（手で置いた値）。
- 図: (a) 主解析と感度の AUC と同等の帯（results の JSON から `tools/readme_media.py` で作る・論文の図 1 と同じ数）、
  (b) 推定器と評価の流れの SVG。図の数値が results と一致することを検査で確かめる。

## 影響範囲

GSE の repo には `.steering/20261106-public-repo-assembly/` だけを足す。論文の原稿の Materials・要旨の置き字は
公開（DOI）の後に別に直す。

## 既存パターンとの整合性

- 手本: `~/Affective-Tactility-Works-public`（README の構成・LICENSE と LICENSE-docs の分け方・CITATION.cff）。
- 前のタスクの門と provenance の仕組みはそのまま写す（書き換えない）。

## Skill・道具の対応表（完了前に照合する）

| 場面 | 使うもの |
|---|---|
| 写す範囲の漏れ・依存の洗い出し | 自分で grep（範囲が狭い）。広がれば file-finder |
| 書き手ごとの値・秘密の混入 | `data-privacy` を参照・`tools/check_release.py`＋陽性対照 |
| 断定（「入っていない」「通る」） | `verify-before-claiming`（走らせて確かめる） |
| README の図 | `dataviz` を参照。出した図は自分で見る |
| レビュー | code-reviewer＋security-checker を並列、完了時に `/cross-review`（Codex あり） |
| 出典（README の文献） | `citation-ssot`（新しい文献を足すときだけ） |
| commit | `git-workflow`（GSE 側は docs だけなので [skip ci]・push は研究者） |
| GitHub の作成・Zenodo | 押す前に研究者に AskUserQuestion |

## テスト戦略

上の検査 1〜4 を `tools/` の 1 本のスクリプト（`tools/verify.sh`）にまとめ、写した先で回す。陽性対照（偽の id・
manifest の 1 バイト違い）で赤を見る。

## ロールバック計画

`~/stall-runup-equivalence` は公開前は手元だけなので、消して `assemble.sh` で作り直す。
