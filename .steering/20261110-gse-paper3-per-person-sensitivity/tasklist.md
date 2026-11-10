# タスクリスト

## 準備
- [x] 引き継ぎ・round 2 の verdict・外枠・tau-extend の条件とコードを読む
- [x] requirement.md
- [x] design.md（v1 → /reimagine → ハイブリッド）
- [x] conditions.md と SEED（コードより前にコミット）

## 実装
- [ ] scripts/synth.py（真の母数・λ の較正・単位の生成）
- [ ] scripts/run_synth.py（複製ごとに手順を当てて集計）
- [ ] scripts/selftest.py（V1 の対照）・check_mutations.py・mutate.sh
- [ ] scripts/report.py（読みの形の機械の当て・tables.md）
- [ ] run.sh（selftest → 変異 → 時間の見積もり → 本計算 → report）
- [ ] code-reviewer（本計算の前）

## 本計算
- [ ] selftest と変異が通る
- [ ] 時間の見積もりと D6 の削り
- [ ] 本計算

## まとめ
- [ ] notes.md（読みの形に当てた結論）
- [ ] 外枠の S15・4.3・限界・open items・Status の行
- [ ] code-reviewer と /cross-review（Codex を含む）

## attack-me round 3
- [ ] Step 0〜5（Codex を 5 本の後に直列・既知の未決の一覧を添える）
- [ ] verdict.md・推移を見て次を研究者に聞く

## 照合の表（場面 → 使う道具）
- コード → code-reviewer（本計算の前）・/cross-review（完了前）
- 外枠の直し → code-reviewer と /cross-review
- 事前登録に当たる条件 → コードより前にコミット（済み）
- 論文のプレ査読 → attack-me（Codex を加える）
