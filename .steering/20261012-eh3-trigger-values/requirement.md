# EH3 の招待の契機の値（試作の段）

引き継ぎ: `.steering/_handoff/next-session-eh3-trigger-values.md`（2026-10-12・Surface）。

## 背景

- EH3 の招待は `p_stuck ≥ 0.60` が 30 秒続いたときに出る（`src-tauri/src/analysis/invitation.rs` の `TRIGGER_P_STUCK`・`TRIGGER_HOLD_MS`。稿 `experiments/20261011-portrait-eh3/preregistration-draft.md` §10.1 の F-2）。研究者は `.steering/20261011-portrait-eh3-after-impl/decisions.md` 判断 1 #3 でこの値を認めた。
- 同じ decisions.md の判断 3（Windows の実機・2026-10-12）では、意図した打ち方でこの契機を作れなかった。`p_stuck ≥ 0.6` の継続は最長 16 秒で、手を止めると 0.54 で頭打ち、速く打ち直し続けると 0.01 まで下がった。実際の使い方でも招待がほとんど出ないと、PC-12・M-2〜M-4 が測れない。
- 判断 4 で研究者は「試作と利用者の検証の段では出やすい側に調整し、記録を見て詰める」方向を決めた。具体の値と、段の値の切り替え方は未決。

## ゴール

1. 試作の段の契機の値を、手元の記録から数えた根拠とともに研究者に示し、研究者に決めてもらう。
2. 段の値を切り替える方法を研究者に決めてもらい、実装する。
3. 稿 F-2 に「試作の段の値」と「本番の値（凍結の前に決める）」を分けて書く。

## スコープ

### 含むもの
- 記録から契機に届く回数を数える道具（`invitation.rs` の判定をそのまま使う）と、その結果
- 招待の状態機械の契機の値を段で切り替えられるようにする実装とテスト
- 稿 §10.1 F-2・判断の記録・前タスクの tasklist への書き添え

### 含まないもの
- 本番の値の凍結、ADR-035 の Accepted、F-1・F-3・F-6
- Windows の実機の残り（招待の図像・失効・スリープ・再起動・複数モニタ）
- `metrics.rs` の `p_stuck_trigger: 0.60`（Stuck エピソードの定義・事前登録済みの指標）。変えない

## 受け入れ条件

- [ ] 研究者が試作の段の値と切り替え方を決め、decisions.md に逐語とともに残っている
- [ ] 契機の値の境界（閾値ちょうど・継続ちょうど）のテストがあり、変異を入れると落ちる
- [ ] 本番の値（既定）の挙動が変わらないことをテストで確かめている
- [ ] 稿 F-2 が試作の値と本番の値を分けて書き、metrics 側の 0.60 と別の値になりうることを明記している
- [ ] `cargo test --lib`・clippy `-D warnings` が緑、code-reviewer ∥ security-checker と /cross-review 2 巡を通している

## 関連ドキュメント

- `.steering/20261011-portrait-eh3-after-impl/decisions.md` 判断 1・3・4
- `docs/adr/ADR-035-invitation-choice-principles.md`
- `experiments/20261011-portrait-eh3/preregistration-draft.md` §10.1

## 運用メモ
- /reimagine 適用: No
- 理由: 値の調整と段の切り替えの小さな実装で、設計の分岐は研究者への問い（値・切り替え方）で閉じる。grill は引き継ぎが背景・ゴール・範囲外を確定しているので省いた。
