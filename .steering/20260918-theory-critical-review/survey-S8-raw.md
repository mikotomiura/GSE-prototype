# S8 生報告の退避（S8-a / S8-b）—— ⚠️ 未検証。3 票検証の入力

> 2026-09-19。サブエージェント（Opus）の報告。⚠️ S8-a は逐語を抽出テキストの行番号で示した（引用制限のため）。
> ★ 取得済み本文: `C:\Users\johnd\AppData\Local\Temp\s8lit\*.txt`（pypdf 抽出）—— カード化の前にメインが逐語を照合する。

## S8-a（burst の定義と個人化閾値）

### ⚠️ 前提の訂正（メインの依頼文の誤り）
- 依頼文は [P123] を「Chukharev-Hudilainen の指摘」と書いたが、**[P123] は Rosenqvist 2015（Umeå 大学の学士論文）**。Chukharev-Hudilainen 2014 は未登録で、しかも本人は作文研究について固定閾値を容認している（p.66 *"it is safe to establish a (somewhat arbitrary) cut-off value for pauses"*）。個人化を求めたのは自発的なチャットの場合に限る。

### 文献表
| 著者 年 | 題名 | DOI | 設計・N | 範囲 |
|---|---|---|---|---|
| Roeser, De Maeyer, Leijten & Van Waes 2024（online 2021） | Modelling typing disfluencies as finite mixture process（Reading and Writing） | 10.1007/s11145-021-10203-z | ベイズ混合・コピー課題・オランダ語・N=250 | 全文 |
| Baaijen, Galbraith & de Glopper 2012 | （S7 と共通） | 10.1177/0741088312451108 | N=80 | 全文 |
| Chukharev-Hudilainen 2014 | Pauses in spontaneous written communication: a keystroke logging study（Journal of Writing Research 6(1)） | 10.17239/jowr-2014.06.01.3 | ロシア語チャット・ex-Gaussian・N=36 | 全文 |
| Alves, Castro, de Sousa & Strömqvist 2007 | Influence of typing skill on pause–execution cycles in written composition（*Writing and Cognition*, Brill） | 10.1163/9781849508223_005 | ScriptLog・N=21 を打鍵速度で 2 群 | 章全文 |
| Almond et al. 2012 / Deane & Zhang 2015 / Deane et al. 2018 | （S7 と共通） | — | — | — |
| Torrance & Conijn 2023 | Methods for studying the writing time-course（Reading and Writing・特集号序論） | 10.1007/s11145-023-10490-8 | レビュー | 全文 |
| Bandaru, Carl & Ren 2026 | Assessing pause thresholds…（arXiv:2604.01410） | arXiv（DOI なし） | 翻訳 478 セッション・GMM | extended abstract |
| Dux Speltz, Roeser, Bouwman, Chukharev & Torrance 2026 | Writing traits: consistency…（採録版） | DOI 未確認 | N=30・論証 3 課題 | 採録版全文 |
| Kim 2022 | Do written language bursts mediate…（Written Communication） | 10.1177/07410883211068753 | 二次引用源 | 該当頁 |
| Chenoweth & Hayes 2001 / Hayes 2012 / Kaufer et al. 1986 | — | 10.1177/0741088301018001004 / 10.1177/0741088312451260 / 10.58680/rte198615612 | — | abstract のみ／未取得 |
| Crotti et al. 2026（Hylog） | [V5] 既登録 | 10.1109/ACCESS.2026.3718565 | — | 該当節 |

### 定義（言い換え・行番号）
- P-burst / R-burst: 2 秒以上のポーズで終わる = P、評価・修正・文法的不連続で終わる = R（Kaufer 1986 を Baaijen 2012 p.250 が再掲 ＝ **二次**・`baaijen2012.txt:215`）。★ burst は**終わり方だけで定義されている**という批判（p.252–253, `:316`）
- C&H 系の burst の「2 秒超」は Kim 2022 が括弧で補ったもの（`kim2022.txt:52-58`）→ 原典の閾値は未確認
- execution period: 2 秒の非活動で区切られ 1 語以上を含む打鍵区間。1 秒では遅い群のポーズを拾えないため 2 秒に上げた（Alves 2007 p.58/p.60）
- ETS burst: 編集イベントを除いた列で IKI < 2/3 秒が続く部分。閾値は「学生ごとの語間ポーズ中央値の学生間中央値（約 0.6 秒）より少し上」（Almond 2012 p.15・脚注 7 p.53）
- 非定常ポーズ: 語間ポーズを対数正規 3 成分に分解し、第 2 成分の平均＋3SD 超を極端ポーズ。個人ごとに BIC で成分数（3 成分 58%・2 成分 19%・判定不能 23%）（Baaijen 2012 pp.263–264）
- tpause = ex-Gaussian の μ+τ+3σ。個人値 358–810 ms・平均 492 ms（Chukharev-Hudilainen 2014 p.76–77）
- 非流暢な打鍵遷移: 2 成分対数正規混合。混合比 θ は参加者ごと、遅れ幅 δ は母集団共通（Roeser 2024 式 7 p.369）
- long pause（ETS RM-18-06）: 書き手ごとの IKI 中央値より 4SD 以上（p.10）⚠️ 同報告 p.49 では「>2 s」—— 報告内で揺れる
- PUB（分位点型）: 個人 IKI の上位 1/(平均語長×3 語) 分位 ≒ 英語で 5.5%（Bandaru 2026 p.2）

### claim
- 固定閾値は原理的に恣意的で、個人・課題・テキスト上の位置に依存すべき（Roeser 2024 pp.360–362）
- 2 秒には理論的根拠がなく 250 ms〜10 s のどこに置いても同じ理屈が立つ（Torrance & Conijn 2023 p.243）
- **個人差として現れるのは非流暢の確率 θ であり、遅れの大きさ δ ではない**（Roeser 2024 pp.376–377）
- **θ は 2 課題間で相関しない**（Roeser 2024 p.376 Fig.5e・p.377。⚠️ コピー課題に限る —— 著者が一般化の限界を認める p.380）
- **burst 長は打鍵速度と交絡**: 速い群 11.6 s・5.4 語 ／ 遅い群 7.7 s・2.5 語、ポーズ数 184 対 358、1 回あたりのポーズ長は差なし（Alves 2007 Table 2 p.61・N=21）
- P-burst 長は書き方の戦略を反映しうる。被験者内では 85%/96% に有意な関連なし（Baaijen 2012 p.252, p.265）
- **burst 長は語数で測ると形式間で比較的安定（r .48–.85）、時間 ms で測ると不安定（.15–.57）**。文間ポーズは .09–.24（Deane & Zhang 2015 Table 5 p.9 ※特徴は burst 長の SD）
- 閾値は一般基準ではなく個々の書き手の特性に対して設定できる（Baaijen 2012 p.271）
- 混合モデルは短いログで収束しにくい: burst 長で 18/64 が 1 成分に縮退、BIC は残り 46 中 41 で単純なモデル（Almond 2012 p.27）
- PUB の妥当化は GMM 上側閾値との相関だけ（Pearson .58 / Spearman .68）（Bandaru 2026・extended abstract）
- ポーズ傾向を含む打鍵プロファイルは課題間で偶然以上に安定（16/30 名が 3 課題とも同じクラスタ）（Dux Speltz 2026・abstract）
- L2 経験で burst 長が伸びる（Chenoweth & Hayes 2001・abstract）
- 通常のキーロガーは IME 経由の入力で語境界を誤認し IKI が系統的に歪む（[V5] pp.4–5）

### サブエージェントの推論（文献の主張ではない）: GSE の p99 との比較
- 利点: 分布の仮定が不要・混合モデルのような収束失敗が無い・個人にスケール・分位点型の先例（PUB）
- 欠点 1: 分位点を固定すると超過割合が構造上 1% に固定され、実際に個人差・課題差として動く θ（Roeser 2024）を表現できない
- 欠点 2: p99 は既存のどの pause 定義よりはるかに極端（Baaijen の極端ポーズ群でも語間ポーズの約 9%）。p99 で切った burst は文献上の P-burst と別物で、この水準の検証例は無い
- 欠点 3: IKI はテキスト上の位置で数十倍違う（語内 90 ms 〜 文間 2,981 ms, Baaijen Table 3 p.264）。GSE は直前のキー種別で近似するしかない（[P121] と整合）
- 欠点 4: 日本語 IME では確定前後の遷移が上側の裾を占めるおそれ（[V5] からの外挿）

### 見つからなかったもの
- 書字研究で log-survivor / bout criterion（Sibly 型）を IKI に適用した研究: **0 件**
- 日本語 IME の作文で burst / ポーズ閾値を扱った研究: **0 件**
- 「窓内の純産出（挿入 − 削除）< 1」の形で再開・再停止を操作化した先行研究: **0 件**（近いのは Backspace を burst 内に許す ETS 定義と R-burst）
- 未読の手がかり: Hall et al. 2022・Chenu et al. 2014・Li 2021・Roeser et al. 2025（JEP:G, 10.1037/xge0001759）・ETS 特許 US11195431（「中央値 IKI の 4 倍」）

## S8-b（中断・再開研究と bout 解析）

> 取得済み本文: `C:\Users\johnd\AppData\Local\Temp\s8lit\`。逐語つき。

### 要点（主張を狭める方向）
- **bout 解析だけでは「連結」の根拠にならない** —— bout criterion が決めるのは間隙が bout の内側か間かだけ。停滞中の 1 打鍵の前後がどちらも基準超なら、その 1 打鍵は「1 イベントの bout」になり分割される（★ サブエージェントの推論）。
- 連結を直接支える先例は 2 系統: **再開の判定に持続を要求**（Iqbal & Horvitz 2007 の 15 秒 ＝ **[P35] 既登録**）／**短い異種行動を bout の内側として吸収**（Tolkamp / Yeates の「飲水を含む間隙」＝ 食事内の第 3 母集団）。

### 文献表（DOI 確認済み。既登録: [V144] Altmann & Trafton 2004 / [P35] Iqbal & Horvitz 2007 / [P355] Brumby 2013）
| 著者 年 | 題名 | DOI | 設計 | 範囲 |
|---|---|---|---|---|
| Altmann & Trafton 2002 | Memory for goals（Cognitive Science 26(1)） | 10.1207/s15516709cog2601_2 | 理論 | 全文（p.40） |
| Trafton, Altmann, Brock & Mintz 2003 | Preparing to resume an interrupted task（IJHCS 58(5)） | 10.1016/S1071-5819(03)00023-5 | N=17 | 全文 |
| Altmann & Trafton 2004 | [V144] | — | N=96 | 全文 |
| Iqbal & Horvitz 2007 | [P35] | 10.1145/1240624.1240730 | 27 名・2,267 時間 | 全文 |
| Monk, Trafton & Boehm-Davis 2008 | The effect of interruption duration and demand on resuming suspended goals（JEP:Applied 14(4)） | 10.1037/a0014402 | 3 実験 | 全文 |
| Trafton & Monk 2007 | Task Interruptions（Reviews of Human Factors and Ergonomics 3(1)） | 10.1518/155723408X299852 | 総説 | 全文 |
| Brumby et al. 2013 | [P355] | 10.1037/a0032696 | — | abstract |
| Mark, Gonzalez & Harris 2005 | No task left behind?（CHI 2005） | 10.1145/1054972.1055017 | 観察 N=24 | 全文 |
| Dabbish, Mark & González 2011 | Why do I keep interrupting myself?（CHI 2011） | 10.1145/1978942.1979405 | 36 名・切替 5,089 | 全文 |
| Adler & Benbunan-Fich 2013 | Self-interruptions in discretionary multitasking（Computers in Human Behavior 29(4)） | 10.1016/j.chb.2013.01.040 | ラボ | 全文 |
| Parnin & Rugaber 2009 | Resumption strategies for interrupted programming tasks（ICPC 2009） | 10.1109/ICPC.2009.5090030 | 85 名・約 1 万セッション | 全文 |
| Slater & Lester 1982 | Minimising errors in splitting behaviour into bouts（Behaviour 79） | 10.1163/156853982X00229 | 方法論 | abstract |
| Sibly, Nott & Fletcher 1990 / Langton, Collett & Sibly 1995 | bout 分割の原典 | 10.1016/S0003-3472(05)80726-2 / 10.1163/156853995X00144 | 方法論 | **未取得** |
| Tolkamp et al. 1998 | Satiety splits feeding behaviour into bouts（J Theor Biol 194） | 10.1006/jtbi.1998.0759 | 牛 16 頭 | abstract |
| Tolkamp & Kyriazakis 1999 | To split behaviour into bouts, log-transform the intervals（Animal Behaviour 57） | 10.1006/anbe.1998.1022 | 牛 38 頭・35,171 間隙 | abstract |
| Yeates et al. 2001 | Mixed distribution models（J Theor Biol 213） | 10.1006/jtbi.2001.2425 | 牛 | abstract |
| Halfaker et al. 2015 | User session identification based on strong regularities in inter-activity time（WWW 2015） | 10.1145/2736277.2741117 | Web ログ | arXiv 全文 |
| Mehrzadi & Feitelson 2012 | Extracting session data from activity logs（SYSTOR 2012） | 10.1145/2367589.2367592 | AOL ログ | 全文 |
| Li 2021 | Mixture components in keystroke logs（Frontiers in Psychology 12:628660） | 10.3389/fpsyg.2021.628660 | 小論文 1,944 本 | 全文 |
| Almond 2012 / Roeser 2024 | （S7 / S8-a と共通） | — | — | — |

### 定義（逐語）
- resumption lag: *"the time interval separating the end of the secondary task and the first subsequent action taken by the human operator in the primary task"*（Altmann & Trafton 2004 p.43）／ 操作化 *"the first subsequent action (mouse click)"*（p.46）／ 基線: *"values below 1 s were discarded first, to eliminate anticipation errors…"*（p.46）
- Trafton et al. 2003 p.592: *"to the first mouse click or key press a participant made to resume the primary task"*（disruption score ＝ resumption lag − 平均 inter-click lag）
- Monk et al. 2008 pp.303–304: *"screened for errors to isolate VCR task actions that represented successful postinterruption goal resumption"*・*"less than 100 ms, which were assumed to be due to incidental mouse clicks"* を除外
- **Iqbal & Horvitz 2007 p.679: *"we considered users to resume a suspended task if they had spent more than 15 seconds on the suspended application, which is more time than required for rapid application switches"***
- Parnin & Rugaber 2009 p.82: edit lag = *"the time between returning to a programming task and making the first edit"*／ p.83: セッションは *"a break in activity of 15 minutes or more"* で分割
- Dabbish et al. 2011 p.3128（自己中断）: *"for no apparent reason, the informant stopped what they were doing in the current working sphere prior to event completion and switched to a different working sphere"*
- Adler & Benbunan-Fich 2013 p.1445: 自己中断数 = *"the total number of switches (tab clicks) minus five"*（滞在時間の下限なし）
- Mark et al. 2005 pp.323–324: interrupted = *"when work was abandoned in the middle of an event"*
- Tolkamp et al. 1998（abstract）bout criterion: *"that time between events that separates intervals within, from intervals between, bouts"*（前提は Poisson・負の指数分布）
- Yeates et al. 2001（abstract）: *"the longest interval accepted as part of a meal"*／ 3 母集団 *"(1) short intervals within meals; (2) intervals within meals during which animals drink; (3) intervals between meals"*
- Slater & Lester 1982（abstract）: *"choose that bout criterion which leads to the fewest within and between bout intervals being assigned to the wrong category"*
- Halfaker et al. 2015 p.3: 閾値は *"equally likely to be within the gaussians fit with sub-hour means (within-session) and … beyond an hour (between-session)"* となる点
- Almond 2012 p.15: burst = *"uninterrupted typing that does not include pauses longer than two-thirds of a second"*

### claim
- 連結を支持: 最初の 1 操作をそのまま再開の成立とみなさない（Monk 2008 pp.303–304 の除外規則）
- **連結を支持: フィールドでは持続を条件に再開を判定（Iqbal & Horvitz 2007 p.679「15 秒」）**
- 連結を支持: 速い再開は誤りを伴う（Brumby 2013 [P355] abstract *"the lockout prohibited fast, inaccurate task resumptions"*）
- 連結を支持（形式の類比）: 短い異種行動を bout の内側に吸収するモデル（Yeates 2001 / Tolkamp & Kyriazakis 1999）
- 反証: 「最初の 1 操作で再開」を採る先例も実在（Parnin 2009 edit lag・Adler 2013 のタブクリック 1 回 = 自己中断 1 回）
- 反証: 簡単な課題では再開コストは最初の 1 手に集中（Trafton & Monk 2007 p.120・Ratwani & Trafton 2006a の二次記述）
- 連結のリスク: 長い閾値は誤結合を生む（Mehrzadi & Feitelson 2012 p.3 *"too long for other cases where it will erroneously concatenate sessions that should actually remain separated"*）
- 基準が個体によっては立たない（Tolkamp & Kyriazakis 1999 abstract *"No meaningful bout criterion could be obtained for some individuals"*）
- 誤分類が大きければ bout 解析自体が無用（Slater & Lester 1982 abstract）
- Poisson 前提の従来法は不適（Tolkamp 1998 abstract）
- 打鍵閾値は恣意的で参加者ごとに決めるべき（Roeser 2024 p.359・pp.362–363 *"A pause threshold would need to be participant-specific"*）
- 混合成分数は作文ごとに異なる（Li 2021 Table 5: 3 成分 431 本・4 成分 410 本）
- 標本が少ないと推定が不安定（Almond 2012 p.26: InWord 2 成分が 68 本中 58 本しか収束しない／ p.28 *"a person-dependent cut point"*）
- 大域閾値にも規則性はあるが判定は目視（Halfaker 2015 p.3 *"none were as good as a simple visual inspection"*）

### 見つからなかったもの
- 「再開のあと短時間で再停止」を正式な類型として定義した中断研究: **0 件**（Iqbal & Horvitz の 15 秒規則が暗黙に扱う唯一の例）
- log-survivorship / Sibly 型の bout criterion を打鍵・マウス・書字に適用した研究: **0 件**（打鍵の混合対数正規は同じ統計的系譜だが bout 文献を 0 件引用）
- Sibly 1990・Langton 1995・Luque & Guinet 2007・Berdoy 1993 の一次: 未取得
- Troiano 2008 の「bout 内で 1〜2 分の中断を許容する」定義: 未検証
