# タスクリスト —— 手跡の PR 2（帯と見えていた時間）

## 準備
- [x] worktree `/Users/johnd/GSE-prototype-handmark-pr2`（枝 `feature/handmark-pr2-edge-strip`・origin/main d2d3cad8 から）
- [x] 空きを戻す（判断 4・10 GiB）
- [x] requirement・判断 1〜3・design・承認（判断 5）

## 実装 A（Sonnet・Rust の純粋な部分）
- [x] `day.rs` の `visible_ms` の累計（`serde(default)`）・`add_visible`
- [x] 駆動役の `on_strip_visible`・刻みの `add_visible`
- [x] 行の `visible_ms`・schema の説明の文・`emit_schema`
- [x] `strip_near` と `PointerOut::StripNear`
- [x] テスト（design のテスト戦略の Rust の分）
- [x] 私が走らせ直す（fmt・clippy・test）・変異

## 実装 B（Sonnet・窓・配線・tsx・検査）
- [x] `handmark_edge_strip.rs`（窓・NSPanel・見張り・置き場・`STRIP_VISIBLE`）
- [x] `lib.rs` の配線（setup・開け閉め・状態の配り・近さ・`on_strip_visible`）
- [x] tsx・`handmarkEdgeStrip.ts`・main.tsx・capabilities
- [x] node のテスト・検査の拡張（陽性対照つき）
- [x] 私が走らせ直す（fmt・clippy・test・tsc・node・emit_schema）・変異

## 確かめ
- [x] 区切りの点検（code-reviewer・security-checker）（判断 8・直しは判断 9）
- [ ] 画面の確かめ（研究者が gse-next を止めた時間に・一時の HOME）
- [ ] CPU（累積の秒の差・帯の有無）
- [ ] 完了時のレビュー（code-reviewer・security-checker・/cross-review に Codex）
- [ ] gse-dataset の同期（schema の文が変わったら）
- [ ] push の前に `target` を消す（空き 8 GiB）・push と PR は研究者に確かめる

## 場面ごとの対応
| 場面 | 使うもの |
|---|---|
| Rust を書く | rust-standards・architecture-rules・hook-constraints（Atomic）・data-privacy（logger・schema） |
| TS を書く | typescript-standards |
| 実装を渡す | subagent-delegation（model を明示・範囲と禁止事項） |
| 区切りの点検 | code-reviewer＋security-checker を並列 |
| 完了 | /cross-review（Codex を加える）・/finish-task |
