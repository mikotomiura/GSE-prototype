# タスクリスト

## 準備
- [x] 引き継ぎ・ADR-039 D5/D6・カード 3・issue #333・判断 7〜11 を読む
- [x] 記録の項目（`KeyCategory`・key 行・`ime_state`・`ime_shadow`・`anonymize_ndjson`）を確かめ、確定の Enter が見分けられるかを判定する（design.md §2）
- [x] 未決 2 点と k・N・雑音の大きさを AskUserQuestion で決める（decisions.md 判断 1）
- [x] requirement.md / design.md / decisions.md を書く（換算表を結果の前に固定）
- [ ] `experiments/20261009-length-sequence-uniqueness/` の config・SEED・preregistration・env・requirements を書き、結果の前にコミットする

## 実装
- [ ] `scripts/romaji_table.py`（表の写し＋癖）
- [ ] `scripts/select_works.py`
- [ ] `scripts/fetch_works.py`（1 秒に 1 件・SHA-256）
- [ ] `scripts/build_segments.py`（前処理・かな化・B0〜B3）
- [ ] `scripts/uniqueness.py`（指標 1）
- [ ] `scripts/matching.py`（指標 2）
- [ ] `scripts/selftest.py`（採点・正解の選ばれ方・換算・BS の較正・前処理）
- [ ] `scripts/summarize.py`・`run.sh`

## 実行
- [ ] 自己検査が通る
- [ ] 作品の取得（1,500 ＋ 参照 12）と manifest
- [ ] 前処理（無効の割合・ルビの食い違いの割合・r̄ を記録）
- [ ] 指標 1・指標 2・診断
- [ ] 2 回目の実行で結果が同じ（再現）

## 記録
- [ ] `notes.md`（結果と限界）・`data.md`・`env.md`
- [ ] ADR-039 D6 に日付つきの注
- [ ] issue #333 にコメント
- [ ] 引き継ぎファイルに完了の印

## 完了
- [ ] `/finish-task`（code-reviewer ∥ `/cross-review`）
- [ ] commit → push → PR → CI 緑なら merge → main の CI 確認
