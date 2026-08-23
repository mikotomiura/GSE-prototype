# tasklist — O1 計器の実装 (R3-a) と区間指定削除 UI

> ★ 引き継ぎ: `.steering/_handoff/next-session-prompt-o1-instrument-and-deletion-ui.md` の T0〜T5。

## T0. 決定の記録（⚠️ 実装より先）

- [x] **ADR-014 判断 4 に「配布境界」を追記**し、R3-a の実装着手を記録した
      （`docs/adr/ADR-014-…md`「判断 4 の追補」）
- [x] `/start-task` で `.steering/20260823-o1-instrument-r3a/` を作った

## T1. 区間指定削除 UI（⚠️ 最優先ブロッカー）

- [x] **時間帯を指定して該当セッションの NDJSON 行を削除する経路**（★ 理由を聞かない）
      → `src-tauri/src/redaction.rs` + `delete_time_range` コマンド + `RecordingControls.tsx`
- [x] **稼働中インジケータ**（`get_recording_status` + 常時表示バッジ）
- [x] **即時の一時停止**（`set_recording_paused` + `recording.rs` + ロガーの書き出しゲート）
- [x] ⚠️ **削除した事実を記録に残す**（`redaction_ledger.jsonl`・★ **5 つの数だけ**）
- [x] ⚠️ **`data-privacy` Skill を拡張**（ルール 6 = 区間指定削除 / ルール 7 = 非打鍵チャネル）

## T2. ゲート分割（ADR-016 D8）

- [x] `hook_windows.rs` / `hook_macos.rs` の `is_typing_key` を **`is_observed_key` へ改名し広げた**
- [x] ⚠️★★★ **`is_feature_key` を `analysis/key_gate.rs` に置き、`loop_step::step()` から呼ぶ**
      → ★ **本番と `gse-replay` の両方に 1 か所で効く**（decisions **D-B**）
- [x] ⚠️ **ドロップを実測した** → ★ **0 件**（≈279 events/s の修飾キーを 15 秒注入・decisions **D-K**）
- [x] ⚠️ **両 OS に対のテスト**（テンキー / 修飾キーの OS 非対称・decisions **D-A**）
- **acceptance**
  - [x] `HMM_VERSION` **不変**（着手時 `0.5.0` → 完了時 `0.5.0`）
  - [x] 実 fixture 由来のゴールデン **5 本が byte-equal**
  - [ ] ⚠️ **合成 fixture `category_coverage` は 1 本だけ再生成した**（★ 理由は decisions **D-C**。
        ⚠️ ADR-016 D8 の前提「ゴールデンは新カテゴリを含まない」が**偽だった**）
  - [x] `category` は `{"type":"string"}` のままで **enum 制約を足していない**

## T3. R3-a 計器の実装

- [x] **L-c フォーカス遷移**（Win = 3 本目の `SetWinEventHook(EVENT_SYSTEM_FOREGROUND)`）
      ⚠️ **HWND を callback の外へ出さない**（★ 送るのは `u64` の時刻 1 個だけ）
- [x] **L-b ポインタ**（Win = Raw Input `RIDEV_INPUTSINK` + `GetRawInputBuffer`・**マウスのみ**）
      ★ 1 秒固定ビン・量子化スカラのみ・**ゼロ抑制**（`analysis/pointer_bin.rs`）
- [x] **キーボードレイアウト識別子**（開始時 1 回・識別子のみ・⚠️ `ToUnicodeEx` を呼ばない）
- [x] **計器の健全性**を `capabilities` に自己刻印（★ `config_gated`・理由は `capabilities.rs`）
- [x] `gse-replay` に 4 行種の variant を足した（⚠️ **無いと `--snapshot` 経路が丸ごと落ちる**）
- [ ] ⚠️★★★ **macOS 実装は「明示的なスタブ」にした**（★ 理由は decisions **D-F**）
- [ ] ⚠️ **`secure_input`** —— ★ 行種・schema・writer は用意したが、**送出元は macOS 実装待ち**
- [ ] ⚠️ **D6 の穴** —— ★ 実測で**読み替えが必要**と判明（decisions **D-J**）。
      **判断 4 / 判断 5 待ちなので本タスクでは直さない**
- **acceptance**
  - [x] `HMM_VERSION` 不変
  - [x] ゴールデンの差分は**新フィールドの追加のみ**（★ NDJSON は additive・snapshot は D-C の 1 本のみ）
  - [x] `check_schema_parity.py` が **exit 0**（⚠️ `C:\gse-dataset\schema\current.json` へ配置済み・**コミットは未**）
  - [x] **記録のみ・推論に 1 バイトも流さない**（★ `o1_observation_lines_are_skipped_by_run_replay` が固定）

## T4. 実機確認の残り

- [x] ★ **Windows の同時稼働を再確認**（GSE と probe が同時に `WH_KEYBOARD_LL`・`hook_calls` 1630/1630）
- [ ] ⚠️ **実入力 probe の取り直し** —— ★ **人が実際に打鍵する必要がある**（合成入力では確認にならない）
      ```bash
      bash "/c/Users/johnd/AppData/Local/Temp/claude/C--GSE-prototype/49c2c9cf-e3b0-4118-bb3d-850e9d2e4da5/scratchpad/hookprobe/rerun_real.sh"
      ```
- [ ] ⚠️★★★ **macOS の同時稼働 probe** —— **実機が要る**（⚠️ 落ちたら `§9.5` の案 α へ降りる）
- [ ] ⚠️ **`pointer_bin` / `focus_transition` の行が出ることの実地確認**
      ★ 手順（★ 3 分・⚠️ 測定中に**マウスを動かし・ウィンドウを切り替える**こと）:
      ```bash
      cd C:/GSE-prototype/src-tauri
      GSE_DATASET=/c/Users/johnd/AppData/Local/Temp/gse-o1-check ./target/debug/gse-next.exe &
      # ★ 20 秒ほどマウスを動かし、別アプリへ切り替えて戻る
      taskkill //IM gse-next.exe //F
      grep -c pointer_bin      /c/Users/johnd/AppData/Local/Temp/gse-o1-check/raw/*/*.ndjson
      grep -c focus_transition /c/Users/johnd/AppData/Local/Temp/gse-o1-check/raw/*/*.ndjson
      ```

## T5. 研究者に返すもの（★ dev が決めない）

- [ ] **判断 4**: `creative` の意味と**被験者向けの文言**（→ ADR-016 D7-iv）
- [ ] **同意文書の承認**（⚠️ 承認まで配布しない）
- [ ] **事前登録の未凍結 5 件**
- [ ] ⚠️★★★ **追加で返すもの（本タスクで判明）**
  - **同意文書 注 A の「テンキー」は Windows でのみ真**（decisions **D-A**）
  - **O1 の自然作業が `task_kind:"argumentative"` として記録される**（decisions **D-J**）
  - **macOS の O1 計器は未実装**（★ ADR-016 D9 前提 1 の実機確認が先・decisions **D-F**）

## 完了処理

- [x] 全テスト緑（`cargo test --workspace`: **498 + 30 + 1 passed / 0 failed**）
- [x] 禁止語 grep が **ヒット無し**
- [ ] ⚠️ **コミットしていない**（★ ユーザーの指示待ち）
- [ ] ⚠️ **`C:\gse-dataset` 側の `schema/current.json` のコミット**（★ ファイルは配置済み）
- [ ] ⚠️ **`code-reviewer` / `security-checker` / `/cross-review` は未実行**（decisions **D-L**）
