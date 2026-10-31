# 設計（タスク B）

## 1 契機を差し替える口（`analysis/invitation.rs`）

- 出す規則（1 区間 1 回・繰り越さない・60 秒で失効・閉じた後 30 分・1 日の上限・時間帯・研究の条件・一時停止）は今の `InvitationMachine::tick` のまま共有する。差し替えるのは「この tick で契機が立ったか」（`triggered`）だけ。
- `TriggerKind`（serde・`deny_unknown_fields`・`tag = "kind"`）:
  - `estimator { p_stuck, hold_ms }`: 今の区間の追跡（`track_episode`）そのもの。`Trigger::MAIN` / `PROTO` はこの値。EH3 はここだけを使う。
  - `rising { delta, window_ms }`（friction_rising）: `p_stuck(now) − p_stuck(now − window_ms) ≥ delta` が偽から真になった tick で立つ。真の間は立ち直さない。値の既定は置かない。
  - `random { per_active_hour, seed }`: 離席候補の外（`idle_ms < AWAY_IDLE_MS`）・区切りでない tick ごとに、確率 `per_active_hour / 3600` で立つ（1 tick = 1 秒の前提・tick の間隔が 1 秒からずれたら経過秒で割合を変える）。乱数は外部 crate を足さずに splitmix64 を本モジュールに置き、seed から再現する。既定値は置かない。
  - `none`: 立たない（統制の「なし」）。
- 将来の候補（止まりの初期・フォーカスの遷移）は合流の後で足す。足しやすいよう、契機の判定は `TriggerKind` ごとの小さな状態（enum の中の構造体）に閉じ、`tick` の本体は `triggered: bool` だけを受ける形にする。
- 推定器の以外の契機での「区間」: `estimator` は今の区間をそのまま使う。`rising` と `random` は立った瞬間を 1 区間とみなし、`episode_used` の繰り越さない規則は「その瞬間に出せなければ出さない」と同じ意味になる。

## 2 研究者の設定ファイル

- `~/.gse/invitation_trigger.json`（EH3 の `eh3.mode` と同じ置き場の作法・本人の画面には出さない）。中身は `TriggerKind` の JSON 1 つ。
- 無い → `estimator` の `MAIN`。読めない・未知の欄・値の欠け・範囲外（負・NaN・`per_active_hour` が 0 以下か 60 超・`delta` が (0, 1] の外・`window_ms` が 0）→ 通常のモードの招待を出さない（applog に警告・内容は書かない）。
- EH3 はこのファイルを読まない（`eh3::TriggerStage` のまま）。

## 3 通常のモードの配線（`lib.rs`・`App.tsx`）

- セッション開始のコマンドに `invitation_enabled: bool` を足す。`App.tsx` の `PHASE_WEEKS`: 第 1 週 false・第 2 週 true。第 2 週の `label` を「第2週 (招待)」、`description` を事実に合わせる（識別子 `week2_intervention` は変えない・タスク A の D3 と同じ）。
- 通常のモードでも `InvitationRunner` を作る（今は `eh3::assignment()` があるときだけ）。研究の条件は「EH3 なら今のまま（`is_eh3() && assigned_today`）／通常のモードなら『セッションの宣言が true かつ O1 でなく G1 でなく、設定ファイルが読めた』」。
- `get_invitation_state` は EH3 か、通常のモードで招待が許されているときに真を返しうる。図像と設定の窓は EH3 と同じもの（`InvitationGlyph.tsx`・`InvitationSettings.tsx`）を使う。本人の設定（`~/.gse/eh3_invitation.json`）は共有する（置き場の名前は変えない・変えると EH3 の本人の設定が消える）。

## 4 記録

- 新しい行 `invitation_condition`: `{ type, t, condition: "estimator"|"rising"|"random"|"none", params..., hmm_version }`。通常のモードで招待を許すセッションの開始時に 1 行（条件が決まった時点）。EH3 は今の `eh3_day` のまま（足さない）。
- 提示は今の `invitation_present` を使う。立ったが出さなかった契機は記録しない（今の規則）。
- `schema_dto.rs`・`emit_schema`・`schema/current.json`・`capabilities.rs`（送出元の宣言）を揃える。gse-dataset 側の parity は別作業として記録する。

## 5 gse-replay

- `--invitation <trigger.json>` モード（他のモードと相互排他）。記録の `feat` 行（`p_stuck`）と `key` 行（押下の時刻だけ）から tick を組み、同じ `InvitationMachine` を回して、立った時刻と出した時刻を JSON で出す。組み方は `examples/invitation_trigger_sweep.rs` と同じ（30 秒の欠けで区切り・4:00 の日の区切り）で、共通部分は関数に寄せてよい。
- 本文は読まない（`key` 行は時刻と押下だけ）。

## テスト戦略

- 既存の招待のテストは書き換えない。
- 契機ごとの単体テスト・設定の読み込みのテスト（無い・壊れ・未知の欄・範囲外）・通常のモードの研究の条件（第 1 週・O1・G1 で偽）。
- `gse-replay --invitation` の小さな fixture でのテスト。
- スナップショット回帰（`cargo test` の中の snapshot テスト）・`emit_schema` の byte-equal。
