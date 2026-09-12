# requirement — F-3 を足し、F-4 はやらない (★ 研究者裁定 2026-09-12)

## 背景

★ `next-session-followups-f1-f5.md` / `next-session-mac-default-clippy.md` の残件。
⚠️ **F-4 の前提 (mac の default features clippy = exit 0) は PR #199 で満たされている。**

## ★ 研究者裁定

| | 裁定 |
|---|---|
| **F-4** (CI に default features の clippy を足す) | ⚠️ **やらない** |
| **F-3** (`stop-check.sh` に `--features package`) | ★ **必要なら足す** → **足す** |

## ★ F-4 をやらない根拠 (PR #199 の実測)

⚠️ `cfg(not(feature = "package"))` は **repo 全体で 0 件**。
→ ★ **default スコープは `--features package` スコープの真部分集合**であり、
⚠️ **F-4 は既存 job の真部分集合を検査するだけでカバレッジを 1 mm も増やさない。**

⚠️★★★ **ただし「やらない」と決めた瞬間、この判断は検査されない前提の上に乗る。**
★ 不変条件が壊れる条件は **1 つだけ**: 誰かが `#[cfg(not(feature = "package"))]` を書く。
→ ★ **その 1 点を機械で守る** (= F-4 の代替)。⚠️ 守らないなら「やらない」は成立しない。

## ★ F-3 を足す根拠

⚠️ 現状の `stop-check.sh:22` は **default features** で回る:

```bash
cargo clippy --manifest-path "$MANIFEST" --quiet --all-targets -- -D warnings >/dev/null 2>&1
```

→ ⚠️★★★ **CI の真部分集合しか見ていない。** ★ CI の clippy は `ci.yml:590` の
`--all-targets --features package` **1 箇所だけ**である。
→ ⚠️ **`packaging.rs` / `reconcile.rs` / `gse-package` / `gse-unpack` / `gse-submit` は
ローカルで 1 度も lint されない** —— ★ これは**提出経路** (被験者データ・age 暗号化) そのもの。

★ しかも **2 回走らせる必要が無い**: default ⊂ package なので **scope を置き換えるだけ**。
⚠️ 実測コスト (mac・1 ファイル編集後): **4–5 秒 → 6 秒** = **+1〜2 秒**。

## ⚠️★★★ ただし F-3 は単独では価値が薄い

★ 現状の hook は失敗時に `>/dev/null 2>&1` で**中身を捨て**、`WARN` を 1 行出すだけ:

```
[stop] WARN: cargo clippy reported issues. Run 'cargo clippy --all-targets' to inspect.
```

→ ⚠️ **何が悪いか分からない WARN の範囲を広げても、払った時間に見合わない。**
★ **先に WARN を実用的にする** (= 指摘の先頭を出す) のが本丸である。

## ゴール (受け入れ条件)

1. ★ `stop-check.sh` の clippy が **`--features package`** で回る (= CI と同スコープ)。
2. ★ 失敗時に **実際の指摘が読める** (⚠️ 「issues があります」だけで終わらせない)。
3. ★ `cfg(not(feature = "package"))` の出現を **0 件に保つゲート**が機械で回る。
4. ⚠️ **ゲートに陽性対照がある** (★ 違反を仕込んだら赤くなることを実証する)。
5. ★ CI が両 OS で緑。

## スコープ外

- ⚠️ **CI に default features の clippy step を足さない** (= F-4 そのもの)。
- ⚠️ `stop-check.sh` を**ブロッキングにしない** (★ Stop hook の WARN という性格を変えない)。
- ⚠️ `HMM_VERSION` は bump しない (★ `analysis/` に触らない)。

## 運用メモ

- /reimagine 適用: **No**
- 理由: 裁定は研究者が下しており、実装は既存パターン (`scripts/check_*.py` ＋
  `scripts/tests/test_*.py`) をなぞるだけ。
