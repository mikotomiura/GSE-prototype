# sq6: 2巡目 引き直し（Q-A / Q-B / Q-C）

## 引けなかった索引（正直に）
- OpenAlex: 無認証の日次予算が枯渇（"Rate limit exceeded ... $0 remaining"）。キー発行は研究者のメールを使うので行わず。
- Semantic Scholar: 429（Too Many Requests）を 6 回連続で返し、結果ゼロ。
- Crossref: 動いたが query.bibliographic はノイズが多い（Plaue & Stasko 以外は無関係の語が当たった）。以後は DOI 照合（書誌の裏取り）に使った。
- 主は WebSearch（14 本）。したがって「学術索引で網羅的に引いた」とは言えない。ゼロ判定は「WebSearch と Crossref の範囲でゼロ」の意味。

## Q-A 自然らしい動き vs 抽象図形の動き（周辺・同一課題）
引いた語: peripheral ambient display nature-inspired animation vs abstract geometric shapes distraction primary task / nature scenes screen saver peripheral distraction abstract motion / animate vs inanimate motion distractor attention capture biological motion / task-irrelevant nature urban distractors / (Crossref) peripheral display nature animation distraction; biological motion peripheral distractor attention capture
結論: **「自然の動き（水・草・風・雲・群れ）と抽象図形の動きを、周辺表示で同一課題に載せて、注意奪取・主作業成績・好み・慣れを比べた実験」は、見つからなかった（ゼロ）。** 近いものだけ（いずれも条件がずれる）:

1. Pratt, J., Radulescu, P. V., Guo, R. M., & Abrams, R. A. (2010). It's alive! Animate motion captures visual attention. Psychological Science, 21(11), 1724–1730. doi:10.1177/0956797610387440
   - 確かめた先: Crossref（巻・頁・年）、APS ページ（抄録）。抄録のみ。保存: primary/pratt-2010.txt
   - 設計: 6 実験・N は抄録に無く未確認。予測不能な動き（animate）vs 衝突で予測できる動き（inanimate）の物体上の標的の検出時間。
   - 結果: animate 動きの標的の方が速く応答。「uniqueness や top-down 戦略でなく知覚された animacy による」。数値は未確認。
   - 引用: "targets involving objects that underwent animate motion were responded to more quickly than targets involving objects that underwent inanimate motion." / "We conclude that animate motion does indeed capture visual attention."
   - 読み: 標的検出課題で、周辺の妨害刺激ではない。「生き物らしい動きは注意を引く」＝背景に生物らしい動きを置くと主作業から注意を奪う方向の傍証にはなりうる、止まり。
2. Volk, F. A., & Halcomb, C. G. (1994). Psychology of computer use: XXXII. Computer screen-savers as distractors. Perceptual and Motor Skills, 79(3 Pt 2), 1632–1634. doi:10.2466/pms.1994.79.3f.1632
   - 確かめた先: Crossref + Wichita State SOAR（抄録）。抄録のみ。保存: primary/volk-1994.txt
   - 設計: 16 男＋16 女の学部生、3 課題（熟練/非熟練校正、聴解）、妨害は「コンピュータ生成の動的グラフィック」。自然 vs 抽象の比較なし。
   - 結果: 校正（視覚課題）は妨害条件で有意低下なし。聴解は少なくとも 1 条件で有意低下。
   - 引用: "The visually demanding task of proofreading (skilled and unskilled) showed no significant decreases in performance in the distractor conditions."
3. Eich, B., & Beck, M. R. (2023). Differences in the duration of the attentional blink when viewing nature vs. urban scenes. Attention, Perception, & Psychophysics, 85, 1846–1867. doi:10.3758/s13414-023-02749-7
   - 確かめた先: PDF 本文（25 頁）＋ Crossref。保存: primary/eich-2023.txt（dl3/eich-beck-2023.pdf）。N は本文を grep したが拾えず未確認。
   - 設計: 静止画の RSVP（自然 vs 都市）、4 実験。動きではなく静止場面。
   - 結果: 注意の瞬き（attentional blink）は都市場面で短く、周辺ドット検出は自然場面で良い（注意が広がる）。
   - 引用: "The peripheral targets were better detected for nature scenes, suggesting that participants have a broader spread of attention for nature scenes, even in an RSVP task."
   - 読み: 自然場面は周辺を広く見させる（背景の自然画像が周辺の注意を誘う可能性）。動きの比較ではない。
4. （本文を読んでいない）Bristol 群、Global Environmental Psychology 2026 年 5 月オンライン先行。無関係な自然/都市シーンを妨害にした形状弁別課題。WebSearch の要約では「分心を決めるのは自然/都市のカテゴリでなく意味内容の取り出しやすさ。カテゴリ・不快さ・好み・魅力は成績を予測しなかった」。著者・題名・DOI は確かめていない（出どころ: research-information.bris.ac.uk の 2 ページが検索に出たのみ）。65 人という数値は ScienceAlert 経由の二次情報。引用に使うなら一次を取り直すこと。
5. （抄録の存在のみ・本文を読んでいない）Roddy, G., Troje, N. F., & Gurnsey, R. (2010). Peripheral sensitivity to biological motion is unaffected by dividing attention. Journal of Vision, 9(8), 604. doi:10.1167/9.8.604（Crossref で書誌確認。VSS の抄録）。biological motion の周辺感度という題だけ確認。

biological/organic vs mechanical を周辺表示で比べた HCI 実験: ゼロ。
補助: McCrickard/Stasko 系（既登録）と Shen 2009（既登録）は WebSearch でも再度出たが、内容は金融データ等で自然/抽象の比較ではない。

## Q-B 周辺に常駐する動く表示への慣れ（日〜週）
引いた語: habituation ambient peripheral display weeks field study novelty effect / ambient display long-term deployment weeks habituation novelty wore off / (Crossref) habituation ambient display long-term field study weeks（ノイズのみ）
結論: **「周辺の動く表示への habituation を、日〜週の単位で、注意奪取や主作業成績の指標で測った実験」は、見つからなかった（ゼロ）。** 近いもの:

1. Lewandowska, A., Dziśko, M., & Jankowski, J. (2022). Investigation the role of contrast on habituation and sensitisation effects in peripheral areas of graphical user interfaces. Scientific Reports, 12, 15281. doi:10.1038/s41598-022-16284-2
   - 確かめた先: PMC 本文（PMC9464255）＋ Crossref。保存: primary/lewandowska-2022.txt
   - 設計: 画面中央に注意を向けさせ周辺に色付き円（disc）を出す。視線計測で除外後 58 名（60 名中 2 名除外）。時間軸は 1 セッション内で、日〜週ではない。
   - 結果: 中程度のコントラスト・水平/垂直位置・2 Hz 点滅が視認性最良（U3 = 66% が 4 Hz で気付く等）。常時表示では「不要な苛立ちや認知負荷」とも述べる。
   - 引用: "A medium contrast level, a horizontal or vertical display localization, and a flashing frequency of 2 Hz are sufficient to obtain the best visibility in the peripheral area."
   - 読み: 習慣化を扱うが短時間・点滅円で、自然背景ではない。日〜週の根拠にならない。
2. （本文を読んでいない・WebSearch 要約のみ）Hamburg HAW の Ambient Surfaces 系（4 週間・22 週・36 週・5 年超の展開、DFG 2021–2024 で novelty/honeypot 効果の分離が「いまだ不明確」とされる）と、ECSCW 2019 の「周辺表示の研究は短期展開が中心」との指摘。書誌（題名・著者・DOI）は確かめていない。ページ: csti.haw-hamburg.de/project/ambient-surfaces、gepris.dfg.de/gepris/projekt/451069094。「長期の ambient display 野外研究は少ない」という言い方の根拠候補。ただし habituation の数値は取れていない。
3. （存在のみ）Kunikata/Tsuji/Fujinami（東京農工大）の長期使用で行動変容効果を保つ情報提示（日本語）。抄録断片のみ、書誌未確認。

## Q-C 抽象的な ambient 表示から他者が状態を実際に読み取れたか
引いた語: abstract ambient display of colleague activity observers infer stress mood busyness / shared activity visualization remote workers observers guess availability interruptibility stress accuracy / sharing biosignals partner abstract visualization interpret emotional state / MoodLight ambient display arousal social / ambient display mood awareness; (Crossref) peripheral display awareness of colleague state（JSON エラー）
結論: **「抽象 ambient 表示から他者の状態を観察者が正しく読み取れるかを、正解と照らして測った実験」は、見つからなかった（ゼロ）。** 近いもの（読み取りの精度でなく、知覚の変化・使用感を測る）:

1. Morrison-Smith, S., Chilton, L. B., & Ruiz, J. (2021). AmbiTeam: Providing team awareness through ambient displays. Proc. Graphics Interface 2021（DOI は未確認。graphicsinterface.org/proceedings/gi2021/gi2021-04/）
   - 確かめた先: PDF 本文（8 頁）。保存: primary/morrison-smith-2021.txt（dl3/morrison-smith-2021.pdf）。
   - 設計: 科学者 10 名・4 チーム、4 週間・週 2 日のランダム日に email で各メンバーの労力を 1–9 で評価（その間は表示を消す）。表示は共有ファイル活動の抽象的な可視化。
   - 結果: 自己評価に効果なし（t(9)=0.45, p=.66）。他者への評価も前後差なし（t(17)=0.78, p=.45）。活動量と、協働者が付けた評価の変化に弱い正の相関（r=0.22, p=0.011）、本人評価では相関なし（r=0.09）。インタビューでは「表示を意図して見に行かない・背景にとどまった」。
   - 引用: "We found a weak positive correlation (r = 0.22, p = 0.011) between collaborator ratings and the activity" / "participants did not intentionally check the visualization for updates, indicating that the information generally stayed in the background."
   - 読み: 活動の可視化が他者の労力評価と弱く関連。「正しく読めた」ではなく、効果は弱く矛盾を含むと著者自身が書く。
2. Snyder, J., Matthews, M., Chien, J., Chang, P. F., Sun, E., Abdullah, S., & Gay, G. (2015). MoodLight: Exploring personal and social implications of ambient display of biosensor data. CSCW '15, 143–153. doi:10.1145/2675133.2675191
   - 確かめた先: Crossref ＋ Penn State Pure（抄録）。抄録のみ。保存: primary/snyder-2015.txt。N と結果は読んでいない。
   - 引用: "...influence our perceptions of ourselves and those around us."
   - 読み: 覚醒度を灯りの色にした design probe。観察者の読み取り精度の報告があるかは未確認。
3. Omran, H., & Gross, T. (2016). An explorative study on requirements for ambient displays presenting mood awareness. Mensch und Computer 2016. doi:10.18420/muc2016-mci-0227（Crossref 照合は失敗、dl.gi.de のページから転記）
   - 抄録のみ。保存: primary/omran-2016.txt。N=19 のアンケートで、気分の共有意向は実際の気分に左右される。読み取り精度は測っていない。
   - 引用: "the actual mood has a strong influence on the willingness to share one's mood."
4. Liu, F., Park, C., Tham, Y. J., Tsai, T.-Y., Dabbish, L., Kaufman, G., & Monroy-Hernández, A. (2021). Significant Otter: Understanding the Role of Biosignals in Communication. CHI '21, 1–15. doi:10.1145/3411764.3445200
   - 確かめた先: PDF 本文＋ Crossref。保存: primary/liu-2021.txt。
   - 設計: 20 組のカップル、1 か月、生体信号センシング OFF/ON。表示は動くカワウソのアバター（解釈済みの状態を動画化。抽象図形ではない）。
   - 結果: ON の方が会話が楽・本物らしく、社会的つながりを促進。自律性・主体性への懸念も。
   - 引用: "sensing ON enabled easier and more authentic communication that fostered social connection."
   - 読み: 状態の読み取り精度ではなく、通信への効果。本人以外が状態を読めたかの証拠にはならない。
5. 「Liu ら biosignal sharing」の別件: WebSearch が Animo（Liu ら、IMWUT 2019、2 週間 N=34、形・色・動きが生体信号で変わる抽象的な視覚）を示したが、DOI を推測で引いて失敗したため書誌は未確認・本文未読。使うなら一次の取り直しが必要。

## 持ち帰りの要点
- Q-A / Q-B / Q-C とも、問いそのものに合致する実験は見つからず（ゼロ）。ただし OpenAlex・Semantic Scholar が使えなかったので、索引の網羅性は弱い。再実行するなら API キー（研究者が発行）か日を改めて。
- 使える近縁: Pratt 2010（動きの生物らしさが注意を引く・抄録のみ）、AmbiTeam 2021（4 週・弱い相関・背景にとどまる、本文あり）、Lewandowska 2022（周辺習慣化・短時間、本文あり）、Bristol 2026（意味内容が分心を決める・本文未読・書誌未確認）。
