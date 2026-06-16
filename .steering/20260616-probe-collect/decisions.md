# decisions.md — Task C「frontend 収集」

## DC-1 回答カードは Overlay に mount(2026-06-16 ユーザー承認)
- **判断**: ProbeCard を既存 Overlay(always-on-top 透過)に置き、card 表示中のみ
  `setIgnoreCursorEvents(false)` で操作可能にする。専用ウィンドウ/main は採らない。
- **根拠**: Overlay は最上位の割込面で他アプリ作業中も見える。専用窓は Windows の
  WebviewWindowBuilder デッドロック制約と生成コスト。main は作業中に見ないため見逃す。
  §1.3 中断最小化・原則5(モデル非表示)と整合。

## DC-2 start 画面で session_meta 宣言 + ビネット導線(2026-06-16 承認)
- **判断**: start 画面に task_kind セレクタ + track/monk/intervention を置き、開始時に
  `record_session_meta`。ビネットは start 画面の「尺度理解テスト」エントリから 8 問(再実行可)。
  PreReg-1 ゲートはソフト(結果表示のみ・本番を強制ブロックしない)。
- **根拠**: スモーク段階では明示的・シンプルが適切。初回強制(永続フラグ)は過剰。

## DC-3 #7 受領 ID 再検証は ProbeId::is_valid で単一情報源化
- **判断**: `ProbeId::is_valid(&str)`(長さ16 && 全文字が ALPHABET)を probe_scheduler に追加し、
  realtime_label command で source=random_probe⇒probe_id 必須+is_valid、self_marker⇒None を強制。
- **根拠**: cross-review #7(DB-11)。アルファベットを生成側(ProbeId)と検証側で二重定義しない。
  不正 ID は command が Err 返却(本文/タイトル由来文字列の混入を境界で遮断・data-privacy)。

## DC-4 VignetteResponse は clamp 構築子を追加(cross-review Codex#1)
- **判断**: `LogEntry::vignette_response(ts, vignette_id, expected_quadrant, q1, q2)` を logger に追加し
  q1/q2 を `1..=5` clamp。直構築でなく構築子経由で producer 強制。
- **根拠**: VignetteResponse は直構築だと clamp されず(format の debug_assert は release で無効)。
  realtime_label と同じ producer 強制方針に揃える。schema は不変(構築子追加のみ)。

## DC-6 送信成功後にのみ UI 遷移する(code-reviewer MEDIUM 対応)
- **判断**: ProbeCard の回答/skip・VignetteTest の次へは `await invoke(...)` 成功後にのみカードを閉じる
  /次へ進む。失敗(例: log channel full)時はカードを残し再送可能にする。
- **根拠**: 先に `setProbe(null)` すると channel full 等で較正データが**静かに失われ MNAR バイアス**に
  直結する(回答率が研究の主指標 PreReg-2)。較正系では欠損の不可視化が最も避けるべき。

## DC-7 Wall とプローブカードを共存させない(code-reviewer HIGH の構造的クローズ)
- **判断**: Overlay で `{!isWallActive && <ProbeCard/>}` とし、Wall 発動時は probeActive をリセット。
- **根拠**: cursor 制御式 `!(isWallActive || probeActive)` は元々正しい(Wall が OR 支配項で、プローブ
  消滅が Wall ブロックを解除しない)ため**実バグではない**が、介入中のプローブは自然作業のサンプリングで
  なく UI も衝突するため、構造的に共存させないのが堅い。較正スモークは介入オフ(D-14)のため実害は元々小。
- **取りこぼし可視化**: 回答中に新規 probe_triggered(self_marker 等)が来た場合は `console.warn`。

## DC-8 受容(根拠付き・cross-review)
- **window_start/end の整合チェックなし**: frontend は B が emit した値をエコーバックするだけで、
  backend 権威記録 `probe_assignment` と突合すれば監査検出可能(security も「数値のみ・漏洩なし」と評価)。
  reject は入れない(正常 frontend は常に start≤end)。
- **session_meta 失敗は best-effort**: logger hiccup でセッション開始をブロックするのは過剰。失敗は log のみ。
- **latency 基点が setProbe 時刻**: render 遅延(~1 frame)が乗るが latency 中央値 ≤10s 目標に対し無視可能。
- **security-checker**: CRITICAL/HIGH/MEDIUM なし。三重防御(型 + 境界再検証 + 出力エスケープ)で
  本文/タイトル/Unicode が NDJSON に到達する経路なしを確認。

## DC-9 Codex cross-review 対応(Task C)
- **二重送信防止(Codex#1)**: ProbeCard / VignetteTest に `submitting` フラグを足し、送信中はボタン
  disable + 早期 return。await-before-clear(DC-6)で表示が残る間の連打による重複記録を防ぐ。
- **window 整合(Codex#2 + code-reviewer 両者)**: `record_realtime_answer/skip` で
  `window_end_ms < window_start_ms` を Err 返却。q1/q2 は構築子 clamp 済(範囲は維持)。
- **intervention_enabled の実挙動配線(Codex#3)**: 宣言だけで挙動に効かない乖離を解消。
  `static INTERVENTION_ENABLED`(record_session_meta が設定)を `get_intervention_decision` が参照し、
  無効時は policy を進めず `safe_default`(none)を返す。main が last_decision を更新しないため
  overlay も none を表示 = **両ウィンドウ単一情報源で抑止**。較正中の介入混入を実際に止められる。
- **command 検証テスト(Codex#6)**: `build_probe_ref`(random/self_marker/不正 source/不正 id)と
  `is_valid_opaque_id` の単体テストを lib.rs に追加(Tauri 非依存)。
- **受容**: ビネット matches/done の state race は React batching で整合(Codex#4・誤検知寄り)。
  error の `{:?}` echo は console/Tauri error のみで NDJSON 非到達(Codex#5・security clean 済)。
  React 受信/UI のテストはテスト基盤未導入につき Task E 手動スモークで担保。

## DC-5 schema_dto.rs / current.json は touch しない
- **判断**: session_meta/realtime_label/vignette_response は Task A で確定済。C は producer 配線のみ。
- **根拠**: finish-task の tier-3 parity guard を回避(DB-5 と同方針)。
