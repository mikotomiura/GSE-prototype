# novelty-a3 報告（angle 3: 本人の動き・打鍵・生体のリズムを写す背景・環境の表示）

## 結論（下位の問いごと）
- (a) 本人の打鍵・行動・生体のリズムでリアルタイムに動く背景・環境の表示は既にあるか: **近いものは見つかった（完全一致は見つからなかった）**。KeyStrokes（打鍵リズムを写すリアルタイム可視化だが、背景ではなく「送る文面の絵」）、UbiFit Garden（自分の行動で育つ壁紙だが、スマホの待受で、打鍵のリアルタイムではなく1日単位）、Brombacher 2020（PC 操作を写すデスクトップのアンビエント表示。リアルタイム性・背景全面かは未確認）、Moraveji 2011（画面端の呼吸ガイド。本人の信号を写すのではなく外から与える）。デスクトップ背景全面が打鍵リズムで動き続ける研究は、この範囲で見つからなかった。
- (b) 自己を写す表示を状態計として読んだか・表示のために行動を変えたか（ゲーム化・反応性）を測った研究: **この範囲で見つからなかった**。UbiFit は「flowers が欲しくて動機づけられた」と語る参加者はいるが、状態計として読んだかを直接問うていない。表示を動かすために行動を変えたか（水増し）を測ってはいない。
- (c) 作業中に背景・周辺で動き続ける表示の注意の代償を測った研究: **見つかった（ただし自分の状態を写す表示ではない）**。Plaue & Stasko 2007（アニメーションの周辺表示）が主観の邪魔さと課題成績を測っている。
- (d) 同じ表示で、作業中の代償と中断後の再着手を分けて測った研究: **この範囲で見つからなかった**。

GSE の空白の主張への見立て: 反証側の決定的な証拠は無かった。ただし「近い先行」として KeyStrokes、UbiFit、Brombacher 2020、Plaue & Stasko 2007 は言及して差分を述べる必要がある。「前例がない」とは書けず、「打鍵リズムを背景全面に写し、状態計として読まれたか・ゲーム化を測った一次は、この調査の範囲で見つからなかった」までが言える。

## 見つけたソース

### 1. KeyStrokes（(a) に近い）
- Neumann, P., Tat, A., Zuk, T., Carpendale, S. (2007). KeyStrokes: Personalizing Typed Text with Visualization. Eurographics/IEEE-VGTC Symposium on Visualization (EuroVis 2007), pp. 43-50. DOI: 10.2312/VisSym.EuroVis07.043-050（DL ページ diglib.eg.org/handle/10.2312/VisSym.EuroVis07.043-050。DOI は検索結果の URL から。DL ページ自体は 403 で未取得）。本文 PDF: https://petra.isenberg.cc/publications/papers/Neumann_2007_KPT.pdf（全 8 頁を pypdf で読んだ）。
- 内容: 打鍵の速さ・リズム・手の使い方・消去や打ち直しを使い、入力中の文面から絵をリアルタイムに生成する。出力は、電子ポストカードのように後から送る「絵」。
- 評価: 二つの学会のデモで 68 人（InfoVis'06 37 人・CSCW'06 31 人）が紙の質問票に答えた。4 時間のデモ、参加者が自分で 1 通打って絵を印刷し、任意で回答。質問は個性を捉えるか・使いたいかなど。作業中の使用・行動変化・注意の代償は測っていない。
- 逐語（抄録）: "we introduce an artistic real-time visualization of typed messages that additionally captures and encodes aspects of an individual's unique typing style."
- 逐語（本文 4.2）: "We collected responses to this visualization through a questionnaire given out in paper form at two conference demonstration sessions."
- 下位の問い: (a) に部分的に当たる（打鍵リズムのリアルタイム可視化）。(b)(c)(d) は当たらない。
- 崩すか: 崩さない。背景ではない・自己の状態計でもない・作業中でもない。ただし「打鍵リズムをリアルタイムに視覚化した先行」として引く必要がある。
- 付随: 同著者の予備稿 Neumann et al. 2006 "Visualization of Typed Communication"（petra.isenberg.cc/publications/papers/Neumann_2006_VTC.pdf）がある。読んでいない。

### 2. UbiFit Garden（(a)(b) に部分的）
- Consolvo, S., McDonald, D. W., Toscos, T., Chen, M. Y., Froehlich, J., Harrison, B., Klasnja, P., LaMarca, A., LeGrand, L., Libby, R., Smith, I., Landay, J. A. (2008). Activity Sensing in the Wild: A Field Trial of UbiFit Garden. CHI 2008. 本文 PDF: https://makeabilitylab.cs.washington.edu/media/publications/Consolvo_ActivitySensingInTheWildAFieldTrialOfUbifitGarden_CHI2008.pdf（pypdf で読んだ。著者名は検索結果の記憶ではなく未突合の部分があるので、書誌登録前に確認が必要）。
- 設計: 12 人・3 週間のフィールド試行。センサで推定した活動に応じて庭の花が咲く。
- 逐語（抄録）: "We conducted a 3-week field trial in which 12 participants used the system and report findings focusing on their experiences with the sensing and activity inference."
- 逐語（本文）: "The glanceable display uses a non-literal, aesthetic representation of physical activities and goal attainment to motivate behavior (Fig 1). It resides on the background screen, or "wallpaper," of a mobile phone"
- 逐語（参加者）: "It's right there on your wallpaper so every time you pick up your phone you are seeing it and you're like, 'Oh, look at this. I have all those flowers. I want more flowers.'"
- 3 か月・28 人の別の実験（Consolvo et al. 2008, "Flowers or a robot army?" UbiComp 2008, DOI 10.1145/1409635.1409644 は検索結果による）では、庭の表示がある群は活動を保った。これは検索結果の要約のみで、原文は読んでいない。
- 下位の問い: (a) 自分の行動で変わる壁紙（ただし頻度は日単位、スマホ）。(b) 動機づけられたという自由回答はあるが、状態計として読んだか・水増ししたかは測っていない。
- 崩すか: 部分的に近い。「自分を写す壁紙が行動を変える」ことを示した前例として必ず引く。GSE の差は、打鍵リズムの秒単位・PC の背景全面・作業の状態の計器として読んだか。
- 付随: Fish'n'Steps（Lin et al. UbiComp 2006）は 14 週・19 人でゲーム化による運動促進。抄録の要約を検索で見ただけで原文は読んでいない。これは「表示のために行動を変える」（ゲーム化）が意図された設計であり、(b) の反対側の例。

### 3. Brombacher et al. 2020（(a) に最も近い可能性。要確認）
- Brombacher, H., Ren, X., Vos, S., Lallemand, C. (2020). Visualizing Computer-Based Activity on Ambient Displays to Reduce Sedentary Behavior at Work. OzCHI 2020, pp. 760-764. DOI: 10.1145/3441000.3441022（出版社ページの掲載情報 pure.bit.edu.cn で確認）。
- 設計: デスクトップ上のアンビエント表示 2 つ（Yamin, Apphia）。16 人の事務職による探索的な質的ラボ研究。
- 結果（逐語ではなく要約。WebFetch が逐語を出さなかった）: PC 活動の可視化は、気づき・自己省察・社会的相互作用を高めうる。
- 未確認: 打鍵をリアルタイムに使うか・背景全面か・表示のために行動を変えたか。本文は読んでいない（有料の可能性があり未取得）。
- 下位の問い: (a)(b) に当たる可能性。
- 崩すか: 要確認。本文を入手して、表示の中身とリアルタイム性を確かめるべき。最優先の追跡対象。

### 4. Plaue & Stasko 2007（(c) に当たる）
- Plaue, C., Stasko, J. (2007). Animation in a Peripheral Display: Distraction, Appeal, and Information Conveyance in Varying Display Configurations. Graphics Interface 2007, pp. 135-142. DOI: 10.1145/1268517.1268541（検索結果による。題名はスライドの表紙から確認）。スライド: https://sites.cc.gatech.edu/gvu/ii/talks/gi07.pdf（pypdf で読んだ。本文は読んでいない）。
- 設計: BlueGoo（RSS ニュースを動く写真のコラージュにする）。タイマー付き監視課題を主課題にし、表示の大きさ・位置を変えた。N は未確認。
- 逐語（スライド）: "Angled displays result in higher self-reported distractions"、"Low subjective ratings for distraction along with any significant difference in task completion time"
- 下位の問い: (c) に当たる（動き続ける周辺表示の邪魔さ）。ただし本人の状態を写す表示ではない。(d) は測っていない。
- 崩すか: (c) の「注意の代償が測られていない」という主張は崩す。「動く周辺表示の代償は測られているが、自己を写す表示では測られていない」と書く。

### 5. Moraveji et al. 2011（(a) に関連）
- Moraveji, N., Olson, B., Nguyen, T., Saadat, M., Khalighi, Y., Pea, R., Heer, J. (2011). Peripheral Paced Respiration: Influencing User Physiology during Information Work. UIST 2011. DOI: 10.1145/2047196.2047250（検索結果による）。hci.stanford.edu/publications/paper.php?id=186 で題名・著者・会議を確認。抄録と N は取得できなかった。
- 内容（検索要約）: 画面端に呼吸ガイドを置き、作業中の呼吸数が下がった。本人の信号を写すのではなく、外から与える。
- 下位の問い: (c) 作業中の周辺表示。(d) は測っていない。崩すか: 崩さない。

### 6. 生体のアンビエント表示（読んでいない）
- DeLight（Yu et al. 2018, Personal and Ubiquitous Computing, DOI 未確認。URL: https://www.drhu.eu/publications/2018-PUC-DeLight.pdf）: HRV を環境光で示す。検索要約では、ストレスの気づきを高めた。作業中ではなくリラックスのセッション。本文は読んでいない。
- Inner Flower（Hamon et al. 2018, arXiv 1808.08711）: 周辺モードは集中モードより弱い。検索要約のみ。
- Heartscape は検索で出なかった。

## 使った検索語（英語・日本語）
KeyStrokes Visualizing typing EuroVis 2007 / ambient display own physical activity self-monitoring UbiFit glanceable / ambient biofeedback display heart rate breathing wallpaper peripheral work / typing rhythm real-time visualization generative art desktop background / Neumann Tat Zuk Carpendale KeyStrokes user study / Peripheral paced respiration Moraveji / peripheral ambient display distraction attention cost / Fish'n'Steps / ambient display reactivity gaming participants changed behavior / キーストローク 打鍵 リアルタイム 可視化 作業環境 背景 自己状態 アンビエント / ambient display typing activity wallpaper focus / Heartscape biofeedback ambient wall / animated desktop background wallpaper attention resumption / Brombacher computer-based activity ambient / Plaue Stasko animation peripheral display。

## 限界
- 25 分の範囲で、日本語の検索は 1 回だけ（成果なし）。
- 「self-monitoring の reactivity（Hawthorne 的な行動変化）」は健康心理学の語彙で、HCI の検索では当たらなかった。心理学側（self-monitoring reactivity の総説）は探していない。反証側の取りこぼしがありうる。
- 次に探すなら: (1) Brombacher 2020 の本文、(2) Hamon 2018 / Yu 2018 の本文、(3) self-monitoring reactivity の総説、(4) Wallpaper Engine や音楽ビジュアライザ（オーディオ連動の背景）を研究として扱ったもの、(5) 割り込み後の再着手（resumption lag）と周辺表示を併せて測った研究。
- 保存した一時ファイル: (temporary work area, removed)\ks.pdf と ks.txt（KeyStrokes 本文）。リポジトリは編集していない。
