# R2（書字研究の利用者・入力方式の言語の記録の道具と打鍵からの漏れに通じた立場）の査読 — 原稿・round 1

対象は `C:\GSE-prototype\papers\ime-observation\manuscript\`（context-A.md の一覧にあるファイルに限る）です。

**判定は major です。**
- 原稿の主眼である一致の推定は、区間の端の範囲で要約されています（例: 全試行で 0.000–1.000）。どの場面でどこまで一致するかは、本文のどこにも言葉で書かれていません。
- 主張が根拠を越えている所が 3 つあります。測度の表、Windows の経路を結論に書いた部分、題と要旨が文の漏れの大きさを示していない点です。
- 冗長さが大きく、引き継ぎの #10 は未解消です。

---

## 1. 接地（この立場が論文に求める基準）

**Conijn et al. (2019)**
- C1: どの測度を選ぶかが解釈を決める。"The selection of the correct keystroke features is crucial for the interpretation of the results and therefore, the derived conclusions."（conijn2019.txt:84-86）
  - 測度を定義で示すことも求めている。"The terminology of these time-based features is sometimes used interchangeably. For clarity, we provide an overview of the time-based features"（100-101）
- C2: バーストには修正と先端の外への挿入の情報が要る。"written language bursts are often operationalized as sequences of text production (keystrokes) without an IKI longer than two seconds and without a revision and without an insertion away from the leading edge"（146-148）
- C3: 課題をまたいで一般化しない。"caution should be taken when generalizing the effect of these features across tasks"（808-809）

**Monaco (2018)**
- M1: 時刻や位置が粗くても、打鍵の記録は内容を漏らす。"nontrivial information gains can be achieved even in the presence of substantial measurement error"（monaco2018.txt:20-22）
- M2: 検出と同定は分けて評価する。"Keylogging is a two-step process comprised of two distinct problems: keystroke detection and key identification."（382-383）
- M3: 時刻の情報量は人によって違う。"These results suggest that temporal side channel information gain is highly user-dependent."（698-699）

**Crotti et al. (2026)**
- K1: 入力方式を通る書字では、言語の単位と確定の前後で打鍵間隔を分けるべき。"A robust input logger for research should identify these types of IKIs"（crotti2026.txt:336-337）
- K2: 比べる次元を明示し、比べた材料の出どころも明示する。
  - "We compared the input loggers across three dimensions: whether or not they are ecological …, if they include support for non-alphabetic languages …, and their ability to record fine-grained timestamps for keyup and keydown events"（488-492）
  - "The data reported in the table derive from our direct experience with Inputlog 9.5, Translog II, GenoGraphiX-Log and CyWrite."（480-482）
- K3: 押下の重なり（rollover）は無視できない。"Rollover—where a second key starts to be pressed before the first is completely released—is a salient phenomenon"（440-442）。Table XIII では John の Latin letters の 26.44%（1610 行）。
- K4: 規模を正直に言う。"Given the small sample (two participants), results are only illustrative."（1258-1259）

---

## 2. 評価表

**a 主張と根拠の一致: 3**
- 事前登録・逸脱・範囲の断りは丁寧です。
- 要旨と結論の主の数値（区間の端の範囲）は、一致の大きさを伝えていません（指摘 1）。
- 測度の表の「Yes」の 2 行（バースト・キーを押している時間）は根拠を越えています（指摘 3）。
- Windows の窓のイベントの経路を結論で前に出していますが、データはこの経路が働いたことを示していません（指摘 4）。

**b 方法の穴: 3**
- 精度の計画、外したものの扱い、ブロックを単位にした bootstrap、予測との 3 つの比較は良い設計です。
- 穴は 3 つあります。
  - 文ごとの ICC が設計のために縮退している（指摘 5）。
  - Windows の計測機の状態が報告されていない（指摘 8）。
  - closed-set の攻撃の囮が長さの違う句から引かれ、同定の仕組みが分析されていない（指摘 2）。

**c 持ち帰れるもの: 2**
- 考察の節がありません。読者が知りたいことが本文に書かれていません。
  - macOS は S6（Backspace で全部消す）と S10（Tab で予測候補）でだけ一致が落ちる。
  - Windows は S2/S8 が二行に割れ、速い打鍵で取りこぼす。
  - Windows の `dwell_ms` は 1 セッションあたり 0.5〜1 秒短い。
- 推奨 5 つのうち 3 つは「しないこと」です。研究で使うための情報もありません。
  - 権限
  - アプリを区別できないこと
  - パスワードの打鍵

**d 簡潔さと構成: 2**
- 約 21,100 語・66 頁・表 18（横向き 10）です。
- 同じ断りが 4〜7 回繰り返されます（指摘 6）。
- 要旨には約 30 の数値の範囲が入り、読めません。結論は要旨の数値を並べ直しただけです。

**e 規程への適合: 3**
- 要旨 249 語（上限 250）、Declarations の見出し、OPS の位置、標本数の決め方、除外の報告は満たしています。
- 満たしていないもの:
  - タイトル頁に住所と電話がない（"must"）。
  - double spacing と右上の頁番号が main.tex に見当たらない。
  - データの DOI が参考文献の一覧に入る形になっていない。
  - 表に内部の識別子が出ている（指摘 9・10・11）。

**f 先行研究の位置づけ: 3**
- Crotti らとの比べ方はおおむね公平です。Hylog の検出の値を並べない理由も書いてあります（related.tex:30-32）。
- ただし残る点があります（指摘 7）。
  - Hylog の中核の次元（IKI を単位で分けること）が表の列にない。
  - Inputlog 9.5 の評価を 9.7.0.1 の行に当てている。
  - 最も使われる道具の検証の欄が "Not examined" のまま。
- IME の文字入力の評価の文献も欠けています（outline.md:555-556 の open item のまま）。

---

## 2b. 引き継ぎの判定

| # | 判定 | 原稿の位置と逐語 |
|---|---|---|
| 1 | **一部** | 規則（30 試行以上の層・外した数）は main.tex:102-108 に入った。しかし範囲は依然として一致を伝えない。primary で "0.280--1.000"（values.tex:338）、全試行で "0.000--1.000"（values.tex:15, 392, 776）。main.tex:111-113「over all trials recall spanned …」→ 指摘 1 |
| 2 | 解消 | recommendations.tex:32-37「it reads the reference side only and does not estimate the logger's agreement … no shorter registered check exists for macOS」 |
| 3 | 解消 | introduction.tex:15-18「A logger that keeps only the final text does not see it. A logger of keys does not record it directly … A logger that observes the conversion reads the composition string or the text on the screen.」と 20-21「A log that holds neither the text nor the names of keys …」 |
| 4 | 解消 | logger.tex:27-36（脚注「every analysis uses the rows of presses only」・「the times of releases enter no measure」）と table-key-timing.tex:4「Timing of the key rows of presses」 |
| 5 | 解消 | table-reference.tex:10, 22, 35, 42（各群に「read with misses in detection …」などの読み方がある） |
| 6 | 解消（外枠の事項） | outline.md:32-34 に "effect size" が戻った。原稿には method.tex:177-187 の精度の計画と区間がある |
| 7 | **未解消** | outline.md:567-568「What else was running on the Windows measuring machine during the completed run is to be established」のまま。results-agreement.tex:18-19「ended while the machine was short of memory」→ 指摘 8 |
| 8 | 解消 | recommendations.tex:16-23「On the window-event path on Windows a long conversion is kept as a row of about 25~s」と「on Windows a row does not record which path wrote it」 |
| 9 | 解消 | limitations.tex:17-18「They hold for an unknown mixture of the logger's two paths」 |
| 10 | **未解消** | 「別の構成概念」の断りが 7 か所にある（main.tex:113-114, introduction.tex:39-41, observability.tex:125-128, results-agreement.tex:9-12, recommendations.tex:11-14, limitations.tex:16-17, conclusions.tex:33-34）→ 指摘 6 |
| 11 | 解消（ただし新しい誤りあり） | logger.tex:155-160 に語数・効率・入力モード・境界の休止・「Defined by this study」が入った。新たに「Bursts … Yes」「Key hold times … Yes」の過大がある → 指摘 3 |
| 12 | 解消（公平さに残りあり） | related.tex:14-16 に選び方（Wengelin の 5 本 ＋ Hylog）。46 行に言語別版の独立の行、49 行に「Two participants, one input method」、30-32 行に並べない理由 → 残りは指摘 7 |
| 13 | 解消（原稿に ID は出ない） | recommendations.tex:1 のコメント「claims RE1 to RE5」だけ |
| 14 | 解消 | README.md:1 の題が一致。6-7 行「`experiment/data.md` (macOS) and `experiment/data.windows.md` (Windows)」 |
| 15 | 解消 | logger.tex:2-3 のコメント「the format specification kit/formats/FORMATS.md, and sections 1.1, 4.4 and 10.3 of the registration」 |
| 16 | 解消 | dataset.tex:49「times of presses and releases on both systems」 |
| 17 | 解消 | main.tex:113-114「where the logger's sessions … are a different construct」。CPU は要旨にない。main.tex:119-120「so none is recommended; nor did either on Windows」 |

---

## 3. 指摘の一覧（severity の重い順）

- [severity: major] 要旨と結論の主の数値（区間の端の範囲）は一致を伝えず、どこで一致が落ちるかは本文のどこにもない（考察の節もない）
  - 位置と引用:
    - main.tex:111-113「over all trials recall spanned \rv{macos-standard-live-off.all.recall.range} and …」。値は values.tex:15 と 392 で「0.000--1.000」。
    - main.tex:102-104 の primary は values.tex:338「0.280--1.000」、718「0.301--1.000」。
    - conclusions.tex:14-42 は同じ範囲を並べ直しているだけ。
    - method.tex:330-331「the estimates are described without evaluative words」。
    - 原稿の構成（main.tex:127-139）に Discussion がない。
  - なぜ問題か: 範囲の狭い端は、少数の場面で決まっています（補遺の表で確かめた）。
    - macOS で範囲の下端を決めているのは S6（detection-strata.tex:112「S6 & fast … 0.386 [0.280, 0.503]」）と S10（120-121「0.500」「0.493」）。他の場面は概ね 0.92〜1.00。
    - Windows は S2/S8 で 1 つの変換が二行に割れ（1068「split rate 0.952」・1086「0.969」）、S1 は速い打鍵で 0.571（1067）。
    - 書字研究の利用者にとって使える情報は「どの変換の仕方で、どの速さで、どちら向きに外れるか」です。予測候補の確定、読みの全消去、候補の巡回はいずれも日常の書字にあります（C3 の通り、場面をまたいで一般化できません）。
    - 「評価語を使わない」規則と、パターンを記述することは矛盾しません。
  - 解消の条件:
    - 要旨は pooled の値（例: 0.896 [0.883, 0.908]、values.tex:256）か中央の層の値に、最も低い場面の名前を添える形に変える（規則が外枠で固定済みなら、外枠に逸脱として記録する）。
    - 全試行の 0–1 の範囲を要旨から外す。
    - 結果の後に Discussion を置き、低い層を場面と速さで名指し、ロガーの規則のどれが原因か（macOS では gt_pred と gt_obs が同じなので規則の側）を書く。
  - 自信: 高

- [severity: major] 文の漏れの大きさ（K=10 で 0.90）が要旨と結論にない。同定がほぼ数（長さ）だけで起きることも説明されていない
  - 位置と引用:
    - main.tex:118-120「neither granularity of the key rows without times met the registered near-chance rule … so none is recommended」。
    - 値は table-closed-set.tex:9-12。`no_time` と `counts_only` が全セルで同じ「0.902 [0.890, 0.913]」「0.421 [0.403, 0.440]」。
    - recoverability.tex:96-109 は判定だけを書いている。
  - なぜ問題か:
    - 時刻を除いたキーの行で、10 の候補から 9 割、100 の候補から 4 割強を当てています。題の "without recording text" は記録しないことの主張で、明かさないことの主張ではありません。それでも読者は後者と読みます。
    - `no_time` が `counts_only` と同じ値なので、識別はほぼ種類ごとの数（＝読みの長さ）で起きています。これは公開の仕方を決める実務の情報なのに、述べられていません。
    - Monaco は粗い観測でも情報が漏れることを示しています（M1 "nontrivial information gains can be achieved even in the presence of substantial measurement error"）。
    - 囮が 6〜30 かなの長さの違う句から引かれる設計（recoverability.tex:33-35、method.tex:163-164）が数の効きを強めている可能性もあり、ここも分析されていません。
  - 解消の条件:
    - 要旨と結論に K=10・100 の正答率と chance を数で入れる。
    - 「数だけで同じ正答率になる」ことと、それが長さを通じて起きることを結果の節で述べる。
    - 囮の長さを揃えた場合の値を探索的に示すか、示せないなら限界に書く。
    - 題は変えないとしても、序論の最後か結論に「記録しない ≠ 明かさない」を一文で置く。
  - 自信: 高

- [severity: major] 測度の表が「計算できる」を言い過ぎている。ログがアプリ・焦点・マウスを持たないことも書いていない
  - 位置と引用:
    - logger.tex:154「Bursts of typing & Yes & Yes & No & Not evaluated」
    - logger.tex:152「Key hold times & Yes & Yes & No & Releases are paired by category only」
    - logger.tex:85-86「observed system-wide without identifying its application」
    - logger.tex:9-11（行は header・キー・セッションだけ）
  - なぜ問題か:
    - バーストは修正と先端の外への挿入を除く定義です（C2 "without a revision and without an insertion away from the leading edge"）。このログにはカーソルの位置もマウスもなく、Backspace が読みを消したか確定文を消したかも分かりません（logger.tex:153 自身がそう書く）。休止で切った近似しか作れません。
    - 押している時間は、同じ種類（文字）のキーが重なると種類だけでは対にできません。Crotti らの資料では、文字の間の rollover が 26%（K3、crotti2026.txt:1610）に及びます。
    - さらにログは全アプリの打鍵を区別なく持つので、自然な書字ではすべての測度に検索窓やチャットの打鍵が混ざります。研究者が最初に知るべき制約です（C1）。
  - 解消の条件:
    - バーストは「休止で区切った近似のみ（修正・先端の条件は不可）」に、押している時間は「重なりのない打鍵のみ・同じ種類の重なりでは対にできない」に直す。
    - 表か本文に「行はアプリも焦点もマウスも記録しない → 対象の文書の打鍵だけを分けられない」の行を足す。
  - 自信: 高（バーストと押している時間）／中（rollover の割合を日本語のローマ字入力に当てること）

- [severity: major] 結論は Windows の窓のイベントの経路を前に出すが、データはその経路が測定で働いたことを示していない
  - 位置と引用:
    - conclusions.tex:8-11「Windows offers events of the input method's windows that carry no text, which the logger follows … that the Windows route works was established only for the input method measured」。
    - 対して observability.tex:63-65「the candidate window of the Microsoft input method was shown and hidden by uncloaking and cloaking it, and the window events of the input method did not arrive」。
    - results-agreement.tex:197-199「no row lasted from 20 to 25~s … so the rows give no indication of the window-event path」。
    - S13 は「wait 21~s」（method.tex:142）。
  - なぜ問題か: 窓のイベントの経路には 20 秒の打ち切りがありません（logger.tex:89）。S13 でこの経路が働けば、20〜25 秒の行が出るはずですが、1 本も出ていません。開発時の観察と合わせると、測った入力方式の行は cloaking の経路（入力方式の窓のクラス名に依存）から来た可能性が高いです。「Windows の経路が働くことが確かめられた」と書くと、他の入力方式へ移せる見込みを読者に過大に伝えます。
  - 解消の条件: 結論を「測ったセッションがどちらの経路から来たかは分からず、20〜25 秒の行が無いことは cloaking の経路と矛盾しない」に直す。cloaking の経路が入力方式の窓のクラス名に依存することを結論か推奨に置く。
  - 自信: 中

- [severity: major] 文ごとの ICC が設計上縮退しているのに、説明がない
  - 位置と引用:
    - table-text-agreement.tex:10-12「Conversions per trial … 0.000 [$-$0.000, 0.000]」（Windows の slow と mid も同じ、34-35 行）。
    - Fraction of time converting は 0.000〜0.037（19-21, 31-33 行）。
    - results-text.tex:9-12「the ICC … also depends on how much the texts of this design differ」で止まっている。
  - なぜ問題か: 基準の側では、どの試行もほぼ 1 つの変換を持つように作られています。そのため文の間の分散がほぼ 0 で、ロガーの良し悪しに関係なく ICC は 0 に寄ります。書字研究の読者は ICC = 0 を「一致しない」と読みます。4 つの集計のうち 2 つで、主の一致の指標が情報を持ちません。
  - 解消の条件: 縮退を本文で明言し、その 2 つの集計では一致の限界だけを読むように書く（あるいは ICC を「設計上定義できない」と表で示す）。基準の側の文の間の SD を表に添える。
  - 自信: 中（縮退の原因の推定は表の値からの推論。結果のファイルは読んでいない）

- [severity: major] 同じ断りの繰り返し（引き継ぎ #10 が未解消）
  - 位置と引用:
    - 「別の構成概念」の断りが 7 か所（2b の #10 の行の位置）。
    - 「privacy の基準ではない」が recoverability.tex:56-57, 108-109、recommendations.tex:29-30、conclusions.tex:46-47。
    - 「外部の装置で測っていない」が related.tex:93-97、method.tex:62-68、results-agreement.tex:109-112、limitations.tex:12-13。
    - 「pooled の Wilson は下限」が method.tex:186-187, 327-328、results-agreement.tex:152-153、limitations.tex:58-59。
  - なぜ問題か: 21,000 語の原稿で、どの段落を消しても主張が弱くならない箇所が多いです。指摘 1 と 2 で述べた実務の情報が、断りの中に埋もれています。
  - 解消の条件: 各断りは定義の 1 か所（方法か限界）にだけ置き、他は節の参照にする。結論は数値を並べ直さず、指摘 1 の要約に置き換える。目安は本文 15,000 語前後。
  - 自信: 高

- [severity: minor] Crotti らとの比べ方: 相手の中核の次元が表にない。版がずれている。検証の欄の材料が片寄っている
  - 位置と引用:
    - related.tex:41 の列（「Input-method conversion」「Text or key names in the log」「Validation reported」）。
    - related.tex:45「Inputlog 9.7.0.1 … Not supported$^{a}$ … Not examined$^{b}$」と脚注 54-56「which examined Inputlog 9.5」「The primary article is not openly accessible and was not read」。
  - なぜ問題か:
    - Hylog の存在理由は、IME の打鍵間隔を単位と確定の前後で分けることです（K1）。それを列にせず、このロガーが勝つ次元（文もキー名も持たない）を足しています。本文の「does not separate inter-key intervals by script」（related.tex:33）は、Crotti の (a)〜(e) の分類とは別のことです。
    - 9.5 の評価を 9.7.0.1 の行に置くのは、Crotti 自身が出どころを版で限っている書き方（K2）と合いません。
    - 最も使われる道具の検証を "Not examined" とし、自分の行を "pre-registered" とするのは、読む材料の差が比べる結果に出ています。
  - 解消の条件:
    - 列「IME の単位ごとの打鍵間隔（音節・語・確定の前後）」を足し、このロガーは「不可（確定の前後のみ近似）」とする。
    - Inputlog の行は 9.5 として書くか、9.7.0.1 の文書から埋める。
    - 検証の欄は公開の資料で埋められなければ、表の注で非対称を明言する。
  - 自信: 高

- [severity: minor] Windows の完了した試行の計測機の状態が報告されていない（引き継ぎ #7）
  - 位置と引用: results-agreement.tex:18-19「when the process that ran it was ended while the machine was short of memory」。outline.md:567-568 が open のまま。
  - なぜ問題か: 8 GB の機械で 1 回目がメモリ不足で止まっています。2 回目に何が動いていたかは、届き方・遅れ・取りこぼし（速い打鍵での recall 0.571）の読みに関わります。
  - 解消の条件: method.tex §5.2 と表 attempts に、2 回目の間に動いていたもの（または確かめられなかったこと）を書く。
  - 自信: 高

- [severity: minor] 研究で使うための情報がない（権限・全アプリの打鍵・パスワード）
  - 位置と引用:
    - recommendations.tex:7-41（5 項目のうち (a)(c)(e) は「しないこと」）。
    - 原稿に macOS の event tap の権限（入力監視）の記述がない（"permission"・"Input Monitoring" の語が無い）。
    - kit/logger/README.md:41「Run as: `ime-observation-logger --out <path> [--duration-s <n>]`」だけ。
  - なぜ問題か: BRM の規程は "BRM readers want practical solutions." を求めます（context-A の抜粋）。人を対象にこのロガーを使う研究者は、次のことを知る必要があります。
    - 権限の付け方
    - 全アプリの打鍵（パスワードの欄を含む）が数として入ること
    - 同意文書に何を書くべきか
  - 解消の条件: 推奨か補遺に「人で使う前に」の短い節（権限、全アプリの打鍵が入ること、アプリを区別できないこと、行の公開は判定していないこと）を置く。
  - 自信: 中

- [severity: minor] タイトル頁に住所と電話がない。double spacing と頁番号が見当たらない
  - 位置と引用: main.tex:86-87「The postal address and the telephone number of the corresponding author are given in the submission system only.」。main.tex:5-15 に setspace も `\doublespacing` もない。
  - なぜ問題か: 規程は "The title page must include … the corresponding author's address, telephone number, and e-mail address." と "All manuscripts are to be double spaced and have 1” margins with page numbers in the upper right corner of each page." です。
  - 解消の条件: タイトル頁に住所と電話を入れ、組版を double spacing・1 インチの余白・右上の頁番号にする（雛形のオプションで足りるなら、その旨を確かめる）。
  - 自信: 中（雛形の既定の行間は確かめていない）

- [severity: minor] データとコードの DOI が参考文献の一覧に入る形になっていない
  - 位置と引用: declarations.tex:27-28「deposited in Zenodo under the persistent identifier \tbd{DOI of the dataset}」。references.bib にはデータセットとリリースの項目がない（OSF の 2 件だけ、6-21 行）。
  - なぜ問題か: 規程は "Data citations should include a persistent identifier (such as a DOI), should be included in the reference list" です。`\tbd` を埋めても本文の中だけに残ります。
  - 解消の条件: データセットとコードのリリースを bib の項目にし、本文と OPS から `\citep` で引く。
  - 自信: 高

- [severity: minor] 表に内部の識別子が出ている
  - 位置と引用:
    - table-detection.tex:9「macos-standard-live-off & \texttt{gt\_obs} (primary)」
    - table-closed-set.tex:9「\texttt{no\_time}」
    - table-session.tex など
  - なぜ問題か: 規程は "Figures and tables are to be designed as per APA style." です。読者はコードの名前を本文と対応させなければなりません。
  - 解消の条件: 「macOS, live conversion off」「Reference vs. logger」「No time」などの読める名前に置き換える（生成の道具の側で）。
  - 自信: 高

- [severity: minor] 読んでいないと注に書いた一次文献を、本文で引いている可能性がある
  - 位置と引用: related.tex:56「$^{b}$The primary article is not openly accessible and was not read.」と、introduction.tex:8・related.tex:12 の `\citep{leijten2013,...}`。
  - なぜ問題か: 注の "primary article" が leijten2013 なら、読んでいない文献を一般の主張の根拠に使っています。
  - 解消の条件: 注 b がどの文献かを明記する。leijten2013 なら、本文の引用を読んだ文献（wengelin2023 など）に限るか、読む。
  - 自信: 低

- [severity: nit] Translog-II の key-up の扱いが出典の間で食い違う
  - 位置と引用: related.tex:48「Key-down only \citep{zou2026}」。Crotti は Translog II を "does not have visibility of keyup and keydown events"（crotti2026.txt:497）としている。
  - 解消の条件: 食い違いを注で一言書く。
  - 自信: 中

- [severity: nit] 公開する README に開発中の言い回しが残っている
  - 位置と引用: README.md:25-27「## Component staging areas / Subsequent components are built at the following locations.」
  - 解消の条件: 「Components」などに改め、使い方の入口（ロガーの README）を指す。
  - 自信: 高

---

## 4. 総合の推奨: **major**

1. 主の貢献である一致の推定が、区間の端の範囲（全試行で 0.000–1.000 を含む）でしか要約されていません。どの変換の仕方と速さで一致が落ちるかが本文と要旨にありません。考察の節もありません。
2. 測度の表の過大（バースト・押している時間）、アプリを区別できないことの欠落、Windows の経路を結論に書いた部分、縮退した ICC の無説明は、書字研究の利用者を誤らせます。
3. 方法の土台（事前登録・逸脱・範囲・予測との比較・透明な寄託）は強いです。上の点の書き直しと分量の圧縮で、受理に足る原稿になると考えます。

---

## 5. 読めなかった範囲と注入の疑い

**読んでいない（一覧にあるが読まなかったもの）**
- experiment/preregistration.md・deviations.md・notes.md・data.md・data.windows.md・pilot-macos.md・pilot-windows.md
- kit/run/README.windows.md・kit/e3/README.md・e3_macos.txt・e3_windows.txt
- ロガーのソースのすべて
- supplement/observability-documents.tex
- generated の fig-*.tex・table-cost.tex・reference-strata.tex・session-strata.tex・text-agreement.tex・closed-set-all.tex・detection-layers.tex
- figures/components.tex
- 読む補助の main.txt

**一部だけ読んだ**
- outline.md: 549-572 行と grep の結果だけ
- FORMATS.md: grep だけ
- detection-strata.tex: macOS の live off の primary（86-137 行）と Windows の primary（1060-1104 行）だけ
- references.bib: grep だけ

**接地の本文**
- conijn2019.txt: 882 行以降（参考文献）を読んでいない
- monaco2018.txt: 131-369、480-594、725-1119、1355 行以降を読んでいない
- crotti2026.txt: 840-929、1099-1239、1350-1599、1709 行以降を読んでいない

**注入の疑い: なし。** 読んだ範囲の接地の本文と対象物に、査読者や LLM に向けた指示は見当たりませんでした。
