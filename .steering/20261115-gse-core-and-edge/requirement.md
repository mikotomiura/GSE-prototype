# GSE の研究の核と尖りを磨き直す（gse-core-and-edge）

## 背景

2026 年度未踏の不採択コメントの対応表（`docs/mitou_submission/review-response-2026.md`）で、次の 3 点が弱いと出た（引き継ぎ `.steering/_handoff/next-session-gse-core-and-edge.md` §1）。

1. 核を入れ替えたことの説明。PM は「推定の核を磨き上げた上で再挑戦」と書いた。今の答えは、推定では先回りできないと分かったので、見分けられる所と保留すべき所を本人の申告で実測する研究に移った、である。書き方を誤ると「難しい所から逃げた」と読まれる。
2. 一言で言える尖り。今の headline（`docs/research-positioning.md` §1.3）は長く、尖りとして読みにくい。
3. 新規性が組み合わせの水準にとどまる（同 §8）。

## ゴール

- 研究の核と尖りの一言を、読み手を問わない形で SSOT（新しい ADR と `docs/research-positioning.md`）に決める。位置づけが変わらなければ、変わらないことを記録する。
- そこから未踏の PM 向けの派生の素材（核を入れ替えた説明と尖りの一言）を `docs/mitou_submission/` に 1 本書き、attack-me（Codex を加える）で攻めさせる。
- `review-response-2026.md` の該当行を更新する。
- 最後に、位置づけが変わった所だけをプロジェクト概要のスライドに反映する。

## スコープ

### 含むもの
- 一言の候補を 3〜5 つ、根拠の ADR と実験つきで並べる。`/reimagine` で別案を独立に出して比べる。`codex-consult` に集計値と案だけを送る。
- 新しい ADR（ADR-054 の見込み）と `research-positioning.md` の改訂（ADR-053 の作法・旧版は docs/history/）。
- 未踏向けの派生の素材 1 本と attack-me。
- スライド（`docs/slides/project-overview/`）の差分の反映。

### 含まないもの
- 事前登録の値・L0 の項目の追加・H1 の判定/記述の直し（事前登録の値のタスク）。
- 段 1 の実施・手跡の実装・コード。
- 応募書類の提出版の改訂。
- AI を目標・主張・アウトカムに入れること。

## 受け入れ条件

- [ ] 一言の候補と比べ（/reimagine・codex-consult の結果を含む）が design.md にあり、採否を研究者が AskUserQuestion で決めた
- [ ] 決めた位置づけが新しい ADR に書かれ、`research-positioning.md` が合わせて直され、旧版が docs/history/ にある（変わらなければ、変わらないことの判断が decisions.md にある）
- [ ] 一言と説明に禁止用語（「詰まる前に」・3 状態の名前・「不便益 HCI である」・「〜は新しい」）が無い（grep で確かめる）
- [ ] 未踏向けの素材が `docs/mitou_submission/` にあり、attack-me の判定と対応が記録されている
- [ ] `review-response-2026.md` の「核」「尖り」の行が更新されている
- [ ] スライドは変わった所だけ更新し、`validate.py --original tpl.pptx` が通り、Keynote の PDF で全枚を目で見た（位置づけが変わらなければ触らない）
- [ ] /cross-review を通した

## 関連ドキュメント

- `docs/research-positioning.md`・`docs/mitou_submission/review-response-2026.md`
- ADR-045・047・048・052・053
- `docs/literature/20261105-abstention-and-observation-limits.md`・`docs/theory/README.md`

## 運用メモ
- /reimagine 適用: Yes
- 理由: 位置づけの判断で最良案が自明でない（研究者が 2026-11-15 に選択。codex-consult も使う）
