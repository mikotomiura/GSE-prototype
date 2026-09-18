# 「返権の負荷逆説」と「権限・負担の二重台帳」の先行 —— 自動化の皮肉・責任と権限の二重拘束・A2CR

> 2026-09-19 / `/literature-review` 1 ラウンド（S1）/ **新規性の衝突確認**（★ 生成的返権論の新規性の核）
> 名前空間: `P`（理論基盤）。登録 **[P368]–[P379]**。既登録の再利用: [P42] / [P364] / [P365]。
> ⚠️ 対象の主張は **pre-SSOT の理論草案**（`.idea/20260915-generative-relinquishment-theory.md` §6.3 / §8）であり、`docs/` の主張ではない。

## 動機（★ なぜこのラウンドを回したか）

★ 段 1 の批判的レビュー（`.steering/20260918-theory-critical-review/review-B.md` B-23 / B-24 / B-26 / B-32）が、
草案の新規性の核 ——「**返権の負荷逆説**」（系が意味づけ・認定の権限だけを返し、解釈・検証・修正・応答・説明要求・是正義務・帰結負担を利用者へ残す配置）と
「**権限・負担の二重台帳**」、構成命題 **GR-C1（委譲は双方向）** / **GR-C7（権限の返還と負担の解除は独立）** —— について、
⚠️ **草案の衝突表（§6）に人間-自動化研究の系譜が 1 行も無い**ことを指摘した。
★ 研究者判断（2026-09-18・判断 1 #17）で段 2 に S1 を入れた。⚠️ 判断 1 の見直し条件:「**S1 の結果で新規性の核が既存概念に吸収された場合、J-1 / J-2 を再度伺う**」。

★ 下位問い: **S1-a** 自動化の皮肉・moral crumple zone・責任の空白・検証負担の移転 ／ **S1-b** 権限・能力・責任・制御の整合（A2CR）・制御の遷移（take-over）・adjustable autonomy / mixed initiative。
（★ 自動再開の無人実行のため、分解は事前合意なしで記録した）

## 検証状態

- **探索**: サブエージェント 2 本（Opus・angle: 責任・負担の移転の系譜 ／ 権限の配分・遷移の系譜）
- **取得ソース**: 24 件（★ 全文到達 18 件 ／ abstract のみ 5 件 ／ 未取得 1 件 —— `.steering/20260918-theory-critical-review/survey-S1-raw.md`）
- **claim 抽出**: 19 件 → **検証 19 件**
- **confirmed 11**（3-0 が 9 / 2-1 が 2）／**否決 4**／**判定不能 4**（該当ゼロ）
- ★ **メインが保存本文で逐語を照合した**: [P368] p.775 ・[P369] p.86 / p.88 ・[P370] p.6 / p.7 / p.11 / p.17 ・[P371] p.41 / p.49 ・[P372] p.59 ・[P374] p.171 ・[P375] §3.1 ・[P376] p.2 ・[P377] p.176 ・[P378] p.9 ・[P379] p.1063

### claim 台帳

| # | claim | 出典 | 票 | 温度 |
|---|---|---|---|---|
| 1 | 自動化は自動化しきれない仕事を人に残し、その支援は考慮されない | [P368] | **3-0** | 確定 |
| 2 | 人は原理上の上書き権限と結果責任を持つが、機械の出力を濾過する**支援のない**仕事を負う ＝ **responsibility/authority double-bind** | [P369] | **3-0** | 確定 |
| 3 | 権限・能力・責任・制御を**別概念として主体ごとに**記述し、整合規則（ability ≥ authority ≥ responsibility）を置く枠組みがある | [P370] | **3-0** | 確定 |
| 4 | 制御配分を**変える権限**（change authority）は人・機械の双方に割り当てられる | [P370] | **3-0** | 確定 |
| 5 | 自動化が制御を担いながら人に全責任を残す配置は、既に不整合として名指されている | [P370] | **3-0** | 確定 |
| 6 | 権限と責任が同じ主体に割り当てられないと、責任側に追加の監視作業が生じ、それを作業負荷として別計上する指標がある | [P372] | **3-0** | 確定 |
| 7 | 制御は分散したが責任はそれに応じて拡がらず、人が負担を吸収する（moral crumple zone） | [P371] | **3-0** | 確定 |
| 8 | 生成 AI で利用者の役割が産出から評価へ移る（検証負担の移転） | [P376] | **3-0** | 確定 |
| 9 | adjustable autonomy は定義上、系が自ら自律を下げて人へ制御を移すことを含む | [P374] | **3-0** | 確定 |
| 10 | 自動運転の遷移研究では、自動化側から始まる遷移は**義務的なもの**に限られ、任意の返還は射程外 | [P375] | **2-1** | 確定（留保: 適応的自動化の例外あり） |
| 11 | 人間の監督を要求する政策は、説明責任を構造を決める側から無力な現場の操作者へ移す | [P378] | **2-1** | 確定（留保: 対象は行政アルゴリズム） |
| 12 | 制御を失えば責任も減る（負担は「集中」でなく「空白」になる型） | [P377] | —（対照） | 確定（★ 草案の負荷逆説の**対照**として記録・票は不要） |
| 13 | 「意味の認定・評価・報酬」を**権限**として扱い、系がそれを返す記述 | — | — | **判定不能（今回の範囲で 0 件）** |
| 14 | 解釈・説明要求を**負担項目**として同じ台帳に並べる枠組み | — | — | **判定不能（0 件）**（★ 説明要求の概念上の対応物は [P379] の public accountability） |
| 15 | 権限と責任が**一致したまま**返還しても残務が移る型を独立に立てた記述 | — | — | **判定不能（0 件）** |
| 16 | 系が**価値判断に基づいて任意に**返還する局面の分析 | — | — | **判定不能（0 件）**（★ [P375] が射程外と明記） |
| 17–20 | ⚠️ 否決 4 件 → §否決リスト | — | **1-2 が 1 / 0-3 が 3** | — |

★ 集計の検算: confirmed = #1〜#11（3-0: #1〜#9 ／ 2-1: #10 #11）・対照 = #12（票なし・集計外）・判定不能 = #13〜#16・否決 = 4 ＝ 計 19 件（#12 を除く）。

## gate 判定（要点先出し）

| 下位問い | 温度 | 一言 |
|---|---|---|
| **S1-a** 「権限だけ返して負担を残す」は既出か | **確定（一般形は既出）** | Woods 1985 の **responsibility/authority double-bind** [P369]・Elish の moral crumple zone [P371]・Bainbridge [P368]・Green [P378] |
| **S1-b** 権限と責任を別台帳で記述する枠組みは既出か | **確定（形式は既出）** | Flemisch et al. の **A2CR** [P370]・Pritchett の不一致指標 [P372] |
| GR-C1「委譲は双方向」 | **確定（制御権限については既出）** | change authority [P370]・adjustable autonomy [P374] |
| 残る差分 | **判定不能（今回の範囲で見つからず）** | ★ 次の 3 点の**組み合わせ**: (a) 返すのが**認識的権限**（意味の認定・評価・報酬）、(b) 負担台帳に**解釈と説明要求**が入る、(c) **権限と責任が一致したまま**返還しても残務が移る型（★ A2CR の整合規則では不整合として検出されない）。＋ (d) 系が**価値判断で任意に**返す局面（[P375] が射程外と明記） |

★ **判定**: 草案の新規性の核は**縮小**。⚠️ **「返権の負荷逆説」「二重台帳」「GR-C1」を単独で新規と書けない**。★ 書けるのは「既存の double-bind / A2CR を**認識的権限の任意の返還**へ拡張し、**一致したまま移る残務**を記述する」まで（⚠️ 体系的レビュー前に「先行が無い」とは書かない）。→ ★ **研究者判断 J-1 / J-2 を再度伺う**（判断 1 の見直し条件に該当）。

---

### カード 1: 「権限だけ返して負担を残す」の一般形は 1985 年に名指されている **[検証済 3-0]** [P369] [P368] [P371]

1. **どんなもの?** 人間-機械の協調認知系の設計論（Woods）・自動化の皮肉（Bainbridge）・moral crumple zone（Elish）。
2. **先行研究と比べてどこがすごい?** ★ Woods は、人が**名目上の上書き権限**と**結果責任**を持ちながら、機械の出力を濾過する**支援のない仕事**を負う配置を **double-bind** と名付けた。
3. **技術や手法の肝は?** 逐語 *"it is the human problem solver who has responsibility for the outcome. Of course, the person has in principle the authority to override the machine"*・*"there is great danger of a responsibility/authority double-bind"*（[P369] p.88）・*"the potentially difficult and unsupported task of filtering poor machine solutions"*（[P369] p.86）。Bainbridge: *"little thought may have been given to providing support for them"*（[P368] p.775）。Elish: *"While control has been effectively distributed, responsibility has not scaled accordingly."*（[P371] p.49）。
4. **どうやって有効だと検証した?** 概念論文と事例分析（航空・自動運転）。
5. **議論はあるか?** ⚠️ **起点が違う**: 既存は「自動化が人の仕事を *取る*」か「系が *破綻* して人へ戻る」局面（[P371] p.47 の Alternate Law）。★ 草案は「系が意味づけの権限を**設計価値として自ら手放す**」局面を扱う —— ★ この差分は**今回の範囲で見つからなかった**（ゼロ ≠ 非存在）。
6. **次に読むべき論文は?** Woods & Cook (2002)・Dekker (2002)（Flemisch が double bind の出典に挙げる・未取得）／ Davies (2024) *accountability sink*（未取得）／ privacy self-management の「自律を名目に負担を個人へ移す」系譜（Solove 2013・未確認）

### カード 2: 権限と責任を別台帳で記述する枠組み（A2CR）は既にある —— 二重台帳の「形式」の先行 **[検証済 3-0]** [P370] [P372]

1. **どんなもの?** 共有・協調制御の設計枠組み（A2CR: ability / authority / control / responsibility）と、その計量。
2. **先行研究と比べてどこがすごい?** ★ 4 概念を**主体ごとに別々に**記入し、整合規則を置く。
3. **技術や手法の肝は?** 逐語 *"Ability should not be smaller than authority; authority should not be smaller than responsibility."*（[P370] p.7）・*"(Control) Change authority: This is the authority to change the control authority to another control distribution giving more or less control to one of the actors."*（[P370] p.6）。★ 不整合の名指し: *"An extreme would be an automation that does the control task completely, but where the human would keep all the responsibility."*（p.11）・*"leave the human with low abilities, low authority and insufficient control, but still with the full responsibility"*（p.17）。★ 計量: *"Several problems can intrinsically arise when the responsibility and authority are not assigned to the same agent, including the additional monitoring actions the responsible agent must perform."*（[P372] p.59）。
4. **どうやって有効だと検証した?** 自動運転の事例（HAVEit）と機能配分の指標論。
5. **議論はあるか?** ★ **残る差分（★ サブエージェントの分析をメインが一次で確認した範囲）**: (a) A2CR の authority は**制御**であり、草案の**意味の認定・評価・報酬**ではない。(b) A2CR の responsibility は**帰責**であり、草案の負担台帳の**解釈・説明要求**を持たない。(c) ⚠️★★★ 草案の配置は**権限と責任が両方とも利用者側**にあるので A2CR の「authority ≥ responsibility」に**違反しない** —— ★ **A2CR で捉えられるのは ability < authority の不整合だけ**。→ 草案が新規性を主張するなら「**一致したまま移る残務**」が A2CR の「能力不足」に縮約されないことを示さなければならない。
6. **次に読むべき論文は?** Flemisch et al. (2019, CTW 21(4))・Pritchett らの対論文（10.1177/1555343413490944・未登録）

### カード 3: 「委譲は双方向」は制御権限については既出 —— 差分は「認識的権限の *任意の* 返還」 **[検証済 3-0 / 2-1]** [P374] [P375] [P370]

1. **どんなもの?** adjustable autonomy と自動運転の遷移研究。
2. **先行研究と比べてどこがすごい?** ★ adjustable autonomy は**系が自ら自律を下げて人へ返す**ことを定義に含む: 逐語 *"entities dynamically varying their own autonomy, transferring decision-making control to other entities (typically agents transferring control to human users)"*（[P374] p.171）。
3. **技術や手法の肝は?** 返還のコスト（割り込み・人が決められない可能性）を期待効用で扱う（[P374]・[P42]）。
4. **どうやって有効だと検証した?** 実装（Electric Elves）と遷移の分類。
5. **議論はあるか?** ★ **草案に有利な逐語**: 逐語 *"automation-initiated transitions can only be mandatory"*（[P375] §3.1）＝ **自動化側からの *任意の* 返還は既存の遷移研究の射程外**。→ ★ GR-C1 は「既存の双方向性を**認識的権限の任意の返還**へ拡張する」と書くのが安全（⚠️ 例外: 状況認識を回復させるための適応的自動化・[P375] §3.2.3）。⚠️ ただし「認識的権限」に最も近い既存の段は、自動化の 4 段階のうちの **information analysis**（[P373]・⚠️ メイン未照合）であり、外界の分析の自動化として既に扱われている —— 草案の「本人の作業の意味の認定・評価・報酬」との違いを定義に書き込む必要がある。
6. **次に読むべき論文は?** Parasuraman, Mouloua & Molloy (1996)（自動化した課題を監視能力のために人へ戻す・abstract のみ）／ Inagaki (2003) "Automation and the cost of authority"（未取得）

### カード 4: 検証負担の移転と説明責任の移転 —— 負担台帳の項目の対応物 **[検証済 3-0 / 2-1]** [P376] [P378] [P379] [P377]

1. **どんなもの?** 生成 AI の皮肉・人間の監督政策の批判・責任の空白の分類。
2. **先行研究と比べてどこがすごい?** 負担台帳の項目のうち**検証**と**説明**に既存の対応物がある。
3. **技術や手法の肝は?** 検証: *"users' roles have shifted from producing output to evaluating it"*（[P376] p.2）。説明責任の移転: *"shift accountability for algorithmic harms from agency leaders … to frontline human operators (who are relatively powerless)"*（[P378] p.9）。説明要求: public accountability = *"an obligation to explain and to justify his or her conduct"*（[P379] p.1063・Bovens の定義）。★ 対照 —— 負担が**空白**になる型: *"In situations where the operator has reduced control over the machine he also bears less or no responsibility."*（[P377] p.176）。
4. **どうやって有効だと検証した?** 概念・政策分析。⚠️ **効果の出典には使えない**。
5. **議論はあるか?** ⚠️ [P376] は系が制作を控える（問いかけで返す）ことを**緩和策**として扱い、その**失敗様式**（＝ 草案の負荷逆説）は論じていない → ★ 草案の差分候補（今回の範囲で）。
6. **次に読むべき論文は?** 社会学の responsibilization（自律を名目に負担を個人へ移す）

---

## 否決リスト（★ カード本体に書かない）

| # | 主張 | 票 | 否決理由 |
|---|---|---|---|
| 1 | 「返権の負荷逆説は先行研究の無い新しい現象である」 | **0-3** | 一般形は Woods の double-bind [P369]・Elish [P371]・Bainbridge [P368] が既に記述 |
| 2 | 「権限・負担の二重台帳は新しい分析枠組みである」 | **0-3** | 形式は A2CR [P370]・Pritchett の不一致指標 [P372] が既出 |
| 3 | 「GR-C1（委譲は双方向）は新しい命題である」 | **0-3** | 制御権限については change authority [P370]・adjustable autonomy [P374] が既出 |
| 4 | 「"liability sponge" は査読文献に出典のある確立した語である」 | **1-2** | Elish p.41 は引用符つきで出典表示なし。査読文献での出典は今回見つからず（ブログ類のみ） |

## GSE への還元（★ pre-SSOT の理論草案への還元）

- ★ **`review-B.md` B-23 / B-24 / B-26 / B-32 の判定を更新**: 「要サーヴェイ」→ **縮小**（先行を明示的に引き、差分を (a)〜(d) の組み合わせに限定）。
- ★ **研究者判断を再度仰ぐ**（判断 1 の見直し条件に該当）: 「返権の負荷逆説」を独自の語として残すか、Woods の **responsibility/authority double-bind** を先行として引いてその下位型と位置づけるか（J-2 の名称ゲートと一緒に）。
- ⚠️ `research-positioning.md` への還元は **段 3 へ送る**（★ そもそも RP は理論を主張に含めていない —— 研究者判断 1 #1）。

## やり残し

- ⚠️ **「認識的権限の任意の返還」「一致したまま移る残務」「解釈・説明要求を含む負担台帳」はいずれも今回の範囲で 0 件** —— 体系的レビュー（検索式・DB・採否基準を固定）の前に「先行が無い」とは書かない
- 未取得: Woods & Cook 2002・Dekker 2002・Inagaki 2003・Davies 2024・Miller & Parasuraman 2007・Solove 2013（privacy self-management）・社会学の responsibilization
- 脅威になりうる系譜（未検証）: privacy self-management / notice-and-choice（「選択を返す」ことで負担を個人に移す）
