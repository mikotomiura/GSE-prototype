# 設計

## 実装アプローチ

★ **「黙って間違う」経路を 3 つとも塞ぐ**。⚠️ 起票 23 が名指しするのは 1 つ目だけだが、
同じ関数の中に**同型の穴が 2 つ**ある（★ 一次で確認した）。

| # | 穴 | 現在の挙動 | ★ 是正後 |
|---|---|---|---|
| **1** | ★ **config をタスクと無関係に選ぶ**（`:57` の `tail -1`） | ⚠️ 名前順で最後の 1 つ。⚠️ **1 件でも黙って使う** | ★ **`--task` / `LOOP_TASK` で選ぶ**。⚠️ 無ければ **config が 1 件以上あれば die** |
| **2** | ⚠️ **`jq` の失敗を飲む**（`:59` の `2>/dev/null \|\| true`） | ⚠️ `jq` 不在 / 壊れた JSON / 不正な値 → **黙って `main` へ落ちる**（★ pin が無言で消える） | ★ **`jq` を使わない**（下記）。⚠️ **読めない・曖昧・不正なら die** |
| **3** | ⚠️ **解決結果が無人モードC で誰にも見えない** | ★ `:349` は stdout に 1 行出すが、⚠️ `loop-run.sh:436` が `2>/dev/null \| tail -1` で**パイプに吸わせて捨てる** | ★ **provenance ＋ default からの乖離**を **stderr** に出し、`loop-run.sh` が **run ログへ記録** |

### ★ 解決の優先順（⚠️ 変えるのは真ん中だけ）

```text
1. LOOP_BASE_BRANCH            ★ 従来どおり最優先。⚠️ config を読まない
2. --task / LOOP_TASK で選んだ config の base_branch     ← ★ ここを作る
   ⚠️ task 未指定 かつ config が 1 件以上 → die (fail-closed)
   ★ task 未指定 かつ config が 0 件     → 3 へ（従来どおり）
3. origin/HEAD                 ★ 従来どおり
4. main → master → 現 HEAD     ★ 従来どおり
```

⚠️★★★ **研究者裁定（2026-09-21・grill）**: **config が 1 件でも止める。**
★ 理由: 2026-09-21 に実測された事故（38 コミット前の枝）は **config が 1 件の状態で起きた**。
→ ⚠️ 「複数ヒットだけ止める」では**報告された事故そのものが直らない**。

### ⚠️★★★ `jq` を捨てる理由（★ 3 つある）

1. ★ **CI の性質を壊さない** —— `ci.yml:651` 逐語「本テストは **jq を要らない**」。
   ⚠️ `jq` を残すと AC1（pin が効く）のテストが `jq` を要求し、**この性質が壊れる**。
   ★ skip フラグで逃げる手は採らない（⚠️ memory「skip フラグの 3 状態テストが自己矛盾を隠した・**4 回再発**」）。
2. ⚠️ **macOS の self-hosted runner に `jq` があるか未検証**である（★ `ci.yml` が deny gate を
   macOS に配線していない理由として逐語で書いている）。→ ★ **`jq` 依存のままだと macOS の
   モードA で pin が無言で消える**（＝ 穴 2 が OS ごとに違う顔で残る）。
3. ★ 読む値は **git のブランチ名 1 つ**であり、config は **repo が `_template/loop-config.json` から
   生成する機械可読なファイル**である。→ ★ **狭い抽出器で足りる**（⚠️ 汎用 JSON パーサは要らない）。

### ⚠️★★★ 抽出器の罠（★ 一次で踏み抜いた。行頭アンカーにしてはならない）

★ **実測**: 既存 2 本のテスト（`loop-worktree-deny-test.sh:396` / `loop-run-guard-test.sh:154`）が
書く fake config の逐語は **1 行に 3 キーが同居**している:

```json
  "task": "stub", "mode": "C", "base_branch": "main",
```

→ ⚠️★★★ **`^[[:space:]]*"base_branch"` で引くと 1 件も当たらない。**
★ さらに悪いことに、⚠️ **fake repo の default ブランチは `main`** なので、
取り逃がして fallback に落ちても**結果が偶然一致し、テストは緑のまま穴が生きる**。
→ ★ **行頭に依存しない抽出**にし、⚠️ **「取り逃がし」を「値が無い」と混同しない**
（★ 下記のとおり **キーの出現数と値の出現数を別に数える**）。

### ★ 抽出器の契約（⚠️ 4 状態を区別する）

| キー出現 `n_key` | 値の形 `n_val` | ★ 扱い |
|---|---|---|
| **0** | — | ★ **キーが無い** → 未指定として fallback（⚠️ 従来と同じ・die しない） |
| **1** | **1** | ★ 値を採る（`null` なら未指定として fallback） |
| **1** | **0** | ⚠️★★★ **die** —— キーはあるが値が **`null` でも単純な文字列でもない**（★ 数値 / 配列 / エスケープ入り） |
| **2 以上** | — | ⚠️★★★ **die** —— ★ 入れ子に同名キーが足された等。**推測で 1 つ選ばない** |

★ 実装は **`awk` の `match()` を 1 行内でループ**させる（⚠️ `grep -o` の BRE alternation `\|` は
**BSD grep で移植性が無い**ため使わない。★ repo の既存コードも `awk` を多用している）。

### ★ 値の検証（⚠️ 既存には 1 つも無い）

★ 解決した base は **`git fetch --quiet origin "$base"`** と
**`git worktree add -b "$branch" "$wtdir" "$start"`** に**引数として流れる**。
→ ⚠️ 先頭が `-` の値は**オプションとして読まれうる**。★ 次を順に課す:

1. **先頭が `-` でない**
2. **文字集合 `[A-Za-z0-9._/-]` のみ**（⚠️ 空白・引用符・`$`・`;` を弾く）
3. **`..` を含まない / `/` で終わらない**
4. ★ **`git check-ref-format --branch "$v"` が 0 を返す**（⚠️ **git 自身に聞く** —— 1〜3 を先に通すので
   先頭 `-` が `check-ref-format` のオプションに化けることはない）

## 変更対象

### 修正するファイル

- `scripts/loop-spawn.sh` — ★ 本体
  - `:45` の `--no-exec` 単発判定を **先頭オプションの while ループ**へ（`--no-exec` / `--task <v>` / `--task=<v>`）。
    ⚠️ **`--cleanup` は従来どおり `$1` で効く**ように、ループはその判定の**前**に置く
    （★ `--cleanup` は `resolve_base` に到達しないので `--task` は使わない）。
  - `resolve_base()` を書き換え。⚠️ **戻り値を stdout で返すのをやめ**、
    グローバル `RESOLVED_BASE` / `RESOLVED_FROM`（provenance）に入れる
    （★ provenance を 2 値目として返す必要があるため。⚠️ stdout を 2 行にすると呼び出し側が壊れる）。
  - `json_top_value()` を新設（★ 上記の抽出器）。
  - `valid_refname()` を新設（★ 上記の検証）。
  - `find_task_config()` を新設（★ `--task` の解決。**ディレクトリ / 名前 / 日付付き名前**の 3 形）。
  - `:349` の 1 行 echo を **stderr の provenance ブロック**へ置き換え、
    ★ **default ブランチからの乖離**（`git rev-list --left-right --count <default>...<start>`）を併記。
- `scripts/loop-run.sh` — ★ モードC の配線
  - `:436` を `--task "$TASK_DIR"` を渡す形へ。
  - ⚠️ `2>/dev/null` をやめ、**stderr を一時ファイルへ受けて `log` で run ログに流す**
    （★ `log()` は `:16` 逐語 `echo "$PREFIX $*"`）。
- `scripts/loop-spawn-cleanup-test.sh` — ★ 回帰群の追加（下記テスト戦略）
- `.steering/_template/loop-config.README.md` — ★ `:97-100` の `base_branch` 節に解決順の変更を書く
- `docs/loop-engineering.md` — ★ `:113` の起動欄（モードA / モードC で `--task` が要ること）
- `.claude/commands/loop-issue.md` — ★ `:33` 逐語「`scripts/loop-spawn.sh <id>` の実行を案内して停止する」

### 新規作成するファイル

- ★ **無し**（⚠️ 受け皿は既にある。**新しいテストファイルを作らない** ——
  `scripts/check-tests-are-wired.sh` の対象が増えると CI 配線も増やす必要があり、
  ★ 起票 23 は既存の `loop-spawn-cleanup-test.sh` を受け皿に指名している）

### 削除するファイル

- 無し

## 影響範囲

| 呼び出し元 | 一次 | ★ 影響 |
|---|---|---|
| **モードC** `loop-run.sh:436` | ★ `TASK_DIR` を持っている | ⚠️ **`--task` を渡さないと die する**ので**必ず直す**（★ 本タスクで直す） |
| **モードA** 人間 | `loop-spawn.sh <id> [short]` | ⚠️ config がある状態では **`--task` が必須になる**（★ die メッセージが書き方を出す） |
| `loop-worktree-deny-test.sh:292` / `:319` | ★ 直接 `--no-exec 001 t` | ★ **影響なし** —— ⚠️ 一次で確認: `setup_fake_repo`（`:270-289`）は `scripts/` だけを作り **`.steering/` を作らない** → config 0 件 → 従来経路 |
| `loop-worktree-deny-test.sh:418` | ★ `loop-run.sh .steering/task` 経由 | ★ **loop-run.sh を直すので緑のまま**（⚠️ 直さないと赤くなる ＝ **配線の検査になっている**） |
| `loop-run-guard-test.sh:198` / `:204` | ★ `loop-run.sh .steering/task` 経由 | ★ 同上 |
| `loop-spawn-cleanup-test.sh` 既存 29 件 | ★ `setup_fake_repo` は `.steering/` を作らない | ★ **影響なし** |

⚠️★★★ **既存の `_loop-config.json` は書き換えない** —— ★ `20260914-mhd-feature-offline-tiers` の
`base_branch` は**完了済みの枝のまま残す**。⚠️ 本タスクの保証は「**黙って選ばない**」ことであって、
「古い pin を掃除すること」ではない（★ 掃除すると**テストの対象が消えて**しまう）。

## 既存パターンとの整合性

- ★ **`grep -q` をパイプ終端に置かない** —— ⚠️ `set -o pipefail` 下で上流に SIGPIPE が飛び、
  **一致したのに非 0** になりうる（★ `loop-spawn.sh:321` / `loop-spawn-cleanup-test.sh:82` に逐語で書いてある）。
  → ★ `grep -c` / `awk` で全部読ませる。
- ★ **`awk` で `exit` しない**（★ 同じ理屈。`loop-spawn.sh:31` 逐語）。
- ★ **stdout の最終行は worktree の絶対パス**（`--no-exec` の契約・`loop-run.sh:436` の `tail -1`）。
  → ⚠️ **新しい出力はすべて stderr**（★ `loop-worktree-deny.sh:37` 逐語「stdout は使わない」と同じ作法）。
- ★ **die で止めるときは「次に何をすればよいか」を書く**（★ `abort_worktree` の先例）。
- ★ **テストは実 repo に 1 バイトも触れない**（`mktemp` 配下の使い捨て git repo のみ）。

## テスト戦略

★ すべて `scripts/loop-spawn-cleanup-test.sh` に**群 7 として追加**する（⚠️ 既存 6 群の後）。
★ ⚠️ **`jq` を要らない性質を壊さない**（★ 本設計が `jq` を捨てるので、**むしろ強化される**）。

### 群 7: base の解決（★ 起票 23 の回帰）

| # | 何を | 期待 |
|---|---|---|
| 7a | config **0 件** ＋ `--task` なし | ★ 成功し、base が **`main`**（★ AC3・従来経路） |
| 7b | config **1 件** ＋ `--task` なし | ⚠️★★★ **非 0** で、出力に**候補パス**と **`--task`** と **`LOOP_BASE_BRANCH`** が出る（★ AC2・**本丸**） |
| 7c | config **2 件** ＋ `--task` なし | ⚠️ **非 0**・候補 **2 件**が出る |
| 7d | config 2 件 ＋ `--task <dir 名>` | ★ **指定した方**の `base_branch` から worktree が切られる（⚠️ `tail -1` が選ぶ方**ではない**） |
| 7e | `LOOP_TASK=<名>`（env） | ★ 7d と同じ結果 |
| 7f | `--task` と `LOOP_TASK` の両方 | ★ **`--task` が勝つ** |
| 7g | `--task <日付なしの素名>`（`20260101-foo` に対し `foo`） | ★ 当たる |
| 7h | `--task <存在しない名>` | ⚠️ **非 0** |
| 7i | `--task` が **2 つの dir に一致** | ⚠️ **非 0**・両候補が出る |
| 7j | `LOOP_BASE_BRANCH` ＋ config 1 件 ＋ `--task` なし | ★ **成功**し config を読まない（★ AC5） |
| 7k | ⚠️ **1 行に 3 キーが同居**した config（★ 既存テストと同じ形） | ★ `base_branch` が**正しく効く**（⚠️ **行頭アンカーの退行を殺す**） |
| 7l | `base_branch` が **`null`** | ★ 成功し `main` へ落ちる |
| 7m | `base_branch` キーが**無い** | ★ 成功し `main` へ落ちる（⚠️ die しない） |
| 7n | `base_branch` が **数値**（`123`） | ⚠️ **非 0**（★ n_key=1 / n_val=0） |
| 7o | `base_branch` が **2 回出る**（入れ子に同名キー） | ⚠️ **非 0** |
| 7p | `base_branch` が **`-foo`** | ⚠️ **非 0**（★ オプション混入） |
| 7q | `base_branch` が **`a b`**（空白入り） | ⚠️ **非 0** |
| 7r | ⚠️ **存在しないブランチ名**を pin | ⚠️ **非 0**（★ `git worktree add` が失敗する。**黙って `main` から切らない**） |
| 7s | 出力に **provenance と乖離**が出るか | ★ `provenance` 行と「**default (main) より N コミット後ろ**」が **stderr** に出る（★ AC7） |
| 7t | ⚠️ **stdout の最終行が worktree の絶対パス**のまま | ★ 契約が壊れていない（⚠️ `--no-exec` の最重要契約） |

### 群 8: 変異テスト（⚠️★★★ この検査が空振りしていないこと）

★ 既存の群 6 と同じ流儀で、**実装を殺したら赤くなるか**を見る。

| # | 変異 | 期待 |
|---|---|---|
| 8a | ★ **fail-closed を殺す**（`--task` 無しの die を `tail -1` に戻す） | ⚠️ **7b が緑になってしまう**ことを確認 → ★ **検査は空振りしていない** |
| 8b | ★ **抽出器を行頭アンカーに退行させる** | ⚠️ **7k が赤くなる**ことを確認（★ 上記の罠を本当に見ているか） |

⚠️★★★ **8b が最も重要である** —— ★ 7k だけでは、⚠️ 「fake repo の default が偶然 `main`」で
**緑のまま通る**恐れがある。→ ★ **7k は `base_branch` を `main` 以外の実在ブランチ**にして、
`main` と**区別できる形**で書く（★ でなければ 8b が赤くならない ＝ 7k が何も見ていない）。

### 通しで回すもの

```bash
bash scripts/loop-spawn-cleanup-test.sh          # ★ 本タスクの主対象（既存 29 + 新規）
bash scripts/loop-worktree-deny-test.sh          # ⚠️ loop-run.sh 経由の配線が生きているか
bash scripts/loop-run-guard-test.sh              # ⚠️ 同上
bash scripts/check-tests-are-wired.sh            # ★ 検査が CI に載っているか
```

⚠️ **Rust は 1 行も触らないので `cargo` は回さない**（★ `Cargo.toml` は `src-tauri/` にある）。

## ロールバック計画

- ★ 変更は **`scripts/` の 3 本 ＋ docs 4 本**に閉じており、⚠️ **Rust / TS / schema には触れない**。
- ★ 戻すなら `git revert <commit>` 1 本。⚠️ **`_loop-config.json` を書き換えていない**ので、
  戻した瞬間に旧挙動（`tail -1`）へ戻るだけで、**データの不整合は残らない**。
- ⚠️★★★ **戻したら起票 23 は開いたままになる** —— ★ ⑥（P1 前）を Loop で回す前に**必ず再度直す**。
