# 抽出 X1（AF001・AF002・AF003・AF004・AF034・AF005）

共通の注意: ScienceDirect は自動取得に対し 403 / CAPTCHA を返した（WebFetch・curl・ブラウザの 3 経路）。CAPTCHA は迂回していない。`ai-fatigue-fulltext\AF034\b997adee_af034_sd_full.html` と `AF001\b997adee_af001_sd_full.html` は、どちらも本文ではなく ScienceDirect の「Are you a robot?」ページ（本文なし）。AF034 のフォルダの HTML は AF034 の本文ではない。

---

## AF001
1. 本文の入手: 出版社の版（CC BY-NC-ND）。`C:\Users\johnd\Downloads\ai-fatigue-fulltext\AF001\publisher_1-s2.0-S2451958826002605-main.pdf`（19 頁、私が pypdf で `publisher_main.txt` に抽出）。補足資料 `c7bca0ee_AF001_mmc1.docx` / `c7bca0ee_AF001_mmc1.txt`（Table S1–S13・Fig S1。S6 などの表の中身は txt では一部切れている）。他の `*_AF001.txt`（b997adee/c7bca0ee/ffbe473e）は同論文の抽出の写し。Table 1 の項目文は PDF の文字抽出では空で、`ffbe473e_af001_p6.png`（p.6 の画像）から読んだ。DOI 10.1016/j.chbr.2026.101186、Computers in Human Behavior Reports 23 (2026) 101186、受理 2026-06-26。
2. 研究の種類: 一次研究（実証データを集めた）。尺度開発・検証。Study 1 項目作成・専門家レビュー・内容妥当性、Study 2 EFA（横断）、Study 3 CFA・基準関連・収束/弁別妥当性・性別不変性（横断）、Study 4 2 週間の再検査。
3. 対象集団: Study 1 は専門家 3 名（上級研究者 2・大学院生 1）と学部生 5 名（判定者）（p.4）。Study 2・3 は Prolific の米国居住の成人、AI 利用経験者のみ（p.4, p.5）。Study 4 はシンガポールの心理実験を宣伝する Telegram チャンネルで募集（p.13）。調査の実施時期は本文に記載なし（読んだ範囲）。
4. N: 解析 N は研究ごとに別（単一値は付けない）。Study 1: 判定者 5（専門家パネル 3）。Study 2: N=300（除外の記載なし。全員が注意チェックを通過、p.4）。Study 3: 募集 295 → AI 未使用 5 名を除外 → 290（p.6）。Study 4: 122（平均年齢 24.15、p.13）。抄録の「717 人」は 300+290+122+5=717 と合う（Study 1 の判定者 5 名を含む。専門家パネル 3 名は含まない）。
5. AI・利用環境: 一般的な生成 AI の利用全般（特定の製品・課題なし）。「AI は上位語、プロンプト型の生成 AI を指すときは生成 AI」と書く（p.2）。Study 3 では「AI をどのくらい使うか」を 1 項目（0–4）で聞く。「(at least) a few times a week」が 92.41%（p.6）。
6. 疲労の測り方: 15 項目の AI Fatigue Scale、5 件法。4 下位尺度（認知過負荷 1–4、情動負担 5–7、行動回避 8–11、身体・感覚疲労 12–15）。出典は 5 つの既存尺度（社会メディア疲労ほか）を AI 向けに改作（Table S1、p.4）。AI は項目文に明示されている。前置きは「…it reflects your experience with AI」（Table 1、p.6）。例: 項目 8「I avoid using AI even when it could help me.」項目 11「I prefer doing tasks manually rather than using AI.」（行動回避。疲労の結果というより回避行動そのもの）。項目 5 は「I sometimes feel a little frustrated when AI does not produce the results I expect.」。著者は特性（疲労しやすさ）を測るとも書く（p.2）。
7. 主要結果: Study 2 は 30 項目から 15 項目へ（EFA、KMO .94、4 因子、RMSEA .05、TLI .97、説明分散 64%、α=.90）（p.5）。Study 3 の CFA は 2 次因子モデルで χ²(86)=126.01、CFI=.98、RMSEA=.05（p.10）。α=.92（p.7, p.12）。収束: 疲労評価尺度 r=.63、Chalder .52、MFI .59、画面疲労 .60、SNS 疲労 .63、AI テクノストレス（複雑性）.46・（過負荷）.18（p.11）。弁別: AI での批判的思考 .05、AI 依存 .11、AI への愛着 −.17（p.11）。基準関連: 疲労が高いほど現在の AI 利用が少ない b=−.29、β=−.27、R²=.07、利用削減意図が強い β=.33、R²=.11（p.10）。増分: 他の疲労・テクノストレスを入れても追加説明 8.38%（利用）・2.62%（削減意図）（p.11）。ノモロジカル: 否定的態度 r=.54、神経症傾向 .49、否定的感情 .47 など（p.11）。性別不変性は構成・測定・スカラー・厳密まで ΔCFI ≤.01（Table 2、p.12）。再検査 ICC(2,1)=.65（95%CI .53–.74）、下位尺度 .54–.71（p.13）。
8. 限界・要確認点: 著者の限界は、横断・相関で因果不可、サンプルの一般化（英語圏・成人）、基準 2 項目が単項目の自己報告（p.14–15）。読んで気づいた点: (a) 疲労尺度の行動回避 4 項目の中身が結果変数（利用頻度・削減意図）と重なる。著者も重なりに言及し、行動回避を除く版でも結果は残ると報告（p.10）。(b) 再検査 ICC .65 は著者自身が「moderate」と書く。再検査標本は Telegram・平均 24 歳（Study 2・3 は米国の成人 Prolific で別集団）。(c) Study 2 の α=.90 と Study 3 の α=.92（抄録は .92）、認知下位尺度の α も .81（Study 2）と .85（Study 3）で値が違う（標本が別なので不整合ではない）。(d) 実施時期の記載なし。
9. データ・コードブック・解析コードの公開: 「All datasets have been made publicly available via ResearchBox: https://researchbox.org/6748.」（p.3, p.15 Data availability）。コード公開の記載は読んだ範囲に記載なし。
10. 倫理: 著者の大学の IRB、番号 IRB-25-197-A159 (925)（p.3）。参加は任意、全研究で同意を得たと記載。
11. 品質の材料: 組み入れ基準は AI 利用経験者（Study 2・3）、Study 3 は事前登録の組み入れ基準に従う、4 つの注意チェックのうち 3 つ以上通過（p.6）。事前登録は「Studies 2–4 で事前登録の設計・解析・標本計画に従った」とあるが（p.3）、登録先の URL・ID は本文に記載なし（Study 1 は事前登録の対象外）。標本サイズの根拠: CFA は RMSEA 検出力で n=291（99%）（p.6）、再検査は Bonett 法で n=89 以上（p.13）。内容妥当性: 判定者 5 名・psa/csv 基準 .72/.51、30 項目で psa=.97、csv=.95（p.4）。構造: EFA→別標本の CFA、AVE .58–.76、第 2 次 AVE .59（p.10）。内的一貫性: α と複合信頼性 .85–.90（p.12）。再検査: 上記。基準関連: 上記。交絡の統制: 基準関連の増分で他の疲労尺度・テクノストレスを入れた（p.11）、MIMIC で人口統計を同時に投入（p.11–12）。性格・年齢の統制は主解析にはない。解析: R（lavaan, MLR）。WLSMV の感度分析（Table S13）。
12. 『AI適格性評価』の次の確認・作業（出版社版と補足の項目・登録計画を照合。日本語版での妥当性を既検証としない）: 出版社版の項目（Table 1、p.6）は確かめた。補足の Table S6 は 30 項目、Table S8 は 15 項目の EFA 負荷量。登録計画の中身（登録先・登録日）は本文・補足の抽出では確かめられない（URL なし）。日本語版は本文に記載なし（英語版のみ、p.14 の限界で他言語は今後の課題と書く）→ 既検証とはいえない。
13. 確認事項の行: なし。
14. ほかに確かめること: 本文の表は Table 1（15 項目尺度、p.6）と Table 2（性別不変性の適合度、p.12）の 2 つだけ。図は Fig. 1（CFA）、Fig. 2、Fig. 3。本文に「Table 6」は無く、本文から「Table 6」を参照する箇所も無い（全文 grep で 0 件）。補足の Table S6 は「30-Item Scale Used for EFA」（本文 p.4 が参照）。補足は Table S1–S13 と Fig S1（S1 改作元尺度、S2 初期 60 項目、S3・S4 専門家・判定者への指示、S5 32 項目、S6 30 項目、S7 Study 2 人口統計、S8 15 項目の EFA、S9 Study 3 人口統計、S10 Study 4 人口統計、S11 AI テクノストレス項目、S12 MLR の CFA、S13 WLSMV の CFA）。4 研究: Study 1 N=5（判定者）、国の記載なし、募集は学部生・専門家（方法の記載は薄い）、事前登録なし（本文の事前登録の範囲は Study 2–4）。Study 2 N=300、米国、Prolific、あり。Study 3 N=290（募集 295）、米国、Prolific、あり。Study 4 N=122、シンガポール、Telegram チャンネル、あり。

---

## AF002
1. 本文の入手: 入手不可（抄録のみ）。ただし抄録も取れていない。OpenAlex は closed、出版社ページは 403、CAPTCHA あり。Crossref・Semantic Scholar・OpenAlex・Europe PMC に抄録の本文なし（abstract = null）。得たのは書誌のみ（著者 Hui Yang・Yu Zeng・Huizi Xing・Peng Hu、Crossref 参考文献 75 件、OpenAlex の公表日 2025-11-26、Int J Inf Manag）。URL: https://doi.org/10.1016/j.ijinfomgt.2025.103010
2–11. 読んでいない（本文・抄録とも未取得）。推測で埋めない。
12. 次の確認（項目の原尺度との対応、交絡調整、事前登録の有無）: 確かめられない（本文なし）。
13. なし。
14. N・時期・場・国・著者: 著者は上記（確認済み、Crossref）。N・時期・募集の場・国は読んでいない。AF003 との関係: 著者が重なる（AF002 は Hui Yang が筆頭、Peng Hu が最後。AF003 は Hui Yang 筆頭・Jinqiang Wang・Peng Hu。Peng Hu は ORCID 0000-0003-1624-466X が両方で一致）。同一標本かは判断材料が無い（本文を読んでいない）。応答の不確実性 vs プロンプトの不確実性の係数は読んでいない。

## AF003
1. 本文の入手: 入手不可（抄録のみ・ただし抄録も取れていない）。OpenAlex は closed、出版社ページは 403、CAPTCHA あり。書誌のみ（Hui Yang・Jinqiang Wang・Peng Hu、Crossref 参考文献 62 件、OpenAlex の公表日 2026-06-23、Computers in Human Behavior）。URL: https://www.sciencedirect.com/science/article/pii/S0747563226001949
2–11. 読んでいない。
12. 次の確認（リテラシーの主効果・交互作用・非有意結果を別々に抽出）: 確かめられない。
13. なし。
14. AF002 の項を参照。N・時期・場・国・2 本の標本の同一性は読んでいない。著者は一部重なる（上記）。

---

## AF004
1. 本文の入手: 入手不可（抄録のみ）。出版社の本文は 403 / CAPTCHA。OpenAlex は gold だが、PMC に無い（Europe PMC: pmcid なし、ライセンス表示 cc by-nc、本文なし）。使った材料: Europe PMC の抄録 `C:\Users\johnd\Downloads\ai-fatigue-fulltext\AF004\europepmc_abstracts.txt`（PMID 41076923）。
2. 研究の種類: 抄録から: 一次研究、横断の質問紙、調整付き媒介モデル（PROCESS Model 8）。
3. 対象集団: 中国の大学生（抄録）。募集の方法・時期は読んでいない。
4. N: 580（抄録: 「Data were collected from 580 Chinese university students」）。除外などの注記は読んでいない。
5. AI・利用環境: 学生の「AI 依存」（学習での AI 支援）。細部は読んでいない。
6. 疲労の測り方: 抄録は「cognitive fatigue」を媒介変数とする。尺度・項目・AI 明示の有無は読んでいない。なお抄録は調整変数を「information literacy」と書く一方、原題は「AI literacy」（食い違い。本文未確認）。
7. 主要結果（抄録のみ）: AI 依存が高いほど批判的思考が低く、認知疲労が部分媒介。情報リテラシーは AI 依存の批判的思考への負の影響を緩衝する一方、AI 依存が高いときは認知疲労を増幅した（交互作用の向き・係数は読んでいない）。
8–11. 読んでいない。
12. 次の確認（原著と訂正通知の全文を対にして確認。『参考文献のみの訂正』と断定しない）: 確かめられない（訂正の全文を取れていない）。
13. 確認事項（訂正全文を確認し原著の抽出に反映）: 確かめられない。AF034 の本文なし。
14. 訂正通知の変更箇所・原著の抽出値への影響: 読んでいない。したがって「参考文献のみ」とも「表・係数の訂正」とも言えない。

## AF034
1. 本文の入手: 入手不可。DOI 10.1016/j.actpsy.2026.107179（出版社の中間ページは https://linkinghub.elsevier.com/retrieve/pii/S0001691826009807）。Europe PMC（PMID 42225464）に抄録なし、本文なし。Semantic Scholar も抄録 null。フォルダの `b997adee_af034_sd_full.html` は CAPTCHA ページ（本文ではない）。
2–11. 訂正通知であること以外は読んでいない（書誌: Tian J, Zhang R、2026-06-01 公開、Acta Psychologica）。
12. 次の確認（訂正本文を取得して対象箇所と影響を確認し AF004 の抽出値を更新）: 確かめられない。
13. 確認事項: 確かめられない（訂正全文を未取得）。
14. 訂正の変更箇所（表・本文・文献）と原著の抽出値（交互作用の向き・係数）への影響: 読んでいない。AF004 の抄録の「AI 依存×リテラシーが認知疲労を増幅」の向きが訂正で変わるかは確かめられない。

---

## AF005
1. 本文の入手: 出版社の版（Frontiers、CC BY）。`C:\Users\johnd\Downloads\ai-fatigue-fulltext\AF005\frontiers.pdf`（14 頁）、`frontiers.txt`（抽出）、`pmc.html`（PMC13501034）。URL: https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2026.1879080/pdf 。受理 2026-07-10、公開 2026-08-10。
2. 研究の種類: 一次研究。横断の質問紙、PLS-SEM（SmartPLS 4.0）。媒介と調整（認知・感情・行動の枠組み）。
3. 対象集団: 中国。生成 AI の利用者。オンライン調査プラットフォーム「Wenjuanxing（問卷星）」から SNS で配布（p.5）。調査の時期は記載なし（読んだ範囲）。女性 65.3%、25 歳以下 81.7%（本文の「80%」と表で数字がずれる、p.5 と Table 1）、学部生 72.1%（Table 1）。著者は中国の大学（Guangdong Ocean University）。
4. N: 426（有効）。500 回収 → 426 に除外（回答時間が極端に短い・80% 以上同一回答・論理的な矛盾・外れ値、p.5）。
5. AI・利用環境: 生成 AI 全般（文章作成 72.8%、情報検索 66.9% など）。ほぼ毎日以上が 50.2%（Table 1: 19.2%+31.0%）。
6. 疲労の測り方: 「認知疲労」を AI 誤情報疲労（8 項目）と AI プライバシー疲労（8 項目）の 2 尺度で測定。Choi ら（2018）から改作（p.7、Table 2）。7 件法。項目の要点: 「Repeated verification of the authenticity of AI-generated information has left me affectively exhausted.」「I've lost interest in assessing the reliability of AI-generated content.」（Table 2、p.8）。AI は項目に明示。一般的な AI 疲労（AI 使用そのものの疲労）ではなく、検証・リスク管理に特化した疲労。
   負担・無力感・回避の含み方（項目文の要点、各尺度 8 項目）: 負担（exhausted / tired of constantly evaluating / monitoring）は各尺度の前半 4 項目。無力感・無意味感（「my efforts … have any real impact」「worrying … is pointless」「skeptical whether adjusting privacy settings will make any difference」）が各尺度の 2 項目。回避・関与低下（「lost interest in assessing」「less proactive in identifying misinformation / protecting personal data」）が各尺度の 2 項目。使用回避そのもの（AI の使用を減らす）の項目は疲労尺度には無く、別の尺度「AI 利用中止意図」（5 項目）で測る。
7. 主要結果: 誤情報リスク知覚 → 誤情報疲労 β=0.469、プライバシーリスク知覚 → プライバシー疲労 β=0.420（Table 5、p.10）。疲労 → AI 不安: 誤情報疲労 0.196、プライバシー疲労 0.213。リスク知覚 → AI 不安は直接 0.153 と 0.316。間接効果 0.092（CI .033–.160）と 0.089（CI .042–.140）（Table 6、p.11）。VAF 37.6% と 22.0%。AI 不安 → 利用中止意図 β=0.195（p<.001）。AI 依存の調整 β=−0.107（CI −0.190 から −0.016、p=0.015）。R²: 誤情報疲労 0.220、AI 不安 0.471、利用中止意図 0.223（p.7）。疲労から利用中止意図への経路は直接検定されていない（疲労は不安への経路でのみ検定。モデルの経路は H1–H10 で H7・H8 は媒介）。
8. 限界・要確認点: 著者の限界: 横断データで因果不可・共通方法分散、生成 AI のみ、リスクの種類が 2 つ、AI 依存のみを調整変数に、標本が若年・高学歴（p.12）。読んで気づいた点: (a) 抄録は「misinformation risk and privacy risk … increase AI anxiety, and this effect is further strengthened by increased … fatigue」と書き、「cognitive fatigue が媒介」とも書く。本文の効果は部分媒介（間接効果は総効果の 37.6%/22.0%）で、表記に強弱の揺れ。(b) 年齢の「80%（18–25 歳）」（p.5）と Table 1 の 81.7%（25 歳以下）。(c) 利用中止の項目 5 のうち「I plan to gradually reduce my reliance」を含む（意図）。実際の利用の中止ではなく意図（著者も記載、p.7）。(d) AI 依存尺度 4 項目の中身は「AI を使いすぎる」「人間関係を害した」など問題的使用に近い（Table 2）。
9. データ・コードブック・解析コードの公開: 「The datasets presented in this study can be found in online repositories. The names of the repository/repositories and accession number(s) can be found in the article/supplementary material.」（p.12）。ただし本文中に名前・番号は見当たらない（読んだ範囲では記載なし。補足は未取得）。
10. 倫理: 「Ethical review and approval was not required … in accordance with the local legislation and institutional requirements. The participants provided their written informed consent」（p.13）。承認機関・番号は記載なし。
11. 品質の材料: 組み入れ基準は生成 AI 利用者（頻度の下限は Table 1 に「rarely」まで含む）。除外基準は上記。測定: 既存尺度の改作（Table 2）、α>.8（.843–.943）、CR .865–.956、AVE .566–.814、HTMT<.90、Harman 31.23%、完全共線性 VIF 1.000–1.963（p.7, Table 3）。交絡の統制: 年齢・性別・学歴・利用頻度を共変量に入れたかは記載なし（読んだ範囲で、モデルは Fig. 2 の経路のみ）。事前登録: 記載なし。サンプルサイズの根拠: 記載なし。SRMR 0.075（p.7）。
12. 次の確認（疲労項目が負担・無力感・回避をどこまで含むか確認し、一般 AI 疲労と層別化）: 確かめた。項目は上の 6 のとおり、疲労は「誤情報の検証」「プライバシー管理」という特定の負担に限られ、一般的な AI 利用疲労の尺度ではない。層別化に使う箇所: Table 2（p.8）。
13. なし。
14. 疲労項目が負担・無力感・回避をどこまで含むか: 上の 6 に項目文の要点を記載。
