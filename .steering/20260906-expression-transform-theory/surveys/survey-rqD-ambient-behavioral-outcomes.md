# RQ D サーヴェイ: アンビエント表現の効果は「行動指標」で測られてきたか

## 0. 再実行に関する注記

先行試行はレート制限で成果物ゼロのまま終了した。本ラウンドは探索を **16 ソース**で打ち切り、
早期書き出し（本ファイル）→ 追記の方針で進めた。以後の追記はすべて本ファイルへの上書きで行っている。

## 1. 動機

GSE は表現層の合否指標を「可読性（弁別正答率）」から「行動指標」へ主要アウトカムとして
差し替え、可読性は manipulation check へ降格する方針転換を検討している。本ラウンドは、
この「形」（周辺的・非侵入的表現の効果を行動指標で測る／可読性は前提条件に留める）に
先行研究があるかを、UbiFit（登録済み・除外対象）の外側で確かめる。

## 2. 検証状態

- 探索 angle: (a)評価手法の系統的把握 / (b)UbiFit 以外の行動アウトカム統制研究 /
  (c)可読性と行動の乖離報告 / (d)manipulation check 明示設計 / (e)反証（novelty effect・効果薄）
  の 5 angle × 各 3〜4 クエリ。
- 収集ソース数: **16 件**（一次全文確認 = **6 件**、二次資料水準（要約・抄録止まり） = **10 件**）。
  - 一次確認: Matthews, Hsieh & Mankoff 2009 / Karlin, Zinger & Ford 2015 / Tiefenbeck et al. 2018
    (Management Science) / Kelly & Knottenbelt 2016 / Jörke et al. 2026 (Bloom, arXiv) の 5 本は
    pypdf でダウンロード済み PDF の全文を直接読んだ。Tiefenbeck et al. 2019 (Nature Energy) は
    書誌情報のみ CrossRef で確認（本文はペイウォール/認証リダイレクトで未取得）。
- claim 抽出: **10 claim**（C1〜C10。うち主要 8 件を敵対的 3 票にかけた）。
- 敵対的 3 票の内訳: **confirmed 7 件**（うち 3-0 = 2 件、2-1 = 5 件）、**否決 1 件**（1-2、Fish'n'Steps
  の「行動変化した」という強い主張）、**判定不能 1 件**（C6: salience bias の必要条件仮説、直接検証なし）。

## 3. gate 判定（要点先出し）

- **(a) 最優先**: **確定（定性）/ 判定不能（定量内訳の網羅性）**。一般的な ambient/peripheral
  display 評価の慣習的基準は「usability 系 + awareness/distraction 系」であり、行動変化は標準
  カテゴリに入っていない（Matthews 2009 / Pousman & Stasko 2006 / Hazlewood et al. 2011 が独立に
  一致）。ただし eco-feedback/persuasive tech という**隣接分野では行動指標(実消費量)が標準**
  （Karlin et al. 2015: 42 効果量すべて消費量ベース）。★ **ambient display 研究全体を横断した
  「内訳の実数・割合」を報告した単一の系統的レビューは本ラウンドでは発見できなかった**
  （Karlin の 42 件は eco-feedback に限定した収集基準の産物であり、母集団の内訳ではない）。
- **(b)**: **確定**。UbiFit 以外にも行動指標を主要アウトカムに据えた統制研究は存在する。
  最強例は Tiefenbeck et al. 2018 (N=697, RCT, 22% 減、2 か月間減衰なし)。ただし
  ★ そのデバイスは純アンビエントではなく **数値+アイコンのハイブリッド**である点に留保。
- **(c)**: **PLAUSIBLE BUT UNPROVEN**。Pereira et al. 2013 (N=12, 52 週) は「気づきは上がったが
  対話行動は 9 割減り、消費量は有意に変化しなかった」という乖離を報告するが、小規模・統制群なし。
  ★ **個人内で「理解度」と「行動変化」の相関を直接検定した研究は本ラウンドでは発見できなかった**
  （やり残しに記録）。
- **(d)**: **確定（存在するが希少）**。Jörke et al. 2026 (Bloom, CHI'26) が、アンビエント表示の
  知覚可能性を N=100 の別建てオンライン変化検出課題（96% 正答 vs 33.3% チャンス、p<.001）で
  事前検証し、本番の主要アウトカムは客観的行動指標（歩数・活動時間等）に置くという、
  求めている設計パターンの明確な実例。ただし発見できたのは実質 1 例のみ。
- **(e) 反証（必須）**: **判定不能（両論併存）**。作動水準（meta 分析の study 間比較）では
  「頻度・期間による有意な減衰」は確認できない（Karlin et al. 2015: frequency p=.624、
  duration 区分 p≈.076 で非単調）。Tiefenbeck 2018 も 2 か月間で減衰なし。他方、
  個体内の長期展開では対話行動が 9 割減る habituation が実測されている（Pereira et al. 2013）。
  ★ **「効果の消滅」と「関与・注視行動の消滅」は別物**であり、GSE への影響もこの区別に沿って
  評価すべき（§8 参照）。

## 4. 「何を測ってきたか」の内訳表（(a) の成果）

| 系統 | 標準的な主要アウトカム | 典型ソース | 定量内訳の有無 |
|---|---|---|---|
| 一般 ambient/peripheral display 評価 (HCI 伝統) | usability 系（学習容易性・エラー可視性・有用性・満足度）＋ attention 系（awareness・distraction） | Matthews, Hsieh & Mankoff 2009［一次確認］; Pousman & Stasko 2006［二次］; Hazlewood et al. 2011［二次］ | ★ **内訳の実数・割合を出した系統的レビューは未発見**（本レビュー内で確認できたのは「どの基準が使われてきたか」という定性的タキソノミーのみ） |
| eco-feedback / persuasive technology (エネルギー・水) | **実消費量（kWh・リットル）＝行動指標** | Karlin, Zinger & Ford 2015［一次確認、k=42 効果量、全て消費量ベース］; Fischer 2008［二次］; Kelly & Knottenbelt 2016［一次確認、k=12 研究］ | ○ Karlin 2015 は効果量 42 件中 35 件（83%）が正の効果、5 件（12%）が負、2 件（5%）がゼロと定量化。ただし**収集基準自体が「消費量を報告した研究」なので母集団内訳ではない** |
| 通知・アラート研究 (McCrickard 系フレームワーク) | interruption / reaction / comprehension の 3 パラメータを**設計者が目標として設定し、それに対して評価**（行動指標ではないが、comprehension を最終目的ではなく設計変数として扱う先例） | Matthews et al. 2009 内で紹介（McCrickard et al. 2003b, Matthews et al. 2007）［一次確認、孫引き］ | 定性のみ |
| スマホ利用時間・身体活動の新しい ambient display 研究 (2020 年代) | 客観行動指標（画面時間分・歩数・活動エネルギー） | Zheng, Seo & Choe 2025 (TIMER)［二次］; Jörke et al. 2026 (Bloom)［一次確認］ | 定性のみ（研究数が少なく統計不可） |

## 5. カード（落合フォーマット）

### カード A: Matthews, Hsieh & Mankoff (2009) "Evaluating Peripheral Displays" [検証済 3-0]

1. **どんなもの**: Awareness Systems (Springer, HCI シリーズ) 第 19 章。周辺ディスプレイ評価の
   タキソノミーと 2 ケーススタディを提示する review chapter。
2. **先行と比べてどこがすごい**: 個別評価技法の乱立を、「伝統的ユーザビリティ基準」
   （学習容易性・エラー可視性/回復・有用性・満足度）と「注意関連基準」（awareness・distraction）
   の 2 群に整理した。McCrickard らの notification-level 設計論（interruption/reaction/
   comprehension を設計目標として先に決め、それに対し評価する）も紹介する。
3. **手法の肝**: 過去の周辺ディスプレイ評価研究の文献横断整理＋自チームの 2 ケーススタディ
   （ヒューリスティック評価 → ラボ実験 → フィールド実験の 3 段階）。
4. **どう有効と検証したか**: レビュー章のため単独の効果検証はない。ただし列挙された基準は
   すべて出典（McCrickard, Mankoff, Zhang, Cadiz, Ho-Ching ら）付きで、行動変化を主要基準とした
   評価は列挙されていない（章内を全文検索して確認・不在を確認）。
5. **議論はあるか**: awareness の測定は「気づいたかを尋ねる」か「反応速度で間接測定する」かに
   割れており、著者ら自身が「awareness のデータ収集は難しい」「行動の変化は小さすぎて
   気づきにくい」と明言している（p.449 相当）。
6. **次に読むべき論文**: Pousman & Stasko (2006)、McCrickard et al. (2003b)（本チャプターが
   繰り返し引用する notification-level 設計論の一次ソース、本ラウンドでは孫引きに留まる）。

**GSE への含意**: 一般的な ambient display 評価の「相場」は行動ではなく awareness/distraction/
usability である。GSE が行動指標を主要アウトカムに据えるのは、この一般的相場からは**逸脱**であり、
「標準的」ではなく「隣接分野（eco-feedback）からの輸入」として位置づけるのが正確。

---

### カード B: Karlin, Zinger & Ford (2015) "The Effects of Feedback on Energy Conservation: A Meta-Analysis" [検証済 3-0]

1. **どんなもの**: Psychological Bulletin 141(6), 1205–1227。エネルギーフィードバック研究
   42 件（効果量 r）を対象にしたメタ分析。DOI: 10.1037/a0039650。
2. **先行と比べてどこがすごい**: 出版バイアス・研究の質・7 種のモデレータ（頻度・媒体・
   計測粒度・比較対象・介入併用・単位・期間）を体系的に検定した初の包括的メタ分析。
3. **手法の肝**: 固定効果・変量効果モデルの両方で主効果を算出し、モデレータはmixed-effects
   モデルで検定。出版バイアスは funnel plot 的な trim-and-fill に相当する手法で評価。
4. **どう有効と検証したか**: 主効果は加重平均 r=.0397（固定効果, p<.0001）/ r=.0754
   （変量効果, 95%CI [.0484, ...]）。42 効果量中 35 件（83%）が正、5 件（12%）が負、
   2 件（5%）がゼロ。**フィードバック頻度**（月次以下 8 件・週 1-4 回 8 件・日次 4 件・
   **連続 17 件**）は効果量の有意なモデレータではなかった（p=.624）。**フィードバック提供期間**
   区分（<1 か月・1-3 か月・3-6 か月・6-12 か月・12 か月超）も有意水準に届かず(概ね p≈.076)、
   かつ非単調（1-3 か月区分が r=.178 で最大、3-6/6-12 か月で r=.05 前後に下がり、12 か月超で
   r=.096 に再上昇）。
5. **議論はあるか**: 著者ら自身が「頻度は媒体と交絡しているため、この null 結果の解釈には
   注意が必要」と明言。また「continuous feedback は常時利用可能でも、電子的に提供される
   ため実際にはユーザーが**能動的に情報を取りに行く必要があり、たまにしかアクセスされない**」
   と指摘している（p.1492 相当）——これは常時稼働のアンビエント表現が「見られているとは
   限らない」という懸念と直結する。
6. **次に読むべき論文**: Delmas, Fischlein & Green (2013)（別系統の feedback メタ分析、本ラウンド未確認）。

**GSE への含意**: (1) 「連続的feedback＝ambient的な露出」は study 間レベルでは特別に減衰しやすい
わけではない（frequency は非有意）——GSEの常時稼働設計を頭ごなしに否定する根拠にはならない。
(2) ただし「常時見られる」ことと「実際に見られる」ことは別問題だと著者ら自身が釘を刺しており、
GSE の manipulation check（気づいたか）を行動指標と並置する設計は、この懸念に対する直接的な
防御策として位置づけられる。

---

### カード C: Tiefenbeck et al. (2018) "Overcoming Salience Bias: How Real-Time Feedback Fosters Resource Conservation" [検証済 2-1]

1. **どんなもの**: Management Science 64(3), 1458–1476。スイス 697 世帯を対象にした
   ランダム化統制フィールド実験。シャワー中の資源消費（水・エネルギー）にリアルタイム
   フィードバックを与える。DOI: 10.1287/mnsc.2016.2646。
2. **先行と比べてどこがすごい**: 世帯レベルの**集計**フィードバック（電気料金明細等、月次）
   ではなく、**個々の行動の瞬間**（シャワー中）に介入することで salience bias
   （顕著性バイアス）を是正するという因果メカニズムを提示し、697 世帯という規模と RCT
   デザインで検証した点。
3. **手法の肝**: 装置は amphiro a1 スマートシャワーメーター。**表示要素は数値（リットル・
   温度・kWh・A〜G の効率レーティング）とアイコン的アニメーション（消費が増えるほど縮む
   氷山＝シロクマ演出）の両方を含むハイブリッド**。統制群は水温のみ表示。
4. **どう有効と検証したか**: リアルタイムフィードバック群は統制群比でエネルギー・水消費
   ともに **22% 減**（エネルギーで 0.59kWh/回、水で 9.5L/回）。世帯当たり 1.2kWh/日の節約は
   照明の平均使用量を上回る規模。★ **効果は 2 か月間の観察期間を通じて持続し、"no visual
   tendency for the gap between [conditions] to narrow" と明記**——観察された範囲では
   減衰（novelty effect）は確認されなかった。
5. **議論はあるか**: 著者ら自身が参加世帯の**自己選択バイアス**（一般母集団より若く都市的）
   を認めている。同グループの後続研究 Tiefenbeck, Wörner, Schöb, Fleisch & Staake (2019,
   Nature Energy, DOI: 10.1038/s41560-018-0282-1)「Real-time feedback promotes energy
   conservation in the absence of volunteer selection bias and monetary incentives」は
   まさにこの批判に応える追試だが、★ **本ラウンドでは書誌情報のみ確認、本文は認証リダイレクト
   により未取得**（二次資料水準にも届かず、存在確認のみ）。
6. **次に読むべき論文**: 上記 Tiefenbeck et al. (2019, Nature Energy)。

**GSE への含意**: 「点介入・実時間・行動指標」という設計思想は GSE の常時アンビエント表現と
親和的だが、★ **この研究の表示は数値情報が主体でアイコン演出は補助的要素に過ぎず、
「周辺視野的・非侵入的」な純アンビエント表示の効果として引用するのは過大解釈になる**。
GSE が引用する際は「ハイブリッド」であることを明記すべき。

---

### カード D: Pereira, Quintal, Barreto & Nunes (2013) "Understanding the Limitations of Eco-feedback: A One-Year Long-Term Study" [検証済 2-1]

1. **どんなもの**: HCI-KDD 2013 (LNCS 7947, pp.237–255)。ポルトガルの 12 世帯に
   非侵入型負荷モニタリング(NILM)＋エコフィードバックシステムを 52 週間展開した長期研究。
2. **先行と比べてどこがすごい**: エコフィードバック研究の大半が短期（数週間〜数か月）で
   終わる中、丸 1 年間の展開データを取得した数少ない研究。
3. **手法の肝**: 家庭内センサーで実消費量を継続計測し、あわせてシステムとの対話ログ
   （ログイン・閲覧頻度）と事後インタビューで主観的な awareness を調べる縦断デザイン
   （統制群なし、単群前後比較に近い）。
4. **どう有効と検証したか**: 52 週間で世帯の**電力消費量には有意な増減が見られなかった**。
   一方、**システムとの対話（利用行動）は週あたり約 2.2% ずつ減少し、1 年でほぼ 90% 減少**
   した。同時にインタビューでは電力消費への**主観的な気づき（awareness）は増加した**と
   報告されている——「気づきは上がったが対話も消費行動も変わらない/減った」という乖離。
5. **議論はあるか**: N=12・統制群なしという小規模デザインであり、季節変動や世帯構成の
   変化（本文でも触れられている）を消費量の交絡因子として排除できていない。著者ら自身が
   「先行研究の多くは短期のため長期的にどう振る舞うか知見が乏しい」とギャップを指摘している。
6. **次に読むべき論文**: Fischer (2008)（frequency/duration のモデレータ議論の理論的背景）。

**GSE への含意**: 「理解（気づき）」と「行動」が乖離しうるという GSE の仮説を**弱く支持**する
数少ない実測例。ただし N=12・統制群なしのため確定的な証拠ではなく、**個人内で理解度スコアと
行動変化を直接相関させた研究ではない**（気づきは事後インタビューの定性報告、行動は世帯単位の
消費量ログという異なる粒度の指標の並置に留まる）。

---

### カード E: Jörke et al. (2026, CHI) "Bloom: Designing for LLM-Augmented Behavior Change Interactions" [検証済 2-1]

1. **どんなもの**: CHI 2026 採択論文（arXiv:2510.05449）。UbiFit にインスパイアされた
   「庭が育つ」アンビエント表示＋ LLM 会話コーチを組み合わせた身体活動支援システム "Bloom" の
   4 週間・N=54・被験者間ランダム化フィールド実験。
2. **先行と比べてどこがすごい**: ★ 本 RQ が求めていた設計パターン——**アンビエント表示の
   知覚可能性（perceptibility）を、本番の行動アウトカム評価とは別建てで、事前に
   manipulation check 的に検証する**——を明示的に実施している数少ない実例。
3. **手法の肝**: 本番実験の前に、**N=100 のオンライン参加者による変化検出課題**を実施。
   庭の画像を 5 秒→ 2 秒で 2 枚提示し、進行/後退/同一を判定させる。混合効果ロジスティック
   回帰で検出率 96%（オッズ 3.28±0.23）を算出し、チャンスレベル 33.3% を有意に上回ることを
   確認（Wald z=17.3, p<.001；画像ペアごとの Holm 補正ブートストラップ検定でも有意）。
   この検証は「アンビエント表示が意図通り機能するか」という**前提条件**として位置づけられ、
   本番実験の主要アウトカムではない。
4. **どう有効と検証したか**: 本番実験（N=54, 4 週間, LLM 群 vs no-LLM 統制群、統制群にも
   アンビエント庭表示は残る設計と読める）の主要アウトカムは Apple HealthKit 由来の客観的
   身体活動指標（歩数・消費カロリー・運動時間・歩行距離）。両群ともベースラインから有意に
   改善（H1 確認、d=0.59〜0.75）したが、**LLM 群と統制群の間の差は統計的に非有意**
   （群間差 H2: p=.78–1.0、変化率の群間差 H3: p=.77–1.0、著者ら自身が探索的研究であり
   検出力不足と明記）。
5. **議論はあるか**: (i) 知覚可能性の pretest はオンラインの静止画 2 枚比較課題であり、
   実際の「ながら見」的なアンビエント視認条件を模したものではない——**注視課題に近く、
   周辺視野的な条件での知覚可能性を保証するものではない**という外的妥当性への疑義が残る。
   (ii) 本番実験は LLM コーチの有無を比較しており、アンビエント表示単体 vs 無表示の比較では
   ない（両群にアンビエント庭がある可能性が高い）ため、**アンビエント表示それ自体の行動効果を
   直接示す証拠にはならない**。
6. **次に読むべき論文**: Jörke et al. が参照する Murnane et al.（変化検出課題の手法的source、
   本ラウンド未確認）。

**GSE への含意**: 「知覚可能性は事前検証、主要アウトカムは客観的行動指標」という GSE の
方針転換とほぼ同型の設計が 2026 年時点で実例として存在する——**先行ゼロではない**。
ただし (i) knowledge-check の妥当性（オンライン注視課題でよいか）と (ii) 行動面での群間差が
非有意だった点は、そのまま GSE への警句として使える：**知覚可能性を確認しても、それだけで
行動指標での有意差が出るとは限らない**。

---

### カード F: Kelly & Knottenbelt (2016) "Does disaggregated electricity feedback reduce domestic electricity consumption? A systematic review" [検証済 3-0（方法論的注意喚起として）]

1. **どんなもの**: 3rd International NILM Workshop (2016) 発表、arXiv:1605.00962。
   詳細分解型（家電別）フィードバック 12 研究の系統的レビュー。
2. **先行と比べてどこがすごい**: 「詳細な内訳を見せれば効果が上がる」という業界通念に対し、
   集計フィードバックとの直接比較を行った 4 研究すべてで「集計フィードバックは詳細分解型と
   少なくとも同等」という反直観的な結果を報告。
3. **手法の肝**: 12 研究の効果量（平均 4.5% 減）を単純に平均するのではなく、
   **全 12 研究が「志願者(opt-in)バイアス」を免れていない**ことを明示し、母集団への
   一般化可能性に疑義を呈する構成。
4. **どう有効と検証したか**: 平均 4.5% 減（12 研究）だが、著者は「一般母集団への外挿としては
   楽観的すぎる推定」と自己批判。詳細分解の追加効果は「一部の "energy enthusiast" 層にのみ
   効くかもしれない」と留保。
5. **議論はあるか**: 系統的レビューとしての厳密性（PRISMA 等）は限定的（5 ページの
   ワークショップ論文）。
6. **次に読むべき論文**: Fischer (2008)。

**GSE への含意**: eco-feedback 系研究全般に共通する**自己選択バイアス**の構造的懸念を補強する。
GSE のパイロット参加者も志願制である以上、Tiefenbeck 2018 やカード B の効果量を
「一般ユーザーでも同様に出る」と単純に外挿しない注意が必要。

## 6. 登録候補一覧

| 仮 key | 出典 | N | 設計 | 効果量 | 主要アウトカムの種類 | 確認水準 |
|---|---|---|---|---|---|---|
| prov-matthews2009 | Matthews, T., Hsieh, G., & Mankoff, J. (2009). Evaluating Peripheral Displays. In *Awareness Systems* (HCI Series), pp.447–472. Springer. DOI: 10.1007/978-1-84882-477-5_19 | — (review) | タキソノミー＋2 ケーススタディ | N/A | 主観評価／理解度（レビュー対象基準の総称） | 一次確認済み |
| prov-pousman2006 | Pousman, Z., & Stasko, J. (2006). A Taxonomy of Ambient Information Systems: Four Patterns of Design. *AVI 2006*. | — | タキソノミー | N/A | 理解度（interruption/reaction/comprehension） | 二次資料水準 |
| prov-hazlewood2011 | Hazlewood, W. R., Stolterman, E., & Connelly, K. (2011). Issues in evaluating ambient displays in the wild: two case studies. *CHI 2011*. DOI: 10.1145/1978942.1979071 | 2 ケーススタディ | フィールド評価 | N/A | 主観評価／理解度 | 二次資料水準 |
| prov-karlin2015 | Karlin, B., Zinger, J. F., & Ford, R. (2015). The Effects of Feedback on Energy Conservation: A Meta-Analysis. *Psychological Bulletin, 141*(6), 1205–1227. DOI: 10.1037/a0039650 | k=42 効果量 | メタ分析 | r=.0397(固定)/.0754(変量) | **行動指標**（実消費量） | 一次確認済み |
| prov-tiefenbeck2018 | Tiefenbeck, V., Goette, L., Degen, K., Tasic, V., Fleisch, E., Lalive, R., & Staake, T. (2018). Overcoming Salience Bias. *Management Science, 64*(3), 1458–1476. DOI: 10.1287/mnsc.2016.2646 | N=697 世帯 | RCT（統制群あり） | 22% 減（p<.05 相当、統制群比） | **行動指標**（実消費量、ハイブリッド数値+アイコン表示） | 一次確認済み |
| prov-tiefenbeck2019 | Tiefenbeck, V., Wörner, A., Schöb, S., Fleisch, E., & Staake, T. (2019). Real-time feedback promotes energy conservation in the absence of volunteer selection bias and monetary incentives. *Nature Energy, 4*(1), 35–41. DOI: 10.1038/s41560-018-0282-1 | 未確認 | 未確認（志願バイアス排除を標榜） | 未確認 | 行動指標（推定） | ★ 書誌のみ確認・本文未取得（provisional） |
| prov-kuznetsov2010 | Kuznetsov, S., & Paulos, E. (2010). UpStream: Motivating water conservation with low-cost water flow sensing and persuasive displays. *CHI 2010*. DOI: 10.1145/1753326.1753604 | 4 世帯（3 週間） | アンビエント vs 数値表示比較 | 定性（アンビエントの方が「効いた参加者が多かった」） | 行動指標（水使用量） | 二次資料水準 |
| prov-kappel2009 | Kappel, K., & Grechenig, T. (2009). "Show-me": Water consumption at a glance to promote water conservation in the shower. *Persuasive 2009*. | 小規模 | LED アンビエント表示 | 定性 | 行動指標（自己申告含む） | 二次資料水準 |
| prov-kluckner2010 | Kluckner, P. M., et al. (2010). Ambient Persuasive Technology Needs Little Cognitive Effort: The Differential Effects of Cognitive Load on Lighting Feedback versus Factual Feedback. *Persuasive 2010*. | 実験室実験 | 認知負荷操作×フィードバック種別 | 定性（光フィードバックの方が認知負荷に頑健） | 主観評価／処理過程 | 二次資料水準 |
| prov-kluckner2013 | Kluckner, P. M., et al. (2013). Making it not too obvious: The effect of ambient light feedback on space heating energy consumption. *Personal and Ubiquitous Computing*. | 未確認 | フィールド | 未確認 | 行動指標（暖房エネルギー） | 二次資料水準 |
| prov-pereira2013 | Pereira, L., Quintal, F., Barreto, M., & Nunes, N. J. (2013). Understanding the Limitations of Eco-feedback: A One-Year Long-Term Study. *HCI-KDD 2013, LNCS 7947*, 237–255. | N=12 世帯 | 単群縦断（52 週間） | 消費量: 有意差なし／対話行動: 週2.2%減(52週で約90%減) | **乖離**（awareness↑・行動→不変） | 二次資料水準 |
| prov-zheng2025 | Zheng, J., Seo, S., & Choe, E. K. (2025). From Awareness to Action: Ambient Display and Customizable Attention Signals for Self-regulated Smartphone Usage. *IMWUT*. DOI: 10.1145/3749507 | N=41 | 単群 3 週間（週ごとに条件付加、統制群なし） | 画面時間 -38分(10.7%)→ 追加で-32分(9.0%) | 行動指標（画面時間） | 二次資料水準 |
| prov-lin2006 | Lin, J. J., Mamykina, L., Lindtner, S., Delajoux, G., & Strub, H. B. (2006). Fish'n'Steps: Encouraging Physical Activity with an Interactive Computer Game. *Ubicomp 2006*. | N=19 | 統制群なし・14 週間 | 歩数（定性的解釈、TTM ステージ） | 行動指標（自己申告寄り） | 二次資料水準 |
| prov-fischer2008 | Fischer, C. (2008). Feedback on household electricity consumption: a tool for saving energy? *Energy Efficiency, 1*, 79–104. | レビュー | 定性レビュー | 5–20% (レビュー内推定レンジ) | 行動指標（一般論） | 二次資料水準 |
| prov-kelly2016 | Kelly, J., & Knottenbelt, W. (2016). Does disaggregated electricity feedback reduce domestic electricity consumption? A systematic review of the literature. arXiv:1605.00962 | k=12 研究 | 系統的レビュー | 平均 4.5%減（opt-in バイアス注記） | 行動指標 | 一次確認済み |
| prov-jorke2026 | Jörke, M., et al. (2026). Bloom: Designing for LLM-Augmented Behavior Change Interactions. *CHI 2026*. arXiv:2510.05449 | pretest N=100／本実験 N=54 | pretest: 変化検出課題／本実験: 4週間 RCT | pretest 96% vs chance 33.3%(p<.001)／本実験 群間差非有意(H2/H3 p>.7) | **知覚可能性は前提条件として個別検証、主要アウトカムは行動指標** | 一次確認済み |

## 7. 否決リスト

- ⚠️ **否決**: 「Fish'n'Steps は行動変化を統制された形で実証した」（C4）— 統制群なし・N=19・
  自己申告寄りの解釈（Transtheoretical Model のステージ推定）であり、3 票中 1-2 で否決。
  独立した強い再現もない。UbiFit 以外の「弱い」先行例として登録候補には残すが、
  エビデンスとしては採用しない。
- ⚠️ **保留（3 票にかけず判定不能のまま）**: 「salience bias 補正メカニズムは"気づき"を
  行動変化の必要条件として要求している」（C6）— Tiefenbeck 2018 の理論的主張の解釈であり、
  個人レベルで気づきと行動変化の相関を直接検定した分析は同論文内に存在しないため、
  claim として確定させず留保にとどめた。

## 8. 結論

★ **GSE の方針転換（可読性→manipulation check への降格／行動指標を主要アウトカムに）という
「形」は、(ii) 前例はあるが少数、に該当する。** 一般的な ambient/peripheral display 評価の
学術的伝統（Matthews 2009 / Pousman & Stasko 2006 系譜）は今も awareness・distraction・
usability を主軸としており、GSE の転換はこの伝統からの逸脱である。しかし隣接分野
（eco-feedback / persuasive technology、および 2025-2026 年の新しい ambient+行動変化研究）
には、(1) 行動指標を主要アウトカムに据えた統制研究が複数存在し（Tiefenbeck 2018 が最強例、
ただしハイブリッド表示という留保付き）、(2) 知覚可能性を manipulation check 的に前提条件として
切り出す設計（Jörke et al. 2026, Bloom）も直近の実例として確認できた。★ **「先行ゼロ」ではなく、
「eco-feedback／持続的行動変化という隣接分野からの輸入として正当化できる」という位置づけが
最も正確**である。

(e) の反証角がどう効くか: novelty effect への懸念は**部分的に効き、部分的には効かない**。
study 間レベルの meta 分析（Karlin 2015）や 2 か月の RCT（Tiefenbeck 2018）では
「頻度・期間による有意な効果減衰」は確認されておらず、GSE の常時稼働設計を理由に
「どうせ数か月で効かなくなる」と早合点する根拠はない。他方、52 週間の長期展開研究
（Pereira 2013、小規模だが唯一の長期データ）では**対話・関与行動そのものが 9 割近く
減少**しており、これは「効果が消える」というより「**見なくなる**」という別種のリスクである。
GSE の表現層が生き残るには、行動指標そのものの持続性だけでなく、**表現に対する注視・関与が
長期的に維持されるか**を独立に測る必要がある——これはまさに manipulation check を
一回限りでなく継続的な健全性チェックとして設計すべき理由になる。

## 9. やり残し

- ★★★ **個人内で「理解度（可読性スコア）」と「行動変化量」を直接相関させた研究**は
  本ラウンドで発見できなかった。これが見つかれば (c) の温度を大きく引き上げられる。
  次ラウンドでは "comprehension accuracy" AND "behavior change" AND correlation/individual-level
  という角度、および health literacy 分野（ヘルスリテラシーと服薬行動など、乖離が
  よく研究されている隣接領域）を探索すべき。
- Tiefenbeck et al. (2019, Nature Energy) の本文が未取得（認証リダイレクトで阻まれた）。
  志願者バイアスを排除した追試の詳細（N・効果量・持続性）を次ラウンドで確認する価値が高い。
  ETH Zurich リサーチコレクション (http://hdl.handle.net/20.500.11850/294409) が 403 を返した
  ため、別ルート（Sci-Hub は使用不可、著者のホームページや ResearchGate 経由）を試すこと。
- Kluckner et al. の 2 本（2010 Persuasive、2013 PUC）は要約止まり。特に 2013 年論文の
  N・統制の有無・効果量を一次確認できれば、(b) の「純アンビエント（数値表示を伴わない光のみ）」
  の実例として C3（Tiefenbeck）のハイブリッド性への留保を補強できる。
- 系統的レビューで「ambient display 研究全体の中で、主要アウトカムを可読性/理解度に
  置いた研究と行動指標に置いた研究の比率」を直接報告したものは見つからなかった。
  §4 の内訳表はあくまで定性的な系統分類であり、定量的な census ではない。この census
  自体を目的にした探索（例: "systematic review" + "ambient display" + "outcome measures"
  + 集計）を次ラウンドの候補にする。
- health/activity tracker 分野の novelty effect に関する系統的レビュー（web 検索で
  "Beyond novelty effect" などの断片は見えたが未精読）を次ラウンドで一次確認すること。
