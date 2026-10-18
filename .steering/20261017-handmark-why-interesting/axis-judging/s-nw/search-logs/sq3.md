# SQ-3 探索結果（本文を読めた 5 件＋周辺）
保存先: /private/tmp/claude-501/-Users-johnd-GSE-prototype/f99bdc93-3f93-41b7-863c-4ad0bd1f8194/scratchpad/survey/primary/ （pdftotext 全文。行番号は各 txt の行）

## 1. Alt ら 2010（反例寄りの材料：抽象化は「やや」守るだけ・読まれ方も弱い）
- 書誌: Florian Alt, Alireza Sahami Shirazi, Andreas Kaiser, Ken Pfeuffer, Emre Gürkan, Albrecht Schmidt, Paul Holleis, Matthias Wagner. "Exploring Ambient Visualizations of Context Information." 2010 8th IEEE Int. Conf. on Pervasive Computing and Communications Workshops (PERCOM Workshops), pp. 788-791, 2010. DOI 10.1109/PERCOMW.2010.5470542（検索結果の BibTeX/OpenAlex 記載で確認。doi.org への直接解決は未実施）。
- 取れたもの: 本文全文 -> primary/alt-2010.txt
- 設計/N: オンライン調査 N=73（女性19・平均28.2歳）。ウサギ型 Nabaztag とデジタル写真立ての 2 試作で位置・活動などの文脈を表示。
- 結果: 写像理解テスト（4 文のうち正誤 2:2 を判定）の正答率 Nabaztag 66%、写真立て 78%。「理解しやすい/とても」52%。使ってみたい 25% / 33%。プライバシー: 詳細表示が影響すると答えた 73% に対し、環境的可視化は 40%。
- 逐語（alt-2010.txt L126-130）: "presenting information in a non-intrusive, abstract, and hence privacy preserving way. ... 73% of the participants considered presenting detailed information to affect their privacy. However, only 40% considered the same to be true for an ambient visualization."
- 位置づけ: 抽象化しても 4 割は「プライバシーに影響」と答えた = 「抽象なら漏れない」への反例。ただし回答は自己評価で、他者が実際に読み取れたかの実験ではない。自然の写像ではなく動物/写真立て。

## 2. Skog, Ljungblad, Holmquist 2003（天気を色/位置に写した例と、色の連想のずれ）
- 書誌: Tobias Skog, Sara Ljungblad, Lars Erik Holmquist. "Between Aesthetics and Utility: Designing Ambient Information Visualizations." IEEE Symposium on Information Visualization (InfoVis) 2003, Seattle, Oct 19-21, 2003. DOI 未確認（本文に記載なし。ページ番号も未確認）。
- 取れたもの: 本文全文 -> primary/skog-2003.txt
- 設計: Informative Art（モンドリアン風の色四角）で世界の天気・地域天気予報・メール・バス。評価は主にバス表示の学生インタビュー（8人）と現地観察（5人中 3 人が読み方を知っていた）。天気表示の評価は定性的で数値なし。
- 結果: 任意の空間配置（メール・地域予報）は覚えにくく、地理的メタファーの配置は覚えやすい。色: 天気表示で青=雨だが "many users associated it with 'blue skies'"（誤読の実例）。
- 逐語: skog-2003.txt L752-754 "(e.g. in our weather visualization blue means "rain" whereas many users associated it with "blue skies" ...)"。L683-686 "The arbitrary spatial mappings ... tended to be harder to remember than the ones where we used a geographical metaphor"。
- 位置づけ: 反例（色による天気写像は、利用者の連想とずれる）かつ、凡例なしで読めた人は少ない（L440-470 付近）。逆に「天気を状態の指標に使う」例ではなく、天気そのものの表示（天気=データ）なので、背景が天気で本人状態を示す案の直接証拠ではない。

## 3. Vogel & Balakrishnan 2004（公共の環境ディスプレイでの第三者閲覧の要件）
- 書誌: Daniel Vogel, Ravin Balakrishnan. "Interactive Public Ambient Displays: Transitioning from Implicit to Explicit, Public to Personal, Interaction with Multiple Users." UIST 2004, ACM, ISBN 1-58113-957-8/04/0010。DOI 未確認。
- 取れたもの: 本文全文 -> primary/vogel-2004.txt
- 内容: 設計原則とプロトタイプ。実験の数値は乏しい（初期ユーザーフィードバックのみ）。
- 逐語（L203-210）: "information considered totally innocuous to some is considered personally private to others" ; "People tend to be more voyeuristic with large displays"。
- 位置づけ: 根拠（何が「無害」かは見る人で違う。抽象化の水準で一律に決められない）。ただし「抽象表示から状態を読まれた」実証ではない。

## 4. Hudson & Smith 1996（awareness 表示の privacy–awareness 二重トレードオフ）
- 書誌: Scott E. Hudson, Ian Smith. "Techniques for Addressing Fundamental Privacy and Disruption Tradeoffs in Awareness Support Systems." CSCW '96 (Boston), p.248 以降（ファイル名 Hudson-CSCW96-p248 による。末尾ページ・DOI 未確認）。
- 取れたもの: 本文全文 -> primary/hudson-1996.txt
- 内容: 映像を 8x8 画素に粗くする等のぼかし手法（L492付近）。同期した数値評価は本文では確認していない（全文を精読していない）。
- 逐語（L33-39）: "the more information about oneself that leaves your work area, the more potential for awareness of you exists for your colleagues. Unfortunately, this also represents the greatest potential for intrusion on your privacy."
- 位置づけ: 根拠（情報量と漏れは表裏。抽象化=漏れゼロにはならず、設計で折り合う）。読み取りの実験ではない。

## 5. Consolvo ら 2008 UbiFit Garden（(a) への反例：自然の比喩だが蓄積する）
- 書誌: Sunny Consolvo, David W. McDonald, Tammy Toscos, Mike Y. Chen, Jon Froehlich, Beverly Harrison, Predrag Klasnja, Anthony LaMarca, Louis LeGrand, Ryan Libby, Ian Smith, James A. Landay. "Activity Sensing in the Wild: A Field Trial of UbiFit Garden." CHI 2008, Florence, Apr 5-10, 2008. DOI 未確認（本文に無い）。
- 取れたもの: 本文全文 -> primary/consolvo-2008.txt
- 設計: 3 週間現場試験 N=12。携帯の壁紙に庭（週内に花が咲き、目標達成で蝶、過去の達成は小さな白い蝶）。
- 逐語（L429-431, L449-451）: "The display uses the metaphor of a garden that blooms throughout the week" ; "the user is not punished for inactivity, for example, with wilting flowers, weeds, or a stormy sky."
- 位置づけ: 反例/対比。自然の比喩だが週で蓄積し、過去の達成も残る（蓄積・成長型）。逆に「嵐の空を悪い状態に使わない」と意図的に避けている点は、天気で状態を表さない制約と整合する先例。第三者の読み取りは本文に議論なし（grep で others/privacy の該当は主題外のみ）。

## 周辺（本文は読んでいない）
- Holmquist らの 3 段階理解（that/what/how）は登録済みのため再掲せず。
- Tomitsch ら "Towards a Taxonomy for Ambient Information Systems"（CEUR Vol-254 paper09）は本文取得済みだが分類論で今回の問いに直結せず未精読 -> primary/dl/ceur.txt
- Röcker & Magerkurth, "Privacy and Interruptions in Team Awareness Systems"（HCII 2007, DOI 10.1007/978-3-540-73279-2_31 は検索結果の記載のみ）: Hudson & Smith のトレードオフは本質的でないと論じるとの要約を検索結果で見ただけ。本文未読。
- Hutzler & Gortais の天気表示、arXiv 1612.07303（RGB-LED の雨雲=悲しみ、配色の文化差）、arXiv 2308.02831（affective visualization の総説）は検索結果の要約のみ。本文未読。

## 見つからなかったもの
- (a) 「蓄積も成長もしない」ことを明示して本人データを自然の動きに写した例: 探した語 "ephemeral/non-accumulating ambient display", "stateless". 該当ゼロ（UbiFit のように蓄積型が大半。今回の検索範囲では。網羅ではない）。
- (b) 天気・季節・空を人の状態/メール/ストレスの計器にした ambient display で、見る人の読み取り/誤読を測った研究: 検索 "weather metaphor email stress" で該当なし。天気を「天気データそのもの」に使う例（Skog, Hutzler）と、感情を雨雲などで表す設計論（LED 研究）のみ。写像の読み取り率を測った実験は見つからず。
- (c) 抽象的な周辺表示から同僚/画面共有の相手が本人の状態を実際に読み取った実験: 検索 "bystanders infer ... abstract visualization" で該当なし。得たのは自己評価の調査（Alt 2010）と設計論（Vogel, Hudson）のみ。shoulder surfing 文献は表示の抽象度との関連で該当ゼロ。
- 未実施: ACM DL / Google Scholar 直接検索（WebSearch のみ）、Fish'n'Steps (Lin 2006)、Ambient Orb / Ambient Umbrella、Mood/emotion 共有表示の追試。次の探索候補。
