# public-data-findings-paper

## 背景

GSE 本体の研究（段 1・段 2）とは別に、既に公開データ（CoAuthor・KLiCKe・CS1）で得た知見を先に論文にする。倫理審査も段 1 も待たない。出発点は `.steering/_handoff/next-session-gse-public-data-findings-paper.md`（2026-11-05）。

中身は 2 つ。

1. 打鍵の観測で作業の停滞の手前を先取りできるか（反証）。手前 30 秒の推定の上がりは AUC 0.49〜0.52。代理のラベルは道具を使った出来事で、詰まりではない。小さい効果（0.53〜0.58 程度）は否定できない。
   - （2026-11-06 追記・判断 32。背景は着手時の記録として残す）現在の論文 1 は、事前登録した同等の確認（陰性の結果）で、「反証」の語は使わない。ラベルは停滞（文字の入力が 30 秒以上止まること）、幅は [0.45, 0.55]、推定器（HMM_VERSION 0.5.0・このデータで推定していない係数・この入力の写し方で動かす）（データからは推定していない）。外枠は `paper-write/outline.md` v6。
2. 停滞の形（記述と方法の知見）。停滞は短く、ありふれていて、手の操作を含む。前が沈黙だけの停滞は長引く。日の揺れは数え上げの見込みの 2〜3 倍。推定の水準はデータで桁が違う。受領は経路しだいで計れない。

## ゴール

この段（タスクの前半）のゴール:

- 新規性の文献のラウンド（Q1〜Q4）を回し、カードと出典の登録を終える。
- その結果をもとに、論文を 1 本にまとめるか 2 本に分けるかを研究者が決める（AskUserQuestion）。
- 誰に読ませて何を変えたいか（paper-write Step 0）を確定し、主張と新規性を確定する。主張の確定の段で /reimagine を使う。

後半（本数・主張の確定の後）: 濃くする道（引き継ぎ §4）のどれを足すかを決め、足すなら事前登録を OSF で凍結してから回す。草稿は MacTeX。

## スコープ

### 含むもの
- 文献のラウンド（`/literature-review`）・カード・`docs/references.md` への登録
- 本数・読者・主張・新規性の確定
- 濃くする道の選択と、足すものの事前登録の草案

### 含まないもの
- 1 人ごとに学ぶ効きの知見（論文 3。τ の試験の結果の後）
- 公開データでの照合（打鍵の記録の加工の効き目。IME 論文の次の論文）
- GSE の段 1 の主張の先取り（段 1 の C4 のデータは無い）
- O1（研究者本人の記録）の利用（既定は使わない。使うかは研究者に聞く）

## 受け入れ条件

- [ ] Q1〜Q4 のカードが `docs/literature/` にあり、`python3 scripts/check_citations.py` が違反なしで終わる
- [ ] ラウンドを単独でコミットした
- [ ] 本数の判断が decisions.md に記録されている
- [ ] 読者と変えたいこと・主張・新規性が decisions.md に記録されている（/reimagine の比べを含む）

## 関連ドキュメント

- `.steering/_handoff/next-session-gse-public-data-findings-paper.md`
- `experiments/20261031-coauthor-pre-request-signal/` ほか（引き継ぎ §2）
- `docs/adr/` ADR-030（停滞の定義）・ADR-047（位置づけの言い方）・ADR-039（O1 の扱い）
- `docs/literature/20260815-silence-discrimination-pause-semantics.md`・`20260919-resumption-restop-and-bout-segmentation.md`・`20260903-japanese-ime-keystroke-gap.md`・`20260816-ai-escape-moment-and-friction.md`

## 運用メモ
- /reimagine 適用: Yes
- 理由: 研究者の選択（2026-11-05）。主張と新規性を確定する段（paper-write Step 0 の後）で初回案を破棄して作り直し、比べる。
