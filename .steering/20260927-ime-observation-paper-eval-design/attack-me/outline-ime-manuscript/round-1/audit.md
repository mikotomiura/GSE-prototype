# 意図の監査（attack-me・stage `outline`・round 1）

対象物は `C:\GSE-prototype\papers\ime-observation\manuscript\outline.md`（commit 6f0af22b）です。意図は context-B.md と、そこに挙がっていた design.md §0・§5、decisions.md の判断 1・6・15・21・106・145・146・147、research-positioning.md 805〜856 行だけから読みました。外枠が名指しする事前登録などの記録（context-A の一覧）は、外枠の中の矛盾を確かめる目的にだけ使いました。本文が無いことと結果の値が無いことは、指摘に入れていません。

重さは 3 段で付けました。**重**＝主張の芯か持ち帰りに効く、**中**＝原稿にそのまま写すと食い違いになる、**軽**＝言い方の問題です。

---

## 0. context-B が「見てほしい」とした 2 点への答え

**(a) 貢献の数え方と題の釣り合い（重）**
釣り合っていません。原因は判断どうしの時間差です。
- 判断 15（09-28）が決めた題は「ロガー」を独立の柱に立てています。逐語: "Observability limits, a cross-platform logger, and a synthetic-input validation"（outline.md 11–12 行）。
- 判断 147（10-04、1292 行）は逆で、逐語「ロガーは独立の貢献にせず貢献 2『ロガーとその検証（主）』にまとめた」です。題を見直したかどうかは、判断 147 に書かれていません。
- 結果として、題の 3 つの柱は貢献 1・2a・2b に当たり、貢献 3（漏洩）・4（実行コスト）・5（データセット）は題に現れません。
- 加えて「(主)」の付け先が 2 か所でずれています。
  - 貢献の箇条（53 行）は "**A cross-platform logger and its validation (primary).**" で、ロガーという作成物ごと「主」にしています。
  - Scope（32 行）は "The primary contribution is the estimate of agreement between the logger and a reference input field" で、主は推定値です。判断 6（49 行）も「(1) 精度評価（主）」です。
  - 判断 147 の言い方（ロガーとその検証が主）と、判断 6・Scope の言い方（精度評価が主）が揃っていません。
- 題の見直しの条件も意図とずれています。判断 15（148 行）は「E2 の結果が強ければ T4 へ変えてよい」、外枠（14 行）は "may be changed to a question form after the text-recoverability results are known" で、「強ければ」という条件が落ちています。T4 が問いの形かどうかは、paper-suggest.md を読んでいないので確かめていません。

**(b) データセットで芯がぼやけるか（中）**
主張と根拠の表では、芯は保たれています（AG が 10 行、DS が 3 行）。Scope の 32–33 行もそのままです。ぼやけの入口は 3 つあります。
1. **貢献 5 の言い方が、§10 の用途 (b) より広い。**
   - 貢献 5（64–65 行）: "released with a datasheet so that other observers can be evaluated against the same reference"
   - §10 (b)（213–214 行）: "evaluating another observer on the same plans with the same executor and reference input fields"
   - 判断 146（1276 行）の (b) は「同じ計画で再実行して比べる」です。つまり、比べられるのは寄託したデータではなく、一式を回し直したときです。
   - 寄託したデータだけで評価できるのは、記録した key 行を入力にする観測器（macOS 型の推論）に限られます。窓のイベントを使う Windows 型の観測器は、回し直さないと評価できません。
   - 貢献 5 のままだと、データセットを「観測器の評価の基準」として売る言い方になり、判断 146 の「過大にしない」から外れます。
2. **要旨の骨子（74–77 行）が、6 つの作業と 7 種の結果を平らに並べています。** 主の推定がどれかの印が無いので、250 語の中で芯が埋もれる形になっています。
3. **DS2 が content-free の主張をデータセットに広げています**（下の 3-C-5）。

---

## 1. 意図にあって対象物に無いもの（届いていない主張・持ち帰り）

**1-1（重）「20 秒の打ち切りが集計量をどう動かすか」を結果に基づいて持ち帰る、を支える行が表に無い**
- 意図（context-B 18 行）: 「20 秒の打ち切りが集計量をどう動かすか…を、結果に基づいて持ち帰る」
- 外枠の §11（220 行）は "how the 20-second cut-off changes a researcher's aggregates" と書くだけで、根拠の ID がありません。AG5 は打ち切りでの観測器の挙動、AG10 は `under_limit` の L2 で、`all_trials` との差を集計量への効果として出す行がありません。
- 事前登録 §6.4（714–716 行）の逐語: "The values under `all_trials` depend on this design's fraction of long trials … and is not a property of natural typing. The effect of the cut-off on a researcher's aggregates follows from the rule stated in section 1.1."
- つまり、結果から言えるのは向きと仕組みまでで、大きさは計画に依存します。
- Windows ではさらに、どの経路が行を書いたかが記録されません。§10.7（1285–1286 行）の逐語: "The path that wrote a row is not recorded and is not inferred"。研究者が自分のログで打ち切りの有無を知る手段は無い、ということです。
- 意図の「結果に基づいて」と、事前登録の「規則から従う」の食い違いを、外枠はまだ解いていません。

**1-2（中）意図の読者に「中国語など」があるのに、その読者の持ち帰りが無い**
- 意図（context-B 13 行）: 「日本語・中国語など、入力方式を通して書く言語を含む」
- 外枠の Scope（34–35 行）は "No claim is made about … other input methods" です。§2 の背景（101–102 行）以外に、中国語の読者が持ち帰るものがありません。
- 観測可能性の議論（OB1–OB3）は OS の層の議論なので、言語によらず当てはまる部分があり得ます。どこまでが OS の層で、どこからが日本語の入力方式に固有かを §3 か §11 で 1 文に分けるか、読者を狭めるかのどちらかが要ります。

**1-3（中）事前登録の限界のうち、主の推定の読み方を左右するものが §12 に無い**
意図の「既知の限界」は外枠 §12（226–229 行）にすべて入っています。そのうえで、外枠が優先すると明言している事前登録の次の限界が §12 にありません。context-B の一覧にもありません。
- §7（974–978 行）"The reference is a reference input field, not the input method's internal state." / "Another application may receive other calls from the same input method"
- §7（979–981 行）正解は §4.3 の規則（ライブ変換での自動確定の畳み込み）に依存する
- §10.11（1422–1423 行）"the agreement measures both the observer's errors and the difference of the constructs"（Windows の 2 つの構成概念）
- §10.11（1413–1416 行）"in applications that draw the candidates themselves the observer may see nothing. This was not tested."
- §7（984–989 行）合成の打鍵には人の時間構造が無く、そのことが漏洩の結果を制限する

**1-4（軽）design §5 の限界「かな入力の欠陥」が外枠にも context-B にも無い**
- design.md §5（212 行）の逐語: 「Limitations — 合成入力のみ・参照入力欄は 1 アプリ…・マウス確定・**かな入力の欠陥**・IME の版と学習・バッテリー未測定」
- 後の判断がこれを外した記録は、読んだ範囲にはありませんでした。何を指すかは確かめられていません。読みの中の minus・comma・period で区切れる件（事前登録 §6.4 の 736–739 行）なら AG6 の層に入っていますが、限界の節には挙がっていません。

**1-5（軽）判断 106 の「今後の課題に回す」の置き場が無い**
- 判断 106（850 行）の逐語: 「他の IME と他のアプリでの転移は『この研究の外』と書いて、限界と今後の課題に回す」
- 外枠では、§12 の 1 行と §13 の空の見出し（231 行）だけです。事前登録 §1.3（84–85 行）の "whether the agreement transfers … left to a separate study" に当たる文がありません。

---

## 2. 対象物にあって意図に無いもの（主張の漂流・範囲を超えた言い方）

**2-1（重）新規性を主張する一文**
- §2（104–105 行）の逐語: "which show that dropping text is not new in itself; **what is new here is a log of the conversion that holds no text.**"
- これは、外枠自身の Scope（45 行）"The manuscript makes no claim of priority." とぶつかります。
- 意図とも合いません。design §0（35–36 行）は「書かないこと: 『世界初』『先行が存在しない』… **設計上の排他性**で書く」です。research-positioning 820 行は「差分は『文献の不在』ではなく『設計上の排他性』」、851 行は「IME を扱う能力と本文非保存が、既存のどの系でも両立していないこと」です。
- Scope の 46 行（"which loggers handle input-method conversion, and which of them do so without reading the text"）の形に言い換える必要があります。

**2-2（重）「ほかに道が無い」という強い言い方。外枠自身の §3 がそれを崩している**
- §3 の macOS（125–126 行）の逐語: "the list of windows can show a candidate window only by polling and not before a conversion; … A logger that records no text can therefore **only** infer sessions from key presses."
  - 直前の文が、ポーリングという別の部分的な道を挙げています。そのうえ "only" は Scope（43–44 行）の "worded as "no documented interface provides" and not as a proof that observation is impossible" という書き方の規則を破っています。
- §3 の Windows（115 行）"**The only route** into every application is a text service" も、OB1 の "the only documented route" から "documented" が落ちています。119–121 行では、アプリに依存する変換対象のイベントの存在を自分で認めています。
- 意図（context-B 17 行）の「観測する道は…に限られ」も同じ強さです。意図の側を Scope の書き方に合わせるか、「文書化された公開の手段のうち、アプリによらず使えるものは」と限定する必要があります。

**2-3（重）§11 の推奨が、Scope が主張しないと決めた場面（研究者自身の利用）に向いている**
- §11（219–221 行）: "Per system, which measures the results support … how the 20-second cut-off changes a researcher's aggregates, and the granularity of key rows that the recoverability study supports for publication."
- Scope（34–35 行）: "No claim is made about agreement in natural typing, … about other applications than the reference input fields"
- 事前登録 §10.11（1419–1421 行）: "The agreement measured here therefore cannot be carried to an application whose field does not record a reference"
- 推奨を「参照入力欄・合成入力の範囲で」と条件づけないと、読者は自分の研究（人の打鍵・一般のアプリ）への推奨として受け取ります。
- 同じ §11 の "supports for publication" は、Scope（41 行）の "it does not describe the log as safe to publish" の境界に触れています。RC2 にある "(or that none is recommended)" も §11 にはありません。

**2-4（中）Windows で漏洩の推奨の対象外になる行を、外枠が「key rows」と一括りにしている**
- §4（135 行）は "one key row per press and release"、Scope（42 行）は "The recommendation concerns one phrase at a time and the key rows only."
- 事前登録 §10.7（1334–1337 行）の逐語: "the judgement on Windows concerns the key rows of presses other than modifier keys; the modifier rows and the release rows that the Windows observer writes … are not evaluated, and publishing them is outside the recommendation"
- §6.8（899–901 行）のとおり、session 行も推奨の外です。外枠の「key rows only」は、Windows については対象を広く言いすぎています。

**2-5（中）時刻を落とした粒度に推奨を限る理由が、事前登録の理由と違う**
- §2（106–107 行）: "attacks that infer typed text from keystroke timing, which **motivate** … the restriction of its recommendation to granularities that keep no time."
- 事前登録 §6.8（870–874 行）の理由は、合成の打鍵間隔がキーと独立なので "cannot be carried over to human logs" であることです。§7（987–989 行）は、ms と 1 秒のビンの間の粒度は評価していないとも書いています。
- 外枠の言い方だと、評価できなかったという制約が、文献に動機づけられた設計判断に見えます。§12 にもこの限界がありません（1-3）。

**2-6（軽）登録に無い判定語**
- Scope（40 行）: "If a granularity of the key rows lets a phrase be identified **well above chance**, the manuscript says so"
- 登録された判定は near chance（各 K で Wilson の上端が 2/K 以下、事前登録 879–880 行）だけで、「well above」は定義されていません。near chance に届かないとき、「報告して推奨しない」（事前登録 897–899 行）との間に、もう 1 段の判定語ができています。

**2-7（軽）速さの由来の但し書きが落ちている**
- §5.4（165–166 行）: "three speeds with key-interval medians of 480, 240 and 120 ms from published typing data"
- 事前登録 §3.3（389–390 行）の逐語: "Those values come from transcription typing of English sentences; they are used to span the range of typing speeds, not as estimates of Japanese typing."

---

## 3. 意図どうしの矛盾と、対象物の中の矛盾

### 3-A 意図どうし

**3-A-1（重）「入力方式自身のセッションと一致」と「参照入力欄であって入力方式の内部状態ではない」**
- context-B（17 行）「入力方式自身のセッションとどこまで一致するかを…示す」と、design §0 C3（31 行）「IME 自身の状態と◯◯の精度で一致し」
- 事前登録 §7（974 行）の逐語: "The reference is a reference input field, not the input method's internal state."
- 外枠の中でも割れています。Scope（32 行）は "agreement between the logger and a reference input field" と正しく書き、序論（90–91 行）は "how closely such a log agrees with **the input method's own sessions**" と意図の言い方を写しています。
- Windows では、参照（TSF の composition）と観測（窓が見えている期間）が別の構成概念です（事前登録 §10.11、1422–1423 行）。そのため「入力方式自身のセッション」と書くと、Windows の一致の値を観測器の誤りだけと読ませてしまいます。

**3-A-2（重）「どの測度を信頼してよいか」と「合否の判定をしない・閾値を置かない」**
- context-B（18 行）「OS ごとにどの測度を信頼してよいか…を、結果に基づいて持ち帰る」と、design §5（211 行）「OS ごとに『信頼してよい測度 / 使ってはいけない比較』」
- 事前登録 §1.2（46–47 行）"No estimate is turned into a pass or fail decision, except the near-chance rule"、外枠の Scope（37 行）"no threshold of adequate agreement is set"
- 測度ごとに「信頼してよい」を言えば、閾値を事後に置くことになります。OS をまたぐ比較の禁止のように、構成概念から導ける推奨は両立します。値から導く「信頼」は、どの規則で書くかが未決です。§11 の "none is written before the results"（222 行）は、事後であることを認めているだけで、規則を与えていません。

**3-A-3（中）判断 15 の題と判断 147 の貢献の数え方** — 0-(a) を見てください。

**3-A-4（参考・外枠の側で解消済み）**
- 判断 6（49 行）の「(2) 本文を再構成**できないこと**の定量分析」は、結果を先取りした言い方です。外枠の貢献 3（58–60 行）と Scope（40 行）は中立に直してあり、判断 6 のトレードオフ（51 行）「一部は漏れるになってもそのまま報告する」と合っています。
- design §0 C5（33 行）の「常駐コストは**実用範囲**」という評価語は、外枠の RT1（280 行）で落とされています（"values of the two systems not compared"）。
- research-positioning 821 行・838 行の差分（リアルタイムの介入・一般アプリ横断・自然作業・回復との接続）は、この論文では主張できないもので、外枠に入っていないのが正しい状態です。

### 3-B 対象物の中（外枠と、外枠が優先すると書いた事前登録の間を含む）

外枠の 6–7 行は事前登録が優先すると書いていますが、外枠の文をそのまま原稿に写せば食い違いが残ります。

**3-B-1（中）区間の付かない推定**
- 要旨の骨子（76–77 行）"Results as interval ranges: … recoverability against chance, **runtime cost under two conditions**"、Scope（36 行）"Estimates are reported with their intervals."
- 事前登録 §1.2（44–46 行）の逐語: "F1, the counts, the mean rank and the per-scenario and per-speed accuracies of question 4, the delivery figures of section 6.3 and the figures of sections 6.9 and 6.10 are reported without one"
- 実行コスト（§6.10）は区間を持たないので、要旨で区間の範囲として書けません。

**3-B-2（中）データセットの中止した run の扱いが、DS1 の中で揃っていない**
- DS1（281 行）は、本計測が "for each measurement run **admitted by the stopping rule**"、パイロットが "the calibration-pilot runs that **meet the registered criteria**" です。
- 事前登録 §3.4（474–476 行）の逐語: "The same check is made on a run that the runner aborted: such a run is never analysed, and it is deposited only if the check passes or if it left neither a reference log nor an observation log."
- つまり、runner が中止した本計測の run も寄託され得ます。DS1 の本計測側の書き方では抜け落ちます。判断 146（1280 行）は、限界に「中止した run の扱い」を明記すると決めていますが、§10（208 行）の "what was not deposited and why" は、寄託した中止 run を覆いません。

**3-B-3（中）OB1・OB2 の「Registered definition」が、登録していない議論を指している**
- 外枠の 4–5 行は "Each claim names the registered question and section that define it"。OB1・OB2 の列は "Section 10.3 (the observer on Windows)" です。
- §10.3 は観測器の 2 つの経路を書いた節で、文書から観測可能性を論じる議論は事前登録にありません。観測可能性の分析は登録の外の議論だと明記しないと、読者は登録済みと読みます。

**3-B-4（中）DS3 の根拠が、自分で書いた説明書になっている**
- DS3（283 行）: "The dataset supports uses (a) to (c) …"。根拠は "Datasheet released with the data"、Registered definition は "Sections 2.1, 7, 10.11" です。
- 用途 (a)〜(c) は判断 146 で決めたもので、事前登録のどの節も定義していません（挙がっている節は限界の節です）。判断 146 の「解析を足さない」（1282 行）とも合わせると、DS3 は検証された主張ではなく、記述として扱う方が筋が通ります。

**3-B-5（中）content-free の根拠が、形しか保証しない検査器になっている**
- LG1（265 行）"The logger writes key categories and session summaries and no text"、根拠は `validate_logs.py`。DS2（282 行）"Every deposited log passed the content-free check"
- FORMATS.md（216–222 行）の逐語: "**The meaning of a value is not guaranteed**: payload encoded into an integer field … cannot be detected this way. Keeping the log content-free is the producing side's design responsibility"
- 「本文を書かない」の根拠は、ロガーのソース（何を書くか）が担います。検査器が担うのは形だけです。外枠の §4（146–147 行）"a validator rejects any log that departs from it" も、保証の範囲を言っていません。

**3-B-6（軽）LG2 の根拠が Windows を覆っていない**
- LG2（266 行）の主張は "The macOS session rules **and the Windows session paths**"、根拠は "the self-test of `kit/analysis/spec_predict.py` against that source"
- 事前登録 §10.7（1271–1273 行）"The prediction of section 4.5 models the macOS observer; no prediction applies to the Windows observer"。Windows の経路の根拠はソースだけです（spec_predict.py 本体は読んでいません）。

**3-B-7（軽）F13 以上のキーの書き方**
- §4（135–136 行）"(input-mode keys and, **on macOS**, F13 to F19 and modifier keys produce no row)"
- 事前登録 §10.3（1179–1180 行）によれば、Windows も "it writes no row for the input-mode keys … or for F13 and above" で、修飾キーは行を書きます。外枠の書き方だと、Windows では F13–F19 が行を作ると読めます。

**3-B-8（軽）"qualify" の語が 2 つの意味で使われている**
- Scope（33 行）"Every other result is reported next to it and is not used to qualify it."、RC2（278 行）"the same judgement on Windows **as a qualification**"
- 事前登録 §6.2（662–664 行）は、器具の検査を "so that a failure of the reference is not read as one of the observer" と、主の推定の読み方に効く材料として置いています。Scope の意味は「試行の除外や調整に使わない」（事前登録 §1.2、68–69 行）だと思われるので、その形で書く方が誤読を防げます。

**3-B-9（軽・外枠が名指しする作成物）ロガーの README に古い文が残っている**
- `C:\GSE-prototype\papers\ime-observation\kit\logger\README.md` 41–42 行の逐語: "(until a driver is present for the current platform, this ends with "not implemented")"
- 外枠は、両 OS で動くロガーを貢献 2 に置いています。BRM の "readers can easily use the materials" の読者にとっては、使えないという印象になります。

---

## 4. 位置と逐語

各項目の中に、外枠の行番号と逐語を付けました。意図の側の出どころは次のとおりです。
- context-B.md 13・17・18 行
- design.md 31・33・35–36・211–212 行
- decisions.md 49（判断 6）・148（判断 15）・850（判断 106）・1274/1276/1280/1282（判断 146）・1292（判断 147）行
- research-positioning.md 820・821・838・851 行

---

## 5. 読めなかった範囲と、注入の疑い

**読んでいない**
- preregistration.md の 401–454 行（§3.4 の前半）、494–599 行（§4・§5）、1460 行以降（References の後半）
- pilot-macos.md の 1–169 行と pilot-windows.md の 1–190 行（どちらも「Raw logs」の節だけ読みました）
- decisions.md の、指定以外の判断（指示どおり）。判断 36・43 など、公開物の書き方に関わる判断は読んでいないので、それに基づく指摘はしていません。
- design.md の §0・§5 以外、research-positioning.md の 805–856 行以外
- 題の候補 T4 が載っている paper-suggest.md（一覧の外）。T4 が「問いの形」かは確かめていません。
- 外枠が名指しするコード（`pipeline.py`・`spec_predict.py`・`validate_logs.py`・`clock_sync.py`・`run.sh`・`kit/logger/src/`）。context-A が一覧から外しています。

**注入の疑い**: ありません。読んだ文の中に、LLM や査読者に向けた指示は見当たりませんでした。
