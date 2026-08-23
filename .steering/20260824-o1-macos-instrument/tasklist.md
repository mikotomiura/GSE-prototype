# タスクリスト

## 準備
- [x] 引き継ぎ文書を読む（`.steering/_handoff/next-session-prompt-o1-macos-instrument.md`）
- [x] `HMM_VERSION` を grep で実測して控える（0.5.0）
- [ ] `.steering/20260823-o1-instrument-r3a/decisions.md` の D-A/D-F/D-K/D-M を読む
- [ ] `src-tauri/src/input/observe_windows.rs` を読む（対称実装の全体像）
- [ ] `src-tauri/src/input/observe_macos.rs` の現状（スタブ）を読む
- [ ] `src-tauri/src/input/ime_macos.rs:130-195` を読む（FFI パターン）
- [ ] Skill: hook-constraints / rust-standards / architecture-rules / data-privacy を Read

## T1: 同時稼働の実機確認（実装より先）
- [x] Windows 版 probe の作法（`probe-concurrent-hooks.md`）を読む
- [x] scratchpad に使い捨て probe を作成（VK/文字/座標を読まない、数だけ数える）
- [x] 2プロセス同時起動し、`tap設置成否` / `callback到達数` を比較（52=52, 70=70 で完全一致）
- [x] 合成入力（✅完全一致）・実入力（signal_absent、Windows版と同型）の両方で確認
- [x] `ScrollWheel` / `MouseMoved` の別 tap も同時に張れるか確認（✅ 別 tap で 70/70 一致）
- [x] 判定を記録（✅ 一致 → T2へ）— `decisions.md` T1 節

## T2: observe_macos.rs 実装（T1 ✅ の場合のみ）
- [x] `keyboard_layout_id()` 実装（TISCopyCurrentKeyboardLayoutInputSource、UCKeyTranslate は呼ばない）
      ⚠️ 実装当初は `ime_macos.rs` を真似て `dispatch_sync_f` 経由にしたが、実機で
      メインスレッド自己デッドロック→クラッシュを実測（decisions.md 判断3）。
      呼び出し元 (`lib.rs::setup()`) がメインスレッドである前提で直接呼ぶ形に修正し解消。
- [x] `secure_input_enabled()` 実装（IsSecureEventInputEnabled、1Hz、変化時のみ送出）
- [x] `FOCUS_AVAILABLE` / L-c フォーカス遷移実装（NSWorkspace 通知、u64時刻のみ送信・objc2 経由）
- [x] `POINTER_AVAILABLE` / L-b ポインタ実装（別tap、pointer_bin.rs 利用、相対座標のみ）
- [x] CGEventTapIsEnabled の定期確認・無通知失効への再有効化を追加
      ⚠️ **即再有効化 (TapDisabledByTimeout/ByUserInput) のみ実装**。「tap 完全失効時の
      作り直し」は未実装（decisions.md 判断4・次セッション送り）

## T3: 宣言と実装の一致
- [x] `capabilities.rs` の `emitterless` から実装済み行種を除去
- [x] `config_gated()` に `secure_input` の条件付き push を追加
- [x] `cargo test` で宣言/実装一致を確認（10 tests green）

## T4: 両OS対テスト
- [x] 既存4本のテストが壊れていないことを確認
- [x] ポインタ変換が座標を持たないことのテストを追加
- [x] secure_input が遷移時のみ行を出すことのテストを追加

## T5: 実機総合確認
- [x] ドロップの実測（0件・dropped_delta 出現なし・hook_health 変化なし）
- [x] pointer_bin / focus_transition の行が実際に出ることを確認（73行/13行、合成マウス+アプリ切替）
- [x] meta に keyboard_layout が載ることを確認（com.apple.keylayout.ABC）
- [ ] 区間指定削除UI/一時停止/インジケータが mac で動くことを確認
      ⚠️ 未確認（本 Mac ではスクリーンショット不可・本タスクの diff 対象外の既存機能）
- [ ] 長時間安定性確認（約90秒のみ確認。数時間規模は未検証）

## テスト
- [x] ゴールデン6本 byte-equal（cd src-tauri・`replay_snapshot_goldens_byte_equal` green）
- [x] check_schema_parity.py は未実行（`--dataset` に gse-dataset repo のローカルパスが必要で
      本セッションには無い）。★ ただし `schema_dto.rs`/`schema/current.json` は本タスクで
      **1バイトも変更していない**（`git diff --stat` で確認済み）ので drift リスクは無い。
      `emit_schema` の出力と `schema/current.json` の byte-equal は確認済み
- [x] cargo test --workspace 緑（479 lib tests + 30 replay tests + 1 integration test、修正後）

## レビュー
- [x] code-reviewer によるレビュー（HIGH 2 / MEDIUM 6 / LOW 5）
- [x] security-checker によるレビュー（HIGH 1(H1) / MEDIUM 2 / LOW 4）
- [x] HIGH 指摘への対応（3件すべて対応 — secure_inputエッジロス・tap設置リトライ・
      ビジーループ回避。decisions.md「code-reviewer/security-checkerレビュー」節）
- [x] MEDIUM/LOW のうち妥当なもの 10 件を対応、2件(M1/M2)は理由付きで見送り記録
- [x] 修正後に実機で再確認（クラッシュ0・pointer_bin/focus_transition/secure_input出力・
      CPU高使用率は本タスク無関係の既存事象と確認・moved=0は注入ツールのcoalescing artifactと確認）
- [x] /cross-review（finish-task Step 3）— 両者一致HIGH1件を修正（`pointer_ok`永久固着バグ）、
      Codex指摘MEDIUM1件を採用（secure_input 2段目ドロップの検知）、
      Codex指摘HIGH1件を実機検証で反証・却下

## ドキュメント
- [x] 禁止語 grep 確認（効果があ|精度が上が|有効性 → ヒット0、後述で再確認）
- [x] docs の更新（`workspace-behavior-observation.md` §9.2 7-b に完了を追記）

## 完了処理
- [x] design.md の最終化
- [x] decisions.md の作成・更新（T1判定・設計判断5件・レビュー対応2ラウンド）
- [x] 完了報告に §6 のチェックリストを転記して報告
- [ ] git commit（ユーザー承認待ち）
