# ime-shadow-debug-readout

> ★ 親 PR: **#182**（`feat/macos-ime-shadow` / issue 008）。
> ⚠️ 本タスクは **#182 の上に積んである**（`emit_ime_shadow` が両 OS に開かれていないと計器が無い）。

## 背景

### 1. ★ mac 往復は常態であり、毎回「どの NDJSON か」から始まる

`_handoff/` を見ると mac 実機の往復は繰り返し発生している
（`macos-visual-check-and-distribution` / `o1-macos-instrument` / `o1-macos-distribution` /
`mac-build-distribution-zips` …）。★ そのたびに**書き込み先の特定**から始まる。

⚠️ **現状、書き込み先パスは `logStatus.ok` が false のとき（＝異常時）しか画面に出ない**
（`src/components/Dashboard.tsx:234-246`）。正常時は見えない。

⚠️★★★ さらに **NDJSON は 1 セッションで 2 本できる** ——
起動時に 1 本開き（`lib.rs` の `default_log_path()`）、Dashboard の「開始する」で
`next_session_path()` へ**ローテートする**。→ ★ **取り違えやすい**。

### 2. ⚠️ issue 008 の AC 6 は `gse-replay` では確認できない

`src-tauri/src/bin/replay.rs:149-151, 273, 1828-1829` は `ime_shadow` を
**読み飛ばすだけ**で、`--snapshot` / `--metrics` のどれにも現れない。
→ ★ 現状の確認手段は **jq / grep だけ**。

### 3. ⚠️★★★ 既存の診断パネルに足してはならない（★ 2026-09-11 に実測して判明）

`src/components/Dashboard.tsx:399-428` の診断パネルは **`debugView` で囲まれていない**。
★ フックが 20 秒以上有効にならないときに**被験者にも出る**トラブルシュート用で、
しかも `Object.entries(diagnostics)` で**全フィールドをそのまま吐く**。

→ ⚠️ ここに `abandon` 件数を足すと、**被験者が自分の「放棄回数」を見る**。
★ 較正は**完全ブラインド**が前提なので、これは設計違反である。

## ゴール

**研究者だけが見られる読み出しを 1 つ足し、mac 実機確認を「画面を見るだけ」にする。**

出すもの（★ `ime_shadow` のみ・研究者判断 2026-09-11）:

| 項目 | なぜ |
|---|---|
| ★ **いま書いている NDJSON の絶対パス** | ⚠️ 2 本できる問題を根本から消す |
| `ime_shadow` の**総件数** | ⚠️ **0 件 = 計器が死んでいる**を即座に見る |
| **確定 / 放棄の内訳** | ★ **issue 008 の AC 6 そのもの** |

## スコープ

### 含むもの
- 研究者向け IPC コマンド 1 本（⚠️ **backend も `GSE_DEBUG` で拒否する**）
- `Dashboard.tsx` の **`debugView` で囲んだ**表示ブロック 1 つ
- `emit_ime_shadow` に Atomic カウンタ 2 つ

### 含まないもの
- ⚠️ **他の行種の生存カウンタ**（`key` / `feat` / `paste` / `ime_state`）
  → ★ `logger.rs` の書き出し経路に手を入れる必要があり、範囲が広がる（研究者判断で見送り）
- ⚠️ **既存の診断パネル (`get_diagnostics`) の変更** → ★ 被験者に見えるので触らない
- ⚠️ **常時ポーリング** → ★ ボタンで取得する（既存の診断と同じ作法）
- ⚠️ `gse-replay` に `ime_shadow` を通すこと → ★ Replay-as-Truth の面に触るので別件
- ⚠️ **被験者に見える UI の変更** → ★ 一切しない

## 受け入れ条件

- [ ] 研究者ビルド（`VITE_GSE_DEBUG=1` + `GSE_DEBUG=1`）で、パス・総件数・確定/放棄が画面に出る
- [ ] ⚠️ **被験者ビルド（フラグ無し）では描画されず、コマンドも `Err` を返す**（★ 二重ゲート）
- [ ] ⚠️ **`get_diagnostics` の戻り値に新フィールドが増えていない**（★ 被験者に漏れない）
- [ ] `cargo test --workspace` / `gse-replay --snapshot` / `emit_schema` parity がすべて exit 0
- [ ] ⚠️ **NDJSON の行が 1 行も増えていない**（★ 読み出し専用。`schema/current.json` は不変）
- [ ] `npx tsc --noEmit` が exit 0（`any` 禁止）
- [ ] `code-reviewer` + `security-checker` を通している

## 関連ドキュメント

- `.steering/20260911-outcome-arbitration-and-o1-preflight/issues/008.md` — AC 6
- `.steering/_handoff/next-session-mac-ime-shadow-verification.md` — ★ 本タスクで手順が短くなる
- `.claude/skills/typescript-standards/SKILL.md` — ⚠️ 必読（`any` 禁止 / Tauri IPC）
- `.claude/skills/data-privacy/SKILL.md` — ⚠️ 必読（被験者に何を見せてよいか）

## 運用メモ

- **/reimagine 適用: No**
- 理由: ★ 既存の `debug_force_probe` / `force_nudge` と**同じ形**に載せるだけで、
  アーキテクチャ判断も公開 API の新設も無い。⚠️ 唯一の設計判断（「既存の診断パネルに
  足さない」）は**背景 3 で実測により確定済み**であり、複数案を比べる段階に無い。
