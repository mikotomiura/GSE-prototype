# 長さの並びの一意性（ADR-039 D6 の関門の最初の実測）

## 背景

ADR-039 D6（公開前の関門）の攻撃のうち「照合」は、公開した打鍵の記録を候補の文章と突き合わせ、その文章を書いたときの記録かを当てる攻撃である。記録には文字が残らないが、境界（句読点の `SentencePunctuation`・`Enter`）の間の打鍵の個数の並びが残る。この並びが公開テキストの中でどれだけ一意になるかは、文献では決まらなかった（`docs/literature/20261009-keystroke-release-reidentification.md` カード 3・claim #8）。研究者は 2026-10-09 に、関門の実測の最初の一歩をこの見積もりにすると決めた（`.steering/20261009-release-deidentification-survey/decisions.md` 判断 7・9・10・11、引き継ぎ `.steering/_handoff/next-session-length-sequence-uniqueness.md`）。

## ゴール

青空文庫の公開テキストで、句読点（、。）と改行の間の打鍵数の並びについて、次の 2 つを見積もり、結果を `experiments/20261009-length-sequence-uniqueness/` と本作業記録に残し、ADR-039 D6 と issue #333 に要点を返す。

1. 長さを k 個並べたとき、コーパスの中で位置が一意に決まる割合（k の関数）。
2. 候補の文章 N 本から正解を当てる照合の正答率を、偶然の水準 1/N と並べたもの。

条件は、理想（推敲なし・打鍵数が正確）、雑音あり（3 段と源ごと）、確定の Enter も区切りに入る条件（癖の仮定 2 つ）。

分かるのは「長さだけを、正確に使える攻撃者」の場合の目安であって、照合の危険の上限ではない。この実測は合否を判定しない。

## スコープ

### 含むもの
- 青空文庫の作品の選定・取得（版は zip の SHA-256 で固定）と、かな化（SudachiPy の読み）・ローマ字の打鍵数への換算
- 2 つの指標の計算、採点の処理の自己検査（合成データ）
- 確定の Enter と改行を記録の項目から見分けられるかの、コードと仕様での確認
- 結果のノート、ADR-039 D6 への日付つきの注、issue #333 へのコメント

### 含まないもの
- O1・G1・Phase1 の記録（NDJSON）を読むこと・使うこと
- 研究者や参加者の文章をコーパスにすること
- 合格の基準（ADR-039【決 6】の許す差・信頼の水準・本番の N）を決めること
- 文節の区切り（変換の Space の位置）を長さの定義に使うこと（確定の Enter の癖の仮定にだけ使う）
- 時刻の癖・本人の過去の文章・言語モデルを使う照合、合成入力での照合攻撃の試作（次の一歩）
- 英語のコーパス（後で足す）

## 受け入れ条件

- [ ] 換算表・かな化の手順・雑音の大きさ・k・N・偶然の水準の前提を、結果を見る前に作業記録と `experiments/` に書き、コミットしてから本計算を回した
- [ ] 採点の自己検査（候補の大きさが不揃い・同じ並びが複数の候補に出る・正解のラベルの頻度・情報を使わない予測が 1/N）が通った
- [ ] `bash experiments/20261009-length-sequence-uniqueness/run.sh` で、取得済みの zip から結果が再現する（zip の SHA-256 を照合する）
- [ ] 結果のノートが、上限ではないこと・コーパスと分け方への依存・打鍵の個数は本文の長さと同じではないことを書いている
- [ ] ADR-039 D6 に日付つきの注、issue #333 にコメントを足した（本文は消さない）
- [ ] `/finish-task`（code-reviewer と `/cross-review`）を通した

## 関連ドキュメント

- `docs/adr/ADR-039-research-use-and-release.md` D5・D6
- `docs/literature/20261009-keystroke-release-reidentification.md` カード 3・「GSE への還元」
- issue #333
- `src-tauri/src/analysis/anonymize.rs`（`KeyCategory::from_vk`）・`src-tauri/src/logger.rs`（key 行）・`src-tauri/src/input/ime_compose.rs`
- `papers/ime-observation/kit/corpus/build_corpus.py`・`papers/ime-observation/kit/gen/romaji.py`（前処理とローマ字の表の出どころ）

## 運用メモ
- /reimagine 適用: No
- 理由: 主な設計（コーパス・長さの定義・2 つの指標・理想と雑音と確定の Enter の条件・偶然の水準の前提）は 2026-10-09 に研究者が決めており、残りの未決（作品・読みの誤り・k・N・雑音の大きさ）も AskUserQuestion で決まった。作り直しても決まった点をなぞるだけになる（研究者の回答 2026-10-09）。
