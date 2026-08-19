# G1 リブート — 計器 (ADR-013) と運用 (G-1 二度押し) を直してから測り直す

## 背景

2026-08-19、研究者が **G1 をリブートする**と決定した (`_handoff/next-session-prompt-g1-reboot-and-instrument-fix.md §0`)。

- P010 は**確証標本から外し、パイロットとして保存**する (削除しない)。★ 残り 2 名ではなく **3 名を取り直す**。
- ⚠️★★★ **リブートの範囲は「計器＋運用」に限る。設計の問い (何を測るか・条件・ブロック構成・
  分析計画) は 1 文字も変えない** (研究者決定 #2)。

### ★ なぜリブートが「損失」ではないか

ゲートの種類が違う:

| 何 | 何で塞がれていたか | リブートで開くか |
|---|---|---|
| **ADR-013 実装** | **G1 が *実施中* であること** | ★ **開く。停止期間がそのまま実装窓になる** |
| ADR-011 D4「読む実装」 | **G1 の *判定*** | ⚠️ 開かない |

さらに **ADR-013 実装 → リブート**の順にすると、新 G1 ログに `starve_window` が載り、
**ADR-012 Stage 0 の左打ち切り問題が緩和される** (`C_write` を下界だけでなく幅で出せる)。
⚠️ 逆順にするとこの利得を失う。

### 直す対象は 2 件だけ (実測で確認済み・これ以外は増やさない)

1. **G-1: セッション active 中の「開始する」二度押し** (P010 block07 で実発生)
   `lib.rs:2008` の `if g1_mode().is_some() && !was_active` によりローテートが走らず、
   `lib.rs:2036` の `SessionStart` だけが積まれる ＝ **1 ファイルに 2 セッション**。
2. **ADR-013: 収集仕様の自己記述性** (D1〜D6・仕様は確定済み。設計し直さない)

## ゴール

★ **次コホートの収集を始める前に、計器と運用を直し切る。**
⚠️ **収集開始より後に計器を直したら、本タスク群の動機そのもの (「計器がコホートを跨げなかった」失敗
2 件) を 3 件目として再生産する。**

### Done (exit code / テスト名で言える形)

`src-tauri/` から:

| # | 条件 | 検証コマンド |
|---|---|---|
| D-a | 単体テストが緑 | `cargo test --workspace` が exit 0 |
| D-b | ADR-013 D3-1 網羅テスト | `capabilities_covers_every_line_type` が緑 |
| D-c | ADR-013 D3-2 OS 対のテスト | `ime_shadow_in_capabilities_on_windows` / `ime_shadow_absent_from_capabilities_on_macos` が**両 OS の CI で**緑 |
| D-d | ADR-013 D3-3a 仕様の回帰 | `starve_window_omits_empty_windows` / `dropped_delta_is_per_line_difference` / `hook_health_semantics_unchanged` が緑 |
| D-e | ADR-013 D3-3b 過大申告の逆アサート | `every_capability_has_a_reachable_emitter` が緑 |
| D-f | ADR-013 D3-4 schema parity | `cargo run --bin emit_schema` の出力が `schema/current.json` と byte-equal かつ `python scripts/check_schema_parity.py --dataset <gse-dataset>` が exit 0 (⚠️ `--dataset` 必須。省くと exit 0 のまま空振りする) |
| D-g | ゴールデン 6 本が byte-equal | `cargo run --bin gse-replay -- … --snapshot …` が 6 本とも exit 0 |
| D-h | `HMM_VERSION` 据え置き | `0.4.0` のまま (additive のみ)。⚠️ 動いたら設計を疑う |
| D-i | G-1 修正 | `double_start_closes_previous_session_then_rotates` / `double_start_is_noop_outside_g1_mode` が緑 |
| D-j | 事前登録の版一致 | `preregistration.md` 第 17 版 / `config.json` / `analyze.py PREREG_REVISION` が一致し `analyze.py --selftest` が exit 0 |

### Stop (これが起きたら止めて研究者に返す)

- `HMM_VERSION` を上げないとゴールデンが緑にならない → ★ additive のはずなので**設計を疑う**
- `hook_health` の出力条件・意味論を変えないと実装できない → ★ ADR-011 探索トラック /
  ADR-012 Stage 0 が再計算になるので**止める** (ADR-013 D4)

## スコープ

### 含むもの

- ADR-013 D1 / D2 / D4 の実装 (`meta.capabilities` / `meta.app_version` / `starve_window` / `dropped_delta`)
- ADR-013 D3 の 5 テスト
- G-1「閉じてから開く」修正 (⚠️ **G1 モードのときだけ**)
- 事前登録 **第 17 版** への改訂 (+ `config.json` / `analyze.py PREREG_REVISION`)
- P010 のパイロット格下げの記録 (`data.md` / `notes.md` / 事前登録)
- ★ 「G1 は実施中」を前提にした記述 **8 件**の修正 (handoff §6)
- ADR-013 D5-2b: `consent.md` 記録項目表 + `participant-guide.md` への `starve_window` / `app_version` 追記

### 含まないもの (⚠️ 明示的に外す)

- **設計の問い** (何を測るか・条件・ブロック構成・分析計画) — 研究者決定 #2
- **適格性ゲート `keydown ≥ 100`** — 同上 (ADR-011 D3)。⚠️ 触ると `§9` A-Q3 が基準にしている CV `0.502` の再計算に波及する
- **`gse-submit` の提出経路** — 既に解決済み (2026-08-08 自動提出・`notes.md §8`)
- **ADR-011 D4「読む実装」** — G1 の *判定* 待ち。リブートしても開かない
- **App.tsx の argumentative lock 解除の実装** — 方針だけ `decisions.md` に凍結する (判断 5/6)
- **較正プロトコル (T-C) の G1 相乗り** — 研究者決定で**相乗りさせない** (判断 3)
- **電子同意フォーム (Google フォーム) との突合** — repo 内 2 文書のみ直し、突合は収集開始前ゲートとして残す
- **非打鍵モダリティの信号本体** — ADR-013 D6 / ADR-012 の実測待ち

## 受け入れ条件

- [ ] Done の D-a 〜 D-j がすべて緑
- [ ] `.steering/` に `decisions.md` (判断 1〜8) が記録されている
- [ ] handoff §6 の 8 件が「G1 は実施中」→ リブート後の記述に更新されている
- [ ] ADR-013 D5 のゲートが「G1 完了後」→「**リブート前の停止期間**」へ改められ、ADR に追記されている
- [ ] `/cross-review` を通している (パス限定で実行・skip した場合は理由を明記)

## 関連ドキュメント

- `.steering/_handoff/next-session-prompt-g1-reboot-and-instrument-fix.md` (本タスクの発注書)
- `docs/adr/ADR-013-collection-self-description.md` (D1〜D6・実装仕様)
- `docs/adr/ADR-012-…` / `docs/adr/ADR-011-low-typing-window-track.md` (依存する探索・形成的トラック)
- `experiments/20260801-controlled-friction-task/preregistration.md` (第 16 版 → 第 17 版)
- `experiments/20260801-controlled-friction-task/protocol.md §1` (1 ブロック = 1 ファイル)
- `docs/architecture/task-adaptation-and-scope-gating.md §2.1 / §2.8`

## 運用メモ

- **/reimagine 適用: Yes** — 理由: G-1 の「閉じてから開く」は**部分失敗のときに何を保証するか**が
  設計の核であり、素直な実装 (3 回 `try_send` するだけ) は `protocol.md §1` が却下した
  「沈黙して間違った結果を出す」失敗を再導入しうる。実装着手前に代案を出して比較する。
