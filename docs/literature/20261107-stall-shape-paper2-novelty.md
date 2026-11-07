# 文献カード: 停滞の形を濃くする 3 つの計算に先行はあるか（論文 2）

- **トピック**: stall-shape-paper2-novelty
- **日付**: 2026-11-07
- **作業記録**: `.steering/20261107-paper2-stall-shape/`
- **用途**: 論文 2 を単独にするかを決める計算（揺れの分解・数え上げとの比・multiverse）の条件を書く前の新しさの確かめ。gate 判定ではない。

## 動機

`20261105-public-data-findings-novelty.md` のカード 4 の 5 は、知見 2 の残りについて「日・セッション・人の 3 水準以上の分解、停滞の数を数え上げ（ポアソン）と比べること、閾値や切り方を振る multiverse は 0 件」と書いた。判断 43（`.steering/20261105-public-data-findings-paper/decisions.md`）でこの 3 つを回すと決めたので、回す前に、その後に出た研究と前回の探し漏れを短く確かめる。

## 検証状態

- 下位の問い 3 つ（Q1 3 水準以上の分解・Q2 出来事の数の過分散・Q3 分析者の選択を振る multiverse）を、Sonnet のサブエージェント 3 本で並列に探した。各々に「既にやられている」側の角度（EMA・デジタル表現型の日の揺れ・セッションの切り方・time-on-task の推定・MOOC の離脱の定義）を含めた。既登録の文献は番号だけ挙げさせた。
- 新規に登録したもの 4 件（[V468]〜[V471]）。既登録で番号だけ挙がったもの: [V415]・[V416]・[V420]・[V425]・[P36]・[V424]・[V152]・[V161]〜[V163]・[V334]・[V365]・[V423]・[V440]・[V448]・[V414]・[V450]・[P122]・[V418]・[P123]・[V192]。
- メインが一次で照合したもの: [V468]（PDF の全文・4 か所の逐語）、[V469]（PDF の全文・§2.8 の逐語と、本文の "dispersion" の出現が 2 回だけであること）、[V470]・[V471]（OpenAlex の抄録の逐語）。BiAffect 系・ETS 系・MOOC の離脱の定義の候補は要旨か検索の要約だけで、登録していない（やり残し）。
- claim 6 件を 3 票（内的妥当性・外への広げ・頑健さ）で判定した。確定 3・留保つき確定 1・判定不能 2。否決 1。

## 要点を先に

| 問い | 温度 | 一言 |
|---|---|---|
| Q1 打鍵の休止・停滞の数や長さを 3 水準以上（人・課題・日・まとまり）で分解した研究 | **判定不能（0 件）** | 近いのは 2 水準（[V415]・[V425]）と、日や時刻を回帰に入れる BiAffect 系（[V334]）。occasion をまたぐ安定性（[V152]）は本文未確認 |
| Q2 休止・停滞・行き詰まり・離脱の数の過分散の大きさを報告した研究 | **判定不能（0 件）** | 休止の数でポアソンを既定とし、過分散なら負の二項に切り替えた例はある（[V469]）。値は出していない |
| Q3 分析者の選択（閾値・切り方）で結論が動くことを示した研究 | 確定（命題は既出） | 学習分析の time-on-task で、推定の仕方だけで R² が平均 0.15 動く（[V468]）。休止・停滞のラベルの率・順位・データの間の比べを振った multiverse は 0 件 |

→ 論文 2 の新しさは「切り方で結論が動く」という命題には置けない（[V468] が既出）。置けるのは、対象（打鍵の停滞のラベル）・見せ方（率だけでなく、データの間の順位・同じ人の中の過分散・推定の水準の比べがどう動くか）・3 つのデータを同じ手順で回すこと、に限られる。

---

### カード 1: 推定の仕方だけで学習分析の結論が動く。命題は既出 **[検証済 3-0]** [V468]

1. **どんなもの？** Kovanović ら（[V468]）は、LMS の記録から time-on-task を出す 15 の戦略（最後の行動の扱い・外れ値の上限 60/30/10 分・置き換え）を、オンラインの 1 科目（81 人）と混合型の 9 科目で比べ、成績を予測する回帰の結果がどれだけ動くかを示した。
2. **先行研究と比べてどこがすごい？** 要旨の逐語: *"our findings indicate that time-on-task estimation methods play an important role in shaping the final study results, particularly in online settings where the amount of interaction with LMS is typically higher."* §6 の逐語: *"On average, the difference in R2 was 0.15, which corresponds to 15% of the variance being explained solely by the adoption of a particular time-on-task estimation strategy."* 係数の有意も入れ替わる（*"In one of them (x:l10), none of the β coefficients were significant, while in the other two models (x:ev and x:rm) the coefficients for the time spent updating messages and viewing assignments were significant"*）。
3. **技術や手法の肝はどこ？** 閾値の選び方の難しさを名指しする: *"it is hard to pick a threshold value that would remove as much of the off-task behaviour as possible, while not affecting genuinely long actions."*
4. **どうやって有効だと検証した？** 同じデータに 15 の戦略を当て、最良と最悪の R² の差と係数の有意を並べた。
5. **議論はあるか？** 振った軸は時間の推定の 1 系統で、休止や停滞のラベルではない。個人やデータの順位は扱っていない。全組合せの specification curve ではない。混合型のデータでは効きが小さい。論文 2 は「選択で結論が動く」を新しいとは書けず、[V468] を先行として名指しし、対象と見せ方の違いで位置づける。
6. **次に読むべき論文は？** 同じ著者の LAK 2015 の短報（doi:10.1145/2723576.2723623・要旨だけ確認・未登録）。Hart らの打鍵の潜時からの time-on-task の推定（SIGCSE 2023・PLOS ONE 2025・本文未確認・未登録）。

### カード 2: セッションの切り方の閾値は恣意的と言われ続けている **[検証済 3-0]** [V470] [V471]

1. **どんなもの？** Halfaker ら（[V470]）は、複数の領域の利用の記録で、行動の間隔の分布の規則性からセッションの切れ目を決める。Maslennikova ら（[V471]）は、学習環境の記録で、個人ごとのセッションの時間の窓を求める手法を出す。
2. **先行研究と比べてどこがすごい？** [V470] の抄録の逐語: *"Past work has argued that session identification strategies based on an inactivity threshold is inherently arbitrary or has advocated that thresholds be set at about 30 minutes."* [V471] の抄録の逐語: *"The majority of previous works address this issue by establishing an arbitrary session timeout threshold."*
3. **技術や手法の肝はどこ？** 閾値の代わりに分布や個人から決める。
4. **どうやって有効だと検証した？** 抄録の範囲では、分布の当てはめと視覚の道具。本文は読んでいない。
5. **議論はあるか？** どちらも代わりの決め方の提案で、閾値を振って下流の結論が動くかは見ていない（抄録の範囲）。論文 2 の観測区間の切り方（押下の空白 5 分・30 分）を振る根拠の 1 つになる。作文の休止の 2 秒の閾値の恣意性は既に [V161]〜[V163] にある。
6. **次に読むべき論文は？** [V423]（Hall ら・PDF は取れていない）と Wengelin 2006 の本文（作文の側で複数の閾値を並べた比べがあるかもしれない）。

### カード 3: 休止の数を数えるモデルで過分散を確かめた例はあるが、値を出した研究は見つからない **[検証済 2-1]** [V469]

1. **どんなもの？** Gullberg ら（[V469]）は、31 人の語り（話す・書く × 真・偽）の休止・ディスフルエンシー・削除の数を混合モデルで分析した。
2. **先行研究と比べてどこがすごい？** §2.8 の逐語: *"Because the dependent variables represented count data (e.g. number of pauses, disfluences or deletions), models with a Poisson distribution were used as the default. When the Poisson models exhibited overdispersion or failed to converge, a Negative Binomial distribution was employed instead"*。*"All models were checked for overdispersion using performance (version 0.15.2, Lüdecke et al., 2021)."*
3. **技術や手法の肝はどこ？** 過分散はモデルの選択の点検で、結果ではない。
4. **どうやって有効だと検証した？** 該当しない（過分散の値の報告なし。本文に "dispersion" は 2 回だけ）。
5. **議論はあるか？** 留保（1 票）: 探索は OpenAlex と WebSearch の浅いもので、本文の方法の節にだけ負の二項を使った作文・プログラミングの研究は拾えていない可能性がある（[V469] がまさにその型）。「過分散の大きさを主題にした研究は見つからなかった」までは言えるが、「誰も測っていない」とは書けない。単位（セッション・日・課題）ごとの数の揺れが数え上げを超えるかを見たものは 0 件。
6. **次に読むべき論文は？** van Duijn & Böckenholt 1995（綴りの誤りの反復の数の混合モデル・doi:10.2307/2986139・要旨だけ・打鍵ではない・未登録）。

### カード 4: 日や時刻の揺れを扱う打鍵の研究は回帰の形で、分散の分け前ではない **[検証済 3-0]** [V334] [V152] [V415] [V425]

1. **どんなもの？** BiAffect 系（[V334] など）は、スマホの打鍵の速さとその揺れを、時刻・気分の固定効果を持つ混合モデルで扱う。ETS 系（[V152]）は occasion をまたぐ特徴の安定性を問う。
2. **先行研究と比べてどこがすごい？** [V152] の要旨の逐語（サブエージェントが OpenAlex から写した・メインは未照合）: *"keystroke log features vary considerably in stability across testing occasions"*。
3. **技術や手法の肝はどこ？** 時刻・気分・課題は固定効果か回帰の説明変数。
4. **どうやって有効だと検証した？** 回帰と安定性の係数。
5. **議論はあるか？** 人・課題・日・まとまりの分散の分け前を、停滞の数と長さで出したものは 0 件。[V152] の本文に occasion の分散成分があるかは確かめていない（いちばん強い反証の候補）。
6. **次に読むべき論文は？** [V152] の本文。Zhang ら 2025（doi:10.1111/emip.12668・要旨だけ・未登録）。

---

## 否決リスト

1. **「分析者の選択で行動ログの結論が動くことを示した研究は無い」0-3**: [V468] が time-on-task で示した。論文 2 の主張は対象と見せ方に限る。

## 本ラウンドのやり残し

- [V152] の本文（occasion の分散成分の有無）。
- 作文の側で複数の休止の閾値を並べて結果を比べた研究（[V423]・Wengelin 2006・Baaijen ら 2012 の本文）。
- 要旨・検索の要約だけで登録しなかったもの: Hart ら（SIGCSE 2023・PLOS ONE 2025）・Edwards ら（SIGCSE 2022）・Khalil & Ebner（MOOC の離脱の定義を 5 通り並べた表）・Zhang ら 2025・BiAffect 系（Ross 2021・Zulueta 2018・Ning 2023）・van Duijn & Böckenholt 1995・Robitzsch 2022（教育測定の specification curve）。
- 探索は浅い（各角度 20 分）。PsyArXiv・OSF のプレプリントは探していない。
