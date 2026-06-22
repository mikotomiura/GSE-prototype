# 設計判断 (capture-schema-freeze)

## CD1: external_paste_chars はクリップボード長のみ読む (ユーザー承認 2026-06-23)
- **判断**: ペースト検出時にクリップボードのテキスト長 (文字数=整数) のみ取得し、中身は即破棄。
  NDJSON には `external_paste_chars`(数値)のみ残す。保存・送信は一切しない。
- **根拠**: v0.4 (b)指標 `manual_contribution_ratio = manual_insert_chars/(manual_insert_chars+external_paste_chars)`
  の分母に必須。捕捉しないとパイロットで不可逆に失う。
- **プライバシー姿勢の変更**: 「クリップボード非接触」→「ペースト時に長さのみ読む」。data-privacy
  ルール1(Unicode 文字内容を記録しない)とは整合(長さは内容ではない)。
- **実装制約**: クリップボード読みは**フックコールバック外**(lib.rs main 側、is_paste 処理時)。
  hook-constraints(ブロッキング禁止)に抵触させない。

## CD2: label_pool は SessionMeta にセッション単位で付与 (推奨・承認)
- condition から導出可能だが、X1 判定が `calibration_blind` のみを使うため明示タグが安全。`Option`。

## CD3: dismiss 4択 UI は Nudge のみ実装 (推奨・承認)
- `InterventionResponse` variant は `action`(nudge/wall/..)で汎用化し、Wall の early-unlock/Zen 応答
  配線は別タスク(過剰スコープ回避)。本タスクは Nudge dismiss の 4択を配線する。

## CD4: 全追加フィールドは Option / 新 variant (後方互換)
- 既存 fixture(新フィールド無し)のパース失敗を防ぐ(影響分析 HIGH 指摘)。FeatSnapshot 不変。

## CD5 (改訂): クリップボード読みは**同期**で行う (cross-review HIGH 対応・CD5 撤回)
- **当初 CD5**: code-reviewer MEDIUM (1Hz ループのブロッキング) を避けるため `thread::spawn` で
  クリップボード読みを別スレッドへ逃がした。
- **cross-review (Claude ∥ Codex 両者一致 HIGH) で撤回**: 別スレッド化は次の 3 つを招くと判明:
  - **A1**: ペースト連打で thread が無制限に積まれる (resource exhaustion)。
  - **A2**: 直後に `LogEntry::End` が来ると paste 行が無音で欠落する race。
  - **A3 (TOCTOU)**: 検出〜読取の間にクリップボードが変わり、誤った文字数を記録する窓が広がる。
- **最終判断**: 研究用捕捉は「正確さ > 数 ms のレイテンシ」。**同期読みに戻す**と A1/A2/A3 が全消滅。
  代償は稀なクリップボード競合時の僅かな 1Hz tick 遅延のみ (30s 窓では無視可能)。
- **A3 残存** (同期でも): hook 検出→analysis ループ処理の間 (sub-ms〜数 ms) に高速コピーすると
  external_paste_chars が後続クリップボード値になりうる。通常操作では許容誤差内。`manual_contribution_ratio`
  解析時は「高速コピー→ペースト連打」区間を外れ値として扱う前提を Phase B で明記する。

## CD6: arboard は default-features = false (security LOW 対応)
- `image-data` 既定フィーチャが画像デコーダ (`image` crate 等) を推移依存に引き込む。
  本用途は `get_text()` のみで不要。攻撃面・ビルド時間削減のため無効化。

## CD7: dismiss `silent` は現状 UI から送出しない (既知・将来)
- Nudge の 4択 UI は not_stuck / want_to_struggle / just_close の 3 ボタン。`silent` は
  「理由未選択でフェードアウト」相当のカテゴリとして schema/enum に用意するが、本タスクでは
  自動送出しない (フェード毎の記録はノイズ)。将来 Wall 応答配線や無操作タイムアウト記録で使う。

## CD8: condition/label_pool は calibrationMode の二値から導出 (現フェーズ限定)
- Phase 1b の blind 較正 = `blind_calibration` / `calibration_blind`、それ以外 = `baseline` /
  `post_intervention`。Phase 2/3 の `a`/`b`/`nudge`/`defer` 配線は MRT/AB-BA 実装時 (別タスク)。
  enum 値は先に凍結 (捕捉スキーマの不可逆性)。

## CD9: IPC 固定カテゴリ検証を純粋関数化しテスト (cross-review A5 MEDIUM 対応)
- `parse_optional_condition` / `parse_optional_label_pool` / `parse_dismiss_reason` を lib.rs の
  純粋関数として抽出 (既存 `build_probe_ref` と同流儀) し、未知値→Err / 省略→既定 を単体テスト。
  IPC コマンドはこれらを呼ぶだけにして、Tauri State 無しでバリデーションを検証可能にした。

## CD10: nudgeDismissed の再表示抑制は現状 action 遷移ベース (cross-review A4 MEDIUM・既知制約)
- `nudgeDismissed` は action が nudge→非nudge に変わるとリセット。backend が短時間で none→nudge を
  繰り返すと dismiss 直後に再表示されうる。ただし backend 側に Nudge cooldown (10分) があるため
  パイロット規模では実害は限定的。nudge エピソード ID/タイムスタンプ単位の厳密管理は別タスク。
