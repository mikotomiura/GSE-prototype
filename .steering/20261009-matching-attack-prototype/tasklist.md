# タスクリスト

## 準備
- [x] 引き継ぎ・前のタスクの notes/design/decisions・ADR-039 D6・IME 論文の e2・事前登録 §6.8・FORMATS.md・issue #333 を読む
- [x] 入力の所在と SHA-256 を確かめる（Windows のセル・語句コーパス・手順・設定）
- [x] AskUserQuestion で未決 5 点と /reimagine を聞く（判断 1）
- [x] requirement.md・design.md・decisions.md を書く

## 結果の前の固定
- [ ] `experiments/20261009-matching-attack-prototype/` に README・config.json・SEED・data.md・env.md・requirements.txt・preregistration.md・run.sh を書く
- [ ] 固定をコミットする（本計算の前）

## 実装
- [ ] scripts/kitload.py（SHA-256 を照らして読み込む）
- [ ] scripts/prepare.py（記録の割り当て・試行ごとの値）
- [ ] scripts/crosscheck.py（照らし合わせ）
- [ ] scripts/distances.py（S の試行ごとの距離）
- [ ] scripts/reproduce_ime.py（k = 1 の再現の確認）
- [ ] scripts/matching.py（441 セルと診断）
- [ ] scripts/summarize.py（表）
- [ ] scripts/selftest.py（自己検査）

## 計算
- [ ] 自己検査が通る
- [ ] 照らし合わせ → 再現の確認 → 本計算（研究者に一言伝えてから）
- [ ] 2 回目の実行で出力がバイト単位で同じことを確かめる

## 記録
- [ ] notes.md（結果・限界・逸脱）
- [ ] ADR-039 D6 に日付つきの注
- [ ] issue #333 にコメント
- [ ] 引き継ぎに完了の印

## 完了処理（/finish-task）
- [ ] code-reviewer と /cross-review（1 巡目 = 全体）
- [ ] 直した差分の 2 巡目
- [ ] commit → push → PR → CI 緑なら merge → main の CI 確認
