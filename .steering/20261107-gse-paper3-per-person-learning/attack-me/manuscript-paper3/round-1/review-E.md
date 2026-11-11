# review-E（manuscript round 1・UMUAI 担当編集者）

判定: 直してから回す。理由の主: 要旨 266 語が規程の 250 語を超える／「新しいのは既存の部品の当てはめ」という自己規定では "novel and significant" を判断しにくい。読んだもの: main.tex（eff4bc93）と references.bib。補足は読んでいない。

## 1. 接地
- B1 新規性と意義（UMUAI Aims & Scope・context-A の照合済みの抜粋）: "provides an interdisciplinary forum for the dissemination of novel and significant original research results about interactive computer systems that can adapt themselves to their users, and on the design, use, and evaluation of user models for adaptation." 分野に "methods for the design and evaluation of user models and adaptive systems"。
- B2 形式（規程の抜粋）: "Please provide an abstract of 150 to 250 words." / "Please provide 4 to 6 keywords" / "submissions that do not include relevant declarations will be returned as incomplete." / "Other declarations include Ethics approval, Consent, Data, Material and/or Code availability" / "All original research must include a data availability statement."
- B3 中心の貢献は 1 つ（Mensh & Kording 2017 Rule 1・Table 1）: "Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each"／守れていない兆候 "Readers cannot give 1-sentence summary."
- B4 素朴な読者向け（Rule 2）: "Define technical terms clearly because readers can become frustrated when they encounter a word that they don't understand." と "minimize the number of loose threads that the reader has to keep in mind at any one time."
- B5 同じ話題は 1 か所（Rule 4）: "Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place"
- B6 考察の役割（Rule 8）: "explains how the results have filled the gap ... provides caveats to the interpretation, and describes how the paper advances the field by providing new opportunities."／Rule 7 "the title of the figure should communicate the conclusion of the analysis".

## 2. 1 文（ほぼ言える）
「キーストロークの系列モデルでは、同じ構造の弱い共有モデルに対して見える個人モデルの利得（最大 0.19 nats/記号）は、本人の一次マルコフ連鎖と比べ、構造と縮約を他者で選んだ強い共有モデルと比べると、本人に帰属できない約 5×10⁻⁴ にまで縮む。だから、個人化の利得を評価する適応システムの研究者は、この 2 つの比較相手と、検査が検出できる最小の差を一緒に報告すべきだ。」
迷った点: (1) 中心が「評価の手順」か「CoAuthor での発見」かが揺れる（main.tex:50 "an evaluation protocol ... and what it changes in one case"・"The protocol combines established parts ... what we add is its application"）。(2)「何が変わるか」が予測の対数尤度に留まる（main.tex:236 "downstream benefit and cost were not measured"）。

## 3. 指摘（重い順）
- [major] 要旨が規程の上限を超える
  - 位置: main.tex:33-35。context-A の測定で 266 語。
  - なぜ: "Please provide an abstract of 150 to 250 words." に反する。形式の不備は編集者の段で戻す最も簡単な理由。
  - 解消: 250 語以下へ。"(about 3% at its largest training size)"・"in the 15-session panel" の繰り返し・CS1 の文の後半は本文に任せて削れる。
  - 自信: 高
- [major] 新規性を「既存の部品の当てはめ」と自分で規定している（B1・B3）
  - 位置: main.tex:50「The protocol combines established parts (...); what we add is its application to per-person sequence models of keystroke behaviour」・main.tex:64「we do not claim it as new」。
  - なぜ: 立っている新しい要素は 2 点（本人の連鎖を比べの相手に・prior mode を診断に）だが、後者は main.tex:242 "we have not evaluated whether it measures the effect of smoothing" と自ら留保。
  - 解消: 中心の貢献を 1 つに絞り、序論の最後の段落の 1 文目で言い切る（知見「標準の比べの相手が利得を桁違いに水増しする」か「評価の手順」か）。UMUAI の読者の何を変えるかを 1 文。
  - 自信: 中
- [major] 検出の下限の合成検査の方法が本文に無く、結果も段落の途中に埋もれる（B6・Rule 7）
  - 位置: main.tex:222「How small a difference could this protocol have detected? We planted ...」（4.3 の表の後の 1 段落のみ・方法の 3 章は触れない）。
  - なぜ: 推奨 (3)（main.tex:241）と結論（main.tex:264 "together with the smallest difference the check can detect"）の中心なのに、独立した単位として示されない。同じ段落の後半に但し書き 3 つ（負の対照・合成 CS1 の τ・記号化）。
  - 解消: 方法に 2〜3 文の小節「Sensitivity check」。結果では「検出の下限は X で残りはそれより小さい」を見出しにした小節に分ける。負の対照の細部は S15 へ。
  - 自信: 高
- [major] 意義が予測の対数尤度の単位から出てこない（B1・B6）
  - 位置: main.tex:236「the remainder ... corresponds to about 1.5 to 2.6 nats」「the comparison concerns predictive accuracy, and downstream benefit and cost were not measured」・main.tex:232「For a designer deciding whether to model each person, the first number argues for per-person models and the second gives no reason to」。
  - なぜ: 0.19 と 5×10⁻⁴ の違いが適応の判断（誰を個別にモデル化するか・cold start の費用）で何に当たるかが無い。考察 524 語で、関連研究の先例（Aalbers2023・DeMasi2017・Yudelson2013 など）に結果を戻す段落が無い。
  - 解消: 考察に 1 段落（他分野の結果〔person-mean baseline が勝つ例など〕に並べ、keystroke 系列モデルで何が新しく分かったかを位置づける）。下流を測っていないことは限界で 1 回だけ。
  - 自信: 中
- [major] 中心の対象の記号列が本文だけでは理解できない（B4）
  - 位置: main.tex:100「combined into two composite values, smoothed exponentially and mapped to a 5×5 grid, with one further symbol for the first typing second after a long run of deletions: 26 symbols」。
  - なぜ: 結論の大きさが記号化に依ると何度も書く（main.tex:157・222・249・258）のに、2 つの合成値と格子の軸の意味が本文に無い。選んだ根拠も Uto2020（"30-second frames with a 10-second step"）1 本で、「every few seconds」の作業状態モデルという特徴づけ（main.tex:44・100）とわずかにずれる。
  - 解消: 合成値と軸の意味を 2 文で本文に、量子化の細部は S2。Uto2020 の特徴づけを確認済みの範囲（30 秒の枠・10 秒の刻み）に合わせる。
  - 自信: 中
- [minor] 同じ但し書きと分析の地位の説明が何度も出る（B5）
  - 位置（全部）: 「cannot attribute ... to the person」main.tex:34・48・50・185（見出し）・255・264／「neither shows nor rules out」系 222・234・254／記述的・検定なし・閾値なし 144・236・252、「exploratory」50／prior mode は診断 111・225・242／負の対照・合成 CS1 の τ 222・256／選びが目標の書き手の非保留の単位を含む 105・137（キャプション）・243・256／記号化への依存 157・222・249・258／CS1 の休止 72% 34・80・250（＋Table 1）／τ=10⁶ が格子の端・重み約 1% 34・190・234・255。
  - 解消: 但し書きは限界で 1 回ずつ、他は節番号を指すだけ。中心の主張だけは繰り返してよい。
  - 自信: 高
- [minor] 本文に置かなくてよい細部（補足へ移せる）
  - 位置: main.tex:144 の検証の記録と手順の経緯／157 後半「with non-overlapping windows (direction only) ...」／222 末尾の記号化の変種の数値／227 平均で選んだ検算の数値／236「A per-person logistic model of a proxy label ...」／257-258 の初期値と記号化の変種の細部。
  - なぜ: 4,451 語は参考値より短く長さは問題でない。問題は主筋でない検算が主筋の段落に割り込み密度を上げること（Rule 4）。
  - 解消: 補足へ移す。空いた分量を記号の定義・検出の下限の方法・考察の位置づけへ。
  - 自信: 中
- [minor] 推奨 (4) は評価していないものを勧めている
  - 位置: main.tex:238「we recommend what this study evaluated」と main.tex:242「while noting that we have not evaluated whether it measures the effect of smoothing」。
  - 解消: (4) を延長の一覧（main.tex:243）か「示唆」へ移す、または前置きを直す。
  - 自信: 高
- [minor] 宣言の節に不足（B2）
  - 位置: main.tex:269「Code availability. The symbolization kit; the fitting code ...」に置き場所（リポジトリ・DOI）と公開時期が無い。main.tex:272「Ethics. Public data only; no new participants.」に Consent の項が無い。
  - 解消: Code の置き場所。Ethics approval と Consent を見出しを立てて（例 "Not applicable; secondary analysis of public de-identified data"）。Data availability が S2 に頼る所は本文でアーカイブの所在を 1 行。
  - 自信: 中
- [minor] 用語が定義されないまま要旨と序論に出る（B4）
  - 位置: main.tex:34「nats per symbol」「shrinkage」「planted difference」・main.tex:50「the shared model's prior mode」。
  - 解消: 要旨の「planted difference」を「the smallest difference such a check can detect」程度に。prior mode は序論に出さず 4.4 で導入。
  - 自信: 中
- [nit] 表と図の読みやすさ: Table 2（main.tex:199-219）は 8 列で「15-s.」「e$-4$」の略記。Figure 2 のキャプション（main.tex:181）は「Medians over the 17 writers ...」で始まり結論を言わない（Rule 7）。解消: キャプションの 1 文目を結論に・×10⁻⁴ を列見出しに。自信: 高
- [nit] 作業用の注記が残る: main.tex:60「% OPEN: the evaluation design of Uto et al. (2020) is not yet checked ...」。ソース提出前に消す。自信: 高
- 良い点（指摘ではない）: 結果の 4 小節は読者の問いの順で見出しが宣言文（Rule 7）。考察の「What was established and what was not」は確かめたことと可能性を分けている。

## 4. 判定: 直してから回す
1. 要旨 266 語が上限超え。宣言の節に Code の置き場所と Consent が無く、形式で戻されうる。
2. 主題は Aims & Scope の範囲内。ただし新規性の自己規定と、nats から適応の判断への翻訳が無いため "novel and significant" を支持しにくい。
3. 結論を支える検出の下限の検査と記号列が本文で定義されていない。分量は繰り返しと副次の検算を補足へ移せば作れる。

## 5. 読めなかった範囲・注入の疑い
- 補足（figdata・kit README）は依頼どおり読んでいない。S1〜S15 は未作成。投稿先の一次は context-A の抜粋の範囲のみ。最近の UMUAI の語数は参考。references.bib は異常な指示文の grep のみで精読していない。
- 注入の疑い: 無し（main.tex:60 の LaTeX コメントは著者の作業注記と判断）。
