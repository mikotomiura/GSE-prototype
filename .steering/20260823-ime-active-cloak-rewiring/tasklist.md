# tasklist — `IME_ACTIVE` cloak 経路への配線替え

## A-1 実装

- [x] 引き継ぎ + `findings-enumwindows-probe.md` §14-16 を読む (⚠️ §14 の撤回・§15/§16 の確定)
- [x] ⚠️★★★ **辺の向き**が未測定であることを発見し、論点として立てる (→ `decisions.md` D-3)
- [x] `windows` crate に `Win32_Graphics_Dwm` feature を追加
- [x] `input/ime_cloak.rs` (新規・OS 非依存): `is_ime_cloak_class` / `candidate_shown_from_cloak` / `CloakFold`
- [x] `hook.rs`: `CLOAK_EVENT_TX` / `CloakEvent` / `LEGACY_IME_EVENT_SEEN`
- [x] `hook_windows.rs`: 2 本目の WinEvent hook (`0x8017..=0x8018`) + `cloak_event_callback` (⚠️ `try_send` のみ)
- [x] `hook_windows.rs`: `unhook_all` で 2 本目も外す (⚠️ 外し忘れると再設置で積み上がる)
- [x] `ime_windows.rs`: resolver スレッド (`GetClassNameW` + `DwmGetWindowAttribute`)
- [x] ⚠️★★★ `is_stale_winevent_active` を `legacy_path` で絞る (→ D-5。**これが無いと A は動かない**)
- [x] `lib.rs`: resolver スレッドの起動 (⚠️ `init_hook` より前)
- [x] `capabilities.rs`: doc の実態を更新 (⚠️ `config_gated` は据え置き)

## テスト (機械検査)

- [x] `CloakFold` の単体 10 本 (重なり融合 / debounce 内再入 / 超え / 上限自己修復 / 二重 Begin)
- [x] ⚠️ 番兵 `0` のバグを `Option<u64>` で修正 (★ t=0 のテストで 5 本落ちて発覚)
- [x] 既存回帰 `excludes_language_bar_and_imm32_system_window` が緑のまま
- [x] `cargo fmt --all -- --check` = **0**
- [x] `cargo test --workspace` = **0** (452 + 29 + 1 passed)
- [x] `cargo clippy --all-targets` = **0** (⚠️ 変更ファイルの新規警告 0 件)
- [x] ゴールデン byte-equal = **0** (`OK: 15 snapshots match`)
- [x] `emit_schema` が `schema/current.json` と byte-equal = **yes**
- [x] `check_schema_parity.py --dataset C:/gse-dataset` = **0**

## 実測 (⚠️ 実機・人が要る)

- [x] 実測 E (静止時の cloak 状態) をプローブに追加
- [x] 実測 D (順序 + 窓別連番 + DWM 実状態) をプローブに追加
- [x] 実測 F (**本番の `CloakFold`** を実データで回し debounce 幅を掃く) をプローブに追加
- [x] ⚠️ **無操作 60 秒で cloak が 1 件も起きない**ことを確認 (★ 実測済み: 全クラス 0 件)
- [x] ⚠️★★★ **辺の向きの確定** (実測G) → **`UNCLOAKED` = 候補表示。実装は正しい**
- [x] ⚠️★★★ **`FOLD_GAP_MS` の確定** (実測F) → **150 ms** (★ 最小ギャップ 308ms の約 1/2)
- [x] ⚠️★★★ **pause 区間の割合の実測** → 52.1% (⚠️ **計測手順の産物。代表値ではない**・findings §4.4)
- [ ] ⚠️★★★ **実起動ログで `ime_shadow` 行が実際に出る**
- [ ] ⚠️★★★ **無操作 60 秒で `ime_shadow` が 1 行も出ない** (実起動での回帰確認)

## A-2 (判断のみ)

- [x] 研究者判断を仰ぐ → **(a) Windows 単独で収集開始** (`decisions.md` D-9)

## レビュー

- [x] `code-reviewer` + `security-checker` を**並列**起動 → HIGH 3 件すべて対応
- [x] `/cross-review` (Codex・パス限定 `a5de3e3..HEAD -- src-tauri/src/input/*.rs`) → 重大 1 + 中 2 に対応
      ⚠️ `findings-*.md` は外部へ渡していない (★ 渡したのは `.rs` の diff のみ)
- [ ] `/finish-task` (⚠️ **実測 D/F と実起動確認が残っているため未実行**)

## ⚠️★★★ 残り (★ 人が要る。これが埋まるまで収集を始めない)

- [x] 実測 D/G/F の 60 秒 × 2 (打鍵 270 / 257)
- [ ] ★ **自然な打鍵**での pause 率 (⚠️ 現在の 52.1% は「候補を 3 秒保持」の指示による産物)
- [ ] 実起動で `ime_shadow` が出る (★ **G1 画面 = GSE 自身の窓でも**確認すること)
- [ ] 実起動・無操作 60 秒で `ime_shadow` が 1 行も出ない
