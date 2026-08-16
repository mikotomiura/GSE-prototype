# 卓上の可搬な物理オブジェクトと「身体活動 → 表現」の連動 — 具体案を探すサーヴェイ (2026-08-15)

> `/literature-review` 1 ラウンド。★ 研究者の指示（原文）:
> 「**キューブなどはポケットWi-Fiみたいな形で持ち運びが可能であり, パソコンの隣などでの視界に
> 妨げにならない程度のそばに置く感じでよいのでは**」
> 「**歩行をすることにより, そこメディア表現の箇所が改善されるまたは変化が起きるという形にするのはどうだ**」
> 「これらの中で…様々な問題や課題が見えているのだが**具体的な改善案などがないかリサーチ・サーヴェイしてから
> 具体的な案出しをしてくれないか**」

## 動機（★ なぜこのラウンドか）

★ 前ラウンド（2026-08-14）は **「音が要るか」**を問うて **「音が優れている証拠は無い」**で終わった。
★ 本ラウンドは**その先**——研究者が具体的な形（**可搬な物理オブジェクトを机の隣に常在**させ、
**歩行を表現に連動**させる）を出したので、⚠️ **その形に既に見えている課題を解く具体案が先行研究にあるか**を探した。

⚠️★★★ **前提の訂正が 1 件ある** —— 前セッションの引き継ぎは研究者の直感 1 を **「pull 型（見に行く）」**と
符号化していたが、★ 研究者の原文は **「見**れる**ようにする」**であり、**遠くではなく周辺**である。
→ ★ **本ラウンドは「常在・周辺・可搬」を前提に探索した。**

## 検証状態

| 項目 | 数 |
|---|---|
| 探索 angle | **6**（★ 反証 angle 2 つ内蔵: 報酬否定側の対抗メタ分析 ／ null・悪化・慣化） |
| 取得ソース | 約 28（★ うち **一次全文 6 本**: StatCounter / Deci-Koestner-Ryan / UbiFit CHI08 / UbiFit UbiComp08 / Spark / Chasing Shadows） |
| 新規登録 | **[P98]–[P107]（10 件）** |
| 抽出 claim | 7 |
| カード | 8 |
| 敵対的検証 | ★ **3 レンズ**（内的妥当性 / 外的妥当性・外挿 / 効果量の頑健性） |
| confirmed | 4（うち 3-0 が 2 件） |
| ⚠️ **否決** | **2 件** |
| ★ 判定不能（該当研究ゼロ） | **1**（★ RQ-2 の核心） |

## gate 判定（要点先出し）

| 下位問い | 温度 | 1 行 |
|---|---|---|
| **RQ-1 卓上・常在の物理/アンビエント表示の先行** | ★ **確定（実在し、統制つきの効果もある）** | ★★★ **UbiFit が N=28・3 条件・3 か月で「表示ありは活動を維持、表示なしは有意に低下」を出している**（[P101]）。⚠️ **効果は「増加」ではなく「維持」** |
| ★★★ **RQ-2 身体活動を「測らずに」表現へ結びつけた設計** | ⚠️★★★ **判定不能（該当研究ゼロ）** | ⚠️ 6 角度で探して**ゼロ**。★ 見つかった系はすべて**活動そのものを計測して表示している**。→ ★ **「歩行を測らず、戻った後の打鍵で表現が変わる」形は空白**であり、⚠️ **空白は有望を意味しない** |
| **RQ-3 「改善」でなく「変化」だけの非評価的表現** | ⚠️★★ **部分的に否決される** | ⚠️★★★ **実証があるのは「純粋な非評価」ではなく「罰を外した非対称な正の強化」**（[P100] 逐語）。★ 私が前セッションで推した「純粋な記録版」は、**この分野の実証の外側にある** |
| **RQ-4 可搬な自己状態オブジェクトの社会的可視性** | ★ **確定（ただし N=1）** | ★★★ [P98] が**まさにこの形**（ポケットに入る e-ink・机の laptop の隣）を **36 週**運用し、**他者からの「それ自分の被引用数？」**という反応と、⚠️ **「回復空間へ評価的圧力が拡張する」**という著者自身の結論を残している |
| **RQ-5（反証）null / 悪化 / 慣化** | ⚠️ **偏りを再確認** | ⚠️ **明確な null / 悪化の RCT はまた見つからなかった**（★ カード 9・[P90] の警告と同じ非対称が再現）。★ 慣化は [P102] が **3 週で 43.5% 減 vs 14.3% 減**という形で示す |

> ★★★ **本ラウンドの芯**: **研究者の「机の隣に常在する物理オブジェクト」という形は、
> この分野で最も強い統制つき証拠（[P101]）が支持する側にある。**
> ⚠️★★★ **しかし「歩行を連動させる」形は、そのままだと実証のある設計から外れる** ——
> ★ **実証があるのは「罰を外した正の強化」であって「純粋な記録」ではない**（[P100]）。
> ⚠️ **そして「測らずに連動させる」案には、支持も反証も存在しない。**

---

## カード 1: ★★★ 抽象・非数値のアンビエント表示は、3 か月・統制つきで活動の「維持」に効いた **[検証済 2-1]** [P101]

**1. どんなもの**: Consolvo, Klasnja, McDonald ら (UbiComp 2008)。**N=28・3 実験条件・3 か月**、
★ **冬の休暇シーズン**を狙って実施した野外実験。UbiFit の **glanceable display**（携帯の壁紙に咲く庭）の
有無・fitness device の有無を要因とした。

**2. 先行研究と比べてどこがすごい**: ★★★ **この分野で GSE が参照できる、最も統制の効いた実地結果**である。
★ アンビエント表示の効果を **統制条件つき・3 か月・実生活**で測っている例は稀。

**3. 技術・手法の肝**: 混合モデル。固定効果に **Glanceable Display (Y/N)・Fitness Device (Y/N)・Age・Gender・
BMI・Week in Study・Holiday Week (Y/N)** と、Display / Device × Age・Gender・Week・Holiday の 2 元交互作用。

**4. どうやって有効だと検証した**（★ 一次逐語ベース）:
- **Display × Week in Study** on Activity Duration: ★ **F(1, 312) = 6.51, p = .0112**
  → 逐語: **"it was the average Activity Duration for participants without the glanceable display that
  decreased over time … While participants who had the glanceable display maintained, on average,
  their activity duration"**
- **Display × Holiday Weeks**: ★ **F(1, 311) = 4.11, p < .05**、post-hoc Tukey HSD で
  逐語: **"Activity Duration significantly decreased over Holiday Weeks for participants who did not have
  the Glanceable Display, Activity Duration over Holiday Weeks remained as high as during non-holiday
  weeks for participants who had the Glanceable Display"**

**5. 議論はあるか**:
- ⚠️★★★ **効果は「増加」ではなく「維持」である。** ★ 著者の主張も逐語で
  **"were able to maintain their physical activity level (even during the holidays)"** であって増加ではない。
- ⚠️★★ **Activity Count では有意に達していない**（逐語: **"although it did not reach statistical
  significance (p = 0.095)"**）。★ **2 つの指標のうち 1 つは null** である。
- ⚠️★★ **標準化効果量が報告されていない**（F 値のみ）。★ **他の証拠と大きさを比較できない。**
- ⚠️★★ **多重比較**: 固定効果 7 つ ＋ 2 元交互作用 8 つを 1 モデルに入れ、**補正の記載が無い**。
  ★ N=28 を 3 条件に割ると **1 条件あたり約 9 名**。
- ⚠️ 対象は**身体活動**であって知的作業ではない。2007–08 年の携帯電話。

> ★★ **GSE への含意**: ★ **「常在する抽象表示が、放っておくと落ちるものを落ちないように保つ」**という
> 形の効果は実在する。★★★ **GSE の主張範囲（機会を保存する・壊さない）と、この「維持」という
> アウトカムの形は一致している** —— ★ **増加を目標に置く必要が無い。**

## カード 2: ★★★ この分野の実証は「非評価」ではなく **「罰を外した非対称な正の強化」** に付いている **[検証済 3-0]** [P100]

> ★★★ **本ラウンドで、私（エージェント）の前セッションの推奨を最も強く揺さぶった 1 件。**

**1. どんなもの**: 同じ UbiFit の **CHI 2008** 論文（n=12・3 週の野外試行）。★ 表示の**設計原則が逐語で書かれている**。

**3. 技術・手法の肝（★ 逐語）**:
> "With UbiFit Garden's display, a healthy garden represents healthy behavior. **UbiFit Garden uses positive
> reinforcement—the user is not punished for inactivity, for example, with wilting flowers, weeds, or a
> stormy sky. Instead, the garden will simply be sparse (or empty) with a blue sky and healthy grass.**
> If the user does not meet the weekly goal, the garden will simply **not have the large butterfly**"

★ 設計系譜も逐語で書かれている:
> "using **non-literal, understandable, aesthetic representations of behavior** (as done by Fish'n'Steps),
> … providing **positive reinforcement rather than punishment** (drawing from Houston's success and
> **problems found by Fish'n'Steps**)"

★ 併せて: 大きな黄色い蝶＝週間目標達成、★ 小さな白い蝶は **"recent goal attainments, serving to
reward and remind the user of past successes"**。★ 庭は**週で区切られる**
（逐語: "at the beginning of the week—… **the absence of flowers means no activity this week**"）。

**5. 議論はあるか**:
- ⚠️★★★ **UbiFit は「純粋な記録版」ではない。** ★ 著者自身が **"reward"** と書いており、
  **目標・達成・蝶という報酬構造を持っている。**★ 外したのは**罰の側だけ**である。
- → ⚠️★★★ **したがって「評価を一切与えない表現」の実証は、この分野には無い。**
  ★ **私が前セッションで推した「改善ではなく変化だけ」は、[P101] の実証の外側にある。**
- ★ 逆に言えば、**設計の分解能が上がった** —— 「評価するか / しないか」の二択ではなく、
  ★★ **「上向きの評価を出すか」と「下向きの評価を出すか」は別々に決められる。**

> ★★★ **GSE への含意**: ★ **`spec` §4 の「快さは高いまま固定し、事象性にだけ状態を写す」という既定は、
> UbiFit の「罰を外す」と同じ構造である**（★ 独立に同じ所へ来ている）。
> ★ **「歩かなかった日」の設計解は、この分野に既にある —— 「悪くする」のではなく「疎らにする」。**

## カード 3: ★★★ 「期待された評価」は、肯定的フィードバックを伴っても内発的動機を損なう **[検証済 2-1]** [P99]

**1. どんなもの**: Deci, Koestner & Ryan (1999) *Psychological Bulletin*。**128 研究**
（94 の公刊論文 ＋ 19 の学位論文）のメタ分析。free-choice 行動指標 101 件、自己報告の興味 84 件。

**4. どうやって有効だと検証した**（★ 一次逐語・実数）:

| 条件 | free-choice 内発的動機への d |
|---|---|
| engagement-contingent | **−0.40** |
| completion-contingent | **−0.36**（外れ値 1 件除去後 −0.40, CI [−0.54, −0.25]） |
| performance-contingent | **−0.28**（外れ値除去後 −0.23, CI [−0.33, −0.13]） |
| ★★★ **performance-contingent で「最大報酬に届かなかった」群** | ★★★ **−0.88（本メタ分析中、全群で最大の毀損）** |
| Pritchard ら 1977（メタ分析対象外） | free-choice **−0.95** / 興味 **−0.76** |

★★★ **さらに決定的なのは言語的報酬の側である**（逐語）:
> "we examined the effects of these conditions meta-analytically and found that **anticipated evaluation
> (when followed by positive feedback) led to significant undermining of free-choice behavior with a
> composite effect size of d = −0.40 (CI = −0.71, −0.09)**. It seems, therefore, that **expected verbal
> rewards may undermine intrinsic motivation just as expected tangible rewards do.**"

**5. 議論はあるか**:
- ⚠️★★★ **この文献は係争中である。** Cameron & Pierce (1994) / Eisenberger & Cameron (1996) は
  「毀損は限定的で回避可能」と主張し、[P99] への直接の反論 (Eisenberger & Cameron, 1999) と
  再反論 (Deci et al., 2001) / 再々反論 (Cameron, 2001) が続いている [P107]。
  ★ **一方の側だけを引いてはならない。**
- ⚠️★★ **ほぼ全て実験室研究**で、対象は学生・児童が中心。**短期**である。
- ⚠️ **自己報告の興味では効果が小さい**（engagement −0.15 / completion −0.17）、
  ★ performance-contingent の自己報告は **d = −0.01 (CI [−0.10, 0.08]) ＝ 効果なし**。
  → ★ **「行動指標では出るが自己報告では出ない」**という非対称がある。

> ★★★ **GSE への含意（★ 研究者の提案に直接効く）**:
> **「歩けば表現が改善する」は、定義上 performance-contingent かつ anticipated evaluation である。**
> ★ **歩かなかった日／歩きが足りない日 = 「最大報酬に届かなかった」群 = d = −0.88 のセル**にあたる。
> ⚠️ ただし**係争中の文献であり、実験室・短期**である。**断定に使わず、設計の危険標識として使う。**

## カード 4: ★★★ 可搬な個人指標ディスプレイの 36 週 —— 「回復空間へ評価的圧力が拡張する」 **[効果は 1-2 否決 → 設計仮説として保持]** [P98]

> ★★★ **研究者の形（ポケットに入る・机の laptop の隣・持ち運ぶ）と、ほぼ完全に一致する唯一の先行。**

**1. どんなもの**: Oppenlaender (PerDis '26)。**Raspberry Pi Zero 2 WH ＋ Waveshare 2.3" e-ink
(250×122)**、バッテリ駆動、**ポケットに入る**。Google Scholar の被引用数を **7–22 時に毎時 4 回**更新。
★ **一人称の自己民族誌**で **36 週（2025 年 3–11 月）**——通勤・出張（日本での学会）・在宅・欧州旅行に携行。

**2. ★ GSE にとって決定的な一致点**:
- 逐語: **"the device always rested in my peripheral vision when working"**（★ **常在・周辺**）
- 逐語: **"The device sat near my laptop."**（★ **PC の隣**）
- ★ **"During longer stationary work, the device was docked and kept powered via USB"**
  → ★★★ **「据置時は USB、持ち出すときは電池」という形が、実際に運用されている。**

**4. 何が起きたか**（★ 一次逐語）:
- ★ **微小確認の常態化**: **"a subtle gravitational pull"** / 更新時に e-ink が光ることで
  **"ambient presence (and magnetic pull)"** が生じた（★ push 通知ではない）。
- ⚠️★★★ **減少への負の反応**: **"I recall glancing at the display after returning from lunch and noticing
  that my citation count had decreased by one. I shared my frustration over this decrease in our research
  group's social network."**
- ⚠️★★★ **停滞への自己疑念**: **"During a long stretch in midsummer, I started doubting if my personal
  year-end goals could be reached."**
- ⚠️★★★ **社会的可視性（RQ-4 の一次証拠）**: 来訪者が **"Is that your citation count?"** と尋ね、
  **"a tool, a joke, or a status display"** かの議論になった。著者の総括は
  **"the same numbers that felt companion-like to me could appear as self-promotion or pressure to others."**
  ★ 車内では見知らぬ人に **"You carry around how much people cite you?"** と言われた。
- ★ **携行による伴侶性**: **"companionship was most pronounced during liminal moments: waiting for a bus,
  brewing coffee in the morning, or grabbing the device when heading to work."**

**5. 議論はあるか**:
- ⚠️★★★ **効果の主張には使えない（1-2 否決）**: **N=1・著者自身が設計者・統制なし・自己民族誌**。
- ⚠️ 表示は**数値**であり、しかも被引用数は **外部規範を持つ指標**（[P48] の血圧と同型）。
  ★ **抽象符号なら同じことが起きるとは言えない。**
- ★ **それでも設計仮説としては極めて重い** —— ★ 著者自身が中心的な設計課題として名指しした逐語:
  > **"The same ambient access that supports reflection also extends evaluative pressure into spaces that
  > might otherwise offer distance from it. This tension between reflective benefit and evaluative reach is,
  > I believe, the central design challenge for ambient scholarly displays."**

> ★★★ **GSE への含意**: ★ **「Wall が出たらキューブを持って席を立つ」案は、この逐語が名指しした危険そのもの**
> ——★ **持ち出すことは、評価的圧力を回復の空間へ運ぶことである。**
> → ★ **持ち出すなら、外では黙っていなければならない**（★ 演繹であって実証ではない）。

## カード 5: ⚠️★★★ 抽象表現でも「減る・停まる」は否定的に読まれる **[検証済 2-1]** [P98] [P102]

**1. どんなもの**: 2 つの独立な系で**同じ形の観察**が出ている。

**2. 観察**:
- [P102]（WhoIsZuki・CHI 2020・N=16・3 週）: 参加者は履歴表示の喪失に反応し、
  **"feeling bad about all the birds going away"** / **"What happened to my roses?!"** と述べた。
- [P98]: **停滞そのもの**が年末目標への自己疑念を生んだ（カード 4）。

**3. ★ 併せて出た逆向きの要求**: ⚠️★★★ [P102] では**参加者の側から罰を求める声**が出ている ——
**単一章条件の 2 名が、動機が落ちたときの「不利な物語展開」（活動の消去・章のやり直し・"game over"）を要望した。**

**5. 議論はあるか**:
- ⚠️ 両者とも**質的観察**であり、統制された比較ではない。
- ⚠️ [P102] は **N=16・3 週・4 条件（1 条件 4 名）**で、著者自身が
  **"This deployment was not intended to 'prove' behavior change"** と明記している。
- ★ しかし **2 つの独立な系・異なる母集団・異なる符号（数値 / 物語）で同じ向き**に出ている。

> ★★★ **GSE への含意**: ★★ **「悪いことを表示しない」だけでは足りない。**
> **「良かったものが減る / 増えない」こと自体が否定的な信号になる。**
> → ★ **設計解は 2 つ: (a) 一度現れたものを減らさない ／ (b) 空の状態そのものを成立した絵にする**
> （★ 後者は [P100] の **"sparse (or empty) with a blue sky and healthy grass"** そのもの）。

## カード 6: ★★ 同じ表現を繰り返すと 3 週で慣化する（43.5% 減 vs 14.3% 減） **[検証済 2-1]** [P102]

**1. どんなもの**: Murnane ら (CHI 2020)。身体活動を**多章の物語**として lock/home 画面に出す。
**N=16・3 週・被験者間 4 条件**（多章 / 単章 × 通知あり / なし）。

**4. 数値**:
- ★ **第 2→3 週の記録活動の減少: 単章 43.5% / 多章 14.3%**
- 目標 100% 達成者: 第 2 週 **多章 6/8 vs 単章 1/8**、第 3 週 **6/8 vs 2/8**
- 画面確認回数は多章が単章より **38% / 30.2% / 24.2%**（第 1–3 週）多い
- ⚠️ **通知の主効果は有意でなく、通知×章長の交互作用も無い**

**5. 議論はあるか**:
- ⚠️★★ **N=16 を 4 条件に割っている（1 条件 4 名）。** ★ 著者自身が効果証明を意図していないと明記。
- ⚠️ 単章条件は「同じ話の繰り返し」であり、★ **GSE の層 0（情報を運ばない定常音）とは性質が違う**
  —— 単章は**情報を運ぶはずのものが運ばなくなった**状態である。
- ⚠️ **美的不一致の報告**: 3 名が **"too cutesy" / "juvenile"**、1 名は公共の場での表示に
  **"It is so cutesy that, at my age, I'm a little embarrassed."**

> ★★ **GSE への含意**: ★ **内容が変わり続けないと 3 週で落ちる。**
> ★ これは `spec` §2 改訂（層 0 の自律変異を許す・S3-D11）と同じ方向を独立に支持する。
> ⚠️ **併せて「美的トーンが本人に合わないと公共の場で恥ずかしくなる」** ——
> ★ **可搬・他者から見える形では、美的判断が受容性の一部になる**（[P98] の社会的可視性と同型）。

## カード 7: ⚠️★★★ 「身体活動を測らずに表現へ結びつけた設計」は **存在しない**（判定不能） **[検証済 3-0]** [P98]–[P103]

**1. どんなもの**: ★ 「回復活動（歩行等）そのものを計測せず、**その後の作業の変化**を通じて
表現が変わる」という設計を 6 角度で探した。

**2. 結果**: ⚠️★★★ **ゼロ。** 見つかった系（UbiFit / Fish'n'Steps / WhoIsZuki / Spark / StatCounter /
高齢者の座位物理化 [P106]）は、★ **例外なく対象の活動そのものを計測して表示している。**

**3. なぜこの空白が重要か**:
```text
[P77]（計測それ自体が楽しさを下げる・回復活動で害が最大）が本当なら
      ↓
回復活動を計測しない設計が要る
      ↓
★ しかし「計測せずに連動させる」系は、探した範囲に 1 つも無い
      ↓
⚠️★★★ つまりこの案には、支持する証拠も反証する証拠も存在しない
```

**5. 議論はあるか**:
- ⚠️★★★ **空白は有望を意味しない**（★ 前ラウンドのカード 10 と同じ警告）。
  ★ 「誰もやっていない」のか「やる意味が無いから誰もやらないのか」は**区別できていない**。
- ⚠️ ★ 近い発想として **「反応性を避けるため状態を時間差で見せる」**という記述を 1 件見つけたが、
  ⚠️ **出所が特許（査読なし）**であり、**根拠に使ってはならない**。★ 着想としてのみ記録する。

> ★★★ **GSE への含意**: ★ **「歩行を測らず、戻った後の打鍵で表現が変わる」案は、この分野の空白である。**
> ⚠️ **同時に、証拠ゼロの案である。**★ **採るなら「新規貢献」として自分で測るしかない。**

## カード 8: ⚠️ 肯定側への偏りが、本ラウンドでも再現した **[検証済 3-0]** [P90]（既存）

**1. どんなもの**: ★ RQ-5（反証 angle）として **null / 悪化 / 撤去後**の報告を明示的に探した。

**2. 結果**: ⚠️ **明確な null または悪化を報告した統制つき研究は、また見つからなかった。**
★ 見つかった否定的所見はすべて **同じ論文の中の副次的な記述**（[P102] の慣化・美的不一致、
[P98] の負の情動、[P100] が引く Fish'n'Steps の "problems"）である。

**5. 議論はあるか**: ★ これは前ラウンドのカード 9（[P90] Hazlewood ら「**無視されるように設計されたものを
深く評価することは原理的に難しい**」）と**同じ非対称の再現**である。
⚠️ **この非対称自体が出版バイアスの兆候**である。

> ★★ **GSE への含意**: ★ **上のカード 1 の効果量（唯一の統制つき結果）も、この偏りの中で読む。**
> ★ **GSE 側で ON/OFF の対照を自前で組むことの価値は、本ラウンドでさらに上がった。**

---

## ⚠️ 否決リスト

| # | 否決した主張 | 票 | 否決理由 |
|---|---|---|---|
| **S-1** | ★ **「可搬な個人指標ディスプレイは評価的圧力を回復空間へ拡張する」を効果として主張する** | **1-2** | ★ **N=1・自己民族誌・著者＝設計者・統制なし**。★ **設計仮説としてのみ保持**（カード 4） |
| **S-2** | ⚠️★★★ **「非評価的な表現（変化だけ・改善なし）で行動が保たれる」** | **0-3** | ⚠️ **この主張を支持する実証が 1 件も無い。**★ 実証がある [P101] の表示は **目標・達成・蝶という報酬構造を持つ**（[P100] 逐語で著者自身が "reward" と書く）。★ 外されているのは**罰の側だけ**である。→ ★ **「純粋な記録版」は未検証の設計であり、実証済みの設計ではない** |

★ **対称性の記録**: ⚠️ **否決 2 件のうち S-2 は、私（エージェント）が前セッションで研究者に推した案そのもの**である。
★ **自分の推奨を否決する側に倒した。**

## ⚠️ やり残し（★ 次ラウンドの入口）

1. ★★ **Fish'n'Steps (Lin et al. 2006) の全文** —— ★ [P100] が **"problems found by Fish'n'Steps"** として
   **罰を外す根拠にした当の論文**なのに、⚠️ **一次が取れていない**（★ リンク 404）。
   ★ **「罰を出すとどうなるか」の唯一の直接証拠になりうる。**
2. ★★ **[P101] の効果量（標準化）** —— ★ F 値しか報告されておらず、**他の証拠と大きさを比較できない。**
3. ★ **[P106]（高齢者の座位を家の装飾品で物理化）の全文** —— ★ **abstract のみ**。
   ★ 「slow revelation」「aesthetic ambiguity」という設計語彙が GSE に直接使える可能性がある。
4. ⚠️ **[P107] の係争の現在地** —— ★ 報酬が内発的動機を損なうかは**決着していない**。
   ★ 2010 年代以降の再解析・事前登録再現を追えていない。
5. ⚠️ **前ラウンドからの持ち越しは未着手のまま**: Warnock 2011 全文 / Maglio & Campbell 2000 全文 /
   Klatte 1995 / Browne & Cruse 1988 / Olton & Johnson 1976 の原著。
