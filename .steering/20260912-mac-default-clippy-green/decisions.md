# decisions — mac default features clippy

## 決定 1: ⚠️★★★ **mac の default features clippy は「直す対象が 0 件」だった**

**決定**: ★ `cd src-tauri && cargo clippy --all-targets -- -D warnings` は **exit 0**。
**コード変更は 0 行**。→ ★ **F-4 の着手条件は満たされた。**

**実測** (2026-09-12・MacBook Air (aarch64)・clippy 0.1.98 / cargo 1.98.1):

| 検査 | 結果 |
|---|---|
| `rustup show active-toolchain` | `1.98.1-aarch64-apple-darwin (overridden by '/Users/johnd/GSE-prototype/rust-toolchain.toml')` ★ 期待通り |
| `cargo clippy --all-targets -- -D warnings` (**default**) | ✅ **EXIT=0** |
| `cargo clippy --all-targets --features package -- -D warnings` (CI と同じ) | ✅ **EXIT=0** (退行なし) |
| `cargo test --features package --workspace` | ✅ **EXIT=0** / **11 スイート・705 件** passed, 0 failed |
| `gse-replay --snapshot` | ✅ `OK: 15 snapshots match` |
| `emit_schema` vs `schema/current.json` | ✅ **byte-equal** |
| 作業ツリー | ✅ `git status --porcelain` 空 (★ ゴールデンを書き換えていない) |

**理由**: ⚠️ **予想が外れた。** ★ handoff メモは「mac で新しい lint が出るかもしれない」を
前提に書かれていたが、⚠️ **1 件も出なかった**。→ 決定 2 がその理由である。

**却下案**: ★ 「exit 0 だったのでそのまま報告する」 → ⚠️ **却下**。
初回実行が **14 秒**で終わっており、キャッシュ由来の「何もしていない緑」と区別がつかない。
→ ★ 決定 3 の陽性対照を先に通した。

---

## 決定 2: ★ 緑だったのは偶然ではなく **構造的に保証されていた**

**決定**: ⚠️★★★ **default スコープは `--features package` スコープの真部分集合である。**
→ ★ **package が緑なら default も緑**であり、mac の default が緑だったのは必然だった。

**根拠 (実測)**:

- ★ `grep -rn 'not(feature *= *"package")' src-tauri/src src-tauri/tests src-tauri/build.rs`
  → ⚠️ **0 件**。= **default のときだけコンパイルされるコードが 1 行も無い。**
- ★ `package` feature が足すのは `#[cfg(feature = "package")]` のコードと、
  `required-features = ["package"]` の bin **3 本** (`gse-package` / `gse-unpack` / `gse-submit`) のみ。
- ★ mac は host = `aarch64-apple-darwin` なので、
  ⚠️ **`--target aarch64-apple-darwin` を付けても付けなくても同一**
  (= mac セッションが 2026-09-12 に測った形と host target が一致している)。

**⚠️ だから F-4 の費用対効果は低い** (★ ただし**判断は研究者**であり、ここでは材料だけ置く):
- ★ CI に default features の clippy を足しても、**検査する集合は既存 job の真部分集合**になる。
- ⚠️ **例外が生じる条件は 1 つだけ**: 誰かが `#[cfg(not(feature = "package"))]` を書いた瞬間、
  この保証は消える。→ ★ **F-4 を「やらない」と決めるなら、その条件を検査する方が安い**
  (例: `cfg(not(feature = "package"))` の出現を 0 件に保つ grep ゲート)。

**却下案**: ★ 「真部分集合だから F-4 は不要」と**私が決める** → ⚠️ **却下**。
handoff 手順 4 が「CI には足さない・F-4 は Windows 側の仕事」と明記しており、
★ **スコープ外の判断を先回りしない**。材料の提示に留める。

---

## 決定 3: ⚠️★★★ **陽性対照は `-D warnings` を外して打つ**

**決定**: ★ 全ターゲットに `clippy::ptr_arg` 違反を仕込み、**`-D warnings` 無し**で実行して
**7/7 ターゲットで検出されること**を確認した。→ ★ 「clippy が全ターゲットを解析している」ことの立証。

**実測**:

```
検出されたターゲット (7/7):
  src/lib.rs                    src/main.rs
  src/bin/cohort.rs             src/bin/emit_schema.rs
  src/bin/replay.rs             tests/applog_subscriber.rs
  tests/macos_hook_rehook.rs
clippy::ptr_arg 警告総数: 7 (期待 7)
復元後 git status: 空 (完全復元)
```

**理由**: ⚠️★★★ **`-D warnings` を付けたままだと対照が空振りする。**
★ clippy は **lib が落ちた時点で止まる**ので、lib の対照しか見えず
「bin と test も解析された」ことを**示せない**。
→ ⚠️ **実際に踏んだ**: 最初に打った `-W clippy::pedantic -D warnings` の対照は
**build.rs で止まり** (`semicolon_if_nothing_returned`)、lib にすら到達しなかった。
★ これは handoff メモが警告していた「29 件と見えたものが 51 件になった」現象と同じ構造である。

**却下案**:
- ★ `-D clippy::pedantic` を対照にする → ⚠️ **却下**。build.rs で止まり射程が足りない。
- ★ lib にだけ違反を仕込む → ⚠️ **却下**。bin/test が解析された証拠にならない。

---

## 決定 4: ⚠️ **zsh の語分割で対照が空振りし、偽の緑を出した** (★ 自分の測定器の欠陥)

**決定**: ★ 対照スクリプトは **`bash -c` で明示実行**する。

**何が起きたか**: ★ `for f in $TARGETS; do ... done` を **zsh** で回したところ、
⚠️ **zsh は未クォート変数を語分割しない**ので `$TARGETS` が **1 個のファイル名**として扱われ、
`cp` が全滅した。⚠️★★★ **その結果 `EXIT=0` / `ptr_arg 警告 0 件` が出た** ——
★ これは **「対照が 1 つも仕込まれなかった」のに「緑」に見える**状態であり、
⚠️ **実在の欠陥と見分けがつかない偽陰性**である。

**★ 何が救ったか**: `cp` のエラー行を**捨てずに表示していた**こと。
→ ⚠️ `2>/dev/null` で黙らせていたら、**対照が通ったと誤報告していた**。

**再発防止**: ★ 対照には**必ず件数の期待値を添える**
(`バックアップ数: 7 (期待 7)` / `変更ファイル数: 7 (期待 7)` / `警告総数: 7 (期待 7)`)。
⚠️ **exit code だけを見ない。**

★ 既存 memory の `macos-default-tools-break-gates` / `measurement-instrument-false-positives`
と同型 (⚠️ 前者は bash 3.2、本件は **zsh** という別の shell 差)。

---

## 決定 5: ★ F-3 の判断材料 — mac の clippy コスト (⚠️ 判断はしない)

**実測** (★ 1 ファイル編集後 = Stop hook の実条件):

| 条件 | default | `--features package` | 増分 |
|---|---|---|---|
| ★ **mac** (本機・aarch64) | **4–5 秒** | **6 秒** | ⚠️ **+1〜2 秒** |
| ★ Windows (G-GEAR・既報) | 10 秒 | 14 秒 | +4 秒 |
| (参考) 完全キャッシュ時 | 0 秒 | 1 秒 | +1 秒 |
| (参考) `lib.rs` 編集後 = 最悪ケース | 5 秒 | 6 秒 | +1 秒 |

→ ★ **mac では F-3 のコストは Windows の半分以下**。⚠️ ただし**判断は研究者**。

⚠️★★★ **warm 値 (0 秒) を根拠にしないこと** —— ★ Stop hook が発火するのは
**編集した直後**なので、意味のある数字は「1 ファイル編集後」である。

---

## 決定 6: ★ `stop-check.sh` が出力を捨てている件 (⚠️ メモの主張を検算した)

**決定**: ★ handoff メモの記述は**正しい**。実測で確認した:

```
.claude/hooks/stop-check.sh:22
  if ! cargo clippy --manifest-path "$MANIFEST" --quiet --all-targets -- -D warnings >/dev/null 2>&1; then
.claude/hooks/stop-check.sh:23
      echo "[stop] WARN: cargo clippy reported issues. Run 'cargo clippy --all-targets' to inspect."
```

→ ⚠️ **default features で回ってはいるが、`>/dev/null 2>&1` で中身が見えず、WARN でブロックもしない。**
★ 本タスクの時点では**捨てていた出力の中身が空だった**ことが確認できた
(= 現状 mac で WARN は出ない)。
