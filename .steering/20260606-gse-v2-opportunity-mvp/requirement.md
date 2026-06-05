# GSE v2 Opportunity MVP

## 背景

GSE は脳内の認知状態を直接読むのではなく、PC 操作に現れる行動的シグナルから、介入判断に必要な作業上の状態を推定する方針へ再設計する。

現行実装は `p_stuck` 閾値を Frontend で直接判定し、Nudge / Wall を発火している。このままだと「詰まりらしさ」と「今介入してよいか」が分離されず、介入しすぎや説明困難な判断につながる。

## ゴール

- Need 層は現行 `p_stuck` を中心に維持し、既存挙動との比較可能性を残す。
- Opportunity 層を Rust 側に追加し、`cooldown` / `daily_cap` / `recent_dismiss` / `Monk Mode` / `idle_ms` / `post_burst_pause` を使って介入可否を判定する。
- Frontend は Rust から返る `InterventionDecision` に従って Nudge / Wall を表示する。
- 介入判断を NDJSON に記録し、初期検証で dismiss・過介入・defer を分析できるようにする。
- 本文テキスト、Unicode 文字、ウィンドウタイトルは記録しない。

## スコープ外

- マウス、スクロール、フォーカス、キャレットの OS 取得実装。
- ONNX や学習済みモデルへの移行。
- Nudge dismiss UI の新設。
- 生テキスト、選択文字列、ウィンドウタイトルの取得・保存。

## 受け入れ条件

- `analysis/` に OS API が入らない。
- `InterventionDecision` が `none` / `nudge` / `wall` / `defer` を返せる。
- Wall は現行どおり `p_stuck >= 0.70` の累積 30 秒を基本条件にする。
- Nudge / Wall に cooldown と daily cap が適用される。
- Monk Mode は Wall を抑制する。
- `intervention_decision` ログが schema / replay と整合する。
- TypeScript build と Rust test が通る。

## 運用メモ

- /reimagine 適用: No
- 理由: 事前の文献・設計議論で v2 方向性を承認済み。今回は MVP Opportunity の限定実装として進める。
