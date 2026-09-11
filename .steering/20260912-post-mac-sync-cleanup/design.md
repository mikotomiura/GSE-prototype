# 設計: mac 同期後の後片付け

## アプローチ

⚠️★★★ **振る舞いを 1 ビットも変えないことが本タスクの不変条件**である。
★ それを機械で守る装置が既にある —— **ゴールデン回帰 6 fixture / 226 snapshot の byte-equal 比較**。
→ ★ 各修正の後に必ず回す。⚠️ **1 snapshot でもずれたらその修正は誤りとして戻す**。

⚠️ `cargo clippy --fix` の一括適用は**しない**。理由:
`doc list item without indentation` が触るのは **★/⚠️ を含む日本語 doc コメント**であり、
自動整形が意味の区切りを壊しうる。→ ★ 分類ごとに手で当てる。

## clippy 29 件の分類と方針

| # | lint | 箇所 | 方針 | リスク |
|---|---|---|---|---|
| A | `dead_code` 1 件 | `ime_windows.rs:168` | ★ **関数ごと削除** | ⚠️ 低 (後述) |
| B | `doc_list_item_without_indentation` 8 件 | `engine.rs:34-36` / `logger.rs:1277` / `schema_dto.rs:39-42` | ★ 継続行を字下げ | ⚠️ **doc のみ**・コード不変 |
| C | `needless_range_loop` 6 件 | `engine.rs:426,428,441,548,550,560` | ★ `iter_mut().enumerate()` へ | ⚠️★★★ **最高** (後述) |
| D | `manual_is_multiple_of` 3 件 | `features.rs:151` / `metrics.rs:1130,1148` | ★ `.is_multiple_of(2)` | ⚠️ 低 |
| E | `needless_lifetimes` 1 件 | `metrics.rs:1035` | ★ `'a` を省略 | ⚠️ 低 |
| F | `manual_abs_diff` 1 件 | `metrics.rs:1047` | ★ `a.abs_diff(b)` | ⚠️ **中** (後述) |
| G | `manual_range_patterns` 1 件 | `hook_windows.rs:148` | ★ `0x25..=0x28` | ⚠️ 低 |
| H | `new_without_default` 1 件 | `ime_windows.rs:27` | ★ `Default` impl を足す | ⚠️ 低 |
| I | `unnecessary_map_or` 3 件 | `ime_windows.rs:285,302` / `lib.rs:3609` | ★ `is_some_and` 等へ | ⚠️ 低 |
| J | `collapsible_if` 1 件 | `ime_windows.rs:298` | ★ `&&` で畳む | ⚠️ 低 |
| K | `too_many_arguments` 1 件 (8/7) | `logger.rs:369` | ⚠️ **`#[allow]` + 理由コメント** | — |
| L | `redundant_closure` 1 件 | `lib.rs:1696` | ★ `std::env::var_os` を直接渡す | ⚠️ 低 |
| M | `explicit_auto_deref` 1 件 | `lib.rs:2306` | ★ `&log` | ⚠️ 低 |

### ★ A: `is_ime_active_check` を削除してよい根拠 (一次資料)

- ★ 本体は `// Kept for API compatibility (unused)` と書かれ、**常に `false` を返すだけ**。
- ★ repo 全体の grep で **参照は定義行のみ** (TypeScript 側・Tauri コマンド登録にも無し)。
- ★ `.steering/20260415-windows-onboarding/completion-log.md` / `20260606-.../tasklist.md` /
  `20260823-wall-removal/tasklist.md` の **3 本が「既存 warning」として記録**しており、
  ⚠️ **今回の変更由来ではない**ことが裏取りできる。
- ⚠️ 「API compatibility」の相手は存在しない (★ 本体は配布アプリでありライブラリではない)。

### ⚠️★★★ C: engine.rs の HMM ループが最高リスクである理由

★ 対象は **Forward Algorithm の行列積** (`old_probs` × 遷移行列 → `new_probs`)。
⚠️ **浮動小数の加算は結合則を満たさない** ので、**総和の順序を変えると値が変わる**。
→ ⚠️★★★ `iter().sum()` や `fold` への**書き換えはしない**。
★ `needless_range_loop` が求めているのは **外側の添字を `enumerate()` にすること**だけであり、
**内側の加算順序は保つ**。この 2 つを混同しない。

★ 守り方: この 6 件を当てた直後に**単独で**ゴールデン 6 fixture を回す
(⚠️ 他の修正とまとめて回すと、ずれたとき原因の切り分けができない)。

### ⚠️ F: `abs_diff` の意味同値を確かめてから当てる

★ `abs_diff` は**符号なし**を返す。元の式が `i64` の引き算を経由している場合、
⚠️ **オーバーフロー時の挙動と戻り値型が変わりうる**。→ ★ 型と呼び出し元を読んでから当てる。

### ⚠️ K: `too_many_arguments` だけ `#[allow]` にする理由

★ 他の 28 件は「書き方を変えるだけ」だが、これは **関数シグネチャの設計変更**を要求する。
⚠️ 引数を構造体に畳むのは **`logger.rs` の呼び出し元すべてに波及**し、
「振る舞いを変えない後片付け」という本タスクの枠を超える。
→ ★ `#[allow(clippy::too_many_arguments)]` に **なぜ許容するか**を書いて残す
(⚠️ 黙って握りつぶさない)。

## 変更対象ファイル

| ファイル | 件数 | 層 |
|---|---|---|
| `src-tauri/src/analysis/engine.rs` | 9 (B3 + C6) | analysis |
| `src-tauri/src/input/ime_windows.rs` | 5 (A1 + H1 + I2 + J1) | input |
| `src-tauri/src/schema_dto.rs` | 4 (B) | — |
| `src-tauri/src/analysis/metrics.rs` | 4 (D2 + E1 + F1) | analysis |
| `src-tauri/src/lib.rs` | 3 (I1 + L1 + M1) | — |
| `src-tauri/src/logger.rs` | 2 (B1 + K1) | — |
| `src-tauri/src/input/hook_windows.rs` | 1 (G) | input |
| `src-tauri/src/analysis/features.rs` | 1 (D) | analysis |

⚠️ **モジュール境界は 1 つも動かさない** (`architecture-rules`: `analysis/` に OS API を入れない
—— ★ 本タスクは `use` を 1 行も増やさない)。

## テスト戦略

★ **追加のテストは書かない**。理由: 振る舞いを変えないことが要件なので、
**既存のゴールデン回帰が "変わっていないこと" の証明そのもの**である
(⚠️ 新しいテストを足すと「何を守っているか」が二重になる)。

実行順 (★ `src-tauri/` から):
1. `cargo clippy --quiet -- -D warnings` → **exit 0**
2. `cargo test --workspace` → **653 passed** 維持
3. ゴールデン 6 fixture (`gse-replay --snapshot`) → 全一致
4. `cargo run --bin emit_schema` → `schema/current.json` と byte-equal
   (⚠️ `schema_dto.rs` を触るので **必須**。★ doc コメントだけなら出力は変わらないはず
    —— ★ それを機械で確かめる)

⚠️★★★ **`HMM_VERSION` は bump しない。** ★ bump 条件は「HMM 挙動を変えたら」であり、
本タスクは**変えない**。→ ⚠️ もしゴールデンがずれたら、それは bump の合図ではなく
**修正が誤っている合図**である。

## ブランチ / dataset の後片付け

- ★ `git branch -d` (⚠️ **`-D` は使わない** —— 未マージを取り違えたら止まってほしい)。
- ⚠️ **`origin` には触れない** (`git push --delete` を実行しない)。
- ★ dataset 13 本は **`raw/P000/*.ndjson` が追跡済みで残っている**ため再生成可能。
  → ⚠️ それを**削除前に確認済み**。
