# novelty angle 1: 動く壁紙・デスクトップ背景の評価（反証側の探索）

## 結論（下位の問い別）
- (a) 本人の打鍵・行動・生体のリズムでリアルタイムに動く背景・環境の表示は既にあるか: **見つかった（作品・試作のみ。評価研究は見つからなかった）。** Dakadaka（Reas/Levin 2000）は打鍵を動的な表示につなぎ「ordinary typing を補う ambient 表示の試作」と自称する芸術作品。KeyStrokes（Neumann ら 2006/2007）は打鍵の速さ・リズムを可視化するが、送信用の絵であって作業中の背景ではない。Brombacher ら（OzCHI 2020）はデスクトップ上の ambient 表示で PC 活動を見せる質的試作（N=16）。Moraveji ら（UIST 2011）は画面周辺に呼吸ペース表示（生体に合わせた周辺表示の評価だが、ペースは本人の呼吸でなく外から与える）。**「全面の背景が、打鍵のリズムで、滑らかに動き続け、作業中に評価された」例は見つからなかった。**
- (b) 自己を写す表示を状態計として読んだか・表示のために行動を変えたか: **近い研究は見つかった（背景・打鍵ではない）。** Rogers ら（UbiComp 2010）は ambient 表示で行動が有意に変わったが本人は気づかなかったと報告。Fish'n'Steps（UbiComp 2006）は歩数を魚に写して 14 週・19 人。背景の全面表示で測った研究はこの範囲で見つからなかった。
- (c) 作業中に背景・周辺で動き続ける表示の注意の代償: **見つかった（周辺表示であって壁紙ではない）。** Maglio & Campbell（CHI 2000）は「継続的にスクロールする周辺表示は断続型より注意を奪う」。Dutta ら（VT）は周辺の動く表示で主課題の衝突が増えた。壁紙・背景そのものを対象にした査読研究は **見つからなかった**。
- (d) 同じ表示で作業中の代償と中断後の再着手を分けて測った研究: **この範囲で見つからなかった。** Shen（2009）が display-distraction と self-interruption を分けるが、再着手の遅れ（resumption lag）で測ってはいない（抄録レベルの確認）。

**GSE の空白の主張への見立て**: 「動く壁紙を評価した査読論文 0 件」は、この探索でも覆らなかった（検索結果は SEO の記事ばかりで出典なし）。ただし「周辺で動き続ける表示の注意の代償」は 2000 年前後から大量にあり（Maglio、Bartram の moticon は既に [P85] 登録）、**空白と言えるのは「全面の背景」「本人の打鍵に同期」「作業中の代償と中断後の再着手の分離」の組み合わせに限る**。「周辺の動きは注意を奪う」という方向は既知であり、GSE 側がそこに新規性を置くと崩れる。Dakadaka は「打鍵を ambient 層にする」着想の先行作品として、新規性の文面で言及が要る。

## 見つけたソース

### 1. Maglio & Campbell 2000（(c) に当たる・空白を部分的に崩す）
- Maglio, P. P., & Campbell, C. S. (2000). Tradeoffs in displaying peripheral information. *CHI 2000*, pp. 241–248. DOI: 未確認（PDF: https://www.interruptions.net/literature/Maglio-CHI00-p241-maglio.pdf）
- 設計: IBM の参加者 29 人（本文で確認。pypdf で全文を取得）。文書編集を主課題に、周辺のティッカー（スクロール表示）の動かし方を比べた。
- 結果: 継続スクロールは断続スクロールより主課題への妨害が大きく、記憶は同程度。
- 逐語（抄録・pypdf の本文から。行 22–24 付近）: "continuously scrolling displays are more distracting"（前後は改行で分断。完全文は未確認）。
- 見立て: 作業中に動き続ける周辺表示は代償を生む、の直接の先行。壁紙ではない。登録: references.md に未登録（Grep で 0 件）。

### 2. Dutta, McCrickard, Deshmukh, Jouenne（Virginia Tech）（(c)）
- "Evaluating Benefits and Distractions of Animated Secondary Displays For Attention-Centric Primary Tasks". 年・会議名は**未確認**（文書内に記載なし。URL 名は CISST02 とあるが推測は避ける）。https://www.interruptions.net/literature/Dutta-CISST02.doc
- 設計: 29 組のデータ。動く正方形を中央に保つ主課題＋副表示（なし／フェード／ティッカー）。結果: 副表示ありで衝突が有意に増加（F(2,81)=7.90, p<.001）。
- 逐語（本文）: "Animated displays in the periphery can cause distraction to a high-attention-centric motion intensive tasks."
- 見立て: (c)。主課題が特殊（運動の追跡）。壁紙でない。

### 3. Dakadaka（Casey Reas / Golan Levin, Ars Electronica 2000）（(a) 先行作品）
- 書誌: Ars Electronica 2000 カタログの 1 頁（https://webarchive.ars.electronica.art/en/archiv_files/20001/E2000_386.pdf）。ページ・正式な題は未確認。評価研究ではない。
- 逐語（本文・pypdf 抽出）: "One can understand Dakadaka as a prototype for an ambient display which could augment one's ordinary typing as an auxiliary, transparent layer"。別の箇所: "By connecting the physical act of typing to a dynamic display instead of a static one, Dakadaka reflects these fleeting performances back to us"。
- 見立て: (a)。打鍵のリズムを動的な表示に返す着想は 2000 年に既にある。ただし Java アプレットの作品で、デスクトップ背景ではなく、評価なし。**新規性の文面で引くべき。**

### 4. Neumann, Tat, Zuk, Carpendale（KeyStrokes）（(a)）
- "KeyStrokes: Personalizing Typed Text with Visualization". *EuroVis 2007* (Eurographics/IEEE VGTC Symposium on Visualization), pp. 43–50. DOI: 未確認（https://diglib.eg.org/handle/10.2312/VisSym.EuroVis07.043-050）。前身 2006 の VTC 論文 "Visualization of Typed Communication"、ポスター（lri.fr 上の PDF）。
- 内容（検索要約・本文は読んでいない）: 打鍵の速さ・リズム・手の使い方・消去を取り、実時間の可視化にする。送信用の絵（electronic postcard）。
- 見立て: (a)。目的が違う（他者へ送る個性の表現）。背景でなく作業中の評価もない。逐語引用は取れていない（抄録のみ・それも要約経由）。

### 5. Brombacher, Ren, Vos, Lallemand（OzCHI 2020）（(a)(b)）
- "Visualizing Computer-Based Activity on Ambient Displays to Reduce Sedentary Behavior at Work". *OzCHI '20*, pp. 760–764. DOI: 10.1145/3441000.3441022（ページから確認）。https://hbo-kennisbank.nl/details/sharekit_fontys:oai:surfsharekit.nl:57ca752c-6275-4919-9d70-da7e89e04d8b
- 設計: 試作 Yamin と Apphia、探索的・質的、ラボ、オフィスワーカー 16 人。結果: 気づき・内省・社会的相互作用を促す可能性。
- 見立て: (a)(b) に近いが、デスクトップ上の ambient 表示で PC の利用量を見せ、目的は座位の削減。リズムの同期でも壁紙でもない。要旨のみ（本文未読・逐語は取っていない）。

### 6. Moraveji ら（UIST 2011）（(a)(c)）
- Moraveji, Olson, Nguyen, Saadat, Khalighi, Pea, Heer. "Peripheral Paced Respiration: Influencing User Physiology during Information Work". *UIST 2011*. DOI: 10.1145/2047196.2047250（https://idl.uw.edu/papers/peripheral-paced-respiration）。N は取得できず未確認。
- 逐語（ページの抄録）: "Participant respiration decreased significantly in the pacing condition."
- 見立て: 画面周辺の周辺表示を作業中に評価した例。ただし呼吸ペースを外から与えるもので、本人のリズムに同期する表示ではない。作業の代償の測定の詳細は未読。

### 7. Rogers ら（UbiComp 2010）（(b)）
- Rogers, Hazlewood, Marshall, Dalton, Hertrich. "Ambient influence: Can twinkly lights lure and abstract representations trigger behavioral change?" *UbiComp '10*, pp. 261–270. DOI: 10.1145/1864349.1864372（https://research-information.bris.ac.uk/en/publications/ambient-influence-can-twinkly-lights-lure-and-abstract-representa/）。N・期間は未確認（ページに記載なし）。
- 結果（要約・逐語は取れず）: 参加者は行動を変えたと気づいていないが、ログでは有意に変化。階段対エレベーター。
- 見立て: (b)。物理空間の表示で、デスクトップでない。反応性の測定ではなく行動の変化の測定。

### 8. Lin, Mamykina, Lindtner, Delajoux, Strub (2006)（(b)）
- "Fish'n'Steps: Encouraging Physical Activity with an Interactive Computer Game". *UbiComp 2006*, LNCS, Springer. DOI: 10.1007/11853565_16（検索結果の表記）。ページ範囲は資料間で食い違い（未確認）。
- 設計（検索結果の要約）: 14 週・19 人。歩数が魚の成長に反映。結果: 運動と態度を促進。悪い状態の魚で使うのをやめる例が二次資料にある（未確認）。
- 見立て: (b) 自己を写す表示の古典。背景でなく、反応性の測定として設計されたものでもない。抄録レベルの確認のみ。references.md には備考欄で言及があるのみで、登録行は見つからなかった。

### 9. Shen（2009）Intrusive Evaluation of Ambient Displays（(c)(d)）
- IGI Global の章／*J. Ambient Computing and Intelligence* 1(4):12–31 の記載が混在（IDEAS 経由）。著者・DOI は未確認。抄録のみ。
- 要約: display-distraction と self-interruption を分け、アニメーションは前者にだけ効くと報告。視覚手がかりの妨害順は「animation > color > area > position」。
- 見立て: (d) に最も近いが、再着手の遅れは測っていない（抄録のみ）。

### 補助的に見つかったが関係が薄いもの
- Xu ら 2025 *Behavioral Sciences* 15(7):953, DOI 10.3390/bs15070953（PMC12292703）。N=32、背景の環境映像を LED 画面に出して読書中の注視を測る。理解テストは報告なし。背景映像の効果の弱い間接証拠（(c)）。逐語: "the Dormitory environment best supports sustained, focused attention"（本文）。壁紙ではなく環境映像＋音声。
- 赤・青・ベージュのモニター色の研究（PubMed 11883587）は色のみで、動きでない。書誌は未確認。

## 空振りした範囲（使った検索語）
英語: animated desktop wallpaper attention productivity user study／live wallpaper typing rhythm reactive background ambient display keystroke visualization／dynamic desktop background distraction task performance peripheral animation／ambient display desktop wallpaper behavior change CHI／self-tracking ambient display gamification reactivity／affective wallpaper mobile live wallpaper emotion mood／task-irrelevant background motion video distraction reading／wallpaper image desktop background cognitive load／typing rhythm ambient generative visual feedback writing flow／peripheral ambient display continuous animation resumption after interruption／biofeedback ambient background display during computer work／Wallpaper Engine live wallpaper battery preference／ambient display gaming the display reactivity。
日本語: 動く壁紙 デスクトップ 背景 作業 集中 影響 実験 論文／生成的 背景 キーボード 打鍵 リアルタイム 可視化 デスクトップ 壁紙 研究。
- 結果: 動く壁紙の査読研究は 0 件のまま。ヒットしたのは SEO の記事（出典なし・引用に値しない）のみ。電池・好みについても査読研究は見つからなかった。
- 未実施: Google Scholar・ACM DL・CiNii・J-STAGE への直接検索（WebSearch 経由のみ）。画面保護（screensaver）・仮想背景（ビデオ会議）・Mac の Dynamic Desktop・Wallpaper Engine の学術研究は探せていない。ここは別の angle での確認を勧める。
- 読んでいない: KeyStrokes 本文、Shen 本文、Rogers 本文、Fish'n'Steps 本文、Moraveji 本文。

## 注意
- 書誌は上記で「未確認」とした項目を除き、取得したページ・PDF で確認したもの。Fish'n'Steps のページ範囲は食い違いがある。
- references.md への登録はしていない（編集禁止）。重複確認: Maglio・Moraveji・Dakadaka・Brombacher・Rogers は未登録（Grep 0 件）。Bartram の moticon は [P85]（[P251] は tombstone）。
