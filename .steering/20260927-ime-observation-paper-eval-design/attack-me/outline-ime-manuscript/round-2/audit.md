# 意図の監査（stage outline・round 2）

対象物は `C:\GSE-prototype\papers\ime-observation\manuscript\outline.md`（commit 9463fae6）。意図は round 2 の `context-B.md` と、そこが指す資料。行番号は outline.md のもの（他のファイルは名前を付けて書く）。

**要点（重い順）:**
- 要旨の規則が、凍結した事前登録 §6.1 と食い違う（3-A）。
- 外枠は「時刻つきのキー行は攻撃に渡していない」と書くが、事前登録とも外枠 §8 とも食い違う（3-B）。
- 貢献 1 の「any input method」は言い過ぎ（2-A）。
- 要旨の区間の範囲は、試行が 3〜5 本の層で決まってしまう（3-D）。
- 「推定であって検定しない」が外枠のどこにも無い（1-A）。

## 0. 引き継ぎの判定

| 指摘 | 判定 | 根拠（位置・逐語） |
|---|---|---|
| 0-(a) | 解消 | l.15「The title is fixed here and is not changed after the results are known.」／l.80-81「The estimate of this agreement is the primary contribution of the paper.」。README.md:1 の題は "Observing…" のまま。判断 149-4 で M12 に回した既知のずれ。 |
| 0-(b) | 解消 | l.89-91「an alternative rule that infers sessions from key presses can be evaluated against the same ground truth without new measurement; an observer that needs other signals has to be run again with the kit」。要旨の規則は l.96-102。（残る問題は 2-D） |
| 1-1 | 解消 | RE2 l.393「Basis: rule (sections 1.1, 6.4, 10.3)」と §11(b) l.309-311「its size depends on the writing and is not given」。意図の側の言い方に残る問題は 3-I。 |
| 1-2 | 一部 | 中国語の読者への文 l.73-75「The analysis concerns the operating systems and applies to any input method on them」は、言い過ぎを新しく生んだ（2-A）。 |
| 1-3 | 一部 | §12（l.320-332）に主な限界は入った。ただし登録済みの限界の一部が無い（1-D）。 |
| 1-4 | 未解消（具体を出した） | 1-C を見てほしい。 |
| 1-5 | 解消 | l.336「other input methods, other applications, and human typing」 |
| 2-1 | 解消 | l.149-150「Not recording text is not new in itself; the design difference here is a log of the conversion that holds no text.」。research-positioning.md:851 の「設計上の排他性」と合う。 |
| 2-2 | 解消 | l.171「no documented call names another process」／l.184-185「The logger therefore infers sessions from key presses and the input mode.」 |
| 2-3 | 解消 | l.315-316「All recommendations hold for the reference input fields and synthetic input of this study.」 |
| 2-4 | 解消 | l.60「on Windows the rows of modifier keys and of key releases」。ただし l.193 との新しい矛盾が出た（3-C）。 |
| 2-5 | 解消 | l.281-282「the synthetic key intervals are independent of the keys」／l.331-332。ただし同じ箇所の周りに新しい誤りがある（3-B）。 |
| 2-6 | 解消 | 外枠を「well above」で grep して 0 件。 |
| 2-7 | 解消 | l.239「without estimating Japanese typing」 |
| 3-A-1 | 一部 | l.37-38 と貢献 2 は直った。ただし l.126-127「the sessions that an input field receives from the input method」と l.153「exists only in the calls an application receives」（2-B）に実体化した言い方が残る。 |
| 3-A-2 | 解消 | 「trust」の grep は "trusted repository"（l.30）の 1 件だけ。「reliable」は 0 件。 |
| 3-B-1 | 解消 | l.49-50。要旨の規則 (iv) l.101「without an interval」 |
| 3-B-2 | 解消 | l.294「Runs that the runner aborted are included when they pass the same checks」は事前登録 §3.4 l.474-476 と合う。D6 の試行 1 を寄託しないこと（deviations.md l.139）とも矛盾しない。 |
| 3-B-3 / 3-B-4 / 3-B-5 / 3-B-7 / 3-B-8 | 解消 | OB1-3・DS3 の「Not registered」、LG1a/LG1b、l.194-195 の F13、l.279「qualification」 |
| 3-B-6 | 解消 | 一覧にあるファイルの中で次を確かめた。ime_compose.rs:795 `over_long_sessions_are_truncated_without_a_row`・:587 `other_keys_close_the_session_as_confirmed`、ime_cloak.rs:449 `session_self_heals_after_max_duration`・:374/393/432（150 ms の間隔）、candidate.rs:43 `is_stale_winevent_active`。`#[test]` の数は 37/12/8/12/9 で context-A と一致した。ただし「約 25 秒の行を書く」ことを試すテストは、一覧にあるファイルの中に名前では見つからなかった。 |
| 3-B-9 | 未解消（既知） | kit/logger/README.md:41-42「(until a driver is present for the current platform, this ends with "not implemented")」が残っている。 |

## 1. 意図にあって対象物に無いもの

**1-A. 「推定であって検定しない」と「合否にするのは near-chance だけ」が無い**
- 意図: context-B の持ち帰り 2「仮説は検定せず…推定を合否にするのは、漏洩の研究の near-chance の規則だけ」。事前登録 §1.2 l.43「The study estimates; it tests no hypothesis.」、l.46-48「No estimate is turned into a pass or fail decision, except the near-chance rule」。
- 外枠: 「hypothes」の grep は 0 件。Scope l.50-51 は「No threshold of adequate agreement is set」だけを書く。
- 外枠 l.31-32 は投稿時の確認（検出力）を引くので、検定を予期する読者への先回りが要る。

**1-B. 要旨の規則に、持ち帰り 1 と 3 の差し込み口が無い。2 つの OS の値を並べるのに、比べないという但し書きも無い**
- l.96-101 の (i)〜(iv) は数値だけである。次の 3 つが要旨に届かない。
  - 観測可能性の結論。l.112 は「What was done (observability analysis; …)」だけで、結論が無い。
  - 2 つの構成概念。
  - §11 の推奨。
- 一方 (i)(ii) はセルごとに macOS と Windows を並べ、(iv) は 2 つの OS の CPU を並べる。外枠 RE1 l.392「not compared across systems」、RT1 l.391「values of the two systems not compared」、Scope l.39-41（Windows の一致には構成概念の違いが入る）と釣り合っていない。
- context-B の気にしていること 1（持ち帰りが見えにくくなっていないか）に、この点がいちばん効く。

**1-C. （引き継ぎ 1-4 の具体）macOS の規則が、読みの途中のキーでセッションを閉じる**
- 意図の資料: design.md §5 l.212「かな入力の欠陥」。その中身は §1.4 l.130 の S12 の行にある。
- 登録済みの記述:
  - 事前登録 §4.5 l.559-561「the trial sends the minus, comma or period key, which closes a session under the observer's rules (in Romaji input these keys type a long-vowel mark, a comma and a full stop; in the kana layout of S12 they type ho, ne and ru)」
  - §6.4 l.736-737「a reading split by the minus, comma or period key」
  - §3.1 l.276 では 113 試行で起き、そのうち 76 が S12。
- 外枠: §4 l.198 は「another closing key」とだけ書く。§11・§12・Table 4 に記述が無い。context-B の既知の限界からも落ちている（意図どうしのずれでもある）。
- 長音記号はローマ字入力でもよく打つので、書字研究者の集計（変換の数）に直接効く。

**1-D. 登録済みの限界のうち、§12 に無いもの（1-3 の残り）**
- near-chance の規則は、ブロック内の依存があると甘くなる。事前登録 §6.8 l.904-906「a rule that reads the Wilson upper end is met more easily than it should be」。§11(c) と要旨 (iii) の判定の向きに効くのに、外枠には無い。
- 攻撃が最強だとは言わない。§6.8 l.931-932「Neither attack is claimed to be the strongest possible; the results hold for these attacks.」。外枠 §8 l.282-283 は「conditions that are expected to favour identification」と片側の向きだけを書いている。
- ブロックのブートストラップは、ブロックをまたぐ依存を覆わない（§7 l.995-996）。§12 l.331 は Wilson の区間についてだけ書く。
- 予測（spec）は修飾キー・行の回収・遅れを模していない（§7 l.1004-1009）。
- Windows は既定の設定で、予測候補を表示している。§10.11 l.1416-1417「With predictive candidates turned off, the window would open at the conversion」。外枠 §5.2 と §12 には設定の記述が無い。
- 研究者自身のログでは、打ち切られたセッションを確かめられない（§6.4 l.716-718）。§11(b) に足りない一言。
- テキストごとの LoA と ICC は速さの間で比べない（§6.7 l.804-806）。§7 l.273-274 に無い。

**1-E. 「結論」にも同じ規則がかかる**
事前登録 §6.1 l.623「In the abstract and the conclusions, estimates are given as the ranges of their intervals」。外枠 §13（l.336）はこの規則を受けていない。

## 2. 対象物にあって意図に無いもの（漂流）

**2-A. 貢献 1 の「applies to any input method on them」（l.74）**
- 「文書化されたインタフェースが無い」という否定の側は OS の層の話である。しかし残る経路は入力方式に依る。
  - 隠蔽の経路は窓のクラスが正確に "IME" であることに依る。ime_cloak.rs:59-61 `class == "IME"`。
  - 事前登録 §10.11 l.1414-1415「in applications that draw the candidates themselves the observer may see nothing」。
  - macOS の推論は標準の IME の鍵の割り当てに依る。Space・Return・Escape の扱いは、たとえば中国語の拼音入力では違う。
- context-B の持ち帰り 1 は「文書化された公開のインタフェースから見る限り」としか言っていない。判断 106（他の IME は別の研究）を超えている。

**2-B. §2 l.152-153「the construct (a conversion session) exists only in the calls an application receives」**
- 事前登録 §7 l.976 は「an application sees a conversion only through these calls」と書く。外枠の文はそれより強い存在論で、Scope l.38-39「not the input method's internal state」とも当たる。

**2-C. RE4 l.395「the 39-trial check of section 10.8 is its smallest unit」と §11(d) l.313-314**
- この点検は「計画どおりのセッションが参照に出るか」だけを見る。観測（ロガー）は封をして読んでいない。data.windows.md l.50-53「The observation log was sealed before the reference side was read. … every trial produced the session its plan intends (39 of 39)」。
- したがって「一致の検証の最小単位」ではない。
- 39 試行の点検は Windows のものである。macOS ライブ変換 ON は 14×3=42 の層で、登録された点検が無い。
- 根拠に挙げた kit/run/README.windows.md は計測の run の手順で、研究者向けの 39 試行の手順は書いていない。
- 「registered procedure」とあるが、§10.8 が登録したのはこの計測の関門であって、利用者の手順ではない。

**2-D. §10 l.300-302 の (b2) をデータセットの「Intended uses」に数えている**
DS3 l.399 自身が「use (b2) needs the kit to be run again」と書く。(b2) はデータセットではなく一式の使い道である。context-B の気にしていること 3 の釣り合いを崩す。

## 3. 矛盾

**3-A. ★ 要旨の規則が、凍結した事前登録と食い違う（判断 149-5 と事前登録 §6.1 の矛盾）**
- 外枠 l.101-102「The values over all trials and every other estimate … are not quoted in the abstract.」
- 事前登録 §6.1 l.623-626「In the abstract and the conclusions, … An estimate in the primary scope is given together with the fraction of trials that the scope sets aside and the estimate under `all_trials`」。deviations.md に、これを変える逸脱は無い。
- 外枠の中でも Scope l.53-54 は事前登録と同じ文を書いている。
- Scope l.43-44「the fraction of trials excluded for this reason [carry-over] is reported next to every primary estimate」も、要旨の (i)(ii) には入っていない。
- 外枠の前置き l.6-8 は事前登録が優先すると言う。このままでは、要旨の規則は逸脱として報告するか、直すかのどちらかが要る。

**3-B. ★ 時刻つきのキー行の扱い**
- 外枠の側:
  - Scope l.59-61「the key rows with times … were not given to the attacks, and publishing them is not evaluated」
  - §12 l.331「evaluates no timed record」
- 外枠の他の箇所と事前登録の側:
  - 外枠 §8 l.280-281「The feature sets that keep time are reported as estimates only」と RC1 l.388（6 つの特徴の集合）
  - 事前登録 §6.8 l.836「The attacks read the category and time of every key row」、l.872-874「reported as an estimate only, and they are excluded from the recommendation」
- 正しくは「渡したが、判定と推奨からは外した」である。context-B の既知の限界「時刻つきの記録…は評価しない」も同じ不正確さを持つ。

**3-C. 押下と解放**
- 外枠の側: l.193「one key row per press and release」、貢献 2 l.76-77「for every key press and release」。どちらも OS を分けていない。
- 事前登録の側:
  - §1.1 l.20-21「For every key press it receives … it writes one of fourteen key categories and a time」（macOS）
  - §10.7 l.1335-1336「the modifier rows and the release rows that the Windows observer writes」
  - §3.3 l.396-397「key-up times are not part of any measure」
- 外枠 Scope l.60 も、解放の行を Windows に限って書いている。
- Table 1 の次元「key-down and key-up times」（l.134）の、このロガーのセルに効く。macOS のドライバは一覧の外で読んでいないので、ソースでの確認が要る。

**3-D. 精度の計画の「the smallest with 30 and 31 trials」（l.242）**
- 事前登録 §3.3 l.324-325 の 31 は「the smallest stratum under the cut-off other than those of S6 and S13」である。l.354 では macOS の S6 は slow 3（ON）/ 5（OFF）、mid 27（ON）。
- 帰結: 要旨の規則 (i) l.97-98「from the lowest lower end to the highest upper end of the per-stratum Wilson intervals」の下端は、n=3〜5 の層が決める。範囲がほぼ情報を持たなくなり、主の貢献が要旨で見えなくなる（気にしていること 1）。

**3-E. 「同じ計測の run」**
- 外枠の側: l.128-129「All analyses of agreement, recoverability and the dataset come from the same measurement runs.」、l.221「All questions are answered from the same measurement runs.」
- 食い違う側:
  - 外枠 §10 l.292-294。データセットには較正パイロットの区分がある。
  - 事前登録 §6.2 l.674「The run of the `working` condition of question 5 is not used for questions 1 to 4」と §10.8 l.1377-1378。問い 5 は別の run である。

**3-F. 値を写す元の一覧が狭い**
- l.360-365 は「Every result value … is copied from these files」とし、対象を notes.md の結果ファイルと登録の設計値に限る。
- しかし次の値は、その外の記録から来る。
  - RF1 l.378: `clock_sync.py` の出力と pilot-windows.md
  - AG9 l.385: data.md・data.windows.md・deviations.md
  - §5.2 l.227: 「39 of 39」

**3-G. 投稿規程の言い換えで効果量が落ちている**
- 外枠 l.31-32「appropriate measures of variability and, when relevant, of statistical power」。context-A の逐語は「variability, effect size, and (when relevant) statistical power」。

**3-H. 用語**
- 題の注 l.15-16 は「"Logging" is used because on macOS the conversion is inferred … rather than observed」と書く。
- 一方、事前登録の題（preregistration.md:1）は「an observer」である。外枠は「observation rows」（l.378）・「observation」（§5.6）を使い、「an observer that needs other signals」（l.90, l.300）では他の道具を指している。
- 「logger」と登録の「observer」が同じものだと、外枠は書いていない。

**3-I. 持ち帰りの言い方（意図の側）**
- context-B の持ち帰り 3「20 秒の打ち切りが集計を動かす向きは規則から言える」。しかし外枠 §11(b) l.310 と事前登録 §6.4 l.719-722 では、変換の数と放棄率は「either direction」である。向きが規則から決まるのは 4 つのうち 2 つだけ。
- Windows の窓のイベントの経路には 20 秒の打ち切りが無く、約 25 秒で行を書く（§10.3 l.1158-1161）。§11(b) の「the 20-second cut-off」は macOS と隠蔽の経路の言い方である。

**3-J. 要旨の規則の「For each cell」（l.96）**
(iii) の推奨は macOS の 2 セルを合わせて決める（RC2 l.389）。(iv) の実行コストは OS ごと（RT1）。軽微。

**context-B の気にしていること 2（題と推論・LG1b）への所見**
l.207-209 と LG1b は、本文を書かないことは版（manifest の SHA-256）の性質であって、ログからは確かめられないと正直に書いている。題との釣り合いは取れている。残るのは 3-H の用語のずれだけ。

## 5. 読んだ範囲と読めなかった範囲・注入

**読んだもの:**
- context-B、context-A、carryover-audit、outline.md の全体。
- design.md: l.1-37（§0）と l.200-219（§5）。ほかに grep で l.30・52・88・130 を見た。★ l.130（§1.4）は指定の節の外で、1-C の「かな入力の欠陥」の中身を知るためだけに使った。
- decisions.md: 範囲で読んだため、指定の外の判断（2〜5・7〜9・16〜20・22・107・108 の頭・148）も目に入った。指摘の根拠には指定の判断（1・6・15・21・106・145〜147・149）だけを使った。
- research-positioning.md l.805-856。
- preregistration.md: l.1-190、270-284、311-400、455-493、541-580、600-935、972-1046、1097-1456。
- data.windows.md・kit/logger/README.md・kit/run/README.windows.md の全体。
- FORMATS.md l.60-99、deviations.md l.120-165、ime_cloak.rs l.40-79。
- そのほかは grep だけ: README.md・notes.md・data.md・pilot-macos.md・pilot-windows.md・ime_compose.rs・ime_winevent.rs・cloak.rs・candidate.rs。

**読んでいないもの:**
- preregistration.md の l.191-269・285-310・401-454・494-540・581-599・936-971・1047-1096。
- deviations.md の D1〜D5 の本文。
- pilot-*.md・data.md・notes.md の本文。
- ime_winevent.rs・cloak.rs・candidate.rs の本文。
- macOS のドライバ（一覧の外）。

**一覧の外に触れたこと:** `kit/logger/src` 全体への Grep で、一覧に無い main.rs・driver_windows.rs・driver_windows/keyboard.rs・driver_macos/tests.rs・input/ime_mode.rs・analysis/key_gate.rs の関数名とテストの数が出力に出た。開いてはいない。指摘の根拠にもしていない。

**注入の疑い:** 無し。読んだ文の中に、LLM に向けた指示は見当たらなかった。
