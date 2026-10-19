# 判断の記録

## 判断 1（2026-10-17）論文の形は見積もりを見てから

- 研究者の答え: 「見積もりを見てから決める」（AskUserQuestion）。

## 判断 2（2026-10-17）C を単独の論文にする

- 材料: `feasibility.md`。264 件をすべて審査すれば含めるのは約 30〜90 件（中央で約 60 件）。候補の集合が 25 件以上になるには、中央の想定で審査の順の先頭から 120〜150 件（2 人で 85〜105 時間ほど）。
- 研究者の答え: C を単独の論文にする（推奨どおり）。narrative review は待たずに投稿でき、C はそれを引く。
- 帰結: 外枠は `papers/` の下に置く。探索の集合（11 報告）と narrative review の重なりは `overlap-narrative-review.md` のとおりで、検証の側に重心を置いて切り分ける。
- 見積もりの数は登録にも原稿にも書かない（結果の予想にあたる）。

## 判断 3（2026-10-17）投稿先はまだ決めない

- 候補として示したもの: Meta-Psychology（about のページに "There is no fee for publishing"・2026-10-17 に取得）、AMPPS（APS の案内で採択後 APC $1,000・資金が無ければ減額・免除。ページは 2021 年ごろで今の額は未確認）。
- 研究者の答え: まだ決めない。外枠は APA 7 版・抄録 250 語以内を仮置きし、規程の節は投稿先を決めたときに書き直す。

## 判断 4（2026-10-17）外枠の置き場と形

- `papers/ai-fatigue-measurement/`（公開物の作法: 英語・内部の番号やパスを書かない）。`_style_check.py` で違反 0 件。
- IME 論文の外枠の形（題・規程・主張の範囲・寄与・抄録の規則・節の計画・主張と根拠の表・表の入れ物・未決）に合わせた。
- narrative review との関係は独立の節にし、新しいと言えるものを 5 点に限った（`overlap-narrative-review.md` の「違い」の列から）。
- 見積もり（`feasibility.md`）の数は外枠に入れていない。

## 判断 5（2026-10-17）外枠のプレ査読（attack-me・outline round 1）への対応

- 記録: `attack-me/outline-c-manuscript/round-1/`（判定 major・指摘 F1〜F26 は `verdict.md`）。査読者 3 人（全員有効）・意図の監査役・Codex（研究者の承認を得て送った。外枠の全文と登録版の Background and questions の節。研究者の求めで「どこが面白いか」も問うた）。
- 研究者の採否（AskUserQuestion）:
  - 設計の判断が要らない直しはすべて直す（推奨どおり）。
  - 推奨の節は「既存の基準を当てたもの」と「この枠組みの提案」に分ける。表 14。抄録と結論に入れない（推奨どおり）。
  - 尺度の表を 2 つ足す: 検証の集合の研究が使った尺度の版すべて（表 15）と、研究ごとの C1〜C7 の表（付録）（推奨どおり）。
  - 焦点を「測ったものから結論がどこまで行けるか」に移す（Codex の指摘・推奨どおり）。
  - 外枠を登録の添付 5 にする・C4f は statcheck との違いを書き結果単位の数も出す・抄録は 3 つの面（C1・C2b・問題の文）を必ず残す（いずれも推奨どおり）。
  - 題: 研究者が「新しい手順の提案なら親しみやすい名前にしたい」と述べ、符号化の手順に名前を付ける案を選んだ。題は "TRACE: Tracing how studies of "AI fatigue" attribute, measure and report fatigue. A registered methodological review"。TRACE の展開（仮に Tracing Reports' Attribution, Content and Evidence）は後で詰める。2026-10-17 の簡易の検索（Web 2 回）では、研究の報告の手引き・尺度で同名のものは見つからなかった（金融の FINRA TRACE は別分野）。投稿の前に調べ直す。
  - narrative review の著者・引き方・関係の書き方: 研究者が「草稿が完成してから共著者と直接相談する」と決めた。外枠の未決に置き、登録版の文（両著者が著者）は今は変えない。
- 研究者に確かめていない、メインの既定（round 2 か研究者の確認で見直す）:
  - C4f で表の中の値を再計算の対象に含める（登録版にはこれまで書かれていなかった。R3 の問いに答えるため含める側で書いた）。
  - C7 の条件 (iii) と C6a が名前を比べることを、範囲の節に書き、C7 を常に条件ごとに報告する（F10。登録のコードは変えない）。
- 出典: Elson et al. 2023 を [P524]、Lintner 2024 を [P525] として `docs/references.md` に登録（本文は Europe PMC で照合）。
- 登録版を 0.7 にし、合成の脚本に 3 つの出力（C4f の結果単位・使われた尺度の版・研究ごとの表）を足した（`.steering/20261017-ai-fatigue-c-outline/decisions.md` 判断 13）。

## 判断 6（2026-10-17）外枠のプレ査読（attack-me・outline round 2）への対応

- 記録: `attack-me/outline-c-manuscript/round-2/`（判定 minor revision・指摘 G1〜G24 は `verdict.md`）。査読者 3 人（全員有効）・意図の監査役。Codex は加えていない（引き継ぎの方針）。round 1 の F15・F26 は context-B で直した。
- 研究者の採否（AskUserQuestion）:
  - 直す一覧と、登録版 0.7 の GSRR-1・10・12・56・63 を外枠に揃える直しを、すべて進める（推奨どおり）。C4f は表の値を含める既定を確定し、出どころの列・不完全な報告の扱い・r を対象に加える（推奨どおり）。
  - C7 は登録で 3 つの問題の型に分ける（推奨どおり）。
  - 中心の問いは帰属を見出しにする（推奨どおり）: 「AI に関わる疲労を報告する研究は、疲労を AI にどう結びつけ、題と結論はその結びつきと、尺度の名前と設計が示せる範囲に留まるか」。答えるのは帰属・名前・設計の照合で、妥当性の証拠ではないと書いた。
  - 研究者の問い「この論文に価値はあるか・NR と尺度の論文（AI 疲労の新しい尺度を作る論文）との 3 本組になるか」に、メインの見立てを答えた（返答のみ。記録の主張にはしない）。
- 直したもの: 外枠（版と日付・範囲・NR との関係・寄与・抄録の規則・序論・背景・方法 5・結果・考察 5.2〜5.4・主張と根拠の表・表 9・11〜15・未決・参考文献）、README（題・抄録の見本）、抄録の見本 `abstract-mock.md`（新規）、登録版 0.8 と脚本（`20261017-ai-fatigue-c-outline/decisions.md` 判断 14）、`overlap-narrative-review.md` に古いことの注。
- 抄録の見本（G5）: 規則どおり数を全部並べると 364 語。手順 2 と簡潔な言い方で 231 語（C4 の型の名を入れて約 247 語）。250 語に収まるのは手順 2 と簡潔な言い方のときだけで、余裕はほとんど無い。手順 3（背景を 15 語以内の 1 文に）を足した。
- 出典: Terwee et al. 2018（COSMIN の内容的妥当性の方法）を [P526]（Springer の OA の PDF で照合）、Flake & Fried 2020 を [P527]（provisional。書誌は OpenAlex で照合、無料の版 PsyArXiv は OSF が 503 で本文を取れず未照合。照合するまで主張の根拠に使わない）。
- 残したもの: narrative review の著者（判断 5 のまま。外枠は「共有する見方」と書き、著者の断定を減らした。登録版 GSRR-46 の文は変えていない）、背景の文の出典、比較の軸の文献、TRACE の展開。
- /cross-review: かけていない（このタスクの途中の段。登録版の差分の確認と合わせて、研究者の判断で行う）。

## 判断 7（2026-10-20）投稿先の客観的な比較（まだ決めない）

- 研究者の問い: 論文ができたらどこに出すか、どこなら通りやすいか。答え（AskUserQuestion）: まだ決めない。分析だけ残す。
- 前提: 費用ゼロ（APC・掲載料を払わない）。第 1 著者は所属なし。
- 公式ページで確かめたこと（2026-10-20 に WebFetch で取得）:
  - Meta-Psychology（open.lnu.se/index.php/metapsychology/about）: "There is no fee for publishing"。範囲に "systematic reviews, meta-analyses" を含む。"Meta-Psychology does not publish a limited number of studies or seek to have a certain rejection rate" / "Novelty is not considered a criterium"。査読は公開・署名あり。投稿時にプレプリントが要る。
  - Research Synthesis Methods（Cambridge・author-instructions）: 2025 年から全件 OA。"Authors without a Transformative Agreement or funding to pay an APC are granted waivers by Cambridge University Press."。ただし範囲は統合の方法で、一次研究の測定を数える本稿とは合いにくい（メインの判断）。
  - AMPPS（APS・apc-waivers-policy）: 免除の申請に "Confirmation from the corresponding author's department administration and/or acquisition librarian" が要り、採択後に判定する。所属なしでの扱いは書かれていない。APC $1,000 は APS の別ページ（サブエージェントが取得・メインは未照合）。
- 未確認（出版社のページが自動取得を 403 で拒んだ）: CHB / CHB Reports・IJHCI・BIT・BRM・Assessment・Psychological Methods・EJPA・SPPS・Collabra・RSOS の現行の費用と規程、PCI RR の公式ページ（対象範囲・既存データの水準・無料の friendly 誌）。ハイブリッド誌の購読型ルートが無料かは、誌ごとに公式で確かめていない。
- 採択率: 公式の現行値は取れなかった。Psychological Methods 約 16%（APA 2015 年の統計）、SPPS 17%（2012〜2013 年の編集者の報告）など古い値だけ。CHB の値は第三者の推定で根拠不明のため使わない。
- 先例（測定の実践を批判するレビューの掲載先）: AMPPS（Flake & Fried 2020）、SPPS（Flake, Pek & Hehman 2017）、Communications Psychology（Elson et al. 2023）。AI 疲労・AI 不安の尺度の測定レビューは見つからなかった。
- メインの推奨（採られていない）: Meta-Psychology。費用ゼロが公式で確定し、範囲が合い、新しさを問わない。弱みは、AI 疲労の研究を書く人（CHB などの読者）に届きにくいこと。
- 時期の注: PCI RR の Stage 1 は主のコード化（2026-12-31 に集合が締まった後）より前に原則受理が要るので、今の登録の日程とぶつかる。使うなら日程の見直しが要る。
- 追記（2026-10-20・研究者の指摘「購読型の道があるのでは」を受けて Chrome で公式ページを読んだ）:
  - CHB（sciencedirect の open-access-options）: "two choices to publish your research: Open access / Subscription"。購読型は "No open access publication fee."。OA の APC は USD 4840。"Your publication choice will have no effect on the peer review process or acceptance of your submission."。自己保存の猶予は 24 か月。投稿規程: 論文の種類に "literature reviews"。査読は二重匿名。抄録 250 語以内・ハイライト 3〜5 点。データは Option C（公開か、できない理由の記述）。人を対象とする研究でなければ倫理承認は不要。
  - IJHCI（T&F の投稿規程）: "There are no submission fees, publication fees or page charges for this journal."。OA は Open Select で任意（APC は OA を選んだときだけ）。論文の種類に "Review Articles"。"There are no word limits for papers in this journal."
  - 帰結: 「費用ゼロ」の条件では CHB と IJHCI も候補に残る（判断 7 の未確認のうち 2 誌が確定）。
- 追記（2026-10-20・読み手の確かめ）: 候補 264 件（`~/Documents/TRACE/data/records264.json`）の掲載誌に CHB・IJHCI・BIT は 0 件。多いのは Applied Clinical Informatics 7、Frontiers in Psychology 8（大小文字の表記揺れを合算）、Acta Psychologica 7、JAMA Network Open 5、Cureus 5。分野の語では psycholog 20・educat 17・informatic 16・medical 10・nurs 7。対象者は医療者 93 件が最多。探索の集合の記録（`.steering/` の AI 疲労の各タスク）での言及は Acta Psychologica・Frontiers in Psychology・Scientific Reports が多く、CHB Reports 6 回・CHB 3 回・IJHCI 1 回（言及の回数で、研究の数ではない）。→ AI 疲労の研究を書いている人の多くは心理学の総合誌と医療情報の雑誌にいて、CHB・IJHCI の読者と重なるのは一部。
- 追記（2026-10-20・目的から並べ直す）: 研究者の差し戻し「難易度や格の高さを重視していない？手段が目的になってる？」を受け、目的を聞いた。答え: 「AI 疲労の研究のやり方を変える」と「測定の方法論として出す」が五分五分。
  - 読み手の実態: 候補 264 件は 186 誌に散らばる（最多でも 8 件）。本拠地の雑誌は無く、届くかどうかは見つかるか（PubMed 等の索引）と読めるか（OA）で決まる。
  - 公式で確かめたこと（Chrome）: Meta-Psychology は NLM Catalog に ISSN 2003-2714 が無い（PubMed に載らない）。PLOS ONE は論文の種類に systematic review があり、Registered Report の枠もある。掲載料は Research Article で $2,596〜$3,165（表の行と誌の対応は読み切れていない）。PLOS の PFA は "authors unable to pay all or part of their publication fees and who can demonstrate financial need"・投稿時に申請・"A decision is usually sent to the author within 10 business days"・"case-by-case"・"Information about applications for fee assistance are not disclosed to journal editors or reviewers"。Journal of Clinical Epidemiology は購読型なら無料（OA は USD 4560）。Collabra・RSOS はボット判定の確認ページで読めず未確認（突破していない）。
  - メインの案: PLOS ONE に PFA を付けて出す（OA・PubMed で医療者の著者にも届き、方法論の論文も載る）。PFA が全額でなければ査読の前に取り下げ、Meta-Psychology に出す。どちらでもプレプリントを先に出す。CHB・IJHCI・JCE の購読型は、読めない形になるので目的に合わない。
- 追記（2026-10-20・研究者の求め「購読云々関係なしで再分析」）: 条件を「掲載料ゼロで出せる道がある」だけにして並べ直した。
  - 追加で確かめたこと（Chrome）: JAMIA は "If you do not select the open access option, your paper will be published with standard subscription-based access and you will not be charged."。Reviews は "Word count: up to 4000 words" / "Tables: up to 4"。Acta Psychologica は完全 OA で APC USD 2650（購読の道なし）。Applied Clinical Informatics は投稿規程のページが見つからず未確認。
  - 原稿の大きさ（`~/TRACE/manuscript/draft`）: 表 16（tables.tex の table 環境）、本文は結果が空の段で概算 4,300〜7,400 語（数え方で幅）。
  - 読み手の塊（264 件）: 医療情報（ACI 7・JAMIA 4・JAMIA Open 4・JMIR 系 6・ほか）約 24 件が最大、心理学の OA 誌（Frontiers in Psychology 8・Acta Psychologica 7・BMC Psychology 2・Scientific Reports 2）約 19 件。CHB・IJHCI は 0。
  - メインの見立て: 掲載料ゼロの道が確かな 5 誌（Meta-Psychology・IJHCI・CHB・JCE・JAMIA）のうち、2 つの目的の両方に効くのは JCE（メタ研究の掲載先で、医療者の研究の読者がいる）。方法論だけなら Meta-Psychology。JAMIA は読み手に最も近いが Review の上限（4,000 語・表 4）に収まらない。CHB・IJHCI はどちらの目的にも強くない。JCE の語数・表の上限と範囲（対象が医療に限られない研究を載せるか）は未確認。
- 追記（2026-10-20・JCE と ACI の規程を確かめた）:
  - JCE（guide-for-authors）: 範囲に "Meta-science"・"Developing and evaluating outcome measures"・"Research integrity and culture"。原則受けないものに "Meta-research studies that demonstrate weaknesses or limitations in the evidence ecosystem but lack reflection on how these might be addressed"・"Bibliometric studies and those on infodemiology, social media trends, and health informatics"・"systematic reviews ... where the main focus is not on the methods"・"Studies limited to one country, jurisdiction, or clinical area"。上限は "Original Research: 3,000 words, 100 references, 5 figures, 5 tables"。Registered Reports あり。→ 範囲は方法論として合う（推奨の表 14 が「どう直すか」に当たる）が、3,000 語・表 5 に TRACE（表 16）は大きく削らないと入らず、医療の外の対象（264 件の約 6 割）が誌の目的「health care decision-making」から遠い。
  - ACI（connect.thieme.com の Author Guidelines）: OA の道は "Gold Open Access" か "Hybrid Open Access" と書かれ、OA を選んだときの 2026 年の APC は $3,620。購読で出す場合の費用、論文の種類と上限はこのページに無く未確認（旧 PDF の URL はこのページへ転送された）。範囲は臨床の情報学で、TRACE の対象の一部にしか当たらない。

## 判断 8（2026-10-20）投稿の計画（仮に決めた）

- 研究者の答え: 「一旦投稿の計画はこの形にしようか」（判断 7 の分析の後）。
- 計画:
  1. 本命は Meta-Psychology、予備は IJHCI。どちらも掲載料ゼロ・語数の上限なし（判断 7 で公式を確かめた）。JCE（3,000 語・表 5）と JAMIA（Review 4,000 語・表 4）は形式で外す。CHB は目的のどちらにも強くないので外す。
  2. 原稿は本文の表を 7〜8 に絞り、残りを補足に回す。本文: 記録の流れ（図）・コードの一覧・C1・C2b・C6/C7・問題の文・推奨、C4/C5 は要約表 1 つ。補足: 逸脱・集合の内訳（流れの図に統合）・一致の詳細・C2 の残り・C3・C4/C5 の詳細・感度の分析・尺度の版の一覧・網羅の確かめ。登録したコードはすべて報告する（削らない）。
  3. Meta-Psychology にはプレプリントと同時に出す（同誌の必須）。コード表と脚本は OSF。不採択なら同じ原稿を IJHCI へ。
  4. 現場の著者へ届ける別の短い論文（医療者の部分の推奨など）は、採択後に必要なら考える。本体の計画には入れない。
- 投稿先を選んだ根拠は目的（研究のやり方を変える・測定の方法論として出す、が五分五分）で、格や採択率は補助にとどめた。
- 符号化は第 2 著者が本体の集合の全部（判断 45 の写し・GSE 側の記録）。外枠 `outline.md:85-86` と登録版 `registration-en.md:15・29・51・352` はまだ「少なくとも 20%、または全部」の文で、揃えるかは研究者が決める（未変更）。
- 次の段: 外枠の「Journal requirements」の節を Meta-Psychology の規程で書き直し、表の本文と補足の分け方を外枠に入れる（研究者の指示を待つ）。

## 判断 9（2026-10-20）第 2 著者の符号化を「全部」だけにした（登録版 0.17・外枠 9 版）

- 研究者の答え: AskUserQuestion で「全部を計画、2 割を戻り先に」を選んだ後、「やっぱり全部のみにして」。判断 45 の戻り先（引き受けられなければ 2 割）と、判断 62 の「第二著者の登録への反映は共著者の返事の後」は、この指示で置き換わる。
- 直したもの（TRACE のコミット）: 登録版 GSRR-2・役割の表・段の 5・GSRR-44（冒頭と手順 6）・GSRR-49 から 2 割の選択と抜き方（seed 20261021）を外した。8 週以内に始められないときは、規則を書いていない別の人が全部を符号化してよい、誰もいなければ単独の符号化として逸脱に書く。第 1 著者の役割の「the only coder」を「first coder」に直した。外枠の範囲の節・抄録の規則・方法の計画 6 も「全部」に。
- 直していないもの: 登録版 GSRR-64 の「the draw of the second coder's sample」の行と、`c_synthesis.py` の `second_coder_sample`（SECOND_CODER_SEED・`--draw-second-coder`）と `make_dummy.py:348` の確かめ。使われなくなったが、脚本は登録の添付 2 なので研究者の指示を待つ。草稿 `main.tex:27` の「registration draft 0.16 … outline (version 8)」の注。
- Meta-Psychology の API キー（Drive の `TRACE/meta-phychology_api.md`）: 研究者の答えは「投稿の手続きの自動化」。ファイルは開いていない。投稿や提出は毎回研究者の確認を取り、キーの値は会話にも repo にも書かない。
