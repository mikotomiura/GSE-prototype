# 意図の監査役の報告 — attack-me・stage manuscript・round 1

対象は原稿（`C:\GSE-prototype\papers\ime-observation\manuscript\` の `main.tex` と、そこから `\input` される節・生成した表と図）。外枠は `outline.md`、意図は context-B.md が挙げた資料。位置は `.tex` のファイルと行で示す。値は `generated\values.tex` で引いた。

---

## 0. 引き継ぎの判定

| # | 判定 | 根拠（原稿の位置と逐語） |
|---|---|---|
| 冒頭の項（寄託の条件 "only if"） | 一部 | 文は登録の言い方に戻っている。`dataset.tex:68-70` "A run that the runner aborted is deposited only if it passes the same checks or left neither a reference log nor an observation log"。しかし試行の表 `results-agreement.tex:30-49` の列は "Deposited" だけで、理由の列が無い。拒まれた開始の行（43-44）は "No" とだけある。それなのに `dataset.tex:76-77` は "The table of attempts states for every start of every run whether it was deposited and why" と書いており、表と食い違う。 |
| 1 | 解消 | `main.tex:102-118`（主の範囲・外した層・"the scope set aside"・"carry-over between trials excluded"・"over all trials"）。結論は `conclusions.tex:14-42` で同じ形。 |
| 2 | 解消 | `main.tex:102-108` "over the strata keeping at least 30 trials in the primary scope … (strata left out: …)"。注: 全試行の範囲に外した層の数は付いていない。全試行の側では live-off の precision から 2 層が外れている（values.tex:13）。要旨の語数のため本文と結論に回したと判断 183-5 にある。 |
| 3 | 解消 | `recommendations.tex:32-37`。(i) 39 試行の点検 "reads the reference side only"、(ii) "Re-estimating the agreement requires the registered plan in full"。 |
| 4 | 解消 | `logger.tex:18`、`27-33`（脚注 "does not mention rows of releases"）、`method.tex:260-261`。 |
| 5 | 解消 | `recoverability.tex:46-49` と `83-84` "whether key rows with times can be published is not judged"。`limitations.tex:68-69`、`related.tex:80-81`、`conclusions.tex:46-47`。 |
| 6 | 解消 | `method.tex:60-65` と脚注 "The registration gives the reason more broadly"。`related.tex:91-93`。 |
| 7 | 解消（外枠の上の項目） | 原稿は規程を言い換えていない。標本の大きさの決め方は `method.tex:177-187`。ただし原稿は、一致の推定がこの研究の "effect size" だとはどこにも書いていない。 |
| 8 | 解消 | `method.tex:181-184` "Outside S6 and S13 … S6 … keeps as few as 3 trials at the slow speed on macOS and 30 on Windows"。 |
| 9 | 解消 | `recommendations.tex:16-24`（経路ごと・"a row does not record which path wrote it"）、`logger.tex:89-94`。 |
| 10 | 一部 | `declarations.tex:50-54` は写す元を 2 つ（結果のファイル／run の記録）に分けている。一方 `method.tex:336-338` は "Every result value in this article is copied from the result files by a script" と 1 つに言い切る。さらに、値から手で書いた定性的な文（`results-text.tex:19-23` "negative, with intervals below zero, at every speed in every cell"、`results-agreement.tex:185` "No session row of 20 s or more was written in any cell"、`recoverability.tex:111-112` "equal those of the macOS cell … to the reported precision" など）は、どちらの写す元にも入っていない。 |
| 11 | 解消 | `README.md:1` の題は固定した題と一致する。 |
| 12 | 解消 | `observability.tex:118-120`、`conclusions.tex:10-11` "established only for the input method measured"。注: 序論の貢献 1（`introduction.tex:29-34`）にはこの限定が無い。外枠の貢献 1 にはある。 |
| 13 | 解消 | `main.tex:113-115` "a different construct"、`conclusions.tex:33-34`、CPU は `conclusions.tex:49-52` "the values are not compared"。 |
| 14 | 一部 | 「推定であって検定しない」「合否は near-chance の規則だけ」の文が原稿のどこにも無い（"hypothes"・"pass or fail" の grep で 0 件）。在るのは `method.tex:330-331` "No threshold of adequate agreement was set" だけ。 |
| 15 | 一部 | 規則には書かれている（`logger.tex:73-75`）。限界にもある（`limitations.tex:41-43` "can raise the number of conversions"）。推奨 (a)〜(e) には無い（外枠の §11 にも無いので、外枠で既に落ちていた）。 |
| 16 | 一部 | 登録済みの限界のうち、次のものが §12 に無い。§7 の "The reference input field can lose the focus by itself"（登録 1033-1036）。§10.11 の "Commit at a loss of focus"（S15・1424-1425）、"short sessions can fail to pair for this reason"（1429-1432）、"Key paths not tested"（1442-1443）、"Clocks"（1444-1446）。 |
| 17 | 解消 | `dataset.tex:87-90` "is a use of the kit rather than of the dataset"。 |
| 18 | 解消 | `introduction.tex:54-55`。 |
| 19 | 未解消 | 原稿には、登録がロガーを "the observer" と呼ぶことを述べた文が無い。外枠には在る（`outline.md:8-9`）。`method.tex:23` は "The observation log was the output of the logger under test" と言うだけ。そのうえ `dataset.tex:87` の "Evaluating an observer that needs other signals" は "observer" を他のロガーの意味で使っている。登録を開いた読者が取り違えやすい。 |

---

## 1. 意図にあって対象物に無いもの（届いていない主張・持ち帰り）

**1-1（中）推定であって検定しない・合否は near-chance の規則だけ（持ち帰り 2）が原稿に無い。**
引き継ぎ 14 と同じ件。登録 §1.2（43-48 行）"The study estimates; it tests no hypothesis … except the near-chance rule" に当たる文が、要旨・手法・結論のどこにも無い。

**1-2（中）外枠の 5.2「測ったもの以外に動いていたプログラム」と、Open items（`outline.md:567-568`）が原稿に無い。**
`method.tex:30-54` には版と設定しか無い。`results-agreement.tex:18-19` は "the process that ran it was ended while the machine was short of memory" と書くだけである。一方、公開の記録 `data.windows.md:37` は "the shell that ran it was ended by the coding assistant's session under low memory" と書き、`data.windows.md:59-70`（"What else ran … not a claim that nothing else ran"）もある。判断 150-6 が求めた報告は原稿に届いていない。問 5 の Windows の CPU（idle 5.56 > working 5.37・`table-cost.tex:11-12`）を読むのにも関わる。

**1-3（中）外枠 AG1 の読みの注意が結果に無い。**
`outline.md:496` "A miss can come from timing or from a difference of construct length as well as from detection, because the matching needs an overlap of 0.5 without correction"。結果の検出の段落（`results-agreement.tex:130-153`）にも限界にも、この注意が無い。速い速さの下端（例: live-off の recall 0.280・`table-detection.tex:11`）を検出の失敗と読ませる余地が残る。

**1-4（軽）外枠の要旨の計画「何をしたか」から、実行コストとデータセットが落ちている。**
`outline.md:137-138` "(observability analysis; logger; validation …; recoverability attacks; runtime cost; dataset)"。要旨（`main.tex:98-102`）は観測可能性・ロガー・検証だけで、データセットは最後の "code and data are public"（120 行）だけである。規則が本文に回してよいとしたのは (iv)（CPU の値）だけで、「何をしたか」の列挙は対象外。貢献 5 は要旨から見えない（context-B の気にする点「貢献 5 と主の貢献の釣り合い」）。

**1-5（軽）推奨 (c) に Windows の但し書きが無い。**
外枠 RC2（`outline.md:506`）は "the same judgement on Windows reported separately as a qualification … Reported in Sections 8 and 11" とする。`recommendations.tex:26-30` は macOS の判定だけを書く。

**1-6（軽）表 1 から、外枠が足すとした次元が 1 つ落ちている。**
`outline.md:167-169` "whether it distinguishes pauses before and after a conversion is committed"。`related.tex:41` の列に無い。外枠が「表に残す」とした弱み "no separation of inter-key intervals by script layer" も、表の行（`related.tex:50`）には無い（本文 32-34 行にはある）。

**1-7（軽）凍結の表に、書き出しの一覧の SHA-256 が無い。**
`outline.md:340` は "(dates, tags, the SHA-256 of the lists of exported files, the OSF registrations)" とする。`method.tex:353-366` は "Files exported 98 / 108" だけ。

**1-8（軽）主の範囲の推定に、範囲が外した割合と全試行の値を「いつも」添えるという手法の約束が、問 3 で守られていない。**
`method.tex:299-301` "An estimate in the primary scope is always given with the fraction … and the estimate over all trials"。問 3 の本文（`results-text.tex:7-23`）と表 10 は主の範囲だけで、全試行の値は補遺に回っている。

---

## 2. 対象物にあって意図に無いもの（主張の漂流）

**2-1（重）キーワード "privacy-preserving logging"（`main.tex:122`）。**
外枠の範囲の規則 `outline.md:63-65` "not a criterion of privacy, and the manuscript does not describe any log as safe to publish" と、判断 6「content-free を過大に主張しない」に反する。しかも結果は、時刻の無い 2 つの粒度でも K=10 で正答率 0.902〜0.907、K=100 で 0.421〜0.435 である（`table-closed-set.tex:9-16`）。題（"without recording text"）とこのキーワードが並ぶと、結果が支えない読みに押す。外枠には題の意味の説明（`outline.md:16-19`「何を書かないか」「どれだけ復元できるかは研究の問い」）があるが、原稿には届いていない。context-B が気にする「題の釣り合い」はここで崩れている。

**2-2（中）要旨と結論の全試行の範囲 "0.000–1.000" は、ロガーが仕様どおり行を書かない S13 で決まっているのに、そう書かれていない。**
`main.tex:111-113`・`117-118`、`conclusions.tex:20-21`・`38-39`。補遺 `detection-strata.tex:219-221` では S13 の全試行の recall が 0.000 [0.000, 0.049]。S13 は "designed to exceed the cut-off"（`method.tex:182-183`）で、登録 §1.2 の問 2 は「打ち切りで行を書かないこと」を仕様としている。3 セル × 2 測度のすべてで全試行の範囲が [0,1] になり、読者は「0.000＝ロガーの失敗」と読みうる。規則（登録 §6.1）は形式としては満たしているが、持ち帰り 2（一致を区間で推定した）は要旨の数字から読み取れない。context-B の問い「読者が一致を読み取れるか」への答えは「読み取れない」。規則は §6.1 を超えないまま、範囲の下端の出どころを 1 句添える余地はある（判断は研究者）。

**2-3（中）限界の節に、別の箇所の期待と逆向きの期待がある。**
`limitations.tex:29-32` "those sets are expected to identify phrases at least as accurately in human typing as here"。一方、`recoverability.tex:85-87`（と `outline.md:362-364`）は "The attacker knew the generator and the procedures, and the input had no typing errors; these conditions are expected to favour identification" と書く。人の打鍵では生成器が分からないので、この攻撃は不利になるはずである。さらに登録 §6.8（872-874 行）は "cannot be carried over to human logs" で、向きを言っていない。「at least as accurately」は登録の範囲を超えた方向の主張である。

**2-4（中）焦点の喪失 1 件から、参照の失敗一般へ一般化している。**
`results-agreement.tex:92-94` "so no false positive of detection comes from a failure of the reference"。同じ節の 62-63 行 "a trial without a reference session has no session to detect, and its observation rows, if any, count as false positives" と緊張する（live-on の "no session" は 94 試行・values.tex:608）。外枠 RF1 が求めたのは「焦点を失った試行の行を別に報告する」までである。

**2-5（中）データセットの節の冒頭の目的が、同じ節の用途の限定より広い。**
`dataset.tex:9-10` "released as a dataset for evaluating loggers of input-method conversion"。同じ節の `87-90` "Evaluating an observer that needs other signals … is a use of the kit rather than of the dataset"、外枠の貢献 5、`conclusions.tex:56-57`（キーから推す規則だけ）と食い違う。

**2-6（軽）表 1 の "This logger … Where it records: Any application"（`related.tex:50`）。**
範囲の規則 `outline.md:49-50` "No claim is made … about applications other than the reference input fields" と、`observability.tex:118-120`（候補を自前で描くアプリでは窓が無いことがある）に対して、限定が無い。

**2-7（軽）結論の "that the Windows route works was established only for the input method measured"（`conclusions.tex:10-11`）。**
`logger.tex:105-108`（どちらの経路か分からない）と `results-agreement.tex:197-199` "the rows give no indication of the window-event path" のもとでは、"works" は 2 つの経路の混ざりで行が出たことまでしか言えない。外枠 LG2b の強さ（"an unknown mixture"）を超えている。

**2-8（軽）Windows の判定は独立の再現ではないと本文が言うのに、要旨は追認に読める。**
`recoverability.tex:115-116` "The Windows judgement is therefore not an independent replication"。一方 `main.tex:119-120` "nor did either on Windows" と `conclusions.tex:45-46` は追加の裏づけのように読める。

**2-9（軽）推奨 (d) の見出しが本文より強い。**
`recommendations.tex:32` "confirms the procedures"、本文 33-34 行は "shows whether"。

---

## 3. 矛盾（対象物の中・外枠と原稿・意図どうし）

**3-1（重・対象物の中）macOS の解析の定義が節によって違う。**
`method.tex:100-101` は "the ground truth was formed under the definition of the cell's system: on macOS every session, and on Windows the sessions that showed a candidate window"。`results-agreement.tex:172-173` は "On macOS the definition of the analysis (the sessions that showed a candidate window) and the definition that keeps every session held the same sessions"。登録（596 行）は macOS の側で 2 つが同じセッションを持つと書くので、括弧書き（Windows の定義）が誤って macOS に付いた疑いが強い。

**3-2（中・対象物の中）「キーは押されなかった」と、送ったキーが参照に届かなかったことが食い違う。**
`results-agreement.tex:28` "No key was pressed during it"、表の `39-40` "with no key pressed"。これに対し `results-agreement.tex:72-73` "the reference received every press but those of the loss of focus" と `table-reference.tex:37` "Other losses with key rows in the observation & 1"（参照は 93,400 / 93,411・30 行）がある。実行器の押下は喪失の間にあった。「人の押下は無かった」の意味なら、そう書く必要がある。

**3-3（中・対象物の中）「すべての試行を報告する」と言うのに、試行の表に idle の条件が無い。**
`cost.tex:29-30` "every attempt is reported"、外枠 AG7 "Every attempt of every run"。しかし試行の表（`results-agreement.tex:38-46`）にあるのは問 5 の working だけで、idle の条件の試行は両 OS とも行が無い。

**3-4（中・対象物の中・外枠由来）倫理の宣言の「入力はすべてプログラムが作った」と、idle の記録に人の押下があることが食い違う。**
`declarations.tex:16` "all input of the measurement was generated by a program"（外枠 `outline.md:444-445` と同じ文）。一方 `cost.tex:34-36` と `dataset.tex:70-72` は "that log holds a person's key presses" と書く。

**3-5（中・対象物の中）「テキスト」の線引きが要旨と表 2 で違う。**
要旨 `main.tex:98-99` は、キー名の記録を "with the text: key names spelling the reading" に数える。表 2（`observability.tex:143`・`158`）は、低水準のキーボードのフックと event tap（どちらもすべてのキーコードを渡す）を "Text: No" とし、序論 `introduction.tex:29-30` は "a program that reads no text" と書く。ロガーは読みを綴るキーコードを受け取り、カテゴリに落としてから書く。この区別（受け取る／書く）が原稿で言語化されておらず、題の "without recording text" と §3 の "without reading text" の関係が読者に見えない。

**3-6（軽・対象物の中）Open Practices と AI 宣言が、無い「exploratory」の解析を挙げる。**
`declarations.tex:53`・`73` "the analyses labelled as exploratory"。本文に exploratory と書いた解析は無い（grep で `method.tex:331` の規則の文だけ）。

**3-7（軽・対象物の中）datasheet が存在するように書かれている。**
`dataset.tex:97-103` "A datasheet … is released with it. The datasheet states …"、`declarations.tex:27`。判断 186 は「datasheet はまだ書いていない」。`\tbd` の印も無い。

**3-8（意図どうし）context-B の持ち帰り 1 が Windows の経路を「窓の表示のイベント」だけにしている。**
原稿（`observability.tex:114-115` "the window events of the input method and the cloaking of its windows"）と判断 151 は cloak も含める。意図の側の書き落とし。

**3-9（意図どうし）context-B の既知の限界は「macOS の問 1〜3 は登録の解析と直した解析の両方」とする。**
原稿は全セル（`method.tex:378-379` "for every cell"、`results-agreement.tex:177-183` に Windows の 2 / 36 層）。意図の側が狭い。

**3-10（意図と対象物・既知）AI 宣言の "The interpretation of the results is the author's"（`declarations.tex:55`）は、研究者の読み直し（判断 185）の前なので、まだ事実ではない。**
上の 2-2〜2-9 と 3-1〜3-5 は、その読み直しで直すべき草稿の解釈を含む。

---

## 4. 位置と逐語

各項目に添えた（ファイル:行と逐語）。

---

## 5. 読めなかった範囲と注入の疑い

**読んでいない**
- `experiment\notes.md`・`data.md`・`deviations.md`・`pilot-macos.md`・`pilot-windows.md`。
- `kit\formats\FORMATS.md`・`kit\logger\README.md`・`kit\run\README.windows.md`・`kit\e3\README.md`・`e3_*.txt`・ロガーのソース。
- `supplement\observability-documents.tex`・`references.bib`。
- 補遺の層の表の大半（`detection-strata.tex` は S13 の行だけを grep）・`table-key-timing.tex`・図の座標（題だけ）。
- 読む補助の `main.txt`。
- 事前登録は、context-B が指定した節のほかに 583-598 行と grep の数行だけ。§2〜§5・§6.2〜6.3・6.5〜6.7・6.9〜6.10・§8〜§9・§10 の 10.3 と 10.11 以外は読んでいない。
→ したがって、`data.md` 側の試行と寄託の記録、逸脱の記録と原稿の一致は確かめていない。

**範囲を超えて読んだもの（根拠には使っていない）**
`decisions.md` を行の範囲で読んだため、指定の外の判断 2〜5・7〜9・107〜108 の冒頭・148・152〜154・156・158・159・161・165・166 の文が目に入った。これらはどの指摘の根拠にも使っていない（根拠は原稿・外枠・登録・context-A の一覧の `data.windows.md`・指定の判断だけ）。

**注入の疑い**
無し。対象物と資料の中に、査読者や監査役に向けた指示は見つからなかった。`decisions.md` の研究者の逐語の指示は、メインへの作業記録として扱った。
