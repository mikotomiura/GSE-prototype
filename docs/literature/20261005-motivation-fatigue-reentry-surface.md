# AI 疲労は動機の低下か —— 再着手の面に置く「評価されない驚き」とあわせて、4 つの下位問いを一次に当てる

> 2026-10-05 / `/literature-review` 1 ラウンド（S-MR）/ **設計根拠の補強とランドスケープ**（gate 判定ではない）
> 対象: `.idea/20261005-motivation-fatigue-reentry-surface.md`（版管理外・研究者の気付きから始めた議論の記録・EH0）／ `.steering/20261005-motivation-reentry-survey/`
> 名前空間: `P`（新規 [P437]–[P453]）。既登録の再利用: [P362]（AI Fatigue Scale・AI 疲労 DB の AF001）[P99] [P107] [P77] [P100] [P199] [P200] [P201] [P203] [P209] [P210] [P35] [P215] [P341] [P343] [P351] [P355] [V108] [V109] [V110] [V144]。
> ⚠️ 登録の途中で、AF001 が [P362] として既に登録済みだと `check_citations.py` が捕捉した（私の事前の grep は語「AI Fatigue Scale」で探していて、題の語順が違うため当たらなかった）。未コミットのうちに新規の行を落とし、採番を詰めた（citation-ssot ルール 2 の例外）。
> ★ 2026-10-05 に `/cross-review` 1 巡目（Claude・Codex）の指摘 24 件と、2 巡目の 16 件を当てて改訂した（`.steering/20261005-motivation-reentry-survey/decisions.md` 判断 4・5）。

## 動機（★ なぜこのラウンドを回したか）

2026-10-05、研究者は AI 疲労 DB の文献を読んで、「勉強・作業での動機づけの低下から AI 疲労が始まり、デジタル疲労が併発して作業場の認知の停滞になる」と気付いた。議論の中で研究者は次のように決めた（`.idea/` §2）。

- 「始まり」は順序ではなく**構成**として持つ。AI 疲労の中身の少なからぬ部分は動機の低下である。（→ 本ラウンドの結果、カード 1 §5 で「一般には言えない」に改めた）
- 「併発」は「**両方高い人がいる**」（人と人のあいだ）の意味である。
- 疲労と停滞は「**多層**」で結ぶ（人の背景 × その人の中の停滞の配合と終わり方）。
- 介入は「**思いがけない形が返る**」側とする。面は**再着手の面**（壁紙）と画面端の小面で分担する。

> ⚠️ **用語の訂正**: 議論ではこの介入を「非随伴」と呼んだが、不正確だった。形は打鍵から作るので、**打鍵には随伴する**。随伴しないのは**成績・評価**である。Deci et al. の分類でも、予期しない報酬（unexpected）と課題に随伴しない報酬（task-noncontingent）は別のカテゴリである [P99]。→ 本カードでは 2 つの語を使い分ける: **予期しない驚き**（評価の有無を問わない上位の語・[P445] の予告なしの賞も含む）／ **予期しない・評価を含まない驚き**（介入案の条件）。

議論の時点で、次の 3 点が repo 内の一次に接地していなかった。

1. 両方高い人がいる、の根拠が AF001 の 1 本だけだった。
2. 予期しない驚きが動機・再関与に効く証拠がゼロだった。
3. 動機が効くのは着手より再着手だ、は推測だった。

★ 既存カードとの関係: 周辺表示の代償（`20260907-pc-invitation-surface-and-peripheral-cost.md`）は「代償は出すか出さないかと面積でしか動かない」とし、やり残しに「**状態変化のときだけ・単発で出す条件を単離した実験はゼロ**」を挙げていた。本ラウンドの SQ4 はその隣の穴（作業の切れ目に出す面）を当たる。

★ 下位問い（研究者と合意・2026-10-05・`decisions.md` 判断 1。文言は用語の訂正の後）:
- **SQ1 構成**: AI 疲労・テクノストレス・デジタル疲労の尺度は動機を含むか。個人間で強く相関するか。弁別できるか。
- **SQ2 多層**: 人のレベルの疲労・動機が、その人の中のエピソードの頻度・長さ・終わり方を変えるという多層の証拠はあるか。
- **SQ3 驚き**（＋**反証 angle**）: 予期しない驚きは内発的動機・再関与を上げるか。慣れ・ゲーム化の減衰・逸脱刺激・gaming・快楽順応で消えるか、害になるか。
- **SQ4 再着手の面**: 作業へ戻る瞬間の手がかり・周辺表示・壁紙は、復帰のコストを増やすか減らすか。

## 検証状態

- **探索**: サブエージェント 5 本（Sonnet・angle ごと・入れ子禁止）。締切は 20 分としたが、実際の所要は **各 2.5〜3.6 分**だった。⚠️ **網は粗い**。以下の「0 件」は、すべて **この探索の範囲で見つからなかった**の意味であり、研究が存在しないという主張ではない。生の出力は scratchpad（`survey/A1–A5.md`・版管理外）。
- **探索の範囲**（2026-10-05・Web 検索 ＋ Europe PMC の REST ＋ Crossref の API・有料の DB は使っていない）:
  - A1（心理測定）: Web 検索 6 回（generative AI technostress fatigue discriminant validity HTMT ／ videoconference fatigue scale motivation ／ mental fatigue motivational shift cost-benefit ／ Müller & Apps ／ technostress Zoom fatigue correlation ／ MFI reduced motivation）
  - A2（多層）: Web 検索 3 回（Dora ／ daily diary × burnout × cross-level × procrastination ／ Fisher）＋ Europe PMC 4 回（burnout × cross-level × ESM ／ technostress × diary ／ work engagement × interruption ／ DOI 照会）
  - A3（驚き）: Web 検索 約 8 回（Isen Reeve ／ Gruber ／ Deci unexpected tangible ／ unexpected reward free-choice ／ Kidd Hayden ／ failed replication positive mood gift ／ surprise gift unexpected bonus persistence ほか）
  - A4（反証）: Web 検索 8 回（Sailer Homner ／ Parmentier deviant ／ novelty effect ambient display ／ gaming quantified self ／ hedonic adaptation ／ Shin novelty ／ gaming productivity metric ほか）
  - A5（再着手の面）: Web 検索 5 回（Kim Park Niu microbreak ／ UbiFit glanceable wallpaper ／ Trafton 2003 resume ／ Hunter Wu break ／ desktop wallpaper lock screen exposure）
- **取得ソース**: 約 30 件（★ 全文到達 約 22 件 ／ 抄録のみ 4 件 ／ 取得できず 5 件）。本ラウンドで新規に登録したのは 17 件。
- **claim**: 台帳 22 件 ＋ 検証の途中で立てて落とした一般化 6 件（否決リスト N1–N6）＝ 28 件
  - 台帳 22 件の内訳: **confirmed 16**（3-0 が 2 ／ 2-1 が 14。温度は 確定 14 ・ PLAUSIBLE BUT UNPROVEN 2）／ **否決 1**（#17 → N7）／ **判定不能 5**
- ★ **メインが一次で逐語を照合した**: [P362] 結果の節（収束・増分・基準関連）と Table 1 の 15 項目（p.6・画像）／ [P437] 抄録と CFA の節／ [P438] 抄録と考察／ [P439] 本文 2 か所／ [P440] 結果 2.2・考察 3 の 4 か所と参加の条件／ [P441] 考察 2 か所・抄録の N／ [P442] 結果と抄録の N／ [P99] p.640／ [P443] 結果（Exp.1 の秒数・最初の選択・Exp.2 の主効果）と抄録／ [P444] 抄録 2 か所／ [P445] 抄録と結果／ [P446] 抄録と**結果の節**（PostGo / PostNoGo）／ [P447] §7.1／ [P448] 抄録と結果／ [P449] 考察 2 か所／ [P450] 章の本文／ [P451] 抄録・§3・§4.2.5／ [P452] §3・§6.1。[P453] は**抄録を Crossref の API から自分で取得して照合**した（本文は有料で未取得）。
- ★ 書誌（著者・巻号頁・DOI）は、新規の 17 件と再利用の [P362] の **18 件すべてを Crossref で確認**した（[P452] の DOI と [P450] の章 DOI は Crossref の書誌検索で特定した）。
- ⚠️ サブエージェント A1 の報告は、WebFetch の要約を逐語として扱っていた（頁番号なし）。→ A1 由来の文献のうち、本文を自分で取れなかったもの（Zhao et al. 2026・Scientific Reports の EFL 研究・Gecaite-Stonciene et al. 2020）は**登録しなかった**（下の「登録しなかったもの」）。

### claim 台帳

| # | claim | 出典 | 票 | 温度 |
|---|---|---|---|---|
| 1 | AI 疲労の尺度は、画面疲労（r = .60）・SNS 疲労（.63）と個人間で強く相関し、一般・臨床の疲労（FAS .63・Chalder .52・MFI .59）とも同程度に相関する | [P362] | **2-1** | 確定（留保: 1 研究・この尺度に限る。既存の 5 尺度を書き換えて作った尺度なので、項目の重なりが相関を押し上げうる） |
| 2 | AI 疲労を、一般・臨床・デジタルの疲労と AI テクノストレスに足すと、現在の AI 利用の説明が 8.38% 増えた（F(1, 281) = 28.10。著者は増分妥当性として報告） | [P362] | **3-0** | 確定 |
| 3 | AI 疲労が高いほど現在の AI 利用が少なく（β = −.27）、減らす意図が強い（β = .33）。行動の回避の次元を除いた版でも残る（β = −.17） | [P362] | **2-1** | 確定（留保: 横断・利用は自己報告） |
| 4 | ビデオ会議疲労の尺度には「動機の疲労」の下位尺度があり、MFI の動機低下の項目から作られている | [P437] | **3-0** | 確定 |
| 5 | 主観的な疲労は動機の条件によらず時間とともに増えたが、動機が高い区間では成績と関与（努力の投入）が保たれた | [P438] | **2-1** | 確定（留保: 実験室・数独 3 時間・N = 28） |
| 6 | 努力・疲労・退屈は理論上分離でき、努力は費用であると同時に価値も足す | [P439] | **2-1** | PLAUSIBLE BUT UNPROVEN（総説） |
| 7 | 1 人の中では、疲労・退屈が高い時間ほど、回答後の 20 分にスマホの使用があった確率が高かった（OR 1.36・1.43。使用があったのは全体の 52% のケース）。使用があった場合の、その 20 分の使用時間の合計への効果の証拠は無かった | [P440] | **2-1** | 確定（留保: 観察・因果は不明と著者が明記・探索的・計画の標本数に届かず中断・CrI の下限 1.02・仕事用のアプリは除いていない） |
| 8 | 人のレベルの特性（FOMO）は、人の中の「疲労・退屈 → スマホ」の関係を強めなかった | [P440] | **2-1** | 確定（留保: 特性は FOMO であって疲労ではない・探索的） |
| 9 | この 2 研究（自己報告の日誌）では、人と人のあいだの関係と 1 人の中の関係が一致しなかった（効く変数が違う・相関の大きさが大きく違う） | [P441] [P442] | **2-1** | 確定（留保: 2 研究とも自己報告の日誌・[P442] の日々の構成概念は単一項目の代理指標） |
| 10 | 人のレベルの疲労・動機が、1 人の中の作業エピソード（停滞・離脱・復帰）の頻度・長さ・終わり方を変えることを直接検定した研究 | — | — | **判定不能（S-MR の範囲で 0 件）** |
| 11 | 予期しない物質的報酬の条件では、内発的動機（自由選択）への平均効果は検出されなかった（d = 0.01 [−0.20, 0.22]・9 研究。著者は *"do not affect"* と解釈） | [P99] | **2-1** | 確定（留保: CI は −0.20 まで含む・係争中 [P107]・GSE の驚きは報酬ではない） |
| 12 | 予期しない小さな贈り物で生じた肯定的感情は、直後の自由選択で面白い課題に使う時間を増やした（233 秒 vs 127 秒） | [P443] | **2-1** | 確定（留保: 数分の単発・実験者からの贈り物・実験 2 本とも N = 60） |
| 13 | 消耗課題のあとに肯定的気分を誘導しても、握力・Stroop の粘りが戻る結果は一貫しなかった（4 実験） | [P444] | **2-1** | 確定（留保: 消耗パラダイムで、その土台の効果自体が頑健でない [P199]–[P201]・知的作業ではない） |
| 14 | 予告なしの（遡及の）賞は、その後の出席を下げた。著者は、賞が「他の人より多くやった」という比較の情報を伝えたためと示唆する | [P445] | **2-1** | 確定（留保: p = .018 / .047・学生の出席・**機序は調査研究からの著者の示唆**） |
| 15 | 予期しない驚きが、離れた作業へ戻ること（再関与）を上げることを直接測った研究 | — | — | **判定不能（S-MR の範囲で 0 件）** |
| 16 | 予期しない課題無関係の刺激は、継続中の課題の反応を遅らせる（聴覚の oddball）。ただし直前に反応した試行に限られ（dz = 0.485）、反応しなかった試行では逆に速まる（dz = −0.640） | [P446] | **2-1** | 確定（留保: 聴覚・ミリ秒単位の連続課題・N = 32） |
| 17 | 新奇性は常に薄れるわけではない（慣れたあとに有用性の評価が 5.47 → 6.32 に上がった例がある） | [P447] | **1-2** | **否決 → N7** |
| 18 | 本人の行動に随伴する表示を良く見せるために、本人が行動を変えること（gaming）を測った経験研究 | — | — | **判定不能（S-MR の範囲で 0 件）** |
| 19 | 中断の前に準備できると復帰が速いが、その差は 2 回目のセッション以降に消えた。著者は、復帰時に知覚的な手がかりが使われないよう作業窓を背景化した | [P451] | **2-1** | 確定（留保: 実験室・小標本） |
| 20 | 作業へ戻る瞬間に、作業と無関係な表示を足したときの復帰の遅れを測った研究 | — | — | **判定不能（S-MR の範囲で 0 件）** |
| 21 | 休憩中の認知的な活動は、仕事の要求と終業時の否定的感情の結びつきを強めた（リラックス・社交は弱めた） | [P453] | **2-1** | PLAUSIBLE BUT UNPROVEN（**抄録のみ**・結果変数は感情で、戻ってからの関与ではない） |
| 22 | PC のデスクトップ壁紙の曝露（実際に見られる頻度）と効果を測った研究 | — | — | **判定不能（S-MR の範囲で 0 件）** |

票の 3 つの視点は、内的妥当性 ／ 外挿（GSE の場面 = PC での知識作業・1 人の中の数分〜数十分）／ 効果量の頑健性（標本・再現・p の余裕）である。

★ 温度の凡例: **確定** = 直接証拠あり ／ **PLAUSIBLE BUT UNPROVEN** = 継ぎ接ぎでしか言えない ／ **判定不能** = 今回の探索の範囲で該当ゼロ ／ **未決**（本カードで足した語）= 該当はあるが、一般化をどちらの向きにも否決した

## gate 判定（要点先出し）

| 下位問い | 温度 | 一言 |
|---|---|---|
| SQ1-a AI 疲労とデジタル疲労は個人間で強く相関するか | **確定（1 研究・[P362] の尺度に限る）** | r = .60 / .63。ただし一般・臨床の疲労とも同程度（.52〜.63）。「AI・デジタルに特有の疲労」は PLAUSIBLE BUT UNPROVEN |
| SQ1-b 疲労の尺度は動機を含むか | **確定（測度による）** | ビデオ会議疲労の尺度は「動機の疲労」を含む [P437]。⚠️ **AI 疲労の尺度 [P362] の 15 項目には、自分の作業・勉強への動機の低下を問う項目が無い**（「離脱」の 4 項目は **AI からの**離脱） |
| SQ1-c 「疲労 = 動機の変化」か | **PLAUSIBLE BUT UNPROVEN（同一ではない側）** | 実験室の 1 研究で、主観の疲労は動機によらず増え、成績と関与は動機で保たれた（分かれた）[P438] |
| SQ2 人のレベルの背景がエピソードを変えるか | **判定不能（S-MR の範囲で 0 件）** | 隣接: 疲労・退屈が高い時間ほど、次の 20 分にスマホの使用があった確率が高かった（観察・探索的）。使用時間への効果の証拠は無い [P440]。2 つの日誌研究では、人と人のあいだと 1 人の中の関係が一致しなかった [P441] [P442] |
| SQ3 予期しない驚きは再関与を上げるか | **判定不能（S-MR の範囲で 0 件）** | 隣接: 予期しない物質的報酬では平均効果が検出されない（CI −0.20〜0.22・係争中）[P99]。予期しない小さな贈り物は、直後の自由選択で面白い課題の時間を増やした（1 研究）[P443]。予告なしの賞は出席を下げた（事前登録の RCT）[P445]。その機序（比較の情報）は著者の示唆 |
| SQ3 反証: 慣れ・逸脱・gaming | 作業の最中の逸脱 = **確定**（聴覚・実験室・直前に反応した試行に限る）／ 新奇性・ゲーム化の減衰 = **未決**（該当はあるが、一般化をどちらの向きにも否決した: N1・N2・N3 ／ N7）／ gaming = **判定不能（S-MR の範囲で 0 件）** | 限定的な観察として、活動量計の低使用群で 3 か月後に使用率が下がった（生存者の標本）[P448]。GSE の形への減衰を判断できる直接の証拠は未確認 |
| SQ4 再着手の面は復帰を助けるか | **判定不能（S-MR の範囲で 0 件）** | 隣接: 復帰前の準備は復帰を速めるが、慣れで差が消える [P451]。休憩中の認知的な活動は、仕事の要求と否定的感情の結びつきを強めた（抄録のみ）[P453]。デスクトップ壁紙の研究は今回の範囲で 0 件 |

---

### カード 1: AI 疲労はデジタル疲労とも一般の疲労とも同程度に相関する。動機は一部の疲労の尺度の中にある **[検証済 3-0 / 2-1]** [P362] [P437]

1. **どんなもの?**:
   - [P362] は 15 項目の AI Fatigue Scale の開発・検証である（Lau et al. 2026。Study 3 は Prolific の米国の成人・AI 利用者 290 人・横断）。4 因子は認知の過負荷（cognitive overload）・情動の負担（emotional strain）・行動の回避と離脱（behavioural avoidance and disengagement）・身体と感覚の疲労（physical and sensory exhaustion）。
   - [P437] はビデオ会議疲労の尺度 ZEF の開発（Fauville et al. 2021。5 研究・最終 15 項目・5 次元）。
2. **先行研究と比べてどこがすごい?**: [P362] は AI 疲労を、一般・臨床の疲労とデジタル疲労の**両方**と同じ標本で並べて相関を報告し、増分の説明も検定した。
3. **技術や手法の肝はどこ?**: 収束・弁別・基準関連・増分の妥当性を 1 つの標本でまとめて出している。
4. **どうやって有効だと検証した?**（★ 一次逐語・メインが照合）:
   - [P362] 逐語 *"AI fatigue correlated positively and strongly with established general and clinical fatigue scales: Fatigue Assessment Scale (r = .63, p < .001), Chalder Fatigue Scale (r = .52, p < .001), Multidimensional Fatigue Inventory (r = .59, p < .001). AI fatigue also correlated positively and strongly with established digital fatigue scales: Screen Fatigue Scale (r = .60, p < .001), and Social Media Fatigue Scale (r = .63, p < .001)."*
   - [P362] 増分: *"adding AI fatigue increased explained variance by 8.38%, F (1, 281) = 28.10, p < .001"*（現在の AI 利用）。
   - [P362] 基準関連: *"higher AI fatigue predicted lower current AI use, b = −.29 … β = −.27 … R2 = .07"*、減らす意図は *"β = .33 … R2 = .11"*。行動の回避の次元を除いた版でも *"continued to predict lower current AI use (… β = −.17 …)"*。（⚠️ PDF の抽出テキストでは負号が落ちる。CI［−.41, −.17］から負と確かめた）
   - [P437] 逐語 *"revealing five dimensions of fatigue: general, social, emotional, visual, and motivational fatigue"*。CFA の節: *"The two remaining items from the reduced motivation construct (redmot_2 and redmot_4) were grouped with the only remaining item from the reduced activity construct (redac_5), creating the construct of motivational fatigue."*
5. **議論はあるか?**:
   - ⚠️ [P362] は既存の 5 尺度（SNS 疲労ほか）を AI 向けに書き換えて作られている（Table S1・AI 疲労 DB の前タスクでメインが確認）。→ 項目の内容の重なりで相関が上がりうる。
   - ⚠️ 一般の疲労（.52〜.63）とデジタル疲労（.60 / .63）がほぼ同程度である。→ 「AI 疲労とデジタル疲労が特に結びつく」とは読めない。共通の 1 つの疲労という読みは**検定されていない**（否決リスト N6）。
   - ⚠️ 神経症傾向 r = .49・否定的感情 r = .47（DB の前タスクでメインが確認）。共通の原因で相関しうる。
   - ⚠️★ **研究者の「AI 疲労の中身は動機」への含み**:
     - [P362] の 15 項目（Table 1・p.6 をメインが画像で確認）には、**自分の作業・勉強への動機の低下を問う項目が無い**。最も近いのは「行動の回避と離脱」の 4 項目（例 *"I avoid using AI even when it could help me."* ／ *"I prefer doing tasks manually rather than using AI."*）と項目 7（*"I sometimes feel a little discouraged when AI takes lots of retries to give me what I need."*）で、いずれも **AI からの**離脱・落胆である。
     - 動機・関与の項目を含む測度はある（ビデオ会議疲労の [P437]）。AI 疲労 DB では AF005 の「関与の低下」2 項目が**手がかり**になる（references.md 未登録・`measurement-issues.md` M4 の記録）。
     - ただし含む測度でも、得点のどれだけが動機かは測られていない。
     - → 「中身は動機」は**一般には言えない**。[P362] が測る AI 疲労は「AI から離れる」側の構成概念である。
6. **次に読むべき論文は?**: AI 疲労・デジタル疲労・一般の疲労を**同じ因子分析に入れた**研究（今回の範囲で 0 件）。
- **やり残し**: 「両方高い人がいる」は 1 研究で確定、「それは AI・デジタルに特有だ」は未確認である。作業・勉強への動機の低下を AI 疲労の一部として測った尺度は、今回の範囲で見つからなかった。

### カード 2: 主観の疲労と関与の低下は分かれうる —— 「疲労 = 動機の変化」とは同一視しない **[検証済 2-1]** [P438] [P439]

1. **どんなもの?**: [P438] は内発的動機と精神的疲労の実験である（Herlambang et al. 2021。28 人が数独を 3 時間解き、動機の高い区間と低い区間を交互に 14 ブロック。画面の隅で猫の動画が流れる）。[P439] は努力の逆説の総説（Inzlicht et al. 2018）。
2. **先行研究と比べてどこがすごい?**: [P438] は主観・成績・生理（心拍変動・瞳孔）を同じ被験者内で同時に測り、疲労の自覚と関与を分けて見た。
3. **技術や手法の肝はどこ?**: 動機を被験者内で操作し、時間の経過（疲労）と交差させた。
4. **どうやって有効だと検証した?**（★ メインが照合）:
   - [P438] 考察の逐語 *"motivation, both extrinsic and intrinsic, is an important factor in mental fatigue: Even though participants reported becoming fatigued over time, motivation helped participants maintain performance levels and stay engaged with the task by investing more mental effort."*
   - [P439] 逐語 *"it is clear that effort expenditure does eventually decline with time on task"*、*"Boredom could thus be theoretically decoupled from, and in different instances positively or negatively related to, experiences of mental effort or fatigue"*
5. **議論はあるか?**:
   - ⚠️ [P438] 著者 *"it was limited to a laboratory environment"*。
   - ★ **GSE への含み**: 疲労の自覚は、動機が保たれていても増える。→ 研究者の「AI 疲労の中身は動機」は、**「AI 疲労と呼ばれる得点には、主観の疲労と動機の低下が混ざりうる。行動の離脱を左右するのは後者かもしれない」**という仮説に留める（カード 1 の §5 のとおり、[P362] には動機の因子が無い）。
   - ★ 既登録との関係: [P203]（投資の意思）・[P209]（報酬で戻る）と同じ向きである。資源側の反証として [P210] がある。
6. **次に読むべき論文は?**: Müller & Apps 2019（動機の疲労）。今回は無料の本文が見つからなかった。
- **やり残し**: 日常の知識作業で、疲労の自覚と離脱を分けて測った研究。

### カード 3: 疲労・退屈が高い時間ほど、次の 20 分にスマホの使用があった —— FOMO による調整は無かった **[検証済 2-1]** [P440] [P441] [P442]

1. **どんなもの?**: [P440] は職場での疲労・退屈とスマホの客観ログの経験サンプリング（Dora et al. 2021。博士課程の学生 83 人・オフィス勤務の 3 日・毎時の自己報告 1,724 回 ＋ アプリの使用ログ・時 < 日 < 人の 3 水準）。[P441] は職場の先延ばしの日誌研究（Prem et al. 2018。110 人・762 日）。[P442] は AI に置き換えられる不安と学業の燃え尽きの 10 日日誌（Li et al. 2026。751 人・4,625 件）。
2. **先行研究と比べてどこがすごい?**: [P440] は自己報告でなく**行動ログ**で、疲労の「後の 20 分」を見た。
3. **技術や手法の肝はどこ?**: [P440] は、回答後の 20 分の使用の有無と、使用があった場合のその 20 分の使用時間の合計を、別のモデルで推定した。
4. **どうやって有効だと検証した?**（★ メインが照合）:
   - [P440] 逐語 *"as fatigue increases by half a standard deviation (approx. 11 points), participants are estimated to be 1.36 times more likely to interact with their smartphone in the following 20 min (95% credible interval = (1.02, 1.82))"*。
   - [P440] 逐語 *"We conclude that there is no evidence for an effect of fatigue and boredom on the amount of time the smartphone is used, provided that it is used at all."*
   - [P440] 逐語 *"FOMO did not strengthen the relationships between fatigue and boredom and smartphone use."*
   - [P440] 記述統計 *"In the 20 min following the completion of the hourly questionnaire, participants had interacted with their smartphone in 52% of the cases. On average, they spent 92 s (s.d. = 181) on their smartphone"*
   - [P441] 逐語 *"depending on the level of analysis and the perspective one takes, different variables seem to play a role in the emergence of workplace procrastination"* ／ *"challenge and hindrance appraisal affected self-regulation effort only on the within-person level"*。
   - [P442] 逐語 *"Within-person correlations were positive but small to modest (r = .077-0.252), whereas between-person correlations were stronger, particularly for cynicism and the academic-inefficacy proxy indicator (r = .845)."*（.845 は特定の組の**最大値**）
5. **議論はあるか?**:
   - ⚠️ [P440] 著者 *"our results should be considered exploratory and should be interpreted with caution. Given the observational design of our study, we cannot conclude that the experiences of fatigue and boredom are causally related to smartphone use."*
   - ⚠️ [P440] は**仕事用のアプリを除いていない**。参加の条件が「勤務中のスマホは私用の方が多い」という自己申告である。→ スマホの使用は作業からの離脱と同じではない（代理にすぎない）。
   - ⚠️ 「使用時間への効果の証拠は無い」は、効果が無いことの証拠ではない。
   - ⚠️ [P440] の人のレベルの変数は FOMO だけで、疲労の特性ではない。→ SQ2 に直接は答えない（claim 10 = 判定不能）。
   - ⚠️ [P442] の日々の構成概念は単一項目の代理指標である。
   - ⚠️ 同じ趣旨の [V108]（群の結果は個人へ一般化しないことがある）は、既存の行のとおり**強い形では引かない**（同誌で 2 本の Letter による批判 [V109] [V110] があり、著者も部分的に譲歩している）。
   - ★ **GSE への含み**:
     - 研究者が選んだ「両方高い人」（人と人のあいだ）から、1 人の中の停滞の起き方を推論できるとは限らない（[P441] [P442]）。→ 多層の仮説は、**人のレベルを別に測り、クロスレベルの交互作用を明示して検定する**形で立てる。
     - [P440] が使用の有無と量を分けて推定した形は、GSE のエピソードの分け方（開始・長さ・終わり方）を考えるときの参考になる。ただし対象も単位も違う（20 分の窓の中のスマホの使用 ／ 停滞の検出時点からのエピソード。ADR-030 は Proposed）。
6. **次に読むべき論文は?**: 燃え尽きの ESM でクロスレベルの調整を報告したとされる研究（`10.1080/1359432X.2023.2266874`）。403 で本文が取れず、検索要約の主張は未確認。
- **やり残し**: 人のレベルの疲労 × 1 人の中の作業エピソードの直接の検定は、今回の範囲で 0 件。自前の計測が候補になる。

### カード 4: 予期しない驚き —— 物質的報酬では効果が検出されず、直後の関与は上がりうる。再関与の研究は今回の範囲で 0 件。予告なしの賞は出席を下げた **[検証済 2-1]** [P99] [P443] [P444] [P445]

1. **どんなもの?**:
   - [P99]（既登録）: 予期しない報酬の条件のメタ分析値。
   - [P443]: 肯定的感情と内発的動機の実験 2 本（Isen & Reeve 2005。各 N = 60。操作は予期しない小さな贈り物＝袋入りの飴）。
   - [P444]: 肯定的気分は認知資源を回復させるかの 4 実験（Nealis et al. 2016）。
   - [P445]: 予告ありの賞と予告なしの（遡及の）賞の事前登録フィールド RCT（Robinson et al. 2021。N = 15,329 の生徒・出席）。
2. **先行研究と比べてどこがすごい?**: [P445] は事前登録の大規模 RCT で、「予告なしの賞」の効果が仮説と**逆向き**に出た。
3. **技術や手法の肝はどこ?**: [P443] は自由選択の時間（面白い課題・つまらない課題）と最初に選んだ課題で、内発的動機を行動として測った。
4. **どうやって有効だと検証した?**（★ メインが照合）:
   - [P99] p.640 逐語 *"Nine studies involved unexpected tangible rewards, and they yielded an average d = 0.01 (CI = −0.20, 0.22), indicating, as predicted, that unexpected tangible rewards do not affect free-choice behavior."*
   - [P443] 逐語 *"positive-affect participants spent more time (M = 233.3 s) on the interesting task than did neutral affect participants (M = 127.4 s), t(58) = 2.35, p < .05"*。Exp.2 でも、面白い課題の時間に感情の主効果 *"F(1, 56) = 14.11, p < .01"*。抄録 *"positive affect does foster intrinsic motivation, and enjoyment and performance of enjoyable tasks, but not at the cost of responsible work behavior on an uninteresting task that needs to be done."*
   - [P444] 抄録 *"participants did not persist significantly longer on the handgrip task following a positive mood induction"* ／ *"across four studies, we failed to find a consistent pattern of results suggesting that positive moods restore cognitive resources."*
   - [P445] 抄録 *"Contrary to our preregistered hypotheses, prospective awards had no impact while the retrospective awards decreased subsequent attendance. Survey studies provide evidence suggesting that receiving retrospective awards may demotivate the behavior being awarded by inadvertently signaling (a) that recipients have performed the behavior more than their peers have …"*。結果 *"60.75% compared to 62.55% in the control … p = .047"*。
5. **議論はあるか?**:
   - ⚠️ [P99] の d = 0.01 は CI が −0.20 まで含む。「害が無い」とは言えず、「平均効果が検出されなかった」までである。係争も続いている（[P107]）。
   - ⚠️ [P443] の効果は数分の単発で、「離れた作業へ戻る」は測っていない（claim 15 = 判定不能）。
   - ⚠️ [P444] は消耗パラダイムの上の実験である。その土台の効果自体が頑健でない（[P199]–[P201]・`docs/glossary.md` の「消耗・回復」の行）ので、「回復しなかった」から驚きについて言えることは少ない。
   - ⚠️ [P445] の p は .018 / .047 で余裕が小さい。読んだのはワーキングペーパー版（HKS RWP18-020）で、公刊版との数値の差は未確認。機序（比較の情報）は**著者の示唆**であり、評価を含まない驚きと比べた群は無い。
   - ⚠️★ **形は打鍵に随伴する**（「動機」節の用語の訂正）。最初は予期しなくても、慣れると「打鍵すれば形が返る」という予期された帰結になる。Deci et al. の分類では、予期された・取り組みに随伴する物質的報酬は、自由選択の指標で内発的動機を下げた（engagement-contingent d = −0.40。自己報告の興味では −0.15・係争中 [P107]・一方の側だけを引かない。[P99] の既存のカード `20260815-portable-ambient-object-and-activity-coupling.md` カード 3）。形は報酬ではないが、本人が価値を置くなら報酬のように働きうる。**これは未検証のリスクである。**
   - ★ **GSE への含み**:
     - 「驚きに比較・評価を載せない」という条件は、ADR-025・ADR-033・[P99] [P77] に加え、[P445] の著者の示唆とも同じ向きである（根拠の候補であって、評価を含まない驚きの効果を示したものではない）。
     - 「思いがけない形で動機を上げる」は**言えない**。言えるのは「予期しない報酬の平均効果は検出されず、肯定的感情は直後の自由選択を少し上げうる（1 研究）」までである。
6. **次に読むべき論文は?**: "No Gifts Returned: Surprise Bonuses Reduce Productivity in a Natural Field Experiment"（Management Science・本文は有料・OSF 版が同一かは未確認）。
- **やり残し**: 予期しない驚き → 再関与を直接測った研究は、今回の範囲で 0 件。

### カード 5: 作業の最中の予期しない刺激は反応を遅らせる —— ただし直前に反応した試行に限る **[検証済 2-1]** [P446]

1. **どんなもの?**: [P446] は聴覚の oddball による注意の逸れの実験（Parmentier et al. 2022。N = 32・標準音 80%・逸脱音 10%・無音 10%・数字の分類課題）。
2. **先行研究と比べてどこがすごい?**: 直前の試行で反応したか（Go / NoGo）で、逸脱刺激の効果が逆向きになることを示した。
3. **技術や手法の肝はどこ?**: 逸脱音と予期しない無音を分け、直前の試行の種類と交差させた。
4. **どうやって有効だと検証した?**（★ メインが結果の節で照合）:
   - 抄録 *"It has been established that participants performing a continuous categorization task respond significantly slower following the presentation of unexpected, task-irrelevant, auditory stimuli, compared to a repetitive (standard) sound."*（← これは先行研究の要約の文）
   - 結果 *"in the PostGo condition, deviant sounds yield distraction relative to the standard condition: t (31) = 2.743, p = .010, d az = 0.485 (95% CI: 0.115 to 0.848) … In contrast, the effect was reversed in the PostNoGo condition: t (31) = -3.623, p < .001, d az = -0.640 (95% CI: -1.017 to -0.255)"*。予期しない無音でも反応は遅れた（*"F (1,31) = 4.359 … p = .045"*）。
5. **議論はあるか?**:
   - ⚠️ 聴覚でミリ秒単位の課題である。PC の作業の切れ目に出す視覚の表示へは外挿にすぎない。
   - ⚠️ 一律に妨げるのではない（反応しなかった試行では速まる）。
   - ★ **GSE への含み**: 驚きを**打鍵の最中に出さない**ことの根拠は、既存の能動タイプ中の defer と [P341] [P343] に、[P446] が（外挿として・聴覚の実験室）加わる。
   - ★ 新奇性・ゲーム化の減衰は**未決**である（一般化を、減衰の側 N1・N2・N3 も反例の側 N7 も否決した）。→ **減衰を前提にも否定にもせず、週単位で測る**。
6. **次に読むべき論文は?**: Koch et al. 2018（大型ディスプレイ展開の新奇性効果・人間確認で本文が取れず）。
- **やり残し**: 「本人の手つきから作った思いがけない形」への慣れの速さと、gaming の経験研究は、今回の範囲で 0 件。

### カード 6: 再着手の面 —— 準備は復帰を速めるが慣れで差が消える。デスクトップ壁紙の研究は今回の範囲で 0 件 **[検証済 2-1]** [P451] [P453]

1. **どんなもの?**: [P451] は中断への準備と復帰の実験（Trafton et al. 2003）。[P453] は職場のマイクロブレイクの 10 日の経験サンプリング（Kim, Park & Niu 2017。86 人・842 点・**抄録のみ**）。
2. **先行研究と比べてどこがすごい?**: [P451] は準備の効果がセッションを重ねると消えることを示した（慣れ）。
3. **技術や手法の肝はどこ?**: [P451] は復帰時の知覚的な手がかりを**消した**うえで、記憶だけによる復帰を測った。
4. **どうやって有効だと検証した?**（★ メインが照合）:
   - [P451] 抄録 *"Participants in the Warning condition prepared more than participants in the Immediate condition, as measured by verbal reports, and resumed the interrupted task more quickly. However, Immediate participants resumed faster with practice, suggesting that people adapt to particularly disruptive forms of interruption."*
   - [P451] §4.2.5 *"there was no effect of warning for session two … or session three"*。
   - [P451] §3 *"The software also deactivated (or defocused, or 'back-grounded') all windows of the tank task, so that during resumption the operator would not be able to infer from perceptual cues which window he or she had been working in."*
   - [P453] 抄録（Crossref） *"relaxation and social activities reduced the effects of work demands on end‐of‐workday negative affect … Unexpectedly, cognitive activities aggravated the effects of work demands on negative affect."*
5. **議論はあるか?**:
   - ⚠️ [P451] は実験室で小標本である。復帰の瞬間に表示を**足す**操作はしていない（claim 20 = 判定不能）。
   - ⚠️ [P453] は抄録のみで、結果変数は終業時の否定的感情である（要求と否定的感情の結びつきの調整）。
   - ★ **GSE への含み**（いずれも**外挿**）:
     - 再着手の面が見せる形は、**解読を求めない**ものにする（[P453] の「認知的な活動」の側に寄せない）。
     - 復帰時の知覚的な手がかりは復帰に使われうる（[P451] の著者がそれを消した理由）。ただし GSE の形は content-free で、作業の中身を指せない。手がかりとして働くかは未知である。
     - 既登録の [P351] [P355] [V144] [P35] とも矛盾しない。
6. **次に読むべき論文は?**: Hunter & Wu 2016（[P215]・休憩の活動。今回は 403 で本文未取得）。
- **やり残し**: **デスクトップ壁紙の曝露と効果を測った研究は、今回の範囲で 0 件**（claim 22）。携帯の壁紙の研究（[P452] [P100]）はあるが、外挿は否決した（N4）。自前の計測（EH2 / EH3）が候補になる。

---

## 否決リスト（★ カード本体に書かない）

| # | 立てた主張 | 出典 | 票 | 否決の理由 |
|---|---|---|---|---|
| N1 | 新奇性効果は約 3 か月で消える（一般則として） | [P448] | **1-2** | 活動量計を最低 2 か月使った人だけの標本（生存者）・N = 23・著者自身が *"we infer"*。逐語 *"The novelty period for Fitbit users in this study was approximately 3 months"* |
| N2 | ゲーム化の効果は時間で薄れない | [P449] | **1-2** | 期間は調整変数として有意でなかったが、逐語 *"only one study reported a delayed posttest"*。逆向きの「薄れる」も証拠なし（0-3） |
| N3 | 肯定的な状況の変化の効果は快楽順応で薄れる（多様さを保てば薄れにくい） | [P450] | **1-2** | 概説章で、一次（Sheldon & Lyubomirsky 2009）を読んでいない。逐語 *"these effects are relatively small, and tend to erode over time (as shown by Sheldon & Lyubomirsky, 2009)"* |
| N4 | 壁紙は作業の切れ目に見え、作業を妨げない（デスクトップにも当てはまる） | [P452] [P100] | **1-2** | 携帯のホーム画面（解錠や切り替えのたびに出る）と自己申告だけ。[P452] 逐語 *"All 16 participants reported in interviews that, on the whole, they did not find Emotipix's display distracting or disruptive to their workflow"*。デスクトップは最大化した窓の背後に隠れる（`pc-workplace-media-reassessment.md:40`） |
| N5 | 予期しない驚きは作業への動機を上げる | [P99] [P443] [P444] [P445] | **0-3** | 再関与を測った研究は今回の範囲で 0 件で、隣接の証拠は割れている（平均効果は検出されず・直後のみ上昇・粘りの回復は一貫せず・予告なしの賞は逆効果） |
| N6 | AI 疲労とデジタル疲労は 1 つの共通の疲労である | [P362] | **1-2** | 相関だけで、共通因子を検定した研究は今回の範囲で 0 件 |
| N7 | 新奇性は常に薄れるわけではない（反例がある） | [P447] | **1-2** | 測ったのは**有用性**の評価で、新奇性への関与ではない（新奇性の効果が薄れつつ、習熟で有用性が上がることは両立する）。3 週間・N = 12・生成 AI の業務ツール。逐語 *"we found the average system utility increased by 12.1% after familiarization (5.47/7 to 6.32/7, p-value < 0.005)"*（= 台帳 #17） |

## 登録しなかったもの（★ 次のラウンドで重ねて取らないため）

- **本文を自分で確かめられなかった**: Zhao et al. 2026（Frontiers in Psychology・AI 時代のデジタル燃え尽き尺度・WebFetch の要約のみ）／ Scientific Reports の EFL 学生の研究（認証と CAPTCHA）／ Gecaite-Stonciene et al. 2020（MFI の因子分析・WebFetch の要約のみ）。
- **二次引用だけ**: Gruber et al. 2014・Kidd & Hayden 2015（好奇心と学習。再関与を測っていない）／ Hamari et al. 2014。
- **取得できず（突破していない）**: Koch et al. 2018（人間確認）／ Tandfonline の燃え尽きの ESM 研究（403）／ "No Gifts Returned"（有料）／ Parmentier 2014 のレビュー（有料）。
- **概念論文**: Whitson 2013（gaming the quantified self）。経験研究ではない。

## GSE への還元

- **`docs/research-positioning.md` は還元不要**（研究者の決定・`decisions.md` 判断 1）。本ラウンドは EH0 の設計案の根拠であり、§3・§4 の既存の主張を補強も反証もしない。
- 還元先は `.idea/20261005-motivation-fatigue-reentry-surface.md` §7（版管理外）。要点は次の 4 つである。
  1. **構成の精緻化**: 「AI 疲労の中身は動機」は**一般には言えない**。動機・関与の項目を含む測度はある（[P437]・AF005 は手がかり）が、[P362] の 15 項目には自分の作業への動機の低下を問う項目が無く、「離脱」は AI からの離脱である。含む測度でも、得点のどれだけが動機かは測られていない。仮説として「AI 疲労と呼ばれる得点には主観の疲労と動機の低下が混ざりうる。行動の離脱を左右するのは後者かもしれない」に留める（カード 1・2）。
  2. **多層は今回の範囲で直接の検定が 0 件**: 人のレベルを別に測り、クロスレベルを明示して検定する設計でしか立たない。自前の計測が候補になる（カード 3）。
  3. **驚きの条件**: 比較・評価の情報を運ばない。目標は「動機を上げる」ではなく「評価されない驚きに出会う機会」のままにする。形が打鍵に随伴することのリスク（慣れると予期された帰結になる）を設計の未決として持つ（カード 4）。
  4. **面と時**（いずれも外挿を含む）: 打鍵の最中には出さない。再着手の面には解読を求めない形を置く。デスクトップ壁紙は今回の範囲で研究が見つからず、自前の計測が候補になる（カード 5・6）。

## やり残し

1. **SQ2 の最有力**: 燃え尽きの ESM でクロスレベルの調整を報告したとされる研究（`10.1080/1359432X.2023.2266874`）の本文。
2. **SQ3 の反証側の最有力**: "No Gifts Returned" の OSF 版（驚きのボーナスが生産性を下げたとされる）。
3. **新奇性の減衰の速さ**: Koch et al. 2018 の本文と、周辺表示の数週間の展開研究。
4. **快楽順応の一次**: Sheldon & Lyubomirsky 2009。
5. **AI・デジタル・一般の疲労の合同の因子分析**と、作業・勉強への動機の低下を AI 疲労の一部として測る尺度の探索。
6. **デスクトップ壁紙の曝露**: 今回の範囲で研究が見つからない。自前の EH2 / EH3 が候補になる。
7. ⚠️ 本ラウンドの探索は各 angle 2.5〜3.6 分で、網が粗い。判定不能の 5 件は、より広い探索で埋まる可能性がある。
