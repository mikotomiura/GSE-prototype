# 3 つの検査の公開の道具の設計（three-checks-tool-design）

## 背景

- ADR-054（Accepted・2026-11-15）で位置づけの一言を「本文を保存しない打鍵の観測から、作業の停滞についてどこまで言えるかを、予測・定義・漏れの 3 つの検査で確かめる」に改めた。D5（判断 9）で、作るものは「3 つの検査を他の打鍵の記録にも当てられる公開の道具」を主にし、GSE のアプリ（手跡・招待）をその地図に従う最初の利用例にすると決めた。
- 研究者は 2026-11-16 に、未踏と言える形にする主の道としてこれ（A: 道具を主・B: 手跡を最初の利用例）を選んだ（ADR-054 D5 の確認で、新しい決定ではない）。
- 道具の入力・出力・完成の条件の案は `docs/mitou_submission/core-and-edge-material.md` §1・§3・§5 にあるが、実装できる設計（言語・置き場・入力の形式・各検査の最小の実装・判定の規則の扱い・回帰のテスト）はまだ無い。
- 2026-11-16 の O1 の実施の記録（`experiments/20261116-o1-conduct-record/`）の後、予測の面の物差しを「手で作った HMM の失敗」から「学習器の上限（床・新しい推定器・上限の 3 つの比べ）」に移す必要が出た（引き継ぎ追記・`gse-mhd-revision-plan-after-stage1.md`）。

## ゴール

道具の設計書（design.md）を書き、研究者が承認する。実装はしない。

## スコープ

### 含むもの
- 道具の形（言語・置き場・公開の単位）
- 入力の形式（最小の列・GSE の NDJSON と公開データからの変換）
- 3 つの検査それぞれの最小の実装と、面の判定の規則（値は利用者が事前に決めて入れる）
- 出力（面ごとの判定・証拠の格・限定・検査していない脅威）
- 完成の条件の検査（既定の例の規則で今の 3 つの判定を再現・GSE 自身の記録で正解の無い面を「未検査」と返す）
- 未踏の期間に入るものと、その前に済ませるものの区別
- 今のコード（論文 1・論文 2・IME 論文 1・照合の論文）の使い回しの見込み

### 含まないもの
- 実装・計算の実行・holdout を開くこと
- 照合の論文の原稿とその枝（`docs/public-keystroke-matching-manuscript`）への書き込み
- 打鍵の内容・NDJSON・公開データの記録を外部の LLM（Codex を含む）に送ること
- 新しい ADR（ADR-054 D5 の範囲内。設計の中で既存 ADR と食い違う判断が出たら研究者に問う）
- push と PR（研究者に確かめてから）

## 受け入れ条件

- [ ] design.md が「設計で決めること」1〜6 と予測の面の物差し（学習器の上限）にそれぞれ答えている
- [ ] 各決定に研究者の選択（AskUserQuestion）か一次の根拠が decisions.md に残っている
- [ ] 完成の条件が外れうる形（回帰のテストの名前と期待値の出どころ）で書かれている
- [ ] 主張の数値と既存コードの位置は一次（file:line・commit）で照合してある
- [ ] /cross-review（Codex を含む）を通した

## 関連ドキュメント

- `.steering/_handoff/next-session-gse-three-checks-tool-design.md`（入口）
- `docs/adr/ADR-054-positioning-three-checks.md` D2〜D5
- `docs/mitou_submission/core-and-edge-material.md` §1・§3・§5
- `.steering/20261115-gse-core-and-edge/attack-me/outline-core-edge/round-3/verdict.md`（枝 `docs/gse-core-and-edge`）
- `experiments/20261116-o1-conduct-record/notes.md` §4
- `.steering/_handoff/gse-mhd-revision-plan-after-stage1.md`（本線のチェックアウトの未追跡ファイル）

## 運用メモ
- /reimagine 適用: Yes（予定）
- 理由: 公開の外部インターフェース（入力の形式・判定の規則・出力）を定め、言語と置き場に複数案がある。設計の初案を書いた後に /reimagine で比べ、codex-consult で第二意見を取る（送るのは設計の抜粋だけ）。
