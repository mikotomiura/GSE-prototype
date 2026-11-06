# public-repo-assembly（論文 1 の公開 repo stall-runup-equivalence を組む）

## 背景

論文 1（公開データの知見・停滞の手前の 30 秒の変化の同等の検定）の manuscript round 2 で、4/4 が止める理由に「推定器と replay が未公開で外から再現できない」を挙げた。判断 37 で推定器と replay だけを固定で切り出して別の公開 repo＋Zenodo に出すと決め、前のタスク `20261106-estimator-replay-extract` で `papers/public-data-findings/kit/estimator/` に切り出して全件一致の門を通した（e20b63b0）。原稿の Materials は、評価・探索・変換のコード、seed、環境、検証済みファイルの manifest、replay の版と SHA-256、係数の表、データの入手手順を出すと約束している。

## ゴール

GSE の repo の外（`~/stall-runup-equivalence`）に公開 repo の中身を組み、写した先で検査が通る状態にする。GitHub の repo の作成・push・Zenodo の公開は研究者に確かめてから行う。

## スコープ

### 含むもの
- 推定器の crate 一式（`target/` を除く）。写した先で `cargo test --locked` と `check_provenance.py --self` を通す。
- 実験のスクリプトと記録を GSE のパスのまま写す。manifest（`confirm-manifest.sha256`）の照合は `tools/check_manifest.py` で、公開物の 15 件を照合し、GSE の文書と .steering の 6 件は公開しない（判断 2）。
- 原稿の tex（`paper/`）。
- 論文の計算と探索の実験ディレクトリ（`20261104-cs1-landscape`・`20261105-findings-paper1-prefreeze`・`20261106-findings-paper1-exploration`）のスクリプト・条件・記録（日本語のまま）・集計の結果。依存先の実験（`20261031-coauthor-pre-request-signal`・`20261101-klicke-early-stall-trigger`・`20261102-public-data-landscape`）は参照されるスクリプトを。
- README（英語と日本語版・図つき）・ライセンス（コード MIT OR Apache-2.0、文書と結果 CC BY 4.0）・CITATION.cff。
- 書き手ごとの値・取り置きの id が入っていないことの機械の検査（陽性対照つき）。

### 含まないもの
- GSE の `docs/`・`.steering/`・`src-tauri/`・未踏の情報（研究者の指示・判断 2）。
- 書き手ごとの値・推定の行・取り置きの id の一覧（CS1 の約束・著者の返事待ち）。
- 入力のフック・logger・介入・O1、データそのもの。
- 凍結した文書と manifest の書き換え。外枠 v6 の書き換え。
- attack-me round 3（公開 repo ができた後に別に判断する）。

## 受け入れ条件

- [ ] `~/stall-runup-equivalence` で `tools/check_manifest.py` が通る（公開物 15 件が一致・6 件は公開しない）。
- [ ] 写した crate で `cargo test --locked` が緑、`check_provenance.py --self` が OK。
- [ ] 書き手ごとの値・取り置きの id の検査が 0 件（混ぜた対照で検出する）。
- [ ] README（英・日）が中身・再現の手順・GSE 本体が非公開であること・データの入手手順を書いている。
- [ ] code-reviewer・security-checker・/cross-review（Codex あり）の指摘に対応した。
- [ ] GitHub の作成と Zenodo の公開は研究者の確認を経た（または確認待ちとして記録した）。

## 関連ドキュメント

- `.steering/_handoff/next-session-gse-public-data-findings-paper-12.md`
- `.steering/20261106-estimator-replay-extract/decisions.md`
- `.steering/20261105-public-data-findings-paper/decisions.md` 判断 35・37
- `papers/public-data-findings/manuscript/sections/discussion.tex` の Materials

## 運用メモ
- /reimagine 適用: No
- 理由: 置き方（GSE のパスのまま）と範囲は研究者が決めた。残りは写す一覧と README で、作り直して比べる案の幅が小さい（研究者の回答）。
