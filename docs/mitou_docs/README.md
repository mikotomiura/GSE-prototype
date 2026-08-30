# 未踏提出文書（2027 年度版）

## ⚠️★★★ どれが正本か

| ファイル | 役割 |
|---|---|
| `*.docx.md` | ★★★ **正本（source of truth）。編集はこちらだけを触る** |
| `*.docx` | ⚠️ **生成物。`scripts/md2docx.py` が MD から作る。直接編集しない** |

⚠️★★★ **`.docx` を直接編集しても MD へ戻す経路は無い。**★ 次に再生成した瞬間に黙って消える。

## 再生成

```bash
cd <repo root>
for f in docs/mitou_docs/*.docx.md; do
  PYTHONUTF8=1 python scripts/md2docx.py "$f" "${f%.md}" --unescape
done
```

⚠️ Windows コンソールは cp932 なので **`PYTHONUTF8=1`** を付ける。
⚠️ 本機に `pandoc` は無い（2026-08-30 実測）。変換は `scripts/md2docx.py`（標準ライブラリのみ・
G1 の配布資材と共用）である。

★ **`--unescape` は必須**（★ 付けないと見出しが `1\. なにをつくるか` のように出る）。
⚠️ このフラグは **opt-in にしてある** —— G1 側の markdown はコードブロック内に
`\n` / `\g` / `\<` 等を含んでおり、無条件に外すと壊れるためである。

★ 変換で写しているのは **見出し / 段落 / 箇条書き / 番号付き / 表 / 引用 / 水平線 / コードブロック**、
インラインは **太字 / `コード` / *斜体***。⚠️ **`[text](url)` 記法は写せない**ので、
本文中の URL は**素の URL で書く**こと（★ 現状の 2 文書はそうなっている）。
⚠️ **体裁の最終調整は Word 側で行う前提**である。

## ★ 主張の SSOT との関係

⚠️★★★ **本ディレクトリの文書は主張の SSOT ではない。**★ 主張の正は以下であり、
**未踏文書がこれらと食い違ってはならない**:

| SSOT | 何の正か |
|---|---|
| `docs/research-positioning.md` | ★ 研究の問い・差分・主張範囲 |
| `docs/adr/ADR-015-wall-removal.md` | ⚠️ Lv2 Wall / Zen Timer / Monk Mode の全削除 |
| `docs/adr/ADR-017-expression-channel-boundary.md` | ★ 表現チャネルの境界 / 身体活動センシングの恒久除外 |
| `docs/preregistration-v0.3.md` | ⚠️ 凍結された合否契約（PreReg-1〜8 / GATE1–3） |
| `docs/glossary.md` | ⚠️ **禁止用語** |

★ **文献番号は 2 文書それぞれの独自体系**であり、`docs/references.md` の `[Pn]` / `[Vn]` とは別である。
⚠️ **未踏文書の中で番号を振り直しても `references.md` は動かさない**（`citation-ssot` の規約）。
★ ただし **2 文書は同時に提出するので、同じ番号が別の文献を指さないように揃えてある**
（★ 技術設計書側の 36〜38 番・50 番が欠番なのはそのためである）。

## ★ 改訂の記録

| 版 | 記録 |
|---|---|
| **2027 年度版** | `.steering/20260830-mitou-2027-rewrite/`（★ 何を降ろし何を足したかは `decisions.md`） |
| 2026 年度版 | ⚠️ **git には無い**（★ 研究者決定・同 `decisions.md` D3）。原本 `.docx` は研究者の手元 |
