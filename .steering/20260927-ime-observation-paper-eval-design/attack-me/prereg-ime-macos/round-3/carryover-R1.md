# carryover-R1 — round 2 からの引き継ぎ（R1: 打鍵の時刻を測る道具の検証の立場）

作成: 2026-10-02（メイン）。あなた（R1 の立場）の round 2 の新しい指摘 11 件（N1〜N11）と、round 2 であなたが「部分的に解消／未解消」と判定した round 1 の指摘 10 件について、メインの裏取り・研究者の採否・対応・未解決を書く。
⚠️ **再掲を求めない**。各指摘が今の版で**解消したか**を 1 件ずつ判定してから（解消 / 部分的に解消 / 未解消・理由 1 行・今の版の位置）、**今回の直しが作った新しい穴**を探してほしい。round 2 で「解消」と判定した指摘は引き継がない（変わっていない節は round 2 の判定のまま）。
「採らなかった」部分は研究者の選択（またはメインの選択）で、理由を添えた。その理由が成り立たないと考えるなら、新しい指摘として根拠つきで書いてよい。

## 版の変化（round 2 の版 `384712ee` → 今の版 `abc5d7f9`）

- 節番号は変わっていない。round 2 の行番号は使えない（本文は 9,326 語から 11,217 語に増えた）。変わった節とコードの関数は context-A の「round 2 から変わった箇所」。
- 読んでよいファイルの一覧は round 2 と同じ（増減なし）。

## A. round 2 の新しい指摘

裏取りの判定は、メインがコード・計画・事前登録で確かめた結果。11 件すべて「真」（N7 だけ「部分的に真」）。

### N1 [minor] §3.3 の精度の文が、表と Wilson 区間の非対称を取り違えている
- 裏取り: 真（メインが再計算: 71/75 → [0.871, 0.979]・68/75 → [0.820, 0.954]。表は round(n·p) の整数で計算されていた）。
- 研究者の採否: 文を区間の幅の記述に替え、主の範囲での層ごとの n と半幅を書く。n は変えない。
- 対応: §3.3 の Trials（n を決めた順序: 精度で決め、本番の打鍵間隔を決める前で、打ち切りが分かった後も見直さなかった・1 晩は副の根拠）・Precision of proportions（「round(n x p) successes in n trials」と明記・表の最小の行を 31 に）・表の後の段落（「this does not guarantee that 0.95 and 0.90 are told apart (71 of 75 gives the interval 0.871 to 0.979)」・31 試行で約 9 点・主の範囲の速さごとの n と 1.4〜1.8 点）。

### N2 [minor] 主の範囲 `under_limit` は、速さごとに読みの長さと思考時間で試行を選ぶ
- 裏取り: 真（論理。間の無い S3 でも slow は 75 試行のうち 59 だけが残る〔新しい `long` の定義で〕）。
- 研究者の採否: 解消の条件 1 と 2 を採る。
- 対応: §6.1 第 1 段落の後半（「In the primary scope the trials that remain differ between speeds in composition … so a difference between speeds is not an effect of speed alone. The number of letter keys and the think time of the trials in each scope are reported per stratum, from the plan.」）・§7 の打ち切りの範囲の項（読みの長さを足した）。コード: `pipeline.py` の `_composition`（層 × 範囲ごとの英字のキー数と思考時間の n・中央値・最小・最大を計画から出し、`_prediction_summary` の `composition` に入れる）。
- 採らなかった: 解消の条件 3（要旨の規則に「`under_limit` の主の値には、外した試行の割合と `all_trials` の値を並べる」を加える）。メインが直す一覧に入れなかった（§6.1 の要旨の規則は変えていない）。

### N3 [minor] 層の定義が、繰り越されたセッションが打ち切られた後に新しいセッションを始めた試行を拾わない
- 裏取り: 真（`spec_predict.py` の旧版は `long` を打ち切られたセッションの始まった試行に付け、`match.py` は受け手を `n_started == 0` だけで決めていた）。
- 研究者の採否: `long` を「打ち切られたセッションに打鍵が 1 つでも入った試行」に、持ち越しを受けた層を「前の試行で始まったセッションに打鍵が入った試行」に定義し直す（予測から決定的）。§3.1・§3.3 の数を計算し直す。
- 対応: §4.5（各セッションが「打鍵が入った試行」を持つ・「the press that cuts a session off does not enter it」・`long` と `received carry` の定義・`started none` を置き換えた）・§3.1（`long` は ON 755・OFF 713、`received carry` は両セル 184、そのうち自分のセッションを始めない試行は 113 / 109）・§3.3 の表（計算し直し・S13 は全試行が `long`）・§6.4（Scopes と Layers）。コード: `spec_predict.py` の `_Machine`・`summarise_trials`（出力の形式 `spec_predict/2`）・`match.py` の `parse_prediction`（`received_carry` を必須に）。
- メインの実装上の選択: 打ち切る打鍵は打ち切られたセッションに入らない（打ち切りが遷移より先）。そのため、打ち切りの後の最初の打鍵が次の試行の先頭なら、その試行は `long` にも `received carry` にもならない（selftest で守る）。

### N4 [minor] `pred_obs` と `gt_pred` の時刻の扱いが §6.9 の論拠の外にある
- 裏取り: 真。
- 研究者の採否: 解消の条件のうち、文で書く道（3 つ目と 1 つ目の一部）を採る。断片の行を IoU 以外で比べることは採らない。
- 対応: §6.9 の後半（「In `pred_obs` the predicted rows carry the executor's dispatch times, so the difference between the executor's clock and the observation's … adds to the collection delay: a short predicted row, such as the fragment of one key interval after a cut-off, can fail to pair for timing alone. Such a disagreement is counted in `pred_obs` like any other and is not attributed to a cause」）・§7 の予測の項（予測は回収と送出から観測器までの遅れを模さない）。
- 採らなかった: 対にならないことがある長さの下限を数で書くこと・断片の行を試行ごとの数と帰属で比べること。

### N5 [minor] 問 4 の唯一の判定が、打鍵 1 つの欠けか余りで、セル全体ごと消える
- 裏取り: 真（旧 `closed_set.py` の selftest「one missing press stops the run instead of shifting later trials (exit 2)」）。
- 研究者の採否: ブロックの印で合わせ直し、打鍵が計画と合わないブロックの試行は「採点しない」として数え、残りで判定する。closed set と open set の両方。
- 対応: §6.2 の Other contingencies の該当の項・§6.8 の新しい第 2 段落（「Both attacks assign the observed key presses to the trials in plan order, block by block. A block whose observed presses do not agree with the plan … is not scored … resumes at the next block-start marker …」）・§6.8 の表の注（「if blocks are unscored, the rule is applied to the scored trials」）。コード: `closed_set.py` の `marker_categories`・`_is_anchor`・`_next_anchor`・`align_blocks`・`align_plan`・`merge_alignments`・`segment_by_plan`。`open_set.py` も `align_plan` を使う（照合を「数と英字の数」から区分の並びの全体に強めた）。
- メインの実装上の選択: 錨は「印と同じ区分の並びが、ちょうどその長さの連なりで現れる位置」。合わないブロックは自分の印で一度探し直し、だめなら次のブロックの印へ。印が壊れたときは、見つけた錨で次のブロックが丸ごと合えばそこから再開する（損失は原則 1 ブロック）。`--markers-in-obs` が無いときは今までどおり止まる。
- 採らなかった: 送出の記録の試行の時刻で区切ること（合わせ直しは印で行う）。

### N6 [minor] 毎ブロックの最初のかなキーのため、入力ソースのポーリングの経路を通らない
- 裏取り: 真（`driver_macos.rs` のコメントで確かめた。ポーリングの本体は一覧の外で、メインも確かめていない）。
- 対応: §7 の「The input is synthetic」の項（「The input mode is switched only by the kana key at the start of each block, so the observer's other way of following the input mode, polling the input source, is not exercised.」）。

### N7 [minor] `carry_over` の除外が「計画どおりでない試行は除かない」の原則と食い違う
- 裏取り: **部分的に真**（除外としては §6.2 に理由つきで宣言済みだった。原則の明示の例外として書かれていない点が残っていた）。
- 対応: §1.2 の最後の文（「The one exclusion that rests on the input method's behaviour is that of a session carried from one trial into the next (section 6.2), because such a session cannot be assigned to one trial.」）・§6.2 の `carry_over` の項（「This is the only exclusion that rests on what the input method did」）と観測の行の項（「the number of observation rows excluded is reported by reason」）。除いた試行の数は、§6.2 の冒頭のとおり理由・層・数で報告する。
- メインの実装上の選択: 除いた観測の行は `match.py` がすでに `excluded.obs.by_reason` で数えているので、コードは変えず文だけ直した。

### N8 [nit] 節のあいだの食い違いと書き漏れ
- 裏取り: 真。
- 対応: §6.4 の Scopes の最後の段落（問 1 は 3 範囲・問 2 は `under_limit` と `all_trials`〔`over_limit` は §6.6 の Cut-off だけ〕・問 3 は主 `under_limit`・副 `all_trials`）と Comparisons（問 1・2 は 3 つの比較・問 3 は最初の 1 つだけ）・§1.2 の区間の文（区間を付けないものを列挙: F1・数・問 4 の平均順位・§6.3・§6.9・§6.10 の記述の値）。
- **対応していない**: `log_truncated` がどちらのログかを書くこと（§6.2 の項は「a session still open when the log ends」のまま）。メインが直す一覧に載せ漏れた。

### N9 [nit] near chance の表は 1 つの集合の確率で、「粗い集合の最大」の規則を含まない
- 裏取り: 真。
- 対応: §6.8 の表の注（「for the accuracy of one feature set measured over the planned numbers of trials; for a set whose reported accuracy is the maximum over coarser sets as well, the probability is at most this」）。

### N10 [nit] 回収は 1 枠で、2 つが 1 回のポーリングのあいだに閉じると 1 行が失われる
- 裏取り: 真（`ime_compose.rs` のコメント）。
- 対応: §4.4 の最後の文（「such a loss appears as a missed row in `pred_obs`」）・§7 の予測の項。

### N11 [nit] nav の正解は送出の記録
- 裏取り: 真。
- 対応: §6.6 の Navigation（「The true count is the number of arrow presses sent (section 4.3), so this measure compares the observer with the executor, not with the reference input field.」）・題を "a reference input field" に変えた。

## B. round 2 で「部分的に解消／未解消」と判定した round 1 の指摘

### M1（部分的に解消と判定）問 4 の推奨は合成の間隔から決まる
- 研究者の採否: 1 秒のビンも推奨から外す（あなたの解消の条件の 1 つ目）。推奨は `no_time`・`counts_only` だけ。`bin1s`・`bin1s_count` は ms の集合と同じく推定だけを報告する。
- 対応: §6.8 の第 5 段落（「The attack's accuracy on the feature sets that keep any time (`all`, `no_runs`, `bin1s`, `bin1s_count`) therefore cannot be carried over to human logs … The recommendation considers only the two sets that keep no time」）と推奨の段落・§7 の「The input is synthetic」（「finer granularities are not evaluated」）。
- 代償（研究者が承知のうえ）: 推奨する粒度では時刻の指標が残らない。中間の粒度（100 ms・250 ms のビンなど）は評価しない。

### M3（部分的に解消と判定）§6.6 Cut-off の「specified: zero」は正解の側の期間で数える
- 対応: §6.6 の Cut-off を書き直した: `over_limit` の行と予測の行の比較に「specified: the same rows」、どの範囲でも 20 秒以上の行は「specified: zero」。正解の側の 20 秒以上のセッションが対・分割・併合に現れる数は報告するが「it is not specified to be zero, because the ground truth's session can last longer than the observer's」。

### M5（部分的に解消と判定）§7 の `n_continued_commits` で「見える」は過大
- 対応: §7 の基準の規則の項を「The sessions affected are marked by `n_continued_commits`, and the agreement of abandonment is reported separately for them (section 6.6); the other measures are not split by it.」に狭めた。
- 採らなかった: 検出と期間も `n_continued_commits` で分けること。

### m1（部分的に解消と判定）「small」に量が無い
- 対応: §6.1 の区間の段落（「the design effect is at most about 1.8 (an interval at most about 1.34 times wider)」）・§3.3 の連続量の精度（「and at most about 1.34 times that」）。

### m2（部分的に解消と判定）`pilot-macos.md` の 66 ms
- 対応: `pilot-macos.md` の Clocks（22 ms だけなら約 66 ms、回収の遅れ〔最大約 100 ms〕を足すと約 370 ms。長さの違う区間ではもっと小さいずれで対にならない）・§6.9・`notes.md` の同じ文。

### m4（部分的に解消と判定）中止の後のやり直しの順と学習
- 対応: §3.2（「An attempt that has to be repeated (section 3.4) is repeated before the next item of this order is run, so the order is kept; the learning that the repeated attempt added is not undone (section 7).」）・§7 の学習の項（「also through attempts that are repeated」）。

### m5（部分的に解消と判定）焦点を失った試行の観測の行が主の `gt_obs` の偽陽性になる
- 対応: §6.2 の焦点の喪失の項（「the observation rows assigned to them, and how many of these are false positives, are reported with the detection results, so that a failure of the reference is not read as one of the observer」）。コード: `delivery.py` の `_focus_losses` が `trials_with_focus_out` を出し、`pipeline.py` の `_focus_loss` が S15 以外のその試行に割り当たる行と偽陽性の数を、すべての検出の結果の `focus_loss` に入れる。
- 採らなかった: 焦点を失った試行を除いた副の値（数を並べるだけ）。

### m10（部分的に解消と判定）1,000 ms の閾値の根拠
- 対応: §6.2 の `clock_jump`（「The threshold equals the wait between trials, so a step of the wall clock that could move an event into another trial is caught; a smaller step is not excluded, and with network time synchronisation turned off (section 3.2) none is expected.」）。

### m11（未解消・後退と判定）パイロットの生ログを預ける文が消えた
- 研究者の採否: 約束を戻す。封印したパイロットの観測のセッション行は、凍結と本計測の後に預けるためにだけ開け、解析しない（探索にも使わない）。
- 対応: §3.1 の第 1 段落（「The raw logs of its runs that meet the criteria set out there are deposited with the measurement data. The observation logs of the pilot are deposited whole, so their sealed session rows (section 2.5) are unsealed after the measurement only to be deposited; they are not analysed, not even in an exploratory analysis.」）。
- **未解決**: 預ける基準そのものは、まだ `pilot-macos.md` の "Raw logs" に書いていない（測定機での残りの作業）。
- 本計測の預け: `data.md` の手順 4 で、試行の外の行の上限をログごとに分け（観測 4・参照 5 / ブロック）、説明できない run は中止した試みに数える（§3.4 にも同じ文）。

### n3（部分的に解消と判定）解析コードの同一性
- 対応（round 2 から）: §9 に凍結コミットの 40 桁の識別子を登録に載せること・書き出しの根を足した。
- 採らなかった（round 1 から）: 結果のファイルにコミットと dirty の有無を機械で記録し、タグと照合すること。
