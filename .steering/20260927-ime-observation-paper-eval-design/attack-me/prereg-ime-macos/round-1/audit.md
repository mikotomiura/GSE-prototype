# 意図の監査（attack-me・stage `prereg`・round 1）

対象物は `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`（d0cf4343 の下書き）です。意図は context-B.md が指す資料だけから読みました。重さは 高・中・低 で付けています。行番号は対象物と各ファイルのものです。

---

## 1. 意図にあって対象物に無いもの（届いていない主張・判断 85〜98 との差）

**1-1【高】判断 91 の「限界」が書かれていない。§6.1 の根拠の文はブロックが互いに独立だと読める**
- 意図: 判断 91「学習の影響は候補の並びや自動確定の位置に出うる。区間はブロック単位のクラスタ・ブートストラップで出すが、ブロックをまたぐ依存は扱えない → 限界に書く。」「影響: design.md §1.1b からの逸脱として事前登録に書く」。context-B の既知の限界にも「ブロックをまたぐ依存は区間に入らない」とあります。
- 対象物に在るのは条件だけです。§3.2 L190-191「The input method's learning is not reset: no method of resetting it was found, and the plans request no reset.」
  - 影響（候補の並び・自動確定の位置）も、ブロックをまたぐ依存が区間に入らないことも書かれていません。
  - 逆に §6.1 L299-300 は「resample whole blocks ..., because trials in one block share the state of the input method」と書きます。リセットしない条件の下では、ブロックが互いに独立だと読める根拠の文になっています。
- 学習の履歴を左右する順序も固定されていません。
  - ON と OFF のどちらのセルを先に測るか。
  - E3 `working`（ON の計画を 8 時間流す）を E1 の前に回すか後に回すか。
  - パイロット（同じコーパス `c8f890cb…`）で IME が既に学習していること。
- handoff §2 の確認点 3 は、このままでは未対応です。

**1-2【高】handoff §2 の確認点 4（構造から予想できる dwell の偏り）について、対象物は何も書いていない。Return 2 回より大きい構造もある**
- 意図（handoff §2 の 4）: 予想を「書けば検定の形になる・書かなければ後付けの説明に見える」ので研究者の判断、とあります。判断 85〜98 にこの裁定は在りません（未決）。
- 対象物は予想も、構造が凍結の前から分かっていることの開示も書いていません。以下は §1.1 L22-25 の観測器の規則（「closed as committed by Return, by any key other than a letter, digit, space, backspace, arrow or input-mode key ... closed as abandoned by Escape」）と、§2.3 の表・`kit/gen/recipes.json`・`ime_compose.rs` L198-207 / L294-317 から読めるものです。観測の値は見ていません。
  - S1・S2・S7・S12・S15（ON）: 観測は 1 回目の Return で閉じ、正解は 2 回目で閉じる（handoff の指摘）。
  - **S10（両セル）**: 表 L117「Tab (a predictive candidate), pause, Return」。Tab は「その他」のキーなので、観測は Tab で閉じます。正解は think（0.2〜20 s）の後の Return まで続きます。think が長ければ IoU < 0.5 になり、見逃しと偽検出に割れる見込みです。
  - S4・S5（ON）: 観測は 1 回目の Escape で閉じ、正解は 2 回目または 4 回目の Escape で閉じる。
  - **S6（両セル）**: Backspace は観測のセッションを閉じません（`ime_compose.rs` L297-302「セッションは続く」）。全部を消した後も行が出ず、次の試行の打鍵に続いて 1 行になるか、20 s で打ち切られる見込みです。試行をまたぐ汚染ですが、§6.2 の carry_over は正解側にしか掛かりません。
  - ⚠️ Tab を「その他」に写す `hook_macos.rs` の写像は一覧の外なので、確かめていません。
- §6.8 L428-429「a session is still paired as long as the offset stays at or below a third of its length」は、2 つの区間の長さが同じときにしか成り立ちません。上のように長さが構造からずれるシナリオでは、根拠になりません。

**1-3【中】think の目的（20 秒の打ち切りの境界を見る）が計画の解析から消え、探索に回っている**
- 意図: design §1.5「候補を選ぶまでの間（思考の間）を 0.2 s〜20 s の範囲で振り、dwell_ms の誤差と 20 秒打ち切りの境界を見る」。判断 85 は「20 秒打ち切りの境界を見るという think の目的（design.md §1.5）」を理由に上限 20 s を残し、1 セルあたり約 1 時間を受け入れました。
- 対象物では、§2.3 L105「It is a continuous covariate, not a factor.」とした上で、§6.11 L449-450「for example, the dependence of the duration error on think time ... is reported as exploratory」としています。境界について計画に在るのは §6.5 の件数（20 s 以上で行が出たか）だけです。
- 共変量と書きながら共変量の解析を計画していない形になっています（BRM の J8）。

**1-4【中】handoff §2 の確認点 1（連続量の精度の目標）が未解決。しかも notes.md は在ると言っている**
- §3.3 L205-206 が出すのは、比率 0.95 付近の Wilson の半幅だけです。dwell の誤差・Bland–Altman・ICC には「何が分かれば informative か」の目標がありません。
- 一方で `notes.md` L5-6 は「the estimates that answer them, and the precision that counts as informative are stated in `preregistration.md`」と書きます（3-2 に再掲）。

**1-5【中】E3 `working` の run が E1 の run と別だと書かれていない（判断 98 の 4）**
- 意図: 判断 98 の 4「E1 の夜とは分ける（サンプラーの負荷を E1 に混ぜない）」。
- 対象物 §6.9 L433-435 は「`working` (the observer runs while the runner plays the plan of the cell with live conversion on)」と「one night each」だけです。次の 3 点が開いたままです。
  - この run の観測・正解を E1・E2 の解析に使わないこと。
  - §3.4 の「1 セル 1 run」に数えないこと。
  - 8 時間で止めた後、約 11.9 時間の計画の残りをどうするか。
- 持ち帰り 2 の「1 通りに決めてある」に、ここで分岐が残っています。

**1-6【中】L2 の「シナリオの混合」が落ちている**
- design §1.3a「★ 速さ・シナリオの混合を変えた 2〜3 の「合成テキスト母集団」で、集計量の偏りが混合比で動くかを見る。」
- 対象物 §6.6 L367-369 は速さの 3 混合だけです。判断 85〜98 にこれを外した判断は見当たりません（それより前の判断は読んでいません）。

**1-7【低】design §1.3 の除外規則のうち「IME の異常終了」が無い**
- design §1.3「事前に決める除外規則: 時計の跳び・IME の異常終了・ホストのクラッシュ。」
- 対象物 §2.2 L92「A run is aborted if the front-window check fails or if either program stops.」の「either program」は参照入力欄と観測器です。IME のプロセスの異常は、中止にも除外にも入っていません。

**1-8【低】判断 98 の 1 の計画の SHA-256 を登録していない**
- 判断 98 の 1 は ON `c7a5469d…`・OFF `3759ebf7…` を記録しています（d0cf4343 は Mac でも一致と記録）。
- 対象物 §2.4 L142-143 は「The plan is generated on the measuring machine; its SHA-256 is recorded in the run manifest.」だけです。凍結の時点で期待する計画の値が固定されていません。

**1-9【低】E3 の Windows をどこで登録するかが書かれていない**
- design §3「両 OS で測り直す」。`kit/e3/README.md` L15-16 も「Two conditions on two systems make four nights.」と書きます。
- 対象物 §1.3 L64-66 が追補に回すと書くのは Windows のセル・他の IME・他のアプリだけで、E3 の Windows は挙がっていません。

---

## 2. 対象物にあって意図に無いもの（主張の漂流・範囲を超えた言い方）

**2-1【中】題が、E2 で確かめる性質を前提にしている**
- 対象物 L1「Pre-registration: agreement of a **content-free** observer of Japanese input-method conversion ...」。
- 意図の側の言い方:
  - requirement.md は「本文再構成不能性（content-free 主張）の評価設計」と書き、content-free を評価の対象にしています。
  - design §0 の題は「without recording text」です。
  - design §2 は「同定はかなりできる見込み」と書きます。
- 本文の §1.1 L19 は「No character, reading, candidate string or window name is written.」と正確に書いています。題だけが、検証前の性質を言い切っています。

**2-2【中】n の根拠が、精度から「1 晩に収まる」へ入れ替わっている**
- 対象物 §3.3 L206「The number was chosen so that each run fits in one night.」
- 意図:
  - design §1.5 は n = 75 を「再現率 0.95 付近で Wilson 95% 半幅 ≈ ±5pt」で決めました。
  - 判断 85 は精度を見て n = 75 を選び、「1 セル約 10 時間を受け入れる」としました。
  - その後、判断 90 で 11.9 h になりました。
- 時間は受け入れた費用であって、選んだ基準ではありません。しかも同じ段落が、見積もりは「leaves out the start of each block」と書いています。11.9 時間超を「1 晩」と呼ぶのも苦しい言い方です。

**2-3【中】盲検の言い方が、macOS の観測器の性質と合わせると強すぎる**
- 対象物 §2.5 L150-151「...were all fixed without reference to any session row of the observer.」。同じく §3.1 L167-168 は「the key rows of the observation」を解析したと書きます。
- §1.1 自身が書くとおり、macOS の観測器は打鍵から状態を推論します。セッションの行は、key 行（区分と時刻）と入力モードからほぼ決まります（`ime_compose.rs` の遷移表）。
- 文字どおりには正しい言い方です。ただし、パイロットで読んだ key 行がセッションの行の入力そのものだった点に触れていません。handoff §2 の 4 も「構造はコードの仕様から分かる」と認めています。
- ⚠️ 14 区分が遷移表の分岐（英数字・Space・Enter・Esc・Backspace・矢印・モード・その他）をすべて区別するかは、区分表が一覧の外なので確かめていません。

**2-4【低】K0 / K1 の意味が、知識の段からモデルの次数へ変わっている**
- 意図: design §2「K0 = ログだけ / K1 = K0 ＋ 文のジャンル」。`kit/e2/README.md` L31-32 も同じです。
- 対象物 §6.7 L404-405 は「K0, a character unigram model, and K1, a character trigram model ...」です。
- 実装（`open_set.py` L19「K0 no knowledge of the genre: a character unigram model estimated from the training phrases」）では、K0 も同じコーパスから推定しています。対象物は、K0 が何から推定されるか、それがなぜ「ジャンルを知らない」に当たるかを書いていません。

**2-5【低】パイロットでの手打ちが、何から決めたかの一覧に入っていない**
- 意図: requirement.md の含まないもの「人を対象とする打鍵データの収集（著者本人の打鍵も含めない・合成入力のみ）」。
- `pilot-macos.md` L48-50「the same happened when the keys were typed by hand, both in the reference input field and in TextEdit」は、Return を 2 回にする手順の根拠の一部です。
- 対象物 §3.1 L169-180 の「informed this protocol」の一覧には、この手打ちの確認も送り方 13 通りの試行も出てきません。§2.1 L72「no person's typing is recorded」は本計測についての文で誤りではありません。ただ、パイロットの記述としては不完全です。

---

## 3. 矛盾（対象物の中・公開物とのあいだ・意図どうし）

### 意図どうし・意図と実行可能性

**3-1【高】判断 97 の「K = 1000 でも意味を持つ」が、この n では成り立たない（下は私の計算）**
- 対象物 §6.7 L396-397 の判定は「near chance ... when the upper end of its 95% Wilson interval is at most 2/K」です。
- 数える試行はセルごとに約 2,900〜3,150 です（S12 の合成かな列を除く）。n = 3,000、K = 1000 で、まったくの偶然の攻撃（期待 3 件正解）の Wilson 上端を計算すると次のとおりです。

  | 正解の件数 | Wilson 上端 | 2/K = 0.002 以下か |
  |---|---|---|
  | 3 / 3000 | ≈ 0.0029 | 超える |
  | 2 / 3000 | ≈ 0.0024 | 超える |
  | 1 / 3000 | ≈ 0.0019 | 以下 |

- 偶然の水準の攻撃でも、「偶然に近い」と判定される確率は約 2 割です（Poisson(3) で 1 件以下）。
- `acc` は粗い集合との最大値を取るので、上端はさらに上へずれます。
- K = 1000 では「推奨する粒度なし」がほぼ既定の結果になり、判断 97 の理由と食い違います。K = 10・100 では問題ありません（K = 100 で上端 ≈ 0.014）。

**3-2【中】判断 92 と判断 98 の 6 が両立しにくい**
- 判断 92「追補では、変えてよいのは gt_rules.json の win_imm / win_tsf と、追補の節の本文だけ」。対象物 §7 L457 も同じ文です。
- 判断 98 の 6 は、Google 日本語入力と参照入力欄以外のアプリでの転移確認も「行うなら測る前に追補で登録する」としています。
- しかし次のものは、規則ファイルの Windows の区画の外を要しうる追補です。
  - 転移確認（design §1.6 は oracle だけで数える別の解析）。
  - Windows の (a) IMM と (b) TSF のどちらを正解の経路にするか（design §1.1・§6）。
  - Windows の生成の config（plan_config）。
- 「may change only」を字のとおりに読むと、これらを書く余地がありません。

**3-3【中】`gt_rules.json`・`config.json` の `_note` が段階凍結（判断 92・§7）と食い違い、しかもハッシュに入る**
- `gt_rules.json` の `_note` 逐語「win_imm and win_tsf are still the working hypothesis ... and are revised against the Windows calibration pilot before the freeze.」
- `config.json` の `_note` 逐語「The values are provisional and are frozen when the pre-registration is frozen; ... the rule file is revised against the calibration pilots before the freeze」
- 判断 92 では、Windows の規則を直すのは macOS の凍結の**後**（追補）です。
- 2 つのファイルは凍結のハッシュに入ります（§8）。凍結の時点で、正しくない注記（「provisional」「before the freeze」）が固定されます。
- 追補は `_note` を変えられません（§7 で変えてよいのは Windows の区画だけ）。そのため、追補の後も注記を直す道がありません。

### 対象物の中の矛盾

**3-4【中】§1.2 の参照先が違う**
- L36「which decides which log granularity is recommended (section 6.6)」。粒度の判定は §6.7 です。§6.6 は Question 3（テキスト単位の一致）です。

**3-5【中】正解ログの中身が §2.2 と §4.2 で違う**
- §2.2 L83「and each key-down it receives (key code only). No text is recorded.」
- §4.2 L237「The ground-truth log (`gt.jsonl`): the reference input field's calls (kinds, lengths and times only).」
- `kit/refinput-macos/README.md` L13「The recorded key codes still reflect what was typed.」と合っているのは §2.2 のほうです。

**3-6【低】持ち越しの件数の言い方**
- §6.2 L310-312「so every trial it overlaps is excluded (in the pilot, 2 of 126 trials with live conversion on, in S8 and S10)」。
- 規則では 2 組 4 試行が除外されます（判断 87 は t00098/t00099・t00119/t00120）。「2 of 126 trials」は除外された数に読めます。

**3-7【低】`dwell_ms == 0` の扱いの書き方**
- §6.2 L318-319 は「count as false positives, and their number is reported in every bucket」です。偽検出にしかならない行を、すべてのバケットで数えると言っています。
- §6.5 L347-348「Pairs whose `dwell_ms` is zero are left out」は、§6.2 と `l1.py` L51-52「never into a pair」の下では起きない場合です。

**3-8【低】§1.2 L34「Every estimate is reported with an interval」と、区間の無い推定値**
- §6.4 L340「F1 without an interval」・§6.7 の平均順位・§6.5 の打ち切りの件数には区間がありません。

### 対象物と一覧の公開物のあいだ

**3-9【中】`pilot-macos.md` の所要時間が判断 90 の前の値のまま**
- L148-149「For the measurement settings (below), the generator's estimate ... is 11.2 s per trial with live conversion on and 11.4 s with it off.」
- L153-154「One macOS cell then takes about 9.8 hours ... and 9.3 hours with it off.」
- L161「These settings are frozen with the pre-registration.」
- 対象物 §3.3 は、11.2 / 11.4 s を「the generator's estimate for the pilot's key intervals」と呼び、本番を 11.9 h / 11.2 h（13.6 / 13.8 s）としています。

**3-10【中】`pilot-macos.md` の学習の記述が判断 91 の前のまま。run/README とも食い違う**
- `pilot-macos.md` L20「(a method of resetting it is still being examined). The example cell file (`kit/run/cell.example.json`) describes a reset at every block」
- `kit/run/README.md` L58-61「`reset_cmd` is empty and the `learning` entry of `ime_settings` records that the learning is not reset」
- 対象物 §3.2 は「no method of resetting it was found」です。

**3-11【中】`kit/run/README.md` が時計を合わせると書いている（判断 94 で直したのと同じ型）**
- L160-161「The `gt` and `obs` logs use the clocks of their own processes, so their times are aligned to the oracle in the analysis, not by the runner.」
- 対象物 §4.4 L266-267「no clock correction is applied」・§6.8 と合いません。

**3-12【中】`notes.md` の結果ファイルの名前と、informative の主張**
- L13「`results/e2_closed_set.json`, `results/e2_open_set.json`」。対象物 §6.7（と判断 98 の 3）では `results/e2_closed_set_<cell>.json` / `results/e2_open_set_<cell>.json` です。
- L14「`results/e3_<system>_<condition>.json`」。`kit/e3/README.md` の手順では要約は標準出力で、この名前のファイルは作られません。
- L5-6 の「precision that counts as informative」は 1-4 のとおりです。

**3-13【低】`kit/gen/README.md` が、本番の値をまだ決めていないと書く**
- L37-38「Production values are not yet fixed (speed, think time, and n will be added ... when the protocol is frozen)」・L189「Production speed, think time, and n are not yet fixed.」
- `plan_config.macos.json` で既に決まっています。このファイルは凍結のタグで固定されます。

---

## 4. 対象物と意図が一致していると確かめたもの（参考・指摘ではない）

- **判断 85**: n = 75・think 0.2〜20 s・← → ← →・`nav_count_max` = 3（§2.3・§3.2・`plan_config`）。
- **判断 86**: 50 ms・10〜900 ms で同じセッション（§4.3）。
- **判断 87**: 持ち越しの両方を除外し、oracle の一致は変えない（§6.2・§6.3）。
- **判断 89 の 2**: `settle_ms` 1,000 ms（§2.2）。
- **判断 90**: 480 / 240 / 120・中央値と平均の差 4.6%・英語の書き写しで日本語の推定値ではない・`key_hold_ms` 60（§3.3）。
- **判断 92**: §7 の文。
- **判断 93**: 公開（§8）。
- **判断 94**: 補正しない・`clock_sync.py` を毎回回す（§6.8）。
- **判断 95**: 扱いと docstring（`l1.py` L52-54・`l2.py` L35 は直し済み）。
- **判断 96**: `n_continued_commits`（`gt_sessions.py`・`l1.py` の `abandon_by_continued_commit`）と §6.5。
- **判断 97**: 2/K・極大の要素（`e2/README.md` L239-241 の「coarsest」も直し済み）。
- **判断 98 の 2・3・5・6・7**: seed・E2 の固定値・止める規則・範囲・書誌 9 件。
- **持ち帰り 1**: 推定で書き、検定はしない。
- **持ち帰り 3**: 合成入力・2 セル・参照入力欄（§1.3・§6.1 L297-298）。

---

## 5. 読めなかった範囲・注入の疑い

**読んだもの**
- context-A.md・context-B.md。
- requirement.md（全体）、design.md L13-182・L220-234、decisions.md L674-797、handoff L43-58。
- preregistration.md（全体）。
- `experiment/` の 9 ファイル（全体）。
- `kit/e3/README.md`・`kit/run/README.md`・`kit/logger/README.md`（全体）。
- `recipes.macos-live-off.json`（全体）。

**一部だけ読んだもの**
- `kit/gen/README.md`: L30-129・L180-191 と grep。
- `kit/e2/README.md`: L20-99 と grep。
- `kit/pilot/README.md`: L136-147 と grep。
- `kit/refinput-macos/README.md`: L1-25 と grep。
- `kit/emit/README.md`: grep だけ。
- `recipes.json`: L1-25 と S4・S5・S7・S10・S11・S12・S14・S15 の grep。ON の S8・S13 は読んでいません。
- コード: `l1.py` L20-59・L440-487、`pipeline.py` L318-353、`ime_compose.rs` L1-90・L190-335。`gt_sessions.py`・`l2.py`・`open_set.py` は grep だけです。

**読んでいないもの**
- 一覧の中: `match.py`・`stats.py`・`generate_plan.py`・`run_cell.py`・`clock_sync.py`・`seal_obs.py`・`closed_set.py`、上に挙げた README の残り。
- 一覧の外（読む範囲の規則により確かめていない）: `cell.example.json`・`hook_macos.rs`・KeyCategory の区分表・FORMATS.md。
- 意図の資料のうち指定外の範囲: design.md の §4・§5（L183-219）と冒頭 L1-12、判断 84 以前、handoff の §2 以外。1-6 で「外した判断が無い」と書いたのは、判断 85〜98 の範囲についてだけです。
- 査読者の記録・他の round・`tmp\` は読んでいません。

**確かめられなかった主張**
- 対象物 §2.2 L78-79 の「the SHA-256 of its manifest is written into the header of every log it produces (`manifest_sha256`)」は、一覧の中の `kit/logger/README.md` には書かれていません。実装は一覧の外です。

**注入の疑い**
- 読んだ範囲に、LLM に向けた指示の文は見つかりませんでした。
