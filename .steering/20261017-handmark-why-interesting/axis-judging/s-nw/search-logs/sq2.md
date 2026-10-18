# SQ-2 「育つ」自然・生き物の表示の害・副作用と、効いた証拠（反証 angle）

保存先: /private/tmp/claude-501/-Users-johnd-GSE-prototype/f99bdc93-3f93-41b7-863c-4ad0bd1f8194/scratchpad/survey/primary/
（同フォルダに他 angle の txt も混在。私が作ったのは下記に挙げたものだけ）

## 総評（判断はしない）
- 「育つ表示は害」を直接の実験で示した一次文献は今回 1 本（FocusBuddy、N=20、罰則型のペット）。それ以外の害の証拠は (a) 罰則・必須・競争型の gamification の教室研究 (Hanus & Fox, 二次情報のみ)、(b) 追跡をやめた後の罪悪感 (Epstein 2016)。
- 「育つ表示が効いた」側: Fish'n'Steps（N=19、抄録のみ）、Virtual Fitness Buddy（cluster RCT、効果は 3 か月で消失）。
- gamification が内発的動機を削る、という通説は Mekler 2017 (N=273) では支持されず（動機への有意な影響なし、行動量は増）。
- Forest（木が育つ・枯れる）の査読済み効果研究は見つからなかった。

---
## 1. Ouf & Hussein 2026 FocusBuddy（害の直接証拠・小規模）
- 書誌: Mohamed Ouf, Rowan Hussein. "FocusBuddy: Encouraging Healthy Desk-Work Habits by Caring for a Virtual Pet on a Water Bottle." arXiv:2609.00412v1 [cs.HC], 15 Jul 2026. URL https://arxiv.org/abs/2609.00412 。DOI は未確認（arXiv のみ。査読の有無も未確認）。著者は PDF 冒頭に 2 名（Queen's University / University of Ottawa）。
- 取得: 本文 PDF。保存 focusbuddy-2026.txt
- 設計: N=20 学部生、2 週間、水筒ケースに画面付きの仮想ペット。水を飲む・立つ・ボトルを補充するとペットの状態が良くなる。「at zero points the pet dies」(L188)。事前事後＋自由記述。対照群なし。
- 結果: 水分摂取 中央値 3→4 杯/日、移動 2→4 回/日、最長連続着座 162.5→90 分（いずれも p≤.001、自己報告）。
- 逐語（focusbuddy-2026.txt）:
  - L30-31: "pet neglect can convert a wellness prompt into a source of guilt."
  - L361-364: "P16, who rated pet-related pressure 5 of 5, took breaks 'mostly because I felt bad rather than because I wanted one,' and noted that one missed prompt damaged the pet more visibly than a completed action repaired it."
  - L429-431: "Participants under deadline pressure experienced the declining pet as an accusation ..." / "P13 read the sad pet as 'a reprimand' on stressful days and avoided looking at the device." (L363-364)
  - 3 人 (P11, P02 ほか) は「ペットの世界観は不要・中立なタイマーがよい」と回答（L365-367 付近）。
- 判定: 制約の根拠（弱〜中）。害は「失敗が非対称に重く見える・罰する」設計で出た。著者自身が「設計の誤りであって比喩に固有の代償ではない」(L431-432 付近) と書く → 「育たない・溜まらない」ではなく「罰さない・許す」で足りるという読みの余地がある。N=20・自己報告・対照なし・プレプリントの限界あり。

## 2. Epstein, Kang, Pina, Fogarty, Munson 2016（やめた後の扱い）
- 書誌: Daniel A. Epstein, Jennifer H. Kang, Laura R. Pina, James Fogarty, Sean A. Munson. "Reconsidering the Device in the Drawer: Lapses as a Design Opportunity in Personal Informatics." UbiComp 2016 (Proc. 2016 ACM IJCPUC), pp. 829-840. DOI 10.1145/2971648.2971656（Crossref で確認）。
- 取得: 本文 PDF（著者サイト https://homes.cs.washington.edu/~jfogarty/publications/ubicomp2016.pdf）。保存 epstein-2016.txt
- 設計: Fitbit をやめた 141 人の調査、7 種の可視化と 7 種の枠づけへの選好。
- 結果: 「約半数が追跡をやめたことに罪悪感または苛立ち」(Table 2 の注、L669)。罪悪感群は再開を促すメッセージを歓迎、「追跡は無益・否定的」群は「押しつけがましい」と感じた (L122-125)。
- 逐語:
  - L669: "nearly half felt guilt or frustration over abandoning tracking."
  - L688-690: "Many felt either guilty that they were not using their Fitbit or frustrated that Fitbit did not help them change their behavior."
  - L122-125: "participants who thought tracking was a useless or negative experience felt these messages were presumptive and inconsistent with their experiences."
- 判定: 制約の根拠（間接）。育つ表示ではなく数値追跡の研究。「やめた後」に溜まった記録が罪悪感の的になりうる、という点のみ。ただし一部は「ただ無関心」(ambivalence, L755) で、全員が害を受けるわけではない。

## 3. Mekler, Brühlmann, Tuch, Opwis 2017（動機の置き換えの反例）
- 書誌: Elisa D. Mekler, Florian Brühlmann, Alexandre N. Tuch, Klaus Opwis. "Towards understanding the effects of individual gamification elements on intrinsic motivation and performance." Computers in Human Behavior 71 (2017) 525-534. DOI 10.1016/j.chb.2015.08.048（Crossref で確認）。
- 取得: 本文 PDF（https://glassmanlab.seas.harvard.edu/annotated_works/mekler17.pdf）。保存 mekler-2017.txt
- 設計: 2×4 オンライン実験、N=273、画像タグ付け課題。points / levels / leaderboard 対 統制。
- 結果: 内発的動機・有能感に有意差なし。タグ数は points、特に levels と leaderboard で有意に増加。
- 逐語（mekler-2017.txt 冒頭の抄録）: "Compared to a control condition, game elements did not significantly affect competence or intrinsic motivation, irrespective of participants' causality orientation." / "points, levels and leaderboards functioned as extrinsic incentives, effective only for promoting performance quantity."
- 判定: 「報酬を足すと動機が削られる」への反例（削られなかった）。ただし 1 回きりの短い課題で、長期・自然作業ではない。逆に「量が増える」ことは、背景表示の目的次第で副作用（作業を量で測る方向に傾く）にもなりうる、と読める（解釈は研究者）。

## 4. Hanus & Fox 2015（教室、害の証拠・二次情報のみ）
- 書誌: Michael D. Hanus, Jesse Fox. "Assessing the effects of gamification in the classroom: A longitudinal study on intrinsic motivation, social comparison, satisfaction, effort, and academic performance." Computers & Education 80 (2015) 152-161. DOI 10.1016/j.compedu.2014.08.019（Crossref で確認）。2018 年に corrigendum あり（Computers & Education 127、中身は未確認）。
- 取得: 本文も抄録も取れず（出版社が抄録を伏せている）。hanus-2015-secondary.txt に二次要約のみ保存。本文を読んでいない。
- 二次要約: バッジ必須＋リーダーボードの授業で、満足度・内発的動機が低く、期末成績も低かった。原因は社会的比較か自律性の喪失とされる（二次情報）。
- 判定: 制約の根拠になりうるが、必須・競争・評価つきの文脈。自分だけの背景表示とは条件が違う。数値は未確認なので引用に使えない。

## 5. Ahn ら 2024 Virtual Fitness Buddy（育つペットが効いた側・効果は消えた）
- 書誌: Sun Joo (Grace) Ahn, Michael D. Schmidt, Allan D. Tate, Stephen L. Rathbun, James J. Annesi, Lindsay S. Hahn, Eric Novotny, Christian D. Okitondo, Rebecca N. Grimsley, Kyle Johnsen. "Virtual fitness buddy ecosystem: a mixed reality precision health physical activity intervention for children." npj Digital Medicine (2024). DOI 10.1038/s41746-024-01133-5（Semantic Scholar で確認）。巻・論文番号は未確認。
- 取得: 本文 HTML（PMC11109260）を保存 ahn-2024.txt。抄録は ahn-2024-abstract.txt。
- 設計: cluster RCT、19 か所の学童保育、6 か月×2 コホート、422 人参加（脱落・除外後 ITT 対照 152・介入 155、L475）。介入は仮想の犬＋保護者へのフィードバック。対照は犬なしで目標設定。
- 結果: 座位が軽強度の活動に置き換わった（3 か月まで）。中高強度活動の増加は有意でなく、期間 2 の差は 3.9 分で有意でない (L472)。
- 逐語（ahn-2024.txt L664-666）: "the VFB ecosystem was successful in converting significant levels of sedentary behavior with light-intensity PA for up to three months. However, the current design of the VFB ecosystem seemed to be insufficient in overcoming the downward trend of PA observed between Time 2 and Time 3." 著者は理由に「ペットとのやりとりに十分な新しさがない」ことを挙げる（"lack of sufficiently motivating content ... digital content must be updated to provide new challenges to users who have mastered existing content"）。
- 判定: 反例（育つ・世話する表示が効いた）かつ、長期の飽き・効果の減衰の根拠。ただし犬と保護者の介入の束で、ペット単体の効果ではない。対象は子ども。

## 6. Lin ら 2006 Fish'n'Steps（効いた側・抄録のみ）
- 書誌: James J. Lin, Lena Mamykina, Silvia Lindtner, Gregory Delajoux, Henry B. Strub. "Fish'n'Steps: Encouraging Physical Activity with an Interactive Computer Game." UbiComp 2006, LNCS 4206, pp. 261-278. DOI 10.1007/11853565_16（Crossref で著者・頁を確認）。
- 取得: 本文は取れず（Springer が認証へリダイレクト）。本文を読んでいない。lin-2006-abstract.txt に要約のみ（逐語ではない）。
- 内容: 歩数が魚の成長・活動に対応。14 週間、N=19。運動の「きっかけ」になり態度が改善、と抄録。数値は未確認。二次文献に「悲しい・不健康な魚でやめる人がいうるとの指摘」(ある運動ゲームのレビュー) があるが、一次で未確認。
- 判定: 反例（効いた）。害の有無は本文未読のため判定不能。

## 7. Forest 関連（査読済み効果研究なし）
- Evaluating the Effectiveness of Apps Designed to Reduce Mobile Phone Use ... Multimethod Study（PMC10498313、2023 年。書誌の著者・誌名・DOI は未確認）。13 アプリの機能を分類、gamification を持つのは Forest のみ。Forest の gamification へのレビューの感情は 肯定 48% / 中立 14% / 混合 10% / 否定 28%（検索要約）。保存 unknown-2023-pmc.txt（HTML を文字化したもの。数値の位置は未精査）。本文中に「gamification の効果は十分に検証されていない」旨 (L1130-1132)。
- 判定: Forest の木が育つ表示の効果も害も、一次の実験では示されていない。

---
## 見つからなかったもの
- Forest（スマホを触らないと木が育つ）の査読済みの効果・害の研究: 「Forest app study / CHI / guilt withered tree」で 0 件。上記 2023 の多アプリ研究が最も近い。
- Fish'n'Steps の本文（歩数の増加量、魚の「悲しい」状態への反応、やめた人）: 取得できず。
- Tamagotchi/ペット死の研究で「死ぬ表現」自体を操作した実験: 該当ゼロ（FocusBuddy の自由記述が最も近い）。
- UbiFit を引いて「枯れる・花がない」害を報告した後続研究: 1 回の検索では該当なし（UbiFit の二本は登録済みのため再読せず）。
- 「長期（数か月〜年）の育つ表示の飽き」を直接測った研究: Ahn 2024 の 3 か月での減衰以外は未発見。
- Zimmerling & Höllig (Academy of Management Proceedings 2016, DOI 10.5465/ambpp.2016.18124abstract) の 446 人・5 日の野外実験は存在を確認したが、抄録・本文とも未取得（要約は検索結果のみ）。
- 自己量化の負担（育つ表示固有）、ずるをする（cheating）の研究: 探したが該当を取れず。
