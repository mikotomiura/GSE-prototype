# carryover-R2 — round 2 からの引き継ぎ（R2: 打鍵記録を使う書字研究の利用者・公開の安全の立場）

作成: 2026-10-02（メイン）。あなた（R2 の立場）の round 2 の新しい指摘 12 件（major 3・minor 6・nit 3）と、round 2 であなたが「部分的に解消／未解消」と判定した round 1 の指摘 6 件について、メインの裏取り・研究者の採否・対応・未解決を書く。
⚠️ **再掲を求めない**。各指摘が今の版で**解消したか**を 1 件ずつ判定してから（解消 / 部分的に解消 / 未解消・理由 1 行・今の版の位置）、**今回の直しが作った新しい穴**を探してほしい。round 2 で「解消」と判定した指摘は引き継がない（変わっていない節は round 2 の判定のまま）。
「採らなかった」部分は研究者の選択（またはメインの選択）で、理由を添えた。その理由が成り立たないと考えるなら、新しい指摘として根拠つきで書いてよい。

## 版の変化（round 2 の版 `384712ee` → 今の版 `abc5d7f9`）

- 節番号は変わっていない。round 2 の行番号は使えない（本文は 9,326 語から 11,217 語に増えた）。変わった節とコードの関数は context-A の「round 2 から変わった箇所」。
- 読んでよいファイルの一覧は round 2 と同じ（増減なし）。

## A. round 2 の新しい指摘

裏取りの判定は、メインがコード・計画・事前登録で確かめた結果。12 件すべて「真」。

### 新 1 [major] 1 秒のビンの集合を推奨に残したことが、ms の集合を外した理由と矛盾する
- 裏取り: 真（論理。§6.8 自身が「Pauses between words and phrases … are not modelled either」と書いていた）。
- 研究者の採否: 解消の条件 (a) を採る。推奨は `no_time`・`counts_only` だけ。`bin1s`・`bin1s_count` は ms の集合と同じく推定だけを報告する。(b) の語や文節の境に休止を置く合成の条件は足さない（計画の変更になる）。
- 対応: §6.8 の第 5 段落（「The attack's accuracy on the feature sets that keep any time (`all`, `no_runs`, `bin1s`, `bin1s_count`) therefore cannot be carried over to human logs … A 1-second bin removes the timing of key pairs … but keeps pauses of a second or more, which in human logs fall at the boundaries of words and phrases. The recommendation considers only the two sets that keep no time (`no_time`, `counts_only`).」）と推奨の段落（「The recommended granularity is the most detailed of the two sets considered that is near chance in this sense (`no_time`, of which `counts_only` is a coarsening)」）・§7 の「The input is synthetic」（「finer granularities are not evaluated」）・`kit\e2\README.md`。
- 代償（研究者が承知のうえ）: 推奨する粒度では時刻の指標が残らない（下の B の minor-5 は未採用のまま）。

### 新 2 [major] 打鍵が 1 つ欠けるだけで、E2 の推奨が丸ごと消える
- 裏取り: 真（旧 `closed_set.py` の selftest「one missing press stops the run instead of shifting later trials (exit 2)」・旧 `open_set.py` は数と英字の数が違えば割り当てを拒む・`data.md` 手順 4 は余分な行だけを検査）。
- 研究者の採否: ブロックの印で合わせ直し、打鍵が計画と合わないブロックの試行は「採点しない」として数え、残りで判定する。closed set と open set の両方。
- 対応: §6.2 の Other contingencies の該当の項・§6.8 の新しい第 2 段落（「A block whose observed presses do not agree with the plan (a press missing, added or changed) is not scored: its trials are counted as unscored, and the assignment resumes at the next block-start marker … Accuracies and error rates are over the scored trials, and the numbers of unscored blocks and trials are reported per cell.」）・§6.8 の表の注（「if blocks are unscored, the rule is applied to the scored trials」）・試行数の文（「when every block is scored」）。コード: `closed_set.py` の `align_blocks`・`align_plan` ほか、`open_set.py` も同じ合わせ直しを使う（照合を区分の並びの全体に強めた）。
- 採らなかった: 預ける前に、配送の報告で入力モード以外のキーの到達を確かめる関門（`data.md` の手順 4 は今も余分な行だけを検査する）。欠けは採点しないブロックとして数えて報告する。

### 新 3 [major] 問 3 の主の値がこの設計の思考時間の分布で決まる
- 裏取り: 真（ライブ変換 ON の slow で、打ち切られるセッションに打鍵が入る試行は新しい定義で 447 / 1,050）。
- 研究者の採否: 解消の条件 (a) を採る。問 3 の主を `under_limit` にし、`all_trials` は「この設計の打ち切り率に依存する副」として出す。打ち切りは決定的な規則として示す。
- 対応: §6.4 の Scopes の最後の段落（「Question 3 is answered under `under_limit` (primary) … and under `all_trials` (secondary). The values under `all_trials` depend on this design's fraction of long trials … a session of 20 seconds or more has no row, and a letter or digit pressed after the cut-off opens a fresh session.」）・§6.4 の Comparisons（問 3 は `gt_obs` だけ）・§6.7 の冒頭・§1.2 の最後の段落・§7 の打ち切りの範囲の項・`pipeline.py` の `PRIMARY`・`L2_SCOPES`・`PRIMARY_NOTE`・`notes.md`。
- 採らなかった: (b) の L2 を `gt_pred` でも計算すること。
- 関連する定義の変更: `long` は「打ち切られたセッションに、その試行の打鍵が 1 つでも入った試行」に広げた（§4.5。持ち越したセッションが後の試行で打ち切られる場合を含む）。§3.1・§3.3 の数は計算し直した。

### 新 4 [minor] 推奨の文は「ログ」と書くが、セッションの行を出さないときにしか成り立たない
- 裏取り: 真。
- 対応: §6.8 の推奨の段落（「The recommendation concerns the key rows of a log published without its session rows: the session rows carry their times and durations in milliseconds, were not given to the attacks, and could undo the coarsening of the key rows, so publishing them is not evaluated.」）。

### 新 5 [minor] ブロック内の依存についての論理が逆向きで、表が前提を書いていない
- 裏取り: 真（独立を仮定した Wilson の上端は、相関があると低すぎ、near chance に通りやすい）。
- 対応: §6.8 の最後の段落（「Dependence within a block would widen the interval and make the rule easier to meet; it is expected to be small, because the key rows of a trial follow from its own phrase and procedure, and the phrase, intervals and decoys of each trial are drawn independently, but it is not ruled out, and the block-resampled interval is reported next to the Wilson interval for this reason」）・表の注（1 つの集合の確率・最大で報告する集合では上限）・§7 の新しい項「Intervals that treat trials as independent」。コード: `closed_set.py` の `evaluate` に `--bootstrap`（既定 2,000）と、ブロックで再標本した正解率の区間（記述・最大は再標本ごとに取り直す）。
- 採らなかった: 判定の規則そのものをブートストラップの上端や設計効果で広げること（規則は Wilson の上端のまま。ブロックの区間は記述として並べるだけ）。

### 新 6 [minor] 試行ごとの差を使った重み付けし直しが、繰り越しのために成り立たない
- 裏取り: 真。
- 対応: §6.7 の第 2 段落の最後（「These differences include sessions carried over from an earlier trial, so they are reported twice: over every trial of the scope, and over the trials of the scope in none of the layers of section 6.4, for which reweighting to another mix of scenarios is meant.」）。コード: `l2.py` の `per_trial` の `only_trials`・`per_trial_layer_none`・`match.py` の出力の `scope` の `layer_none_trials`。

### 新 7 [minor] n の根拠が、主の範囲に合わせて書き直されていない
- 裏取り: 真。
- 研究者の採否: n は変えない。言えることを設計に合わせて書き直す。
- 対応: §3.3 の Trials（n を決めた順序と、打ち切りが分かった後も見直さなかったこと・1 晩は副の根拠）・精度の表（最小の行を、S6・S13 以外で主の範囲の最小の層 31 に）・表の後の段落（31 試行で約 9 点・主の範囲の速さごとの n）・打ち切りの下に残る試行の表の後（「Outside S6 and S13, six strata of each cell (all slow) hold fewer than 50 trials.」）。
- 採らなかった: slow の n を増やす・思考時間の幅を狭める。

### 新 8 [minor] open set の結果が推奨とどう関わるか決まっていない
- 対応: §6.8 の Open set の最後（「The open set does not enter the rule above; its results are reported next to the recommendation, as a second view of what the letter-run lengths that `no_time` keeps reveal.」）。
- 採らなかった: open set の結果で推奨を止める規則。

### 新 9 [minor] 「連続量にはすべて区間を付ける」に例外が書かれていない
- 裏取り: 真（旧 `l2.py` の `mixture_bias` は点だけ、`_agree` の偏りと一致の限界も点だけだった）。
- 研究者の採否: `l2.py` に区間を足す。
- 対応: §1.2 の区間の文（区間を付けるもの: 問 1〜3 の一致の推定と問 4 の正解率・誤り率／付けないもの: F1・数・問 4 の平均順位・§6.3・§6.9・§6.10 の記述の値）・§6.1 の区間の段落・§6.7（偏りと一致の限界に区間・混合の偏りは速さごとにブロックを再標本した区間）。コード: `l2.py` の `_agree`・`_ba_interval`・`mixture_bias`・`_stratified_replicates`。

### nit 1 試行の外の行の上限が、観測のログには甘すぎる
- 対応: `data.md` の手順 4（観測は 1 ブロック 4〔マーカー〕、参照は 5〔マーカーとかな〕）。説明できない run は中止した試みに数える（§3.4 にも同じ文）。

### nit 2 速さごとの正解率が無い
- 対応: §6.8 の Reported に「the accuracy per scenario and per speed」。判定はプールのまま。`closed_set.py` に `by_speed`。

### nit 3 冗長さ（打ち切り・配送・合成の間隔の説明の重複）
- **対応していない**（任意として承認された一覧の項目で、メインが今回は手を付けなかった）。本文は 9,326 語から 11,217 語に増えた。

## B. round 2 で「部分的に解消／未解消」と判定した round 1 の指摘

### major-1（部分的に解消と判定）→ 上の新 1 で対応。
### major-3（部分的に解消と判定）→ 上の新 4 で対応。セッションの行を公開する形（丸める・削る）を決めることは round 1 から採っていない。
### major-4（部分的に解消と判定）
- (ii) は上の新 3 で変わった（問 3 の主は `under_limit`）。
- 採らなかった（round 1 から）: (iii) L2 の偏りを「打ち切りの分」と「それ以外」に分けること・中央値か対数の平均の変換時間を足すこと。
### major-5（部分的に解消と判定）→ 上の新 6 で対応。
### minor-5（未解消と判定）中間の粒度と、粒度ごとに計算できる書字の指標
- **対応なし**（round 1 から研究者の承認した一覧に入っていない）。§7 に「finer granularities are not evaluated」とだけ書いた。新 1 の対応で、推奨の粒度では時刻の指標が残らないことは承知のうえ。
### minor-7（未解消と判定）パイロットの生ログを預ける基準と、事前登録から落ちた約束
- 研究者の採否: 約束を戻す。封印したパイロットの観測のセッション行は、凍結と本計測の後に預けるためにだけ開け、解析しない（探索にも使わない）。
- 対応: §3.1 の第 1 段落（「The raw logs of its runs that meet the criteria set out there are deposited with the measurement data. The observation logs of the pilot are deposited whole, so their sealed session rows (section 2.5) are unsealed after the measurement only to be deposited; they are not analysed, not even in an exploratory analysis.」）。
- **未解決**: 預ける基準そのものは、まだ `pilot-macos.md` の "Raw logs" に書いていない（測定機での残りの作業）。
