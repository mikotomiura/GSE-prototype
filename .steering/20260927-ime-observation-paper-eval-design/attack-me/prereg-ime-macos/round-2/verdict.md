# verdict — attack-me・stage `prereg`・round 2（2026-10-01・G-GEAR・メイン）

対象物: `papers/ime-observation/experiment/preregistration.md`（枝 `feature/ime-m3-prereg`・`384712ee`・本文は `29372289` で直した版・SHA-256 `3f98e9d9…1229`）。投稿先 BRM。

## 1. 編集者の判定: **major revision（直して再査読＝round 3）**

- 有効な査読: **3 / 3**（R1・R2・R3 とも、必要な本数の文献から基準を逐語で抜き出して査読まで進んだ）。推奨は R1 minor・R2 major・R3 minor（R3 は「新しい major 2 件を凍結の前に直す」条件つき）。fatal は 0 件。
- round 1 の引き継ぎ: 47 件（R1 20・R2 16・R3 11）のうち、査読者の判定で解消 25・部分的に解消 19・未解消 3（R1 m11〔後退〕・R2 minor-5・minor-7）。監査役は 27 件のうち解消 22・部分的に解消 5。
- 読み替え（stage `prereg`）: major = 直して再査読。凍結しない。ただし round 3 は、今回の直しで変わる節に絞れる（3 人とも「計画の立て直しは要らない」）。
- 理由（3 行）:
  1. round 1 の直しで新しく足した部分（§3.3 の精度の文・§6.4 の範囲と比較と層・§6.8 の依存の理由づけ）に、計算の誤り・定義の穴・文とコードの食い違いが入った。⚠️ 問 3 の主の推定値（Bland-Altman の偏りと一致の限界）には、§6.1 が約束する区間を、凍結するコードが出さない。
  2. 問 3 の主を `all_trials` にした理由（研究者が受ける偏り）が、§7 の「打ち切りの割合はこの設計の性質」と両立しない。主の値は思考時間の分布で決まる。
  3. この研究で唯一の判定（E2 の推奨）が、1 つの打鍵の欠けでセルごと消え、1 秒のビンを推奨に残した理由も、ms の集合を外した理由と同じ形で崩れる。⚠️ パイロットの生ログを預ける文が事前登録から落ちた（後退）。

## 2. 一致した指摘（分母 = 有効な査読 3。監査役は別枠）

| 群 | 指摘 | R1 | R2 | R3 | 監査役 | 裏取り |
|---|---|---|---|---|---|---|
| A | n の根拠: §3.3「separates … one in twenty from one in ten」は誤り・主の範囲（`under_limit`）では精度の目標に届かない層が多い・表は x = round(n·p) で作った・決めた順序 | N1 | N7 | N2（major）・N8・m5 | 1-4 | **真**（メインが `stats.wilson` で再計算: 71/75 → [0.871, 0.979]・68/75 → [0.820, 0.954]・34/34 → 下端 0.8985・p = 0.95・n = 75 の正確な p では半幅 5.29、x = 71 では 5.4。真の recall 0.95 で 73/75 以上が出る確率 0.27） |
| B | §6.4「Each analysis of questions 1 and 2 is computed under three scopes」「Each scope is computed for three comparisons」が §6.6・§6.7 とコードに合わない（問 2 は 2 範囲・問 3 は `gt_obs` だけ） | N8 | N3 の一部 | N3 (ii)(iii) | 3-a・3-b | **真**（`pipeline.py:179-180` `L1_SCOPES = ("under_limit", "all_trials")`・`L2_SCOPES`・`:47-48`「level 2 for gt_obs under all_trials and under_limit」） |
| C | §1.2「Every proportion and every continuous estimate is reported with an interval」に例外（§6.3 の配送・§6.9・§6.10・§6.8 の平均順位・§6.7 の混合の偏り） | N8 | N9 | N3 (i)(iv) | 3-8 | **真**。⚠️ R3 N3 (i) の **問 3 の Bland-Altman の偏りと一致の限界に区間が無い**も真（`l2.py:310-319` の `_agree` は `stats.bland_altman` の点だけを返し、区間は `icc21_ci` だけ。`mixture_bias` も点だけ）。§6.1「the limits of agreement, kappa and the ICC carry 95% percentile bootstrap intervals」と食い違う |
| D | E2 の依存の理由づけ「judging by the upper end allows for part of this」は逆向き・通る確率の表は 1 つの集合の確率で「粗い集合の最大」を表していない・§7 に E2 の限界の項が無い | N9 | N5 | N5 | 1-b | **真**（独立を仮定した Wilson の上端は、相関があると低すぎて near chance に通りやすい。§7 に該当の項が無いことを確かめた） |
| E | 問 3 の主を `all_trials` にした理由（§6.4）が §7 の最後の項目と矛盾し、主の値が設計の打ち切り率で決まる | — | N3（major） | N1（major） | （2-a は問 1・2 の側） | **真**（§6.4:503-505 と §7:720-722。slow の long は ON 423 / 1,050） |
| F | `long` は打ち切られたセッションが**始まった試行**に付くので、後の試行に落ちた打ち切りの帰結（断片の行・失われたセッション）が `under_limit` に残る。層 `started none` は、打ち切りの後に断片を始めた受け手を拾わない。§6.4 の over_limit の文は持ち越しのとき誤り | N3 | — | N4 | 2-a・3-i | **真**（`spec_predict.py:204-211` の打ち切りと当て直し・`match.py:739` が `received_carry` を `n_started == 0` だけで決める。該当は §3.1 の数から ON で最大 75・OFF で最大 77 試行） |
| G | E2 は打鍵 1 つの欠け（か余り）でセルごと止まり、推奨が消える。欠けた打鍵は預けの検査（`data.md` 手順 4）にも無い | N5 | N2（major） | — | — | **真**（`closed_set.py` の selftest「one missing press stops the run instead of shifting later trials (exit 2)」・`open_set.py:70-71`「the assignment is refused when the counts … differ」・`data.md` 手順 4 は `excess_rows` と `rows_outside_trials` だけ。パイロットの欠けは入力モードのキー以外で 0 / 約 8,080） |
| H | `bin1s`・`bin1s_count` を推奨に残したことが、ms の集合を外した理由と同じ形で崩れる（人の記録の語・句の境の休止は 1 秒のビンに残り、この設計はそれを作らない。§6.8 自身が「Pauses between words and phrases … are not modelled either」と書く） | M1（部分的に解消） | N1（major） | — | — | **真**（論理。§6.8:609-615） |
| I | パイロットの生ログを預ける文が事前登録から落ちた（後退）・基準は未記載 | m11 | minor-7 | — | 1-a | **真**（`29372289` で §3.1 の「its raw logs will be deposited with the measurement data after the check that report describes」が消えた。判断 99〜107 にこれを消す判断は無い。⚠️ メインが引き継ぎで自分から書いた件）。監査役は、封印したパイロットの観測ファイルを凍結の後にどうするか（開ける・預ける・開けない）も登録に無いと指摘（真: §2.5 は「the sealed files were not opened」だけ） |
| J | `under_limit` は速さごとに読みの長さと思考時間で試行を選ぶので、速さのあいだの比較が交絡する（§7 の列挙に読みの長さが無い） | N2 | （N6 が近い） | N7 | — | **真**（論理。§3.3 の表: 間の無い S3 でも slow は 60 / 75） |
| K | 本計測の run 単位の関門（預けの検査に落ちた run・計画の SHA-256 が違う run）の後の分岐が無い | m11 の後半 | — | N6 | — | **真**（`data.md:39-43`「not deposited until the extra rows are explained」・§2.4「not analysed」。§3.4 の 3 回に数えるかが無い） |
| L | `pilot-macos.md` Clocks の「about 66 ms」が §6.9 の「about 370 ms」（回収の遅れを含む）と食い違う | m2 | — | — | 3-e | **真** |

- 1 人だけの指摘（すべて裏取りした・真。例外は下の §5）:
  - R1: M3 の残り（§6.6 Cut-off の「specified: zero」は正解の側の期間〔`l1.py` の `truncation_check`: `dwell >= limit_ms`〕で long を数えるので仕様から出ない）・M5 の残り（§7「visible through `n_continued_commits`」は放棄だけ）・m1（D ≤ 1.8 は半幅が最大 1.34 倍）・m4（中止の後のやり直しの順と学習）・m5（焦点の喪失の試行の観測の行が `gt_obs` の偽陽性になり、分けた数が無い）・m10（1,000 ms の根拠）・N4（`pred_obs` は送出の時刻で予測するので、回収の遅れ〔最大約 100 ms〕で短い断片が対にならない）・N6（毎ブロックのかなキーで、入力ソースのポーリングの経路を通らない。`driver_macos.rs:70-72` のコメントで確かめた。本体は一覧の外）・N7（`carry_over` の除外が「計画どおりでない試行は除かない」の原則の例外として書かれていない・**部分的に真**: 除外としては §6.2 に理由つきで宣言済み）・N10（回収は 1 枠で、2 つが 1 回のポーリングのあいだに閉じると 1 行が失われる。`ime_compose.rs:386-388`）・N11（nav の正解は送出の記録）。
  - R2: N4（推奨の文の「publishing logs」はセッションの行を出さないときだけ）・N6（試行ごとの差は、繰り越しの汚染のため、読者の混合での重み付けし直しが成り立たない）・N8（open set と推奨の関係が無い）・nit 1（試行の外の行の上限 5 は、かなを記録しない観測のログには 4。参照はかなを見る〔`delivery.py` の selftest〕）・nit 2（速さ別の正解率が無い。`closed_set.py` は `by_scenario` だけ）・nit 3（打ち切り・配送・合成の間隔の説明の重複）。minor-5（中間の粒度）は未解消のまま（H を採ればさらに重くなる、と R2）。
  - R3: m1 の残り（書き出しの根と、一覧を作る手順が書かれていない・凍結コミットの 40 桁の SHA が登録に入らない。⚠️ 書き出しの道具 `kit/export/export.internal.py` は書き出しの外）・n1 の残り（ICC の model〔mixed〕の名前。`stats.py:192` は「two-way random」）・N9（4 つの層は分割ではない: 3 つの旗は独立）・M2 の残り（2/K の余裕のプライバシーの上の意味の根拠）。
  - 監査役（別枠）: 1-2 の残り（§6.9 の「offset … stays at or below a third of its length」は長さが同じときだけ。`notes.md`・`pilot-macos.md` にも同じ文）・1-5 の残り（E3 `working` で 8 時間の後の計画の残り約 3.9 時間）・1-c（§7 に「他の IME は評価していない」の項が無い・判断 106 の「限界と今後の課題」）・1-d（判断 107 の 1 の「予測のセッションも重なり最大で試行に割り当てる」「試行ごとの表は範囲の外の試行を除く」「`dwell_fraction` の分母は変えない」が本文に無い）・2-a（§7「The primary estimates of questions 1 and 2 describe the sessions the observer is specified to report」は §6.4 の「not removed from `gt_obs`」と合わない）・2-b（§1.1「For every key press」: 入力モードのキー・F13〜F19・修飾キーは行が出ない）・2-c（§7「a conversion exists only as the calls …」は存在の強い主張）・2-d（`kit/refinput-macos/README.md:22`「trials are independent of one another」）・2-e（`notes.md` の問いがはい／いいえの形）・2-f（題「the input method's own calls」）・**3-c**（層 closing key in reading の説明「a long-vowel mark, a comma or a full stop」は S12 のかな配列では誤り: `recipes` の `kana_layout` で minus・comma・period は ほ・ね・る。§3.1 の 113 試行のうち ON 76 は S12。`spec_predict.py:87` のコメント「in Romaji and in kana input alike」も誤り）・**3-d**（§8「may not change any other existing file」と、Windows の手順が既存の `kit/gen/recipes.json` の `os.windows` と `generate_plan.py` の `_PROFILES["windows"]` にあり、`kit/gen/README.md` がそこを直せと書くことが食い違う）・3-g（§6.7「A text mixes the scenarios of its block about equally」は期待値の上だけ）・3-h（凍結のハッシュに入る `gt_rules.json` の `_note`「together with both trials」は「every trial it overlaps」より狭い）。3-f（context-B の「約 3 割」は判断 99 の古い数え方で、事前登録の 40% が正しい）は**意図の側の古さ**で、対象物は直さない。
- Codex は加えていない（既定どおり。今日の台帳は 354,180 / 上限 300,000）。

## 3. 直す順（fatal → major → minor → nit・対象物の位置つき）

### major（★ は設計の判断が要る → 研究者に問う）

- ★ **X1 問 3 の主の範囲**（群 E・§6.4:503-505・§6.7・§7）: (a) 主を `under_limit` にして問 1・2 と揃え、`all_trials` は「この設計の打ち切り率に依存する副」として出す／(b) `all_trials` を主のまま、§6.7・§7 に「この設計の長い試行の割合（§3.1）の下での値で、自然な執筆の偏りではない」と書き、要旨では割合と並べてだけ報告する。
- ★ **X2 `long` の定義と層**（群 F・§4.5・§6.4・§3.1・§3.3）: (a) `long` を「打ち切られたセッションに打鍵が入った**すべての**試行」に広げ（予測から決定的）、`received_carry` を「前の試行で始まったセッションに打鍵が入った試行」に定義し直す（`spec_predict.py`・`match.py`・selftest・変異・§3.1/§3.3 の数の計算し直し）／(b) 定義は今のまま、文で正確に書き、後の試行に落ちる件数を §3.1 に載せる。
- ★ **X3 E2 の 1 秒のビン**（群 H・§6.8:609-615）: (a) 推奨を `no_time`・`counts_only` に限り、`bin1s`・`bin1s_count` は ms の集合と同じく推定だけ／(b) 残すなら「人の休止の構造を持たない記録に限る」と書く（実質、人の記録には使えない）／(c) 語・文節の境に休止を置く合成の条件を足して確かめる（計画の変更）。※ (a) を採ると、推奨の粒度では時刻の指標が残らない（R2 minor-5 の中間の粒度は未解消のまま）。
- ★ **X4 E2 の打鍵の欠け**（群 G・§6.2:469-470・§6.8・`data.md` 手順 4）: (a) ブロックの印で合わせ直し、合わないブロックの試行は「採点しない」として数え、残りで判定する（`closed_set.py`・`open_set.py` の変更と selftest）／(b) 止まるまま、預けの前に入力モード以外の到達を確かめ、欠けのある run は §3.4 の中止の試みとしてやり直す／(c) 止まるままにして、その確率を限界に書く。
- ★ **X5 問 3 の区間**（群 C の (i)・§6.1・§6.7・`l2.py`）: (a) `l2.py` に、問 3 の偏り・一致の限界・混合の偏りのブロックのブートストラップの区間を足す（selftest・変異）／(b) 区間を付けないものとして列挙する。
- ★ **X6 パイロットの生ログ**（群 I・§3.1・§2.5・`pilot-macos.md`）: 預ける約束を §3.1 に戻すか、封印したパイロットの観測ファイルを凍結の後にどうするか（開けて預けるが解析しない／封印のまま／預けない）。基準そのものは Mac の残りの作業。
- ★ **X7 Windows の追補と既存のファイル**（監査役 3-d・§8・`kit/gen/README.md`）: (a) 追補は、既存のファイルの Windows の部分（2 つの手順書の `os.windows`・`generate_plan.py` の `_PROFILES["windows"]`）も変えてよいとし、macOS の部分が変わらないことを 2 つの凍結のタグの差で示す（macOS の解析は macOS のタグから回すので影響しない）／(b) 今のうちに Windows の手順を別のファイルへ出し、追補は新しいファイルだけにする（凍結の前のコードの変更）。
- **X8 n の根拠**（群 A・§3.3）: 「separates …」の文を区間の幅の記述（「0.95 と 0.90 の区別は保証しない」）に替える／主の範囲での層ごとの n と半幅（目標に届く層・届かない層）／速さの水準の n を主の範囲の値（slow ON 627・OFF 577）に／表は x = round(n·p) で作ったと書く／順序（n = 75 は本番の打鍵間隔を決める前に精度で決め、打ち切り率が分かった後も見直さなかった・1 晩は副の根拠）。n は変えない（R3:「言えることを設計に合わせればよい」）。

### minor（主に文の整合。直す一覧の承認で直す。〔コード〕はコードの変更を伴う）

1. §6.4 を「検出は 3 範囲・問 2 は 2 範囲（`over_limit` は §6.6 Cut-off だけ）・問 3 は `gt_obs` だけ」に（群 B）。
2. §1.2 の全称を、記述として出すもの（§6.3・§6.9・§6.10・平均順位）を除く形に（群 C の (iv)）。
3. E2 の依存（群 D）: 逆向きの文を直す（独立の Wilson の上端は相関があると低すぎる）・「key rows は送った打鍵で決まり、句・間隔・おとりは試行ごとに独立に引く」の論証・表の注（1 つの集合の確率で、最大で報告する集合では上限）・§7 に項目。〔コード・任意〕正解率のブロックのブートストラップの区間を記述として併記。
4. `under_limit` の組成の交絡（群 J）: §7 に読みの長さを足し、「主の範囲での速さのあいだの比較は、読みの長さと思考時間の選別と交絡する」と書く。〔コード・任意〕層と範囲ごとの読みのキー数と思考時間の分布（計画と予測だけで計算できる）。
5. §7「describe the sessions the observer is specified to report」を、主の範囲は打ち切りだけを除き、規則が予測する他の食い違いは `gt_obs` に残る（`gt_pred` で見える）と直す（監査役 2-a）。
6. §6.6 Cut-off の「specified: zero」を、予測の long と `pred_obs` に限る（R1 M3 の残り）。
7. §7 の `n_continued_commits` を「放棄で見える」に狭める（R1 M5 の残り）。
8. §6.1 の「small」に量（D ≤ 1.8・半幅は最大 1.34 倍）を（R1 m1）。
9. 中止の後のやり直しの順と学習の持ち越し（ON の中止は OFF の前にやり直す、など）を §3.2・§3.4・§7 に（R1 m4）。
10. 焦点を失った試行の観測の行（`gt_obs` の偽陽性）を数えて出す（R1 m5）。〔コード・小〕
11. `pred_obs` の時刻: 送出の側のずれと回収の遅れで、対にならないことがある短い行の長さを §6.9 か §7 に（R1 N4）。
12. §7 の合成入力の項に、モードの切り替えは毎ブロックのかなキーだけで、入力ソースのポーリングの経路は試していない（R1 N6）。
13. `carry_over` を §1.2・§6.3 の原則の明示の例外として理由つきで書き、除いた試行にあった観測の行の数を出す（R1 N7）。〔コード・小〕
14. §6.8 の推奨の文を「セッションの行を公開しない場合の key 行の粒度」にし、セッションの行を公開する形は評価していないと書く（R2 N4）。
15. 試行ごとの差（§6.7）に繰り越しの汚染が入ることを書き、層 `none`（と `under_limit`）に限った版も出す（R2 N6）。〔コード〕
16. open set は推奨の規則に入らず、推奨の表の隣に記述として並べると書く（R2 N8）。
17. run 単位の関門（群 K）: 預けの検査に落ちた run・計画の SHA-256 が違う run を §3.4 の中止の試みに数える（説明できなければ解析しない）と書く。§8 に「凍結のタグの結果を常に登録の結果として報告し、欠陥が分かった後の解析し直しは逸脱としてその横に示す」。
18. §9 に書き出しの根（公開物の最上位のディレクトリ）と、凍結コミットの 40 桁の SHA を登録に載せることを（R3 m1）。
19. `pilot-macos.md` Clocks の 66 ms を回収の遅れを含めた値に・§6.9／`notes.md`／`pilot-macos.md` の「a third of its length」を長さが違うときの言い方に（群 L・監査役 1-2）。
20. E3 `working`: サンプラーは 8 時間で止め、計画は最後まで流す（など）を §6.10 に（監査役 1-5）。
21. §7 に「標準 IME の 2 セルだけで、他の IME と他のアプリは評価していない（別の研究）」（監査役 1-c）。
22. 判断 107 の 1 の 3 点（予測のセッションも重なり最大で割り当てる・試行ごとの表は範囲の外の試行を除く・`dwell_fraction` の分母は変えない）を §4.5・§6.4・§6.7 に（監査役 1-d）。
23. 層 closing key in reading の説明を「読みの中で、観測器の規則がセッションを閉じるキー（minus・comma・period: ローマ字入力では長音記号・読点・句点、かな配列では ほ・ね・る）を送る試行」に（§3.1・§4.5・§6.4）。`spec_predict.py:87` のコメントも直す（監査役 3-c）。〔コードのコメント〕
24. `notes.md` の問いを how closely の形に（監査役 2-e）。
25. `kit/refinput-macos/README.md` の「trials are independent of one another」を直す（監査役 2-d）。
26. `gt_rules.json` の `_note`「together with both trials」→「every trial it overlaps」（凍結のハッシュに入る・監査役 3-h）。

### nit

- §1.1「For every key press」→ 入力モードのキー・F13〜F19・修飾キーを除く（監査役 2-b）。
- §7「a conversion exists only as the calls …」を和らげる（監査役 2-c）。
- 題の「the input method's own calls」（監査役 2-f）。
- §6.7「about equally」→ 期待値の上で（監査役 3-g）。
- ICC の model の名前（two-way mixed・McGraw & Wong の ICC(A,1)・ICC(2,1) と数値が同じ）と `stats.py:192` の docstring（R3 n1）。
- 4 つの層は重なりうる（R3 N9）。
- 回収は 1 枠で、2 つが 1 回のポーリングで閉じると 1 行が失われる（R1 N10）。
- nav の正解は送出の記録（R1 N11）。
- `data.md` の試行の外の行の上限をログごとに（観測 4・参照 5）（R2 nit 1）。
- E2 の速さ別の正解率を記述で出すか、プールで判定する理由を 1 文（R2 nit 2）。
- 打ち切り・配送・合成の間隔の説明の重複を減らす（R2 nit 3・任意）。
- 1,000 ms の閾値の根拠（R1 m10・round 1 から採らなかったまま）。

## 4. 意図の監査役

- **意図にあって対象物に無いもの**: 1-a（パイロットの生ログを公開する約束・design §1.1a・判断 99〜107 に取り消しは無い → X6）・1-b（§7 の E2 の区間の限界 → minor 3）・1-c（他の IME → minor 21）・1-d（判断 107 の 1 の 3 点 → minor 22）。
- **対象物にあって意図に無いもの**: 2-a（§7 の主の推定の言い方 → minor 5）・2-b〜2-f（nit と minor 24・25）。新しい節（§4.5・§6.3 の配送・§6.4・§7）は、2-a と 2-c を除けば判断 99〜107 の範囲に収まっている、と監査役。
- **矛盾**: 3-a・3-b（→ minor 1）・3-c（→ minor 23）・3-d（→ X7）・3-e（→ minor 19）・3-f（意図の側の古さ・直さない）・3-g（nit）・3-h（→ minor 26）・3-i（→ X2）。
- 監査役は判断 101 の表の値（0.210・0.067・K = 100 で c = 1.5 の 0.487）を計算し直して一致を確かめた。本文の「section N」の参照はすべて正しかった。

## 5. 偽陽性・確かめられない・逸脱・注入

- 接地の引用: 査読者ごとに `round-1/tmp/sources/` で逐語照合した（R1 10 件・R2 10 件・R3 13 件・すべて）。**捏造は 0 件**（PDF の頁の切れ目に柱と頁番号が挟まった 2 件〔Conijn・Plant〕も本文に在った）。
- 部分的な偽陽性: R1 N7（`carry_over` は §6.2 で理由つきの除外として宣言済み。原則の例外として書かれていない点だけ残す）。偽陽性: なし。
- 確かめられない（一覧の外）: R1 N6 のうち、入力ソースのポーリングの本体（`driver_macos.rs` の一覧の外の部分）。コメントの記述は確かめた。
- 規程: 判定に使った J1〜J10 はすべて照合済み・J11 は「規定なし」で、それに依る指摘は無い。未照合の要件: なし。
- **逸脱 1（監査役の保存の検査）**: `secrets-filter.sh` は 0 だったが、応答に一覧の外のパス `C:\GSE-prototype\papers\ime-observation\kit\refinput-windows\README.md:135` が 1 件あった（監査役の自己申告: `kit\**\README.md` への Grep の出力に 1 行出ただけで、指摘にも根拠にも使っていない）。Skill の規則どおり、いったん `audit.md` へ写さずに `tmp/audit.raw.md` に置き、研究者に問うた → **研究者の選択で写した**（一覧の外は同じ論文の公開物の README で、秘密でも封印物でもない。2026-10-01・判断 108）。上の §4 の裏取りはメインが一次で行った。
- **逸脱 2（R1 の保存の検査）**: 検査が `C:\GSE-prototype\papers\ime-observation\`（一覧のファイルの親ディレクトリ・応答の最後の行で相対パスの起点として書いたもの）を一覧の外と判定した。ファイルではなく、その行に並ぶ相対パス 9 件はすべて一覧の中にあることを目で確かめ、写した（検査の偽陽性）。
- 失敗した役・再起動: なし。4 本とも締切の内に返った（監査役 8.3 分・R2 9.3 分・R1 11.4 分・R3 13.8 分）。
- 注入の疑い: なし（4 本とも「無し」と報告。メインも本文を印字していない）。
- 起動の前に研究者へ知らせたこと: この機械に Zenodo のトークンがあること（`sealed/` は無い）。

## 6. 研究者に問うこと

- X1〜X7（設計の判断）と、X8・minor 26 件・nit 12 件の直す一覧の承認、〔コード〕の付いた minor（3・4・10・13・15）を入れるか、round 3 を回すか、監査役の応答の扱い（逸脱 1）を `AskUserQuestion` で問うた（4 問・4 問・2 問）。
- **結果（2026-10-01）: 10 問とも推奨どおり**。X1 問 3 の主は `under_limit`・X2 `long` を打鍵が入った試行すべてに広げる・X3 1 秒のビンを推奨から外す・X4 ブロックで合わせ直す・X5 `l2.py` に区間を足す・X6 預ける約束を戻し、封印は預けるときだけ開ける・X7 既存のファイルの Windows の部分も許す・監査役の応答は写す・直す一覧は全部承認（コードの 5 件も）・round 3 を変わった節に絞って回す。記録は `decisions.md` の判断 108〜110。
