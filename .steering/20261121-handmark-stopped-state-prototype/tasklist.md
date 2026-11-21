# タスクリスト

## 準備
- [x] 始める条件（回 1 が終わった・研究者が始めると決めた・判断 1）
- [x] ADR-056・設計案 §0.1・§4.4 を読む
- [x] 分かれ目を研究者に確かめる（判断 2〜5）
- [ ] 設計案の判断 6〜10・S-SN・ADR-051 D3/D5/D7 を読む
- [ ] 実装を読む: `state.rs`・`trace.rs`・`desk.rs`・窓の側（`HandmarkStage.tsx`・`HandmarkEdgeStrip.tsx`）
- [ ] architecture-rules・rust-standards・typescript-standards を読む
- [ ] 影響範囲を調べる（`StageState` の serde・再生・机上の道具）

## 設計
- [ ] design.md（状態の足し方・生成器・研究者用の切り替え・テスト戦略）
- [ ] 研究者の承認 → /reimagine

## 実装
- [ ] v と移り変わりの始まりの時刻（`state.rs`）
- [ ] 境界の状態（起動・戻し・一時停止の間・一時停止明け）
- [ ] 自律の動きの純関数（日の種・格子の時刻・有限の窓）
- [ ] 窓の側の 3 つの形と研究者用の切り替え（既定は切）

## テスト
- [ ] 単体テスト（requirement の受け入れ条件 1〜6）
- [ ] 机上の道具: 経過が読めない (i)〜(iii)
- [ ] 机上の道具: 漏れの検査（ADR-051 D3）
- [ ] 今ある基層（`drift`）の扱いを (iii) の結果で研究者に確かめる
- [ ] cargo test・clippy・tsc が緑

## レビュー
- [ ] code-reviewer ＋ security-checker（並列）
- [ ] /cross-review 2 巡

## 完了処理
- [ ] 次のタスク（研究者自身の試し・値の確定）の引き継ぎ
- [ ] /finish-task
