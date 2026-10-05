# 査読: BRM で、外部の基準で計時の道具を検証してきた方法論の立場（下位人格: 懐疑家）／stage outline／round 1

対象: `C:\GSE-prototype\papers\ime-observation\manuscript\outline.md`（commit `6f0af22b`）。
読んだもの: context-A.md の一覧にある 11 ファイル（全部を全文で）と、接地の 3 本。

---

## 1. 接地（この立場が論文に求める基準）

引用は原文のままです。PDF 抽出で崩れた改行・語の分割・空白だけを戻しました。

- **G1 基準は測定と独立でなければならない**（Plant, 2016）
  - 「The common thread being that the software or script being run can know nothing of the errors introduced by the hardware, rendering engine, or plug-in. It, just like the experimenter, will blindly act on and report the timings given without question.」
  - 「The sobering fact of the matter is that without using external chronometry there would be little chance of noting that stimuli had been presented for double the amount of time!」
- **G2 自分の環境でその場で自己検証し、区間を書く。一般化はしない**（Plant, 2016）
  - 「In closing I would propose that researchers self-validate their own timing accuracy using external chronometry (e.g., using a Black Box ToolKit or oscilloscope) and state confidence intervals on publication. The only way to be sure of timing accuracy is to check it when paradigms are running in-situ, on the experimenter's own equipment, at the time a given study is carried out. Generalization across apparently similar hardware types or categories of study is folly.」
- **G3 理想化した入力の検証は代表性を欠く**（Plant, 2016）
  - 「I firmly believe benchmarking various experiment generators using idealized equipment and simplified scripts is counterproductive, lulls researchers into a false sense of security, and is unrepresentative of what they do and may achieve in the field.」
  - Bridges et al. (2020) も同じ趣旨で書いている: 「It is very important to note that the timings measured here represent something approaching a best-case scenario.」
- **G4 一定誤差と変動誤差を分けて報告する**（Bridges et al., 2020）
  - 「Precision refers to the trial-to-trial variability of the measures: the jitter of the timing measurement or its "variable error".」
  - 「Accuracy refers to the "constant error" of a measurement which, in timing terms, is often referred to as the "lag", "offset" or "bias" from the true value.」
- **G5 独立に測れば問題が見つかる**（Bridges et al., 2020）
  - 「The chief of these reasons is simply that we independently tested the timing with photodiodes and microphones and, in so doing, we found timing problems that could be addressed first.」
- **G6 生成する入力は実際の課題に似せる。OS の中間層を疑う。打鍵間隔と量子化を明示する**（Pinet et al., 2017）
  - 「A limitation of this approach is that their manipulation involved fixed intervals and a single button. A crucial and original feature of the present study is the use of three distinct keys from the keyboard, and the generation of variable delays between keys, just as it happens in actual experiments involving sequence production.」
  - 「The impact of this intermediate layer of software on keyboard chronometry is not known.」
  - 「Such noncontinuous sampling of the data should be acknowledged」
  - 二段の戦略（機械による検証と、人のデータの品質確認）: 「First, we measured the timing accuracy of the jsPsych interface using a specialized hardware (Black Box Toolkit) … Second, we ran an actual experiment online and performed a complete quality check of the data」

---

## 2. 評価表

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | 23 行のうち多くは、事前登録の節と結果ファイルにきれいに対応している。ただし次の行は根拠が主張に当たらない。<br>・OB3: §3 の本文と矛盾している。<br>・LG2: Windows の部分の根拠（`spec_predict` の自己テスト）は macOS しか扱わない。<br>・LG1: 根拠が「形」の検査だけ。<br>・AG9: Windows の 10.8 の版の確認が根拠に無い。<br>・AG2: 「Error」と呼んでいる。<br>・Intro が掲げる pauses を支える行（キー行の時刻）が 1 行も無い。 |
| b 方法の穴 | 3 | 盲検化・予測による分解・中止の規則は丁寧で、この立場から見ても良い設計。<br>一方で、基準は同じ機械のソフトウェア（G1）。手順は pilot で入力方式が意図どおり動くよう調整されており（G3）、入力は注入の経路だけを通る（G6）。観測可能性の分析には方法（何を・どの版で・いつ調べたか）が無い。 |
| c 持ち帰れるもの | 3 | kit・データセット・観測可能性の表は持ち帰れる。<br>欠けているもの: 研究者が自分の機械と版でその場で検証し直す道筋（G2）。キー行の時刻を使ってよいかの答え。macOS では保存した oracle と gt だけで別の推定規則を評価できる、という最も強い用途も書かれていない。 |
| d 簡潔さと構成 | 3 | 節と表の対応は明快。<br>ただし、基準の妥当性（AG7・AG8）が補遺に回されている。要旨の規則（区間の幅 ＋ 外した割合 ＋ all_trials）を 3 つの cell に当てると 250 語に入らない。同じ実行の解析を「Study 1〜4」と呼んでいる。 |
| e 規程への適合 | 4 | Declarations・Open Practices Statement・要旨の上限・DOI・データ利用の文は、原文の規程どおりに置かれている。<br>規程の「appropriate measures of variability, effect size, and (when relevant) statistical power」に対応する精度計画（事前登録 §3.3）を §5 で示す予定が書かれていない。 |
| f 先行研究の位置づけ | 2 | §2 が扱うのは、執筆の logger・日本語と中国語の執筆研究・テキストを含まないデータセット・タイミング攻撃・一致の方法だけ。<br>BRM が積み上げてきた「計時と打鍵の測定を外部の基準で検証する」系譜（G1〜G6）が無い。なぜ外部の時計ではなくソフトウェアの基準を選んだのかも、外枠には書かれていない。 |

---

## 3. 指摘の一覧（重い順）

- [severity: major] 外部の基準で計時を検証してきた系譜に位置づけていない。ソフトウェアを基準に選んだ理由が外枠に無い
  - 位置と引用:
    - outline.md §2（94〜108 行）: 「Agreement methods used in this paper (limits of agreement, kappa, intraclass correlation, cluster bootstrap).」で終わり、計時の検証の文献が無い。
    - §12（226 行）: 「the reference is software on the same machine」（限界として一語で触れるだけ）。
  - なぜ問題か: BRM で「logger の検証」を名乗れば、読者はまず外部の計時（BBTK・ロボットの打鍵・光センサー）と比べる。G1 は「software … can know nothing of the errors」、G5 は「independently tested … found timing problems」と書く。
    事前登録 §7（974〜978 行）には、それに答える議論がある: 「an external timing device would time the path of the keys, not the conversion」。しかし外枠はこの議論を §2 にも §5.3 にも運んでいない。
  - 解消の条件:
    - §2 に段を 1 つ足す。Plant (2016)・Pinet et al. (2017)・Bridges et al. (2020) などの系譜を挙げ、それらが打鍵の経路の時刻を測る一方で、本研究の構成概念（変換セッション）は API の層にしか無いことを書く。
    - §5.3 で、基準をソフトウェアの層に置く理由と、それで失うもの（物理キーの経路・外部の時計）を述べる。
  - 自信: 高

- [severity: major] 基準（参照入力欄）の妥当性が主結果の「おまけ」になっている。AG2 は「誤差」と名乗っている
  - 位置と引用:
    - 32〜33 行: 「Every other result is reported next to it and is not used to qualify it.」
    - AG8（274 行）の掲載先: 「Section 5.7; supplement」
    - AG2（268 行）: 「Error of `dwell_ms` (median absolute error; Bland-Altman bias and limits of agreement).」
  - なぜ問題か: 一致の主推定が意味を持つのは、基準そのものが妥当なときだけ（G1・G5）。その証拠（計画と GT の一致、基準への届き方、時計）を「qualify しない」と書いて補遺に回すと、読者は検証されていない基準との一致を真値への誤差と読む。
    事前登録は自分で次のように書いている。
    - 10.11（1433〜1435 行）: 「they were not checked against an external clock」
    - 10.3: 「the agreement measures both the observer's errors and the difference of the constructs」
    - pilot-windows.md（113〜115 行）: 「the same input method thus commits at different points in two kinds of field」。基準が欄の種類に依存することを示す直接の証拠だが、外枠のどの行にも入っていない。
  - 解消の条件:
    - 主張の行を 1 つ足す（例: 「参照入力欄は構成概念の基準として何を満たし、何を満たさないか」）。根拠は AG7・AG8 と、pilot の IMM と TSF の比較。これを §6 の主推定より前に置く。
    - 32〜33 行の「qualify」を「adjust」に直す。
    - AG2 と Table 6 の「Error」を「difference from the reference's duration」に改め、§5.3 に一文を足す: 同じ時計を共有する 2 つのソフトウェアの記録の一致であって、外部の標準に対する正確さではない。
  - 自信: 高

- [severity: major] 合成入力の代表性。手順を「入力方式が意図どおり動く」ように調整したことが、限界にも適用範囲にも書かれていない
  - 位置と引用:
    - §5.5（169〜170 行）: 「what the pilots fixed (procedures, ground-truth rules, the stopping-rule settings, the choice of the Windows reference field)」
    - §12（226 行）: 「Synthetic input;」
  - なぜ問題か: pilot は、素朴な手順では入力中の文字列が次の試行へ持ち越されることを示している。
    - macOS: 「An uncommitted composition otherwise runs on into the next trial」（pilot-macos.md 53〜54 行）
    - Windows: 凍結時の手順で TSF は 93/117（pilot-windows.md 99 行）
    手順はそれが起きない形（Return を 2 回、Escape を 3 回、数字のあとに Return）に変えられ、持ち越しは除外の規則で除かれる。人の執筆で logger が壊れやすいのはまさにこの持ち越しの場面だ。
    ほかにも次の理想化がある。
    - 押下が重ならない（事前登録 3.3 の 395〜397 行）
    - 間隔がキーと独立
    - 誤打が無い
    - 注入の経路だけを通る。Windows では手打ちと比べていない（10.11 の 1442〜1443 行「the response of the input method to the presses was not compared with hand-typed presses」）
    G3 の「idealized … simplified scripts … unrepresentative」と、G6 の「just as it happens in actual experiments」が問うのはこの点。
  - 解消の条件:
    - Scope に一文を足す: 手順は各変換が試行の中で終わるよう較正されたこと。
    - §12 の「Synthetic input」を、測度ごとに分けた理想化の列挙に置き換え、それぞれが結果をどちらへ偏らせる見込みかを書く。
    - 要旨と結論で、外した割合と並べて carry_over による除外の割合も示す。
    - §11 の推奨を、この理想化の範囲の中に限る。
  - 自信: 高

- [severity: major] キー行の時刻を検証した主張が無い。それでも Intro は pauses を掲げている
  - 位置と引用:
    - 82〜83 行: 「the measures it supports (pauses, revisions, production rates)」
    - §4（135 行）: 「one key row per press and release with one of fourteen categories and a time」
    - 時刻に触れるのは AG8（274 行）だけで、それも「Delivery of the presses …」（掲載先は supplement）。
  - なぜ問題か: 打鍵の研究者がこの log から計算するのは打鍵間隔と休止である。ところが外枠には、行の遅れ（一定誤差）・ばらつき（変動誤差）・間隔の誤差・量子化を結果として述べる行が無い。
    事前登録 6.3（684〜694 行）はこれらを算出するが、区間を付けずに道具の点検として扱い、「no claim is made about the path from a physical keyboard」と書く。読者には「key rows are validated」と映る恐れがある。
    G4 は一定誤差と変動誤差を分けよと言い、G6 は打鍵間隔の正確さとその量子化を明示せよと言う。
  - 解消の条件: 次のどちらか。
    - (i) 行 KT1 を足す。内容は、ソフトウェアの経路での行の遅れの中央値と散らばり、連続する行の間隔の誤差、時刻の分解能。系ごとに記述的に示す。物理キーボードの経路には主張しないことを明記し、補遺でなく §6 に置く。
    - (ii) Scope と §11 に、キー行の時刻は休止・打鍵間隔の研究に向けては検証されていないと明記する。
  - 自信: 高

- [severity: major] OB3 と §3 が矛盾している。観測可能性の分析に方法が無い
  - 位置と引用:
    - §3（125〜126 行）: 「the list of windows can show a candidate window only by polling and not before a conversion; … A logger that records no text can therefore only infer sessions from key presses.」
    - OB3（263 行）: 「On macOS no documented interface reports the marked text or composition state of another application」
  - なぜ問題か: 窓の一覧は、ポーリングで候補窓の表示（変換状態の一部）を報告する。だから「composition state」を報告する文書化された経路が「無い」とは言えず、「only infer」も強すぎる。
    「文書化された経路は無い」という否定の存在主張を支えるには、調べた範囲（文書の集合・OS の版・調べた日・数え方）が要る。ところがその数は「Open items」（310〜311 行）でまだ決まっていない。
    さらに「Registered definition」の欄は事前登録 §1.1 と §10.3 を挙げるが、そこは観測器の記述で、登録された分析ではない。
  - 解消の条件:
    - OB3 を「marked text を報告する経路は無い。窓の一覧は変換が始まった後にポーリングで候補窓だけを示す。logger はそれを使わない（理由を書く）」に直す。
    - §3 の冒頭に、文書を調べる方法（対象の範囲・版・日付・採否の基準）を置く。
    - 登録の欄は「not registered (documentation analysis)」と書く。
  - 自信: 高（矛盾について）、中（方法の欠落が査読で問われる重さについて）

- [severity: major] LG2 の Windows の部分は根拠が当たらない。どの経路が働いたかも分からない
  - 位置と引用: LG2（266 行）「The macOS session rules and the Windows session paths are those stated … | Logger source in `kit/logger/`; the self-test of `kit/analysis/spec_predict.py` against that source」
  - なぜ問題か: 事前登録 10.7（1271〜1272 行）は「no prediction applies to the Windows observer」と書く。自己テストは macOS の規則しか照合しない。
    また 10.3（1173〜1175 行）は「Which path drives the Microsoft input method on the measuring machine was not determined」と書く。Windows の一致の推定は、経路の割合が分からない混合に対するものになる。別の build で他方の経路が働けば、結果は移らない（G2 の「Generalization … is folly」）。
  - 解消の条件:
    - LG2 を macOS（ソース ＋ 自己テスト）と Windows（ソースだけ・試験なし）に分ける。
    - §4 と §12 に書く: 経路は行に記録されず、20〜25 秒の行と 25 秒以上の行が唯一の手がかりであること。結果は経路の割合が分からない混合に対するものであること。
  - 自信: 高

- [severity: major] Windows の前提条件（10.8 の版の確認）の結果が、根拠の鎖に入っていない
  - 位置と引用:
    - AG9（275 行）の根拠: 「`experiment/data.md`, `experiment/data.windows.md` (run checks); …」
    - deviations.md D5（107〜108 行）: 「the check of section 10.8 (the input method's version differs from the pilot's)」
  - なぜ問題か: 事前登録 10.8（1367〜1371 行）は、版が違えば 39 試行の確認計画を先に回し、「the Windows cell is measured only if every trial produces the session its plan intends (39 of 39)」と定める。
    D5 は版が違ったことを示すが、その確認の結果は data.windows.md の表に無い。一覧の中のどのファイルにも見当たらない（一覧の外にあるかは読んでいない）。
    確認の結果が根拠に無ければ、Windows の主張は前提条件の記録を欠く。
  - 解消の条件:
    - 10.8 の確認の結果（試行数・一致の数・計測時の IME の版）を、AG9 の根拠と §5.2 の「versions and settings recorded per run」に入れる。
    - 版が pilot と違うことを §5.2 と §12 に書く。
  - 自信: 中

- [severity: major] 研究者が自分の環境で検証し直す道筋が、持ち帰れるものに入っていない
  - 位置と引用:
    - §11（219〜222 行）: 「Per system, which measures the results support and which comparisons they do not …」
    - §10 の用途（212〜215 行）
  - なぜ問題か: この系譜の中心の要求は G2 の「self-validate … in-situ, on the experimenter's own equipment」である。事前登録 10.11（1419〜1421 行）は「The agreement measured here therefore cannot be carried to an application whose field does not record a reference, and no procedure of this kit measures it there.」と書く。
    だから、読者が自分の機械と版で参照入力欄に対して検証し直せること（10.8 の 39 試行の確認計画が最小の単位になる）と、自分のアプリでは一致を測れないことを、§11 で明示しなければ読者は持ち帰れない。
  - 解消の条件: §11 に次の 2 つを足す。
    - 「kit で同じ検証を自分の機械と版で回す手順（最小の確認計画、それが覆う範囲と覆わない範囲）」
    - 「自分のアプリでの一致はこの kit では測れない」
  - 自信: 中

- [severity: minor] AG1 の「detection」には、時刻のずれと構成概念の長さの違いが混ざる
  - 位置と引用: AG1（267 行）「Recall, precision, split rate and merge rate of the session rows against the reference」
  - なぜ問題か: 対応づけは IoU が 0.5 以上であることを要し、ずれは補正しない。
    事前登録 6.9（939〜946 行）は、約 370 ms より短いセッションは時刻のずれだけで対にならないと書く。Windows では、窓の区間と composition の区間は長さが違う（10.3 の 1183〜1187 行）。
    取りこぼしの一部は、検出の失敗ではなく、時刻（G4 の一定誤差）や構成概念の長さの違いから来る。
  - 解消の条件:
    - AG1 と §6 に限定の文を足す。
    - 探索的（§6.12）でよいので、GT のセッションの長さ別の recall、または重なるが 0.5 に届かない対の数を示す。
  - 自信: 中

- [severity: minor] 合算した値の Wilson 区間は不確かさの下限だが、要旨の規則にその注記が無い
  - 位置と引用: 36〜38 行「In the abstract and the conclusions they are given as the ranges of their intervals … A pooled value is labelled as pooled」
  - なぜ問題か: 事前登録 6.1（613〜615 行）は、合算した割合の区間を「read as a lower bound of the uncertainty」と書く。3.3（339〜341 行）では、速度の水準ごとの設計効果が 25 に達しうる。要旨に区間の幅だけを出すと狭く見える。規程の「appropriate measures of variability」にも関わる。
  - 解消の条件: Scope に一文を足す（合算した割合の Wilson 区間はブロックを無視した下限である）。要旨で合算の区間を出すなら、そう明記する。
  - 自信: 高

- [severity: minor] 要旨の骨子は 250 語に入らない見込み
  - 位置と引用:
    - 76〜77 行: 「Results as interval ranges: recall and precision of detection, bias and limits of agreement of the duration, agreement of abandonment, per-text agreement, recoverability against chance, runtime cost under two conditions.」
    - 38〜39 行: 「given together with the fraction of trials that the scope sets aside and the estimate over all trials」
  - なぜ問題か: 3 つの cell それぞれで、測度ごとに区間 ＋ 外した割合 ＋ all_trials の値を出すと、数字だけで上限を超える。
  - 解消の条件: 要旨に出す推定を今決める（例: cell ごとの recall と precision、dwell の偏りだけ）。ほかは表を指すと書く。Scope の規則は、要旨に出す推定に限って当てると明記する。
  - 自信: 中〜高

- [severity: minor] AG4 の基準は executor であって、参照入力欄ではない。Windows のシステム全体で数える性質は、この設計では試されない
  - 位置と引用: AG4（270 行）「Agreement of `nav` with the arrow presses sent during the session.」
  - なぜ問題か:
    - 事前登録 6.6（778〜780 行）: 「this measure compares the observer with the executor, not with the reference input field」
    - 10.3（1169〜1171 行）: Windows の nav と abandon はシステム全体で数えた上限値である。計測では executor しか打鍵しないので、上限値であることの影響は表に出ない。
  - 解消の条件: AG4 に基準が executor であることを明記する。§12 に、Windows の nav と abandon が過大になる条件はこの設計では試されないと書く。
  - 自信: 高

- [severity: minor] LG1 の「no text」の根拠が、形の検査だけになっている
  - 位置と引用: LG1（265 行）の根拠「`kit/formats/FORMATS.md` (`obs/1`); `kit/formats/validate_logs.py`; the content-free check …」
  - なぜ問題か: FORMATS.md（216〜222 行）は自分で「The meaning of a value is not guaranteed: payload encoded into an integer field … cannot be detected」と書く。題名に入る主張が、意味を保証しないと自ら述べる検査に頼っている。
  - 解消の条件: 根拠に logger のソースと manifest の照合を足す。検査が保証するのは形だけだと LG1 に書く。
  - 自信: 高

- [severity: minor] DS3 の根拠は datasheet の自己申告で循環している。最も強い用途が書かれていない
  - 位置と引用:
    - DS3（283 行）の根拠: 「Datasheet released with the data」
    - 用途 (b)（213〜214 行）: 「evaluating another observer on the same plans with the same executor and reference input fields」
  - なぜ問題か: (b) のように executor と参照入力欄を使うなら、新たに計測し直すことになる（入力方式の学習は戻せない）。そうなると、保存したデータセットの用途とは言えない。
    一方 macOS では、キーから推定する別の規則を、保存した oracle と gt だけで評価できる。`gt_pred` がまさにその例だが、用途として書かれていない。
  - 解消の条件:
    - (b) を 2 つに分ける: 保存データだけで評価できる規則（macOS・キーから推定するもの）と、kit を回し直す必要がある観測器。
    - DS3 の根拠に、ファイルの中身（どの欄があるか）と `gt_pred` を実例として挙げる。
  - 自信: 中

- [severity: minor] 番号を付けない試行の扱いが逸脱として記録されていない
  - 位置と引用: data.windows.md 36 行「Not numbered (refused before the first trial) … by the researcher's decision this start, which sent no key, is not counted among the at most three attempts」
  - なぜ問題か: 事前登録 3.4（403〜404 行、462 行）は、runner が止めた実行も試行に数え、「No other reason and no explanation is admitted.」と定める。この判断は deviations.md（D1〜D5）に無い。
    結果への影響は小さい（3 回の上限には届いていない）。しかし外枠の Table 4 と AG9 は、逸脱の記録が完全であることを前提にしている。
  - 解消の条件: deviations.md に D6 として、日付・理由・影響を書く。Table 4 と AG9 の根拠に入れる。
  - 自信: 高

- [severity: minor] §5 に精度計画（試行数の根拠と設計効果）を示す予定が無い
  - 位置と引用: §5.4（167 行）「75 trials per scenario and speed」
  - なぜ問題か: 規程の確認項目「appropriate measures of variability, effect size, and (when relevant) statistical power」に当たる内容は、事前登録 3.3 に既にある（Wilson の半幅の表、設計効果、cut-off の後に残る層の大きさ）。しかし外枠はそれを本文へ運ぶ予定を書いていない。
  - 解消の条件: §5.4 か §5.8 に、精度計画と、cut-off の後に最も小さくなる層（31 試行と 30 試行）を書く。
  - 自信: 中

- [severity: minor] 合成入力で行う再構成の攻撃は、偏りの向きが書かれていない
  - 位置と引用: RC2（278 行）「The recommended granularity of the key rows …」
  - なぜ問題か: 攻撃者は同じ生成器と手順を知っている（事前登録 6.8 の 851〜854 行）。誤打も無い。攻撃者に有利な条件なので、「near chance」の判定は保守的になると読めるが、外枠はその向きを述べていない（G3: 理想化された条件の結果は、どちらへ偏るかを示さなければ読者を誤らせる）。
  - 解消の条件: §8 か §12 に、理想化が識別の正答率をどちらへ偏らせると見込むかを、理由とともに書く（断定はしない）。
  - 自信: 低

- [severity: nit] 同じ実行の解析を「Study 1〜4」と呼んでいる
  - 位置と引用: §6〜§9 の見出し（186・191・196・202 行）「### 6. Study 1: Detection and per-session agreement」
  - なぜ問題か: BRM の読者は、Study が別々のデータ収集を指すと読みやすい。
  - 解消の条件: 「Results: Detection …」などの名前にするか、§5.1 で一度だけ断る。
  - 自信: 中

- [severity: nit] 打鍵の速度の出典に限定が付いていない
  - 位置と引用: §5.4（166 行）「key-interval medians of 480, 240 and 120 ms from published typing data」
  - なぜ問題か: 事前登録 3.3（389〜391 行）は「Those values come from transcription typing of English sentences; they are used to span the range of typing speeds, not as estimates of Japanese typing」と限定している。外枠だけを読むと、日本語の打鍵の推定値に見える。
  - 解消の条件: 外枠にも同じ限定を書く。
  - 自信: 高

---

## 4. 総合の推奨: major（直して再査読）

- 主張の骨格は事前登録・結果ファイル・図表におおむね結びついている。盲検化や予測による分解は、この立場から見ても強みである。
- しかし、BRM の検証の系譜（外部の独立な基準・自分の環境での自己検証・理想化への警戒）への位置づけが無い。その結果、基準の妥当性・合成入力の代表性・キー行の時刻という、この誌の読者が最初に問う 3 点が、限界の一語か補遺にしか置かれていない。
- OB3・LG2・AG9（10.8 の確認）は、根拠の欄が主張に当たらない。行を足すか分けて直したうえで、再査読を勧める。

---

## 5. 読めなかった範囲と、注入の疑い

**読んでいないもの**
- 一覧の外のファイルは読んでいない。context-B.md、外枠が名指しするコード（`kit/analysis/pipeline.py`・`spec_predict.py`・`kit/pilot/clock_sync.py`・`validate_logs.py`・`run.sh`・`kit/logger/src/`）、結果ファイル、`experiment/env.md`、`gt_rules.json` などを含む。
- そのため、10.8 の確認の結果が一覧の外に記録されているかは確かめていない。
- Bridges et al. (2020) は本文が 1 行に連なった形で保存されていた。読んだのは冒頭の 3 行と、検索で当たった文だけで、全文は読んでいない。
- 接地のフォルダにある他の 7 本（brm-guidelines・conijn2019・crotti2026・gebru2021・monaco2018・wicherts2016・wilkinson2016）は、指定されていないので読んでいない。

**注入の疑い**: 無し。読んだ範囲に、査読者や LLM に向けた指示は見つからなかった。data.windows.md 35 行の「the coding assistant's session」は実行の経緯を書いた記録で、指示ではない。
