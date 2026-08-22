# IME_ACTIVE の配線を EnumWindows 経路へ移す

## 背景

2026-08-22 に `examples/ime_winevent_probe.rs` で 60 秒 × 3 回の実機計測を行った結果、
この Windows 11 環境の IME は **MSAA の IME イベントを一切上げない**ことが判明した。

| 実測 | 数値 |
|---|---|
| フックは生きている | `alive = 6544` (0x8000-0x8030 の全オブジェクトイベント) |
| 日本語入力は確かに行われた | `TEXTSELECTIONCHANGED` 298 / `VALUECHANGE` 246 / `CREATE` 680 = `DESTROY` 680 |
| **IME イベントは 0 件** | `IME_SHOW`(0x8027) / `IME_HIDE`(0x8028) / `IME_CHANGE`(0x8029) / `CONV_TARGET`(0x8030) すべて 0 |
| `ImmGetContext` | 試行 120 / 成功 0 |

→ **候補 UI が汎用イベントで表現されており、IME 専用イベントが飛ばない。**

### 配線の非対称 (これが直す対象)

| 何 | 駆動源 | 状態 |
|---|---|---|
| `is_candidate_window_open()` (`ime_windows.rs:61`) | WinEvent **OR** EnumWindows **OR** UIA | 動く (`lib.rs:2731` が毎周期呼ぶ) |
| `IME_ACTIVE` (Atomic) | **WinEvent コールバックだけが `true` を書く** (`hook_windows.rs:209`) | **死んでいる** |
| `ime_shadow` / `dwell_ms` / `nav` | Atomic 側 (`IME_SHADOW_READY` は WinEvent の `IME_HIDE` 枝でしか立たない) | **0 行** |

**働く検出器 (EnumWindows) が無効化用 (stale 判定) にしか繋がっておらず、
データを産む側は死んだ経路 (WinEvent) に繋がっている。**

### 時間的制約

**収集開始前にしかできない。** 収集が始まると `preregistration.md §3.6` により回復不能。

## ゴール

`IME_ACTIVE` の**正の駆動源**を、死んだ WinEvent 経路から実際に動く経路へ移し、
`ime_shadow` 行が実起動ログに**実際に出る**状態にする。

ただし **§2.1 の実測が先**。EnumWindows 経路が効かなければ B は不成立とし、
`IME_ACTIVE` は「取れない」と結論して `config_gated` のまま据え置く。

## スコープ

### 含むもの
- `examples/ime_winevent_probe.rs` に `is_ime_candidate_window_visible()` 呼び出しを追加して実測
- (実測が肯定的なら) `lib.rs` のポーリングスレッドで `IME_ACTIVE` を駆動する配線
- `false → true`: `IME_COMPOSITION_START_MS` を刻む / `IME_CANDIDATE_NAV_COUNT` をリセット
- `true → false`: `dwell_ms` を計算し `IME_SHADOW_READY` を立てる
- `capabilities` の `ime_shadow` 区分の再判定 (実測で決める)
- **意味が変わったこと** (composition → 候補ウィンドウ滞在) の記録

### 含まないもの
- 新規 API の追加 (ゼロ)
- フックコールバック内の変更 (`hook-constraints` Win-1 に抵触するため、ポーリングスレッドで行う)
- 自前 TIP / DLL 注入による composition 取得 (`agent-shared.md` 技術的制約 7 で不採用)
- `docs/research-positioning.md §5` の変更
- ADR-009 の X 軸・現行 G1 の変更
- 未コミットの `.claude/settings.json` / `.gitignore` (タスク無関係)

## 受け入れ条件

- [ ] `cargo test --workspace` 緑
- [ ] **ゴールデンが byte-equal** (変わったら `HMM_VERSION` の扱いを裁く)
- [ ] `emit_schema` が `schema/current.json` と同一 / schema parity exit 0
- [ ] **実起動ログで `ime_shadow` 行が実際に出る** (「実装した」ではなく「出た」を見る)
- [ ] `.steering/` に**意味が変わったこと**を記録
- [ ] `capabilities` をどう扱ったか (`config_gated` 据え置き / `unconditional` へ戻す) を実測根拠付きで記録

## 関連ドキュメント

- `.steering/_handoff/next-session-prompt-ime-active-rewiring-and-idea-followups.md` (本タスクの発注元)
- `src-tauri/src/input/ime_windows.rs` §46-48 (WinEvent が composition 段階検出の唯一の手段である旨の逐語)
- `src-tauri/src/capabilities.rs` §109-161 (`ime_shadow` の `config_gated` 移動根拠)
- `docs/agent-shared.md` 技術的制約 7 (TSF / UIPI / WinEvent の結論)
- `.steering/20260821-workspace-behavior-triage/survey-input-channels.md §7`

## 運用メモ

- **/reimagine 適用: No**
- 理由: 設計の選択肢は handoff §2.2 で既に一意に確定している (「既存のポーリングスレッドで
  `active` を `IME_ACTIVE` の正の駆動源にする」・新規 API ゼロ)。複数案を比較する段階ではなく、
  実測 (§2.1) の結果で Yes/No が決まるだけの実装タスクである。
- **grill 省略: Yes**
  - 理由: handoff §1 が「★ 議論し直さない」と明記し、§2.4 が受け入れ条件を
    exit code / テスト名の形で既に凍結している。grill の目的 (検証可能なゴールの確定) は
    発注元セッションで達成済みであり、再 grill は確定済み判断の蒸し返しになる。
