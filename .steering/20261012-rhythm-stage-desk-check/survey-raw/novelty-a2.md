# novelty angle 2 報告 (ambient / peripheral display の連続アニメーションと主課題の代償)

## 下位の問い別の結論
- (a) 本人の打鍵・行動・生体のリズムでリアルタイムに動く背景・環境の表示: **この範囲で、打鍵リズムで動くデスクトップ背景の評価研究は見つからなかった。** 近い作品はある（下記 A1〜A3）が、いずれも背景の全面ではなく、打鍵リズムではなく、作業中の代償を測っていない。
- (b) 自己を写す表示を状態計として読んだか・表示のために行動を変えたか: **部分的に見つかった**（Brombacher 2020 が PC 活動の可視化への自己省察を質的に報告、Kim 2016 TimeAware が 8 週間・N=24 で生産性の変化を報告）。ただし「ゲーム化・反応性」を主題に測ったものではない。
- (c) 作業中に周辺で動き続ける表示の注意の代償: **見つかった**（Maglio & Campbell 2000、Somervell 2002、Plaue & Stasko 2007 ほか）。ただし全面の背景ではなく、小さなティッカー・グラフ・別モニタ上のコラージュ。
- (d) 同じ表示で作業中の代償と中断後の再着手を分けて測った研究: **この範囲で見つからなかった。**

総評: 「背景の全面が動き続ける表示を作業中に評価した研究は 0 件」を覆す直接の証拠は見つからなかった。ただし (c) は 2000 年代に十分蓄積があり、「連続アニメーションの代償」自体を空白と主張するのは危険。空白として言えるのは、本人の打鍵リズムで駆動される全面背景、および (d) の組み合わせに限られる。

## 見つかったソース

### S1. Maglio & Campbell 2000（(c) に当たる。全文を取得して確認）
- 書誌: Paul P. Maglio, Christopher S. Campbell. "Tradeoffs in Displaying Peripheral Information." CHI 2000 (The Hague), 1-6 April 2000. DOI は未確認。PDF: https://www.interruptions.net/literature/Maglio-CHI00-p241-maglio.pdf（p.241 とファイル名にある）
- 設計: 主課題はテキスト編集、副課題は 1 行のティッカーの見出し監視（ティッカー有り/無しの 2 局面）。Experiment 1 の参加者は本文で「Twenty-nine participants … IBM Almaden Research Center」。指標は編集での修正数と事後の再認テスト。
- 結果: 連続スクロールの方が start-stop より編集成績を悪化させた（本文 t(13)=2.46, p=0.014）。
- 逐語（抄録）: "continuously scrolling displays are more distracting than displays that start and stop, but information in both is remembered equally well."
- 判定: (c) に直接当たる。編集という主課題で連続動きの代償を測った古典。ただしティッカーであり背景全面ではない。GSE の主張を崩すというより、「連続的な動きは代償がある」という先行の根拠として引ける。登録済みか未確認（references.md は行が長く出力が省略されたため照合できなかった。要照合）。

### S2. Somervell, Chewar, McCrickard 2002（(c)）
- 書誌: "Evaluating Graphical vs. Textual Displays in Dual-Task Environments." Virginia Tech（HCIC 2002 とファイル名 somervell-hcic02 にある。会議名・頁は PDF 本文からは未確認）。PDF: https://people.cs.vt.edu/mccricks/papers/somervell-hcic02.pdf
- 設計: 疑似の負荷モニタをグラフ表示とテキスト表示で比較する二重課題。主課題は単純なブラウジング。N は未確認（読み切っていない）。
- 逐語（抄録）: "significant differences in display facilitation of information awareness, communication, and introduction of distraction."
- 逐語（結論）: "The simple browsing task … does not demand high attention from the participant; unlike other tasks such as editing or searching."（著者自身が編集課題には当てはまらないと限定）
- 判定: (c)。主課題が軽い点で GSE の文脈（執筆・コーディング）と距離がある。検索結果の要約には「グラフ表示が主課題に悪影響」とあったが、本文でその文言は確認していない（読んでいない）。

### S3. Plaue & Stasko 2007（(c)）
- 書誌: Christopher Plaue, John Stasko. "Animation in a peripheral display: distraction, appeal, and information conveyance in varying display configurations." Graphics Interface 2007, Montréal, pp.135-142. DOI 10.1145/1268517.1268541。https://graphicsinterface.org/?p=4869
- 設計: BlueGoo（RSS を動く写真コラージュにする周辺表示）、主課題はウェブ閲覧＋時間つきの監視課題。表示の大きさ・位置・見る動機を変えた。N はページに記載なし（未確認）。
- 逐語（抄録）: "participants did not find the system to be distracting, and many found it to be appealing."　斜め置きの第 2 モニタ上の動きは他 3 配置より気を散らした。
- 判定: (c)。連続アニメーションの周辺表示で「気を散らさない」とした側の根拠で、GSE の「代償がある」という前提の反証になりうる（代償の有無は条件しだい）。ただし別モニタ上で、本人の行動で駆動されない。主課題の成績を測ったかは抄録からは未確認。

### S4. Brombacher, Ren, Vos, Lallemand 2020（(a)(b)）
- 書誌: "Visualizing computer-based activity on ambient displays to reduce sedentary behavior"（題の末尾は検索結果の URL 由来で、正確な題は未確認）。OzCHI 2020（32nd Australian Conference on HCI）pp.760-764, DOI 10.1145/3441000.3441022。https://orbilu.uni.lu/handle/10993/45724 、https://hansbrombacher.myportfolio.com/yamin-and-apphia
- 設計: デスクトップ上の環境表示 Yamin と Apphia が本人の PC 活動を可視化。ラボでの探索的な質的研究、N=16 の事務職。
- 逐語（抄録）: "visualizing one's computer-based activity could potentially increase the awareness, self-reflection, and social interactions for individuals to become physically active."
- 判定: (a)(b) に最も近い。ただし (1) 駆動する量は PC 利用の総量で打鍵リズムではない可能性が高い（本文未読）、(2) 目的が運動の促進で作業の代償は測っていない、(3) 背景全面か未確認。抄録のみ。

### S5. Kim et al. 2016 TimeAware（(b)）
- 書誌: Kim, Y.-H. ほか（著者全員は未確認）. "TimeAware: Leveraging Framing Effects to Enhance Personal Productivity." CHI 2016. DOI は未確認。https://terpconnect.umd.edu/~choe/download/CHI-2016-Kim-TimeAware.pdf
- 設計: メニューバーの ambient widget ＋ウェブのダッシュボード、8 週間・N=24。
- 逐語（抄録）: "only participants in the negative framing condition improved their productivity." および "the ambient widget seemed to help sustain engagement with data and enhance self-awareness."
- 判定: (b)。自己の PC 利用を周辺表示で返し、行動が変わったことを測った。ただし背景全面でも打鍵リズムでもない。抄録のみ。

### S6. Neumann ほか 2007 KeyStrokes（(a)）
- 書誌: Neumann ほか "KeyStrokes"（略称 KPT とファイル名にある。題・会議・著者全員は未確認）。https://www.lri.fr/~isenberg/publications/papers/Neumann_2007_KPT.pdf
- 内容（検索結果の要約）: 入力したメッセージのリアルタイムの芸術的可視化で、打鍵者の個人差を符号化する。メッセージ用。評価は未確認。
- 判定: (a) の「本人の打鍵でリアルタイムに動く表示」に近い作品。ただし背景ではなく、作業中の代償も測っていない可能性が高い（読んでいない）。

### S7. 引用網から見つけた未読の候補（題と年は Semantic Scholar の被引用リストによる。内容は読んでいない）
- Pousman & Stasko 2006 を引く: "Assessing the cognitive load associated with ambient displays" (Personal and Ubiquitous Computing, 2022)、"Gauging the Utility of Ambient Displays by Measuring Cognitive Load" (Cognition, Technology & Work, 2020)、"Incidental Versus Ambient Visualizations: Comparing Cognitive and Mechanical Tasks" (ICGI 2024; Moreira, Pinto, Mendes, Gonçalves; DOI 10.1109/icgi64003.2024.10923794; 認知課題 N=42・機械的課題 N=28 で ambient と incidental を比較、OpenAlex の要約による) → いずれも (c)。連続する周辺表示の認知負荷を測る。2020 年代の反証候補なので次に読む価値が高い。
- "Investigating the Role of Contrast on Habituation and Sensitisation Effects in Peripheral Areas of Graphical User Interfaces" (Scientific Reports, 2022) → (c)。慣れの効果。
- "Effect of Peripheral Communication Pace on Attention Allocation in a Dual-Task Situation" (INTERACT 2009)、"Intrusive Evaluation of Ambient Displays" (2009)、"Awareness Beyond the Desktop" (Birnholtz ほか, GI 2010, pp.55-62; 周辺視野の表示は注視が半分未満) → (c)。
- "Designing Motivation Using Persuasive Ambient Mirrors" (Nakajima & Lehdonvirta, Personal and Ubiquitous Computing 2011, DOI 10.1007/s00779-011-0469-y) → (b)。抄録は取得できず、中身は未確認。
- Fish'n'Steps (Lin ほか, UbiComp 2006, LNCS 4206, pp.261-278, DOI 10.1007/11853565_16) → (b)。自己の活動を魚に映す。書誌のみ確認、抄録は未取得。
- Mankoff ほか 2003 "Heuristic Evaluation of Ambient Displays" (CHI 2003, pp.169-176, DOI 10.1145/642611.642642) → 評価法の文献で (a)〜(d) には当たらない。
- "Make Me Move at Work! An Ambient Light Display to Increase Physical Activity" (2013) → (b)。自己の行動を周辺に返す。
- 割り込み後の再着手の周辺手がかり: 運転シミュレータの周辺光の手がかりで再開時間が短縮された研究（検索要約のみ、書誌は未確認、ACM の 10.1145/2971485.2971498 が URL にあるが同定していない）→ (d) の隣接。ただし「連続アニメーション」ではなく手がかり。

## 読めなかった・未達
- Stasko 2004 / Pousman 2006 / Hazlewood 2011 の被引用を網羅できていない。Semantic Scholar は Hazlewood 2011 分を取得でき 79 件の題を見た。Pousman 2006 分は 1000 件指定の取得を要約して関連題だけを出させたため、取りこぼしがありうる。Stasko 2004（InfoCanvas）の被引用は未取得。Semantic Scholar が 429 を返して以降、OpenAlex では要約の逐語取得が制約（引用字数制限）で不完全だった。
- Matthews の活動理論による評価の枠組みは、書誌を確認できなかった。
- InfoCanvas の評価（Miller & Stasko ほか）の直接の確認はしていない。
- Zhang の pop-up animations と McCrickard 2001 は登録済みの指示のため調べていない。references.md への照合は Grep の出力が省略されて確認できなかった。

## 使った検索語
- peripheral display continuous animation effect on primary task performance typing document editing evaluation
- ambient display driven by user's own keystroke typing activity wallpaper desktop background visualization study
- Plaue Stasko animation peripheral display distraction primary task
- Yamin and Apphia desktop ambient display computer activity Brombacher
- ambient display of own typing rhythm or physiological state as screen background, users gamed display, reactivity self-monitoring study
- peripheral ambient display effect on task resumption after interruption resumption lag evaluation
- Matthews peripheral display evaluation activity theory / Mankoff Heuristic evaluation of ambient displays
- desktop wallpaper OR desktop background ambient visualization user study work productivity
- Fish'n'Steps abstract / Awareness Beyond the Desktop
- Semantic Scholar の被引用 API（Hazlewood 2011, Pousman 2006）、OpenAlex の題検索
