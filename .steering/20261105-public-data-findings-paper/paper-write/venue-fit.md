# 投稿先の適合（paper-write Step 0）

- 日付: 2026-11-05
- 目的（判断 5）: 読者は行動ログで学習者・利用者の状態を推して介入に使う研究者。変えたいのは評価の設計（「手前から当てた」と言う前に、対照を揃え、手前の変化と作業の局面を分ける）。
- 制約: 著者は所属のない独立の研究者。掲載料は払わない（購読誌として出すか、掲載料なしの OA）。プレプリントを併せて出す。
- 調べ方: 6 誌の規程を Sonnet のサブエージェント 2 本で並列に取った。保存したページは scratchpad の `venue/`（repo の外）。

## 照合の格

- メインが保存したページで逐語を照合したもの: JLA（機関のメール・8,000 語・掲載料なし・プレプリント）、JEDM（掲載料なし・方法と比較・プレプリント・3 か月）、IEEE Computer Society 共通（12 頁・超過 $220/頁・購読型は掲載料なし）。
- 未照合（サブエージェントが Chrome で取り、手で写したもの・Springer と Elsevier は curl が bot 対策で止まる）: UMUAI・BRM・IJHCS の規程の文。投稿先を決めたら、メインが Chrome で開き直して照合する。

## 比べ

| | JEDM | UMUAI | JLA | BRM | IJHCS | IEEE TAC |
|---|---|---|---|---|---|---|
| 読者との合い | 合う（教育データの状態の推定・方法と比較を重んじる） | 合う（利用者の状態のモデルの評価・ログからのフラストレーションの検出の先例） | よく合う（学習分析） | 方法の読者（心理学）。目的の読者とずれる | 具体の解決を期待。反証の論文は合いにくい | 情動に限る。停滞は範囲外の恐れ |
| 掲載料と無料の道 | なし（完全 OA・学会負担） | 購読型で無料（hybrid）。embargo あり（未照合） | なし（完全 OA） | 購読型で無料・著作権は学会へ（未照合） | 購読型で無料（未照合） | 購読型で無料。12 頁を超えると 1 頁 $220 |
| 分量 | 上限の記載なし（テンプレート） | 要旨 150〜250 語・本文の上限は見当たらず（未照合） | 8,000 語（要旨・図表・参考文献込み） | 上限なし・要旨 250 語（未照合） | 要旨 250 語（未照合） | 12 頁（参考文献込み） |
| プレプリント | 可（逐語: "permitted and encouraged to post online a pre-publication manuscript"） | 未確認 | 可（arXiv など） | 未確認 | 可（SSRN の無料投稿あり・未照合） | 未確認 |
| 独立の研究者 | 要件の記載なし | 所属なしの扱いを明記（未照合） | **投稿の責任著者に機関のメールを求める**（逐語: "Personal webmail addresses (e.g., Gmail, Yahoo, Outlook.com) are not accepted for the corresponding author's OJS account."） | 免除なら理由を本文に書く・後付けの承認は原則不可（未照合） | 記載なし | 審査の承認の有無を申告 |
| 査読の期間 | 3 か月を目指す（逐語） | 未取得 | 初回 6 週・公開まで 6〜8 か月 | 未取得 | 未取得 | 未取得 |
| 近い論文 | クリックストリームの予測・一般化の検証（2024〜2026） | ログからのフラストレーションの検出（2024）・認知状態の検出の個人化（2026） | CS1 の予測の再現（2024）・一般化（2026） | マウスの追跡・multiverse の方法 | 打鍵の疲労の指標（2025） | マウスの情動推定・再現研究 |
| その他 | 双盲・査読者 3 名・生成 AI の利用の申告が必須 | 単盲・査読者 2 名・データの可用性の声明が必須 | 双盲・Notes for Practice が必須 | 別の論文が査読中（BR-Org-26-1306）。同じ誌への 2 本目の規定は見つからず | 「具体の利用者への具体の解決」を期待 | 事前選別で範囲外を落とす |

## 結論（3 行）

- この論文は、行動ログで状態を推す研究の評価の設計への反証と方法の貢献に当たる。
- 第一候補は JEDM（読者が合い、方法と比較を重んじ、掲載料なし・プレプリント可・独立の研究者に障害なし）。第二候補は UMUAI（読者が合い、所属なしを想定。購読型で無料）。JLA は読者が最もよく合うが、機関のメールの要件があり、編集部に例外を聞かないと出せない。
- 分量の上限は JEDM に記載が無いので、最近の論文の長さ（次の段で 3 本以上を測る）と paper-write の目安（本文 5,000〜7,000 語）で決める。

## 次の段でやること

- JEDM の最近の論文 3〜5 本の本文の長さと節の並び・方法の置き方を測る（paper-write Step 0 の残り）。
- JEDM のテンプレート（LaTeX）を取り、分量の決まりが無いかをテンプレートの中で確かめる。

## 追記（2026-11-05・Step 0 の残り）: JEDM の最近の論文とテンプレート

### 最近の論文 6 本

OpenAlex の `primary_location.source.id:S7407065558`（JEDM）で 2025〜2026 年の article を新しい順に 15 本出し、総説（1089）と生成 AI の質的符号化の系統の一部を除いて、実証で比べを含む 6 本を選んだ。PDF は OJS の pdf の版（無料）。保存は scratchpad の `jedm/`（repo の外）。

本文の語数は `pdftotext -layout` の出力で、「1. INTRODUCTION」の行から、最初の ACKNOWLEDGMENTS・DECLARATION・REFERENCES・FUNDING・APPENDIX の行の手前までの英単語を数えた（スクリプトは scratchpad の `jedm/count.py`）。表の中の文字と図の中の文字も入るので、地の文だけより多めに出る。

| id | 題（略） | 頁 | 本文の語数 | 節の並び | 補足の置き方 |
|---|---|---|---|---|---|
| 1115 | 読みの力を入れないモデルの公平性 | 27 | 約 10,200 | 序・背景・方法・結果・考察・限界と今後・結論 | OSF への言及 1 |
| 1147 | 知識要素の粒度の比較 | 48 | 約 7,500 | 序・関連研究・方法とデータ・結果と考察 | 参考文献の後に付録（頁の約半分） |
| 960 | 授業の負荷のモデルの一般化と移転 | 28 | 約 10,900 | 序・背景・データと文脈・分析の方法・結果・考察・限界と今後・結論 | 参考文献の後に付録 A・B |
| 1097 | BKT で足場と望ましい困難を評価 | 27 | 約 7,600 | 序・方法・結果・考察 | OSF への言及 3 |
| 1030 | 探索・解釈・確証を分ける分析の枠組み | 28 | 約 10,200 | 序・方法・結果・考察・限界と結論 | なし |
| 1007 | 対話から粘り強さの指標を LLM で同定 | 36 | 約 13,000 | 序・方法論・結果・考察 | 別の Supplemental Materials（表 S1〜） |

- 中央値は約 10,200 語（7,500〜13,000）。頁は 27〜48（12pt の 1 段組みなので頁は多くなる）。
- 節の並びは IMRaD が基本。限界を独立の節にするものが 3 本。
- 方法の細部の置き場は 3 通り: 参考文献の後の付録（1147・960）、別の補足資料（1007）、OSF（1115・1097）。
- 貢献の種類: 比較（1147）・一般化の検証（960）・評価（1097）・方法の枠組み（1030）。反証を主にした論文はこの 6 本には無い。1030 は探索と確証を分けて報告する枠組みで、事前登録に近い考え方を JEDM の読者に向けて論じている（序論で引く候補。書誌の登録は引くと決めてから）。

### テンプレート（2024_08_02_jedm-latex.zip）

Information for authors のページ（`/information/authors`）の Google Drive のリンクから取った。中身は `jedm.cls`・`acmtrans.bst`・`instructions.tex`・`instructions.pdf`・`ref.bib`・`example-fig.pdf`。`\documentclass[notitlepage,12pt]{jedm}`。

逐語で照合した決まり（`instructions.pdf`）:

- 要旨: "It should contain from 100 to 300 words."
- 補足: "Supplementary technical material (e.g., mathematical proofs or descriptions of experimental procedures) should be collected in an appendix at the end of the paper (after the references)."
- 資料のリンク: "Authors should add a sentence at the end of the abstract giving the link(s) to supporting materials."
- 図の代替テキスト: `\Description` で付ける（"The alt text should describe everything necessary in the figure"）。
- 査読用の版は頁番号を付ける。
- 本文の語数・頁の上限: テンプレートの説明（instructions.pdf）にも規程のページにも該当の文は無い（原文を取ったうえで無い）。

規程のページ（`/about/submissions`）で追加で照合したこと:

- 双盲は任意（逐語: "You may submit an anonymized version of your manuscript. If you choose this possibility, the review process will be double-blind."）。上の比べの表の「双盲」は「双盲は任意」に読み替える。
- 生成 AI の申告は、参考文献の前の節 "Declaration of Generative AI Software tools in the writing process" に定型の文で書く。
- 投稿は PDF。編集者への手紙は任意。

### Step 0 の結論（更新）

- 種類: 評価の設計への反証と方法の貢献（比較・一般化の検証の系統に近い）。
- 読者: 行動ログで状態を推す研究者（判断 5）。
- 分量: 規程に上限は無い。最近の論文の本文の中央値は約 10,200 語。予算は `length-log.md` で決める。補足は参考文献の後の付録と、OSF・GitHub に置く。
