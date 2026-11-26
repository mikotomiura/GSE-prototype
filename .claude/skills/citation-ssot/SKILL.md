---
name: citation-ssot
description: >
  外部の理論・手法・文献を参照する文章 (research-positioning.md / functional-design.md /
  architecture.md / 実験 notes / 論文ドラフト) を書く・編集する時に必須参照。本文の該当箇所に
  inline [n] を付け、docs/references.md (中央書誌 SSOT) に append-only で登録する。採番は末尾の
  次番号、[n] は恒久 ID、削除は tombstone、番号の再利用禁止、重複防止キーは DOI/arXiv/正規化 URL、
  書誌未確定は provisional 状態。「設計理由を書く」「手法を引用する」「先行研究に言及する」
  「参考文献をまとめる」「References を作る」時に起動する。引用規約の SSOT は docs/references.md。
allowed-tools: Read, Edit, Grep
---

# Citation SSOT Discipline

## このスキルの目的
設計書・論文の主張に出典を機械的に紐づけ、参考文献を `docs/references.md` 一箇所に集約する。
「最後に References を手で並べる」のではなく、書きながら [n] を付け SSOT を append する。
本 skill は規約を再定義せず、`docs/references.md` の採番ルールを作業時に発火させる。

## 名前空間（GSE 固有・重要）
GSE の references.md は **2 つの局所書誌を名前空間付きで統合**している:
`[Pn]` = 提案の理論基盤書誌 / `[Vn]` = ユーザー検証 v0.4 の方法論書誌。
新規引用はどちらの名前空間かを選び `[Pn]`/`[Vn]` で付ける。両書誌に既出の文献は references.md の「重複」列で相互リンク済み。
append-only / 恒久 ID / renumber 禁止 / tombstone は**名前空間ごと**に守る。

## 主要なルール（SSOT: docs/references.md）
### ルール 1: 主張のたびに inline [Pn]/[Vn]
理論・手法・先行研究に依拠する記述には、その場で該当名前空間の [Pn]/[Vn] を付ける。

> ⚠️★★★ **ADR も対象である**（2026-09-13 追加）。★ 先例: `ADR-010 D5` は検出器の構造を
> conformal outlier testing [V66] に接地し、[V68] / [V69] / [V72] の制約を負っている。
> ⚠️ **実例（同日・ADR-030）**: 特徴量再設計と停滞検出を裁く ADR を **引用ゼロ件**で書き、
> 研究者の指摘で後から接地し直した。★ **「ADR は設計判断だから出典が要らない」は誤り** ——
> **外部の理論・手法・先行研究に依拠した瞬間に本 skill の対象になる。**
> → ★ **ADR で「文献が示す」「既存研究では」と書きそうになったら、先に `docs/references.md` を引く。**
### ルール 2: references.md は append-only
新規は該当名前空間の末尾の次番号。既存番号を renumber しない（inline 番号を安定させる）。

> ⚠️★★★ **例外は「*まだコミットしていない* 追加行を詰めるとき」だけである**（★ 公開された ID は動かさない）。
> ★ 実例: 2026-09-21 の S3 ラウンドで、`check_citations.py` が **key 重複 4 件**（既に登録済みの文献を再登録していた）を捕捉し、
> **未コミットのうちに新規行を落として採番を詰めた**（★ tombstone を作らずに済んだ）。
>
> ⚠️★★★ **そのとき、ID の付け替えは `references.md` の *本文中の参照* にも走らせること。**
> ★ 2026-09-21 に**ここを取りこぼした** —— カード / `_index.md` / `research-positioning.md` / `.steering/` には remap を走らせたのに、
> **`references.md` の備考欄に書いた `[Pn]` を remap の対象に入れ忘れ**、`[P417]` の本文が
> 「slow technology **[P414]**」（★ 正しくは **[P104]**）という**別文献を指す誤参照**になった。
> ⚠️ **`check_citations.py` はこれを拾えない** —— ★ 同スクリプトが見るのは
> **未登録参照 / 同一名前空間内の key 重複 / tombstone の引用 / 欠番**であって、
> **「その `[Pn]` が *意味的に正しい文献* を指しているか」は検査していない**（★ 登録さえされていれば通る）。
> → ★ **見つけたのは Codex の独立レビュー（`/cross-review`）である**（⚠️ Claude 側のレビュー 2 本はどちらも見落とした）。
>
> ★ **手順**: 採番を詰めたら、**remap の対象に `docs/references.md` を必ず含める**（★ カード / `_index.md` /
> `research-positioning.md` / `.steering/` だけでは足りない）。
> ⚠️★★★ **検算は *付け替えた直後* に行う** —— ★ `grep -rn '\[P<旧 ID>\]' docs/ .steering/` で残存ゼロを確かめる。
> ⚠️ **後回しにすると検算できなくなる**: ★ 空いた番号帯は**次のラウンドが再利用する**ので、
> 同じ `grep` が**正しい新しい行にヒットするようになり、旧 ID の残骸と区別が付かなくなる**
> （★ 2026-09-21 は実際にこうなり、**誤参照は grep では見つからず Codex の読解で見つかった**）。
### ルール 3: [n] は恒久 ID
表示順ではない。削除は行を残し tombstone（撤回）とし、番号を再利用しない。
枝ごとに番号の区画を持ち、後の区画の枝が先に main に入るときは、間の区画を `docs/references.md` の
「未マージの枝の番号の予約」の表に書く（2026-11-26・振り直さない）。枝が main に入ったら、区画が全部埋まれば
その予約の行を消し、一部なら残りに縮める。`check_citations.py` は予約の区画の欠番を違反にせず、
予約の区画に登録の行が残っていれば違反にする。
### ルール 4: 重複防止
DOI / arXiv ID / 正規化 URL を key にして二重登録を防ぐ。

**例外（2026-08-16 追加・研究者裁定）**: **同一文献から *別の主張* を引く場合は、同一名前空間内でも
別 ID を許す。ただし「重複」列で相互リンクすること**（例: `[V45]` = 本体の主張 ／ `[V51]` = 同論文の
観察的二次分析。key はどちらも `arXiv:2211.03622`）。
★ ルールの目的は **同じ主張の二重計上を防ぐこと**であって、1 論文 1 ID を守ること自体ではない。
⚠️ **相互リンクの無い同一 key は違反**（＝気付かずに二重登録した事故。`[P130]` がこの型で、
是正手段は tombstone）。→ ★ 機械検算は `python scripts/check_citations.py`。
### ルール 5: 書誌未確定は provisional
DOI/版/URL が未確認なら状態を `provisional` で登録し、確認後 `active` に上げる（捏造した URL を書かない）。
### ルール 6: 整合
本文の全 [n] が references.md に実在し、references.md の各 active 行に「使用箇所」がある。

## 良い例 / 悪い例
- ✅ 「提案は不便益 [1] を行動センシングへ拡張する」+ references.md に [1] が append 済み
- ❌ 本文に出典なしで主張し、最後にまとめて手で参考文献を貼る（SSOT 二重化 → drift）
- ❌ 既存 [2] を消して番号を詰める（inline [n] が全部ずれる）
- ❌ 未確認の DOI/URL をでっち上げる（provisional で登録し確認に回す）

## チェックリスト
- [ ] 外部根拠の各記述に [n] が付いているか
- [ ] [n] は末尾追加（renumber していない）か
- [ ] key（DOI/arXiv/URL）で重複していないか
- [ ] 本文の [n] が references.md に実在するか
- [ ] 書誌未確定は provisional にしたか（捏造していないか）

## 補足資料
- `examples.md` — 良い引用 / 悪い引用の具体例集

## 関連する他の Skill
- literature-card — 文献カード作成時に出典をここへ登録
- reproducibility-discipline — 実験 notes の借用手法 [n] 登録
- `/literature-review` — サーヴェイ 1 ラウンドを回すコマンド（Step 6 で本 skill を発火させる）
