# data.md — 入力データの来歴

## 1. 入力

| | |
|---|---|
| 置き場 | `$GSE_DATASET/raw` (★ 本機は **`C:/gse-dataset`**。⚠️ `GSE_DATASET` は既定で未設定) |
| ファイル数 | **76 本** の NDJSON |
| 内訳 | `raw/P000/` **13** ＋ `raw/phase1-user-verification/` **63** |
| 被験者 | **6 名** (P000 / P010 / P011 / P012 / P013 / P014) |
| 収集時期 | **2026-04-15 〜 2026-07-2x** (★ ファイル名の日付) |

⚠️★★★ **NDJSON は本リポジトリにコミットしない** (`docs/agent-shared.md` / `data-privacy`)。
★ `results/` に置くのは集計値のみ。⚠️ **ファイル名 (= 擬似 ID ＋ セッション開始時刻) を
JSON に入れない** (experiments/_template/README.md の security-checker HIGH)。

★ 行種の実測 (2026-09-06):

| 行種 | 行数 |
|---|---|
| `key` | 384,095 |
| `feat` | 188,094 |
| `ime_state` | 3,603 |
| `intervention_decision` | 3,129 |
| `ime_shadow` | 2,984 |
| **`paste`** | **847** |
| `probe_assignment` | 271 |
| `realtime_label` | 260 |
| `user_label` | 83 |
| `intervention_response` | 29 |
| ⚠️ **`focus_transition`** | ⚠️★★★ **0** (→ §2) |

## 2. ⚠️★★★ capabilities の判定 (ADR-013)

★ **`capabilities` キーを持つファイルは 0/76 である** (実測)。
→ ⚠️ 判定表の **「どれにも無い」= 計器が無かった**に倒れる。

| 行種 | ゲートの判定 |
|---|---|
| `key` / `feat` / `paste` | **PRESENT** (`<legacy>`)。⚠️ 逐語「**『無い場合』の解釈はこのコホートではできない**」 |
| ⚠️ `focus_transition` | ⚠️★★★ **`INSTRUMENT_ABSENT` (exit 4)** |

★ **理由は一次で確定している**: `FOCUS_TX` を所有する `src-tauri/src/input/observe.rs` の
初出コミットは **2026-08-24** (`9eb1384`) であり、★ **収集 (2026-04〜07) より 1〜4 か月あとである**。
→ ⚠️★★★ **「フォーカス遷移が起きなかった」ではなく「計器が無かった」。**

## 3. ⚠️ 本アームで使えないもの

- ⚠️ **`intervention_enabled` の実験的割付が無い** → ★ 効果推定はできない (`notes.md` §7-2)
- ⚠️ **`focus_transition`** → ★ 新規収集後 (`notes.md` §2)
