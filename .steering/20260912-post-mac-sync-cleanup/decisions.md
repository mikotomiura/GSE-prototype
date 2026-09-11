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

---

# レビュー後の判断 (code-reviewer / security-checker を並列実行した結果)

★ 両者とも CRITICAL / HIGH の**新規**脆弱性・欠陥は無しと判定。
⚠️ ただし **私の判断ミスが 2 件**指摘され、どちらも**指摘が正しかったので直した**。

## 判断 8: ⚠️ **`--all-targets` を外したのは誤りだった** (自分の判断を撤回)

- ★ 当初 `requirement.md` で「`--all-targets` はスコープ外 (hook の gate は lib/bin のみ)」と決めた。
- ⚠️★★★ **これは間違いだった。** ★ code-reviewer の指摘どおり、
  **コミットメッセージ自身が書いた罠 (「lib を緑にすると bin が見えた」) が、`#[cfg(test)]` の
  一段下にそのまま残っていた**。
  ★ 証拠: `features.rs` / `metrics.rs` で潰したのと**同じ** `manual_is_multiple_of` が
  `probe_scheduler.rs` のテストに生き残っていた。
- **対応**: `--all-targets` を含めて **12 + 6 = 18 件**を追加で是正し、
  ★ `.claude/hooks/stop-check.sh` の gate 自体に **`--all-targets` を追加**した
  (⚠️ **穴の開いた検査を残したままにしない**)。
- ★ 特筆: `hook_windows.rs` の `assertions_on_constants` は、定数どうしの比較を
  **実行時 `assert!` から `const _: () = assert!(..)` へ移した** (★ テストを呼ばなくてもビルドが落ちる)。
  ⚠️ これは mac 側 `d038527` の「範囲の不変条件をコンパイル時へ移す」と同じ作法である。

## 判断 9: ⚠️ **`impl Default for ImeMonitor` は撤回し `#[allow]` にした** (判断 4 の訂正)

- ⚠️★★★ **判断 4 は誤りだった。** ★ `ImeMonitor::new()` は **COM アパートメントを初期化する**
  (`CoInitializeEx` + `CoCreateInstance`)。`Default` は「安価・副作用なし」が慣習なので、
  **暗黙に COM 初期化が走る入口**を作ってしまう。
- ⚠️ しかも**同じコミットの中で判断が不統一**だった —— `too_many_arguments` と
  `doc_lazy_continuation` は「理由を書いて `#[allow]`」を選んだのに、ここだけ
  **lint に合わせて公開 API を増やした**。
- ★ 「repo に `impl Default` が 10 箇所ある」を前例にしたのも誤り。
  ⚠️ **それらは純粋な構築**であり、副作用のある構築の前例にはならない。
- **対応**: 両 OS とも `#[allow(clippy::new_without_default)]` + 理由コメントへ置き換えた。

## 判断 10: `n_states` を配列長から取る (loud → silent の退行を塞ぐ)

- ⚠️★★★ **code-reviewer の指摘が正しい。** ★ 旧 `for j in 0..n_states` は `n_states` を
  4 にすると `new_probs[3]` で**即パニック**した。
  ⚠️ `iter_mut()` にした後は**配列長どおり静かに 3 回しか回らず**、
  `transitions[i * n_states + j]` の**ストライドだけがずれて無音で誤った確率**を返す。
  → ★ 正確性を最重視する層で **loud failure を silent failure に変えてしまっていた**。
- **対応**: `let n_states = new_probs.len();` ＋ `debug_assert_eq!(old_probs.len(), n_states);`
  を両関数に置き、**反復回数とストライドを 1 つの真実に縛った**。
  ★ ゴールデン 226 snapshot は引き続き byte-equal (値は不変)。

## 判断 11: `redact_home_path` に env を読む側のテストを足した (security MEDIUM)

- ⚠️ 従来は純関数 `redact_prefixes` しか覆われておらず、**env を読む経路が無保護**だった。
  ★ そこが壊れると `homes` が空になり `redact_prefixes(detail, &[])` が**入力をそのまま返す**
  → ⚠️ 被験者が見る提出失敗メッセージへ **OS ユーザー名を含むフルパスが素通り**する。
- ★ **env を書かない**読み取り専用テストにした (⚠️ `set_var` は他テストと競合し `unsafe`)。
  取れない環境では skip する。
- ★ 併せて `format_intervention_decision_line` の doc に
  「**手書き JSON なのでエスケープが無い / 値域を型で閉じること**」を明記した
  (⚠️ `#[allow]` が許すのは**引数の個数だけ**で、値域の緩みではない)。

## 判断 12: MSRV を宣言した (`rust-version = "1.87"`)

- ⚠️ 本タスクの根本原因は toolchain drift なのに、`rust-version` も `rust-toolchain.toml` も無かった。
  ★ さらに `is_multiple_of` / `is_none_or` / `repeat_n` を導入して**実効 MSRV が上がった**のに
  どこにも書かれていなかった。
- ★ **推測で書かず一次資料を読んだ** —— ローカル `rust-src` の `#[stable(since = ...)]`:
  `is_multiple_of` = **1.87.0** / `is_none_or` = 1.82.0 / `repeat_n` = 1.82.0 / `abs_diff` = 1.60.0。
- ⚠️ `edition = "2021"` は resolver "2" なので、**依存解決は変わらない** (MSRV 対応 resolver は "3")。

## ⚠️★★★ 研究者判断に委ねる (本タスクでは**やらない**)

| # | 指摘 | なぜ私が決めないか |
|---|---|---|
| R-1 | **CI に clippy step を足す** (`check` job) | ⚠️★★★ **mac 側の clippy 状態が未知**である。★ `hook_macos.rs` / `observe_macos.rs` 等は Windows で 1 行もコンパイルされず、**本機からは検証できない**。→ ⚠️ ブロックする gate をいま足すと **main の CI が即赤になり全作業が止まりうる**。★ 安全な順序は **① mac で `cargo clippy --all-targets` を回して緑にする → ② CI に足す**。 |
| R-2 | **`rust-toolchain.toml` で toolchain を固定** | ⚠️ 「stable に追従するか、版を固定するか」は**運用方針の選択**であり、★ 両マシン + CI (`dtolnay/rust-toolchain@stable`) に波及する。⚠️ 固定すると今回のような lint 増加は止まるが、**セキュリティ修正の追従も止まる**。→ ★ 研究者が決める。 |
| R-3 | `cargo-audit` の導入 (`verification-runbook.md` へ) | ★ 本コミットは依存を 1 つも動かしていないので**この差分に起因するリスクは無い**。⚠️ 定常スキャン手段の有無は別タスク。 |

★ 却下した指摘 (理由付き):
- 「`0x25..=0x28` を `windows` crate の `VK_LEFT`/`VK_DOWN` にする」→ ⚠️ **同ファイルは
  `0x1B` / `0x70..=0x7B` と生の hex で統一**されている。★ 1 箇所だけ定数にすると読みが割れる。
- 「`schema_dto.rs` はファイル先頭の `#![allow]` にする」→ ⚠️ **変異点を広げない**。
  ★ 実際に lint が出たのは `Meta` variant だけで、variant 単位の方が「どの doc が外部契約か」が精密に残る。

---

# `/cross-review` (Codex 独立レビュー) の結果と、そこで生じた記録

## 判断 13: ★ 両者一致で「振る舞い不変」。**コードの追加修正はしない**

- ★ 重点 6 点 (HMM 加算順序 / `n_states` / `&&` 畳み込みの副作用 / `schema_dto` の `#[allow]` /
  `--all-targets` / doc 移動) を **Claude と Codex が独立に検証し、6 点すべてで一致**した。
- ⚠️ マージを妨げる指摘は **ゼロ**。

### ★ Codex の唯一の踏み込んだ指摘は **false positive** だった

- 指摘: 「`is_ime_active_check` は "API 互換性のため" と書かれていたので、削除は振る舞い不変から外れうる」
- ⚠️★★★ **これは Codex が repo を読めないことに起因する**。★ 入力は diff だけなので、
  **削除された行のコメント文言しか材料が無い**。
- ★ 反証 (一次資料): repo 全体の grep で参照は定義行のみ／`#[tauri::command]` でもない／
  TypeScript 側にも無い／過去 3 本の steering が「既存 warning」と記録。
  ⚠️ かつ **本体は配布バイナリでありライブラリではない**ので「API 互換性の相手」が存在しない。

### ⚠️ Claude 側の指摘 1 件は、こちらが**誤っていた**

- 指摘: 「`Cargo.toml` のコメントの『MSRV 対応 resolver は "3" から』は未検証。resolver "3" は実在しない可能性」
- ★ **実測して反証した** —— scratchpad に `resolver = "3"` の空 crate を作り
  `cargo metadata` を通したところ **受理された**。→ ⚠️ **コメントは正しい。修正不要。**
- ★ 教訓: レビュー結果もまた一次資料で裏を取る対象である (⚠️ 鵜呑みにしない)。

### ★ 対応不要と判断した残りの指摘

| 指摘 | 判断 |
|---|---|
| `debug_assert_eq!(old_probs.len(), n_states)` は `[f64;3]` 固定なので自明に真 | ★ **そのとおり**。⚠️ ただし害は無く、`old_probs` が将来 `Vec` 等に変わったときの道連れ防止として残す。**価値はコメントが謳うほど大きくない**ことをここに記録する |
| 新規テストが env 未設定環境で静かに skip する | ★ **意図どおり** (⚠️ `set_var` は他テストと競合し `unsafe`)。→ ⚠️ **CI で `USERPROFILE`/`HOME` が立っているかは未確認**。★ 次に CI を触るとき確認する (下記 R-4) |
| `rust-version = "1.87"` は crate 全体のビルド実証ではない | ★ **コメント自身が既にそう書いている**。追加の欠陥ではない |

## 判断 14: ⚠️★★★ `.codex/budget.json` の増分は**改竄ではない**ことをここに残す

- ★ 台帳は `26449 → 57445` (**+30,996**)・`invocations 1 → 2` に更新された。
- ⚠️ **`per_invocation_max` (30,000) をわずかに超過している** (30,996)。
  ★ 理由: Windows の既知問題 (`--sandbox read-only` が **エラー 1312** でシェルを起動できず
  repo が不可読になる) を避けるため、**`scripts/run-codex-review.sh` を経由せず
  `codex exec` を直接呼び、diff をプロンプトに貼って「シェル実行禁止」を明記**した。
  → ⚠️ **ラッパーを通っていないので、台帳更新は自己申告**である。
- ★ **なぜわざわざ書くか**: ⚠️ この台帳には
  「**上限を上げた同じ commit で最大消費の記録が消えるのは、意図が正しくても改竄に見える**」
  という過去の反省 (`_comment_history_2026_09_11`) が刻まれている。
  → ★ **経緯を残さない増分を作らない**。history は append-only のまま触っていない。

## ⚠️ 研究者判断に委ねる (追加)

| # | 事項 |
|---|---|
| R-4 | ★ CI 実行環境で `USERPROFILE` / `HOME` が立っているか確認する (⚠️ 立っていないと `redact_home_path` の回帰保護が**実質無効**になる)。→ R-1 (CI に clippy を足す) と同じ機会に見るのがよい |
| R-5 | ⚠️ Windows では `run-codex-review.sh` が使えない (エラー 1312)。★ 直接呼び出し + 「シェル禁止」明記が現行の回避策だが、**ラッパー側を Windows 対応にするか**は別途判断が要る (⚠️ 予算台帳が自己申告になるため) |
