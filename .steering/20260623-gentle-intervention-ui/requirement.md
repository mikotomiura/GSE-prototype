# gentle-intervention-ui (穏やかな介入 UI + 自己ラベル)

## 背景

実機セッション (gse_20260623_084152) + ユーザーフィードバック:
- **Nudge がボタンを押す前に勝手に消える** (`Overlay.tsx:233-250`: 表示が live action に直結、
  p_stuck 振動で action が変わると即 nudgeOpacity=0)。
- **Wall が即時・全画面・不透明で占有し驚く / 強すぎる介入**。
- **「今とても詰まっている」を素早く自己ラベルしたい** (現状 M ホットキー→カードはあるが多段)。

HCI 査読研究 (調査済): breakpoint で割り込む (Bailey&Konstan 2006)、IRC で Nudge は低I低R高C・
Wall はアラーム級→アンビエント寄りへ (McCrickard 2003)、急な onset を避けゆっくりフェード
(Yantis&Jonides 1990/Doherty 1982)、強制はリアクタンスで逆効果・逃げ道付き自己制御型 (Lyngs)、
ESM は単一低負荷 (van Berkel)。

## ゴール

介入 UI を「極力強く介入しない」穏やかな形へ:
- Nudge は応答するまで消えず、フォーカスを奪わず、隅で穏やかに。
- Wall は即時全画面占有をやめ、ゆっくり減光で和らげる (QR/早期解除は維持)。
- 「今詰まっている」をワンタップ (ホットキー + ボタン) で self_marker 記録。

## スコープ

### 含むもの
- Nudge: 応答/タイムアウトまで保持 (タイムアウトは silent 記録)、ゆっくりフェード、右下、非ブロック
  (probe と同じ box 化を nudge にも適用)。
- Wall: 全画面の即時不透明をやめ **CSS でゆっくり減光フェードイン** + 落ち着いた配色 (QR/早期解除維持)。
- 自己ラベル: ワンタップ `record_self_marker` コマンド (source=self_marker, 詰まり=q1高/q2低) +
  Dashboard ボタン + グローバルホットキー (Ctrl+Shift+Alt+D)。

### 含まないもの
- Wall の breakpoint 検出ベースの完全な段階エスカレーション・自動減光トリガー (次段。今回は減光フェードのみ)。
- 介入判定ロジック (Wall/Nudge トリガー閾値) の変更。HMM/schema 変更なし。

## 受け入れ条件

- [ ] Nudge が応答するまで消えない・フォーカスを奪わない・右下に穏やかに出る
- [ ] Wall が即時全画面占有でなくゆっくり減光で出る (QR/早期解除維持)
- [ ] 「今詰まっている」ワンタップ (ボタン+ホットキー) で self_marker が NDJSON に残る
- [ ] cargo test --workspace 緑・--snapshot byte-equal (HMM 不変)・tsc+vite build 緑
- [ ] code-reviewer / cross-review CRITICAL/HIGH なし。実機 GUI 確認 (手元)

## 関連ドキュメント
- HCI 調査レポート (本タスク会話) / Skill: intervention-design / typescript-standards / rust-standards / data-privacy
- 既存: 自己マーカー M ホットキー (lib.rs:1262)・F/I/S UserLabel ホットキー (1292)

## 運用メモ
- /reimagine 適用: No (方向性はユーザー承認済み・研究準拠)。別 PR・main 基点。
