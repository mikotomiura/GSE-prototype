# S4: data portrait / self-tracking art / lived・reflective informatics と「実践生成肖像」

> 日付: 2026-09-21 ／ ラウンド: **S4**（`/literature-review` 1 ラウンド = 1 問）
> 名前空間: **P**（**[P418]–[P429]**）／ 作業記録: `.steering/20260918-theory-critical-review/survey-S4-raw.md`

## 動機（なぜこのラウンドを回したか）

★ `survey-plan.md` の S4 —— **`SUB-PGP`（実践生成肖像 / Practice-Generated Portrait）の新規性**を塞ぐラウンド。
対象主張は **A-13 / B-18 / B-25**。★ S3 と同じ回に続けて回す理由は「出典が重なるため」（`survey-plan.md` の研究者判断）。

★ 理論側は肖像を **5 要件**で定義している（逐語）:

> **指標性**（本人の実際の作業行為から因果的に生じる）／ **非代替性**（最終状態が同じでも、異なる時間経路なら異なる形態）／
> **過程性**（人格プロフィールでなく、現在のセッションで生成中の関係）／ **解釈の余地**（システムの推定を本人の真実として閉じない）／
> **造形的自律性**（データを受けない基層や美的変奏もある）

## 検証状態

- 探索: **4 angle を subagent へ並列**（(a) Data Portraits の一次 / (b) personal・lived・reflective informatics の終端 / (c) 数値を返さない self-tracking art / (d) **反証 ＋ 自己量化の害**）
- 取得: **12 件を [P418]–[P429] として登録**（`active` 4 件 / `provisional` 8 件）。★ **key 重複は 0 件**（⚠️ S3 で 4 件出したので、**登録前に DOI / 著者名で先に照合した**）
- ⚠️ **メインが逐語を照合したもの: 11 件**（★ S4 の brief に「**抽出テキストを scratchpad に保存してパスを報告**」を入れた結果、**担当が到達した一次をメインが全件たどれた**）
  - ★ **[P424] はメインが arXiv から原典 PDF を取得して全文照合**した（★ 本ラウンドで最も重い判定に使うため）
  - ⚠️ **メイン未照合は [P429] のみ**（★ 担当も要約経由と自己申告）→ **結論の根拠にしない**
- claim 抽出 **12 件** → **7 件 confirmed（3-0 が 5 件 / 2-1 が 2 件）** / **否決・判定不能 5 件**

## gate 判定（要点先出し・下位問いごと）

| 下位問い | 温度 | 一行 |
|---|---|---|
| **(a) Data Portraits の接地** | ★ **確定** | ⚠️ 系譜は **経路依存（非代替性）を主張していない**。★ かつ **正確性（accuracy）を望ましい目標に含める** [P418]、**より正確な推定を将来目標に掲げる** [P420] → ★ **`SUB-PGP` の「解釈の余地」はこの系譜の延長ではない** |
| **(b) informatics の終端** | ★ **確定** | ⚠️ 3 本とも **終端の規範を持たず、長期蓄積を前提**にする [P421][P423]（★ 反復が構造として明記 [P421]）。→ ★ 差分は「**先行が無い**」ではなく「**向きが逆**」である |
| **(c) 数値を返さない作品** | ⚠️ **PLAUSIBLE BUT UNPROVEN** | 部分一致のみ [P426][P427]。⚠️★ **反例がある** —— 数値への忠実性を明言する作家 [P428]、凡例を与えることを価値とする作品 [P425] |
| **(d) 反証** | ⚠️★★★ **一部ヒット（主張の縮小が要る）** | **autographic visualization [P424] が `SUB-PGP` の要件のうち「指標性」「解釈の余地」を既に一般理論として述べており、「computer keyboard の摩耗」を直接の例に挙げている** |

> ⚠️★★★ **gate 用途の結論: `SUB-PGP` の新規性主張は縮小する。**
> ★ **「5 要件の結合が新しい」とは書けない。** 残るのは次の 3 点に限られ、⚠️ **いずれも「今回の範囲で見つからなかった」までである**:
> **(i) 非代替性（同じ最終量でも経路が違えば別の形）を *明示の要件* にすること** ／
> **(ii) それを *肖像*（人格表象）の文脈に置くこと**（★ [P424] には `portrait` の語が **0 件**） ／
> **(iii) セッション局所で、長期の人格プロファイルを作らないこと**（★ [P421][P423] と**逆向き**であることが差分の中身）。

---

## カード 1: データ肖像の系譜は「経路依存（非代替性）」を主張していない **[検証済 3-0]** [P418] [P419] [P420]

1. **どんなもの?** MIT Sociable Media Group の data portrait 系譜（*Data Portraits* / *Themail* / *PostHistory*）。
2. **先行と比べて** 「顔ではなく蓄積データで人を描く」を作品ジャンルとして立てた系譜。逐語: *"Data portraits depict their subjects' accumulated data rather than their faces."*
3. **手法の肝** 月次・日次のビンで時系列を保持する。★ 利用者の逐語 *"you can see in the first four month columns all the places he went **and the order too**"* [P419]。
4. **どう有効と検証した?** *Themail* は利用者面接、*PostHistory* は実装と利用報告。★ **本ラウンドの検証はメインによる逐語照合**（保存抽出 10 件すべて一致）。
5. **議論はあるか?** ⚠️★★★ **「同じ最終量でも異なる経路なら異なる形になる」という *理論的主張* は 3 本のいずれにも無い。** ★ 時系列が残るのは**月次ビンという設計の結果**であって、非代替性の要件化ではない。★ 最も近いのは *"These data bodies extend in time"* [P418]（＝蓄積の記述）。
6. **次に読むべき** Donath, J. (2014) *The Social Machine*（MIT Press）の "Data Portraits" 章（★ **未到達** —— MIT Press Gateway が 403）。

> ★ **GSE への含意**: `SUB-PGP` の **非代替性**は、この系譜の**延長ではない**。⚠️ ただし「無い」ではなく「**今回読めた 3 本に無い**」である（★ 2014 年書籍章が未読）。

## カード 2: ⚠️ データ肖像の系譜は「推定を閉じない」方向ではなく、**正確性の不足を課題**とする **[検証済 3-0]** [P420] [P419] [P418]

1. **どんなもの?** 同系譜の、精度・解釈についての自己記述。
2. **先行と比べて** ★ `SUB-PGP` の要件「**システムの推定を本人の真実として閉じない**」と**正面から向きが違う**。
3. **手法の肝** 逐語 [P420]: *"Analysis of the content would allow us to **more accurately determine** the significance of a relationship."* ／ *"Content analysis would also allow us to **more accurately tell** the social context of the relationship"*。
4. **どう有効と検証した?** ★ メインが保存抽出で逐語照合。★ さらに [P420] §5.2 は解釈の揺れを**問題**として報告する: *"users were **confused** about its meaning and accuracy."*
5. **議論はあるか?** ⚠️ **対称性のために両側を書く** —— [P418] には逆向きの強い記述もある: *"Objectivity and accuracy are different, and a computational portrait can be **objective without being the latter**."*・*Personas* は *"a reminder of the **fallibility**, social naivete, and opaqueness of the computer as portrayer"*。★ **ただし結論部は目標を並列に置く**: *"balance the diverse goals — **accuracy**, privacy, dignity, and enjoyment —"*。→ ★ **「閉じない」を規範として掲げてはいない**。
6. **次に読むべき** [P418] が引く van Alphen (1996) "The Portrait's Dispersal"（★ 未読）。

> ★ **GSE への含意**: ⚠️★★★ **「データ肖像の系譜は推定を開いたままにする」と書いてはならない。** ★ [P419] は **満足が「確認（confirm）」と結びつく**ことを報告している（逐語 *"The more Themail **confirmed their expectations** … the more they enjoyed using the tool."*）。

## カード 3: personal informatics の起点は**反復と長期蓄積**を前提にし、終端の規範を持たない **[検証済 3-0]** [P421]

1. **どんなもの?** Li, Dey & Forlizzi (2010) の 5 段階モデル（preparation / collection / integration / reflection / action）。
2. **先行と比べて** personal informatics を設計領域として定義した起点。
3. **手法の肝** ★ 4 性質の 1 つが逐語 *"**they are iterative**"*。★ 最終段階は *"The **Action** stage is the stage when people choose what they are going to do with their newfound understanding of themselves."*
4. **どう有効と検証した?** 質的調査からのモデル構築。★ 本ラウンドはメインによる逐語照合。
5. **議論はあるか?** ⚠️★★★ **長期蓄積が明示的に価値づけられている** —— 逐語 *"**Long-term reflection is valuable** because it allows users to compare personal information between different times and it reveals trends and patterns."*
6. **次に読むべき** [P187] Baumer, *Reflective Informatics*（★ **既登録**・本ラウンドでは読んでいない）。

> ★ **GSE への含意**: `SUB-PGP` の **過程性**（セッション局所）は、**この系譜と逆向き**である。→ ★ 差分を書くときは「**先行が無い**」ではなく「**向きが逆**」と書く。

## カード 4: lived informatics は「行為の前に理解を完了させる」発想を斥けるが、**「系が終える」の先例ではない** **[検証済 2-1]** [P422]

1. **どんなもの?** Rooksby et al. (2014) が [P421] の段階モデルを批判して提案した記述的概念。
2. **先行と比べて** 逐語: *"we are underscoring our observations, **trying to characterize a state of affairs rather than laying out a vision**."*（★ **規範ではなく記述**であると自認している）。
3. **手法の肝** 逐語: *"Li et al.'s model is **technology-centric**."* ／ *"it is problematic to assume that people will **postpone action until they have rationally determined 'newfound understanding'**."*
4. **どう有効と検証した?** 22 名の面接（★ **N はメイン未照合**）。★ 逐語はメインが照合。
5. **議論はあるか?** ⚠️ **2 票目の留保**: 「理解の完了を前提にしない」ことは **GSE の「意味の認定を終える」と似て見えるが、主語が違う**（★ 前者は**利用者の行為**、後者は**系の処理**）。★ 長期蓄積の相対化は逐語で確認できる（*"to track over the short term is **not necessarily to give up or fail**"*）が、⚠️ **セッション局所を規範として述べてはいない**。
6. **次に読むべき** Epstein et al. の lived informatics モデル（★ **既登録 [V75]** の周辺・本ラウンド未読）。

## カード 5: *A Quantified Past* は `SUB-PGP` の要件の**すべてと向きが逆**である **[検証済 3-0]** [P423]

1. **どんなもの?** Elsden, Kirk & Durrant (2016)。自己追跡の**歴史的記録**との付き合い方を扱う 44 頁の論文。
2. **先行と比べて** ★ 対象が *"**long-term** users of different self-tracking tools"* であり、**蓄積された過去**が主題。
3. **手法の肝** 逐語: *"Personal informatics also appear to be particularly **ego-centric** as recording devices."*・設計提案は *"**making account of their data**"*（★ 継続的な営みとして）。
4. **どう有効と検証した?** 15 名の長期利用者への面接。★ 逐語はメインが照合。
5. **議論はあるか?** ★★★ **これは GSE にとって「先行が無い」ことの証拠ではなく、「対照項が在る」ことの証拠である。** → ⚠️ **差分を「空白」と書かず、「向きの違い」と書く**（★ `docs/glossary.md` 禁止用語の趣旨に沿う）。
6. **次に読むべき** 同著者の DIS 2015 pictorial（⚠️ **別稿**。取り違えない）。

## カード 6: ⚠️★★★ autographic visualization が `SUB-PGP` の要件を**一部先取りしている** **[検証済 3-0]** [P424]

1. **どんなもの?** Offenhuber (2019)。**物質的痕跡**を可視化として扱う一般理論。逐語: *"Autographic visualization **starts with the phenomenon** and explores the data generation process through material traces."*
2. **先行と比べて** ★ Table 1 が InfoVis と対比する —— *"Outwards: **reveals the process of data generation**"* / *"Non-representational: the phenomenon presents itself"*。
3. **手法の肝** ★ **指標性（indexicality）が中心概念**（Index Terms に明記）。★ **解釈の非閉鎖**も Barad の intra-action で基礎づけられている —— 逐語: *"autographic visualizations are **not stable artifacts** whose correct interpretation is just a matter of visual literacy, but phenomena that emerge from a recipients' extensive engagement with the world…"*
4. **どう有効と検証した?** 理論論文。★★★ **メインが arXiv から原典 PDF を取得して全文照合**した。
5. **議論はあるか?** ⚠️★★★ **「コンピュータのキーボードの摩耗」を直接の例に挙げている** —— 逐語: *"Autographic visualizations can be **accidental**, such as the desire paths across grass areas in the city or the **uneven traces of wear on a staircase or a computer keyboard**."*
   ★ **ただし限定が 2 つある（★ メインの全文実測）**: (i) この例は **`accidental`（偶発的）**として挙げられている。(ii) 本文に **`portrait` は 0 件**であり、**人格表象としての「肖像」の文脈には置かれていない**。★ また **`trajectory` 0 件 / `path` 3 件**（いずれも desire path の意）で、**経路依存＝非代替性の理論化は見当たらない**。
6. **次に読むべき** Offenhuber, D. *Autographic Design*（MIT Press, **2024**）／ 本論文が引く Ginzburg の evidential paradigm（★ **どちらも未読**）。

> ⚠️★★★ **GSE への含意（本ラウンド最大の帰結）**: **`SUB-PGP` の「5 要件の結合が新しい」とは書けない。**
> ★ **指標性**と**解釈の余地**は [P424] に既出で、**過程性**も「データ生成過程の露出」という形で既出である。
> → ★ 残る差分の候補は **非代替性の明示要件化 × 肖像（人格表象）の文脈 × セッション局所**の 3 点に**縮小する**。
> ⚠️ **それも「今回の範囲で見つからなかった」までである**（★ *Autographic Design*（**2024**）が未読）。

## カード 7: 「データを作品にする＝数値を隠す」ではない **[検証済 2-1]** [P425] [P427] [P428]

1. **どんなもの?** self-tracking art 側の、数値の扱いについての作家自身の記述。
2. **先行と比べて** ★ `ADR-025`（層 A に数値を添えない）と同型の先行を探したラウンド。
3. **手法の肝** ★ **部分一致**: *"**Color and geometry carry what raw numbers cannot**, … the lurch where something broke"* [P427] ／ *"How a dataset is collected and the information included — and omitted — **directly determines the course of its life**"* [P426]。
4. **どう有効と検証した?** ★ メインが保存抽出で逐語照合（4 件すべて一致）。
5. **議論はあるか?** ⚠️★★★ **反例が 2 つある** —— (i) *Dear Data* は **凡例（key）を与えて読めるようにする**ことを価値とする: *"the **code that enabled the recipient to decipher the picture**"* [P425]。(ii) Miebach は **数値への忠実性**を明言し、作品が**計器**として機能することを意図する: *"**By staying true to the numbers** … instruments that could be used in the actual environment"* [P428]。
   ★ **2 票目の留保**: [P425] は **本人 → 他者**への翻訳であり、`ADR-025` が禁じる「**本人に自分の量を返す**」とは構造が違う（★ 直接の反証にはならない）。
6. **次に読むべき** *Dear Data* の**書籍本文**（★ **未取得**・作家サイトのみ）。

> ★ **GSE への含意**: `ADR-025` は **GSE 固有の判断**であって、**データを作品化することの一般的な帰結ではない**。→ ⚠️ 「作品化するなら数値を隠すのが当然」とは書かない。

---

## 否決リスト（★ 履歴を残す）

| # | 主張 | 票 / 温度 | 否決・保留の理由 |
|---|---|---|---|
| 1 | 「*Dear Data* は `ADR-025`（本人に数値を返さない）の先行である」 | **0-3** | ⚠️ **逆である** —— 凡例を与えて解読可能にすることを価値としている [P425]。★ かつ構造が違う（本人 → 他者） |
| 2 | 「Goodhart の法則を自己追跡に当てた学術一次がある」 | **判定不能** | ⚠️ 担当は**ブログ・Medium 水準にしか到達できず**、査読済み一次に未到達と自己申告。★ 捏造回避のため書誌を持ち帰らせなかった |
| 3 | 「Lupton の dataveillance が GSE の『自己量化ゲームへの変質』の先行」 | **判定不能** | ⚠️ **二次記述（書評・要約）のみ**。一次（書籍本文）未到達 |
| 4 | 「[P429] が『良い記録を作ろうとして行動が歪む』ことの証拠」 | **1-2** | ⚠️ **調整変数（マインドセット）の研究**であり直接証拠ではない。⚠️ かつ**逐語がメイン未照合** |
| 5 | 「Etkin (2016) は新規の出典である」 | ★ **重複** | ★ **既登録 [P77] と同一 DOI**（`10.1093/jcr/ucv095`）。⚠️ 担当が重複疑いとして報告 → **メインが照合して登録を見送った**（★ S3 で 4 件出した重複を、S4 では 0 件に抑えた） |

## やり残し（★ 次ラウンドの入口）

1. ⚠️★★★ **Offenhuber, D. *Autographic Design*（MIT Press, **2024**）** —— ★ [P424] は 2019 年の論文であり、**書籍版で「肖像」「経路依存」に踏み込んでいれば、`SUB-PGP` に残った 3 点の差分も消える**。★ **最優先**。
2. **Donath (2014) *The Social Machine* の "Data Portraits" 章** —— ★ MIT Press Gateway が 403。カード 1 の留保を閉じる。
3. **[P429] の一次全文**（★ 逐語がメイン未照合のまま）／ Lupton (2016) の一次。
4. **[P425] *Dear Data* の書籍本文** と **[P426] の 13 原則の全文**（★ どちらも抜粋止まり）。
5. ⚠️ **HCI 側の「abstract / ambient representation of personal data」の評価研究は時間切れで未着手**（★ [P103] Spark 以外）。
6. ⚠️ **「自己量化ゲームへの変質」（本人が良い記録を作ろうとして行動を歪める）の直接証拠は、本ラウンドの範囲では 0 件** —— ★ 理論が**自ら警告している**論点なので、空白のまま放置しない。

## GSE への還元（§4 差分との関係）

- ⚠️★★★ **反証（主張の縮小）**: `SUB-PGP` の **「5 要件の結合が新しい」は書けない** [P424]。→ ★ 残る差分の候補は **非代替性の明示要件化 × 肖像の文脈 × セッション局所**の 3 点（⚠️ **いずれも「今回の範囲で見つからなかった」まで**）。
- ★ **精緻化**: 差分の書き方を「**空白**」から「**向きの違い**」へ変える [P421][P423]（★ 先行は**長期蓄積・反復・ego-centric** を志向しており、**無いのではなく逆**である）。
- ⚠️ **禁止の追加**: 「データ肖像の系譜は推定を開いたままにする」と書かない [P419][P420]（★ 実際は**正確性の不足を課題**として扱う）。「作品化するなら数値を隠すのが当然」と書かない [P425][P428]。
- ★ **`ADR-025` への含意**: 一般的な帰結ではなく **GSE 固有の判断**である、と明示できるようになった（★ 先行は両向きに存在する）。
