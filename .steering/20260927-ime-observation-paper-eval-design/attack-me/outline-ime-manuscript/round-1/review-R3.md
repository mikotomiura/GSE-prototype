# 査読結果（立場: メタサイエンスとデータ管理の方法論の査読者、Behavior Research Methods、stage outline、round 1）

対象物: `C:\GSE-prototype\papers\ime-observation\manuscript\outline.md`（commit `6f0af22b`）
読んだ資料: context-A.md と、その一覧にあるファイル（読んだ範囲は 5 に書いた）、および接地の 3 本。

---

## 1. 接地（この立場が論文に求める基準）

- **S1. 事前登録は具体的・精密・網羅的であること**（Wicherts et al., 2016）
  "it is crucial that preregistrations provide a specific, precise, and exhaustive plan of the study"／"each described step should allow only one interpretation or implementation (it should be precise)"
- **S2. 確証の部分と探索の部分を分けること**（Wicherts et al., 2016）
  "a potential exploratory analyses section of a paper is not at all problematic, as long as the preregistration and the paper clearly distinguish between these very different types of analyses."／R6 "Presenting exploratory analyses as confirmatory (HARKing)"
- **S3. 何を報告するかを選ばないこと・事前登録を正しく示すこと**（Wicherts et al., 2016）
  "the researcher could report only a subset of many analyses that showed the researcher's most desirable results."／R3 "Fail to mention, misrepresent, or misidentify the study preregistration … This problem can be avoided by having reviewers compare the preregistration to the (submitted) research article."
- **S4. 再現できること**（Wicherts et al., 2016）
  "Reproducibility requires a verification of the steps taken from the data collection to the final report"／"The preferred way to assure reproducibility is to share data and analytic details (computer syntaxes/code)"
- **S5. データセットの用途・収集の仕組み・保守を明記すること**（Gebru et al., 2021）
  "to encourage dataset creators to reflect on the tasks for which the dataset should and should not be used"／"How were these mechanisms or procedures validated?"／"Who will be supporting/hosting/maintaining the dataset?"／"Will the dataset be updated … how updates will be communicated to dataset consumers"
- **S6. 識別子・利用条件・来歴**（Wilkinson et al., 2016）
  "F1. (meta)data are assigned a globally unique and persistent identifier"／"R1.1. (meta)data are released with a clear and accessible data usage license"／"R1.2. (meta)data are associated with detailed provenance"

---

## 2. 評価表

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | 対応表は丁寧で、ほとんどの AG 行は事前登録の節と結果ファイルに結び付いている。ただし中心の主張に、根拠が届いていない行が 3 つある。LG1 の「no text」を validator が支えるとしているが、FORMATS.md は形の検査しか保証しない。LG2 の Windows の部分を spec_predict の selftest が支えるとしているが、selftest は macOS の規則しか見ない。DS3 は datasheet の自己申告だけを根拠にしている。さらに第 11 節の推奨と要旨には、主張の行も事前に決めた規則も無い。 |
| b 方法の穴 | 4 | 事前登録はきわめて具体的で、研究者の自由度はほぼ閉じている。残る穴は 3 つ。Windows の試行の扱いに、登録に無い「研究者の判断」が 1 件ある。観測可能性の分析（文書の調査）に、探した手順が書かれていない。Windows のロガーは、行ごとにどちらの経路で書いたかを記録していない。 |
| c 持ち帰れるもの | 3 | ロガー・キット・データセット・粒度の推奨は具体的で価値がある。一方で、第 11 節の推奨は結果を見てから書くと宣言されており、規則で縛られていない。データセットの 3 つの用途について、手元の記録だけで成り立つものと、キットで測り直す必要があるものが分けられていない。ライセンス・保守・版の扱いも外枠に無い。 |
| d 簡潔さと構成 | 4 | 節の流れ（観測可能性 → ロガー → 検証 → 4 つの問い → データセット → 推奨）は筋が通っている。ただし、同じ測定から出る分析を「Study 1–4」と呼ぶと、標本が別々であるかのように読める。 |
| e 規程への適合 | 4 | 要旨の上限、Declarations、Open Practices Statement の位置、データの PID、TOP Level 2 を正しく押さえている。足りないのは、標本の大きさの根拠（規程 (d) の "statistical power" に相当する精度の計画）を Method に載せる計画。Ethics の文は、事前登録自身が認める限界より強く書かれている。 |
| f 先行研究の位置づけ | 3 | 既存のロガーの能力を、二次資料（"a recent comparison"）に頼って書いている。比較の表が予定されていない。「no claim of priority」と「what is new here」が同じ外枠の中でぶつかっている。BRM 自身の、器具やソフトウェアの検証の系譜への位置づけが無い。 |

---

## 3. 指摘の一覧（重い順）

- [severity: major] 第 11 節の推奨と結論の判定が、事前登録に無い合否の判断になっている
  - 位置と引用: outline.md:219-222 「Per system, which measures the results support and which comparisons they do not … Each recommendation cites the result it rests on; none is written before the results.」。対応表には第 11 節を独自に支える行が無い（RC2 と OB4 だけ）。
  - なぜ問題か: 事前登録 1.2 は「No estimate is turned into a pass or fail decision, except the near-chance rule of the text-recoverability study」、6.1 は「no threshold of adequate agreement is set」と言っている。「which measures the results support」は、指標ごとの合否の判断そのものである。その基準を結果の後に決めると宣言しているので、確証として登録された推定値に、登録されていない解釈の層を重ねることになる。（S2: Wicherts "as long as the preregistration and the paper clearly distinguish …"／S1 "it should be exhaustive"）
  - 解消の条件: (i) 第 11 節の推奨を、閾値を持たない記述に限る（例:「指標 X の区間は [a, b]、定義が両システムで異なるので比較しない」）か、(ii) 推奨を出す規則（何を満たせば「支持」と書くか）を結果の前に外枠へ書き、事前登録に無いことを明記して探索の扱いにするか、のどちらかにする。そのうえで、推奨 1 件ごとに対応表の行（ID・登録の有無・結果ファイル）を作る。cut-off が集計に与える影響は、事前登録 6.4 のとおり規則から出る向きだけを述べ、`all_trials` の値（設計に依存する）から量を外挿しない、と書く。
  - 自信: 高

- [severity: major] 要旨と本文の図表で、どの水準（層・速さ・セル・pooled）の推定を出すかが決まっていない
  - 位置と引用: outline.md:76-77 「Results as interval ranges: recall and precision of detection, bias and limits of agreement of the duration, agreement of abandonment, per-text agreement, recoverability against chance, runtime cost under two conditions.」／outline.md:297 「Table 5: detection per speed and cell, for the three comparisons.」／outline.md:290 「Figure 3: Bland-Altman plots of the duration error per cell and speed.」
  - なぜ問題か: 事前登録 6.1 は「The primary estimates are given per stratum: cell, scenario and speed.」と定めている。ところが Q2 の層ごとの主要推定は、本文の図表に出る場所が無い（補遺だけ）。要旨の「ranges of their intervals」が何の集合の範囲なのか（層の全体か、速さか、セルの pooled か）も決まっていない。最大で 3 セル × 約 13〜14 シナリオ × 3 速さ × 3 スコープ × 3 比較の中から、250 語に載せるものを結果の後に選べてしまう。（S3: Wicherts "report only a subset of many analyses …"）
  - 解消の条件: 要旨に載せる推定の規則を、結果の前に外枠へ固定する（例:「各セルの `gt_obs` × `under_limit` で、層ごとの区間の最小の下端から最大の上端まで、指標ごとに 1 範囲。除いた割合と `all_trials` の同じ範囲を併記」）。本文でも Q1・Q2 の主要推定（層ごと）が図か表に載るようにする。pooled の値を載せる場合は "pooled" と書く。Table 5 の「three comparisons」は Windows には当てはまらない（事前登録 10.7）ので、セルごとに書き分ける。
  - 自信: 高

- [severity: major] LG1 の「no text」を、validator という根拠が支えていない
  - 位置と引用: outline.md:265 「LG1 | The logger writes key categories and session summaries and no text … | `kit/formats/FORMATS.md` (`obs/1`); `kit/formats/validate_logs.py`; the content-free check …」／タイトル outline.md:11 「… without recording text」
  - なぜ問題か: FORMATS.md:218-221 は「**The meaning of a value is not guaranteed**: payload encoded into an integer field (`vk`, a length, a timestamp) … cannot be detected this way. Keeping the log content-free is the producing side's design responsibility」と書いている。validator が保証するのは形だけで、「文字を書かない」はソースの設計で支えるしかない。加えて RC1〜RC3 は、キーの区分の列から文が部分的に復元できることを測る問いであり、「no text」を「文字列のフィールドが無い」以上の意味で読ませると、自分の第 3 の貢献と食い違う。（S4: Wicherts "verification of the steps taken"）
  - 解消の条件: LG1 を 2 つに分ける。(a)「文字列の値は閉じた列挙だけ（validator が全ログで確認）」と、(b)「整数のフィールドに内容を埋めないことは、ソース（manifest の SHA-256 で特定）の設計による。機械では検査していない」。タイトルと要旨では "without recording text" の意味を「文字列を書かない」と定め、復元の可能性は RC が測ると明示する。
  - 自信: 高

- [severity: major] LG2 の Windows の部分（経路・cut-off・safety valve）に、テストという根拠が無い
  - 位置と引用: outline.md:266 「LG2 | The macOS session rules and the Windows session paths are those stated, including the cut-off and the safety valve. | … | Logger source in `kit/logger/`; the self-test of `kit/analysis/spec_predict.py` against that source」
  - なぜ問題か: 事前登録 10.7 は「The prediction of section 4.5 models the macOS observer; no prediction applies to the Windows observer」と書いている。spec_predict の selftest は Windows の経路（クロークの 150 ms の隙間、20 秒の cut-off、約 25 秒の safety valve、60 秒の切り替え）を見ていない。しかも 10.3 は「Which path drives the Microsoft input method on the measuring machine was not determined before the freeze」「a row does not record which path wrote it」と書いている。読者は、どの規則がこのデータを生んだのかを確かめられない。（S4・S5: Gebru "How were these mechanisms or procedures validated?"）
  - 解消の条件: Windows の経路ごとの単体テスト（合成のイベント列 → 期待する行）を根拠の列に名指しする。テストが無いなら、LG2 の Windows の部分を「ソースの記述（manifest X）。独立には検証していない」に弱める。20〜25 秒の行と 25 秒以上の行は、経路を示す手がかりにすぎない（10.7 "descriptively"）と本文に書く。
  - 自信: 高

- [severity: major] Windows の試行の数え方に、登録に無い研究者の判断があるのに、逸脱の表（Table 4）の範囲に入っていない
  - 位置と引用: outline.md:183-184 「the deviations recorded before the Windows measurement (Table 4) and any recorded later.」／data.windows.md:36 「No: by the researcher's decision this start, which sent no key, is not counted among the at most three attempts」／data.windows.md:35 attempt 1「the runner was stopped from outside … (the shell that ran it was ended by the coding assistant's session under low memory)」
  - なぜ問題か: 事前登録 3.4 は「up to three attempts」と「No other reason and no explanation is admitted.」を定め、8 は「Any departure … is recorded in `experiment/deviations.md` with its date, reason and effect」を求めている。管理者の権限で起動して拒否された開始を試行に数えないこと、外から止められた run を「aborted (incomplete)」に分けることは、どちらも登録の文に無い判断である。しかし deviations.md には D1〜D5 しか無い（D5 は 10.8 の確認の run の話で、別件）。キーが 1 つも送られていないので結果への影響は小さいが、「under a pre-registered protocol」「deviations are reported」という主張の網羅性に関わる。（S3: Wicherts R3）
  - 解消の条件: 2 件を deviations.md に日付・理由・影響つきで記録し、Table 4 に載せる。10.8 の版の確認（IME の版が pilot と違った場合の 39/39 の確認）の実施と結果も、AG9 か別の行で報告の対象として名指しする。測定中に同じ機械で動いていた他のプロセス（attempt 1 を止めたセッション）を測定の環境として報告するかどうかも決めておく。
  - 自信: 中

- [severity: major] 観測可能性の分析（貢献 1）が、登録された定義を持つかのように表に載っており、文書を探した手順が無い
  - 位置と引用: outline.md:263 「OB3 | On macOS no documented interface reports the marked text or composition state of another application … | Section 1.1 | Apple documentation of …」／outline.md:43-44 「It is worded as "no documented interface provides" and not as a proof that observation is impossible.」
  - なぜ問題か: 事前登録 1.1 の該当の文（「On macOS no public interface reports the conversion state of another application」）は、結論を述べているだけで、分析の手続きを定めていない。「Registered definition」の列に置くと、この分析が事前登録されたように読める（S3: R3 "misrepresent … the study preregistration"）。また「no documented interface」は全称の否定なので、どの文書の集合を、いつ、どの版で、どの基準で調べ尽くしたのかが無ければ、読者は追試できない（S1 "exhaustive"／S6 "R1.2 … detailed provenance"）。外枠の未決事項（outline.md:310「The count of accessibility attributes and notifications examined on macOS is to be confirmed」）も、この手順が未定であることを示している。
  - 解消の条件: OB 行の「Registered definition」を「not registered（文書による論証）」とする。第 3 節に調査の手順（調べた API 群の範囲、文書の URL・取得日・OS の版、数え方、含めた基準と外した基準）を書き、Table 1 の各行に出典と取得日を付ける。調べた一覧そのものを補遺かリポジトリに置く。
  - 自信: 中

- [severity: major] DS3（データセットの用途）の根拠が datasheet の自己申告で、用途ごとの成り立ち方と限界が書かれていない
  - 位置と引用: outline.md:283 「DS3 | The dataset supports uses (a) to (c) of section 10 … | Datasheet released with the data」／outline.md:213-214 「(b) evaluating another observer on the same plans with the same executor and reference input fields」
  - なぜ問題か: 用途を書いた文書は、用途が成り立つことの根拠にならない。(b) は、キー入力から推論する観測器なら、寄託した oracle と gt のログだけで機械の外で評価できる。しかし Windows のようにウィンドウを見る観測器は、キットで測り直す必要がある。その測り直しは、IME の学習を戻していないこと（事前登録 7 "The input method's learning is not reset"）と版の違いのせいで、同じ参照にはならない。（S5: Gebru "the tasks for which the dataset should and should not be used"／"Is there anything about the composition of the dataset or the way it was collected … that might impact future uses?"）
  - 解消の条件: 用途ごとに、(i) 寄託物だけで成り立つのか、キットで測り直す必要があるのか、(ii) 必要なファイルとフィールド（例: (a) は gt.jsonl の呼び出しの種類・長さ・時刻）、(iii) 再現できない要因（学習の状態・版・参照入力欄の種類）を datasheet と第 10 節に書き、DS3 の根拠の列に FORMATS.md の該当の節と、手元の記録で評価する手順（あれば）を足す。用途の例として「使ってはいけない用途」（自然なタイピングの基準や、人の書き手の推定）も対にして書く。
  - 自信: 中

- [severity: minor] 「no claim of priority」と「what is new here」が衝突している。他のロガーの能力を二次資料に頼っている
  - 位置と引用: outline.md:45 「The manuscript makes no claim of priority.」／outline.md:104-105 「… dropping text is not new in itself; what is new here is a log of the conversion that holds no text.」／outline.md:96-97 「Inputlog and ScriptLog, which a recent comparison lists as not supporting non-alphabetic writing」
  - なぜ問題か: 「what is new here」は新しさの主張そのものである。また、他のツールが変換を扱わないことを「a recent comparison」に頼って書くと、ツールの現行の版との差が検証されない。設計の違いとして書くと言うなら、その違いを並べた比較の表が要る。
  - 解消の条件: 「what is new」を「the design differs in …」に直す。ロガーごとに、IME の変換を扱うか・文字を読むか・単体で動くか・対応 OS・確かめた版と日付を、一次の文書で埋めた比較の表を予定に足す。
  - 自信: 中

- [severity: minor] BRM の器具の検証の系譜への位置づけが無い
  - 位置と引用: outline.md:94-108（第 2 節。挙がっているのは、筆記研究のロガー、日本語と中国語の筆記過程、キーストロークのデータセット、タイミングによる攻撃、一致の手法だけ）
  - なぜ問題か: この研究の検証は、合成の入力で、同じ機械の上のソフトウェアの参照に対して器具を較正する種類のものであり、BRM が多く載せてきた、実験ソフトウェアや入力機器のタイミング検証と同じ系譜にある。それが無いと、合成入力と同じ機械の参照という設計の選択（と限界）を、読者が既知の基準で評価できない。また IME を介した文字入力の評価（テキスト入力研究の指標）にも触れていない（具体的な文献は確かめていない。探索の候補として挙げる）。
  - 解消の条件: 第 2 節に「ソフトウェアの器具の検証（合成の入力・外部の時計の有無）」の小節を置き、この研究の参照がソフトウェアの層にある理由（事前登録 7 の第 1 項）と結び付ける。IME を介した文字入力の評価の文献があるかを一次で確かめる。
  - 自信: 低〜中

- [severity: minor] 文の復元の判定で、「well above chance」が登録に無い語であり、判定規則の性質が本文の予定に入っていない
  - 位置と引用: outline.md:40-41 「If a granularity of the key rows lets a phrase be identified well above chance, the manuscript says so」／outline.md:300 「Table 8: the near-chance judgement and the recommendation.」
  - なぜ問題か: 登録の規則は「near chance」（K = 10 と 100 で、Wilson の上端が 2/K 以下）だけである。「well above」の線は定義されておらず、解釈の自由度になる（S1 "precise"）。事前登録 6.8 の表では、K = 100 で真の正答率が 1.5/K でも、約半分の確率で near chance と判定される。また事前登録 7 は「The margin of the rule (2/K) and the values of K are design choices, not derived from a criterion of privacy.」と書いている。これを推奨と並べて示さないと、推奨が安全の保証に読まれる。
  - 解消の条件: 「well above chance」を削り、「the registered near-chance rule is not met」に置き換える。Table 8 に 2/K の幅、判定の確率の表（6.8）、ブロックで resample した区間を併記する。推奨の文には「1 試行・1 フレーズの識別についての判定で、プライバシーの基準から導いたものではない」を必ず添える。
  - 自信: 高

- [severity: minor] Declarations の Ethics の文が、事前登録の限界の記述より強い
  - 位置と引用: outline.md:236 「Ethics approval (Not applicable: no person took part, and all input was generated by a program)」
  - なぜ問題か: 事前登録 7 は「A person's key presses that reach neither the reference nor another application … are caught by neither rule.」と書き、pilot-macos.md:174-176 は「Both logs can carry a person's typing」と書いている。人の打鍵がデータに入らないことは、停止規則が知られた盲点つきで確かめるものであって、断言できることではない。寄託するのは人の打鍵が入り得るログである。（S5: Gebru の Collection Process の、人に関わる問い）
  - 解消の条件: 「No participants were recruited; all input of the measurement was generated by a program; the deposit checks (section 3.4) screen the logs for a person's key presses, with the blind spots stated in Limitations」のように、主張を手続きに結び付けて書く。datasheet にも同じ残りの危険を書く。
  - 自信: 中

- [severity: minor] データセットの節に、ライセンス・置き場所・保守・版の扱いが無い。DS1・DS2 の範囲と根拠に漏れがある
  - 位置と引用: outline.md:208-209 「Contents, formats, how the data were produced and checked, what was not deposited and why, licence, persistent identifier, intended uses, and limits.」／outline.md:281 「for each measurement run admitted by the stopping rule」／outline.md:282 「DS2 … Output of `kit/analysis/pipeline.py --pack` and `--check-deposit`」
  - なぜ問題か: README.md:20-22 はすでに Apache-2.0（コード）と CC BY 4.0（データ・文書）を決めているのに、外枠はライセンスの名前も、信頼できる置き場所も書いていない（S6: R1.1・F1）。保守・正誤表・版の扱いの項目が無い（S5: "Who will be supporting/hosting/maintaining the dataset?"）。DS1 の「admitted by the stopping rule」は、事前登録 3.4 のとおり検査を通れば寄託される、runner が止めた run を含むのかがはっきりしない。DS2 の根拠には、事前登録 3.4 が「reason 1 is checked by hand before a run is deposited」と書く手の検査（data.md の run の検査の表）が入っていない。content-free の検査が形の検査であることも、FORMATS.md の保証の範囲に合わせて書く必要がある。
  - 解消の条件: 第 10 節に、ライセンス（データ CC BY 4.0・コード Apache-2.0）、置き場所の名前、DOI を 1 つにするか部分ごとにするか、保守する人・連絡先・版の付け方・正誤表、を足す。DS1 に「runner が止めた run で検査を通ったもの」を含めるかどうかを明記する。DS2 の根拠に、data.md と data.windows.md の run の検査の表（手の検査を含む）を足す。
  - 自信: 高

- [severity: minor] 標本の大きさの根拠（精度の計画とデザイン効果）を Method に載せる予定が無い
  - 位置と引用: outline.md:165-167 「75 trials per scenario and speed; plans generated from a seed …」
  - なぜ問題か: 規程の確認項目 (d) "appropriate measures of variability, effect size, and (when relevant) statistical power" と、Wicherts の D6・D7（"A rigorous preregistration not only provides a good rationale for the sample size …"）に照らすと、根拠は事前登録 3.3 にある（Wilson の半幅、デザイン効果は最大で約 3.4、primary スコープで層が 31 まで小さくなること）。しかし外枠の 5.4 は数だけを書いている。cut-off で層が小さくなったのに数を変えなかったこと（3.3 "it was not revised"）も、読者が知るべき事実である。
  - 解消の条件: 5.4 か 5.8 に、精度の計画の要点（半幅の表、primary スコープでの層の大きさ、デザイン効果、pooled の区間は下限として読むこと）を載せる予定を書く。
  - 自信: 高

- [severity: minor] 「Every other result … is not used to qualify it」が、事前登録の診断の目的と食い違う
  - 位置と引用: outline.md:32-33 「Every other result is reported next to it and is not used to qualify it.」
  - なぜ問題か: 事前登録 6.2 は、参照入力欄がフォーカスを失った試行の行を報告する目的として「so that a failure of the reference is not read as one of the observer」を挙げており、診断は主要推定の解釈に使う前提である。「qualify しない」と書きながら、本文で診断を使って不一致を説明すると、どの説明を採るかが結果の後の選択になる。
  - 解消の条件: どの診断を、主要推定のどの解釈に使うか（例: フォーカスを失った試行の偽陽性の数は、参照の失敗として別に示す。主要推定の値は変えない）を外枠に列挙する。それ以外の説明は探索として書く、と明記する。
  - 自信: 中

- [severity: minor] タイトルが、macOS の構成概念と「text」の範囲を超えて言っている。結果に応じてタイトルを変える余地を残している
  - 位置と引用: outline.md:11 「Observing Japanese IME conversion without recording text」／outline.md:14 「The title may be changed to a question form after the text-recoverability results are known」
  - なぜ問題か: OB3・OB4 のとおり、macOS では変換を観測しておらず、キーの列から推論している（outline.md:126 「can therefore only infer sessions from key presses」）。タイトルを結果の後に疑問の形へ変える選択は、報告の段階の枠付けの自由度である（S3）。
  - 解消の条件: 両 OS に当てはまる語（例: "Logging Japanese input-method conversion sessions without recording text strings"）にする。タイトルの形を変える条件を、いま決めておく（または変えないと決める）。
  - 自信: 中

- [severity: nit] 「Study 1–4」の呼び方
  - 位置と引用: outline.md:186・191・196・202 「### 6. Study 1: Detection …」ほか
  - なぜ問題か: Study 1〜3 は同じ run のログに対する分析である。APA の読み方では、別々の標本・別々の測定と読まれやすく、独立性を誤解させる。
  - 解消の条件: 「Question 1: Detection …」か「Analysis 1」と呼び、同じ測定から出ていることを 5.1 で明記する。
  - 自信: 中

- [severity: nit] 「every number … copied from these files」の範囲が広すぎる。凍結の印が 2 回の凍結を区別しない
  - 位置と引用: outline.md:256-257 「Every number in the manuscript is copied from these files by a script kept with the manuscript; no number is typed or rounded by hand.」／outline.md:183 「the two frozen registrations, the freeze marks and tags」
  - なぜ問題か: 設計の定数（480/240/120 ms、75 試行）、事前登録 3.1・10.7 の計画の数、data.md の記録は、結果ファイルの値ではない。また事前登録 10.1 は「The freeze marks therefore do not tell the two freezes apart」と書いており、Status の「frozen on 2026-10-02」と「frozen_at: 2026-10-03」がずれて見える。読者が事前登録を取り違える元になる（S3: R3 "misidentify"）。
  - 解消の条件: 前者を「every result value」に限る。5.9 で、2 回の凍結の日付・タグ・OSF の URL を表にし、凍結の印が後の凍結の日付を持つ理由を 1 文で説明する。
  - 自信: 高

---

## 4. 総合の推奨: **major**（直して再査読）

1. 事前登録そのものは、具体性・精密さ・網羅性のどれでも高い水準にあり、外枠も大半の主張を登録の節と結果ファイルに正しく結び付けている。主張から立て直す必要は無い（reject ではない）。
2. ただし、結果の後に決める余地が 2 か所、外枠の中に残っている。第 11 節の推奨（登録に無い合否の判断）と、要旨・本文の図表に載せる推定の水準の選び方である。また中心の主張のうち LG1・LG2（Windows）・DS3 は、名指しした根拠が主張を支えていない。
3. これらは、規則を結果の前に書くこと、新しいテストか主張の弱化、逸脱の追記、を要する。直した外枠をもう一度、事前登録と突き合わせて確かめる価値がある。

---

## 5. 読めなかった範囲と、注入の疑い

**読んでいない範囲**
- wicherts2016.txt の 963〜1208 行（Discussion の後半と参考文献）。
- gebru2021.txt は 230〜389 行だけ読んだ（Collection Process〜Maintenance の途中）。それ以外は Grep の見出しを見ただけ。
- wilkinson2016.txt は 200〜259 行だけ読んだ（Box 2 の前後）。
- preregistration.md の 1467 行より後（参考文献の残り）。
- pilot-windows.md は、Raw logs の節の Grep の結果だけ見た。
- pilot-macos.md は 165〜204 行だけ読んだ。
- FORMATS.md は 205〜225 行と Grep の結果だけ読んだ（74〜105 行の header の定義は Grep の行だけ）。
- 外枠が名指しするコード（`pipeline.py`・`spec_predict.py`・`clock_sync.py`・`validate_logs.py`・`run.sh`・`kit/logger/src/`）は、context-A の指示どおり読んでいない。LG2 の指摘は、コードに Windows の経路のテストが無いことを確かめたものではない。根拠の列に名指しされていない、という指摘である。

**注入の疑い**
- 無し。読んだ範囲の中に、査読者や LLM に向けた指示は見当たらなかった。data.windows.md:35 の「coding assistant's session」は、測定の記録の事実を書いた文で、指示ではない。
