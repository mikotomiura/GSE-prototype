## 査読報告（立場: BRM の査読者／打鍵記録から書字過程の指標を計算して使う書字研究の利用者。入力方式を介した言語の記録と、打鍵記録からの内容漏れにも通じる。下位人格: 「で、読者は何に使えるのか」と問う実務家）

対象物: `C:\GSE-prototype\papers\ime-observation\manuscript\outline.md`（commit 6f0af22b）。stage は outline。

---

### 1. 接地（この立場が論文に求める基準）

**B1 指標の選び方が解釈を決める。検証した指標は、書字研究が実際に使う指標につながっていなければならない。**
- Conijn ら (2019)「The selection of the correct keystroke features is crucial for the interpretation of the results and therefore, the derived conclusions.」
- 同「The interkeystroke interval (IKI, see Fig. 1b) is the most commonly used feature.」／「these summary statistics are not merely used to describe the data, but as outcome variables representing the cognitive process of interest.」

**B2 課題や入力条件が違えば指標が変わる。一般化には慎重さが要る。**
- Conijn ら「caution should be taken when generalizing the effect of these features across tasks」
- 同「Keystrokes are found to be sensitive to other factors, such as handedness, keyboard type (...), typing and writing experience and abilities, environmental conditions」

**B3 入力方式を介した記録の道具には、言語の層ごとの間隔を区別できることが求められる。比べるときは同じ次元で比べる。**
- Crotti ら (2026)「A robust input logger for research should identify these types of IKIs」（(a)〜(e)。(d) 入力方式の確定の前、(e) 確定の後を含む）
- 同「We compared the input loggers across three dimensions: whether or not they are ecological (...), if they include support for non-alphabetic languages (...), and their ability to record fine-grained timestamps for keyup and keydown events」

**B4 時刻の精度は OS の時計の刻みで決まる。どれだけ細かく記録できるかを示す。**
- Monaco (2018)「from the perspective of an application running on the host, keystroke timings will generally align to some multiple of the scheduling clock tick.」／「64 Hz, or a 15.625 ms tick, is characteristic of the Windows family [30] and 100 Hz of Mac OS X [31].」

**B5 時刻が残る打鍵記録は、文字の内容に加えて、書き手が誰かも漏らす。**
- Monaco「For temporal side channels, we find that the information gained by different temporal features strongly correlates to typing speed and style.」
- 同「doing so may actually compromise anonymity, i.e., enable behavior-based identification, an issue not considered in this work.」
- 同「In general, real-world keylogging data is difficult to access and contains sensitive information」

**B6 （BRM の誌の方針。context-A の照合済みの逐語）**「BRM readers want practical solutions. There is little point in describing new materials that cannot be applied easily and correctly.」

---

### 2. 評価表

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | 対応表の 23 行は、事前登録の節と結果ファイルにほぼ正確に結びついている。AG1〜AG10 と RC1〜RC3 は事前登録の 6.4〜6.8 と 10.7 に照合できた。一方で次の穴がある。(1) 読者に一番効く §11（推奨）を支える主張の行が無い。(2) LG1「no text」の根拠が形の検査だけである。(3) 序論の「easier to share」は、検証の範囲（時刻の無い打鍵の行・1 句ずつ）を超えている。 |
| b 方法の穴 | 3 | 合成入力であることと、範囲を絞っていることは誠実に書かれている。足りないのは次の 3 点。macOS の盲検は「出力を伏せただけ」という但し書き。打鍵が重ならない（rollover が無い）という制限を名指しすること。試行の数え方（番号なしの開始・外から止められた試行）が deviations に無いこと。 |
| c 持ち帰れるもの | 2 | 検証する 4 つの集計は、事前登録で「were not selected from a review of the writing literature」とされている。書字研究の主要な指標（IKI・語の間の間・burst・修正・最大の間）との対応が外枠に無い。研究者が自分の記録から指標を出す手順（ツール）も無い。打鍵の行の間隔の誤差は、利用者に最も使える値なのに補遺に回っている。 |
| d 簡潔さと構成 | 3 | 1 回の測定の問い 1〜5 を「Study 1〜4」と呼んでいて、別々の研究に見える。§3 の OS の API の詳細は、心理学の読者には重い。要旨の骨子（3 つの cell × 6 種の結果を区間の幅で示す）は 250 語に収まらない見込みが高い。 |
| e 規程への適合 | 4 | APA 7・Declarations・Open Practices の位置・データの DOI・TOP Level 2 は押さえている。足りないのは 2 点。投稿時の確認 (d)「statistical power」に当たる精度の設計（事前登録 3.3）の置き場所が無い。APA は見出しに番号を振らない。 |
| f 先行研究の位置づけ | 2 | Inputlog を「not supporting non-alphabetic writing」とまとめているが、引いている Crotti らの本文はそうなっていない（後述）。Crotti らが使った比べ方の次元（ecological・keyup/keydown）でこの道具を比べていない。Hylog は人の入力で検証している（n=2・画面録画で照合）が、この点との相補を書いていない。 |

---

### 3. 指摘の一覧（重い順）

- [severity: major] 検証する指標が、書字研究で使う指標とつながっていない。研究者が自分の記録から指標を出す道筋も無い
  - 位置と引用: outline.md:82-83 §1「Keystroke logging as a method of writing research, and the measures it supports (pauses, revisions, production rates).」／ §7（:191-194）「four per-text measures per speed」／ preregistration.md:577-579 §4.6「The four measures are examples of aggregates a writing researcher might compute from such a log; they were not selected from a review of the writing literature.」
  - なぜ問題か: 序論は、間・修正・産出の速さを動機に挙げている。しかし検証されるのは、1 回の変換の要約（dwell_ms・nav・abandon）と、文献から選んでいない 4 つの集計だけである。dwell_ms の中身は 2 つの OS で違う。macOS では最初の文字から確定まで（読みを打つ時間を含む）。Windows では窓が見えている時間（予測の窓は読みを打つ間に開く）。どちらも、Crotti らの (d)「確定の前の間」のような選択の熟慮を切り出していない。書字研究の利用者は、どの既存の指標がこの記録から計算でき、そのうちどれがこの検証で裏づけられたかを知りたい。外枠からはそれが読めない。さらに、現場の研究者の手元にあるのは obs ログだけである（gt は無い）。そのログから指標を出す手順（スクリプトの名指し）と、運用の要件（OS の権限・対応する版・導入）を書く節も、外枠に無い。（Conijn ら「The selection of the correct keystroke features is crucial for the interpretation of the results and therefore, the derived conclusions.」／ Crotti ら「A robust input logger for research should identify these types of IKIs」／ BRM「BRM readers want practical solutions.」）
  - 解消の条件: (1) §4 か §11 に表を置く。表には、書字研究の代表的な指標（IKI 全体・語や句の境界の間・確定の前と後の間・修正の数・最大の間・総時間・変換の回数と時間）を行にとり、各 OS で「obs ログから計算できるか」「この検証で裏づけたか（どの主張 ID か）」「裏づけていない理由」を列に書く。(2) 序論の約束を、この表の範囲に合わせて書き直す。(3) obs ログだけから指標を出す利用者向けのスクリプトと、導入の要件を、§4 か補遺の節として外枠に置く。主張の行（例: LG3「the kit computes measures X from an obs log alone」）とその根拠も置く。
  - 自信: 高

- [severity: major] §11（推奨）に主張の行が無い。20 秒の打ち切りの推奨は、結果ではなく規則からしか言えない
  - 位置と引用: outline.md:217-222 §11「how the 20-second cut-off changes a researcher's aggregates, and the granularity of key rows that the recoverability study supports for publication. Each recommendation cites the result it rests on」／ 対応表で「Reported in」に Section 11 を挙げるのは OB4 と RC2 だけ
  - なぜ問題か: 「which measures the results support」と打ち切りの影響を述べる推奨には、対応表の行が無い。事前登録は、打ち切りの影響を結果からではなく規則から導いている（preregistration.md:714-716「The values under `all_trials` depend on this design's fraction of long trials (section 3.1), which follows from its think times, speeds and procedures and is not a property of natural typing. The effect of the cut-off on a researcher's aggregates follows from the rule stated in section 1.1.」）。だから「cites the result it rests on」という書き方では、大きさを結果から言えるように読めてしまう。Windows ではさらに、どちらの経路が行を書いたかが記録されない（:1169「Both paths can therefore act within one run, and a row does not record which path wrote it.」）。そのため研究者は、20 秒以上の変換が落ちたのか 25 秒で丸められたのかを、自分のログから判断できない。書字研究では、最大の間や間のばらつきが課題に最も敏感な指標になる（Conijn ら「features related to the variance in the general pauses, such as the largest IKI and SD IKI, showed large effect strengths.」）。長い熟慮が黙って消えることは、利用者にとって最も実務的な論点である。
  - 解消の条件: §11 の推奨 1 つにつき 1 行（例: RE1〜RE3）を対応表に足す。各行に、根拠となる主張 ID と、その根拠が「結果」か「規則（事前登録 1.1・6.4・10.3）」かを書く。打ち切りについては、向き（平均の変換時間と変換に使った時間の割合は下がる。回数と放棄率はどちらにも動く）だけを規則から述べ、大きさは述べないと明記する。Windows の行には、行の経路が分からないことの実務上の扱いを書く（例: 20〜25 秒の行と約 25 秒の行の読み方）。
  - 自信: 高

- [severity: major] 先行の道具との比べ方が、引いている文献の本文と合っていない
  - 位置と引用: outline.md:96-99 §2「loggers such as Inputlog and ScriptLog, which a recent comparison lists as not supporting non-alphabetic writing; Translog-II, which records input-method events in its own editor together with the text; and a hybrid logger for non-alphabetic scripts that reconstructs the state of the text by reading it.」／ :45-46「Its difference from earlier loggers is stated as a difference of design: which loggers handle input-method conversion」
  - なぜ問題か: (1) Crotti らの表 III で「No」なのは「Inputlog 9.5」である。同じ論文は、新しい版について「(versions to work with Korean and Chinese are currently being tested)」と書いている。結論でも「a challenge that has motivated both Hylog and the newer, language-specific Inputlog releases」「Together, Hylog and the new Inputlog versions represent meaningful advances in keylogging for non-alphabetic scripts」と述べている。「which loggers handle input-method conversion」で差を言うなら、版を名指しし、新しい言語別の版を数に入れなければ公平でない。(2) Crotti らは、ecological・非アルファベットへの対応・keyup/keydown の 3 つの次元で比べている。この道具は ecological の次元で弱い。検証は参照の入力欄だけで、事前登録 10.11 は「in applications that draw the candidates themselves the observer may see nothing. This was not tested.」と書いている。外枠はこの次元に触れていない。(3) Hylog は、人の入力 2 人分の確定の検出を、画面録画で数えて precision/recall で示している（「Precision98,4% 100%」「Recall99,6% 95,6%」「(as counted from the screen recording)」）。この論文の AG1 に当たる指標を人の入力で出している。合成入力だけのこの論文とは証拠の種類が相補的であり、それを書かないと比べ方が一方的になる。(4) Crotti らは日本語を将来の課題として名指ししている（「Japanese requires handling multiple scripts (hiragana, katakana, kanji) and input methods (romaji, kana input), necessitating additional pattern rules」）。この論文の動機を公平に支える文なのに、使われていない。
  - 解消の条件: §2 に比べ方の表を置く。Crotti らの 3 つの次元に「本文を記録しない」「確定の前と後の間を区別できる」「人の入力で検証したか」を足し、この道具・Inputlog（版ごと。日本語に対応するかは一次で確かめる）・Translog-II・Hylog を並べる。この道具が弱い欄（ecological は未検証・文字の層ごとの IKI は無い・人の入力での検証は無い）も、そのまま書く。Inputlog の書き方は、版を名指しした形に直す。
  - 自信: 高（Crotti らの本文で確かめた）

- [severity: major] 「共有しやすい」という動機が、評価の範囲を超えている。時刻から書き手が特定される経路も書かれていない
  - 位置と引用: outline.md:88-89 §1「A logger that records no text is easier to deploy and to share, if it can be shown what it records and what it leaks.」／ :221 §11「the granularity of key rows that the recoverability study supports for publication」
  - なぜ問題か: 漏れの評価が対象にするのは、時刻を持たない 2 つの粒度の打鍵の行・1 試行に 1 句・K 個の候補からの同定だけである。この道具の主な産物である変換の行は評価していない（preregistration.md:899-901「the session rows carry their times and durations in milliseconds, were not given to the attacks, and could undo the coarsening of the key rows, so publishing them is not evaluated.」）。書字研究で使う、時刻つきの打鍵の行も対象外である。判定の幅は、プライバシーの基準から導いたものではない（:1040-1041「The margin of the rule (2/K) and the values of K are design choices, not derived from a criterion of privacy.」）。そのため「supports for publication」は評価の語として強すぎる。もう一つ、時刻つきの記録は書き手の特定（打鍵の生体認証）を可能にする。これは本文の復元とは別の漏れであり、外枠のどこにも無い（Monaco「doing so may actually compromise anonymity, i.e., enable behavior-based identification」「the information gained by different temporal features strongly correlates to typing speed and style」）。ただし合成入力のデータ集自体には当たらない。
  - 解消の条件: 序論の「easier to share」を、評価した範囲（時刻の無い打鍵の行・1 句ずつ）に合わせて言い直す。§11 は「supports for publication」を、「is near chance under the registered rule, which is not a privacy criterion」のような事実の言い方に変える。§2 と §12 に 2 点を明記する。時刻つきの行と変換の行の公開は評価していないこと。時刻つきの記録は書き手の特定を可能にし、この研究はそれを評価しないこと。
  - 自信: 高

- [severity: minor] 打鍵の行の時刻の精度（間隔の誤差）が補遺に埋もれている。OS の時計の刻みにも触れていない
  - 位置と引用: outline.md:274 AG8「Delivery of the presses to the observation and the reference, and the clock differences at the block markers.」→「Section 5.7; supplement」／ preregistration.md:688-689「in the trials where every press arrived, the delay of each row after its press and the error of each interval between consecutive rows.」
  - なぜ問題か: 連続する行の間隔の誤差は、IKI を使う研究者にとって最も直接に使える値である（B1）。外枠はこれを器械の点検として補遺に回している。また、ホストで取る打鍵の時刻は OS の刻みに揃う（Monaco「keystroke timings will generally align to some multiple of the scheduling clock tick」「64 Hz, or a 15.625 ms tick, is characteristic of the Windows family」）。2 つの OS で行の時刻の分解能がどうなるかは、利用者の判断に直結する。さらに、ソフトウェアで注入した打鍵は物理キーボードの経路を通らないので、この誤差は下限である（Monaco「the physical delay cannot be measured since a keystroke is sensed only at the point of actuation」。事前登録 7 も同じ趣旨）。
  - 解消の条件: 間隔の誤差を、主張の行として本文の表に上げる（AG8 から分ける）。その行に、OS ごとの行の時刻の分解能（間隔の分布に刻みが見えるか）と、「software-injected events, so a lower bound」という但し書きを付ける。分解能を事前登録にない解析として出すなら、exploratory と明記する。
  - 自信: 中（分解能の記述を本文に入れるかは著者の判断）

- [severity: minor] 打鍵が重ならない（rollover が無い）という合成入力の性質を、限界の節で名指ししていない
  - 位置と引用: outline.md:226 §12「Synthetic input; ...」／ preregistration.md:395「The generator never overlaps two presses」
  - なぜ問題か: 人の打鍵では重なりがふつうに起きる（Monaco「some users having as high as 67% and 69% of all keystrokes overlapping for free and transcribed input」。Crotti らの表 XIII でも John の重なりは 26〜69%）。macOS の変換の規則は key-down の順で動くので、重なりは打鍵の行にも変換の推定にも効きうる。「synthetic」と一語で書くだけでは、読者は何が欠けているか判断できない（B2）。
  - 解消の条件: §12 に、合成入力で欠けている人の打鍵の性質を列挙する。少なくとも、打鍵の重なり・キーの組に依存する時刻の構造・語や句の境界での間・物理キーボードの経路。
  - 自信: 高

- [severity: minor] LG1「no text」の根拠が、形の検査だけである
  - 位置と引用: outline.md:265 LG1「The logger writes key categories and session summaries and no text ...」の根拠が「`kit/formats/FORMATS.md` (`obs/1`); `kit/formats/validate_logs.py`; the content-free check」／ FORMATS.md:219-222「**The meaning of a value is not guaranteed**: payload encoded into an integer field (`vk`, a length, a timestamp), a version string (...), or `manifest_sha256` cannot be detected this way. Keeping the log content-free is the producing side's design responsibility」
  - なぜ問題か: 題名の主張（without recording text）を支える行の根拠が、形を保証するだけの検査で終わっている。作る側の根拠（ソースが書き出すのは閉じた列挙と整数だけであること。kit/logger/README.md の「content-free by construction」）が根拠の列に無い。検査が何を保証しないかも、主張の文に入っていない。
  - 解消の条件: LG1 を 2 つに分ける。「形の検査を全ログが通る」（検査が根拠）と、「本文を書く経路がソースに無い」（ソースの該当箇所と自己テストが根拠）。整数の欄には原理的に情報を詰められ、検査はそれを検出しないことを、§4 の本文で一文書く。
  - 自信: 高

- [severity: minor] 序論の「key presses だけの記録には見えない」が、macOS の設計（打鍵から変換を推定する）と食い違う
  - 位置と引用: outline.md:85-86「The conversion is part of the writing process and is invisible to a logger that records only key presses or only the resulting text.」／ :126「A logger that records no text can therefore only infer sessions from key presses.」
  - なぜ問題か: macOS の変換の行は、打鍵の種類と入力モードから決まる、決定的な規則の出力である（事前登録 4.5 が送った打鍵から予測できるほど）。「invisible to a logger that records only key presses」と言い切ると、§3 と矛盾する。逆に読者にとっては、この規則（と gt_pred による規則そのものの検証）を、入力モードを記録した他の打鍵記録にも当てはめられるという点が、持ち帰れるものになりうる。
  - 解消の条件: 序論を「not directly recorded; it can be inferred from key presses only by rules whose validity must be shown」の形に直す。macOS の結果で、gt_pred（規則の妥当性）を、道具に依存しない持ち帰り（他の打鍵記録への規則の適用）として位置づけるかを決め、§11 に書く。
  - 自信: 中

- [severity: minor] §5.5 の「blinding」に macOS の但し書きが無い
  - 位置と引用: outline.md:169-170「the logger's session rows of the pilots sealed and never read.」／ preregistration.md:184-186「The key rows that were read are, on macOS, the very input from which the observer infers its sessions: the blinding withheld the observer's output, not its input.」
  - なぜ問題か: macOS では、読んだ打鍵の行から変換の行を計算できる。そのため「blinding」は事前登録より強く読まれる。
  - 解消の条件: §5.5 の要点に、事前登録 2.5 のこの文を入れる。
  - 自信: 高

- [severity: minor] 速さの設定の「published typing data」に但し書きが無い
  - 位置と引用: outline.md:165-166「three speeds with key-interval medians of 480, 240 and 120 ms from published typing data」／ preregistration.md:389-390「Those values come from transcription typing of English sentences; they are used to span the range of typing speeds, not as estimates of Japanese typing.」
  - なぜ問題か: 書き写し課題と作文では打鍵の特徴が違う（Conijn ら。B2）。日本語のローマ字入力とも違う。代表値のように読まれる恐れがある。
  - 解消の条件: §5.4 の要点に事前登録 3.3 のこの但し書きを入れる。あわせて、標本の大きさの理由（事前登録 3.3 の精度の表）を §5.4 か §5.8 に置く。これは BRM の投稿時の確認 (d) にも当たる。
  - 自信: 高

- [severity: minor] 試行の数え方の判断が deviations に無い
  - 位置と引用: data.windows.md:36「by the researcher's decision this start, which sent no key, is not counted among the at most three attempts」／ :35 attempt 1「the runner was stopped from outside ... Counts as aborted: Yes (incomplete)」／ preregistration.md:403-404「If a run is aborted (the runner stops it), the cell is run again from the start with the same plan, in a new run directory, up to three attempts.」／ :1047-1048「Any departure from this registration after the freeze is recorded in `experiment/deviations.md` ...」
  - なぜ問題か: 実行プログラムが拒んだ開始を試行に数えないこと、外から止められた実行の扱いは、どちらも事前登録 3.4 の閉じた規則に無い判断である。結果（3 回以内）は変わらないが、外枠の Table 4 と AG9 は deviations.md を根拠にしている。
  - 解消の条件: deviations.md に D6 として記録する（日付・理由・効果）。外枠の Table 4 と AG9 が、それを含むことを明記する。
  - 自信: 中

- [severity: minor] 構成: 「Study 1〜4」の呼び方と要旨の骨子
  - 位置と引用: outline.md:186-204「### 6. Study 1: ... ### 9. Study 4: Runtime cost」／ :76-77「Results as interval ranges: recall and precision of detection, bias and limits of agreement of the duration, agreement of abandonment, per-text agreement, recoverability against chance, runtime cost under two conditions.」
  - なぜ問題か: 同じ測定の問い 1〜5 を「Study」と呼ぶと、APA の読者は別々のデータ収集と受け取る。要旨は、3 つの cell × 6 種の結果を区間の幅で、しかも pooled の表示と除いた割合つきで（事前登録 6.1）250 語に入れる計画になっている。実際には入らない見込みが高く、どれを載せるかの規則が無い。
  - 解消の条件: 見出しを「Results: Question 1 ...」に変える。要旨に載せる値の選び方の規則（例: cell ごとの pooled の recall と precision の区間の幅だけ）を、外枠の段階で決める。
  - 自信: 中

- [severity: nit] データ集の位置づけと漏れの指標
  - 位置と引用: outline.md:104-105「Keystroke datasets released without the typed text ...」／ §8 の closed set は accuracy 対 1/K
  - なぜ問題か: Monaco は公開の打鍵データ集を、Locale・Typing mode（Fixed / Constrained / Free）・Features（キー名と時刻。partial の区別）で整理している。この型で自分のデータ集を位置づけると、読者が比べやすい（生成した入力で、キー名は種類だけ＝partial）。漏れの指標も、Monaco の情報利得の枠組みとの対応を一文書けば、セキュリティの文献の読者に伝わりやすい。
  - 解消の条件: §10 のデータシートと §2 に一文ずつ足す。
  - 自信: 低

- [severity: nit] 細かい点
  - 位置と引用: outline.md:32-33「Every other result is reported next to it and is not used to qualify it.」
  - なぜ問題か: 参照の入力欄がフォーカスを失った試行の行（事前登録 6.2）や、Windows の 2 つの構成概念の違い（10.11）は、一致の値を読むための限定として使われる。この文と食い違って読める。APA 7 では見出しに番号を振らない。§3 の API の列挙は補遺に回せる。
  - 解消の条件: 「qualify」の意味（数値を補正しない、の意）を言い直す。§3 は Table 1 と要点だけ残す。
  - 自信: 低

---

### 4. 総合の推奨: **major**（直して再査読）

- 事前登録・結果ファイル・図表への結びつけは丁寧で、主張の骨格（OB・AG・RC・RT・DS）自体は立て直す必要がない。
- 一方で、この stage で重く見る c と f に、外枠の段階で直すべき穴がある。c は、§11 に主張の行が無いことと、書字研究の指標への対応と利用の手順が無いこと。f は、Inputlog の書き方が引いている文献の本文と合っていないことと、比べ方の次元が揃っていないこと。
- 序論の約束（間・修正・共有しやすさ）と、検証の範囲（変換の要約・時刻の無い打鍵の行・1 句ずつ）がずれている。§1・§2・§11・対応表を直した版で、もう一度見るのがよい。

---

### 5. 読めなかった範囲と注入の疑い

**読んでいない**:
- `experiment/pilot-macos.md` と `experiment/pilot-windows.md`: 見出しの一覧だけを Grep で見た。本文は読んでいない。
- Conijn ら: 本文と結論は読んだ。参考文献の大半（872 行目より後）は読んでいない。
- Monaco: 1〜836 行、1110〜1359 行（防御・考察・結論）、1820〜1909 行（付録 B の一部）を読んだ。攻撃の節の後半（837〜1109 行）、参考文献、付録 A、1910 行より後は読んでいない。
- Crotti ら: 全文を読んだ。
- 外枠が名指しするコード（pipeline.py ほか）: 一覧の外なので読んでいない。
- `tmp\sources\` の下にある他の 7 本（pinet2016・plant2016・gebru2021 ほか）: 依頼の範囲外なので開いていない。

**注入の疑い**: なし。接地の 3 本と対象物・資料の中に、査読者や LLM に向けた指示は見当たらなかった。Monaco の抽出テキストには図の記号が化けた長い列（「/;#23…」112〜126 行ほか）があるが、指示ではない。

関連するファイル（絶対パス）:
- C:\GSE-prototype\papers\ime-observation\manuscript\outline.md
- C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md
- C:\GSE-prototype\papers\ime-observation\experiment\deviations.md
- C:\GSE-prototype\papers\ime-observation\experiment\data.windows.md
- C:\GSE-prototype\papers\ime-observation\kit\formats\FORMATS.md
- C:\GSE-prototype\.steering\20260927-ime-observation-paper-eval-design\attack-me\outline-ime-manuscript\round-1\tmp\sources\crotti2026.txt
- C:\GSE-prototype\.steering\20260927-ime-observation-paper-eval-design\attack-me\outline-ime-manuscript\round-1\tmp\sources\conijn2019.txt
- C:\GSE-prototype\.steering\20260927-ime-observation-paper-eval-design\attack-me\outline-ime-manuscript\round-1\tmp\sources\monaco2018.txt
