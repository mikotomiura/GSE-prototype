# タスクリスト

## 準備
- [x] 引き継ぎ・前のタスクの notes/design/decisions・ADR-039 D6・IME 論文の e2・事前登録 §6.8・FORMATS.md・issue #333 を読む
- [x] 入力の所在と SHA-256 を確かめる（Windows のセル・語句コーパス・手順・設定）
- [x] AskUserQuestion で未決 5 点と /reimagine を聞く（判断 1）
- [x] requirement.md・design.md・decisions.md を書く

## 結果の前の固定
- [x] `experiments/20261009-matching-attack-prototype/` に README・config.json・SEED・data.md・env.md・requirements.txt・preregistration.md を書く
- [x] 固定をコミットする（本計算の前・`19f16862`）

## 実装
- [x] scripts/kitload.py（SHA-256 を照らして読み込む）・data.py（攻撃の入力の読み込み）
- [x] scripts/prepare.py（記録の割り当て・試行ごとの値）
- [x] scripts/crosscheck.py（照らし合わせ）
- [x] scripts/distances.py（S の試行ごとの距離）
- [x] scripts/reproduce_ime.py（k = 1 の再現の確認）
- [x] scripts/matching.py（441 セルと診断）
- [x] scripts/summarize.py（表）・run.sh
- [x] scripts/selftest.py（自己検査 75 件・変異 13 種がすべて落ちることを確かめた）
- [x] コードをコミットする（本計算の前・`52f9c0da`・`c73fc37e`）

## 計算
- [x] 自己検査が通る
- [x] 照らし合わせ → 再現の確認（6 つとも公開値と一致）
- [x] 本計算（研究者に一言伝えてから・2026-10-09 に会話で伝えた）
- [x] 2 回目の実行で出力がバイト単位で同じことを確かめる（並列 4 と 2・19 ファイル）
- [x] 事後の探索（判断 4）

## 記録
- [x] notes.md（結果・限界・逸脱）
- [x] ADR-039 D6 に日付つきの注
- [ ] issue #333 にコメント（レビューの後）
- [x] 引き継ぎに完了の印

## 完了処理（/finish-task）
- [x] code-reviewer ∥ security-checker ∥ Codex 2 回（1 巡目 = 全体・判断 6）→ 直して回し直した
- [x] 直した差分の 2 巡目（code-reviewer ∥ Codex 1 回・判断 7）→ 直して回し直した
- [ ] commit → push → PR → CI 緑なら merge → main の CI 確認
