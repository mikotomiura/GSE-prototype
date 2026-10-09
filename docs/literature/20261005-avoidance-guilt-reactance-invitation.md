# 自分の状態の表示を避ける・誘いを無視して後ろめたい・促しに反発する —— 肖像と招待の制約のための小さなサーヴェイ（S-PI）

> 2026-10-05 / `/literature-review` 1 ラウンド（S-PI）/ **設計根拠の補強**（gate 判定ではない）
> 対象: `.steering/20261005-portrait-invitation-constraints/`（肖像と招待の設計制約の台帳と決定）
> 名前空間: `P`（新規 [P454]–[P467]）。既登録の再利用: [V75] [V115] [V116] [P260] [P77] [P380]。

## 動機（★ なぜこのラウンドを回したか）

研究者は 2026-10-05 に、肖像（作業をワクワクさせる面）と招待（停滞に近いときの身体回帰への誘い）を分けると決めた（`decisions.md` 判断 1）。そのとき研究者が挙げた心理的な懸念のうち 3 つは、repo に一次が無かった。

1. 招待や状態の表現が固定的なラベルで決まっていると、自分の状態を突き付けられ、「見たくない」と避けるのではないか（**情報回避**）。⚠️ `references.md` に ostrich・information avoidance の一次は 0 本だった。
2. 招待を無視したときに罪悪感が残り、受け入れられないのではないか（**無視の罪悪感**）。既存の証拠は、記録をやめた後の罪悪感（[V75]・活動 16.2%・お金 8.9%）だけだった。
3. 促されること自体に反発するのではないか（**促しへの反発**）。尺度 [V115] [V116] と、自律支援的な言い回しが効かなかった 1 本 [P260] はあったが、出し方との関係の一次が足りなかった。

★ 既存カードとの関係: 「ラベルと抽象表現の受け入れ」は可読性のカード（`20260906-legibility-demotion-and-ambient-behavioral-evidence.md`）と重なるので外した（判断 2）。物体の必要性は既存の材料（`20260815-portable-ambient-object-and-activity-coupling.md`）から論点を立てる（判断 3）ので、本ラウンドの angle に入れていない。

★ 下位問い（`design.md` の 3 angle をそれぞれ 3 つに割った）:
- **A1 情報回避**: A1a 現象（自己の情報の回避は実在し、どれくらいか）／ A1b 形（数値・ラベル・比較・負の値・統制で回避が変わるか）／ A1c 反証（見ることは達成を高める・回避は小さい）
- **A2 無視の罪悪感**: A2a 現象（促し・通知・目標を無視・不履行にしたときの罪悪感）／ A2b 帰結と形（罪悪感は離脱につながるか・出し方で変わるか）／ A2c 反証（罪悪感は小さい・行動を変えない・むしろ促す）
- **A3 促しへの反発**: A3a 言い方（統制的な言葉 ⇄ 自律を支える言葉）／ A3b 頻度・統制・理由（頻度・本人の統制・理由の提示）／ A3c 反証（反発は小さい・出し方で変わらない）

## 検証状態

- **探索**: サブエージェント 3 本（Sonnet・angle ごと・入れ子禁止・締切 20 分）。実際の所要は **A1 4.0 分・A2 2.9 分・A3 2.7 分**だった。⚠️ **網は粗い**。以下の「0 件」は、すべて **S-PI の範囲で見つからなかった**の意味であり、研究が存在しないという主張ではない。生の出力は scratchpad（`spi/A1–A3.md`・版管理外）。
- **探索の範囲**（2026-10-05・有料の DB と本文は使っていない・学術 API にメールアドレスを送っていない）:
  - A1: OpenAlex の検索（people avoid feedback on relative performance information avoidance experiment ／ self-weighing feedback avoid weight scale experiment negative feedback ／ fitness tracker users stop looking at data avoidance negative emotion ／ Information Avoidance Scale Howell Shepperd）＋ 出発点の文献の DOI 照会
  - A2: Europe PMC と OpenAlex の検索（computer prompts sedentary office workers acceptability annoying ／ point-of-choice prompts sitting time work Evans ほか）。⚠️ **通知の dismiss・snooze と罪悪感の語では検索していない**
  - A3: Europe PMC（reactance AND (notification OR reminder OR prompt OR just-in-time) ／ psychological reactance AND (push notification OR text message OR recommender OR mobile app)）＋ Web 検索（reactance persuasive technology notifications frequency autonomy control mHealth）。⚠️ **ナッジの受容の調査研究は検索していない**
- **取得ソース**: 約 20 件。本ラウンドで新規に登録したのは 14 件（★ 全文で照合 10 件 ／ 抄録だけ 4 件）。
- **claim**: 台帳 19 件 ＋ 検証の途中で立てて落とした一般化 4 件（否決リスト N2–N5）＝ 23 件
  - 台帳 19 件の内訳: **confirmed 12**（3-0 が 1 ／ 2-1 が 11。温度は 確定 11 ・ PLAUSIBLE BUT UNPROVEN 1）／ **否決 1**（#10 → N1）／ **判定不能 6**
- ★ **メインが一次で逐語を照合した**: サブエージェントが保存した原本は使わず、**メインが取り直した原本**（Europe PMC の全文 XML 7 本・PDF 4 本・Crossref の抄録 5 本）で、報告の逐語 24 か所（登録しなかった 1 本を含む）を正規化してから照合した。**24 か所すべて原本にあった**（[P460] は著者原稿の行番号が文に挟まって素の一致を壊していただけで、目で確かめた）。数値はすべて原本の文脈で読み直した。
- ★ 書誌（著者・巻号頁・DOI）は、14 件すべてを Crossref の API で確かめた。
- ⚠️ **サブエージェントの報告の誤りを 3 つ直した**:
  1. [P462] の著者を報告は 3 人（Cooley・Pedersen・Mainsbridge）と書いたが、**Crossref と全文 XML の著者は Cooley と Pedersen の 2 人**だった。
  2. [P465] の N を報告は 526 と書いたが、526 は**募集した数**で、**分析した標本は 525**（Table 1）。
  3. [P462] で報告が「passive prompt」と書いたのは、**本文の定義では「無視できない（強制的な）促し」**である（逐語は カード 3 §5・否決 N1）。字面で「受動的な表示」と読むと意味が反転する。

### claim 台帳

| # | claim | 出典 | 票 | 温度 |
|---|---|---|---|---|
| 1 | 自分の進み具合・不都合な情報を、役に立つ場合でも見ない・避ける現象を、総説 2 本が複数の領域にわたって報告している | [P454] [P455] | **2-1** | 確定（留保: 総説・抄録だけ・対象は自分から見に行く情報） |
| 2 | 銀行口座が赤字になるとログインが減り、ログインは負債と負の相関を示した（家計アプリの観察パネル） | [P456] | **2-1** | 確定（留保: 観察・ワーキングペーパー・恐れと用事の有無の分離は不完全） |
| 3 | 進み具合を確かめる機会を実際に断ることを予測した信念は「情報が不正確」「役に立たない」「統制できている」で、「目標が否定的な感情と結びつく」は予測しなかった。ただし否定的な感情は、体重を量る頻度の低さを予測した | [P457] | **2-1** | 確定（留保: 減量の 1 文脈・自己申告の信念・断ることの説明率は小さい Nagelkerke R² = .06） |
| 4 | 自分の状態の表示の形（数値・固定的なラベル・他者との比較・抽象表現）を操作して回避を測った実験 | — | — | **判定不能（S-PI の範囲で 0 件）** |
| 5 | 進み具合の監視を促す介入は、監視の頻度を大きく上げ（d+ = 1.98）、目標の達成を上げた（d+ = 0.40・k = 138）。記録すると効果が大きく、基準値の種類（過去・目標）と監視の受動・能動では差が出なかった | [P458] | **2-1** | 確定（留保: 監視を**促した**介入の効果で、受動的な表示を自発的に見るかではない・著者原稿で照合） |
| 6 | 画面の端の受動的な表示で、自分の状態の情報の回避が起きるかを測った研究 | — | — | **判定不能（S-PI の範囲で 0 件）** |
| 7 | 食事・運動のアプリで、目標の超過と否定的な表示（赤い可視化）に対して、罪悪感・恥・きまり悪さが報告された | [P459] | **2-1** | 確定（留保: 摂食障害のある大学生の女性 N = 24・質的・引き金は無視ではなく目標の超過） |
| 8 | 罪悪感などの否定的な感情を避けるために記録アプリを使わなくなった、という投稿がある（目標を 1 kcal 超えたとき・達成したときでも）。通知で裁かれていると感じた投稿もある | [P460] | **2-1** | 確定（留保: 摂食障害の掲示板・自己選択の投稿・割合は無い） |
| 9 | 職場の PC の画面上の促しは「簡単に無視される・気づかれない」と予想され、予告なしの画面ロックには苛立つ人がいるだろうと語られた。全文に罪悪感の語は無い | [P461] | **2-1** | 確定（留保: 使った経験ではなく仮定への意見・罪悪感を問うていない） |
| 10 | 無視できない強制的な促しの期間は、任意で起動する期間より、毎時の休憩を完遂する確率が 5 倍高かった | [P462] | **1-2** | **否決 → N1** |
| 11 | 予期された感情（後悔・罪悪感を含む）は、行動の意図と強く相関する（r = .61・k = 67・N = 25,652）。異質性が大きく、快楽的な行動で相関が高い | [P463] | **2-1** | 確定（留保: 相関・結果は意図で行動ではない・罪悪感だけの値ではない） |
| 12 | 促し・通知・招待を無視したときの罪悪感を測った研究（職場の座りすぎ中断を含む） | — | — | **判定不能（S-PI の範囲で 0 件・ただし dismiss・snooze × 罪悪感の語では検索していない）** |
| 13 | 応答を対称に扱う設計（どの応答にも正誤を付けない）で、無視の罪悪感が残るかを測った研究 | — | — | **判定不能（S-PI の範囲で 0 件）** |
| 14 | 自由を脅かす強い言葉は、弱い言葉より、反発（r = .20・k = 53）・怒り（.21）・否定的な認知（.17）を上げた。行動の反復性と伝達様式で調整された。損得のフレーミングでは差が無かった | [P464] | **3-0** | 確定（留保: 抄録だけ・調整の向きは未読・健康メッセージが中心） |
| 15 | 自律支援的な言葉と統制的な言葉で、知覚された自律支援・関連性・全体の評価のどれにも有意な差が無かった。選択を示すと全体の評価が少し上がった（b = .12） | [P465] | **2-1** | 確定（留保: 介入直後の知覚だけ・反発そのものは測っていない） |
| 16 | 自律支援的な言葉は身体活動を増やす意図を**下げた**。選択の効果は無かった。自律の欲求が高い人では、自律支援的な言葉が認知的な反発を下げた | [P466] | **2-1** | PLAUSIBLE BUT UNPROVEN（**抄録だけ**・1 時点の測定（著者は cross-sectional と書く）・意図で行動ではない・[P465] と選択の効果が食い違う） |
| 17 | AI の判断に「なぜ」の説明を付けても、知覚された自律（B = 0.04, p = .092）にも反発（B = 0.01, p = .72）にも、全体では主効果を検出しなかった。場面の差の方が大きかった（SNS で反発が高く、ナビで低い） | [P467] | **2-1** | 確定（**主効果を検出しなかった**という報告として。⚠️ 説明に効果が無いことの証明ではない・同等性の検定は無い。留保: デザインフィクションの想定場面・実使用ではない） |
| 18 | 本人が時期・有無を統制できる促しと、できない促しで、反発を比べた実験 | — | — | **判定不能（S-PI の範囲で 0 件）** |
| 19 | 促しの頻度・反復と反発を直接比べた研究（[P464] の「行動の反復性」は促される行動の性質であって、促しの頻度ではない） | — | — | **判定不能（S-PI の範囲で 0 件）** |

票の 3 つの視点は、内的妥当性 ／ 外挿（GSE の場面 = PC での知識作業・肖像は状態を表さない・招待は小さな PC の要素で応答に正誤を付けない）／ 効果量の頑健性（標本・再現・p の余裕・抄録だけか）である。

★ 温度の凡例: **確定** = 直接証拠あり ／ **PLAUSIBLE BUT UNPROVEN** = 継ぎ接ぎでしか言えない ／ **判定不能** = 今回の探索の範囲で該当ゼロ ／ **未決**（本カードの用法）= 該当はあるが、どちらの向きの一般化も確定できない（否決リストに載せたのが片側だけのときは、その側を明記する）

## gate 判定（要点先出し）

| 下位問い | 温度 | 一言 |
|---|---|---|
| A1a 自己の情報の回避は実在するか | **確定（自分から見に行く情報について）** | 総説 2 本 [P454] [P455]・口座が赤字になるとログインが減る（観察）[P456] |
| A1b 表示の形で回避が変わるか | **判定不能（S-PI の範囲で 0 件）** | 隣接: 断ることを予測したのは「否定的な感情」より「役に立たない・不正確」の信念だった（1 研究）[P457] |
| A1c 反証: 見ることは達成を高めるか | **確定（促された監視について）** | d+ = 0.40・k = 138。基準値の種類と受動・能動では差が出なかった [P458] |
| A2a 無視の罪悪感はあるか | 目標の超過と否定的な表示への罪悪感 = **確定**（臨床の集団・質的）／ 促しを無視したときの罪悪感 = **判定不能（S-PI の範囲で 0 件）** | [P459] [P460]。職場の PC の促しは「無視される」と予想され、罪悪感の語は出なかった [P461] |
| A2b 罪悪感は離脱につながるか・出し方で変わるか | 罪悪感を避けるための不使用 = **確定**（質的・割合なし）／ 出し方 = **判定不能** | [P460]。既登録の [V75]（やめた後の罪悪感）と同じ向き |
| A2c 反証: 罪悪感は小さい・むしろ促す | **判定不能（直接の証拠は S-PI の範囲で 0 件）** | 隣接: 予期された罪悪感・後悔は意図と強く相関する（相関・意図）[P463]。「罪悪感が行動を促す」は否決（N4）。「無害」とも「必ず離脱させる」とも言えない |
| A3a 言い方 | 統制的な強い言葉は反発を上げる = **確定**（メタ分析・抄録）／ 自律支援的に言い換えれば反発が減る = **支持されない**（否決 N2。反発の成分（怒り・反論）を測った [P260] は有意差なし。[P466] で反発が下がったのは自律の欲求が高い人に限る。⚠️ [P465] は反発を測っていない —— 知覚された自律支援・関連性・全体の評価で有意差なし）／ 言い換えが逆効果 = **PLAUSIBLE BUT UNPROVEN**（[P466]・抄録だけ・結果は意図） | [P464] ／ [P260] [P466] ／ [P465] |
| A3b 頻度・統制・理由 | 理由の提示で反発が減る = **支持されない**（否決 N5。1 研究・想定場面で主効果を検出しなかった。⚠️ 効果が無いことも示されていない）／ 時期の統制・頻度 = **判定不能（S-PI の範囲で 0 件）** | [P467] |
| A3c 反証 | A3a・A3b の null 群がそのまま反証側 | — |

---

### カード 1: 不都合な自己の情報は避けられる —— ただし実際に断ることを予測したのは、感情より「役に立たない・不正確」の信念だった **[検証済 2-1]** [P454] [P455] [P456] [P457]

1. **どんなもの?**:
   - [P454] は目標の進み具合の監視を避ける「ostrich problem」の総説（Webb, Chang & Benn 2013）。[P455] は情報回避の経済学・心理学の総説（Golman, Hagmann & Loewenstein 2017）。どちらも**抄録だけ**。
   - [P456] はアイスランドの家計アプリ（利用者 52,545 人）のログインと口座の日次パネル（Olafsson & Pagel・NBER WP 23945・2017 年・2023 年改訂）。
   - [P457] は目標の進み具合を確かめない理由の質問紙 2 本（Chang, Webb & Benn 2017）。Study 1 は N = 288。Study 2 は減量中の人に「進み具合の計算機」を使う機会を出し、断るかを先に測った信念で予測した（分析の自由度から N = 632・募集は 832）。
2. **先行研究と比べてどこがすごい?**: [P457] は、回避の理由を自己申告で集めるだけでなく、**実際に断るかどうか**を予測する形で確かめた。
3. **技術や手法の肝はどこ?**: [P456] は、取引の機能が無い閲覧専用のソフトで、注意（ログイン）を行動から切り離して測った。
4. **どうやって有効だと検証した?**（★ メインが原本で照合）:
   - [P454] 抄録 *"in many instances, people have a tendency to "bury their head in the sand" and intentionally avoid or reject information that would help them to monitor their goal progress."*
   - [P455] 抄録 *"This can create an incentive to avoid information, even when it is useful, free, and independent of strategic considerations."*
   - [P456] 本文 *"when individuals have larger overdrafts they are less likely to log in"*・*"when current accounts go into the red, individuals log in less"*。⚠️ 同じ箇所の脚注 21 は、図の第 1 と第 10 十分位の差は有意でないと書く（回帰では有意）。
   - [P457] Study 2: 計算機を断ることを予測したのは、不正確（*"B = 0.20, S.E. = 0.09 … p = 0.04"*）・役に立たない（*"B = 0.29, S.E. = 0.10 … p = 0.01"*）・統制できている（Factor 10「統制できない」が B = −0.23, p = .009）。Table 6 で「目標が否定的な感情と結びつく」は断ることに 0.08（SE 0.08）で有意でなく、体重を量る頻度の低さには 0.14**。考察の逐語 *"The extent to which the goal was associated with negative emotions predicted the frequency with which participants weighed themselves in order to monitor their progress."*
5. **議論はあるか?**:
   - ⚠️ 4 本とも、対象は**本人が自分から見に行く情報**（ログイン・計算機・体重計）である。画面の端に出る受動的な表示で回避が起きるかは、S-PI の範囲で 0 件（claim 6）。
   - ⚠️ [P456] は観察で、悪い時期に「見る用事が減る」のか「見るのが怖い」のかを分けきれていない（著者は ostrich 効果の側で解釈する）。ワーキングペーパーで、査読誌の版は未確認。
   - ⚠️ [P457] の断ることの説明率は小さい（Nagelkerke R² = .06）。減量の 1 文脈・大学のボランティア。
   - ★ **GSE への含み**:
     - 肖像は状態を表すことを意図しない（判断 1・5）。形に状態の情報が残らなければ、回避の機序が当たる「自己の状態の情報」を肖像は運ばない。⚠️ ただし形の材料（F 系列）は状態の情報を含みうるので、それは**未検証の設計目標**であり、EH1 で検査する（`decisions.md` 判断 8 E1-3）。回避の機序が当たるのは、肖像が状態計として読まれた場合である（台帳 T1）。
     - 招待に状態のラベル（「停滞しています」）を付けると、招待は「進み具合の情報」になり、回避の機序の対象になりうる（外挿）。
     - [P457] で断ることを予測したのは「不正確・役に立たない」の信念だった。GSE の推定は較正の途中で、ラベルを付ければ正確さが問われる。既登録の [V75] の放棄の理由 4（データ品質の懸念）と同じ向きである（外挿）。
6. **次に読むべき論文は?**: Sweeny, Melnyk, Miller & Shepperd 2010（情報回避の総説・抄録だけ見た）／ Howell & Shepperd 2016（情報回避の尺度・未取得）／ Karlsson, Loewenstein & Seppi 2009（未読）。
- **やり残し**: 表示の形（数値・ラベル・比較・抽象）を操作して回避を測った実験は、S-PI の範囲で 0 件。

### カード 2: 監視を促すと達成は上がる —— 回避の反証側。基準値の種類と受動・能動の監視では差が出なかった **[検証済 2-1]** [P458]

1. **どんなもの?**: [P458] は、進み具合の監視を促す介入の実験のメタ分析（Harkin et al. 2016・138 研究）。
2. **先行研究と比べてどこがすごい?**: 監視の頻度と目標の達成の両方を、実験の比較だけでまとめた。
3. **技術や手法の肝はどこ?**: 監視の頻度の変化が達成への効果を媒介するかを検定し、監視の形（記録・基準値・受動か能動か）を調整変数にした。
4. **どうやって有効だと検証した?**（★ メインが著者原稿で照合）:
   - 抄録 *"interventions were successful at increasing the frequency of monitoring goal progress (d+ = 1.98, 95% CI: 1.71 to 2.24) and promoted goal attainment (d+ = 0.40, 95% CI: 0.32 to 0.48)"*（達成は k = 138・N = 18,398、頻度は N = 19,951）
   - 記録: *"Physically recording the information derived from monitoring led to larger effects on goal attainment (d+ = 0.43) compared to not recording this information (d+ = 0.29), Q(1) = 12.71, p < .001"*
   - 形: *"Comparing the current state to a desired (future) target had comparable effects on goal attainment (d+ = 0.41) as comparing the current state to a reference value in the past (d+ = 0.43), Q(1) = 0.14, p = 0.71. Finally, whether participants monitored their rate of goal progress or distance from the goal, or used passive versus active forms of monitoring, did not influence the impact of monitoring on goal attainment"*
   - 著者は、介入が監視をこれほど増やした理由として回避を挙げる: *"One answer may be 'the ostrich problem', or peoples' motivated avoidance of information concerning goal progress (Webb et al., 2013)."*
5. **議論はあるか?**:
   - ⚠️ 効果は**監視を促した**結果であり、受動的な表示を自発的に見るかではない。回避しやすい人が見たときの気分・離脱は測っていない。
   - ⚠️ 照合したのは機関リポジトリの著者原稿で、出版版との数値の差は未確認。
   - ⚠️ 本ラウンドの問いに対しては「見せた方がよい」側の反証だが、**GSE は目標の達成を主張しない**（ADR-018 D1・機会保存）。かつ「量を追えるようにすると活動そのものが痩せる」[P77] の機序は、達成の効果と同居しうる（[P77] は量が増え楽しさが下がった）。→ [P458] は「見せないことに代償がある」とは言えるが、「見せるべき」とは言えない。
   - ★ **GSE への含み**: 「状態を見せると避けられる」を設計の前提にしすぎない。肖像に状態を載せない理由は、回避ではなく ADR-025 の機序（[P77]）と判断 1（突き付け・罪悪感）である。
6. **次に読むべき論文は?**: [P458] の領域別・測定の種類別の調整変数（未読）。
- **やり残し**: 監視を促さずに常時表示した条件での回避と離脱。

### カード 3: 罪悪感は「記録された目標の超過と否定的な表示」で報告され、罪悪感を避けるための不使用もある —— 促しを無視したときの罪悪感は見つからなかった **[検証済 2-1]** [P459] [P460] [P461] [P463]

1. **どんなもの?**:
   - [P459] は摂食障害のある大学生の女性 24 人の、食事・運動のアプリの体験の質的研究（Eikey 2021・調査・think-aloud・半構造化面接）。
   - [P460] は摂食障害の掲示板 3 つの MyFitnessPal に関するコメント 1,695 件（投稿者 920 人）の質的分析（McCaig et al. 2020）。
   - [P461] は英国のデスクワーカー 25 人の、座りすぎを中断する妨げと助けの面接（Ojo et al. 2019）。
   - [P463] は予期された感情と行動の意図のメタ分析（Chitraranjan & Botenne 2024・k = 67・N = 25,652）。
2. **先行研究と比べてどこがすごい?**: [P460] は掲示板という自然な場の語りで、罪悪感を**避けるために使わなくなる**という離脱の経路を記録した。
3. **技術や手法の肝はどこ?**: [P461] は TDF と COM-B の枠で、職場の PC の促し（画面上の通知）への見方を引き出した。
4. **どうやって有効だと検証した?**（★ メインが原本で照合）:
   - [P459] 表のテーマ *"Feeling extreme negative emotions, such as guilt, embarrassment and shame, especially when exceeding one's calorie or nutrient budget or gaining weight; often occurs when receiving negative feedback on the app, such as via red visualisations"*。本文 *"participants felt guilt, embarrassment and shame over exceeding their calorie budget and being shown red visualisations in response."*
   - [P460] *"some commenters reported not using MyFitnessPal to avoid negative feelings associated with its use (e.g., 'stress', 'worried', 'guilt'), which they described experiencing when they violated their goal by as little as one calorie, or even when they achieved their goal. Others also felt judged by MyFitnessPal's standard functionality, such as notifications of consuming too much of a specific nutrient (e.g., fat)."*（同じ節で、アプリは「accountable」と感じさせ動機づけた、とも書く）
   - [P461] *"some participants believed computer on-screen prompts can easily be ignored or go unnoticed, especially when the users are in a meeting or working away from their desks and computers."*・*"It was also perceived that older employees might be irritated seeing their screens locked automatically without warning."*。⚠️ 全文に guilt の語は 0 件。
   - [P463] 抄録 *"a strong correlation between anticipated affect and behavioral intention ( r = .61,95 % C I = [.57,.64], p < .0001, k = 67, N = 25652)"*。本文で予期された感情は *"self-conscious negative emotions (e.g., regret, guilt) expected to be experienced later as a consequence of not engaging in the behavior"* に焦点がある。
5. **議論はあるか?**:
   - ⚠️ 罪悪感の一次は**臨床の集団**（摂食障害）に集中しており、引き金は「無視」ではなく**記録された目標の超過と否定的な表示**である。職場の PC の促しへの外挿は弱い。
   - ⚠️ [P461] は使った経験ではなく、仮定への意見である。罪悪感を問う質問も無い。
   - ⚠️ [P463] は相関で、結果は意図である。予期された罪悪感が行動を促すとは言えない（否決 N4）。
   - ★ **GSE への含み**（いずれも外挿）:
     - 文献で罪悪感の引き金になっていたのは、**目標・記録・否定的な表示（赤）・通知での指摘**の組である。GSE の招待はこれらを既に持たない（目標を設定させない ADR-035 D5・量を返さない ADR-026 D4 / ADR-035 D6・解除に理由を載せない ADR-027 D4・応答を成功に数えない ADR-033）。→ **引き金の組は外されている。それでも罪悪感が残るかは、S-PI の範囲で研究が無い**（claim 12・13）。
     - したがって無視の罪悪感は、**文献で決めず、EH3 で測る**（理論 GR-H9 が測る結果に罪悪感を置いている）。
     - 無視した後に招待が残り続けると、「指摘され続ける」表示になりうる（[P460] の「通知で裁かれている」に近い）。台帳 T4（`PS-Q10` ②）と同じ論点。
6. **次に読むべき論文は?**: Eikey & Reddy 2017（CHI・カロリー記録と摂食障害）／ Kersten-van Dijk et al. 2017（personal informatics のレビュー・取得できず）／ Pedersen et al. 2014（PC の促しの介入・取得できず）／ 通知の dismiss・snooze と感情の研究（未検索）。
- **やり残し**: 促し・招待を無視したときの罪悪感を測った研究は、S-PI の範囲で 0 件（dismiss・snooze の語では未検索）。

### カード 4: 統制的な強い言葉は反発を上げる —— 自律支援的な言い換え・理由の説明・選択の提示の効果は割れる **[検証済 3-0 / 2-1]** [P464] [P465] [P466] [P467]

1. **どんなもの?**:
   - [P464] はメッセージの特徴と心理的リアクタンスのメタ分析（Li & Shi 2025・28 論文・33 研究・146 効果量・2005–2024）。**抄録だけ**。
   - [P465] は自律支援的な言葉 × 選択の 2×2 のオンライン実験（Smit et al. 2019・N = 525・野菜の摂取の介入文）。
   - [P466] は同じ 2×2 を身体活動の促しで行った実験（Solovei, Daal & Smit 2024・N = 218）。**抄録だけ**。
   - [P467] は日常の AI の判断への自律と反発の知覚の調査（Sankaran et al. 2021・N = 328・デザインフィクション・説明の有無 × AI であることの周知の有無）。
2. **先行研究と比べてどこがすごい?**: [P464] は「言葉の強さ」と「損得のフレーミング」を分けて、反発への効果をまとめた。
3. **技術や手法の肝はどこ?**: [P467] は、ナビ・SNS・サーモスタット・フィットネスの推薦など 8 場面で、説明の効果と場面の効果を分けた。
4. **どうやって有効だと検証した?**（★ メインが原本で照合）:
   - [P464] 抄録 *"high freedom-threatening language increased anger (k = 28, r = .21), negative cognitions (k = 25, r = .17), and psychological reactance (k = 53, r = .20) compared to low freedom-threatening language. These effects were moderated by behavior repetitiveness and communication modality. However, gain vs. loss framing showed no significant differences in anger (k = 6, r = –.03), negative cognitions (k = 6, r = –.01), or psychological reactance (k = 12, r = –.02)."*
   - [P465] 抄録 *"Choice had a significant positive effect on the overall evaluation of the intervention (b=.12; P=.003)"*・*"No significant effects on any of the three outcomes were observed for language."*
   - [P466] 抄録 *"Results revealed no effects of choice, however, autonomy-supportive language had a negative effect on the intention to increase physical activity."*・*"when individuals with a higher (vs. lower) need for autonomy were exposed to autonomy-supportive language, this led to a stronger decrease of cognitive reactance."*
   - [P467] 結果 知覚された自律: *"no main effect of explanation ( B = 0.04, 95% CI = [−0.01, 0.09], p = 0.092)"*。反発: *"no main effect of explanation ( B = 0.01, 95% CI = [−0.05, 0.07], p = 0.72)"*。場面: *"participants showed significantly higher reactance when receiving social media filters ( B = 0.27, 95% CI = [0.20, 0.33], p < 0.001), but significantly lower reactance when receiving navigation advices ( B = −0.26, 95% CI = [−0.33, −0.20], p < 0.001)"*
5. **議論はあるか?**:
   - ⚠️ [P464] [P466] は抄録だけで、調整（行動の反復性・伝達様式）の向きは読めていない。
   - ⚠️ 4 本とも健康メッセージか想定場面で、PC の作業中の小さな誘いへの外挿である。
   - ⚠️ 選択を示す効果は [P465]（小さく上がる）と [P466]（効果なし）で割れる。
   - ★ 既登録との関係: [P260]（自律支援的な言い回しの直接検証・N = 521・すべて null）と同じ向きである。ADR-021 D5 は「自律支援的な言い回しへの投資を却下・統制的な語を避ける既決は維持」と決めており、本ラウンドはその両方を補強する。
   - ★ **GSE への含み**:
     - 統制的な語（must / should・「〜しましょう」の指示）を避ける根拠が、メタ分析で 1 本増えた（[P464]）。
     - 「自律支援的に言い換えれば反発が消える」「理由を説明すれば受け入れられる」は言えない（反発は [P260] [P466] [P467]・否決 N2・N5。⚠️ [P465] は反発を測っておらず、知覚された自律支援などで言葉の有意差が無かった、までである）。→ **招待の場で理由（状態）を言う根拠は、反発の側からは得られない。** 事後の透明性（ADR-035・[P380]）は、招待の場ではなく規則と目的の開示で満たす案と矛盾しない。
     - 本人が時期を統制できることで反発が減るかは、S-PI の範囲で研究が無い（claim 18）。ADR-035 の原則は反発の低減ではなく非支配の議論（[P380]）から立っているので、この穴で ADR-035 は揺らがない。
6. **次に読むべき論文は?**: Steindl et al. 2015（リアクタンスの総説・数値は未取得）／ Miller et al. 2007（統制的な言葉・抄録だけ見た）／ Reynolds-Tylus 2019（総説・未精読）／ ナッジの受容の調査研究（未検索）。
- **やり残し**: 時期の統制・頻度と反発の直接比較は、S-PI の範囲で 0 件。

---

## 否決リスト（★ カード本体に書かない）

| # | 立てた主張 | 出典 | 票 | 否決の理由 |
|---|---|---|---|---|
| N1 | 無視できない強制的な促しは、任意の起動より休憩の遵守を高める（= 台帳 #10） | [P462] | **1-2** | 前半 13 週が強制・後半 13 週が任意の固定順で、順序（時間・新奇性の減衰）と交絡している。N = 46 のパイロット。感情は測っていない。⚠️ 本文の「passive prompt」は**無視できない促し**の意味（逐語 *"participants were exposed to a prompt that did not allow them to ignore the request to engage in the recommended behaviour"*）で、受動的な表示ではない |
| N2 | 自律支援的な言い方に替えれば、反発が減り、行動が増える | [P260] [P466]（⚠️ [P465] は根拠にしない） | **0-3** | 反発: 反発の成分（怒り・反論）を測った [P260] は有意差なし。[P466] で反発が下がったのは自律の欲求が高い人に限る。行動: 測った研究は無く、意図は [P466] で下がった（抄録だけ）。⚠️ [P465] は反発も行動も測っていない（知覚された自律支援・関連性・全体の評価で有意差なし）ので、この否決の根拠に使わない |
| N3 | 画面の端の受動的な表示でも、ostrich 型の回避が起きる | [P456] [P457] | **1-2** | 一次はどれも自分から見に行く情報（ログイン・計算機・体重計）で、受動的な表示を対象にした研究は S-PI の範囲で 0 件 |
| N4 | 予期された罪悪感は行動を促す（だから罪悪感は害ではない） | [P463] | **0-3** | 相関で、結果は意図であり行動ではない。著者自身が因果の検証を求めている。かつ罪悪感を動機に使うことは GSE の規則（ADR-033 D3）と向きが逆 |
| N5 | 招待の理由を説明すれば、反発が減り受け入れられる | [P467] | **1-2** | 説明の主効果は反発にも自律にも無かった（B = 0.01, p = .72 ／ B = 0.04, p = .092）。ナビの場面だけ説明が自律を上げたが、場面ごとの分析で、全体の結論ではない |

## 登録しなかったもの（★ 次のラウンドで重ねて取らないため）

- **抄録に数値が無い**: Ma, Ma, Kalny & Walter 2025（*Journal of Communication* 75(5)・k = 35・「概ね理論どおり・異質性が大きい」）。
- **問いに答えない**: Rains 2013（リアクタンスの測定の枠組みのメタ分析）／ Quispe-Torreblanca et al. 2024（ログインが参照点を作る・回避の検定ではなく、ostrich 効果は Karlsson et al. 2009 の二次引用）。
- **査読前**: Humphreys et al. 2025（medRxiv・ウェアラブルの質的研究 11 名）。
- **取得できず（突破していない）**: Evans et al. 2012（職場の point-of-choice prompts の RCT）／ Pedersen et al. 2014 ／ Kersten-van Dijk et al. 2017 ／ Li & Shi 2025・Solovei et al. 2024 の本文（人間確認で停止。抄録で登録した）。
- **未読・未取得**: Sweeny et al. 2010（抄録だけ見た）／ Karlsson et al. 2009 ／ Gherzi et al. 2014 ／ Howell & Shepperd 2016 ／ Steindl et al. 2015 ／ Miller et al. 2007（数値を取っていない）。

## GSE への還元

- **`docs/research-positioning.md` は還元不要**（本タスクの範囲外・`requirement.md`）。本ラウンドは EH0 の設計の制約の根拠であり、§3・§4 の既存の主張を補強も反証もしない。
- 還元先は `.steering/20261005-portrait-invitation-constraints/decisions.md`（ラベル・無視の扱い・物体の決定の材料）と `.idea/20261005-motivation-fatigue-reentry-surface.md`（版管理外）。要点は次の 4 つである。
  1. **ラベル**: 回避の一次は「自分から見に行く不都合な情報」についてで、受動的な表示と表示の形は S-PI の範囲で 0 件。招待に状態のラベルを付けると回避の機序の対象になりうる（外挿）。断ることを予測したのは「不正確・役に立たない」の信念だった（[P457]）。理由の説明の主効果は、反発にも自律にも検出されなかった（[P467]・1 研究・想定場面）。→ **招待の場で状態を言う根拠は、回避の側からも反発の側からも得られない**（カード 1・4）。⚠️ これは「言わないこと」を文献が決めたという意味ではない（言わないのは設計上の選択・`decisions.md` 判断 4）。
  2. **無視の罪悪感**: 文献の引き金（目標・記録・否定的な表示・通知での指摘）は GSE の既決で外されている。それでも残るかは研究が無い。→ **EH3 で測る**（カード 3）。
  3. **言い方**: 統制的な語を避ける（[P464]）。自律支援的な言い換えに効果を期待しない（反発は [P260] [P466]・知覚された自律支援などは [P465]）。
  4. **反証側を忘れない**: 監視を促すと達成は上がる（[P458]）。「見せないこと」には代償がありうる。GSE が状態を見せない理由は回避ではなく ADR-025 の機序と判断 1 である（カード 2）。

## やり残し

1. **dismiss・snooze と罪悪感**: 通知を閉じる・先送りするときの感情の研究（本ラウンドは未検索）。
2. **表示の形と回避**: 数値・ラベル・比較・抽象を操作して回避・離脱を測った実験（S-PI の範囲で 0 件）。
3. **時期の統制・頻度と反発**: 本人が時期を統制できる促しとできない促しの比較（S-PI の範囲で 0 件）。
4. **ナッジの受容の調査研究**（反発の反証側・未検索）。
5. **罪悪感の測り方**: EH3 で使う状態の罪悪感の尺度（本ラウンドは探していない・反発は [V115] [V116] が登録済み）。
6. ⚠️ 本ラウンドの探索は各 angle 2.7〜4.0 分で、網が粗い。判定不能の 6 件は、より広い探索で埋まる可能性がある。
