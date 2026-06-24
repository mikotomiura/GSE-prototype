# タスクリスト

## #1 プローブ/Nudge カード無反応・出っぱなし（最優先・バグ）
- [x] 根本原因の静的調査（共通失敗点 = log channel try_send / フロント失敗時保持）
- [x] 層1: Overlay.tsx Nudge — handleNudgeDismiss await 化・無限再表示ループ廃止・エラー表示
- [x] 層1: Overlay.tsx silent timeout 経路も同様に修正
- [x] 層1: ProbeCard.tsx — error state + インラインエラー/リトライ
- [x] 層1: App.css — nudge-card-error / disabled スタイル
- [x] tsc --noEmit パス
- [ ] **(ユーザー) 実機 repro → devtools console.error 文字列を共有**（full / disconnected 判別）
- [ ] 層2: backend 根本修正（logger.rs consumer 耐障害 or lib.rs try_send 文言分岐）+ 回帰テスト
- [ ] 層1 実機手動確認（ボタンで確実に閉じる / 失敗継続時エラー表示 / 無限再表示なし）

## #2 第2週ダッシュボードの 3 状態表示（測定整合）
- [x] 方針 A をユーザー確定（両週ブラインド・DEV gate）
- [x] Dashboard.tsx 実装（showModelOutput = !calibrationMode && import.meta.env.DEV）
- [x] tsc パス
- [ ] 実機確認（第2週でモデル出力非表示・DEV ビルドで従来表示）

## #3 自作 TSE 5 件法 → 4 件法（プレレジ変更）
- [x] 件法・採点法・スコープ・アンカーをユーザー確定（TSE のみ・強度型・F3 不変）
- [x] GAS TSE_ITEMS 4 件法化（setBounds/labels/anchor を単一定数化し byte 一致保証）
- [x] preregistration-tse-scale.md §2/§3 を 4 件法・5−x・範囲 1.0–4.0 へ同期
- [x] decisions FD10 記録 + FD9 に supersede 注記
- [x] 設問草案.md F2-C 同期
- [x] node --check（GAS 構文 OK）

## 完了処理（全体）
- [ ] code-reviewer + security-checker（logger.rs 変更時必須）
- [ ] /finish-task で /cross-review（無関係な未ステージ変更を混ぜない）
- [ ] git コミット（issue ごとに論理単位分割・Refs 付与）
