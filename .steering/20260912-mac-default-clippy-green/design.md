# design — mac default features clippy の検証

## アプローチ

⚠️★★★ **本タスクは「直す」タスクではなく「測る」タスクだった。** ★ 実測の結果
**指摘は 0 件・exit 0** だったため、手順 2 (指摘を直す) は**発生していない**。
→ ★ したがって設計上の主題は「**緑が本物であることをどう示すか**」に移った。

## ⚠️ なぜ「exit 0 でした」だけでは足りないか

★ 本 repo の既存教訓 (`silent-success-is-not-visible` / `gate-green-but-artifact-broken`)
に照らすと、**exit 0 には 2 通りの意味がありうる**:

| | 意味 |
|---|---|
| ✅ 本物 | clippy が全ターゲットを解析し、指摘が 1 件も無かった |
| ⚠️ 偽 | clippy が**何も解析しなかった** (キャッシュ / ターゲット不在 / 引数の空振り) |

★ 初回実行は **14 秒**で終わっており、⚠️ **キャッシュ由来の「何もしていない緑」と
見分けがつかない**。→ ★ **陽性対照で「解析している」ことを先に立証する**。

## 検証戦略 (★ 陽性対照つき)

1. **toolchain の同定**: `rustup show active-toolchain` が
   `1.98.1-aarch64-apple-darwin (overridden by rust-toolchain.toml)` であることを確認。
   ⚠️ どの版で緑なのかが分からない緑は根拠にならない。
2. **強制再解析**: `find src -name '*.rs' -exec touch {} +` 後に再実行し、
   出力に `Checking gse-next` が出ることを確認する (= キャッシュ返しでない)。
3. ⚠️★★★ **陽性対照 (本命)**: **全ターゲットに既知の違反を仕込み、全部が赤くなることを見る。**
   - 仕込む lint: `clippy::ptr_arg` (★ **既定 (style) の lint** なので `-D warnings` で必ず発火)。
   - ⚠️ **`-D warnings` を外して実行する** —— ★ 付けたままだと **lib で止まり bin/test に届かない**
     ので、「bin が解析された」ことを示せない (⚠️ 実際 pedantic 対照は **build.rs で止まった**)。
   - 対象は `cargo metadata` が列挙した **default features の全ターゲット** (7 個)。
4. **両スコープ**: default と `--features package` の**両方**で `-D warnings` 緑を確認 (退行防止)。
5. **挙動不変の証明**: `cargo test --features package --workspace` / ゴールデン byte-equal /
   `emit_schema` byte-equal。
6. **構造的な説明**: ⚠️ なぜ緑だったのかを `cfg(not(feature = "package"))` の**件数**で裏づける。

## テスト戦略

★ コード変更が 0 行なので「新規テスト」は無い。⚠️ 代わりに**測定器そのものを対照で校正**した。
→ 本タスクの成果物は **コードではなく証拠**である。
