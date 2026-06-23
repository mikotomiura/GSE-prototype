# 設計判断 (gentle-intervention-ui)

## D1: HCI 査読研究を根拠に方向性を確定 (ユーザー承認)
- 調査レポート (本タスク会話) より: breakpoint 割り込み (Bailey&Konstan 2006)、IRC で Nudge=低I低R高C
  (McCrickard 2003)、急 onset 回避=ゆっくりフェード (Yantis&Jonides 1990)、強制はリアクタンス (Lyngs)、
  ESM 単一低負荷 (van Berkel)。Wall=段階的減光、self-marker=ワンタップ をユーザーが選択。

## D2: Nudge は live action から切り離し boolean 保持 (勝手に消えるバグ修正)
- `nudgeOpacity:number`(live action 直結) → `nudgeVisible:boolean`。一度表示したら応答 (dismiss) か
  60s タイムアウト (silent 記録) まで保持。p_stuck 振動で action が変わっても消さない。
- 再表示: dismiss/silent は record_intervention_dismiss → backend record_dismiss が current_action リセット
  + recent_dismiss → action が nudge を離れる → frontend が dismissed 解除 → 次 nudge (cooldown 後) 再表示可。
  永久ロックなし (code-reviewer HIGH-2 は backend 挙動で担保。コメント明記)。

## D3: 非ブロック化は既存 box-mode を nudge にも再利用 (低リスク)
- PR #21 の probeOnly box (右上・窓縮小・クリック透過) を `widgetOnly=(probe||nudge)&&!wall` に拡張。
  nudge も右上 box 内に表示し非ブロック化。新規 window や cursor-forwarding は作らず回帰リスク最小。
- 注: nudge は box(右上)内表示のため画面右上に出る (スクショの右下指定とは別)。bottom-right 化は
  corner 選択ロジックが要るため follow-up (今回は top-right 再利用で低リスク優先)。

## D4: Wall は CSS でゆっくり減光フェードイン (今回は減光のみ)
- `wall-layer` に `wall-dim-in` (opacity 0→1, 3.5s ease-out)。即時不透明占有を緩やかな onset に。
  QR/早期解除/接続バッジは維持。breakpoint 検出ベースの完全な段階エスカレーション (ambient→subtle→強)
  は backend timing が要るため次段 follow-up。

## D5: 自己ラベルはワンタップ (既存 self_marker 概念を再利用)
- 既存: M ホットキー→カード式 self_marker (q1/q2 入力)。本タスクは **ワンタップ** を追加。
- `record_self_marker_inner(now, tx)` に集約 (code-reviewer HIGH-1 対応): ボタン (record_self_marker
  コマンド) と D ホットキー (Ctrl+Shift+Alt+D) が共通で呼び **LAST_SELF_MARKER_MS デバウンスを共有**
  (M とも共有)。送信失敗は tracing::warn (security MEDIUM 対応)。時刻は epoch_ms に統一 (MEDIUM)。
- 記録 = realtime_label source=self_marker, q1=5/q2=1 (Stuck 象限), 窓=self_marker_window_clamped。
  固定カテゴリ+時刻+窓のみ・本文なし (data-privacy 適合・security CRITICAL/HIGH なし)。
- 既存 M カード式は据え置き (回帰なし)。

## D7: /cross-review 対応 (Codex は Win sandbox ACL で部分実行・両者一致分を採用)
- **HIGH-C2 (debounce race)**: load+store → `compare_exchange` で原子的に枠予約 (LAST_LABEL_MS と同流儀)。
  ボタン(IPC スレッド) と D/M ホットキーの同時呼びでの二重記録を防止。
- **HIGH-C1 (UI 偽確認)**: record_self_marker を `Result<bool>` に。デバウンスで弾かれたら false →
  Dashboard は true の時だけ「記録しました」表示。
- **HIGH (Wall QR 不可視)**: opacity フェード → **background/backdrop の暗さランプ + forwards** に変更。
  コンテンツ (QR/解除) は最初から見え、解除手段を常時確保。
- **HIGH (IPC 失敗で nudge 永久ブロック)**: dismiss/silent の invoke 失敗時に nudgeDismissed を false に戻し
  再表示→再試行可能に。
- **MEDIUM (probe+nudge 重なり)**: probe 表示中は nudge を出さない (!probeActive)。
- **LOW**: D ホットキーを epoch_ms に統一、ボタンに aria-label。

## D6: 不変条件
- HMM/engine/features 不変 → `--snapshot` byte-equal・`HMM_VERSION` 不変。
- schema 不変 (realtime_label / self_marker / DismissReason::silent はすべて既存)。replay 不変。
- UI 微調整 (timer null クリア・button disabled) は review MEDIUM/LOW 対応。
