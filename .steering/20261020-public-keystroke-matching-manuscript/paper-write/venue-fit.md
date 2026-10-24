# Step 0: 投稿先の適合（PoPETs 2027・Issue 3）

取得 2026-10-24（`curl -sL`。止められなかった）。原文は scratchpad に置き、repo には入れない。

## 目的（誰に読ませ、何を変えたいか）

- 読者: 打鍵の記録を公開する側（作文・プログラミングの過程のコーパスを出す研究者・データの管理者）と、PETs の研究者（加工の評価の仕方）。
- 変えたいこと: 公開する側が、どの列を残し、時刻と長さをどこまで粗くし、全体か一部かを選ぶときの材料（outline.md「What a releasing party takes away」）。
- 投稿先の選定はこのタスクの外（`docs/public-keystroke-matching-venue-plan` の枝）。ここでは選び直さない。

## 規程（原文の逐語）

出典: <https://petsymposium.org/authors-2027.php>（"Note: This information applies to PoPETs 2027 and later."）、<https://petsymposium.org/cfp27.php>。
（引き継ぎにあった `cfp-2027.php` は 404。CFP は `cfp27.php`。）

- 頁の上限: "Submissions and resubmissions to PoPETs must consist of at most 12 typeset pages for the main body of the paper."
  "submissions exceeding 12 typeset pages for the main body of the paper will be automatically desk-rejected without consideration of appeal."
- 数えない範囲: "The main body excludes the three mandatory sections per the 2027 template (ethical considerations, open science, and AI use) as well as any acknowledgements, the bibliography, and any clearly-marked appendices contained in the submission."
  "There is no page limit for the three mandatory final sections ..., acknowledgements, bibliography, and clearly-marked appendices."
- 付録: "appendices should only be used to provide supplementary information that falls outside of the stated contribution of the paper or to provide extended details that would not be of interest to most readers. The paper should be complete and self-contained without appendices. PC members are not required to read the appendices during review."
  → outline.md の「読む義務はない」は原文どおり。加えて「主張の外の補足」か「多くの読者に関心のない細部の延長」に限る、という条件がある（outline.md に無かった）。
- 詰め込みの禁止: "Authors should not attempt to "squeeze space" by exploiting underspecified formatting criteria ... Authors should seek to meet page limits through the modification of content alone."
- 1 頁目: "The paper should start with the title and an abstract. The first page must clearly state how the work is relevant to real-world privacy applications. The introduction should give some background and summarize the contributions of the paper at a level appropriate for a non-specialist reader."
- 範囲（CFP・2027 で改めた）: "The core contribution must be relevant to real-world privacy applications." "Relevance to real-world privacy applications must also be present throughout the entire paper by dedicating a substantial portion of the submission to work that is traditionally considered practical or applied." "Papers with empirical evaluations must show a clear connection to privacy and to real-world applications." "Papers that treat privacy as a superficial application domain (e.g., if the only relationship to privacy is a privacy-related dataset) ... are therefore out of scope."
- 倫理: "This section should include a justification of the ethics of the work and information about whether the work was submitted to an external ethics panel such as an IRB or the Tor Research Safety Board."
- 利益の主張: "Authors should make clear whether their claims about benefits to a particular user population have been validated in some way ... If authors can't offer such support ... this should be clearly acknowledged in a limitations section."
- 改訂: "Revise" の判定なら改訂で 13 頁。camera-ready も 13 頁。
- 締切: Issue 3 は "Paper submission deadline: November 30, 2026 (firm)"。
- テンプレート: `submission-template-2027.zip` の SHA-256 は `b1abbcc0…ea7d7`（BUILD.md の値と一致・2026-10-24 に取り直した）。

## 最近の PoPETs の論文（9 本）

OpenAlex の `primary_location.source.id:S4210183172`（PoPETs）・2025 年以降で、"re-identification" "anonymization" "linkage attack" "de-identification" "data release" の語で引き、匿名化・加工への攻撃や加工の評価に近いものを選んだ。全部 PoPETs 2026（2027 の新テンプレート以前・camera-ready の 13 頁）。PDF は petsymposium.org から無料で取れた。節の並びと頁は PDF のしおり（`pdftohtml -xml`）から。語数は 1 頁目から謝辞の前までの英字 2 文字以上の語（表・図の中の語と抄録を含む。自稿も同じ数え方で 11,922）。

| 論文 | 本文の終わり | 語数（概算） | 評価・結果が始まる頁 | 節の並び | 付録 |
|---|---|---|---|---|---|
| 2026-0053 Pantomime（動作データの匿名化） | p12 | 9,546 | 評価 p5・結果 p9 | 序論・用語と背景・関連・方法（要件・攻撃者のモデル）・評価（データ・実装・実験・有用性・倫理）・結果・考察と限界・結論 | なし |
| 2026-0037 GAN-Invert（顔の加工への攻撃） | p13 | 8,873 | 設定 p7・結果 p9 | 序論・関連・方法・実験の設定・結果・切除・比較・結論 | 指標の見え方・標準偏差・理論 |
| 2026-0024 SilhouetteTell（ぼかした字幕からの同定） | p14 | 11,377 | 攻撃 p3・評価 p8 | 序論・準備・脅威モデル・攻撃・評価・考察・関連・結論 | データ収集・比較・解像度・速度・環境・規模 |
| 2026-0033 Breaking BAD（Bloom filter の照合への攻撃と修正） | p14 | 8,976 | 攻撃 p4 | 序論・準備・安全性のモデル・攻撃・修正・結論 | 別の攻撃 1 つ |
| 2026-0106 Pseudonymity at Risk（照合の手がかり） | p13 | 9,451 | 評価 p6 | 序論・背景と脅威モデル・分類と照合の方法・データと評価の設定・評価・事例・普及・考察・関連・結論 | なし |
| 2026-0090 Motivated Intruder（推論の枠組み） | p13 | 10,464 | 結果 p7 | 序論・背景・関連・脅威モデル・方法と実験の設定・結果・考察・結論 | データの構成・安定性・符号化の手引き・指示文 |
| 2026-0134 Membership inference の前提の見直し | p14 | 8,789 | 評価 p5 | 序論・背景・脅威モデル・理論・評価・関連・結論 | 証明・追加の図 |
| 2026-0150 Proteus（機器のログの加工） | p13 | 10,181 | 評価 p7 | 序論・背景・既存の限界・脅威モデル・方式・評価・安全性の分析・考察・関連・結論 | 実装 |
| 2026-0085 合成ネットワークデータの安全性と品質 | p14 | 12,035 | 攻撃 p4 | 序論・背景と関連・membership inference・忠実度と有用性・結論 | MI の詳細・忠実度の詳細・実務の手引き |

見えたこと:
- 本文の語数の中央値は約 9,500（8,800〜12,000）で、13 頁に図表を含む。自稿は結果・抄録・序論の残り・結論が無いままで同じ数え方で 11,922 語あり、すでに中央値を約 25% 超える。
- 評価・結果は 4〜9 頁目で始まり、本文の後半の 4〜8 頁を結果に使う。自稿は結果の節が 11 頁目の右段から始まる（方法と脅威モデルで約 10.7 頁）。
- 方法の細部の出し先は付録（データの構成・実装・追加の分析・頑健性・証明）。脅威モデルと評価の設定は本文に 1〜2 頁で置く。
- 9 本のうち 6 本が付録を持つ。付録に出しているのは「追加の分析・細部の延長・実装・データの作り方」で、主張を支える主な結果は本文。
- 照合・加工の評価の型（Pantomime・SilhouetteTell・Breaking BAD・Proteus）は、脅威モデルを短く置き、攻撃の方法を 1 節で述べ、結果を主にしている。

## 結論（3 行）

1. この論文は PoPETs の「加工の評価（測定）」と「照合の攻撃の評価」の種類に当たる（新しい攻撃の提案ではない・Section 2 のとおり）。
2. 読者は打鍵の記録を公開する側と PETs の評価の研究者で、1 頁目に実社会の公開（コンペのマスク）との関係を書く必要がある（規程）。
3. 分量の上限は本文 12 頁（超えれば机上で落ちる）。付録は読まれない前提で、主張の外の補足と細部の延長だけを置ける。
