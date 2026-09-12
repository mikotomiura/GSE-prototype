# decisions — F-3 / F-4

## 決定 1: ⚠️★★★ **F-4 (CI に default features の clippy を足す) は「やらない」**

**決定**: ★ 研究者裁定。⚠️ CI に default features の clippy step / job を**追加しない**。

**根拠** (PR #199 の実測):
⚠️ `cfg(not(feature = "package"))` は **repo 全体で 0 件**
→ ★ **default スコープは `--features package` スコープの真部分集合**
→ ⚠️ **F-4 は既存 job の真部分集合を検査するだけで、カバレッジを 1 mm も増やさない。**

★ 実際にかかるコスト側 (2026-09-12 実測):
- mac の `check` job は **5m45s〜6m22s**。⚠️ feature set が違うと成果物が別に積まれる。
- ⚠️ 開発クローンと self-hosted ランナーは**同一ディスク** (`/dev/disk3s5`)。
  ★ disk guard の threshold は 15 GiB で、⚠️ 実際にこの日 **14.1 GiB まで落ちていた**。

**⚠️ 検証**: `git grep "cargo clippy" .github/workflows/ci.yml` の結果が
`:446` (`--version`) と `:590` (`--features package`) の **2 行のみ**であることを確認した
(= ★ default clippy を**足していない**)。

---

## 決定 2: ⚠️★★★ **「やらない」を成立させるために、不変条件を機械で守る**

**決定**: `scripts/check_default_feature_subset.py` ＋ 対照テストを追加し、CI に配線した。

**理由**: ⚠️ **「やらない」と決めた瞬間、その判断は*検査されていない前提*の上に乗る。**
★ 不変条件が壊れる条件は **1 つだけ**: 誰かが `#[cfg(not(feature = "package"))]` を書く。
→ ⚠️ **人の記憶で守らない。** ★ 破れたら赤くする。
⚠️ コストは python 1 本 (**0.4 秒未満**) であって clippy job ではない (= F-4 ではない)。

**★ 破れたときの手順を検査器自身に書いた** (⚠️ 黙らせる方向へ行かせないため):
1. その `cfg` が本当に必要か問う (★ たいてい肯定形で書ける)
2. 必要なら **F-4 を実施する**
3. そのうえで対象から外す (★ 理由を添えて)

---

## 決定 3: ⚠️★★★ **陽性対照がゲートの穴を 1 つ見つけた**

**決定**: ★ 検出パターンを `cfg(` 直後限定から **`not(...)` 単位**へ広げた。

**何が起きたか**: ⚠️ 初版は `cfg\(\s*not\(` に限定していたため、
★ **`#[cfg(all(unix, not(feature = "package")))]` を素通り**させた
(⚠️ 対照 6 件中 1 件が `rc=0` で落ちて発覚)。
→ ★ 実在の違反を見逃す穴であり、⚠️ **実装より先に対照を書いていなければ気づけなかった。**

★ 現在の検出形 (**対照 6 件すべて rc=1**):

| 形 | 例 |
|---|---|
| 標準形 | `#[cfg(not(feature = "package"))]` |
| 空白なし / 過多 | `#[cfg(not(feature="package"))]` 等 |
| `all(..)` の入れ子 | `#[cfg(all(unix, not(feature = "package")))]` |
| `any(..)` の入れ子 | `#[cfg(any(test, not(feature = "package")))]` |
| `not(all(..))` 形 | `#[cfg(not(all(feature = "package", unix)))]` |

⚠️★★★ **既知の限界を出力に明記した** (★ 「全部見ている」と誤解させない):
**複数行に跨る cfg** / **`cfg_attr` やマクロ経由で組み立てられた cfg** は**検出できない**。
→ ★ 本検査は「うっかり」を止めるものであって**証明ではない**。

---

## 決定 4: ⚠️★★★ **空振り対照を入れた (★ 最も危険な壊れ方)**

**決定**: ★ 走査ファイル数が **0 なら exit 2** で落とす。対照でも実証した。

**理由**: ⚠️ パスを間違えた / 対象が消えた場合に「違反 0 件」で**黙って緑**になるのが
**最も危険**である (★ `silent-failure-in-guard-scripts` の `find <無いdir> | wc -l` 型)。
→ ★ 実 repo に対する対照でも「**走査数 > 10**」を要求している。

---

## 決定 5: ★ **F-3 は「必要」と判断して足した**

**決定**: `stop-check.sh` の clippy を **`--features package`** に**置き換えた**。

**必要性の判断** (⚠️ 研究者が私に委ねた部分):
★ ローカル hook は **CI の真部分集合**しか見ておらず、
⚠️ **`packaging.rs` / `reconcile.rs` / `gse-package` / `gse-unpack` / `gse-submit` は
ローカルで 1 度も lint されていなかった** —— ★ これは**提出経路**
(被験者データ・age 暗号化) そのものである。
→ ★ 気づくのが CI (mac 5m45s / Windows 4m37s の往復) では遅い。

**★ 「足す」ではなく「置き換える」**: ⚠️ default ⊂ package なので **2 本走らせる意味が無い**。
★ 実測コスト (mac・1 ファイル編集後): **4–5 秒 → 6 秒 = +1〜2 秒**。

---

## 決定 6: ⚠️★★★ **F-3 の本丸は scope ではなく「出力を捨てないこと」だった**

**決定**: ★ 失敗時に **指摘の先頭 15 行 ＋ 延べ件数 ＋ そのまま打てる再現コマンド**を出す。

**理由**: ⚠️ 旧版は `>/dev/null 2>&1` で中身を捨て、こう言うだけだった:

```
[stop] WARN: cargo clippy reported issues. Run 'cargo clippy --all-targets' to inspect.
```

→ ⚠️ **何が悪いか分からない WARN の scope だけ広げても、払った +2 秒に見合わない。**
★ しかも ⚠️ **案内されたコマンドは `--features package` が抜けており、
打っても同じ結果にならなかった** (= 嘘の案内)。

**⚠️ 件数表示でも 1 度間違えた**: ★ 陽性対照で **1 件の指摘が「4 件」と表示**された。
原因は `grep -c '^error'` が **末尾の集計行 `error: could not compile ...` も数えていた**こと。
→ ★ 集計行を除外し、⚠️ `--all-targets` では **lib と lib-test が別ユニットなので
同じ指摘が複数回出る**ことを「**延べ**」と明記した (★ 実測 2 件)。

---

## 決定 7: ★ `stop-check.sh` をブロッキングにはしない

**決定**: ⚠️ WARN のまま。`exit 1` にしない。

**理由**: ★ Stop hook は「気づかせる」層であり、⚠️ ブロックする層は **CI** である
(★ 役割を混ぜると、hook が落ちたときに作業が止まる)。
→ ★ 今回やったのは「**WARN を読む価値のあるものにする**」ことである。

## 検証

| 検査 | 結果 |
|---|---|
| ★ F-3 陽性対照 (`reconcile.rs` = **package 専用**に違反を仕込む) | ✅ **検出**・指摘の中身が出た (⚠️ default では解析されない場所) |
| ★ F-3 陰性対照 (綺麗な状態) | ✅ **何も出ない** |
| ★ F-3 件数 | ✅ **2 件 (延べ)** = lib + lib-test で正確 |
| ★ F-4 ゲート対照 (違反 6 形) | ✅ **6/6 検出** |
| ★ F-4 ゲート陰性対照 | ✅ 肯定形 cfg / 別 feature / target_os は緑 |
| ⚠️ F-4 ゲート空振り対照 | ✅ 対象不在は **exit 2** (★ 緑にしない) |
| ★ F-4 ゲート 実 repo | ✅ **0 件 (59 ファイル走査)** |
| `cargo fmt --check` | ✅ EXIT=0 |
| clippy 両スコープ | ✅ EXIT=0 |
| `cargo test --features package --workspace` | ✅ **705 passed / 0 failed** |
| ゴールデン / schema | ✅ byte-equal |
| `analysis/` 差分 | ✅ 無し (⚠️ `HMM_VERSION` 据え置き) |
| ⚠️ CI に default clippy を足していないこと | ✅ `cargo clippy` は `:446` と `:590` の 2 行のみ |
| `ci.yml` YAML 妥当性 | ✅ パース OK・step 2 本が `frontend-check` に入った |
