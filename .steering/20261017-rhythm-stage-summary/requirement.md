# 背景のステージの机上の検査 —— 6 回のまとめ

## 背景

研究者の提案「打鍵のリズムで滑らかに動く背景（ステージ）」は、親タスク `.steering/20261012-portrait-rhythm-motion/` で EH3 の後に回す候補になった（同 decisions 判断 1）。最初の段は、合成の打鍵の列で、リアルタイムの写像（打鍵 → 描画のパラメータ）が停滞・打鍵の有無・速さをどれだけ写すかを測る机上の検査で、ねらいは「試作を作るか否かを安く決める」ことだった（同 判断 4）。

机上の検査は 2026-10-12〜10-17 に 6 回回した（第 1 回・第 2 回・中間の world・揺れの world・原因の切り分け・揺れの形）。最後の回の後、研究者は倍率の world を作り直さず、ここで区切って 6 回をまとめることを選んだ（`.steering/_handoff/next-session-rhythm-stage-after-shape-world.md` §3 の候補 2・2026-10-17）。

引き継ぎ: `.steering/_handoff/next-session-rhythm-stage-summary.md`。

## ゴール

研究者が、背景のステージで次に何をするか（読み 1・2 を分ける検査・試作・机上でもう一段・ここで止める）を決められる材料を、1 つのファイルにまとめる。

## スコープ

### 含むもの
- まとめの本文 `summary.md`（このタスクの dir）。骨（decisions 判断 2）:
  - もともと何を確かめたかったか（親タスクの判断 4・項目 1〜6）。
  - 6 回の world・段・結果を 1 つの主表に（天井・赤・判定不能）。
  - 分かったこと・分からないこと（読み 1 と読み 2 の別・倍率の成分）・計器の限り。
  - 親タスクの判断 3（秒未満を使うか）・判断 4（試作を作るか）・判断 5（訂正を読まない）への材料と、項目 2〜4・6 の短い要約。
  - 次に問うなら: 読み 1・2 を分ける案と、背景のステージの次の段の選択肢（得るもの・費用・限り）。Claude の見立ては「見立て・決定ではない」と明記する。
- 主表を 6 回の一次の JSON と照らす検査 `check_summary.py`（このタスクの dir）。
- `.idea` §12 に足す短い節の文 `idea-section12-addendum.md`（このタスクの dir・追記は研究者）。

### 含まないもの
- 6 回の入れ物・判定・notes・design を書き換えること。判定を作り直すこと。
- 新しい計算（当てはめ・生成）。
- `src-tauri/`・EH3 のファイル。`.idea` に直接書くこと。
- NDJSON の生ログ（合成も）・キーストロークの内容を外部の LLM（Codex を含む）に送ること。
- 「GSE が示した」と書くこと。合成の world の結果を人の打鍵や描画の効果の主張にすること。

## 受け入れ条件

- [ ] `summary.md` が decisions 判断 2〜4 の骨と書き方を満たし、言い方が各回の固定した読み方の範囲に留まっている
- [ ] `python check_summary.py`（このタスクの dir で）が bad 0 で終わり、変異（数を 1 つ変える・行を消す）で落ちることを確かめてある
- [ ] `idea-section12-addendum.md` がある
- [ ] `/cross-review` 2 巡（1 巡目: 自文書と 6 回の記録との矛盾、2 巡目: 足した言い方の境目）の結果と対応が `decisions.md` にある

## 関連ドキュメント

- `.steering/20261012-portrait-rhythm-motion/`（判断 1〜11・idea-section12.md）
- 6 回の記録: `.steering/` と `experiments/` の `20261012-rhythm-stage-desk-check`・`20261013-rhythm-stage-round2`・`20261014-rhythm-stage-graded-world`・`20261014-rhythm-stage-speed-confound-world`・`20261015-rhythm-stage-speed-cause-split`・`20261015-rhythm-stage-speed-shape-world`
- `docs/literature/20261012-rhythm-stage-novelty.md`（新規性の 1 ラウンド・S-RN）
- `.steering/_handoff/next-session-rhythm-stage-desk-check.md`（机上の検査の最初の引き継ぎ・測らないこと）

## 運用メモ
- /reimagine 適用: No
- 理由: 既にある判定と読みを写してまとめる文書で、設計の選択肢を比べる局面ではない。骨は grill で確定した（研究者・2026-10-17・推奨どおり）。
