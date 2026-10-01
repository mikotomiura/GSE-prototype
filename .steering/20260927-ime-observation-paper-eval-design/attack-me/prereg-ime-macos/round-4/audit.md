# 意図の監査（stage `prereg`・round 4）

対象は `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`（952 行・全文を読んだ）と、一覧のうち round 3 から変わった公開物とコードの関数。
意図の資料は context-B と `decisions.md` の 860〜939 行（判断 111〜115）です。行番号は今の版のものです。

全体として、判断 112〜115 はほぼ同じ形で届いていました。重い食い違いはありません。新しく出た指摘の多くは、§3.4 の中止の規則と §3.1 の約束、つまり今回の直しで足した文の周りにあります。

## 古い言い方と名前の残り（判断 112 と 115 で改めたもの）

- `reference_focus_out` と `trials_with_focus_out` は、一覧のどこにも出てきません（Grep で 0 件）。
- `n_conversions` が残っているのは `l2.py:609` と `l2.py:1487` の 2 か所だけで、どちらも `per_trial` です。判断 115 の 1 のとおりです。
- 「`dwell_fraction` の分母はテキスト全体の時間」という古い言い方は残っていません。`l2.py:31-34` と selftest の `l2.py:1052` は、新しい定義を守っています。
- 「説明できる余分な行」という古い言い方も残っていません。"explain" は、新しい規則の "No other reason and no explanation is admitted"（§3.4:354・data.md:37）にしか出てきません。
- 変わった節に出てくる「section N」は、すべて実在する節を指しています。

## 0. 引き継ぎの判定

| 指摘 | 判定 | 理由・今の版の位置 |
|---|---|---|
| A 1-1（`long` の新しい定義が言い方に届いていない） | 部分的に解消 | §1.2:50-51・62、§4.5:422、§6.4:561-562、§7:854-855、`l2.py:121` には届いた。§6.2:517-518 に古い狭い言い方が 1 か所残る: "and the trials whose session the observer's rules cut off, which are set aside from the primary scope"。§1.2:62 の "whose presses went into no session that the observer's rules cut off" に揃えるべき |
| A 1-2（題が範囲を言っていない・nit） | 未解消（採らなかった・既知） | 1 行目の題は変わっていない |
| A 2-1（§3.4 の中止の規則） | 解消 | §3.4:349-357、§3.2:250-251、§6.3:554-556、data.md:23-40 が判断 112 の Y2 と一致する。新しい規則から生じた別の問題は下の 1-A・1-C・2-A・3-A に書いた |
| A 3-1（§7 の粒度の文が §6.8 と合わない） | 解消 | §7:832-833 "granularities between milliseconds and one-second bins are not evaluated" |
| A 3-2（§7 の入力モードの文が S14 と合わない） | 解消 | §7:834-836 |
| A 3-3（README と事前登録の、余裕 2/K と依存の食い違い） | 解消 | README:99・107-110・279-289 |
| A 3-4（notes.md の「すべての結果のファイル」） | 解消 | notes.md:19-21、`pipeline.py:48-49` |
| A 3-5（回収の遅れ・nit） | 解消 | §6.9:786 |
| A 3-6（印を oracle が記録するか・nit） | 解消 | §4.5:415-416 |
| A 3-7（断片の行の割り当て・nit） | 解消 | §6.4:566-569 |
| A 3-8（§1.2 と §6.3 の区間の範囲・nit） | 解消 | §1.2:39-41、§6.1:487-488 |
| B 1-a（パイロットの生ログを預ける基準） | 部分的に解消（中身は既知の未了） | 約束の文は §3.1:188-192 と §3.1:220-222。何を・いつ（凍結の前）・どこに（`pilot-macos.md` と §3.1）は判断 113 の Y4 と合う。書き方の問題は下の 3-D・3-F |
| B 1-4（一致の限界の幅を予想しない理由） | 解消 | §3.3:328-330 |
| round 1 の 3-8（問 4 の場面ごと・速さごとの正解率の区間） | 解消 | §1.2:39-40、§6.1:487、§6.8:710-711 |
| 1-b の nit（依存の文の向き） | 解消 | §6.8:748-752、§7:860-863、README:109-110 |

## 1. 意図にあって対象物に無いもの

**1-A（minor）判断 115 の 2「外からの入力で中止にした run は預けない」が、事前登録に書かれていない**
- このことが書かれているのは data.md:35-37 だけです: "the run counts as an aborted attempt, is not analysed and is not deposited, since its reference log may hold a person's key presses"。
- §3.4:357 は "Aborted runs are reported with their reason and their delivery figures, and are not analysed." までで、預けないことを言っていません。
- 規程 J4 は生データをすべて公開することを求めます。プライバシーを理由にした例外は、凍結される文書に書くべきです。
- あわせて、この種の中止は `run.json` の `aborted` にならず、data.md の表にだけ残ります。`pipeline.py:22-23` の "A run whose manifest says aborted is left out ... and is counted" の数（`n_aborted`）には入らないので、「中止を報告する」場所が 2 つに分かれます。

**1-B（nit）判断 113 の Y3 は「§1.2 の問 4 にも範囲を書く」としたが、§1.2 には単位しか無い**
- §1.2:55-58 は "identify which of K candidate phrases was typed in a trial" と、単位を句 1 つに絞っています。
- 一方、「同じ書き手の複数の試行の組み合わせ・既知の最終テキストとの突き合わせは評価しない」と「ログ全体の安全は述べない」は、§6.8:745-747 と §7:865-868 にしかありません。

**1-C（minor・査読者の領分に近い）新しい中止の閾値が、実際の参照のログで確かめられていない**
- 判断 112 の Y2 の狙いは 2 つです。人の打鍵が混ざっていないかの検査を残すこと。そして、試験の対象の誤りで run を捨てる道を断つこと。
- ところが閾値（`excess_rows` > 0、1 ブロックあたり 5）は、参照の側の振る舞いを前提にしたまま確かめられていません。`pilot-macos.md:182-183` は "the pilot's reach count (`kit/pilot/reach.py`) checked only the direction from the executor to the observation" と書いています。
- まず、参照入力欄が実行器のかなキーを key_down として受けるかが確かめられていません（上限 5 は「受ける」と仮定しています）。受けないなら、1 ブロックあたり 1 打鍵、run 全体で 126 / 117 打鍵の見逃しの余地ができます。
- 逆に、外からの入力が無くても参照に余分な key_down が出ることがあれば、3 回の試みがすべて中止になり、セルは "not measured" になります。
- 判断 113 の Y4 で Mac で行う作業に、パイロットの参照のログへ `delivery.py` を流すことを加えれば、凍結の前に確かめられます。

**1-D（要確認・nit）context-B の「中間の粒度は評価しない」がどの範囲を指すか**
- §7:833 が言うのは「ms と 1 秒のビンのあいだ」の粒度です。
- context-B の「推奨する粒度では時刻の指標が残らない（中間の粒度は評価しない）」に関係するのは、1 秒より粗いビンなど、時刻を少し持つ形のはずです。それは §7 には書かれていません（評価する 6 つの集合から暗に外れるだけ）。
- R2 の minor-5 の中身は読めないので、確かではありません。

## 2. 対象物にあって意図に無いもの

**2-A（nit）§3.4 は判断 112 の「だけ」に、計画の SHA-256 を足している**
- 判断 112 の Y2 は「中止は参照のログの余分な key-down … と試行の外の行の上限超えだけ」です。§3.4:349-350 は "when its plan has another SHA-256 than the plan of section 2.4, or when the reference log shows a key press from outside the executor" です。
- §2.4:170-171 と同じ趣旨なので、中身の漂流ではありません。
- ただし、data.md の "Run checks" の表（data.md:25）にも手順 1 にも、計画の SHA-256 の欄や手順がありません。§3.4:354-355 の "its result and time are recorded in `experiment/data.md`" が届くのは、配送の検査だけです。

**2-B（minor）§6.4:579-582 で新しく足した文が、§2.5 と §4.5 と食い違う**
- 足した文: "An observer's log does not show which sessions were cut off, because they have no row, so a reader who wants to apply the rule to their own data has to estimate from another source how often a conversion lasts 20 seconds or more"。
- §2.5:178-179 は "The key rows that were read are, on macOS, the very input from which the observer infers its sessions" と書きます。§4.5 も、打鍵に規則を当てれば打ち切りが決まるとしています。
- つまり、時刻つきの key 行があれば打ち切りは（入力モードが分からない分を除いて）見つけられます。「示さない」のはセッションの行です。「別の情報源から見積もるしかない」は言い過ぎです。

## 3. 意図どうし・対象物の中・公開物とのあいだの矛盾

**3-A（minor）中止の上限が「ブロックごと」か「合計」か決まっていない**
- §3.4:353-354 は "its `rows_outside_trials` exceeds the five presses made outside the trials in each block"、data.md:34 は "exceeds five per block" です。
- ところが `delivery.py` は合計の `rows_outside_trials` しか出しません（`delivery.py:31`・`365-376`）。判断 115 の 2 は「今ある出力で書いた」としています。
- ブロックごとと読むと、道具では計算できません。合計と読むと、5 に満たないブロックがあれば、別のブロックの外からの打鍵が隠れます（1-C と重なる）。
- 閉じた規則にするなら、読み方を 1 つに書く必要があります。たとえば「合計が 5 × ブロック数を超える」。

**3-B（nit）§6.7:676 の "over the trials in none of the four layers" は空の集合になる**
- §6.4:603-605 は 4 つ目の層を "the trials in none of the three" と定義しています。なので「4 つのどれでもない試行」は 1 つもありません。
- コードは層 none です（`l2.py:116-117` "the trials in none of the prediction's layers"）。正しくは "in none of the three marked layers"（4 つ目の層）。context-A の要約にも同じ誤りがあります。

**3-C（nit）§3.1 の 188 の言い方が、§4.5 の広げた定義と合わない**
- §3.1:229 は "in 188 trials (all S6) a session runs on into a later trial" です。
- §4.5:424-425 は今回 "carried out" を広げました: "(it ends in a later trial, is cut off by a press outside the trials, such as a marker press, or is still open at the end of the log)"。
- 持ち越した試行が 188、持ち越しを受けた試行が 184 なので、後の試行に入らなかった持ち越しが少なくとも 4 つあります。OFF も 186 対 184 で同じです。

**3-D（nit）§3.1 と `pilot-macos.md` で、基準を書く時期が違う**
- §3.1:189-190 は "the criteria set out there, which are written before the freeze"（判断 113 の Y4 も「凍結の前」）です。
- `pilot-macos.md:172-173`（今回は変わっていない）は "Before they are [deposited], the criteria ... will be written here" で、「預ける前」という弱い時期のままです。
- また §3.1 の関係節 "which are written before the freeze" は、生ログにも基準にもかかって読めます。

**3-E（minor）人の打鍵の扱いが、パイロットと本計測で違う**
- `pilot-macos.md:174-183` の基準の下書きは、観測のログを危険と見ています: "the observation records every key press on the machine"。そのうえで、観測のすべての key 行が送出と対応することを求めます。
- 本計測では、送出の無い観測の行があっても解析し、預けます（§3.4:356-357、§6.3:554-556、data.md:38-40）。
- 判断 112 の Y2 が残したプライバシーの検査は、参照の側だけです。同じ理由（人の打鍵が入りうる）から 2 つの違う規則が出ているので、Y4 の (1) を書くときに揃える必要があります。

**3-F（minor）§3.1 の合わせ直しの約束は、「何を」が足りない**
- §3.1:220-222 は "is run, without any attack, on the key rows of the pilot's observation logs" です。
- 最初のパイロットの印は F13・F14・F13 で（§3.1:194-195）、macOS の観測器はこれに行を出しません（README:170-175）。なので `--markers-in-obs` が使えず、印なしでは食い違いが 1 つあれば exit 2 で止まります（README:208-210）。
- 後のパイロットの印は 3 打鍵で、本計測（4 打鍵）とは違う錨を試すことになります。
- どの run を対象にし、どの印で行うかが書かれていないので、「採点されたブロックの割合」が最初のパイロットでは定まりません。

**3-G（nit）README と §6.8 で、ブロックを失う場合の言い方が違う**
- README:201-203 は "An observed press that is added or duplicated ... also loses only that block" です。
- §6.8:691-692 は "or the next block when an added arrow press joins that block's marker" と書きます。selftest（`closed_set.py:1376-1380`）と判断 115 の 6a も、印の直前に足された矢印では次のブロックを失うとしています。README だけがこの場合を書いていません。

**3-H（要確認）§6.6 の「試行ごとの行の数」を出す箇所がコードに見当たらない**
- §6.6:645-647 は "Agreement with the specified rows is read from the numbers of rows per trial" です。
- `match.py` が出すのは層ごとの `n_gt` / `n_obs` です（`match.py:59`・`458-467`）。`pipeline.py`・`match.py`・`l1.py` を Grep した範囲では、試行ごとの行の数を比べる出力は見つかりません。
- 層ごとの数のことなら、"per trial" の言い方がずれています。試行ごとの比べ方なら、事前登録にあってコードに無いことになります。

## 4. 位置と逐語

各項目の中に書きました。

## 5. 読めなかった範囲と、注入の疑い

**読んでいない範囲**
- 意図の資料: `requirement.md`、`design.md` の §0〜§6、`decisions.md` の判断 85〜110。round 4 は絞った回なので、context-B の要約と判断 111〜115（860〜939 行）だけで照合しました。
- 第 1 群のうち次は今回読んでいません: `plan_config.macos.json`、`config.json`、`gt_rules.json`、`SEED`、`run.sh`、`env.md`、`kit\e2` 以外の `kit\*\README.md`（`kit\run\README.md` は Grep の結果だけ）、`recipes*.json`、`keymap_macos.json`。`pilot-macos.md` は 1-10・38-42・165-186 行だけ読みました。
- コードは一部だけ読みました。
  - `delivery.py`: 1-90・260-449・726-777 行
  - `l2.py`: 1-325・985-1009 行
  - `pipeline.py`: 14-198 行
  - `match.py`: 105-129・730-756 行
  - `closed_set.py`: 40-59・600-649・1336-1390 行
  - `l1.py`: 280-337 行
  - そのほかは Grep の結果だけ
- 読んでいないコード: `open_set.py`、`gt_sessions.py`、`stats.py`、`generate_plan.py`、`run_cell.py`、`clock_sync.py`、`seal_obs.py`、logger のソース。
- §3.3 の設計効果の値（Σm²/Σm）と §3.1 の予測の数は、計画を開いていないので計算し直していません。§3.3 の表の列の和が 603 / 852 / 940 と 553 / 783 / 876 に合うことと、§6.8 の n（2,925 / 2,700）は確かめました。

**一覧の外のファイルが出た件**
- `papers\ime-observation` 全体に古い名前を探す Grep をかけたとき、一覧の外のファイルの行が出力に出ました: `kit\refinput-windows\src\core.rs`、`kit\refinput-windows\README.md`、`kit\formats\validate_logs.py`、`kit\formats\FORMATS.md`、`kit\refinput-macos\RefInput.swift`。
- これらの中身は、どの指摘にも使っていません。この Grep で使った結果は、古い名前が 0 件だったことだけです。

**注入の疑い**: ありません。読んだ文の中に、LLM に向けた指示は見当たりませんでした。
