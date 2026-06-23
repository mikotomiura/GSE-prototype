# 設計判断 (debug-force-wall)

## D1: decision polling 経路を再利用 (新 wall 起動経路を作らない)
- `force_wall` は `FORCE_WALL` フラグを立て、main の `get_intervention_decision` が swap で消費して
  action=wall を返すだけ。App→isWallActive→Overlay→wall_server の既存フローに乗る。両ウィンドウは
  既存 polling (overlay は last_decision) で同期。新規 IPC/窓を増やさず最小変更。

## D2: code-reviewer HIGH — force_wall_decision の current_action 副作用を除去
- 当初 force_wall_decision は `current_action=Wall` を設定していた。これは `wall_active` 分岐が
  どのみち設定するため**冗長**で、cooldown 抑制ロジック (`if current_action != Wall`) と暗黙に絡む。
- 対応: **current_action を触らない**。last_decision のみ更新 (overlay 用)。App が isWallActive にすると
  wall_active 分岐が current_action を管理し、解除後の通常 decide が candidate に戻す。force 専用の
  状態変更ゼロ = cooldown/cap を完全非汚染。単体テストで「force→通常 decide 2回→実 wall 発火」を担保。

## D3: force は INTERVENTION_ENABLED より前で発火 (意図的バイパス・MEDIUM 対応)
- 介入無効宣言中でも Wall を検証したいため、force 分岐を INTERVENTION_ENABLED チェックより前に置く。
  これは Task C「宣言と実挙動の乖離解消」を**意図的にバイパス**する debug 動作。コードコメントに明記。
  強制 wall は reason="debug_force" でログされ解析時に除外可能 (宣言乖離の混入を後段で識別できる)。

## D4 (改訂): デバッグボタンの gate は `import.meta.env.DEV` (cross-review HIGH-B 対応)
- cross-review 両者が「UI gate だけでは DevTools/誤操作で pilot に混入しうる」と HIGH 指摘。
- **当初の calibrationMode gate を撤回し `import.meta.env.DEV` に変更**: release/pilot バンドルから
  ボタン自体が完全除去され、被験者セッションへの混入リスクをゼロにする (研究機器として正しい姿勢)。
- ユーザーは検証を `tauri dev` で行う前提 (session NDJSON は dev/release 同一パスに出る)。
  万一 release build で検証が必要なら gate を緩める (follow-up・要連絡)。
- backend `force_wall` コマンド自体は残るが UI から到達不可 (release)。完全ローカル+CSP ロックのため
  DevTools 経由の悪用は被験者の現実的操作ではない。強制 wall は reason="debug_force" で常に除外可能。

## D6: cross-review HIGH-A — wall_active 分岐で last_tick_ms を進める (既存バグ修正)
- `decide` の `wall_active` 分岐は早期 return し `update_wall_accumulation` を通らないため last_tick_ms が
  Wall 表示中ずっと凍結。Wall 解除後の次 tick で elapsed=(Wall 全期間) となり、p_stuck≥0.70 なら
  wall_accum が一気に閾値超え → **即時再発火**しうる (通常 Wall にも潜在、force_wall で顕在化)。
- 対応: wall_active 分岐内で `self.last_tick_ms = Some(input.now_ms)` を更新。回帰テスト
  `wall_active_advances_last_tick_no_accum_blowup_on_dismiss` を追加。

## D7: 据え置いた指摘
- MEDIUM-F (window_label!="main" ガード): 現状 main/overlay の 2 窓のみで、force は overlay 早期 return
  後=main のみ到達するため不要。将来 3 窓目追加時に再検討。
- MEDIUM-C (opportunity_reason と score の不整合): opportunity_reason は #[serde(skip)] の in-memory 専用で
  NDJSON/schema に出ない。forced 用 variant は無く真の標識は reason="debug_force"。placeholder とコメント明記で対応。

## D5: HMM / schema / replay 不変
- engine/features 不変 → `--snapshot` byte-equal・`HMM_VERSION` 不変。
- reason="debug_force" は既存 String 型 → schema 不変・emit_schema parity 不要。
- force_wall は replay 経路外 → ゴールデン不変。FORCE_WALL 既定 false → 通常挙動完全同一。
