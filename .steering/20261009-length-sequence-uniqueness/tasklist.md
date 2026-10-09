# タスクリスト

## 準備
- [x] 引き継ぎ・ADR-039 D5/D6・カード 3・issue #333・判断 7〜11 を読む
- [x] 記録の項目（`KeyCategory`・key 行・`ime_state`・`ime_shadow`・`anonymize_ndjson`）を確かめ、確定の Enter が見分けられるかを判定する（design.md §2）
- [x] 未決 2 点と k・N・雑音の大きさを AskUserQuestion で決める（decisions.md 判断 1）
- [x] requirement.md / design.md / decisions.md を書く（換算表を結果の前に固定）
- [x] `experiments/20261009-length-sequence-uniqueness/` の config・SEED・preregistration・env・requirements を書き、結果の前にコミットする（1eac45f7・b734a897）

## 実装
- [x] `scripts/romaji_table.py`（表の写し＋癖）
- [x] `scripts/select_works.py`
- [x] `scripts/fetch_works.py`（1 秒に 1 件・SHA-256）
- [x] `scripts/build_segments.py`（前処理・かな化・B0〜B3）
- [x] `scripts/uniqueness.py`（指標 1）
- [x] `scripts/matching.py`（指標 2）
- [x] `scripts/selftest.py`（採点・正解の選ばれ方・換算・BS の較正・前処理）
- [x] `scripts/summarize.py`・`run.sh`

## 実行
- [x] 自己検査が通る（59 件・変異 6 種をすべて捉えた）
- [x] 作品の取得（1,500 ＋ 参照 12）と manifest
- [x] 前処理（無効の割合・ルビの食い違いの割合・r̄ を記録）（r̄ = 1.8868・B0 の有効 97.4%）
- [x] 指標 1・指標 2・診断（84 セルすべて計算できた）
- [x] 2 回目の実行で結果が同じ（再現）（並列 4 と 2 で results の 6 ファイル・派生データ 8 ファイルがバイト単位で同じ）

## 記録
- [x] `notes.md`（結果と限界）・`data.md`・`env.md`
- [x] ADR-039 D6 に日付つきの注（README の索引にも 1 文）・references.md の [P269] に使用箇所
- [x] issue #333 にコメント
- [x] 引き継ぎファイルに完了の印

## 完了時のレビュー
- [x] 1 巡目（code-reviewer ∥ security-checker ∥ Codex 2 回）の指摘を一次で確かめ、実装の誤りを直して全体を回し直した（decisions.md 判断 5・design.md §14・notes.md の逸脱）
- [x] 2 巡目（直した規則の境界条件）（判断 6・回し直して出力がバイト単位で同じ）

## 完了
- [x] `/finish-task`（code-reviewer ∥ `/cross-review`・2 巡）
- [x] commit → push → PR #337
- [ ] CI 緑なら merge → main の CI 確認（2026-10-09 20:22 時点: `frontend-check` は緑。`decide-win-runner` が self-hosted の Mac（`macbook-air-m-arm64`）で走るため、Mac が offline のあいだ `queued` のまま止まり、`check` が始まらない。merge は止めた。Mac が online になれば続きが流れる）
