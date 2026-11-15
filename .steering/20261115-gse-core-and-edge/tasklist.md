# タスクリスト

## 場面ごとの道具（完了前に照合する）
- 棚卸し（複数ファイル横断の読み） → サブエージェント（Opus・初案を渡さない）
- 設計判断（一言の選択） → /reimagine ＋ codex-consult（集計値と案だけ・既知の未決を添える）
- 引用 → citation-ssot ／ 事実の断定 → verify-before-claiming
- 外へ出す素材 → attack-me（Codex を加える）
- 決めること → AskUserQuestion（日本語・1 件 1 問・推奨と理由）
- 完了 → /cross-review

## 準備
- [x] 引き継ぎ・research-positioning・review-response を読む
- [x] grill（判断 1〜3）・研究者の追加の指示（判断 4）
- [x] 今の研究の資産の客観的な棚卸し（サブエージェント）→ design.md §1
- [x] 棚卸しの数字を一次（notes.md）で裏取り

## 設計
- [x] 一言の候補 3〜5 つを、棚卸しの強い資産から組む（根拠の ADR・実験つき）
- [x] /reimagine で別案を独立に出して比べる
- [x] codex-consult
- [x] AI を背景に置くかを研究者に聞き直す（判断 4）
- [x] 採否を研究者が決める

## 文書
- [x] 新しい ADR（位置づけが変わる場合）
- [x] research-positioning.md の改訂（旧版を docs/history/ へ・ADR-053 の作法）
- [x] 禁止用語の grep
- [x] review-response-2026.md の「核」「尖り」の行
- [x] 未踏向けの派生の素材（docs/mitou_submission/）
- [x] attack-me（Codex を加える）: round 1〜3 とも major。研究者の判断で round 3 の後に直して閉じた（判断 11）
- [x] 文献のラウンド S-3C（判断 10・研究者の選択）

## スライド（最後の段）
- [x] 位置づけが変わった所だけ反映（表紙・4・9・11・17・19 枚目。4 と 9 は README の一覧の外だが旧い headline と言い過ぎを含んでいた）
- [x] validate.py --original tpl.pptx・Keynote の PDF で全枚を見る

## 完了処理
- [ ] /cross-review
- [ ] design.md・decisions.md の最終化
- [ ] git commit（push・PR は研究者に確かめる）
