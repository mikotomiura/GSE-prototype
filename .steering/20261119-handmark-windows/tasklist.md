# タスクリスト

## 準備
- [x] grill（判断 1〜6）
- [x] 材料を読む: 枝 `docs/tangibility-design` の handoff 4 本・ADR-050・ADR-051・Mac 版の `handmark_stage.rs`・`handmark_edge_strip.rs`・`handmark_pointer_thread.rs`・`handmark_guard.rs`・`wallpaper_windows.rs`
- [ ] 必須 Skill: `architecture-rules`・`rust-standards`・`hook-constraints`・`data-privacy`・`typescript-standards`

## 確かめ（使い捨ての試作・main に入れない）
- [x] 確かめの design（試作の置き場・測り方・陽性対照）を design.md に書く
- [x] 条件 (a): `GetCursorPos`・`GetAsyncKeyState(VK_LBUTTON)` を権限なしで読む（研究者の手のクリックで陽性対照）
- [x] 背景の層の候補 1: WorkerW（W・WL）
- [x] 背景の層の候補 2: 最前面でクリックを通す透過の窓
- [x] 背景の層の候補 3: `IDesktopWallpaper`（成り立ちは EH3 で既知・測らず）
- [x] 候補 B（B1・B2）と両方の良い所を取る B3〜B5（判断 9）
- [x] 候補ごとに: 成り立ち・画面共有に写るか・CPU
- [x] 帯（多画面は画面 1 枚で未確認）: タスクバーの上・全画面・自動で隠す設定・多画面
- [x] results.md にまとめる（OS の版を明記）

## 停止点
- [x] 結果と推奨を研究者に出し、背景の層の候補を選んでもらう（decisions.md に記録）

## 本番の実装
- [x] design.md（本番の形）→ /reimagine
- [x] `input/handmark_pointer_windows.rs`
- [x] 背景の層の Windows の実装
- [x] 帯の Windows の実装（従）
- [x] `lib.rs` の配線（`run_handmark_effects`・ポインタのスレッド）
- [x] ADR-050 D3 の境界の検査を Windows へ広げる（仮想キーの検査を含む・陽性対照）
- [x] 両 OS に対のテスト

## 確認
- [x] cargo test・clippy・tsc（手元）
- [x] 研究者が実機で手跡を目で確かめる

## レビュー
- [ ] code-reviewer + security-checker（並列）
- [ ] /cross-review（2 巡）

## ドキュメント
- [x] ADR-050 補訂（条件 (a)・アイコンの矩形と画素の読み＝判断 10）
- [x] ADR-051 D1 補訂
- [ ] 引き継ぎ（`next-session-gse-handmark-windows.md`）を使用済みにする

## 完了処理
- [ ] /finish-task（push → PR → CI 緑 → merge → main の CI）
