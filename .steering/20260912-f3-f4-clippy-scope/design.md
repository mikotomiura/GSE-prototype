# design — F-3 / F-4

## F-3: `stop-check.sh`

### ★ 変更 1: スコープを CI に合わせる (⚠️ 2 回走らせない)

```diff
- cargo clippy --manifest-path "$MANIFEST" --quiet --all-targets -- -D warnings
+ cargo clippy --manifest-path "$MANIFEST" --quiet --all-targets --features package -- -D warnings
```

★ default ⊂ package なので **置き換えで両方を覆う**。⚠️ 2 本走らせると倍かかるだけで無意味。

### ★ 変更 2: WARN を実用的にする (⚠️ こちらが本丸)

⚠️ 現状は `>/dev/null 2>&1` で捨てている。→ ★ **一時ファイルに受けて、失敗時に先頭を出す。**

- ⚠️ **出しすぎない**: Stop hook の出力なので **先頭の指摘だけ** (★ 目安 15 行)。
- ⚠️ **件数も出す**: ★ 「あと何件あるか」が分かると再現コマンドを打つ判断がつく。
- ⚠️ **再現コマンドを正確に出す**: ★ 現状の文言は `--features package` が抜けており、
  **打っても同じ結果にならない** (= 嘘の案内)。

## F-4: やらない ＋ 不変条件を機械で守る

### ★ `scripts/check_default_feature_subset.py`

⚠️★★★ **検査対象に検査パターンをリテラルで書かない。**
★ 本 repo は**同型の空回りを 2 回踏んでいる** (`gate-green-but-artifact-broken` ④)。
→ ★ パターンは**実行時に連結して作る**。

- 対象: `src-tauri/src` / `src-tauri/tests` / `src-tauri/build.rs` の `*.rs`
- 違反: `cfg(not(feature = "package"))` の出現 (★ 空白の揺れを正規表現で吸収)
- 出力: ⚠️ **見つけたら exit 1** ＋ **なぜ駄目か / どうすべきか**を説明する

### ★ `scripts/tests/test_check_default_feature_subset.py` (⚠️ 陽性対照が本体)

| 対照 | 期待 |
|---|---|
| ★ 違反を仕込んだ一時 repo | ⚠️ **exit 1** (★ 検出できること) |
| ★ 綺麗な一時 repo | ✅ exit 0 |
| ⚠️ 空白の揺れ (`cfg(not(feature="package"))` 等) | **exit 1** (★ 素通りさせない) |
| ⚠️ **対象ディレクトリが空 / 不在** | **exit 1** (★ 「0 件だから緑」で黙って通さない) |

⚠️★★★ **4 番目が肝**: ★ ファイルを 1 つも読まずに「違反 0 件」で緑になるのが
**最も危険な壊れ方**である (`silent-failure-in-guard-scripts` の `find <無いdir> | wc -l` 型)。

### ★ CI への配線

⚠️ **F-4 ではない** —— ★ 足すのは python 1 本 (実測 0.1 秒未満) であって clippy job ではない。
★ `ci.yml` の `check` job に step を 1 つ。
