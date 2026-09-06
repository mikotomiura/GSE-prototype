# RQ α — 理解度と行動変化の個人内関連（2026-09-06・第 3 ラウンド）

> ⚠️ 本ファイルは **サーヴェイ subagent の報告**であり、`docs/references.md` /
> `docs/literature/_index.md` への採番・append は**メインエージェントが直列で行う**。
> ここに挙げるのは **登録候補**であって、採番済みの `[Pn]`/`[Vn]` ではない。
> ★ 本 subagent は repo 内の既存登録（[P1]〜[P316] / [V1]〜[V136]）を見ていないため、
> **既登録との重複判定はメイン側で DOI をキーに行うこと**。

---

## 0. 進捗ログ（1 ソースごとに追記）

- [init] ファイル作成。以後 1 ソース取得ごとに追記する。
- [S1] Fernandes, Lynch & Netemeyer 2014, *Management Science* 60(8):1861-1883, DOI 10.1287/mnsc.2013.1849 — Crossref 検算済（巻号・年・頁一致）。★ 著者 abstract を Crossref から一次取得。angle 4。
- [S2] Webb & Sheeran 2006, *Psychological Bulletin* 132(2):249-268, DOI 10.1037/0033-2909.132.2.249 — Crossref 検算済（Crossref に abstract 無し → 数値は二次資料水準）。angle 6（反証）。
- [S3] Hauser, Ellsworth & Gonzalez 2018, *Frontiers in Psychology* 9:998, DOI 10.3389/fpsyg.2018.00998 — Crossref 検算済（preprint 10.31234/osf.io/afmbg も存在）。**全文取得済（OA）**。angle 5。
- [S4] Fayant, Sigall, Lemonnier, Retsin & Alexopoulos 2017, *International Review of Social Psychology* 30(1):125-130, DOI 10.5334/irsp.102 — **全文取得済（OA）**。Crossref 検算は 2 回失敗の後 3 回目で成功（巻号・頁一致）。angle 5。
- [S5] Aronow, Baron & Pinson 2019, *Political Analysis* 27(4):572-589, DOI 10.1017/pan.2019.5 — Crossref 検算済。**著者 abstract 一次取得**。angle 5。
- [S6] Miller 2016, *Patient Education and Counseling* 99(7):1079-1086, DOI 10.1016/j.pec.2016.01.020 — Crossref 検算済。**全文取得済（PMC4912447）**。r=.14 [.08,.19], k=48, N=19,072、**全て個人間の横断相関**（個人内デザインはゼロ）。angle 2 の主力。
- [S7] Zhang, Terry & McHorney 2014, *Annals of Pharmacotherapy* 48(6):741-751, DOI 10.1177/1060028014526562 — Crossref 検算済。⚠️ 全文未取得（二次資料水準）。angle 2。
- [S8] Sigall & Mills 1998, *Personality and Social Psychology Review* 2(3):218-226, DOI 10.1207/s15327957pspr0203_5 — Crossref 検算済。⚠️ Unpaywall **CLOSED 確定**。二次資料水準。angle 5。
- [S9] Gomes et al. 2025, *European Journal of Nutrition* 64(5):228, DOI 10.1007/s00394-025-03626-9 — PMC12198295 **全文取得**。★ 同一被験者で「客観的理解」と「購買意図」を両方測るが、**個人レベルの相関・媒介は一切報告していない**（群間 OR のみ）。angle 3。
- [S10] Grunert & Wills の「理解が媒介する」モデル — ⚠️ **二次資料水準**（原論文未特定）。angle 3。
- [S11] Baig, Noar et al. 2020, *J Behav Med* 44(1):74-83, DOI 10.1007/s10865-020-00163-0 — PMC9391031 **全文取得**。N=703 RCT、個人レベルで message perceptions → quit attempt が **β=−0.35, p=.003（負）**。angle 3/5。
- [S12] Ejelöv & Luke 2020, *JESP* 87:103937, DOI 10.1016/j.jesp.2019.103937 — Crossref 検算済。⚠️ Unpaywall **CLOSED 確定**。preprint 10.31234/osf.io/8427m は OSF が本文を返さず取得失敗。二次資料水準。angle 5。
- [S13] ★ Mathur 2025, *Advances in Methods and Practices in Psychological Science*, DOI 10.1177/25152459241297537 — Semantic Scholar で GOLD OA (CC BY-NC) 確認、**著者 abstract 全文取得**。⚠️ 本文は SAGE 403 で未取得（「abstract 水準」）。angle 5 の主力。
- [S14] Noar, Barker, Bell & Yzer 2018, *Health Communication* 35(2):148-157, DOI 10.1080/10410236.2018.1547675 — Crossref 検算済、**Europe PMC で abstract 一次取得**。k=6 縦断、PME→行動 r=.201。⚠️ 全文は PMC が reCAPTCHA で不可。angle 3。
- [S15] ★ Okan, Janssen, Galesic & Waters 2019, *Medical Decision Making* 39(3):183-195, DOI 10.1177/0272989X19829728 — PMC6470031 **全文取得**。N=835 個人レベル階層回帰。**グラフリテラシー → 行動意図は n.s.（numeracy・社会人口統計 統制後）**。angle 1 の中核（null 側）。
- [S16] Ancker, Benda & Zikmund-Fisher 2024, *JAMIA* 31(11):2760-2765, DOI 10.1093/jamia/ocae123 — **全文取得**。⚠️★ **検索エンジンの要約が「理解を上げる特徴と行動を変える特徴は違う」という文を本論文に帰属させたが、全文照合で本論文にその明示的区別は無い**（→ §7 否決リスト）。
- [S17] ★★★ Hawley, Zikmund-Fisher, Ubel, Jancovic, Lucas & Fagerlin 2008, *Patient Education and Counseling* 73(3):448-455, DOI 10.1016/j.pec.2008.07.023 — Crossref 検算済、**Europe PMC (PMID 18755566) で abstract 一次取得**。⚠️ Unpaywall **CLOSED 確定**（全文なし）。N=2412。abstract 逐語: **「Verbatim and gist knowledge were significantly (p<0.01) associated with making a medically superior treatment choice.」** → 下位問い (a) の最直接ヒット。ただし (i) 個人*間*（1 標本内の被験者レベル）であり反復測定の個人内ではない、(ii) アウトカムは仮想的な治療選択であって実行動ではない、(iii) **効果量が abstract に無く全文 CLOSED** のため大きさ不明。
- [S18] Spronk, Kullen, Burdon & O'Connor 2014, *British Journal of Nutrition* 111(10):1713-1726, DOI 10.1017/s0007114514000087 — Crossref 検算済、**著者 abstract 一次取得**。k=29、65.5% が有意・正・**弱い (r<0.5)**。⚠️ 異質性のためメタ分析は実施できていない。angle 6。
- [S19] Bullock, Green & Ha 2010, *Journal of Personality and Social Psychology* 98(4):550-558, DOI 10.1037/a0018933 — Crossref 検算済（Crossref に abstract 無し）。⚠️ 二次資料水準。angle 5。
- [S20] Corvalán, Reyes, Correa, Dillman Carpentier & Taillie 2025, OSF preprint DOI 10.31219/osf.io/49dbs_v1 — **著者 abstract 一次取得**。N=889 母親 + 740 青年、前後 2 時点。理解 96%/93%、購買時の栄養情報利用 56%→70% / 23%→31%。★ **両方を同一人物で 2 時点測るが、両者の個人レベルの結び付けは行っていない**。⚠️ **未査読 preprint**。angle 3。
- [S21] Correa, Fierro, Reyes, Dillman Carpentier & Taillie 2019, *IJBNPA* 16(1), DOI 10.1186/s12966-019-0781-x — Crossref 検算済のみ（本文未取得）。angle 3。
- [S22] Matthews らの peripheral display 評価枠組（appeal / awareness / distraction / learnability、comprehension を含む）— ⚠️ **二次資料水準・DOI 未特定**。angle 1（HCI 側の「理解度は測るが行動と結ばない」証拠）。

**取得ソース: 22（全文取得 7 / 著者 abstract 一次取得 6 / 二次資料水準 9）。探索 angle: 6（うち反証 angle 2）。**

---

## 1. 動機（判断 (i) の急所を 3 行で）

判断 (i) は「主要アウトカムを**行動指標**に置き、**可読性は manipulation check へ降格**する」と立てている。
降格そのものより危ないのは、そこに付いた**暗黙の前提** ——「可読性が落ちると、行動側の結果が解釈不能になる」——
であり、これは可読性を「主要アウトカムではないが**行動結果の解釈可能性のゲート**」に据える強い主張である。
2 ラウンド回してこの関係を検証した先行がゼロだった。本 RQ はその穴を埋める。

---

## 2. 検証状態

- 取得ソース **22**（全文 7 / 著者 abstract 一次 6 / 二次資料 9）、探索 angle **6**
  （1: 理解度×行動の個人差 / 2: health literacy / 3: 栄養・警告ラベル / 4: 金融リテラシー /
   5: manipulation check 方法論 / 6: knowledge–action・intention–behavior gap＝反証）。
- 抽出 claim **11**。**confirmed (3-0) 6 / confirmed 留保付き (2-1) 3 / 否決 (1-2, 0-3) 2**（＋§7 に否決 3 件を追加計上）。
- ⚠️ **温度が下位問いで割れた**。(a)(b)(d) は証拠あり、**(a) の「個人*内*（反復測定）」条件だけが判定不能**。平均化してはならない。

---

## 3. gate 判定（要点先出し）

| 下位問い | 温度 | 1 行判定 |
|---|---|---|
| **(a)** 理解度と行動を同一被験者で測り関連づけた研究は存在するか | **確定**（ただし「個人*内*・反復測定」に限れば **判定不能**） | 1 標本内の**個人*間***関連なら存在する（Hawley 2008, N=2412: verbatim/gist 知識 → 医学的に優れた選択, p<0.01）。**反復測定で「理解度の変動」と「行動変化量」を結んだ研究は 1 件も発見できなかった**。 |
| **(b)** 関連は正・null・負のどれか。効果量は | **確定（正・ただし極小）** | 個人間では正だが弱い: 健康リテラシー↔アドヒアランス **r=.14 [.08,.19]** (k=48, N=19,072)。栄養知識↔摂取は 65.5% が有意・正・**r<0.5**。⚠️ 金融では **IV / 心理特性統制で partial effect が劇的に縮小**し、介入は行動分散の **0.1%** しか説明しない。個人レベルのグラフリテラシー→行動意図は **統制後 n.s.**。 |
| **(c)** 埋まらないなら、どの条件を落とせば埋まるか | **確定** | ★ **落とすべき条件はただ 1 つ「個人内（反復測定）→ 1 標本内の個人間」**。落とした瞬間に正の例と null の例が両方現れる。他条件（実行動→意図 / アンビエント→任意の情報提示 / 1 時点→前後）は**既に落ちている**（＝その方向にはもう証拠がある）。「直接相関→媒介」だけは落としても**埋まらない**（識別不能）。 |
| **(d)** manipulation check が落ちた時の主効果の扱いを論じた方法論文献はあるか | **確定・かつ判断 (i) の前提を否定する** | ある。一致して「**失敗した MC は主効果の解釈を無効化しない**」(Fayant 2017)、「**MC で被験者を落とすと識別が壊れる**」(Aronow 2019)、「**ITT は目標内的状態の ATE に対して偏り、方向は不定**」(Mathur 2025)、「**MC を本試験中に挟むとそれ自体が介入になる**」(Hauser 2018)。 |

### ★ 判断 (i) への帰結

1. **降格は支持される。** 主要アウトカムを行動に置き、可読性を主要アウトカムから外す判断そのものは方法論文献と整合する（Sigall & Mills 1998 / Fayant 2017）。
2. ⚠️★★★ **前提は誤りなので書き換える。** 「可読性が落ちると行動側の結果が解釈不能になる」は方法論文献が明確に否定している。正しい定式は
   「**可読性が落ちても ITT は解釈可能。ただし ITT が答えるのは『表現を出したこと』の効果であって『表現が読まれたこと』の効果ではない**」（Mathur 2025）。
3. ★ **設計上の帰結が 3 つ出る**: (i) 可読性を**除外基準に使わない**（Aronow 2019）、(ii) 「読めた人での効果」を言うなら**可読性チェックを操作変数とする IV を事前登録**（Mathur 2025）、(iii) 可読性チェックを**本試験の途中に挟まない**（Hauser 2018 — 符号の意味を教えて主要アウトカムを汚染する）。

---

## 4. claim と 3 票検証

> 3 票の視点 = **①内的妥当性 / ②外的妥当性・GSE 設定への外挿 / ③効果量の頑健性（出版バイアス・補正後）**

### C1: 同一標本の個人レベルで「理解度スコア」と「選択（行動の代理）」を直接関連づけた研究は**存在する** — **[3-0 confirmed]** `確定`

- 根拠: Hawley et al. 2008 (DOI 10.1016/j.pec.2008.07.023)、**N=2412**、6 種のグラフ書式に無作為割付。
  verbatim（数値）知識と gist（概略）知識を測定し、**同じ被験者に治療選択もさせた**。
  著者 abstract 逐語: *"Verbatim and gist knowledge were significantly (p<0.01) associated with making a medically superior treatment choice."*
  また *"Viewing tables was associated with a higher likelihood of having adequate verbatim knowledge vs. other formats (p<0.001) but lower likelihood of having adequate gist knowledge (p<0.05)"* —— ★ **理解の種類によって最適書式が逆転する**という、GSE の符号設計に効く所見も同じ論文にある。
- ①内的: ✓ 書式は無作為化。ただし**知識↔選択の関連自体は観察的**（知識は無作為化されていない）。
- ②外的: ✓ 「存在するか」という問いに対しては成立。
- ③頑健性: ✓ 存在の主張は効果量に依存しない。
- **票 3-0 → confirmed**。⚠️ 大きさの主張は C1b で別に扱う（そちらは否決）。

### C1b: その関連は実務的に意味のある大きさである — **[1-2 否決 → §7]** `判定不能`

- ①内的: ✓ 大標本。
- ②外的: ✗ **仮想的治療選択の 1 回きり web survey**。GSE の「数日〜数週の作業行動の変化量」への外挿は成立しない。
- ③頑健性: ✗ **効果量が abstract に報告されておらず (p<0.01 のみ)、全文は Unpaywall で CLOSED 確定**。N=2412 では極小の効果でも p<0.01 になる。
- **票 1-2 → 否決**。

### C2: 個人レベルで「グラフ理解能力」→「行動意図」は、numeracy 統制後 **null** — **[2-1 confirmed・留保あり]** `確定`

- 根拠: Okan et al. 2019 (DOI 10.1177/0272989X19829728)、**N=835**（米国全国標本、47% が人種的マイノリティ、46% が高等教育未満）、階層回帰 Step 3。
  numeracy・社会人口統計を統制後: **行動意図 n.s. / リスク理解 n.s. / 認知的リスク知覚 n.s. / リスク感情 n.s. / 心配 n.s.**。
  有意に残ったのは **response efficacy（正）** と **defensive processing（負）** の 2 つのみ。
- ①内的: ✓ 大標本・階層回帰・統制変数が事前に定義。ただし**横断**。
- ②外的: △ **留保** — アウトカムが「行動の precursor（意図等）」であり**実行動ではない**。著者自身が実際の健康行動は測っていないと明記。
- ③頑健性: ✓ **null であること自体が頑健性の証拠**（出版バイアスは通常 null を減らす方向に働くので、公刊された null は上方バイアスを受けていない）。
- **票 2-1 → confirmed（留保: アウトカムは意図であって行動ではない）**。

### C3: 理解度と行動の関連は、**個人間でも弱い**（r ≈ .1–.2 帯） — **[3-0 confirmed]** `確定`

- 根拠 1: Miller 2016 (DOI 10.1016/j.pec.2016.01.020) メタ分析。**k=48, N=19,072**、健康リテラシー ↔ アドヒアランス **r = .14 [95% CI .08, .19]**。
  調整因子: 非薬物レジメンで有意に高い (t(46)=−2.443, p=.018)、心血管疾患で高い (t(46)=2.564, p=.014)、
  ★ **主観的測定が客観的測定より強い効果を出す** (t(99)=4.578, p<.001)。
  ⚠️ **全 48 研究が個人*間*の横断相関**であり、個人内・縦断デザインは 1 件も含まれない（全文照合済み）。
- 根拠 2: Spronk et al. 2014 (DOI 10.1017/s0007114514000087) 系統的レビュー **k=29**。著者 abstract 逐語:
  *"The majority of the studies (65·5 %: community 63·6 %; athletic 71·4 %) reported significant, positive, but weak (r < 0·5) associations between higher nutrition knowledge and dietary intake"*。
  ⚠️ 測定法の異質性のため**メタ分析は実施できなかった**（著者明記）。
- ①内的: ✓ 独立した 2 領域・2 本のレビューで一致。ただし両方とも横断。
- ②外的: ✓ 健康・栄養・（C4 の）金融という**3 領域で同じ帯**に落ちる。
- ③頑健性: ✓ Miller の「主観的測定 > 客観的測定」という調整因子は、**測定が甘いほど効果が大きく見える**ことを示しており、真の値は r=.14 より**さらに小さい**方向。
- **票 3-0 → confirmed**。

### C4: 理解度を**上げる介入**は、行動の分散をほとんど説明しない — **[2-1 confirmed・留保あり]** `確定`

- 根拠: Fernandes, Lynch & Netemeyer 2014 (DOI 10.1287/mnsc.2013.1849)、**168 論文 / 201 研究**のメタ分析。著者 abstract 逐語:
  *"interventions to improve financial literacy explain only 0.1% of the variance in financial behaviors studied, with weaker effects in low-income samples."*
  *"even large interventions with many hours of instruction have negligible effects on behavior 20 months or more from the time of intervention."*
  ★ 決定的に: *"the partial effects of financial literacy diminish dramatically when one controls for psychological traits that have been omitted in prior research **or when one uses an instrument for financial literacy to control for omitted variables**."*
- ①内的: ✓ 相関研究と介入研究を分離し、**IV で交絡を落とした**上での結論。
- ②外的: △ **留保** — 金融行動に限定。GSE の「作業中断→再開後の貼り付け率」は時間尺度が桁で違う（分〜時間 vs 月〜年）。
- ③頑健性: ✓ ★ **「相関研究の見かけの効果が交絡由来である」ことを IV で示した稀な例**であり、C3 の r≈.14 を上方バイアスとして疑う根拠になる。
- **票 2-1 → confirmed（留保: 金融領域・長い時間尺度）**。

### C5: manipulation check の失敗者を**除外**すると、推定は識別不能になりうる — **[3-0 confirmed]** `確定`

- 根拠: Aronow, Baron & Pinson 2019 (DOI 10.1017/pan.2019.5)。著者 abstract 逐語:
  *"Dropping subjects based on the results of a manipulation check following treatment assignment is common practice across the social sciences, presumably **to restrict estimates to a subpopulation of subjects who understand the experimental prompt**. We show that this practice can lead to serious bias and argue for a focus on what is revealed without discarding subjects."*
  *"we provide sharp bounds for potential outcomes among those who would pass a manipulation check regardless of treatment assignment. **These bounds may have large or infinite width, implying that this inferential target is often out of reach.**"*
- ★ **逐語で「実験プロンプトを理解した部分集団に限定する」と名指ししている** —— GSE の「表現を読めた人だけで効果を見る」と構造が同一。
- ①内的: ✓ 解析的（Zhang & Rubin 2003 / Lee 2009 の多処置への一般化）。②外的: ✓ 設計非依存の識別問題。③頑健性: ✓ 数学的結果で出版バイアスと無関係。
- **票 3-0 → confirmed**。

### C6: ITT 推定量は「目標とする内的状態」の ATE に対して**偏り、方向は不定** — **[3-0 confirmed]** `確定`

- 根拠: Mathur 2025 (DOI 10.1177/25152459241297537, *AMPPS*)。著者 abstract 逐語:
  *"this intention-to-treat (ITT) estimator is typically biased for the ATE of the target state, and **the bias could be either toward the null (conservative) or away from the null**. I discuss the fairly stringent assumptions under which this estimator is conservative. Given this, **I argue against the status-quo practice of interpreting the ITT estimate as the effect of the target state** without any explicit discussion of whether these assumptions hold."*
  代替案: *"Under a somewhat weaker version of the same assumptions, one can alternatively use **instrumental-variables (IVs) analysis** to directly estimate the effect of the target state."*
  実例として ego-depletion の多施設追試を IV で再解析し、**部分的にしか効かなかった操作を明示的に扱った上で、原著の null 結果を追認した**。
- ★ GSE との構造対応: 割り付けられるのは**表現の提示**であり、目標内的状態は**「本人が表現を読み取ったこと」**。
- ①内的: ✓ 因果推論の形式的結果。②外的: ✓ 「割り付けられない内的状態＋MC」という構造が GSE と一致。③頑健性: ✓ 解析的。
- **票 3-0 → confirmed**。⚠️ **留保: 本文は SAGE 403 で未取得。上記はすべて著者 abstract の逐語**。

### C7: **失敗した manipulation check は、主効果の解釈を無効化しない** — **[3-0 confirmed]** `確定`

- 根拠: Fayant et al. 2017 (DOI 10.5334/irsp.102、**全文取得**)。
  - MC は *"uninformative about internal and construct validity"* であり *"cannot warrant conclusions of causal validity"*。
  - **失敗した MC は代替説明を支持しない** —— MC の失敗は「操作の失敗」ではなく**「測定の失敗」でありうる**から。
  - MC の**成功も**構成概念妥当性を示さない（操作は別の構成概念に効いたかもしれない）。
  - MC を入れること自体が多重検定で Type I / Type II 誤りを増やし、操作を顕在化させて需要効果を招く。
  - 推奨: *"other sources like secondary DVs, pretests, and pilot experiments"* に依拠せよ。
- ①内的: ✓ 論理的議論。②外的: ✓ MC 一般に妥当。③頑健性: ✓ 理論的主張で出版バイアス無関係。
- **票 3-0 → confirmed**。★★★ **これが判断 (i) の前提を直撃する。**

### C8: manipulation check を**本試験の途中に挟むと、それ自体が介入になる** — **[3-0 confirmed]** `確定`

- 根拠: Hauser, Ellsworth & Gonzalez 2018 (DOI 10.3389/fpsyg.2018.00998、**全文取得**)。
  典型的な MC は「処置と従属変数の測定の間に置かれた、非隠蔽的な言語的測定」であり、
  **測定として構想されているが介入としても働き、本来起こらなかった過程を始動させる**。
  「MC は実験結論に影響しない」というデフォルト仮定は正当化されない。
  推奨: *"conducting the manipulation check before actually running the experiment, in a pilot study whose whole purpose is to find out whether the treatment successfully produces the intended psychological state."*
- ★ GSE への直撃: 「この模様は何を意味しますか？」と**作業中に**尋ねること自体が**符号の意味を教えてしまい**、その後の行動（＝主要アウトカム）を汚染する。
- ①内的: ✓ ②外的: ✓ GSE の inline 可読性テストにそのまま当たる。③頑健性: ✓
- **票 3-0 → confirmed**。

### C9: 「理解度が行動効果を媒介する」ことを、理解度を測って媒介分析することでは示せない — **[2-1 confirmed・留保あり]** `PLAUSIBLE BUT UNPROVEN`

- 根拠: Bullock, Green & Ha 2010 (DOI 10.1037/a0018933, *JPSP* 98(4):550-558)。
  measurement-of-mediation デザインでは**媒介変数に無作為割付されていない**ため、媒介変数↔従属変数の関係は相関的にとどまる。
  MC を媒介分析に用いても交絡は排除できない（MC と相関する未測定変数が関係を駆動しうる）。
  処置効果の異質性は、**媒介が無いのに有るように（またはその逆に）見せうる**。
- ①内的: ✓ ②外的: ✓ Grunert & Wills 型の「理解が媒介する」モデル（S10）はまさにこの形。
- ③頑健性: ✗ **留保 — 本 subagent は一次全文も abstract も取得しておらず、二次資料水準**。
- **票 2-1 → confirmed（留保: 一次全文未取得。GSE 文書で引く前に一次確認が必要）**。

### C10: 「主観的な受け取り方の評定」なら、個人レベルで**後の実行動を予測する** — **[2-1 confirmed・留保あり]** `確定`

- 根拠 1: Noar, Barker, Bell & Yzer 2018 (DOI 10.1080/10410236.2018.1547675) メタ分析、**縦断研究 k=6**。
  PME（知覚された message の有効性）→ 禁煙意図 **r = .256, p<.001**、→ **禁煙行動 r = .201, p<.001**（small〜medium）。
- 根拠 2: Baig, Noar et al. 2020 (DOI 10.1007/s10865-020-00163-0, **N=703 RCT**, 3 週間, **全文取得**)。
  **effects perceptions**（「この message は自分の行動を変えうるか」）→ quit attempt **β=0.66, p<.001**、
  forgoing cigarettes **β=0.53, p<.001**、butting out **β=0.36, p<.001**。
  ⚠️ 一方 **message perceptions**（message 属性への評定）→ quit attempt は **β=−0.35, p=.003（負）**、
  quit intentions **β=−0.29, p=.006（負）**。effects perceptions を統制すると **incremental criterion validity ゼロ**。
- ①内的: ✓ 縦断・RCT。②外的: △ タバコ教育に限定。
- ③頑健性: ✗ **留保 — k=6 は出版バイアス検定に足りず、ファンネル解析の有無を確認できていない（全文は PMC reCAPTCHA で不可）**。
- **票 2-1 → confirmed（留保: k=6・出版バイアス未検証）**。
- ★ GSE への含意: manipulation check を置くなら、**「読めたか」より「これは自分に効きそうか」の方が行動を予測する**という順序がここにある。

### C11: FOP ラベル研究は「理解」と「購買」を同一被験者で測るが、**両者を個人レベルで結んでいない** — **[3-0 confirmed]** `確定`

- 根拠 1: Gomes et al. 2025 (DOI 10.1007/s00394-025-03626-9, **N=1204**, 4 群 RCT, **全文取得**)。
  同一被験者が (a) 5 製品セットでの購買選択、(b) 最も害の少ない製品の同定、(c) 過剰栄養素の同定 の 3 課題を**連続して**実施。
  結果は**群間 OR のみ**（OWL 購買意図 OR 2.21 [1.58–3.11]、最も害の少ない製品の同定 OR 3.77 [2.79–5.09]、過剰栄養素の同定 OR 3.26 [2.40–4.43]）。
  ⚠️ **理解と購買意図の個人レベルの相関・媒介は一切報告されていない**（全文照合済み）。Grunert & Wills も引用していない。
- 根拠 2: Corvalán et al. 2025 (DOI 10.31219/osf.io/49dbs_v1、**未査読 preprint**、N=889 母親 + 740 青年、前後 2 時点)。
  理解は **96% / 93% が正答（天井効果）**、購買時の栄養情報利用は母親 56%→70%、青年 23%→31%。
  ⚠️ **同一人物の 2 時点で両方を測っているのに、両者の変化量を結び付けていない**。
- ①内的: ✓ 全文 / abstract 照合済み。②外的: ✓ 3 研究で一致するパターン。③頑健性: ✓ 「報告されていない」という否定的観察は出版バイアスの影響を受けない。
- **票 3-0 → confirmed**。★★★ **これが RQ α の穴の正体: データは存在するのに、解析が行われていない。**

---

## 5. ⚠️ ゼロの検算表（条件を 1 つずつ落とす）

> ★ 完全形（**アンビエント表示 × 個人内反復測定 × 客観的理解度 × 直接相関 × 実行動**）はゼロ。
> しかしそれは**連言で作ったゼロ**なので、1 つずつ落として「どこで埋まるか」を特定する。

| 落とした条件 | 埋まるか | 代表例 |
|---|---|---|
| **個人内（反復測定）→ 1 標本内の個人間** | ★★★ **埋まる（これが唯一の決め手）** | **Hawley 2008** (N=2412): verbatim/gist 知識 → 医学的に優れた治療選択, p<0.01（正）。**Okan 2019** (N=835): グラフリテラシー → 行動意図 **n.s.**（統制後、null）。★ **正の例と null の例が両方ある**。 |
| 直接相関 → 媒介分析でも可 | ⚠️ **埋まらない（質が落ちるだけ）** | Grunert & Wills モデルは「理解が媒介する」と*主張*するが、**Bullock, Green & Ha 2010** により measurement-of-mediation は識別されない。FOP RCT (Gomes 2025) は媒介分析を**実施すらしていない**。 |
| 「客観的理解度」→ 主観的な分かりやすさ / 効きそう感の評定 | ★★ **埋まる（しかも効果が大きい）** | **Noar 2018** メタ (k=6 縦断): PME → 実行動 **r=.201**。**Baig 2020** (N=703): effects perceptions → quit attempt **β=0.66**。⚠️ ただし **message perceptions は β=−0.35（負）** で、構成概念によって符号が反転する。 |
| アンビエント表示 → あらゆる情報提示 | ★★★ **埋まる（上記すべてがこれ）** | 健康リテラシー / 栄養ラベル / 警告ラベル / 金融リテラシー / リスクグラフ。⚠️★ **HCI の peripheral display 側は comprehension を評価軸に持つ（Matthews の appeal/awareness/distraction/learnability）が、行動変化と結んだ研究には到達できなかった**（§8 参照）。 |
| 行動指標 → 意図・自己申告でも可 | ★★ **埋まる** | Okan 2019（意図, **n.s.**）、Gomes 2025（購買意図, OR）、Corvalán 2025（自己申告購買）。⚠️ 意図→行動には **d+=.36** の減衰がさらに乗る（Webb & Sheeran 2006、⚠️ 数値は二次資料水準）。 |
| 1 時点 → 同一人物の前後 2 時点 | △ **各変数は埋まるが、両者の *結び付き* は埋まらない** | **Corvalán 2025**: 同一人物の 2 時点で理解も購買も測っている。**しかし個人レベルで結んでいない**。加えて理解が 96%/93% の**天井効果**で分散がほぼ無い。★「データは既にあるのに解析されていない」典型。 |
| 「理解度」→ 知識一般 | ★★★ **埋まる（そして弱い）** | Miller 2016 **r=.14** (k=48, N=19,072)、Spronk 2014 **65.5% が有意・正・r<0.5**、Fernandes 2014 **介入は行動分散の 0.1%**。 |

### ★★★ この表からの結論（本 RQ 最大の成果物）

1. **落とすべき条件はただ 1 つ ——「個人内（反復測定）」**。これを「1 標本内の個人間」に落とした瞬間、
   証拠は**正の例（Hawley 2008）と null の例（Okan 2019）の両方**で現れる。
   他の条件はすべて既に落ちている（＝その方向にはもう証拠があり、落としても新しい情報が出ない）。
2. ⚠️ **落としても埋まらない条件が 1 つある ——「直接相関 → 媒介分析」**。
   媒介で埋めようとすると Bullock 2010 の識別問題に落ちるので、**代替経路として使えない**。
   → ★ GSE の解析計画で「理解度が媒介する」と書いてはならない。
3. ★★★ **本当の穴は「先行研究の不在」ではなく「解析の不在」である。**
   Corvalán 2025 と Gomes 2025 は必要なデータを**既に同一被験者から取っている**のに、
   理解度と行動を個人レベルで結ぶ解析を**していない**。
   → ★ **GSE がこの解析を最初にやれば、それ自体が寄与になる**（データ取得コストは追加ゼロ。
   既に取る予定の可読性チェックと行動ログを、個人レベルで結ぶ解析を事前登録するだけで済む）。

---

## 6. ★ 登録候補（採番はメインが行う）

> ⚠️ 温度・水準で 3 群に分ける。**二次資料水準（一次全文未取得）のものは明記した**。
> ⚠️ 本 subagent は既存 [Pn]/[Vn] を見ていない。**DOI をキーにメイン側で重複照合すること**。
> 名前空間の目安: 群 A の A1/A2、群 B の B1/B2 は**検証方法論 → `V`**、それ以外は **`P`** が妥当と思われる（最終判断はメイン）。

### 群 A — 一次全文取得済み（強く推奨）

| # | 書誌 | DOI | N / 設計 | 主要効果量 | GSE 設計での接地案（1 行） |
|---|---|---|---|---|---|
| A1 | Hauser DJ, Ellsworth PC, Gonzalez R (2018). Are Manipulation Checks Necessary? *Frontiers in Psychology* 9:998 | 10.3389/fpsyg.2018.00998 | 論考 | — | ★ **可読性チェックを本試験の途中に置かない**（符号の意味を教えて主要アウトカムを汚染する）。pilot / 別標本 / 事後に回す。 |
| A2 | Fayant M-P, Sigall H, Lemonnier A, Retsin E, Alexopoulos T (2017). On the Limitations of Manipulation Checks: An Obstacle Toward Cumulative Science. *IRSP* 30(1):125-130 | 10.5334/irsp.102 | 論考 | — | ★★★ **判断 (i) の前提を書き換える根拠**: 失敗した MC は主効果の解釈を無効化しない（測定の失敗かもしれない）。 |
| A3 | Miller TA (2016). Health literacy and adherence to medical treatment in chronic and acute illness: A meta-analysis. *Patient Educ Couns* 99(7):1079-1086 | 10.1016/j.pec.2016.01.020 | メタ k=48, N=19,072 | **r=.14 [.08,.19]** | 理解度→行動の期待効果量の**上限の目安**。⚠️ 主観測定の方が強く出る (t=4.578, p<.001) → GSE も自己申告アウトカムを主役にしない。 |
| A4 | Okan Y, Janssen E, Galesic M, Waters EA (2019). Using the Short Graph Literacy Scale to Predict Precursors of Health Behavior Change. *Med Decis Making* 39(3):183-195 | 10.1177/0272989X19829728 | N=835, 個人レベル階層回帰 | **行動意図 n.s.**（統制後）／response efficacy 正・defensive processing 負 | ★ **「表現を読める人ほど動く」には既に否定側の証拠がある**。可読性を主要アウトカムに置かない判断の**追い風**。 |
| A5 | Baig SA, Noar SM, Gottfredson NC, et al. (2020). Incremental criterion validity of message perceptions and effects perceptions in the context of anti-smoking messages. *J Behav Med* 44(1):74-83 | 10.1007/s10865-020-00163-0 | N=703 RCT, 3 週 | effects perceptions → quit attempt **β=0.66**; message perceptions **β=−0.35（負）** | ★ manipulation check を置くなら「読めたか」より **「これは自分に効きそうか」** の方が行動を予測する。 |
| A6 | Gomes FS, Gálvez A, Pérez D, et al. (2025). Effects of front-of-package nutrition labelling systems on objective understanding and purchase intention in El Salvador. *Eur J Nutr* 64(5):228 | 10.1007/s00394-025-03626-9 | N=1204, 4 群 RCT | OWL 購買意図 OR 2.21 [1.58–3.11]; 理解 OR 3.77 [2.79–5.09] | ★ **「同一被験者で両方測るが個人レベルで結ばない」現行慣行の実例**。GSE はここを埋めることで差分が立つ。 |
| A7 | Ancker JS, Benda NC, Zikmund-Fisher BJ (2024). Insufficient evidence for interactive or animated graphics for communicating probability. *JAMIA* 31(11):2760-2765 | 10.1093/jamia/ocae123 | 181 研究レビューの二次解析（うち 24 が動的・対話的） | — | 動的・対話的表現は静的表現に対しリスク知覚・信頼・行動のいずれでも強い証拠を示さない → ★ GSE の表現を動的に凝る方向への投資は根拠が薄い。 |

### 群 B — 著者 abstract を一次取得（数値は abstract 逐語。本文未取得を明記）

| # | 書誌 | DOI | N / 設計 | 主要効果量 | GSE 設計での接地案 |
|---|---|---|---|---|---|
| B1 | **Mathur MB (2025). On the Statistical Analysis of Experiments With Manipulation Checks. *AMPPS*** | 10.1177/25152459241297537 | 方法論（ego-depletion 多施設追試を実例に IV 再解析） | — | ★★★ **判断 (i) の解析計画そのもの**: 主要解析は ITT のまま、「読めた人での効果」を言うなら **可読性チェックを操作変数として IV 推定**を事前登録する。ITT を内的状態の効果と読み替えない。 |
| B2 | **Aronow PM, Baron J, Pinson L (2019). A Note on Dropping Experimental Subjects who Fail a Manipulation Check. *Political Analysis* 27(4):572-589** | 10.1017/pan.2019.5 | 方法論（識別限界の解析） | 境界幅が *"large or infinite"* | ★★★ **可読性チェックを除外基準に使わない**。逐語で「実験プロンプトを理解した部分集団に限定する」慣行を名指しで否定。 |
| B3 | Hawley ST, Zikmund-Fisher B, Ubel P, Jancovic A, Lucas T, Fagerlin A (2008). The impact of the format of graphical presentation on health-related knowledge and treatment choices. *Patient Educ Couns* 73(3):448-455 | 10.1016/j.pec.2008.07.023 | N=2412, 6 書式に無作為割付 | 「verbatim/gist 知識は医学的に優れた選択と有意に関連 (p<0.01)」**効果量は未報告** | ★★★ **RQ α の最直接ヒット**。⚠️ 全文 CLOSED 確定・効果量未報告のため、**「関連がある」までしか引けない**。 |
| B4 | Fernandes D, Lynch JG, Netemeyer RG (2014). Financial Literacy, Financial Education, and Downstream Financial Behaviors. *Management Science* 60(8):1861-1883 | 10.1287/mnsc.2013.1849 | メタ 168 論文 / 201 研究 | **介入は行動分散の 0.1%**；IV / 心理特性統制で partial effect が劇的縮小 | ★ **「理解度を上げれば行動が変わる」という因果の期待を下げる**。相関で見えた関連の多くは交絡。 |
| B5 | Noar SM, Barker J, Bell T, Yzer M (2018). Does Perceived Message Effectiveness Predict the Actual Effectiveness of Tobacco Education Messages? *Health Communication* 35(2):148-157 | 10.1080/10410236.2018.1547675 | メタ、縦断 k=6 | 意図 **r=.256, p<.001**、行動 **r=.201, p<.001** | manipulation check の候補としての PME の予測妥当性。⚠️ k=6・出版バイアス未検証。 |
| B6 | Spronk I, Kullen C, Burdon C, O'Connor H (2014). Relationship between nutrition knowledge and dietary intake. *Br J Nutr* 111(10):1713-1726 | 10.1017/s0007114514000087 | 系統的レビュー k=29 | **65.5% が有意・正・r<0.5**。⚠️ 異質性のためメタ分析不能 | C3 の独立領域での再現。 |
| B7 | Corvalán C, Reyes M, Correa T, Dillman Carpentier FR, Taillie LS (2025). Understanding, perceived food healthiness and self-reported food purchase behaviors in Chilean mothers…（**OSF preprint・未査読**） | 10.31219/osf.io/49dbs_v1 | N=889 + 740、前後 2 時点 | 理解 96%/93%（天井）；栄養情報利用 56%→70%, 23%→31% | ★ **同一人物 2 時点のデータがあるのに理解と行動を結んでいない**実例。⚠️ **preprint（未査読）であることを必ず明記して引く**。 |

### 群 C — ⚠️ 二次資料水準（一次全文・abstract とも未取得。引くなら要追加確認）

| # | 書誌 | DOI | 状態 |
|---|---|---|---|
| C1 | Bullock JG, Green DP, Ha SE (2010). Yes, But What's the Mechanism? (Don't Expect an Easy Answer). *JPSP* 98(4):550-558 | 10.1037/a0018933 | ⚠️ Crossref で書誌のみ検算。**abstract すら未取得**（Crossref に無し）。OA PDF が UBC 講義ページに存在（`www2.psych.ubc.ca/~schaller/528Readings/BullockGreenHa2010.pdf`）→ **次ラウンドで一次取得すべき**。 |
| C2 | Ejelöv E, Luke TJ (2020). "Rarely safe to assume": Evaluating the use and interpretation of manipulation checks in experimental social psychology. *JESP* 87:103937 | 10.1016/j.jesp.2019.103937 | ⚠️ **Unpaywall で CLOSED 確定**。preprint 10.31234/osf.io/8427m は OSF が本文を返さず取得失敗。 |
| C3 | Sigall H, Mills J (1998). Measures of Independent Variables and Mediators Are Useful in Social Psychology Experiments: But Are They Necessary? *PSPR* 2(3):218-226 | 10.1207/s15327957pspr0203_5 | ⚠️ **Unpaywall で CLOSED 確定**。二次記述: 「もっともらしい代替説明が無いなら、これらの測定のデータは不要」。 |
| C4 | Webb TL, Sheeran P (2006). Does changing behavioral intentions engender behavior change? A meta-analysis of the experimental evidence. *Psychol Bull* 132(2):249-268 | 10.1037/0033-2909.132.2.249 | ⚠️ 書誌は Crossref 検算済だが **d+=.36 は二次資料由来**。GSE で数値を引くなら一次確認が要る。 |
| C5 | Zhang NJ, Terry A, McHorney CA (2014). Impact of Health Literacy on Medication Adherence: A Systematic Review and Meta-analysis. *Ann Pharmacother* 48(6):741-751 | 10.1177/1060028014526562 | ⚠️ 書誌のみ。Unpaywall は UCF リポジトリを指すが本文未取得。A3 (Miller) と重複領域。 |
| C6 | Correa T, Fierro C, Reyes M, Dillman Carpentier FR, Taillie LS (2019). Responses to the Chilean law of food labeling and advertising. *IJBNPA* 16(1) | 10.1186/s12966-019-0781-x | ⚠️ 書誌のみ。B7 の関連研究。 |
| C7 | Grunert KG & Wills JM の「理解が媒介する」モデル | **未特定** | ⚠️ **二次資料のみ**。原論文（*Journal of Public Health*, 2007 とされる）の DOI を未確認。**引くなら必ず一次確認**。 |
| C8 | Matthews T ら peripheral display 評価枠組（appeal / awareness / distraction / learnability） | **未特定** | ⚠️ **二次資料のみ**。DIS 2006 の "Designing and evaluating glanceable peripheral displays" = 10.1145/1142405.1142457 が候補だが**未検算**。 |

---

## 7. ⚠️ 否決リスト（カード本体に書いてはならない主張）

| 主張 | 票 | 否決理由 |
|---|---|---|
| 「Hawley 2008 の知識↔選択の関連は、GSE の設計判断に使える大きさである」 | **1-2** | ★ **効果量が報告されていない (p<0.01 のみ)、全文は Unpaywall で CLOSED 確定**。N=2412 では極小効果でも p<0.01 になる。外挿先も仮想的治療選択の 1 回きり web survey で、作業行動の変化量とは別物。→ **「関連の存在」までしか引けない**。 |
| 「理解を上げる視覚特徴と、行動を変える視覚特徴は別である（Ancker 2024）」 | **0-3** | ⚠️★★★ **誤帰属**。検索エンジンの要約がこの文を Ancker 2024 (*JAMIA*) に帰属させたが、**全文を取得して照合した結果、本論文にその明示的な区別は存在しない**。本論文が言うのは「動的・対話的表現は静的表現に対し優位を示さない」まで。→ **この主張の出典は不明のままであり、使用禁止**。 |
| 「message perceptions が負 (β=−0.35) だから、理解度は行動に負に効く」 | **1-2** | ⚠️ **構成概念のすり替え**。PME の "message perceptions" は message 属性への評定（信憑性・注意喚起等）であって**客観的理解度尺度ではない**。GSE の可読性に読み替えられない。 |
| 「Corvalán 2025 は理解度と購買行動の個人内関連を示した」 | **0-3** | 前後 2 時点で両方を測っているが、**両者を結ぶ解析を一切していない**（abstract 照合済み）。かつ理解は 96%/93% の**天井効果**で分散がほぼ無い。加えて**未査読 preprint**。 |
| 「健康リテラシー r=.14 は、可読性が行動の前提であることを支持する」 | **0-3** | ★ **対称性の適用**（GSE に有利な読み替えを同じフィルタにかけた）。r=.14 は分散の 2% 未満であり、「前提（ゲート）」の証拠にはならない。むしろ**前提説を弱める**。 |

---

## 8. ⚠️ 取得できなかったもの（経路と失敗理由）

| 対象 | 試した経路 | 結果 | 「探せば取れる」のか「OA に存在しない」のか |
|---|---|---|---|
| **Hawley et al. 2008 全文（効果量）** | Unpaywall → **is_oa: false**（OA location ゼロ）／Europe PMC → abstract のみ（PMID 18755566、PMC 収録なし） | ⚠️ **OA に存在しない**（CLOSED 確定）。効果量が取れないため C1b が否決になった | **取れない**（Elsevier 購読が要る）。★ **この 1 本の効果量が RQ α の中心値なので、購読経路があるなら最優先** |
| Mathur 2025 (*AMPPS*) 本文 | SAGE full → **HTTP 403**／Semantic Scholar `openAccessPdf` → DOI へリダイレクト | GOLD OA (CC BY-NC) と判明しているが本文未取得。**著者 abstract のみ一次取得** | ★ **取れるはず**。OSF preprint 10.31219/osf.io/9y8re が存在するので次ラウンドで直接 PDF を落とす |
| Ejelöv & Luke 2020 (*JESP*) 全文 | Unpaywall → **is_oa: false**／PsyArXiv preprint 10.31234/osf.io/8427m を WebFetch | ⚠️ **OA に存在しない**（CLOSED 確定）。OSF はページ本体を返さず "OSF" のみ（JS レンダリング） | **取れない**（機関購読が要る）。preprint は `osf.io/8427m/download` の直リンクなら可能性あり |
| Noar et al. 2018 (*Health Communication*) 全文 | PMC6538475 → **reCAPTCHA でブロック**／Europe PMC `fullTextXML` → **0 バイト**（isOpen: N） | abstract は Europe PMC `search?query=DOI:...&resultType=core` で一次取得できた | △ PMC は著者原稿を持つ（inEPMC: Y, isOpen: N）ので、ブラウザ経由なら取れる可能性 |
| Bullock, Green & Ha 2010 全文 | Crossref → 書誌のみ（abstract 無し） | ⚠️ 二次資料水準のまま | ★ **取れる**。UBC の講義用 OA PDF が既知（§6 群 C1） |
| Fernandes 2014 / Sigall & Mills 1998 / Zhang 2014 全文 | Unpaywall → 全て **is_oa: false** | Fernandes は **Crossref の著者 abstract で必要数値を確保**。他 2 本は二次資料水準 | Fernandes は SSRN / budgetchallenge.com に PDF があるらしい（未取得） |
| Semantic Scholar による網羅探索 | `api.semanticscholar.org/graph/v1/paper/search` | ⚠️ **HTTP 429 Too Many Requests**（API キー無し） | ★ API キーがあれば「comprehension × behavior × within-person」の網羅探索が可能。**次ラウンドの改善点** |
| Grunert & Wills 原論文 / Matthews の peripheral display 論文 | WebSearch の要約のみ | ⚠️ **DOI 未特定**。二次資料水準 | **取れる**（DOI 特定が未着手なだけ） |
| **「アンビエント／抽象表示で理解度と行動変化を個人レベルで結んだ HCI 研究」** | angle 1・angle 3 の複数クエリ（glanceable / peripheral display / eco-feedback / personal informatics / 自己追跡可視化） | ⚠️★★★ **1 件も発見できず**。HCI の peripheral display 評価は comprehension を評価軸に持つ（Matthews の 4 基準）が、**行動変化と結んだ研究に到達しなかった** | ⚠️ **「探索が足りない」のか「存在しない」のかを本ラウンドでは切り分けられていない**。ACM DL は Cloudflare で閉じており OA 経路が無い。★ 次ラウンドで Semantic Scholar API キー＋ACM の OA 版で再確認すべき |

---

## 9. 次ラウンドへの「やり残し」

★ **(1) Hawley 2008 の効果量（RQ α の中心値）が CLOSED で取れていない。**
★ **(2)「アンビエント表示 × 理解度 × 行動」を HCI 側で確認しきれていない**（探索不足か不在かが未分離）。
この 2 つを埋めれば、判断 (i) の前提の書き換えは実証的にも閉じる。
