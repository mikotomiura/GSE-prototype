# design — `.idea` §7 の未決事項 8 件を裁く

## アプローチ

★ **「裁く」の前に「問いを立て直す」** —— `conflict-audit.md` F7–F10 とメイン自身の再実測により、
8 件のうち複数は **既決** か **問いの前提が崩れている**。したがって各件を次の 3 分類に落としてから裁く。

| 分類 | 扱い |
|---|---|
| **(a) 既決** | 出所 ADR を明示して閉じる。★ **蒸し返さない** |
| **(b) 問いの再定義が要る** | 既決事項に照らして問いを書き直し、書き直した問いを裁く |
| **(c) 真に未決** | サーヴェイ ＋ 一次照合で裁く。埋まらないものは **ADR-021 の Open questions** へ送る |

## 変更対象

| ファイル | 変更 |
|---|---|
| `docs/adr/ADR-021-*.md` | ★ **新規**（本タスクの主成果） |
| `docs/adr/README.md` | 一覧に ADR-021 を追加。⚠️ ADR-019 の行に呼称改訂の注記 |
| `docs/architecture/expression-channel.md` | ★ **層 A の設計要件**（§3 拡張）／`level` 契約の改訂（§2.1）／出口の面（§6）／§8 の空白表を更新 |
| `docs/references.md` | 新規引用を append（★ 次番 `[P239]` / `[V112]`・**実測済み**） |
| `docs/glossary.md` | ★ 層 A / 層 B・招待・モデル成熟の呼称 |
| `docs/preregistration-v0.3.md` | ⚠️ **addendum ブロックに注記 1 段落のみ**（★ 本文は変えない・研究者判断） |
| `docs/mitou_submission/**` | ⚠️ モデル成熟の呼称変更に伴う 2 箇所 ＋ 再生成 |

## テスト戦略

★ 本タスクは**コード変更ゼロ**（表現チャネルは未実装）。検証は次の 4 本。

```bash
PYTHONUTF8=1 python scripts/check_citations.py     # 未登録参照 / 欠番 / tombstone / 相互リンク無し
PYTHONUTF8=1 python scripts/check_doc_lexicon.py   # 提出 5 本の禁止記号・禁止用語
# 提出資料を触ったら再生成（★ 出力は再現可能・内容が同じなら差分ゼロ）
for f in docs/mitou_submission/mitou_docs/*.docx.md; do
  PYTHONUTF8=1 python scripts/md2docx.py "$f" "${f%.md}" --unescape; done
for f in docs/mitou_submission/mitou_pptx/*.pptx.md; do
  PYTHONUTF8=1 python scripts/md2pptx.py "$f" "${f%.md}" --unescape; done
```
★ 最後に `/cross-review` を**パス限定**で（⚠️ `.docx` / `.pptx` を含めると Step 2 が fail-closed する）:
`-- docs scripts ':!*.docx' ':!*.pptx'`

## サーヴェイの委譲（★ 全 7 系統をサブエージェント並列・メインは append のみ直列）

| 系統 | angle | 主に埋める未決 |
|---|---|---|
| A | 媒体の置き場所（ロック / ホーム / 専用アプリ） | #1 |
| B | 他者可視性・THAT/WHAT/HOW の段 | #2（PS-Q5） |
| C | 抽象表現の個人化（固定 / 可変の境界） | #3 |
| D | 招待を差し出す面と framing（自律性支援の言語） | #5 / #6 |
| E | ≤4 秒の可読性（glanceability） | ★ **§4.3 の層 A の穴** |
| F | 可読性・俯瞰・自律性の最小プロトコル | #8 |
| G | ★ **繰り越し 2**: `[P219]`–`[P238]` / `[V89]`–`[V111]` の逐語照合 | （品質保証） |

⚠️ 全系統に **前回の 5 件の誤りの型**（タイトル実在しない / 著者欠落 / 主題が別物 / 測っていない
アウトカム / **abstract が本文より誇張**）を明示し、**Crossref raw JSON での DOI 検算**と
**英語逐語の取得**、**GSE に不利な数値・著者留保の併記**を必須にした。
