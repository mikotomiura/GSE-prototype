# 査読 R1（計時の道具を外部の基準で検証してきた方法論の伝統の査読者）・stage outline・round 2

対象: `C:\GSE-prototype\papers\ime-observation\manuscript\outline.md`（commit 9463fae6）

## 総合の推奨: major

- round 1 の 19 件のうち 12 件は解消しました。外枠の骨格（基準の妥当性 RF1 を主推定より前に置くこと、理想化の列挙、LG・DS の分割、D6）は書き進めてよい形です。
- ただし、直しから新しい major が 4 件出ました。
  - 要旨の規則が凍結した事前登録 6.1 と食い違う。
  - RE4 の「最小の単位」がロガーを検証していない。
  - ソフトウェアの層に基準を置く理由が、外枠自身の §2 と食い違う。
  - KT1 の遅れの定義が書かれていない。
- 4 件とも文言と定義の直しで消せます。ただ、事前登録との整合と、研究者が自分で検証し直せるという主張に関わるので、再査読で確かめたいです。

## 1. 接地（この立場が論文に求める基準）

3 本とも読めました（Bridges 2020 は 1 行の長いテキストなので grep で抜き出して読みました）。

- **G1 記録ではなく外部の基準で確かめる**
  - Plant (2016): "The sobering fact of the matter is that without using external chronometry there would be little chance of noting that stimuli had been presented for double the amount of time! Worryingly the log files suggested that the test had run normally imbuing an unwarranted confidence in the experiment, equipment, and software used."
  - 同: "The common thread being that the software or script being run can know nothing of the errors introduced by the hardware, rendering engine, or plug-in."
- **G2 理想化した手順は最良の場合しか示さない**
  - Plant: "benchmarking various experiment generators using idealized equipment and simplified scripts is counterproductive, lulls researchers into a false sense of security, and is unrepresentative of what they do and may achieve in the field."
  - Bridges et al. (2020): "A study like this can only show what performance it is possible to achieve in a given setting rather than what is likely to occur in a standard experiment."
  - 同: "Papers such as this one, which report “best case” timing performance, should not be used in lieu of study-specific validation and testing."
- **G3 自分の装置で、その場で検証し直す**
  - Plant: "researchers self-validate their own timing accuracy using external chronometry (e.g., using a Black Box ToolKit or oscilloscope) and state confidence intervals on publication. The only way to be sure of timing accuracy is to check it when paradigms are running in-situ, on the experimenter’s own equipment, at the time a given study is carried out."
  - Bridges: "We stress the importance of scientists making their own timing validation measurements for their own stimuli and computer configuration."
- **G4 合成入力は実際の使われ方に似せる**
  - Pinet et al. (2017): "A limitation of this approach is that their manipulation involved fixed intervals and a single button. A crucial and original feature of the present study is the use of three distinct keys from the keyboard, and the generation of variable delays between keys, just as it happens in actual experiments involving sequence production."
- **G5 遅れ（lag）とばらつき（precision）と分解能を分けて報告する**
  - Bridges: "we quantify the technological variability (precision) and lag (accuracy) using dedicated testing hardware"
  - Pinet: "showing a constant 60-ms delay for RTs and a 0-ms delay for IKIs"
  - 同: "This confirms that we should not expect a precision higher than 8 ms on actual IKI measurements."
- **G6 OS の中間層と機械の負荷は計時に入る**
  - Pinet: "OSs interpret successive or concomitant keyboard events according to both automatic and user-based settings ... The impact of this intermediate layer of software on keyboard chronometry is not known."
  - 同: "the delay between programmed and recorded responses is probably a mixed result of the load of ongoing programs running in the OS"

## 2. 評価表 a〜f

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | 31 行の大半は、事前登録の節と結果ファイルに正しく結ばれています（AG1・AG2・AG4・AG5・RC2・DS3 を確かめました）。ずれているのは次の 5 点です。(1) 要旨の規則が事前登録 6.1 と外枠の Scope に反する（M1）。(2) RE4 の根拠と主張がずれている（M2）。(3) RF1 の時計の値が、外枠の「結果の値はすべて結果ファイルから写す」という規則の外にある（m2）。(4) §5.4 の最小の層の数を誤って引いている（m4）。(5) LG2b は「§12 で報告する」と書くのに、§12 にその文が無い（m5）。 |
| b 方法の穴 | 3 | ソフトウェアどうしの一致であることは §5.3 と §12 に書かれました。ただし外部の基準を使わない理由が言い過ぎです（M3）。また、KT1 の遅れと RF1 の「時計の差」は同じ量（送った押下と記録された行の時刻の差）を別の名前で呼んでいて、時計のずれと届くまでの遅れを分けられません（M4・m1）。 |
| c 持ち帰れるもの | 3 | 用途 (b1)（保存した記録だけで別の推論規則を評価する）は、BRM の読者が持ち帰れる強い成果です。ただ、「自分の機械で検証し直せる」（RE4・§11(d)）は、名指しする 39 試行の点検がロガーを見ていないので、そのままでは読者を誤らせます（M2）。 |
| d 簡潔さと構成 | 3 | 語数は 4,374 から 6,984 に増えました。20 秒の打ち切りは Scope・§4・§5.4・§11(b)・§12・AG5・RE2 の 7 か所に出てきます。限定の文が重なり、主張の芯が読みにくくなっています。RF1 には表が無く、本文の散文に埋もれるおそれがあります（m3）。 |
| e 規程への適合 | 4 | Declarations・Open Practices Statement・要旨 250 語・データの引用・TOP Level 2 は押さえています。ただし投稿時の確認事項の言い換えから "effect size" が落ちています（n1）。 |
| f 先行研究の位置づけ | 3 | 計時の道具の検証の系譜を §2 に入れたことは評価します。ただし、基準をソフトウェアの層に置く理由が、§2 で並べる別のロガー（screen recording で検証したもの）と食い違います（M3）。KT1 を打鍵の時刻の検証の先行研究（物理の経路を端から端まで測ったもの）とどう組み合わせて読むかも書かれていません（m8）。 |

## 2b. 引き継ぎの判定

| round 1 の指摘 | 判定 | 根拠（外枠の位置と逐語） |
|---|---|---|
| major: 系譜に位置づけていない・ソフトウェアを基準に選んだ理由が無い | 一部 | §2 の 151〜155 行 "Validation of timing instruments in behavioural research, which compares software timing with an external device and warns that idealised scripts give a best case." は在ります。しかし理由の文 "an external device would time the path of the keys, not the conversion" が、§2 の 137〜138 行と §3 の 186 行と食い違います（M3 に載せました）。 |
| major: 基準の妥当性が主結果のおまけ・AG2 を Error と呼ぶ・qualify | 解消 | 266〜269 行 "First what the reference establishes (RF1), then questions 1 and 2"、380 行 "Difference of `dwell_ms` from the reference session's duration"、46〜48 行 "used to read them, never to exclude trials or to adjust values"。RF1 の表と出どころについては残りがあります（m2・m3）。 |
| major: 合成入力の代表性 | 一部 | 本文側は直っています。42〜44 行 "the fraction of trials excluded for this reason is reported next to every primary estimate"、§12 の 323〜326 行 "for each, the measures it may affect and the expected direction"。しかし要旨の規則（96〜102 行）は持ち越しの割合を要旨に入れておらず、G2 が警告する「最良の場合が一般の値として読まれる」入口が残っています（M1 に載せました）。 |
| major: キー行の時刻の主張が無い | 一部 | KT1 は 387 行に入りました。しかし、何と比べた遅れなのか（executor が記録した送出の時刻）、行と押下の対応のさせ方とその窓、要約の統計量が書かれていません（M4 に載せました）。 |
| major: OB3 と §3 の矛盾・観測可能性の分析に方法が無い | 解消 | 162〜168 行 "Method (stated first): the interfaces examined ... the documents read, with their URLs, the dates they were retrieved"。OB の行は "Not registered (documentation analysis)" です。文書でなく観察から来た文が残っています（m6）。 |
| major: LG2 の Windows の根拠・経路 | 一部 | 376 行の LG2b "which path drove the measured input method is not known, so the Windows estimates hold for an unknown mixture of the two paths" の「Reported in」は "Sections 4 and 12" です。しかし §12（318〜332 行）にこの文がありません（m5 に載せました）。 |
| major: §10.8 の版の確認が根拠の鎖に無い | 解消 | 226〜227 行 "the registered check of section 10.8 passed (39 of 39)"、AG9 の 385 行。data.windows.md の 42〜53 行に節があります。 |
| major: 研究者が検証し直す道筋が無い | 一部 | §11 の 313〜315 行 "(d) researchers can repeat the validation on their own machine and versions with the kit, of which the 39-trial check of the registration is the smallest unit"。この点検はロガーの一致を測っていません（M2 に載せました）。 |
| minor: AG1 の時刻と長さの混ざり | 解消 | 379 行 "A miss can come from timing or from a difference of construct length as well as from detection" |
| minor: 合算の Wilson は下限 | 解消 | 51〜53 行 "is a lower bound of the uncertainty" |
| minor: 要旨が 250 語に入らない | 一部 | 長さの規則（94〜102 行）は在ります。しかし事前登録 6.1 に反します（M1 に載せました）。 |
| minor: AG4 の基準は実行器・上限の性質 | 解消 | 382 行 "the reference for this measure is the executor, not the reference input field"、329〜330 行 "upper bounds whose excess this design does not exercise" |
| minor: LG1 の根拠が形の検査だけ | 解消 | 373〜374 行の LG1a と LG1b |
| minor: DS3・最も強い用途 | 解消 | 298〜301 行の (b1) と (b2)、399 行 "Not registered (description)" |
| minor: 番号を付けない試行 | 解消 | 256 行 "(deviation D6)"。D6 と data.windows.md の文言の違いは m7 に載せました。 |
| minor: 精度計画を §5 に | 一部 | 240〜243 行に精度の計画は在ります。しかし "the smallest with 30 and 31 trials" が macOS の S6 を落としています（m4 に載せました）。 |
| minor: 再構成の攻撃の偏りの向き | 解消 | 282〜283 行 "conditions that are expected to favour identification; this is stated as an expectation, not as a result" |
| nit: Study 1〜4 | 解消 | 見出しが "Results: …" になり、221 行に "All questions are answered from the same measurement runs" |
| nit: 速さの出典の限定 | 解消 | 238〜240 行 "follow published transcription typing of English sentences and span the range of typing speeds without estimating Japanese typing" |

## 3. 指摘の一覧（重い順）

### major

- [severity: major] **M1 要旨の規則が、凍結した事前登録 6.1 と外枠自身の Scope に反する。要旨の区間は小さな層の数で決まってしまう**
  - 位置と引用:
    - outline.md 96〜102 行（Rule for the abstract）: 「(i) recall and precision of detection in the primary comparison and scope, as the range from the lowest lower end to the highest upper end of the per-stratum Wilson intervals, with the fraction of trials that the primary scope sets aside」「The values over all trials and every other estimate ... are not quoted in the abstract.」
    - 同 53〜54 行（Scope）: 「An estimate in the primary scope is given together with the fraction of trials that the scope sets aside and the estimate over all trials.」
    - 同 43〜44 行: 「the fraction of trials excluded for this reason is reported next to every primary estimate」
  - なぜ問題か:
    1. 事前登録 6.1（623〜626 行）は "In the abstract and the conclusions, estimates are given as the ranges of their intervals ... An estimate in the primary scope is given together with the fraction of trials that the scope sets aside and the estimate under `all_trials`" と定めています。外枠の要旨の規則は `all_trials` の値と持ち越しの割合を要旨から外しており、deviations.md にこの逸脱はありません。外枠は冒頭（6〜8 行）で事前登録が優先すると書いているので、外枠の中でも矛盾しています。
    2. 層ごとの Wilson 区間の「最も低い下端」は、事前登録 3.3 の macOS の S6 slow（打ち切りの内側に 3 試行と 5 試行）で決まります。3/3 でも Wilson の下端は約 0.44、5/5 で約 0.57 です。検出が完全でも、要旨の recall の下端は 0.44 前後になります。つまり要旨の値はロガーではなく層の大きさを測ってしまいます。
    3. 持ち越しの除外と打ち切りの除外が要旨から消えると、較正した最良の場合の値が一般の値として読まれます。G2 の Bridges "should not be used in lieu of study-specific validation and testing" が警告する読み方です。
  - 解消の条件: 次のどちらかを選ぶ。
    - 要旨に `all_trials` の範囲と、範囲・持ち越しの 2 つの割合を入れ、250 語に収まることを試算で示す。
    - 要旨の扱いを逸脱 D7 として記録し、理由を書く。
    - どちらの場合も、要旨の範囲から除く層の規則（空の層、一定の数に満たない層）か、層の代わりに速さごとの範囲を使うことを、結果の前に固定する。
  - 自信: 高

- [severity: major] **M2 「自分の機械で検証し直せる」の最小の単位が、ロガーを検証していない**
  - 位置と引用:
    - outline.md 395 行 RE4: 「The validation can be repeated on a researcher's machine and versions with the kit; the 39-trial check of section 10.8 is its smallest unit.」
    - §11 の 313〜315 行（同じ趣旨）
  - なぜ問題か:
    1. data.windows.md の 50〜53 行のとおり、10.8 の点検は「The observation log was sealed before the reference side was read」であり、測ったのは計画と正解の一致（39 / 39）だけです。手順と基準の点検であって、ロガーの一致の点検ではありません。
    2. 事前登録 3.4（469〜471 行）は "`kit/analysis/pipeline.py` applies ... on real data, reason 1 to the plan of each run (the two SHA-256 of section 2.4 are constants of the code ...); it refuses to analyse a run that they catch" と定めています。研究者が短い計画で回した run は、登録した解析では分析できない作りです（コードは読んでいません。事前登録の記述から判断しました）。
    3. したがって、ロガーの一致を研究者の機械で測り直す実際の単位は、登録した計画の全体（1 セルあたり 12〜13 時間）です。
    4. RE4 の根拠の欄は "Basis: registered procedure (section 10.8)" ですが、10.8 は版が変わったときに測定を始めてよいかの前提条件で、研究者の再検証の手順ではありません。根拠も Windows の README だけで、主張は両方の系に向いています。
    5. G3（Plant "The only way to be sure of timing accuracy is to check it when paradigms are running in-situ, on the experimenter’s own equipment"）に照らすと、BRM の読者が最も持ち帰りたい主張です。最小の単位が実は手順の点検だけだと、読者に誤った安心を与えます（G1 "unwarranted confidence"）。
  - 解消の条件:
    - RE4 を 2 段に分けて書く。(i) 39 試行の点検で確かめられるのは、その機械と版で手順が変換を意図どおりに動かすこと（基準の側）だけ。(ii) ロガーの一致を測り直すには登録した計画の全体が要る。または、登録外の計画を探索として分析できる手段があるなら、その手段と、それが登録した解析でないことを書く。
    - 根拠に macOS の手順も含める。§11(d) も同じように直す。
  - 自信: 中〜高（パイプラインの拒否はコードではなく事前登録の文から判断）

- [severity: major] **M3 ソフトウェアの層に基準を置く理由が言い過ぎで、外枠自身の §2・§3 と食い違う**
  - 位置と引用:
    - outline.md 152〜154 行: 「This study places its reference at the software layer because the construct (a conversion session) exists only in the calls an application receives; an external device would time the path of the keys, not the conversion.」
    - 同 137〜138 行: 「a hybrid logger for non-alphabetic scripts that reconstructs the state of the text by reading it and was validated with human input against screen recordings」
    - 同 186 行: 「the two systems log different constructs (a visible window of the input method; ...)」
  - なぜ問題か:
    1. Windows のロガーが記録する構成概念は、外枠自身の言葉で「目に見える入力メソッドの窓」です。これは photodiode や高速度カメラのような外部の装置が直接測れる種類の事象で、BBTK の光センサーはまさにこれに使われてきました。macOS でも未確定の文字は画面に下線つきで表示されます。
    2. §2 で並べる先行のロガーは画面の記録に対して検証されています。「外部の装置は鍵の経路しか測れない」は事実として言い過ぎです。正確には「外部の装置はアプリが受け取る呼び出しそのものは見えない」です。
    3. G1（Plant "the software or script being run can know nothing of the errors introduced by the hardware, rendering engine, or plug-in"、ほかの分野では基準を代用で確かめることは受け入れられないという趣旨の "In no other field of science would this be viewed as acceptable"）の伝統の査読者は、この 1 文を真っ先に突きます。
  - 解消の条件:
    - 理由を「この研究の問いはアプリが受け取る呼び出しとの一致であり、それはどの外部の装置にも見えない」に狭める。
    - そのうえで、外部の装置で行えたが行わなかった検査を「失うもの」（§5.3・§12）に足す。例: Windows の候補窓の表示と消去の時刻を光センサーまたは画面の記録で測ること、macOS の未確定文字の表示。
    - 事前登録 7 にも同じ文があるので、外枠と本文では狭めた言い方を使い、登録の文との違いを注で示す。
  - 自信: 中〜高

- [severity: major] **M4 KT1 の「遅れ」が、何と比べ、どう対応させ、何で要約するかを定めていない**
  - 位置と引用: outline.md 387 行 KT1: 「Timing of the key rows on the software path, per system, descriptive: the delay of each row after its press and the error of each interval between consecutive rows, in the trials where every press arrived.」
  - なぜ問題か:
    1. **比較の相手が書かれていない。** 比べる相手は、executor が自分で記録した送出の時刻（事前登録 4.5 "Their times are the oracle's dispatch times"）です。押下を作るプログラム自身の記録が基準で、AG4 のように明示されていません。
    2. **対応のさせ方と窓が書かれていない。** 事前登録 3.4 は、行を押下に対応させるのに "each row takes the earliest press not yet taken that was sent from 300 ms before the row to 20 ms after it" という窓を使います。KT1 も同じ対応や "every press arrived" の判定に窓を使うなら、遅れは作りのうえで −20〜300 ms に収まり、窓の外の大きな遅れは「届かなかった」として KT1 の集合から黙って消えます。G1 が言う「記録は正常に見える」型の見逃しです。
    3. **要約の統計量が書かれていない。** "descriptive" だけで、一定の遅れ（lag）とばらつき（precision）を分けて何で報告するかが固定されていません（G5）。外枠は「報告の規則を結果の前に固定する」（3〜4 行）と言っているのに、ここだけ結果を見た後に選べる余地が残っています。
    4. **最初のブロックの遅れの扱いが無い。** パイロットでは run の最初のブロックで observation − executor が 95 ms と 86 ms でした（pilot-macos.md 124 行）。ブロックの位置に依存する遅れを 1 つの分布に混ぜると隠れます。
    5. **分解能が書かれていない。** 観察の行の時刻は整数のミリ秒の壁時計だけです（FORMATS.md 28 行の obs の `t`）。
  - 解消の条件: KT1 の行と §5.7 に次を書く。
    - 比較の相手（executor の送出の記録）。
    - 行と押下の対応の規則とその窓、窓が遅れの範囲に与える上限。
    - KT1 から外れた試行の数と割合。
    - 要約（遅れの中央値・平均、SD または百分位、最大）を結果の前に固定すること。
    - 最初のブロックとそれ以外を分けて示すこと。
    - 各記録の時刻の分解能。
  - 自信: 中（KT1 の対応の規則は delivery.py に在り、読んでいません。窓を共有するかは未確認です）

### minor

- [severity: minor] **m1 RF1 の「時計の差」は、送った押下と記録の時刻の差であり、KT1 の遅れと同じ量**
  - 位置と引用: outline.md 255 行「clock differences at the block markers」、378 行 RF1「the clock differences」
  - なぜ問題か:
    - pilot-macos.md 117〜120 行と pilot-windows.md 132〜134 行のとおり、この差はマーカーの押下（矢印キー）を executor・観察・基準が記録した時刻の差です。3 つのプロセスは同じ機械の壁時計を読むので、ここに入るのは時計のずれに、各経路の届くまでの遅れを足したものです。外部の時計が無いので、2 つは分けられません（G1）。
    - 「時計の差」と呼ぶと、遅れを時計のずれと読ませてしまいます。KT1 と RF1 が独立した 2 つの検査のように見える点も誤解を招きます。
  - 解消の条件: 本文では「同じマーカーの押下を 3 つの記録が登録した時刻の差（時計のずれと各経路の遅れの和で、分けられない）」と定義し、KT1 と同じ種類の量であることを書く。
  - 自信: 中〜高

- [severity: minor] **m2 RF1 と AG9 の値の出どころが、外枠の「結果の値はすべて結果ファイルから写す」の外にある**
  - 位置と引用:
    - outline.md 360〜365 行「The result files are those named in `experiment/notes.md`. ... Every result value in the manuscript is copied from these files by a script」
    - 378 行 RF1 の Evidence「the output of `kit/pilot/clock_sync.py` per run; `experiment/pilot-windows.md`」
  - なぜ問題か: notes.md の 8〜15 行の結果ファイルの表に clock_sync の出力はありません。pilot-windows.md は文書です。RF1 は round 1 で求めた主張なのに、写し方の規則が当たりません。
  - 解消の条件: clock_sync の出力を、凍結のタグから作る結果ファイルとして notes.md に足す。または外枠の規則に「文書から写す値」の例外を列挙し、どの値が手で写されるかを示す。
  - 自信: 高

- [severity: minor] **m3 RF1 に表も図も無い**
  - 位置と引用: outline.md 378 行 RF1 の Reported in「Section 6, before the primary estimates」。Tables and figures（401〜424 行）に RF1 の表が無い。
  - なぜ問題か: 計画と正解の不一致は、事前登録 6.3 で層ごと・種類ごとに Wilson 区間つきで報告されます。表が無いと、これが本文の散文に埋もれ、「基準の妥当性を主推定の前に示す」約束が形になりません。
  - 解消の条件: RF1 の表（種類ごとの不一致、届き方、焦点の喪失、マーカーの時刻差）を Table として足す。
  - 自信: 高

- [severity: minor] **m4 §5.4 の最小の層の数を誤って引いている**
  - 位置と引用: outline.md 242 行「the strata that remain under the cut-off (the smallest with 30 and 31 trials)」
  - なぜ問題か: 事前登録 3.3（324〜325 行）の 31 は "the smallest stratum under the cut-off other than those of S6 and S13" です。macOS の S6 slow は 3 試行と 5 試行、S6 mid は 27 試行と 30 試行です（349〜362 行の表）。この限定を落とすと、精度が実際より良く見えます。
  - 解消の条件: 「S6 と S13 を除いて最小 31（macOS）、S13 を除いて最小 30（Windows）。macOS の S6 slow は 3 と 5」と書く。
  - 自信: 高

- [severity: minor] **m5 LG2b の約束が §12 に無く、安全弁の根拠が名指ししたファイルの外にある**
  - 位置と引用:
    - outline.md 376 行 LG2b「including the cut-off and the safety valve ... | Sections 4 and 12」
    - §12（318〜332 行）に経路の混合の文が無い
  - なぜ問題か:
    - 名指しした `ime_cloak.rs` の 148 行は「★ `lib.rs` の IME Monitor にも safety valve がある」と書いており、25 秒の安全弁の実装は名指しした根拠の外にあります。
    - 名指しした単体テストの名前に、安全弁を試すものは見当たりません。20 秒の打ち切りは `session_self_heals_after_max_duration` が試しています。
  - 解消の条件: §12 に「Windows の推定は 2 つの経路の割合の分からない混合に対するもの」を足す。安全弁の根拠に、それを実装するファイルとテストを名指しするか、「安全弁は単体テストで試していない」と書く。
  - 自信: 中

- [severity: minor] **m6 §3 の方法は文書の分析だが、観察から来た文が混ざっている**
  - 位置と引用:
    - outline.md 176〜177 行「Some systems cloak the candidate window instead of hiding it, which the cloak notifications report.」
    - 182〜183 行「The list of windows shows a candidate window, but only by polling and only after a conversion has begun」
  - なぜ問題か: 「一部のシステムは隠蔽する」「変換が始まった後だけ」は、文書の記述というより挙動の観察に見えます。方法の基準（文書を読んで判定する）に当たらない文は、出どころ（どの系・版で、どう観察したか）を書かないと OB 行の "documentation analysis" と合いません。
  - 解消の条件: 該当の文に、文書の出典を付けるか、「観察（系と版、方法）」と標識して Table 2 の出典の列に書く。
  - 自信: 中

- [severity: minor] **m7 測定中の機械の負荷が報告の項目に無く、D6 の 2 つの記録の文言が違う**
  - 位置と引用:
    - outline.md 224〜227 行 §5.2（版だけで、他に動いていたプロセスの項目が無い）
    - deviations.md 127 行「the shell that ran it was ended by another program on the machine under low memory」
    - data.windows.md 35 行「the shell that ran it was ended by the coding assistant's session under low memory」
  - なぜ問題か: 測定用の機械（8 GB）で、試行 1 が別のプログラムによりメモリ不足の中で止められています。G6（Pinet "a mixed result of the load of ongoing programs running in the OS"）のとおり、KT1 と RT1 は他の負荷に左右されます。完走した試行 2 の間に何が動いていたかが外枠の報告項目に無く、AG9 の根拠の 2 文書が同じ出来事を違う言葉で書いています。
  - 解消の条件: §5.2 に各 run の間の機械の状態（他に動いていたプログラム、メモリの状況）を報告する項目を足す。D6 と data.windows.md の文言を 1 つに揃える。
  - 自信: 高（文言の違い）、中（負荷の影響）

- [severity: minor] **m8 KT1 を打鍵の時刻の検証の先行研究に位置づけていない**
  - 位置と引用: outline.md 151〜155 行（§2 の計時の段は一般論だけ）、387 行 KT1「No claim is made about the path from a physical keyboard.」
  - なぜ問題か: 先行研究は物理の経路を含む端から端までの誤差を測っています（G5 Pinet の USB の 8 ms の量子化）。KT1 はその残り（ソフトウェアの経路）だけです。読者が 2 つを足して読むための接続（KT1 は端から端までの誤差の一部であり、物理の経路の分は先行研究の値を参照する）が無いと、持ち帰れません。
  - 解消の条件: §2 か §6 に、KT1 が先行研究の測った経路のどの部分を補うかを 1〜2 文で書く。
  - 自信: 中

### nit

- [severity: nit] **n1 投稿時の確認事項の言い換えから "effect size" が落ちている**
  - 位置と引用: outline.md 31〜32 行「the manuscript includes appropriate measures of variability and, when relevant, of statistical power」
  - なぜ問題か: 規程の原文は "appropriate measures of variability, effect size, and (when relevant) statistical power" です。
  - 解消の条件: "effect size" を戻し、一致の推定そのもの（バイアス、一致の限界、kappa、ICC）がそれに当たると書く。
  - 自信: 高

- [severity: nit] **n2 「検査は除外に使わない」が、登録した `clock_jump` の除外と停止規則による run の打ち切りと衝突して読める**
  - 位置と引用: outline.md 46〜48 行「never to exclude trials or to adjust values」
  - なぜ問題か: 事前登録 6.2 の `clock_jump` は時計の検査で試行を除外します。3.4 の焦点の喪失の規則は run 全体を打ち切ります。§12 の "The stopping rule has stated blind spots" は、10.11 の "Selection by the stopping rule" を含んでいません。
  - 解消の条件: Scope に、これらが除外の規則（§5.8）と停止規則であって、ここで言う読むための検査とは別だと 1 文で書く。
  - 自信: 中

- [severity: nit] **n3 同じ限定が繰り返されている**
  - 位置と引用: 20 秒の打ち切りが Scope・§4・§5.4・§11(b)・§12・AG5・RE2 に重複している。
  - なぜ問題か: 語数が増え、主張の芯が埋もれます。
  - 解消の条件: 定義は §4 と表 3 に 1 回だけ書き、他の場所はそこを参照する。
  - 自信: 中

## 4. 総合の推奨（3 行）

**major**

1. 引き継ぎの 19 件のうち 12 件は解消しました。RF1 を主推定より前に置いたこと、理想化の列挙、題に "synthetic-input validation" を入れたことで、骨格は G1・G2 の伝統に近づきました。
2. ただし、要旨の規則が凍結した事前登録 6.1 に反し（M1）、再検証の最小の単位はロガーを測っていません（M2）。これは事前登録への忠実さと、読者が持ち帰る中心の主張に当たります。
3. 外部の基準を使わない理由の言い過ぎ（M3）と KT1 の定義の欠け（M4）は、この立場の査読者が最初に突く箇所です。4 件とも文言と定義の直しで消せますが、直した形を再査読で確かめたいです。

## 5. 読めなかった範囲と注入の疑い

**読んでいないもの**

- 一覧に在るが読んでいないファイル:
  - `papers/ime-observation/README.md`
  - `experiment/data.md`
  - `kit/logger/src/input/ime_compose.rs`、`kit/logger/src/driver_windows/cloak.rs`、`kit/logger/src/driver_windows/candidate.rs`（名前の grep だけ）
- 部分的にしか読んでいないもの:
  - `preregistration.md` のうち 1〜3.2 節・6.6 の後半〜6.8 節・10.1 節。読んだのは 3.3、3.4、4、5、6.1〜6.6 の前半、6.9〜9、10.2〜10.11 です。
  - `FORMATS.md` は 60 行目より後を読んでいません。
  - `ime_winevent.rs` は冒頭の 60 行とテストの名前だけです。
  - Bridges 2020 は grep の抜き出しだけで、全文は読んでいません。
- 外枠が名指しする `pipeline.py`・`delivery.py`・`clock_sync.py`・`run.sh` は一覧の外なので読んでいません。M2 と M4 のコードの挙動は、事前登録の文から判断しました。
- 開示: `#[test]` の数を数えた grep（count）の結果に、一覧の外のファイル名（`main.rs`・`driver_windows.rs`・`keyboard.rs`・`driver_macos/tests.rs`・`ime_mode.rs`・`analysis/key_gate.rs`）と各ファイルの本数が出ました。中身は読んでおらず、指摘の根拠にも使っていません。

**注入の疑い**

なし。接地の 3 本・外枠・資料に、査読者や LLM に向けた指示は見当たりませんでした。`ime_cloak.rs` の日本語のコメントは開発者向けのメモで、査読者への指示ではありません。データとして扱いました。

**関係するファイル**

- C:\GSE-prototype\papers\ime-observation\manuscript\outline.md
- C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md
- C:\GSE-prototype\papers\ime-observation\experiment\deviations.md
- C:\GSE-prototype\papers\ime-observation\experiment\data.windows.md
- C:\GSE-prototype\papers\ime-observation\experiment\notes.md
- C:\GSE-prototype\papers\ime-observation\experiment\pilot-macos.md
- C:\GSE-prototype\papers\ime-observation\experiment\pilot-windows.md
- C:\GSE-prototype\papers\ime-observation\kit\logger\src\input\ime_cloak.rs
