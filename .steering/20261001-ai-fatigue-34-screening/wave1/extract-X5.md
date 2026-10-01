# 束 X5 抽出（AF025〜AF033）

注: 判定はしていない。逐語は短く、箇所つき。ブラウザ（実際の Chrome）で T&F のページを開いて本文を読めたのは AF025 のみ。Tilburg・RGU のページはボット検査（Cloudflare 系）で止まったため、検査は回避せず、そこで打ち切った。

## AF025
1. 本文の入手: 出版社（Taylor & Francis）の全文ページ https://www.tandfonline.com/doi/full/10.1080/10494820.2019.1674887 を Chrome で開いて本文を読んだ（版: 出版社版）。curl は 403（ボット検査）。ファイルは保存していない（ページのテキストを直接読んだ）。ページの表示は "Open access" ラベルあり。ライセンス条文はページ本文には見つからず、Crossref のメタデータは CC BY-NC-ND 4.0（2019-10-14 起算）、OpenAlex も cc-by-nc-nd。
2. 種類: 尺度開発（AI 不安尺度 AIAS）と、動機づけ学習行動の予測への初期の適用。
3. 対象・場面: 台湾のオンライン調査（surveycake）。一般の回答者（職業等の多様な背景）。AI 技術・製品一般に対する不安。
4. N: 1 つの標本 301 人（Abstract・§3.2・Table 1 の見出し n = 301）。研究は 1 つのみ。項目の専門家レビュー: IS 教授 2・AI 専門家 2・AI 利用者 4（§3.1）。
5. 要点: 構成概念 = AI 不安（AIA）。§2.2 の定義「an overall, affective response of anxiety or fear that inhibits an individual from interacting with AI」。項目プール 59 → 重複で 9 削除 → 50 項目 + 全体 2 項目 + 行動意図 5 項目 = 探索用 57 項目（§3.1）。7 件法リッカート（§3.1）。項目の整理: 補正済み項目-全体相関 <0.40 の Q31・Q50 を削除し 48 項目、α = 0.986（§4.1）。EFA（PCA・バリマックス）で固有値 >1 の 4 因子、分散の 79.638%（§4.2）。最終 21 項目・4 下位尺度（learning・job replacement・sociotechnical blindness・AI configuration）。α 全体 0.964、learning 0.974、job replacement 0.917、sociotechnical blindness 0.917、AI configuration 0.961（§4.3）。基準関連妥当性 r = 0.864（全体 2 項目との同時点、§4.5）。収束・弁別: 下位尺度間相関の信頼区間が 1.00 を含まない（§4.6）。法則的妥当性: 動機づけ学習行動との r = 0.190, p < 0.01（§4.7）。得点の範囲は 21〜136、平均 91.409、SD 26.570（§6）。例項目（付録 A）: 「Learning to use AI techniques/products makes me anxious.」AI に直接触れる（AI への不安の尺度）。疲労の尺度ではない。
6. 限界: 著者記載（§7）= CFA が未実施で今後必要、非無作為標本、21 項目の構造の再確認、再検査信頼性が未検証。確認点: §4.2 は探索的分析と同じ標本で項目を選んでおり、独立標本での確認はない（著者は CFA を今後の課題と書く）。因子ごとの項目数は Table 2 を読んでいない（本文テキストに出ない）。
7. 利用条件: 尺度の使用許諾の記載は本文に見つからない（読んだ範囲）。論文ライセンスは上記（CC BY-NC-ND と Crossref・OpenAlex が示す。出版社ページの条文は未確認）。
8. 次の確認・作業（原著と補足資料で項目・利用条件・版・測定特性を確認。オンライン年 2019 と巻号年 2022 を区別）: 項目 = 確かめた（付録 A に 50 項目の全文、最終 21 項目は Table 2 で、Table は本文テキストに含まれず未読）。測定特性 = 確かめた（上記 §4.1〜4.7）。年 = 確かめた（下記 10）。利用条件 = 確かめられない（尺度の許諾の記載なし。補足資料は見ていない）。
9. 確認事項（年の二重管理）: 確かめた。出版社ページの表示「Pages 619-634 | Received 12 Feb 2019, Accepted 23 Aug 2019, Published online: 14 Oct 2019」と「Interactive Learning Environments Volume 30, 2022 - Issue 4」。Crossref も published-online 2019-10-14、published-print 2022-04-03、volume 30 issue 4 pages 619-634。
10. ほかに確かめること: オンライン公開 2019-10-14、巻号 Vol. 30, Issue 4（2022）。項目数: 21 項目（最終）。因子数: 4。

## AF026
1. 本文の入手: C:\Users\johnd\Downloads\ai-fatigue-fulltext\AF026\b997adee_AF026.txt（.pdf も同じ場所）。Computers in Human Behavior Reports 4 (2021) 100119 の出版社版（CC BY、p.1 冒頭の表記）。
2. 種類: 尺度開発（Zoom Exhaustion & Fatigue Scale、ZEF）。5 研究（Table 1）。
3. 対象・場面: ビデオ会議（Zoom）後の疲労。Mechanical Turk・大学の調査プール・Lucid・便宜標本。
4. N（Table 1・各 Study）: Study 1 インタビュー N = 10（Table 1。本文のインタビュー人数は未精査）／Study 2 予備実施 N = 52／Study 3 尺度実施 N = 395（MTurk）／Study 4 信頼性 N = 130（大学プール + Lucid、学生 73・Lucid 57）／Study 5 次元性と妥当性 N = 2724（便宜標本）。Abstract は「395」と「2724」を挙げる。
5. 要点: 構成概念「Zoom fatigue」（疲労の既存定義・ソーシャルメディア疲労・対人／非言語コミュニケーションの 3 領域から理論づけ）。項目プール 49 → 15 項目（Abstract・§Study 3）。5 下位尺度×3 項目: general・visual・social・motivational・emotional。5 件法（1 = Not at all 〜 5 = Extremely。頻度の 2 問は Never〜、Table 3 の注）。プロンプト「After video conferencing …」（Table 2 の注）。測定特性: Study 3 の CFA で CFI 0.942・TLI 0.929・RMSEA 0.086・SRMR（§Study 3）。Study 4 の第 2 次 CFA で CFI 0.944・TLI 0.930・RMSEA 0.086・SRMR 0.060。Study 5 で CFI 0.97・TLI 0.96・RMSEA 0.065・SRMR 0.032。α: Study 4 は各因子 0.83〜0.89、Study 5 は Table 5 の α 0.82〜0.90（Table 5 は読んだ）、CR 0.83〜0.90、AVE 0.63〜0.76。妥当性: 頻度・長さ・バースト性が ZEF 得点と正の関連、態度と r = −0.48（Table 7）。AI には触れない。
6. 限界（「Limitations and future directions」）: 便宜標本で一部の民族の代表性が低い、5 次元が強く相関し依存的（短縮版の作成を提案）、教育・職業の質問がない版がある、再検査信頼性など妥当性・信頼性の全種類は未評価。内部の注意: Study 3・4 の RMSEA は 0.086（Study 5 は 0.065）。Study 5 の χ2(85) = 1058（Table でなく本文 §Results）。
7. 利用条件: 論文は CC BY（p.1）。尺度の使用許諾の別記は見当たらない（付録に項目全文あり）。
8. 次の確認・作業（AI 文脈に流用された項目と原項目の差を確認。AI 疲労専用尺度の検証数に加えない）: 原項目の確認 = 確かめた（Table 3 の 15 項目は「video conferencing」を主語とする疲労項目。例: 「How tired do you feel after video conferencing?」）。AI 文脈への流用は本論文に出ない = 確かめられない（本論文の範囲外、別の論文側で確認が要る）。
9. 確認事項: 入力に行なし。
10. ほかに確かめること（AI の文脈の例を論文自身が挙げているか）: 挙げていない。本文テキストの検索（artificial・AI・chatbot）で該当なし（「Otter.ai」が転写ツール名として出るのみ）。

## AF027
1. 本文の入手: 入手不可（抄録のみ）。OpenAlex は closed。出版社ページ・Lancaster の eprint（OpenAlex 上で submittedVersion の記載）は取りに行っていない（時間・確認なし）。抄録・書誌は Crossref（出版社が登録）: Information Systems Research 19(4):417–433、2008 年 12 月（Crossref の published-print）。著者 T. S. Ragu-Nathan, M. Tarafdar, B. S. Ragu-Nathan, Q. Tu。
2. 種類: 概念開発と実証（尺度を含む。技術ストレス）。
3. 対象・場面: 組織の ICT 利用者（エンドユーザー）。抄録のみ。
4. N: 読んでいない（抄録に出ない）。
5. 要点（抄録のみ）: 「stress experienced by end users of Information and Communication Technologies」を技術ストレスとし、職務満足・組織コミットメント・継続意図への影響を、Transaction-Based Model of stress を基に検証する。項目数・下位尺度・測定特性は読んでいない。
6. 限界: 読んでいない。
7. 利用条件: 読んでいない。
8. 次の確認・作業（原項目と AI 研究での改変項目の対応を追跡）: 確かめられない（原項目を見ていない）。
9. 確認事項: 入力に行なし。
10. 束ごとの追加: 入力に指定なし。

## AF028
1. 本文の入手: 全文は取れなかった。C:\Users\johnd\Downloads\ai-fatigue-fulltext\AF028\b997adee_AF028_tilburg.html（Tilburg の研究ポータルの記録ページ）と PubMed XML（AF028\pubmed_12670612.xml）で抄録のみ。ポータルは PDF（/files/510406/psychometric.pdf、"Final published version, 119 KB" と表示。OpenAlex は submittedVersion と記載）を載せるが、curl も Chrome もボット検査（403・「セキュリティ検証」）で止まった。検査は回避していない。→ 入手不可（抄録のみ）。
2. 種類: 尺度開発（Fatigue Assessment Scale、FAS）。
3. 対象・場面（抄録）: 週 20 時間以上働く労働者。縦断研究の一部。
4. N: 読んでいない（抄録に N なし）。
5. 要点（抄録のみ）: 10 項目の疲労尺度。内的一貫性が高い、他の疲労尺度 4 種と強く相関、5 つの疲労質問紙の因子分析で FAS が 1 因子解で最高の負荷、疲労と抑うつ・情緒安定性は別構成概念。性別バイアス: 10 項目中 8 項目は無バイアス、2 項目に一様バイアス（抄録）。回答形式・採点・α の値は読んでいない。AI には触れない（抄録）。
6. 限界: 読んでいない。
7. 利用条件: 読んでいない。
8. 次の確認・作業（原著全文・対象集団・採点・翻訳版の測定特性と利用条件）: 対象集団 = 抄録のみで確かめた（労働者）。採点・翻訳版・利用条件 = 確かめられない。
9. 確認事項: 入力に行なし。
10. ほかに確かめること（AI の文脈の例）: 確かめられない（全文未読。抄録に AI の記載なし）。書誌（Tilburg 記録）: J Psychosom Res 54(4), 2003, 345–352。

## AF029
1. 本文の入手: C:\Users\johnd\Downloads\ai-fatigue-fulltext\AF029\b997adee_AF029.txt（.pdf も同じ場所）。Behav Res (2013) 45:1058–1072、オンライン公開 2013-04-10（p.1）。Springer 版。
2. 種類: 尺度開発（認知負荷の 3 種を測る 10 項目、Leppink ら）。
3. 対象・場面: オランダの大学の統計学の講義（学部生・博士課程）。Study IV は統計の例題を学ぶランダム化実験。
4. N: Study I = 56（博士課程、PCA、3 つの項目順）／Study II = 171（心理学 2 年）／Study III = 136 と 148（それぞれ別の講義。抄録は ns = 171, 136, and 148 と一括で CFA の標本として記載）／Study IV = 58（健康科学の新入生、各群 29）。予備調査（ベルギーの大学、100 + 67 人、§導入）。
5. 要点: 認知負荷理論の内在的負荷（IL: 項目 1–3）・外在的負荷（EL: 4–6）・学習関連負荷（GL: 7–10）の 10 項目。形式: 0（全くない）〜10（完全にそうだ）の 11 段階、直前に終わった「活動（講義・授業等）」について回答（付録 1）。例: 「The topic/topics covered in the activity was/were very complex.」。測定特性: Study I α = .81（IL）・.75（EL）・.82（GL）。Study II α = .85/.80/.89（Table 8）。Study III α は .88/.81/.93 と .81/.85/.91（Table 8 の 2 講義）。10 項目のみのモデルは χ2(30) = 30.298, CFI = 1.000, RMSEA = .008（Study III 本文）。因子間相関 IL–EL .41、IL–GL .33、EL–GL −.19（Study II）。Study II では Ayres・Paas 等の既存 4 項目（付録 2）は 3 因子と異なる挙動。疲労・倦怠の項目はなく、「mental effort」の既存項目（Paas）が別に付く。AI には触れない。
6. 限界（本文）: Study I は標本が小さい（予備的）。授業間の課題の違いで IL・EL・GL の関係の解釈が難しい。Study IV の限界: 2 つの形式のあとに 1 回しか事後テストがなく、各形式の寄与を分けられない。順序効果。GL の事後得点が成績を予測する証拠は限定的。要確認: Study III で Study II と有意性が一致しない係数があるとの記述（本文 §Study III）は精査していない。
7. 利用条件: 尺度の使用許諾の記載は読んだ範囲に見当たらない。付録 1 に全項目あり。論文のライセンスは未確認（Springer の bronze 版と OpenAlex は記す）。
8. 次の確認・作業（測定時点・下位尺度・対象課題の対応を確認。負荷低下を疲労軽減と数えない）: 測定時点 = 確かめた（Study I 講義の最後に紙、付録 1「activity that just finished」、Study IV は事前知識テストの後・各学習形式の後・事後テストの後）。下位尺度 = 確かめた（IL/EL/GL の対応は上記）。対象課題 = 確かめた（統計の講義・例題）。疲労との対応は本文に出ない（疲労・倦怠の語なし）ため、負荷の低下を疲労の軽減と読む根拠は本論文にない。
9. 確認事項: 入力に行なし。
10. ほかに確かめること（AI の文脈の例）: 挙げていない。本文テキストの検索（artificial・AI・chatbot）で該当なし。「statistics」を他の領域に置き換えてよいとする記述がある（§導入、Item 8 の説明）。

## AF030
1. 本文の入手: C:\Users\johnd\Downloads\ai-fatigue-fulltext\AF030\b997adee_AF030.txt（.pdf も同じ場所）。White Rose の採択原稿（Accepted Version、巻号頁 Ann Intern Med 169 に当たる pp. 467–473 の記載あり。冒頭ページ）。出版社版ではない。再利用は著作権表示つき（冒頭「Reuse」）。
2. 種類: 報告の指針（PRISMA-ScR）の開発と解説。
3. 対象・場面: スコーピングレビューの報告。
4. N: 専門家パネル 37 人に依頼し 31 人が完了（§3.1 の記述）。第 1 ラウンドは対面 16 人・e-Delphi 15 人。第 3 ラウンドは 27 人に依頼し 24 人が完了。ワークショップ 30 人（Global Evidence Summit 2017）。
5. 要点: 指針は 20 項目 + 任意 2 項目（抄録・§3.7）。元の PRISMA の 27 項目から 5 項目を削除（13・15・16・22・23。Table の「Not applicable」）、2 項目を任意（12・19、批判的吟味）、全項目の文言を修正（§4）。独立・重複作業については項目 10（データ抽出 charting）に「whether data charting was done independently, in duplicate」を記載例として挙げる。項目 9（選定）は過程を述べるよう求める。項目 12・19 は「If done」。
6. 限界: 本文の「Limitations」節は未精読（時間）。
7. 利用条件: 採択原稿の再利用は上記。指針自体の使用条件は読んでいない。
8. 次の確認・作業（実施した方法に即して記載し、未実施の独立判定・品質評価を実施済みとしない）: 確かめた。項目 9 は選定の過程を「State the process」、項目 10 は独立・重複の実施の有無を述べる例、項目 12・19 は「If done」で、実施していない批判的吟味は「実施した」と報告する必要がない（任意）。独立判定を必須とする記載はない（Table 1）。
9. 確認事項: 入力に行なし。
10. 束ごとの追加: 入力に指定なし。

## AF031
1. 本文の入手: 全文は取れなかった。RGU リポジトリ（https://rgu-repository.worktribe.com/output/979072）は Chrome でもボット検査で止まり、検査は回避していない。PubMed XML（C:\Users\johnd\Downloads\ai-fatigue-fulltext\AF031\pubmed_33038124.xml）と Crossref で書誌・抄録のみ。→ 入手不可（抄録のみ）。
2. 種類: 方法の手引き（JBI のスコーピングレビュー手引きの更新）。
3. 対象・場面: スコーピングレビューの実施。
4. N: 該当なし（読んでいない）。
5. 要点（抄録）: 目的は JBI のスコーピングレビュー手引き更新の説明と PRISMA-ScR との整合。JBI の手引きは 2014 年に作成、2017 年に小改訂、2020 年に更新。2015〜2020 年にグループが文献レビュー・会合・ワークショップを実施。更新点: スコーピングレビューが適切かどうか、抽出・分析・提示の方法、実践と研究への示唆。段階数・項目数は本文を読んでいない。
6. 限界: 読んでいない。
7. 利用条件: OpenAlex は RGU の版を cc-by-nc の submittedVersion と記載（Crossref に license なし）。本文は未確認。
8. 次の確認・作業（完全な書誌と現行 JBI 手引きを確認し、選定・抽出手順を事前に固定）: 書誌 = 確かめた（下記 10）。現行 JBI 手引き・選定・抽出手順 = 確かめられない（本文未読。抄録は「updated in 2020」まで）。
9. 確認事項（著者リスト未完）: 確かめた。PubMed と Crossref（OpenAlex も同数）で著者は 9 名。
10. ほかに確かめること: 著者（PubMed の順）Micah D J Peters, Casey Marnie, Andrea C Tricco, Danielle Pollock, Zachary Munn, Lyndsay Alexander, Patricia McInerney, Christina M Godfrey, Hanan Khalil。書誌: JBI Evidence Synthesis 18(10):2119–2126（PubMed XML の Volume・Issue・MedlinePgn）。出版年は Crossref の issued が 2020-09-22（オンライン 2020 年 10 月の記録もある）。出版社ページの表示は未確認。

## AF032
1. 本文の入手: C:\Users\johnd\Downloads\ai-fatigue-fulltext\AF032\b997adee_AF032.txt（.pdf も同じ場所）。Qual Life Res 27:1147–1157（2018）、オンライン 2018-02-12（p.1）。Springer の出版社版・オープンアクセス（CC BY 4.0、本文末のライセンス表記）。
2. 種類: 方法の手引き（PROM の系統的レビューのガイドライン）。
3. 対象・場面: 患者報告アウトカム尺度（PROM）の測定特性の系統的レビュー。
4. N: 該当なし（ガイドライン）。
5. 要点: 10 段階（Abstract・Fig. 1）。Steps 1–4 = 準備・検索・選定、Steps 5–8 = 研究の質・測定特性・解釈可能性・実行可能性の評価、Steps 9–10 = 推奨の作成と報告。Step 4 は「選定は 2 人の査読者が独立に行うことが一般に推奨」と記載。Part B で COSMIN Risk of Bias チェックリスト（very good / adequate / doubtful / inadequate）、結果は基準で評価、全体は修正 GRADE（Table 2: 総 n 50–100 で −1、n < 50 で −2 など）。Step 6（内部構造）は反映的モデルに限る旨の記載（Step 6 冒頭）。評価順は 内容妥当性（Step 5）→ 構造（6.1 構造妥当性・6.2 内的一貫性・6.3 文化間妥当性）→ 他の特性（Step 7）。
6. 限界（Discussion）: ガイドラインの作成は Delphi 等の構造化された過程によらない。方法の適用は 1 件のレビュー（内容妥当性と構造妥当性）のみ。検索のデータベース、検索フィルタ、統計的な統合、標本サイズ規則の根拠などが今後の課題。非 PROM のレビューにも使えるが「steps 5–7 should be adapted」（Discussion）。
7. 利用条件: CC BY 4.0（本文末）。
8. 次の確認・作業（適用する領域と修正点を明記し、尺度別の全文・補足情報を揃えてから正式評価）: 部分的に確かめた。非 PROM への適用は Step 5–7 の修正が必要と著者が書く（Discussion）。心理学・技術の尺度への適用例は本論文にない。尺度別の全文・補足は本論文の範囲外。
9. 確認事項: 入力に行なし。
10. 束ごとの追加: 入力に指定なし。

## AF033
1. 本文の入手: C:\Users\johnd\Downloads\ai-fatigue-fulltext\AF033\b997adee_AF033.txt（.pdf も同じ場所）。J Clin Epidemiol 196 (2026) 112314（出版社版、Amsterdam UMC の機関リポジトリ表紙に Publisher's PDF）。受理 2026-05-01、オンライン 2026-05-08、巻の公開日 2026-08-01（表紙）。
2. 種類: スコーピングレビュー（PRISMA-ScR 更新のための根拠の整理）。指針そのものではない。
3. 対象・場面: スコーピングレビューの報告指針と、スコーピングレビューの報告の評価（13 件の概観）。MEDLINE・Embase・Cochrane Methodology Register と灰色文献。
4. N（件数）: §3.1 検索 10,787 + 灰色文献等 770、重複 3,292 除去、8,265 を題目・抄録で選別、8,110 を除外、全文 155、104 除外。抄録は「43 unique documents（13 overviews of ScRs と 30 guidance documents）」。本文は「47 papers: 43 studies、元の PRISMA-ScR 2018 論文、3 件の随伴報告」（§3.1）。
5. 要点: 37 の追加の報告項目の候補を同定し、後続の Delphi で評価するとの位置づけ（抄録 Results）。最も多い追加項目は目的 67.4%、適格基準 62.8%、検索戦略 51.2% など。著者は将来 Delphi と合意会議を経て新指針を作ると記す（結論近く）。
6. 限界（本文「limitations」）: 見落としの可能性、データ抽出は重複でなく 1 人抽出 + 1 人確認、検索は 20 か月以上前で未更新、項目の分類誤りの可能性、含めた研究の質は評価していない（JBI は質評価を任意とすると付記）。
7. 利用条件: 表紙は「Document license CC BY」、論文本文の末尾は CC BY-NC 4.0 の記載（食い違い）。
8. 次の確認・作業（Delphi 等の後続研究と正式な改訂版の公表を別に確認）: 確かめられない。本文は「Results from this PRISMA-ScR update process are forthcoming in the next year」と書く（結論近く）。公表の有無はこの文書からは確かめられない。
9. 確認事項（ガイドラインと区別・抄録内件数差）: 区別 = 確かめた。抄録 Conclusion「provides additional reporting items for consideration and potential inclusion in an updated guideline」で、本文も Delphi 後に新指針を作るとする。新しい PRISMA-ScR 指針そのものではない。件数差 = 下記 10。
10. ほかに確かめること: 抄録の 43（13 + 30、「unique documents」）と本文 §3.1 の 47 papers（43 + 元の PRISMA-ScR 論文 + 随伴報告 3）。本文は元の PRISMA-ScR を「listed among the unique included studies」としつつ「did not undergo data extraction」で、抽出されたのは 43 と書く。47 = 43 + 1 + 3 の算術では元論文は 43 の外になり、本文内で表現が揃わない。平易な要約も 47 を挙げ、37 項目と併記する。全文 155 − 除外 104 = 51 で、47 との差 4 の説明は読んでいない。新しい PRISMA-ScR の指針そのものではないことは、抄録・本文とも「update に向けた根拠の ScR」と書く。
