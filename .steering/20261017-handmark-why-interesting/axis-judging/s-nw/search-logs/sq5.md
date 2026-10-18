# sq5: 本文取り 2 巡目 (6 件)
保存先: primary/ = /private/tmp/claude-501/-Users-johnd-GSE-prototype/f99bdc93-3f93-41b7-863c-4ad0bd1f8194/scratchpad/survey/primary/ 。書誌は Crossref (api.crossref.org) で確認、著者は OpenAlex でも照合。

## 1. Ishii & Ullmer 1997 — 本文あり
- 書誌 (Crossref 10.1145/258549.258715): Hiroshi Ishii, Brygg Ullmer. "Tangible Bits: Towards Seamless Interfaces between People, Bits and Atoms." Proc. CHI '97, pp. 234-241, 1997-03-27。
- 本文: primary/ishii-1997.txt (出どころ https://arl.human.cornell.edu/879Readings/HiroshiIshii_Tangible%20Bits.pdf, 8 頁。CHI97 版であることは冒頭 "CHI 97 * 22-27 March 1997" で確認)。
- 設計/N: 構想・試作論文 (metaDESK, transBOARD, ambientROOM)。利用者研究・N なし。
- 関わる記述 (逐語):
  - L144-146 "3) Ambient Media: Use of ambient media such as sound, light, airflow, and water movement for background interfaces with cyberspace at the periphery of human perception."
  - L599-606 "The ambientROOM complements the graphically-intensive, cognitively-foreground interactions of the metaDESK by using ambient media – ambient light, shadow, sound, airflow, water flow – as a means for communicating information at the periphery of human perception."
  - L ~650- "We may have a sense of the weather outside from ambient cues such as light, temperature, sound, and air flow from nearby windows."
- 反証/限界: 評価なし。自然の媒体が「良い」という実証はない。入力は情報源 (天気等) の写像で、打鍵のような本人の行為の写しではない。

## 2. Dahley, Wisneski & Ishii 1998 (Water Lamp and Pinwheels) — 本文未取得・本文を読んでいない
- 書誌 (Crossref 10.1145/286498.286750): Andrew Dahley, Craig Wisneski, Hiroshi Ishii. "Water Lamp and Pinwheels: Ambient Projection of Digital Information into Architectural Space." CHI 98 Conference Summary on Human Factors in Computing Systems, pp. 269-270, 1998-04。題の副題は依頼文どおり (Crossref の title は短縮形 "Water lamp and pinwheels")。
- ACM DL は Cloudflare で弾かれ、MIT Media Lab の publications ページは見つからず。OpenAlex に抄録なし。
- 代替: 同じ著者群の 3 の本文 (primary/wisneski-1998.txt) §4 が Water Lamp と Pinwheels を記述している (下記)。2 そのものの記述として引用してはならない。
- 3 §4.1 (L342-352): "A light shines upward through a pan of water, which is actuated by changing information. This action produces changing patterns of light projected onto the ceiling of a room." ソレノイドが水面を叩き、波状の影が天井に出る。

## 3. Wisneski et al. 1998 (Ambient Displays) — 本文あり
- 書誌 (Crossref 10.1007/3-540-69706-3_4): Craig Wisneski, Hiroshi Ishii, Andrew Dahley, Matt Gorbet, Scott Brave, Brygg Ullmer, Paul Yarin. "Ambient Displays: Turning Architectural Space into an Interface between People and Digital Information." In: Cooperative Buildings (CoBuild 1998), LNCS 1370, pp. 22-32。冒頭に "Proceedings of the First International Workshop on Cooperative Buildings (CoBuild '98), February 25-26, 1998"。
- 本文: primary/wisneski-1998.txt (10 頁。出どころ MIT Media Lab publications ページの PDF リンク https://dam-prod.media.mit.edu/x/files/publishedmedia/Papers/314-Ambient%20Displays%20Turning%20Architectural/Published/PDF)。
- 設計/N: 試作 (ambientROOM, Ambient Fixtures=Water Lamp/Pinwheels) と設計論。統制した利用者研究なし。N なし。
- 主要な記述 (逐語):
  - L30-32 "Nature is filled with subtle, beautiful and expressive ambient displays that engage each of our senses. The sounds of rain and the feeling of warm wind on our cheeks help us understand and enjoy the weather even as we engage in other activities."
  - L284-289 "The ambientROOM contains a subtle but audible soundtrack of birds and rainfall, whose sound volume and density are modulated in conjunction with variations in room lighting. Thus, approximate quantities can be monitored with this display, for instance, the number of unread email messages or the level of a stock portfolio."
  - L401-407 "Ambient Fixtures are especially suited to the display of information like natural phenomena ... In ways like these, ambient media can provide a means for people to feel connected to the world around them."
- 反証になる点 (重要):
  - L440-444 "many people reported that the sampled, looped sounds of water in the ambientROOM became annoying after months of repetition. In particular, sounds that are looped in some kind of discernable way tend to become annoying very quickly." (水の音の反復が数か月で不快になった、という逸話的報告。N・方法なし)
  - 対比: Stream of Consciousness (White & Small 1997) の実物の水流は "most people seem to prefer" (L446-448)。実物の物理は好まれる、とあるが根拠は示されない。
  - L ~420-425 モダリティは前景課題に合わせる: ソフト書きのような視覚課題中は壁の視覚表示より聴覚表示のほうが有効かもしれない、との記述あり (視覚の背景は前景課題が視覚だと効きにくいという含意)。

## 4. Weiser & Brown "Designing Calm Technology" — 本文あり (ウェブ再掲)
- 書誌: Mark Weiser, John Seely Brown. "Designing Calm Technology." Xerox PARC, December 21, 1995 (ページの日付表記)。続版: "The Coming Age of Calm Technology" in Beyond Calculation: The Next Fifty Years of Computing (Springer, 1997), pp. 75-85, DOI 10.1007/978-1-4612-0685-9_6 (Crossref で確認。この続版と依頼の「1995/1996」の対応は、本文同一かを未照合)。
- 本文: primary/weiser-1996.txt (出どころ https://calmtech.com/papers/designing-calm-technology。原典の PDF ではなく同サイトの HTML 再掲。ページ番号なし)。
- 設計/N: 論考。実験なし。
- 逐語:
  - "The "Dangling String" is an 8 foot piece of plastic spaghetti that hangs from a small electric motor mounted in the ceiling. The motor is electrically connected to a nearby Ethernet cable, so that each bit of information that goes past causes a tiny twitch of the motor. A very busy network causes a madly whirling string with a characteristic noise; a quiet network causes only a small twitch every few seconds."
  - "At first it creates a new center of attention just by being unique. But this center soon becomes peripheral as the gentle waving of the string moves easily to the background."
  - "While screen displays of traffic are common, their symbols require interpretation and attention, and do not peripheralize well. The string, in part because it is actually in the physical world, has a better impedance match with our brain's peripheral nerve centers."
- 反証/限界: 根拠は著者の主張のみ。「画面表示は周辺化しにくい」は画面上の背景に不利 (本案の背景は画面上)。「個人が中心/周辺の移動を握る」"The individual, not the environment, must be in charge of moving things from center to periphery" は、背景側から注意を引く設計への制約になりうる。

## 5. WaveWatch (Shelton & Nesbitt) — 抄録のみ・本文を読んでいない
- 書誌 (Crossref 確認、著者 Ben Shelton, Keith (V.) Nesbitt の 2 名のみ。Newcastle 大):
  (a) "WaveWatch – An Ambient Display of Web Traffic Data." Application and Theory of Computer Technology 2(1):11-26, 2017, DOI 10.22496/atct20161230121 (巻号は WebFetch した Crossref 整形結果による)。
  (b) "Evaluating WaveWatch: an ambient display of web traffic." Proc. Australasian Computer Science Week Multiconference (ACSW '17), pp. 1-9, 2017-01-31, DOI 10.1145/3014812.3014821。
  (c) 関連: "The aesthetic awareness display" ACSW 2016 (10.1145/2843043.2843371) は未確認の別論文。
- 保存: primary/shelton-2017-abstract.txt (OpenAlex の復元抄録 2 本。出どころ api.openalex.org)。本文 PDF は ACM が Cloudflare、OpenAlex は closed、取れず。
- 抄録から言えること: 3D の海の画面表示。波の高さ・頻度・速さで web トラフィックを写す (20 段階)。実際のマーケティング部門のオフィスで 2 週間展開。"generally positive ... easy to interpret, useful and unobtrusive"。N・参加者数・数値・統計は抄録に無い (確認できず)。
- 逐語 (抄録): "if web traffic was low the ocean would remain calm and as web traffic increased the ocean waves would become more turbulent." / "provide a calming rather than distracting background in the work place."
- 注意: 探索中の検索要約に「7 人・5 日・約 25% の事象に気づいた」という記述があったが、出どころ不明で本論文のものと断定できない。使わない。
- 反証: 抄録は肯定のみ。実際の否定的所見は本文未読のため不明。

## 6. Lin et al. 2006 (Fish'n'Steps) — 抄録のみ・本文を読んでいない
- 書誌 (Crossref 10.1007/11853565_16): James J. Lin, Lena Mamykina, Silvia Lindtner, Gregory Delajoux, Henry B. Strub. "Fish'n'Steps: Encouraging Physical Activity with an Interactive Computer Game." UbiComp 2006: Ubiquitous Computing (LNCS 4206), pp. 261-278, 2006。OpenAlex も著者 5 名一致。
- 取得: Springer は JS チャレンジ、ResearchGate・Semantic Scholar は 403/429、CiteSeerX は HTML 返却。本文取れず。既存 primary/lin-2006-abstract.txt (上書きせず) の抄録のみ。罪悪感・競争の負担・やめた人・魚が悲しむ表現の扱いは、本文を読んでいないので何も言えない。
- 検索要約で見た二次情報 (本文未確認・要照合): 14 週・19 人、"Most players' enthusiasm fell after the first two weeks" 旨、およびトランスセオレティカル・モデルでの解釈。「否定的強化より励ましを重視」との要約も出たが逐語でなく出どころ未確認。魚の気分が歩数に連動するという後続論文の記述あり。
- 次の手: 大学図書館経由で Springer 本文、または著者 (Mamykina) 経由。

## 要約
本文あり: 1, 3, 4。抄録のみ: 5, 6。取れず: 2 (3 の §4 が代替)。
