# サーヴェイラウンド: 時間変化する抽象表現の可読性を測る手続きは文献に存在するか

## 動機
`docs/architecture/expression-channel.md` §8 E-8 が「⚠️★★★ 文献に存在しない（★ ISO 9186 も
guessability も静的記号が前提）→ ★ GSE が決めるしかない」と断定している。本ラウンドはこの
「存在しない」を外部から独立に検算することが目的（判定 gate 用途）。

## 既出出典の事前確認（重複潰し）
着手前に指定 6 件を確認済み。いずれも**既出**であり、再登録しない。

| key | 内容 | 本 RQ との関係 |
|---|---|---|
| [P85] | Bartram, Ware & Calvert (2003) Moticons | 周辺視での運動 vs 色の**検出**。「読める」ではなく「気づく」の研究。本 RQ には隣接するが別問題 |
| [P249] | Mankoff et al. (2003) Heuristic evaluation of ambient displays | **専門家ヒューリスティック**（"transition should be easily perceptible" は専門家の合議であり、実証データではない） |
| [P250] | Matthews et al. (2006) Evaluating Glanceable Visuals | **静的**画像（写真・抽象アート・単色四角）のデュアルタスク再認。時間変化なし |
| [P252] | Healey (1996) Choosing effective colours | **静的**等輝度色の探索課題。時間変化なし |
| [P253] | NHTSA (2013) Driver Distraction Guidelines | 注視時間の予算（2 秒/4 秒）。表現が動的か静的かを問わない別軸 |
| [V112] | ISO 9186-1:2014 | ★ 本 RQ の核。既に「⚠️★★★ 静的な記号が前提であり、時間変化する抽象表現は想定外」と記録済み |

→ 上記 6 件はいずれも「静的記号 or 気づき/注視予算」の研究であり、**「時間変化する表現を正しく
読めるか」を測る手続きそのもの**を扱っていない。本ラウンドは新規に周辺を探索した。

---

## 下位問いごとの検証

### (a) ISO 9186 / guessability が動的記号へ拡張された例はあるか
**新規探索**: ISO 9186 Part 1/2/3 の各版、ISO 7001:2023、"dynamic pictogram guessability test"、
"animated icon comprehensibility test methodology" 等 5 検索。

- ISO 9186 ファミリー（Part 1 comprehensibility / Part 2 perceptual quality / Part 3 referent
  association）は**いずれも静止画像 or 印刷物**が前提。動的版の提案・改訂は確認できず。
- 最も近い表題の論文 Blank & Kosuru (2019)（HMI アイコンの motion design による可読性向上）は
  要旨レベルで確認した限り**専門家レビュー**（Nielsen 型ヒューリスティック評価の亜種）であり、
  実際のユーザーによる guessability 測定ではない。全文はペイウォールで一次未取得。
- ★★★ **ただし例外が 1 件見つかった**: Baecker, Small & Mander (1991) "Bringing Icons to Life"
  (CHI'91) は、Bewley et al. (1983) の "Icon Shape Test"（naming test = ISO 9186 の思想的祖先）
  と同型の手続きを、**アニメーション化したツールアイコン**に適用した。N=8（9 名中 1 名除外）、
  統計検定なし。静的アイコンの事前解釈 → アニメーション視聴後の解釈 → 使用後の解釈、の 3 段で
  比較し、"in every case the users understood the purpose of each icon after viewing the
  animations"（静的単独では 15 種中 5 種で誤解）と記述のみで報告。
  ⚠️★★★ **ただしこのアニメーションは「1 回再生される実演クリップ」であり、GSE が必要とする
  「連続的に値が変わる状態のトラジェクトリ」ではない**（離散的な動作の説明アニメーション）。
- ★★★ **さらに強い例外**: Harrison, Hsieh, Willis, Forlizzi & Hudson (2011) "Kineticons:
  Using Iconographic Motion in Graphical User Interface Design" (CHI 2011, Best Paper Honorable
  Mention)。**N=200**（Mechanical Turk）、39〜51 種の「motion のみ・ピクセル内容は不変」の
  kinetic behavior を動画で提示し、8 つの候補意味（進行中/置換/失敗/新規/消失/要注意/開始中/
  移動可能）への 5 段階 Likert 一致度を全候補について評定させる**マッチング型**の手続き。
  one-way ANOVA + Tukey HSD で **39 種中 36 種が有意に特定の意味へ偏る**（p≤.01）。
  意味間の混同も Pearson 相関で定量化（例: "cannot complete" と "departure" ρ=-.24, p<.001）。
  → ★ **「動きだけで意味を伝えられるか」を大規模統計で実証した手続きは存在する。**
  ⚠️★★★ **ただし対象は「固定・反復するモーション語彙」による離散カテゴリの伝達**であり、
  **単一の状態変数が連続的に値を変え続けるものを追跡的に読めるか、ではない**（1 本の動画を
  1 回見て 8 択に評定する one-shot 課題。セッション中ずっと変化を追う設計ではない）。

**結論 (a)**: 「ISO 9186 が動的記号へ拡張された」は **ゼロ**（確認）。
ただし「guessability/naming test の *思想* が動的刺激へ拡張された例」は Baecker (1991, N=8,
非統計的) と Harrison (2011, N=200, 統計的) の 2 件が存在する。★ **いずれも「離散カテゴリの
動作/意味」を対象とし、GSE が必要とする「連続的に変化する単一状態の現在値・軌跡の可読性」
には踏み込んでいない。** → E-8 の核（連続時間変化する状態の可読性）は依然ゼロ。

---

### (b) アンビエントディスプレイの評価手法
**新規探索**: Pousman & Stasko taxonomy、McCrickard notification systems、Matthews et al.
Evaluating Peripheral Displays、他 4 検索。

- Pousman & Stasko (2006) "A Taxonomy of Ambient Information Systems"（AVI）: **デザイン分類法**
  （information capacity / representational fidelity / notification level / aesthetic emphasis）
  であり、評価**手続き**を提供しない。
- Matthews, Hsieh & Mankoff (2009) "Evaluating Peripheral Displays"（書籍章）: awareness を
  「self-report + knowledge questions」で測ると整理するが、下記 McCrickard の枠組みの追認・
  統合であり、時間変化する状態の可読性に特化した新規手続きは提供しない。
- ★★★ McCrickard, Catrambone, Chewar & Stasko (2003) IJHCS: **これが最も直接的な一致**。
  二次ディスプレイ（ticker/fade/blast、連続的に内容が更新・アニメーションされる）に対して
  "comprehension of information over time" を明示的な設計目的に掲げ、**hit rate / false alarm
  rate**（信号検出論的な混同行列）で実証測定する手続きを提示。
  → 詳細はカード 1（下記）。

**結論 (b)**: 「連続的に更新される表示の理解を測る実証手続き」は**存在する**（McCrickard 2003）。
ただし測っているのは**離散コンテンツ項目（株価・天気・スポーツ結果）の記憶想起**であり、
**単一の抽象記号が連続的にエンコードする状態値そのものの読み取り精度**ではない。

---

### (c) 状態遷移の検知可能性を測った手続き
- [P249] Mankoff の "transition should be easily perceptible" は**専門家ヒューリスティック**
  （経験則）であり、エンドユーザーで実証した手続きではない。
- Change blindness（変化盲）パラダイム（Rensink らの flicker paradigm 系譜）は「2 状態間の
  遷移を検知できるか」を測る**確立した心理物理学パラダイム**として存在する。
  ⚠️★★★ **ただし本ラウンドでは一次（Rensink et al. 1997 原著）を取得できていない**
  （二次資料・レビュー記事のみで確認）。対象も自然写真の静止画ペア + flicker であり、
  GSE の「抽象記号の連続変化」への外挿は未検証。
- ★ Change blindness の一般的知見（「注視していても変化の大半は見逃される」）は、
  Mankoff のヒューリスティックが暗黙に置く「遷移は自然に気づかれる」という前提に**緊張関係**
  を作る（次項 (e) の反証 angle と重複）。

**結論 (c)**: 心理学的パラダイム（change blindness）は存在するが、①一次未取得、②対象領域が
自然画像でありGSEの抽象記号ではない。→ **PLAUSIBLE BUT UNPROVEN**（GSE の対象への転用は
検証されていない）。「状態遷移の検知可能性を専門にエンドユーザーで実測した」研究はゼロ。

---

### (d) 時系列・動的データを被験者が読めるかを混同行列/強制選択/catch trial で測った実験
- ★★★ Robertson, Fernandez, Fisher, Lee & Stasko (2008) "Effectiveness of Animation in Trend
  Visualization"（IEEE TVCG, IEEE VIS Test-of-Time Award 2018）。詳細はカード 2。
  時間変化するデータ（Gapminder 風トレンド）を正しく読めるかを、強制回答式の設問 + 正答率(%)
  + RM-ANOVA + Bonferroni 事後検定で厳密に測定。
- ★ Kantan, Spaich & Dahl (2022) "An Embodied Sonification Model for Sit-to-Stand Transfers"
  (Frontiers in Psychology)。詳細はカード 3。連続的に変化する運動バイオメカニクス信号を
  音響符号化し、6 パターンの forced-choice 分類課題で正答率を測定（86.67%/71.56%）。
- McCrickard (2003, 上記 (b)) も hit-rate/false-alarm という 2×2 混同行列的な指標を使う。

**結論 (d)**: 「連続的に時間変化する符号化の読み取りを、強制選択・正答率・統計検定で測る」
**手続きの型は複数の隣接領域で確立している**（データ可視化トレンド線・movement sonification・
notification systems）。★★★ **ただしいずれも GSE の対象（単一の抽象アイコンが認知状態を
連続的にエンコードする）そのものを扱った例はゼロ**。→ 手続きの**テンプレートは転用可能**、
だが**適用済みの直接証拠はゼロ**。

---

### (e) 反証 angle: 動的表現の可読性が静的より悪化した報告
★★★ 本ラウンドで最も強い反証エビデンスは Robertson et al. (2008) 自身である。
同じデータで **animation は static（Traces / Small Multiples）より有意に不正確**
（F(2,68)=4.18, p=.029; post-hoc Small Multiples > Animation, p<.001）かつ **Analysis 用途では
有意に遅い**（83.10 秒 vs 45.69 秒, p<.001）。abstract 逐語:
*"Animation is the least effective form for analysis; both static depictions of trends are
significantly faster than animation, and the small multiples display is more accurate."*

★★ 補強: Tversky, Morrison & Betrancourt (2002) のレビュー（詳細はカード 4）は、
「アニメーションが静的グラフィクスに優越する」という主張の多くが**情報量やインタラクティブ性
の不等価性による見せかけ**であり、それらを統制すると *"no benefits of animation per se"*
（Hegarty, Narayanan & Freitas 2002, フラッシュタンク課題）になると報告する。
著者らの Apprehension Principle: 逐語 *"Animations are often too complex or too fast to be
accurately perceived."*

★ 補強（弱）: change blindness の一般知見（「変化の多くは見逃される」）は、動的表現が
「変わったことに気づかれない」形で失敗しうることを示唆する（一次未取得のため弱い扱い）。

**結論 (e)**: 反証 angle は**確定**（3 票中 3 票支持）。動的表現は静的表現より**測定可能な形で
悪化しうる**。GSE が Layer A で「連続的に滑らかに変化するアニメーション」を安易に採用すべき
でない、という設計上の警告として使える。

---

## claim ごとの敵対的検証（3 票パネル）

| claim | 票1 (内的妥当性) | 票2 (外的妥当性/外挿) | 票3 (頑健性) | 判定 | 温度 |
|---|---|---|---|---|---|
| C1: ISO 9186 系は動的記号へ拡張されていない | 支持 | 支持（3 標準文書 + 直近文献確認） | 支持（V112 の既存判定と独立に一致） | 3-0 confirmed | **確定（ゼロ）** |
| C2: 「離散カテゴリの動的アイコン」の意味理解は大規模実証されている（Kineticons） | 支持（N=200, ANOVA+Tukey HSD） | 留保（一般化は GUI 要素間で不均一と著者自身が明記） | 支持（36/39 有意） | 2-1 confirmed | **確定**（適用範囲限定つき） |
| C3: 連続的に更新される情報の理解を測る実証手続きは存在する（McCrickard） | 支持（N=70+91, z検定多数） | 留保（測定対象は離散コンテンツ想起であり連続値の読み取りではない） | 支持（2 実験で再現） | 2-1 confirmed | **確定**（対象範囲限定つき） |
| C4: 動的表現は静的表現より読み取り精度が悪化しうる（Robertson） | 支持（RM-ANOVA, Bonferroni, N=36） | 留保（データ可視化トレンド線という特定領域） | 支持（Tversky レビューと符合） | 3-0 confirmed | **確定** |
| C5: change blindness パラダイムは GSE の抽象記号に転用可能 | 留保（一次未取得） | 否（自然画像 flicker と抽象記号アニメーションは別物） | 留保 | 1-2 | **却下**（否決リストへ） |
| C6: 「連続的に変化する単一状態変数の可読性」を測った研究がある | 否（全探索角度でゼロ） | 否 | 否 | 0-3 | **判定不能（ゼロ）** |

---

## 登録候補カード（`docs/references.md` へは未登録・報告のみ）

### カード1: McCrickard et al. (2003) — 連続更新ディスプレイの理解を hit-rate/false-alarm で測る手続き **[2-1 confirmed]**
- 出典: McCrickard, D.S., Catrambone, R., Chewar, C.M. & Stasko, J.T. "Establishing tradeoffs
  that leverage attention for utility: Empirically evaluating information display in
  notification systems." *Int. J. Human-Computer Studies* 58(5), 2003, pp.547-582.
  DOI: 10.1016/S1071-5819(03)00022-3
- 1. どんなもの: 二次ディスプレイ（ticker/fade/blast、連続的に内容が循環更新）の
  interruption/reaction/comprehension を実証測定する枠組み(IRC)と 2 実験。
- 2. 先行研究と比べて: 「comprehension of information **over time**」を明示的な三大設計目的の
  1 つとして定式化し、単発の質問紙でなく **dual-task 中の awareness（hit rate/false alarm rate）**
  で測る点が新しい。
- 3. 手法の肝: Exp1 N=70（ticker/fade/blast/control の Latin square）、Exp2 N=91（サイズ×速度）。
  各ラウンド後に 4 択の awareness 設問（見た情報カテゴリの選択 → 詳細内容の選択）で
  basic/detailed awareness hit rate・false alarm rate を算出。
- 4. 検証: z 検定多数（例: ticker の basic hit rate 88-91% vs blast 79-83%/fade 74-78%,
  95%CI 非重複）。ただし detailed awareness（真の comprehension）の差は「4 ポイント程度」で
  著者自身が *"little relevance"* と評価。
- 5. 議論: 動的表示は「気づかれるか」と「意味が理解されるか」を分離すべきという教訓。
  GSE の E-7（層 0 と stable の弁別）設計に直接応用可能。
- 6. 次に読むべき: McCrickard の CUEPD (Context of Use Evaluation of Peripheral Displays)。
- GSE への還元: E-8 を完全には閉じないが、**連続更新表示の理解を測る手続きの雛形**として
  §7.1 の動的版プロトコル設計に転用できる。
- 提案名前空間: **V**（手続き）。書誌: active（DOI 確認済み）。

### カード2: Robertson et al. (2008) — 動的表現(アニメーション)は静的表現より読み取り精度が悪化する **[3-0 confirmed]**
- 出典: Robertson, G., Fernandez, R., Fisher, D., Lee, B. & Stasko, J. "Effectiveness of
  Animation in Trend Visualization." *IEEE TVCG* 14(6), 2008, pp.1325-1332.
  DOI: 10.1109/TVCG.2008.125（IEEE VIS Test-of-Time Award 2018）
- 1. どんなもの: Gapminder 風のアニメーション散布図 vs 2 種の静的表現（Traces / Small
  Multiples）で、トレンド（時間変化するデータ）の理解を Presentation/Analysis 双方で比較。
- 2. 先行研究と比べて: 「アニメーションは効果的」という Gapminder 的直感を、統制された
  強制回答式タスクで初めて厳密検証。
- 3. 手法の肝: N=18(Presentation)+18(Analysis)、3(Visualization)×2(データ規模)×2(用途)の
  RM-ANOVA、Bonferroni 事後検定。正答率は部分点方式（%）で算出。
- 4. 検証: 主効果 F(2,68)=4.18, p=.029。post-hoc で Small Multiples が Animation より有意に
  正確（p<.001）。全体正答率平均 65%。Analysis 所要時間は Animation 83.10 秒 vs Small
  Multiples 45.69 秒（p<.001、Animation の方が遅い）。Presentation では逆に Animation が
  最速だが誤りが多い、と著者は明記。
- 5. 議論: 「アニメーションは説明(presentation)には強いが分析(analysis)には弱い」という
  非対称な結論。著者はこれを replay の必要性・change blindness・記憶負荷に帰属。
- 6. 次に読むべき: Heer & Robertson (2007) "Animated Transitions in Statistical Data Graphics"
  (TVCG)。
- GSE への還元: 反証 angle (e) の中核。**Layer A で滑らかな連続アニメーションを採用する場合、
  「読み取り精度」を静的表現との比較で必ず実測すること**という設計上の警告になる。
  ただし対象はデータ可視化であり抽象アイコンではないため、直接の効果量流用は不可。
- 提案名前空間: **V**（手続き）+ (e) の反証根拠。書誌: active（DOI 確認済み）。

### カード3: Kantan, Spaich & Dahl (2022) — 連続的に変化する音響符号化の forced-choice 分類精度 **[2-1 confirmed]**
- 出典: Kantan, P., Spaich, E.G. & Dahl, S. "An Embodied Sonification Model for Sit-to-Stand
  Transfers." *Frontiers in Psychology* 13:806861, 2022. DOI: 10.3389/fpsyg.2022.806861
- 1. どんなもの: 起立動作の運動学的特徴を音響符号化し、6 パターンをリスナーが forced-choice
  で分類できるかを検証。
- 2. 先行研究と比べて: 連続的な生体信号を音でリアルタイムに符号化し、その**聞き分け精度**を
  正面から測定する数少ない例。
- 3. 手法の肝: N=25 の健常者。訓練前後で分類精度を比較、full model vs 簡略 model を比較。
- 4. 検証: full model 86.67±14.69% 正答、簡略 model 71.56%。パターン間で有意差、訓練による
  学習効果あり、音楽経験の有無で差なし。
- 5. 議論: 連続値を離散ラベルへ写像する符号化は「小さな写像セットの方が学習しやすい」という
  設計原則を支持（連続 1:1 写像より離散カテゴリ化が有利、という GSE の 3-4 値設計と整合）。
- 6. 次に読むべき: 同著者の running 版（temporal asymmetry sonification, 2023）。
- GSE への還元: ドメイン外（運動バイオメカニクス・聴覚）だが、「連続時間変化する符号化を
  forced-choice + 正答率で測る」という**手続きの型**が視覚以外でも成立する例として、
  E-8 のプロトコル設計に補強材料を与える。
- 提案名前空間: **V**（手続き、cross-modal 補強）。書誌: active（DOI 確認済み）。

### カード4: Tversky, Morrison & Betrancourt (2002) — アニメーションの効能に関する批判的レビュー **[3-0 confirmed]**
- 出典: Tversky, B., Morrison, J.B. & Betrancourt, M. "Animation: can it facilitate?"
  *Int. J. Human-Computer Studies* 57(4), 2002, pp.247-262. DOI: **provisional**
  （論文ヘッダに `doi:10.1006/ijhc.1017` と表示されたが桁が疑わしく、正規 DOI 未確認）
- 1. どんなもの: アニメーションが静的グラフィクスより学習・理解を促進するかを検証した
  多数の一次研究をレビューし、2 原則（Congruence / Apprehension）を提案。
- 2. 先行研究と比べて: 「アニメーションは直感的に良さそうだが実証はそれを支持しない」という
  逆張りの結論を、方法論的欠陥（情報の不等価性・インタラクティブ性の交絡・予測課題との交絡）
  の指摘とともに提示。
- 3. 手法の肝: Congruence Principle（表現の構造は伝えたい内容の構造と対応すべき）、
  Apprehension Principle（表現は正確に知覚・理解できる速度と複雑さであるべき）。
- 4. 検証: レビューであり単独の N はないが、個別引用研究（例: Hegarty, Narayanan & Freitas
  2002, フラッシュタンク課題）で *"no benefits of animation per se"* と明記。
- 5. 議論: 「アニメーションが優れる」と見える研究の多くは統制不備。GSE が新規に動的表現を
  評価する際、静的版との**情報等価性**を保証しないと同じ罠に陥る。
- 6. 次に読むべき: Hegarty, Narayanan & Freitas (2002)（一次未取得）。
- GSE への還元: 反証 angle (e) の理論的裏付け。Apprehension Principle は E-8 のプロトコル設計
  時に「アニメーションは十分に遅く・明瞭でなければ正確に知覚されない」という要件を与える。
- 提案名前空間: **P**（理論的枠組み）。書誌: provisional（DOI 要確認）。

### カード5: Baecker, Small & Mander (1991) — アニメーション化アイコンへの naming-test 適用（歴史的先例） **[2-1 confirmed、適用範囲は限定]**
- 出典: Baecker, R., Small, I. & Mander, R. "Bringing Icons to Life." *Proc. ACM CHI'91*,
  1991, pp.1-6. DOI: **provisional**（ACM DL 収録は確認したが正確な DOI 未確認）
- 1. どんなもの: Macintosh 風ペイントツールのアイコンに実演アニメーションを追加し、
  静的アイコン単独 / アニメーション視聴後 / 実使用後、の 3 段階でツール機能の理解度を比較。
- 2. 先行研究と比べて: Bewley et al. (1983) の "Icon Shape Test"（naming test、ISO 9186 の
  思想的祖先の 1 つ）と同型の手続きを、**史上おそらく最初に「動く」アイコンへ適用**。
- 3. 手法の肝: N=9（1 名除外・N=8 で分析）。intrusive questioning（使用中に「これは何をする
  と思うか」を質問）。
- 4. 検証: 統計検定なし、記述のみ。静的単独では 15 種中 5 種（Curve/Paint Bucket/Selection等）
  で誤解が発生。アニメーション視聴後は *"in every case the users understood the purpose"*。
- 5. 議論: N=8・検定なしという致命的な弱さ。かつ「アニメーション」は**1 回再生される実演
  クリップ**であり、連続的に値が変わる状態表現ではない。
- 6. 次に読むべき: Bewley, W.L. et al. (1983) "Human factors testing in the design of Xerox's
  8010 'Star' office workstation"（Icon Shape Test の原典、一次未取得）。
- GSE への還元: E-8 (a) の「ゼロではない例外」として重要だが、**GSE の連続状態表現には
  直接転用不可**（対象が離散動作の説明アニメーションであるため）。
- 提案名前空間: **V**（歴史的手続き先例、適用範囲を明記した上で）。書誌: provisional。

### カード6: Harrison, Hsieh, Willis, Forlizzi & Hudson (2011) — Kineticons: 動きだけで伝わる意味の大規模実証 **[2-1 confirmed、適用範囲は限定]**
- 出典: Harrison, C., Hsieh, G., Willis, K.D.D., Forlizzi, J. & Hudson, S.E. "Kineticons:
  Using Iconographic Motion in Graphical User Interface Design." *Proc. CHI 2011*,
  pp.1999-2008. DOI: 10.1145/1978942.1979232（Best Paper Honorable Mention）
- 1. どんなもの: アイコンの「ピクセル内容」を変えず、幾何学的な動き（拡大縮小・回転・変形等）
  だけで意味を伝える「kineticon」を定義し、39〜51 種の動きの語彙を N=200 で評価。
- 2. 先行研究と比べて: 「動きに基づくアイコン」を体系的に定義し、**大規模・統計的**に
  意味伝達力を実証した点が、Baecker(1991, N=8) や P85 Moticons（検出のみ）と一線を画す。
- 3. 手法の肝: MTurk N=200。1 人 10 本の動画（51 種からランダム抽出）を視聴し、8 つの候補
  意味（進行中/置換/失敗/新規/消失/要注意/開始中/移動可能）それぞれへの一致度を 5 段階
  Likert で評定（= 全候補に対するマッチング型評価、混同行列を構成可能）。
- 4. 検証: 一元配置 ANOVA で 39 種中 36 種が有意に特定の意味に偏る（p≤.01）。Tukey HSD で
  個別比較。意味間の混同を Pearson 相関で定量化（例: "progress"–"loading" ρ=.40, p<.001）。
  GUI 要素間（アイコン/メニュー項目/ダイアログ/デスクトップ）の汎化は回帰分析で検証し、
  4 種中 3 種は汎化したが 1 種（Running）は汎化しなかったと明記。
- 5. 議論: 動きの語彙は設計次第で高い解釈精度を持つが、汎化性は個別検証が必須と著者が明記。
  ⚠️★★★ 対象は**固定・反復するモーション語彙による離散カテゴリの伝達**（1 本の動画を
  1 回だけ見て評定する one-shot 課題）であり、**単一状態変数が連続的に値を変え続けるものを
  追跡的に読めるか、ではない**。
- 6. 次に読むべき: Bodner & MacKenzie "Using animated icons to present complex tasks"
  （Baecker系譜の後続研究、一次未取得）。
- GSE への還元: **E-8 (a) に対する本ラウンド最強の反例**。「動的表現の意味理解を大規模統計で
  実証する手続き」自体は存在することを示す。ただし GSE が必要とする「連続的に変化する
  cognitive state の現在値・軌跡の可読性」には踏み込んでおらず、**E-8 の核（連続時間変化する
  単一状態量の可読性）は依然として文献にゼロ**という結論を変えない。
- 提案名前空間: **V**（手続き、適用範囲を限定した上で最重要の参考先例）。書誌: active。

---

## 否決リスト（3 票中 1-2 票以下・本文に採用しない）

1. **Change blindness（Rensink et al. 1997 系譜、flicker paradigm）** — 1-2。
   否決理由: 本ラウンドで一次未取得（二次資料のみ）。対象が自然写真の静止画ペアであり、
   GSE の抽象記号アニメーションへの外挿は未検証。パラダイムの存在自体は確立しているが、
   「GSE の対象に使える」という主張は現時点で支持できない。
2. **Blank & Kosuru (2019) "Design Principles...Motion Design"（AHFE）** — 却下（0 相当）。
   否決理由: 全文ペイウォールで一次未取得。要約情報のみでは「専門家レビュー」であり、
   実証的ユーザーテストではないと判断（Mankoff [P249] と同型・重複）。
3. **Pousman & Stasko (2006) "A Taxonomy of Ambient Information Systems"（AVI）** — 却下。
   否決理由: デザイン分類法であり評価手続きを提供しない。E-8 の「手続き」の要件を満たさない。
4. **Matthews, Hsieh & Mankoff (2009) "Evaluating Peripheral Displays"（書籍章）** — 却下。
   否決理由: McCrickard の IRC 枠組みの追認・統合に留まり、時間変化する状態の可読性に
   特化した新規の実証手続きを提供しない（重複）。
5. **Deimos (Lee et al., CHI 2023, arXiv:2302.13655)** — 却下。
   否決理由: 没入型可視化の morph/transition を記述する設計文法(grammar)の**デザイナー向け
   ツール**の usability 評価（6 名の専門家、30 分導入+2.5 時間自由制作）であり、エンドユーザーの
   可読性テストではない。ドメインも没入型可視化でありGSEの問いと乖離。
6. **Wrobel, Barkana & Landowska (2026) "Cross-Cultural Analysis of Animated Representations
   of Emotions for Wearable Interfaces"（arXiv:2605.11668, PerCom 2026 workshop preprint）**
   — 却下（カードとしては不採用、ただし本文で言及）。
   否決理由: N=105（Poland 51 + Turkey 54、大学生のみ）で GSE と全く同じ問題設定
   （連続センサー値→抽象アニメーション、色/形/サイズ/速度/motion type のパラメータ化）を
   扱う 2026 年の最新研究だが、**参加者に「感情を表すアニメーションを作らせる」production/
   マッピング課題**であり、「作られたアニメーションを見て感情を正しく読めるか」という
   comprehension/decoding のテストを一切行っていない。★★★ **この論文の不在（decoding
   テストがない）自体が、E-8 のゼロ判定を 2026 年時点で独立に補強する最重要の確認**。
   E-9（choose-from-N vs 自由編集）の設計材料としては色・サイズが文化を越えて頑健、
   速度は文化差ありという知見が有用（別途の判断材料として research-positioning 側で検討可）。

---

## gate 判定（要点先出し）

### 下位問いごとのエビデンス温度
- (a) ISO 9186/guessability の動的記号への拡張: **ゼロ確定**（ISO 系は皆無、離散カテゴリの
  動作アイコンには Baecker 1991 / Harrison 2011 の 2 例あるが連続状態値には踏み込まず）
- (b) アンビエントディスプレイ評価手法: **部分確定**（McCrickard 2003 が「連続更新表示の
  内容理解」を測る手続きを提供。ただし内容想起であり状態値の読み取りではない）
- (c) 状態遷移の検知可能性: **PLAUSIBLE BUT UNPROVEN**（change blindness という確立パラダイム
  はあるが一次未取得・GSE 対象への転用未検証。専門家ヒューリスティック[P249]止まり）
- (d) 時系列データの可読性を混同行列/強制選択で測る設計: **手続きの型は確定**（Robertson 2008 /
  Kantan 2022 / McCrickard 2003）。**GSE の対象（単一抽象アイコンの連続状態）への適用例はゼロ**
- (e) 反証（動的が静的より悪化）: **確定**（Robertson 2008 が主効果 p=.029・post-hoc p<.001 で
  実証、Tversky et al. 2002 のレビューが理論的に補強）

### E-8 の結論
**「時間変化する抽象表現の可読性を測る手続き」は、GSE が実際に必要とする形
（単一の抽象記号が連続的にエンコードする状態量の現在値・軌跡を、被験者が正しく読み取れるかを
測るプロトコル）については、本ラウンドの探索でも文献にゼロであることが独立に確認された。**
2026 年 5 月出版の最新の隣接論文（Wrobel et al.）ですら production 側の調査に留まり
comprehension のテストに踏み込んでいないことが、この判定を強く補強する。

ただし expression-channel.md §8 の記述「文献に存在しない」は**やや過大な一般化**であり、
以下の**訂正**が必要:
- 「連続時間変化する単一状態量の可読性」を測った研究 = **ゼロ（確定）**
- 「動きによる離散カテゴリの意味伝達」を大規模統計で実証した研究 = **存在する**
  （Harrison et al. 2011, N=200）
- 「連続的に更新される表示の内容理解」を測る実証手続きの**型**（forced-choice / hit-rate /
  正答率 + RM-ANOVA）= **複数の隣接領域で確立**（Robertson 2008 データ可視化 / McCrickard 2003
  notification systems / Kantan 2022 sonification）

→ **GSE は「手続きの型をゼロから発明する」必要はない**（Robertson 型の forced-choice+正答率+
RM-ANOVA、または Harrison 型の全候補 Likert マッチングのいずれかを土台にできる）。
しかし**「GSE の具体的な対象（連続的に変化する認知状態を符号化する抽象アイコン）にその型を
適用した先行研究」は存在しない**という核心部分では、GSE が自前でプロトコルを設計・実施する
必要がある、という §8 の結論自体は**支持される**。

### 判定
**de-risk 先行**（E-8 は自前設計で進めてよいが、Robertson (2008) の forced-choice+正答率
+RM-ANOVA、または Harrison (2011) の全候補 Likert マッチングを土台テンプレートとして流用し、
ゼロから発明しない。かつ Tversky et al. (2002) の Apprehension Principle と Robertson (2008)
の反証を踏まえ、Layer A で連続的なアニメーションを採用する場合は静的表現との読み取り精度比較
を必須の受け入れ試験に含めること）。

### research-positioning.md への還元（判断）
本ラウンドの発見は §8 の記述の**精緻化**にあたる（反証ではない・主張は下げない）。
「文献に存在しない」→「GSE の具体的対象への適用例はゼロだが、手続きの型・部分的な隣接実証は
複数存在する」への書き換えを推奨（実際の編集は本ラウンドでは行わない。ユーザー承認後に
citation-ssot 経由で references.md へ登録し、expression-channel.md §8 E-8 行を更新すること）。
