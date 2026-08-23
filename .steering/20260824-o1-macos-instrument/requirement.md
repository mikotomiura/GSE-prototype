# O1 計器の macOS 実装と実機確認

## 背景

O1（非打鍵チャネルの観測器）は Windows 側 (`observe_windows.rs`) が
2026-08-23 に実装・実機確認済みだが、macOS 側 (`observe_macos.rs`) は
明示的なスタブのまま。ADR-016 D9 は「同時稼働の実機確認（前提1）」が
閉じていることを O1 実装着手の前提としており、Windows では実測で閉じたが
macOS ではまだ未検証。

このタスクは `.steering/_handoff/next-session-prompt-o1-macos-instrument.md`
（前セッションが用意した引き継ぎ文書）をそのまま実行する。設計判断は
ADR-014/ADR-016 で確定済みであり、本タスクは実装 + 実機確認セッション。

## ゴール

1. T1: `CGEventTap` を 2 プロセス（GSE 本体 + 使い捨て probe）で同時に張れるか
   実機で確認する（ADR-016 D9 前提1）。判定は「両プロセスの計数が一致」。
2. T1 が ✅ の場合のみ T2 へ進み、`observe_macos.rs` に以下を実装する:
   - `keyboard_layout_id()`（Carbon FFI, `TISCopyCurrentKeyboardLayoutInputSource`）
   - `secure_input_enabled()`（`IsSecureEventInputEnabled()`, 1Hz, 変化時のみ送出）
   - `FOCUS_AVAILABLE` / L-c フォーカス遷移（`NSWorkspace` 通知, u64 時刻のみ送信）
   - `POINTER_AVAILABLE` / L-b ポインタ（別 tap, `analysis/pointer_bin.rs` 利用, 相対座標のみ）
3. `capabilities.rs` の宣言（`emitterless` / `config_gated`）を実装と一致させる。
4. 両 OS に対のテストを追加（座標を持たないこと / secure_input が遷移時のみ出ること等）。
5. 実機総合確認（ドロップ実測、`pointer_bin`/`focus_transition` 行の実出力、
   `keyboard_layout` の meta 反映、区間削除 UI の mac 動作確認）。

T1 が ❌ の場合は §9.5 案α（同一被験者・別時点）へ降り、その決定を
ADR-016 と `.steering/` に記録して終える（T2 以降は実施しない）。

## スコープ

### 含むもの
- T1: CGEventTap 同時稼働の実機確認（probe は scratchpad に作成、repo に置かない）
- T2: `observe_macos.rs` の実装（T1 成功時のみ）
- T3: `capabilities.rs` の宣言同期
- T4: 両 OS 対テストの追加
- T5: 実機総合確認

### 含まないもの（§5 より）
- 推論への配線（段3）— 新チャネルを読む本番コードは追加しない（ADR-011 D4）
- 役割カテゴリ（ADR-009 D2、G2 判定待ち）
- R3-b（タスク種別ごと）/ 宣言 UI（研究者判断4待ち）
- `is_feature_key` の変更
- 6段階 ablation の事前宣言 / スマホ表現チャネル / Physical Anchor
- G1 被験者への新ビルド配布（`make-distribution.sh` 等は実行しない）

## 受け入れ条件

- [ ] T1 の実機確認結果が完了報告に明記されている（成功/降りたことのどちらか）
- [ ] `HMM_VERSION` が着手前の値 `0.5.0` のまま変わっていない
- [ ] `analysis/key_gate.rs` の `is_feature_key` を1ビットも変えていない
- [ ] ゴールデン6本が byte-equal（`cd src-tauri` して実行）
- [ ] `check_schema_parity.py` が緑
- [ ] `capabilities` の宣言と実装が一致（`cargo test` で機械検証）
- [ ] 段1（`workspace-behavior-observation.md §2.1`）にチャネルを追加していない
- [ ] G1 へ新ビルドを配布していない
- [ ] ドロップの実測値を報告
- [ ] `pointer_bin` / `focus_transition` の行が実際に出力されたことを確認
- [ ] 両 OS の対テストを壊していない
- [ ] 禁止語 grep（`効果があ|精度が上が|有効性`）の結果がヒット0件

## 関連ドキュメント

- `.steering/_handoff/next-session-prompt-o1-macos-instrument.md`（本タスクの引き継ぎ文書、全文）
- `.steering/20260823-o1-instrument-r3a/decisions.md`（D-A/D-F/D-K/D-M）
- `src-tauri/src/input/observe_windows.rs`（対になる実装の全体像）
- `src-tauri/src/input/ime_macos.rs:130-195`（Carbon FFI + dispatch_sync_f パターン）
- `docs/adr/ADR-016-…md` D8/D9
- `docs/adr/ADR-014-…md` D4/D4b/判断4追補
- `.steering/20260823-o1-nonkeystroke-gap-and-prereg/probe-concurrent-hooks.md`（Windows 版 probe 作法）
- `.steering/20260821-workspace-behavior-triage/survey-input-channels.md`

## 運用メモ
- /reimagine 適用: No
- 理由: 設計判断は ADR-014/ADR-016 で確定済み。Windows 側の対称実装
  (`observe_windows.rs`) がリファレンスとして存在し、実装アプローチ・API 選定
  （Carbon FFI パターン、`pointer_bin.rs` の再利用等）はハンドオフ文書に
  既に一次資料付きで指定されている。再生成による複数案比較の余地がない。
