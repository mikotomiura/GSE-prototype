# 設計判断: mac 同期後の後片付け

## 判断 1: `schema_dto.rs` の doc は**整形せず** `#[allow]` で黙らせる

- **決定**: `doc_lazy_continuation` 8 件のうち `schema_dto.rs` の 4 件だけは
  doc を直さず `#[allow(clippy::doc_lazy_continuation)]` を付ける。
- **理由**: ⚠️★★★ **このファイルの doc コメントは外部契約である。**
  ★ schemars が JSON Schema の `description` に本文をそのまま載せており、
  `schema/current.json` に 2026-09-12 時点で実在を確認した。
  ★ 連続行は**空白**で連結され、空の `///` 行は **`\n\n`** になる
  (★ 同ファイル内の他の description で実測)。
  → ⚠️ 字下げでも空行挿入でも **description の文字列が変わり、schema drift になる**。
  ★ `emit_schema` の byte-equal 比較と gse-dataset 側の parity が**同時に落ちる**。
- **却下案**: 「見た目を揃えて `schema/current.json` を再生成する」
  → ⚠️ 本タスクは「振る舞いを変えない後片付け」であり、
  **外部に出ている契約を lint の都合で動かすのは主客転倒**。
- ★ 同じ `doc_lazy_continuation` でも `engine.rs` / `logger.rs` は schema に載らないので、
  **そちらは普通に直した** (★ 空行を 1 行入れる)。

## 判断 2: `logger.rs` の doc は「字下げ」ではなく**本来の関数へ戻した**

- **決定**: `logger.rs:1260-1276` の doc を `static KEYBOARD_LAYOUT_ID` から剥がし、
  `fn write_meta_start` に戻す。
- **理由**: ⚠️★★★ **lint が表面化させたのは書式ではなく実在の欠陥だった。**
  ★ `git show 9eb1384^` で確認すると、この doc は元々 `fn write_meta_start` に直付けされていた。
  ⚠️ `9eb1384` (2026-08-24) が doc と関数の**間に** static を挿入したため、
  **`meta`(session_start) 行の仕様書が別の static の説明になっていた**。
- ★ → ⚠️ **clippy の指示どおり字下げしていたら、誤った付け先を固定してしまうところだった。**
  (★ `verify-before-claiming`: lint の help を鵜呑みにせず一次資料を見た結果)

## 判断 3: `too_many_arguments` (8/7) は `#[allow]` + 理由コメント

- **決定**: `format_intervention_decision_line` の引数 8 個はそのまま。
- **理由**: ★ `logger.rs` の `format_*_line` 群は **NDJSON の 1 行のフィールドと 1:1 に並べる**
  のが既存の規約で、構造体に畳むと「行に何が出るか」がシグネチャから消える。
  ⚠️ 呼び出し元すべてに波及し、「振る舞いを変えない後片付け」の枠を超える。
- ⚠️ **黙って握りつぶさない** —— なぜ許容するかをコードに書いた。

## 判断 4: `Default` は **Windows / macOS の対で**入れる

- **決定**: `new_without_default` は `ime_windows.rs` だけでなく `ime_macos.rs` にも
  `impl Default` を足す。
- **理由**: ⚠️ `ime_macos.rs` の `ImeMonitor::new()` も引数なしなので、
  **mac 側の clippy でも同じ lint が出る**。片方だけ直すと OS で結果が割れる。
- ⚠️★★ **`ime_macos.rs` は Windows では 1 行もコンパイルされない**ので、
  ★ この 1 箇所だけ**本機では検証できていない**。→ mac CI (`check` / macOS) に委ねる。
  (★ `docs/agent-shared.md` の「手元の検証は CI の代替にならない」に該当)
- ★ 前例: repo には `impl Default for X { fn default() -> Self { Self::new() } }` が
  10 箇所あり (`engine.rs:143` ほか)、**これが本 repo の作法**である。

## 判断 5: HMM ループは `enumerate()` に留め、**加算順序を変えない**

- **決定**: `needless_range_loop` 6 件は `iter_mut().enumerate()` / `iter().enumerate()` で
  添字を取るだけにする。⚠️ **`iter().sum()` や `fold` には書き換えない。**
- **理由**: ⚠️★★★ **浮動小数の加算は結合則を満たさない。**
  ★ `trans_sum` / `sum_prob` の足し込む順番を変えると確率列の下位ビットが動き、
  **ゴールデンが割れる** (⚠️ それは `HMM_VERSION` bump の合図ではなく**修正が誤っている合図**)。
- ★ **検証結果**: ゴールデン **6 fixture / 226 snapshot が byte-equal** で一致。
  → ⚠️ したがって `HMM_VERSION` は **bump しない** (★ 挙動を変えていないため)。

## 判断 6: 件数は 29 ではなく **33** だった

- ★ 当初の計測は **29 件**だったが、⚠️ それは **lib のコンパイルが落ちて
  bin が解析されていなかった**ため。
- ★ lib を緑にした時点で `src/bin/replay.rs` の 4 件 (`collapsible_if` ×3 /
  `ptr_arg` ×1) が現れ、**合計 33 件**になった。
- → ⚠️ **「N 件直す」という計画は lint では当てにならない**
  (★ 直すと次が見える)。受け入れ条件を件数ではなく **exit 0** に置いたのが正解だった。

## 判断 7: gse-dataset の未追跡 13 本は**削除**する

- **決定**: `C:\gse-dataset` の `metrics/P000/macos/*.metrics.json` 13 本 (2026-04-15〜17) を削除。
- **理由**:
  1. ★ 元データ `raw/P000/*.ndjson` が **repo に追跡済みで残っている** → **再生成可能**。
  2. ⚠️ `hmm_version` / `app_version` を**持たない旧形式**で、
     ★ どの HMM 版の出力か**帰属できない** (`reproducibility-discipline` に反する)。
  3. ⚠️ 追跡済みの同ディレクトリのファイルが持つ `.range_metrics.json` の**対が無い**。
- ⚠️ **削除前に (1) を実地で確認した** (★ `find raw labeled -name "*2026041[567]*"`)。
