# サーヴェイ結果 2（angle B / D / E / F）

> ★ angle G（逐語照合）と angle C（個人化）は `survey-notes.md` にある。

---

## B. 他者可視性 — 未決 #2（PS-Q5）（★ 完了・9 件）

### ★★★ 発見 1: **「本人だけに見せる」は運用として成立しない**

★ 実地の critical incident 調査（N=174）—— **観察者 84 名のうち本人に気づかれたのは 6 名 = 7.1%**。
逐語 *"Users were aware of it in only 7 % of the incidents reported by observers."*
★ スマホが 157/175 = 89.7%。⚠️ **観察者は主に「知っている人」**（公共空間を除く）。

⚠️★★★ **ところが本人はそのリスクをほぼ知覚していない** —— 1 か月の ESM（N=52・**3,410 状況**）で
**ショルダーサーフィンが「関連するリスク」と知覚されたのは 11 件 = 0.32%**。
→ ★ **「他者に見えるので抽象化しました」と説明しても本人には響かない。**

★ **量的な朗報**: 27 日で平均 43.0h のスマホ使用のうち **2.9h ≒ 6.7% が「ロック状態のまま」**
（★ ロック画面で時刻・通知を見る時間）。→ **ロック画面は本人が習慣的に見る面として実測で存在する。**

### ⚠️★★★ 発見 2: **「抽象化すればのぞき見から守れる」の出所論文は、それを一度も測っていない**

★ 全文検索の結果 —— UbiComp 2008 の常在表示論文に **`privacy` は導入部の 1 回のみ**、
**`onlooker` / `observer` / `stranger` / `bystander` は 0 回**。著者自身も逐語 **"a sense of privacy"** と書く。
→ ⚠️★★★ **GSE はこの論文を「抽象＝プライバシー」の根拠に使ってはならない。**

### ★★★ 発見 3: **選択的な難読化は THAT を漏らす**

逐語 *"Only obfuscating specific photos would already give away potentially sensitive information to an
onlooker like 'the user does not want me to see this specific photo so there is something about it'."*
→ ⚠️★★★ **GSE で「`stuck` のときだけ抽象度を上げる / ぼかす」は、`stuck` であることを他者に告知するのと等価。**
★ **難読化は常に一様でなければならない。**

⚠️ 難読化の**種類**に強く依存する（n=18・162 観察試行）: 記述精度の低下は
Oil Paint `chi2(2)=15.085, p<.001` / Crystallize `chi2(2)=13.244, p<.001` で有意だが、
**直感的なモザイク（Pixelate）は有意差なし**（high 条件で「完璧な記述」が **9/36 = 25%**）。
⚠️★★★ **本人は自分の読み取り能力を過小評価する** —— 逐語 *"they were astonished 'how easy it was'."*
→ ★ **ユーザテストで「読めますか」と *事前に* 聞いてはいけない。実測で判定する。**

### ★★★ 発見 4: **THAT は曖昧にするな。WHAT は曖昧でよい**（★ PS-Q5 に直接答える）

★ 皮膚電気反応の社会的表示（N=10・ペア会話）が **曖昧さを 2 軸に分解**した。逐語:
*"**Ambiguity of meaning** was seen as helpful in supporting a broad range of emotional interpretations
and prompting open-ended reflection. On the other hand, some participants wished to reduce
**ambiguity of observation** in order to feel validated by the system."*

→ ★★★ **「今、何かが表示された」（THAT）は判読可能でなければならない。
「それが何を意味するか」（WHAT）は曖昧なままでよく、そこが唯一うまくいった層である。**

### ⚠️★★★ 発見 5: **「無反応」は「無」ではなく「否定」として読まれる**（★ 判断 9 / 判断 11 に直撃）

★ 表示が変わらなかった場面の逐語（配偶者から）:
*"**Yours are not changing at all. I married an insensitive guy… You don't even feel empathy for the
little guy who's crying.**"* ／ 本人側 *"Oh my god, **do I have no feelings**?"* ／ *"I felt kind of **left out**"*。
→ ⚠️★★★ **「変化なし」を状態の 1 つとして *明示的に描かない* と、本人も他者も「無い」と読む。**
★ **`stable` や 層 0 を「空白」で表すのは危険。**

### ⚠️★★★ 発見 6: **曖昧化しても表示の権威は消えない**

★ 2 日間の日常着用（N=17）—— 逐語
*"**We observed no instances in which participants denied any emotional provenance of a display change
by linking it to temperature instead, although we designed to support this.**"* ／
*"participants used the **override features exclusively** for confirming the shirt's functionality or
demonstrating it to others, **not for performing or hiding emotional responses as we anticipated**."* ／
*"some participants seemed to invest a **potentially harmful degree of authority** in the data display."*

→ ⚠️★★★ **「抽象だから解釈は本人に委ねられる」という前提は成り立たない可能性が高い。**
★ 参加者は**数値が無くても「感情の量」という順序尺度を自作し、自他比較を始めた**。

### ★ [P151] との整合（★ 一見の衝突は解ける）

⚠️ 発見 4–6 の「本人だけ」寄りの結論は [P151]（*"hidden designs essentially remove the technology from
the social situation"*）と衝突するように見えるが、★ **著者自身が両立解を明示している** ——
選択肢は「隠す vs 見せる」ではなく **private display（内省用）か user-controlled public display（社会的呈示用）**。
→ ★★★ **対立軸は `hidden` ではなく `controlled` である。**
⚠️ ただし発見 6 が「制御可能にすれば解決」も楽観的すぎると示す（★ 上書きボタンは使われなかった）。

### ⚠️ 埋まらなかったこと

1. ★ **スティグマ**（下位問 1 の核心）の一次は**発見できず**。
2. ⚠️★★★ **ロック画面上の常在的抽象表示が第三者に読まれたかを直接測った研究は無い。**
   → ★ **GSE の中心的前提はここで実証的に埋まっていない。**
3. ★ **職場文脈が最も弱い**（★ 候補 3 件は書誌確認済みだが**全文にアクセスできず**、
   ⚠️ abstract だけで引くのは禁止のため表から外した）。
4. ★ **打鍵 / 認知状態という題材での先行は無い**（★ 写真・皮膚電気反応・位置のみ）。
5. ★ **THAT / WHAT / HOW の 3 段を名指しした分類学は文献上存在しない** = ★ **GSE が作れる余地**。

### ⚠️ 副次的だが重い: リスク補償

★ プライバシーフィルタを 2 週間与えた研究（N=22・**査読前プレプリント**・対照群なし）——
**物理的に画面を覆う頻度が有意に低下 `p<0.001, d=1.1`**。
→ ⚠️ **「抽象だから安全」と説明した瞬間、本人は画面を隠さなくなり、結果として露出が増えうる。**
⚠️ **プレプリントなので設計根拠として強く引かない。**

---

## D. 招待の面と framing — 未決 #5 / #6（★ 完了・10 件）

### ⚠️★★★ 発見 1: **「PC か スマホか」は文献では決められない**

★ **同じメッセージを「作業中のデバイス」と「別デバイス」に出して比較した実験は存在しない。**
→ ★ **GSE 自身が実験しない限り埋まらない。**

★ ただし **1 点だけ文献が言い切れる** —— ESM（N=31・**有効応答 3,490**・14 日）が、
通知処理の 4 段階（notice / glance / read / act）で **同一面の継続希望**を実測した:

| 遷移 | PC での同一面継続希望 |
|---|---|
| notice → glance | **55.4%** |
| glance → read | **92.2%** |
| read → act | **95.6%** |

→ ★★★ **段階が進むほど「同じ面で終えたい」が急上昇する。面をまたがせる設計が許されるのは
最初期（気づきの直後）だけである。**
⚠️★★★ ただし**この研究のサンプリング枠は「スマホに届いた通知」であり、PC 発の通知が 1 件も入っていない。**
→ **GSE（PC 発）へ外挿してはならない。**

★ **PC 側だけで行動が動く実証はある** —— 18 RCT・**N=1,164**・中央値 8 週:
就業中座位 **−11.79 min/day (95% CI −17.73, −5.86)**、歩数 **+1,029.99 steps/workday (815.97, 1,244)**。
⚠️ **ただし 1 日全体の座位・立位・sit-to-stand 遷移はすべて非有意** ——
★ **就業中に減った座位が就業外で埋め合わされている可能性を排除できていない。**
⚠️ **PC 上 vs 別デバイスの直接比較は 1 件も含まれない。**

### ⚠️★★★ 発見 2: **閾値を置かない招待は、効果量の面では文献に支持されない**

| 一次 | 数値 |
|---|---|
| ★ choice architecture メタ解析の**出版バイアス補正再解析**（334 効果量） | ⚠️★★★ 全体 **未補正 d=0.43 → 補正後 d=0.04 [0.00, 0.14]**。★ **decision information: 0.25 → 0.00 [0.00, 0.00]** / **decision assistance: 0.22 → 0.01 [0.00, 0.07]**。⚠️ **効果が残る唯一のカテゴリは `structure`（default・選択肢構成の変更）＝ GSE が採らないと決めた側**。逐語 *"**no evidence for the effectiveness of nudges remains**"* |
| ★ **HeartSteps MRT**（N=37・42 日・1 日 5 決定点・**非強制の提案・完了判定なし**＝ GSE の招待とほぼ同型） | ⚠️★★★ **Day 1: `e^b=1.66, p<.01`（+66%・+167 歩）→ 2%/日で線形減衰し 28 日目にゼロと区別不能**。★ **42 日平均では `e^b=1.14, p=.06` で有意にすら達しない**。逐語 *"the suggestions **became boring after 2–4 weeks**"* |
| ★ 選択のメタ解析（41 研究・46 標本・290 効果量） | ⚠️★★★ **「圧力・緊張」への効果は `d=−0.03 [−0.33, 0.27]`（ns, k=3）** ＝ **選択肢を開いても感じる圧力は下がらない**。★ 内発的動機は成人で `d=0.25 [0.20, 0.31]`。★★★ **選択機会は 1 回 `d=0.21` より 2–4 回 `d=0.61` が効き、5 回以上で逓減** |
| ★ 自律支援言語の直接検証（**N=521**・2×2 RCT） | ⚠️★★★ **知覚自律 `b*=−.09, p=.799` / 怒り `b*=−.13, p=.721` / 反論 `b*=.37, p=.411` —— すべて null**。逐語 *"participants … perceived high levels of autonomy-support, **regardless of the message frame used**."* |
| ★ リアクタンスのメタ解析 | ★ 高 vs 低 freedom-threatening language → 統合リアクタンス **r=.20 [.16, .23]**、リアクタンス→説得 怒り **r=−.23**。⚠️ **予測区間が広く 0 をまたぐ**（怒り→説得 PI `[−.46, .04]`）。⚠️ 著者留保 *"restricting our findings to **short-term** message effects"* |
| ★ 推奨 / default / 強制の比較 | ★ **自由侵害の序列は 推奨 < default < 強制**。⚠️★★★ ただし **内発的動機が高い人ほど統制的介入で拠出が下がる**（★ 著者自身が *"suggestive, exploratory, correlational"* と限定）→ ⚠️ **GSE の対象はまさに動機が高い局面の本人である。** |

→ ★★★ **結論: 閾値・タイマー・完了判定を置かない判断は *倫理・自由侵害の面では* 文献に支持されるが、
*効果量の面では* 支持されない。**
→ ★★★ **GSE は「効くから閾値を置かない」ではなく「効果を犠牲にして侵襲性を下げている」と明示的に書く方が誠実である。**

★ **閾値の代わりに置ける唯一の設計パラメータは「頻度」と「新奇性」である**
（★ 2–4 回の反復が 1 回より効く `d 0.21 → 0.61`・5 回以上で逓減 ／ ★ 28 日で消える減衰曲線）。

### ⚠️ 埋まらなかったこと

1. ⚠️★★★ **作業中デバイス vs 別デバイスの直接比較実験は存在しない**（★ angle D の中心問い）。
2. ★ 「invitation / offer」対「reminder / should」を**作業中断の文脈で**比較した実験は発見できず。
3. ★ 閾値なしの招待を**閾値ありの版と比較**した研究は発見できず。
4. ★ **「招待の提示それ自体が圧力になる」を直接定量した一次は発見できず**（★ 間接証拠のみ）。
5. ⚠️ 2 件は **403 / CAPTCHA で N・効果量を検算できていない** → ★ **数値根拠として引かない。**

---

## E. 層 A（≤4 秒）の可読性 — ★ §4.3 の穴（★ 完了・10 件）

### ★★★ 発見 1: **時間は律速ではない。争点は意味写像にある**

★ スマートウォッチ実機の 2AFC ＋ 重み付き staircase（~91% 正答へ収束・N=18 × 2 研究）——
**Bar 245 ms [221,272] / Donut 159 ms [155,164] / Radial 1548 ms [1116,2030]**
（24 値時 Bar 360 / Donut 162 / Radial 3593）。
★ 概念検出の下限も **適正マスク下で 53 ms**（⚠️ **「13 ms で意味が読める」は幾何マスクで再現せず
`d'=0.15, t=1.19, p=.127` —— この主張を GSE の根拠にしてはならない**）。
→ ★ **4000 ms は 1–2 桁の余裕がある。**

⚠️ ★ **ただし設計上限は 2000 ms に締めるべき** —— 分野横断の実務基準は
**1 目線 ≤ 2.0 秒 / 総視線離脱 ≤ 12.0 秒**、遮蔽法は **1.5 秒間隔**（24 名中 21 名以上で合格）。逐語
*"When drivers glance away from the forward roadway for greater than 2.0 seconds out of a 6-second period,
their risk of an unsafe event substantially increases"*。
⚠️ 法的拘束力は無く（逐語 *"Conformance is voluntary"*）、二重課題の安全基準である点は留保する。

★ 端末クラスを跨いだ実測でも **peek（≤5 秒）が全 798,423 セッションの 65.2%**（307 ユーザ・実端末ログ）。
⚠️ ただし *"画面が点いていた時間であって見ていた時間ではない"* と別著者が名指しで批判している。

### ⚠️★★★ 発見 2: **未学習の抽象表現は、3 値でもチャンスと区別がつかない**（★ 最も決定的）

★ デュアルタスク実験（Unlearned N=26 / Learned N=49）——
**未学習の低象徴表現（抽象アート・単色四角）の正答率 30–39%（チャンス = 33%）**、
中象徴 52–54%、高象徴 74–92%、テキスト 97%。
★ **学習後は set size 3 も 7 も正答率 93–98% で有意差なし。**

→ ★★★ **層 A を採るなら二択しかない: (a) オンボーディングで明示的に教える、
または (b) 各値が絵として意味の通る high-symbolism 表現にする。★ 中間は無い。**

### ★★★ 発見 3: **段数は「正答率」ではなく「視線コスト」で切る**

★ 同研究 —— 学習後の正答率は set size 3 でも 7 でも 93–98% で差がないのに、
**周辺視のみで同定できた割合は 90% → 76% に落ちる**（単色四角）。
★ 単一次元（色相）で表示要素数に依存しない並列同定が成立するのは **5 色まで（誤り 2.5%）**、
**7 色が上限**（★ 色カテゴリ境界を意識した精密な選色をして誤り 5.2%）。
→ ★ **GSE の 4 値は安全域の内側。**

### ★★★ 発見 4: **色を主符号にしない。代替は「その場で振動する小さな動き」**

★ 周辺視（偏心 7–52 度）の実験（N=12–14）—— 逐語
*"the percentage of undetected targets increased dramatically from **6% to 25%** with the peripheral colour
targets, whereas the failure-to-detect with **motion was less than 2%** in both the near and far field."*
★ 混在環境での色の**識別**誤りは **15–20%**。

★ 使える数値（著者のガイドライン逐語）:
- G3 *"approximately **1° of visual angle** is highly detectable even in pronounced peripheral vision"*
- G4 *"Even relatively slow frequencies are effective. The motions tested had periodic frequencies between **1 and 3 Hz**."*
- G8 *"The **slow linear oscillation** is a good overall signal … not considered intrusive or distracting."*
- ⚠️ G7 *"**travelling motions are significantly more distracting and irritating** than anchored motions."*
  → ★ **移動する動きは使わない。**

⚠️★★★ **上記の実証群に色覚多様性の被験者は 1 人も含まれていない**（★ 色覚正常でスクリーニング）。
→ ★ **色だけで 4 値を分ける設計は文献的に無根拠。**

### ★ 発見 5: **受け入れ基準の言語と、試験の型**

★ アンビエント表示のヒューリスティクス（最終版逐語）:
- *"convey **'just enough'** information. Too much information cramps the display, and too little makes the display less useful."*
- ★ *"The **transition from one state to another should be easily perceptible**."*
  → ★ **層 A は静的な弁別だけでなく *状態遷移の検知可能性* を別途試験する。**
- *"Ambient displays should add **minimal cognitive load** … The display should be intuitive."*

⚠️★★★ **ただし「ambient heuristics が Nielsen より優れる」とは書けない** ——
★ abstract は *"found more, severe problems"* と書くが、**本文の主 ANOVA は逐語
*"There was no statistically significant difference for any factor or combination of factors"*** である。
→ ⚠️ **abstract が本文を誇張している実例がここにも 1 件。**

★ **試験の型**: 提示時間固定 ＋ 強制選択（★ 2AFC ＋ staircase が最小の再現可能な型。
層 A では **提示時間 2000 ms 固定で正答率**を測る方が実装が軽い）。
★ 評価は **3–5 名の heuristic evaluation で既知課題の 40–60%** を拾うところから。

### ★ 発見 6: **データを担わない視覚次元を仕様で明示的に固定する**

★ 3 か月の待受画面フィールド実験の逐語 ——
*"a flower's height has **no relation** to the activity's duration and **varies simply for aesthetics**."*
→ ★ **層 A も「変化してよいが意味を持たない要素」と「変化が意味を持つ要素」を書き分ける。**
★ これは **層 0 の自律変異（S3-D12）と同じ構造**である。

### ★★★ 判定: 4 値を ≤4 秒で弁別させられるか

| 観点 | 判定 | 根拠 |
|---|---|---|
| **時間** | ✅ **問題にならない** | 24 値の大小比較で 162–443 ms。厳格条件の概念検出下限でも 53 ms。★ ただし設計上限は **2000 ms** |
| **段数** | ✅ **4 は安全域の内側** | 並列同定の安全域 5・上限 7。学習済みなら 7 値でも 93–98% |
| **学習** | ❌ **ここが律速** | ⚠️ 未学習の抽象表現は 3 カテゴリでチャンス（30–39%） |
| **写像の一貫性** | ⚠️ **4 値のうち 1 つが異質** | ★ `intervention_active` は「状態推定」でなく「系の動作」。★ 同一の 1 目盛りに混ぜると写像の一貫性が壊れる |

★★★ **サーヴェイ側の推奨（★ 判断 4 に *独立に* 到達している）**:
1. **1 目盛りに載せるのは 3 値（`stable` / `friction_rising` / `stuck`）に留める。**
   ★ set size 3 は周辺視のみでの同定率が最も高い（90%）。
2. **`intervention_active` は 1 目盛りから外し、別チャネル（存在／不在の 2 値）に出す。**
   ★ 具体的には **振幅 ~1°・1–3 Hz のその場振動を on/off** するのが、色に依存せず travelling でなく
   1 目盛りの読みを汚さない唯一の実証済み手段。
3. **学習を前提にできるなら 4–5 値まで拡張してよい。7 を超えない。**

### ⚠️★★★ 必ず併記する留保

★ **上記のどの研究も「内的な認知状態」を抽象表現で弁別させてはいない。**
弁別対象はすべて**外的な量**（棒の高さ・色相・活動種別・メールの送信者群）である。
→ ★★★ **層 A の 4 値弁別は「文献で許可されている（段数・時間ともに範囲内）が、実証されてはいない」。**
★ **受け入れ試験は GSE 側で自前に回すしかなく、文献で代替できない。**

### ⚠️ 埋まらなかったこと

1. ★ **ロック画面そのもの**を対象に提示時間を制限して読み取り正答率を測った研究は**発見できず**。
2. ★ **内的な認知状態のカテゴリ**を抽象表現で提示し弁別させた研究は**発見できず**。
3. ★ 抽象表現の**学習曲線**（何日で 30–39% から 90% に上がるか）を測った研究は**発見できず**。
4. ★ **色覚多様性のある被験者を含めた**時間制限下のカテゴリ弁別は**発見できず**。
5. ★ **「余白」「密度」で状態を弁別させた実証は発見できず**（★ 動き・色・形には数値付き実証があるが、
   ⚠️ **`.idea` §4.1 が第一に挙げる「余白の広さ」「密度や反復」には無い**）。
6. ⚠️ Cleveland & McGill (1984) は**本文が一次未取得（有料）** →
   ★ **「position > length > angle > area」の順位を根拠に使わない。**

---

## F. 最小プロトコル — 未決 #8（★ 完了・16 件）

### ★ 使える計器（★ 一次で検算済み）

| 目的 | 計器 | 数値・逐語 |
|---|---|---|
| **可読性（自由記述）** | **ISO 9186-1:2014** comprehension test | 逐語 *"each respondent is presented with **one variant for any single referent** and asked "What do you think this symbol means?" … Each variant is scored in terms of the **percentage of correct answers**."* ／ *"three is the maximum number of variants for any one referent"* ／ *"the number of referents … does not exceed 15"* ／ ★ *"Instruct the respondent to write the response "Don't know""* ／ 順序は *"no more than 5 booklets in 50 shall have the same order"* |
| **自律性（UI 単位）** | **TENS-Interface 短縮版**（★ 各下位尺度 **3 項目**・relatedness を除外） | ⚠️ 著者留保 *"because items need to be slightly modified to fit the technology of interest, the **psychometric properties of the scales may change**"* → ★ **毎回 α を再計算して報告する義務**。★ autonomy frustration は **α=0.66 / 0.69**（acceptable 止まり） |
| **自律性（生活単位）** | BPNSFS（24 項目）／日誌版 12 項目 | ⚠️★★★ **日誌版はマニュアル逐語で *"The English version of this scale has **not been formally validated yet**."*** → ★ 日本語訳は二重に未検証 |
| **リアクタンス（状態）** | ★ **怒り 4 項目**（irritated / angry / annoyed / aggravated）＋ **thought listing** を 2 名で符号化 | ★ **場面非依存で GSE に最も転用しやすい**。⚠️ 原典本文の逐語は未取得（paywall・引用は二次） |
| | ⚠️ SSR Scale（10 項目・α .88/.76/.81） | ⚠️★★★ **項目が場面固定**（大家シナリオ）→ ★ **`experience of reactance` の 4 項目のみ**を場面適応。★ 他 2 因子は転用不能。⚠️ **ドイツ語で実施**（英語版未検証） |
| **リアクタンス（特性・共変量）** | HPRS-11 | ⚠️ **α を一次で確認できていない**。★ **trait 尺度なので介入効果は測れない** → 共変量以上の役割を与えない |
| **俯瞰** | **think-aloud（Level 1/2 のみ）** | ★★★ 逐語 *"the "think-aloud" effect size is **indistinguishable from zero (r = −.03)**"* ／ ⚠️★★★ *"procedures that entail **describing or explaining** thoughts and actions are **significantly reactive**"* → ★ **「なぜそう思ったか説明して」は禁止**。⚠️ *"**All** verbal reporting procedures tend to **increase times** to complete tasks."* → ★ **時間を指標にしない** |

### ⚠️★★★ 主張の上限（★ 本 angle の最大の収穫）

1. ⚠️★★★ **「ISO 9186 準拠で 66%（67%）を超えたので合格」とは書けない** ——
   ★ **その合格スコアは ISO 9186-1 本文に存在しない。** 本文は逐語
   *"These organizations **can require** … and **can lay down the score**"* ＝ **基準は別組織が定める**とだけ書く。
   → ★ **閾値を置くなら自前で事前登録し、ISO を根拠にしない。**
2. ⚠️★★★ **「形成的だから統計を出さない」を正当化する一次は無い。むしろ逆向きの一次がある** ——
   CHI2014 の悉皆分析（**519 研究**・mode 12 / median 18）は逐語で
   *"many studies published at CHI are **underpowered even to find large effects**: a two condition,
   within-subjects study with 17 participants … has a **power of 0.49** to find a large effect."*
   ＋ *"**Small N Studies, Especially, Should be Replicated**"*。
   → ★★★ **正しい定式化は「形成的だから統計を出さない」ではなく
   「検定力が足りないので確認的検定を主結果にしない・記述統計と 95% CI に留める・複製を前提にする」。**
3. ⚠️ **測定反応性は小さいが 0 ではない** —— 質問すること自体の効果 **g=0.14 [0.11, 0.18]**、
   ★ trim-and-fill 補正後 **g=0.08 [0.04, 0.12]**（94 検定・**N=116,087**）。
   ★ 自己判断の要求（JOL）は全体 `g=0.054`（ns）だが **関連材料で `g=0.32–0.38`**。
   → ★ **「形成的だから反応性は無視できる」は言えない。順序を固定し、事後に限定を書く。**
4. ⚠️ ESM の compliance 期待値は **69.6%（SD 22.8%）** / **75.06% [72.37, 77.65]**（126 研究・N=19,431）。
   ★ **80% を合格線に置かない**（★ 著者自身が 80% に文献的根拠が無いと注記）。
   ★ 項目数は **30 未満**（★ 長い質問紙で compliance 有意低下 `χ²(1)=6.06, p=.014`。
   ⚠️ **頻度は有意でない `χ²(2)=1.07, p=.59`** ＝ **削るべきは項目数であって頻度ではない**）。
   ★ 期間は **7–14 日**（★ 2–4 週で品質劣化）。

### ⚠️★★★ GSE が既に持つ一次との衝突（★ 対処が要る）

★ モバイル ESM のレビューは脱落対策として逐語
*"allowing participants to **measure progress and answer their personal (quantified-self) questions**"* を推奨する。
⚠️★★★ **これは GSE が既に採用済みの [P163]「表示するトラッカーを避けよ / data are not visible にせよ」と
正面から衝突する。**
→ ★★★ **GSE は ESM の脱落対策として自己データ可視化を採らない。**
★ 代わりに **期間短縮（7–14 日）＋ 項目削減（<30）** で負担を下げる。

### ★ [P229]（R² 1–3%）との接続

⚠️★★★ **「俯瞰」を客観指標で裏づける道が塞がっている** —— 自己判断と客観指標の一致（resolution）を
測ろうにも、**客観側の説明力が 1–3% では一致度の解釈が不能**。
→ ★★★ **形成的段階では「俯瞰」を *探索的（記述のみ）* に格下げし、確認的主張をしない。**

### ⚠️ 埋まらなかったこと

1. ★ **「作業中の自己状態への気づき」を状態レベルで測る妥当性検証済み尺度は発見できず**
   （★ thought probe は mind-wandering 専用で、⚠️ **標準文言すら存在しない（69 変種）**）。
2. ⚠️★★★ **抽象表現（非アイコン・*時間変化する* 表現）の可読性を測る確立手続きは発見できず** ——
   ★ ISO 9186 も guessability も**静的記号が前提**。
3. ★ **短期形成的調査における反応性の大きさを直接推定した研究は発見できず**（★ 外挿にとどまる）。
4. ★ カードソートの必要人数は **二次情報のみ** → ★ **根拠に引かない。**
