# review-R3 — 方法論と再現性の番人（attack-me・prereg・Windows の追補・round 1）

（paper-reviewer・2026-10-03 に返った応答をメインが写した。保存の検査を通してから写す）

総合の推奨: **major（直して再査読）**。最も重いのは、§10 が Windows の観測器のセッションの規則を書かず、書いた説明が実装と違うこと。主要な範囲 `under_limit` の根拠（D3）がその規則に依る。D2 の SHA-256 は §10.5 とコードで一致し、§8 の手続きはおおむね守られている。

## 1. 接地

- G1（Wicherts et al. 2016）"each described step should allow only one interpretation or implementation (it should be precise). Finally, a preregistration should exclude the possibility that other steps may also be taken (it should be exhaustive)."
- G2（Wicherts 2016）"the syntax for the statistical analyses should preferably be created in advance to be run (once) on the collected data to yield the final statistical results."
- G3（Wicherts 2016, D5）"explicates that the stated rules of exclusion will be the only ones that will be used to discard participants (it should be exhaustive)."
- G4（Wicherts 2016）"should describe the complete sampling plan, i.e., the targeted sample size, when the data collection starts and ends" ／ C4 "Determining the data collection stopping rule on the basis of desired results"
- G5（Lakens 2022）"researchers should carefully justify their sample size before data is collected." ／ "collects sufficient data to have an estimate with a desired level of accuracy."
- G6（Koo & Li 2016）"reporting ICC should include the following items: software information, "Model," "Type," and "Definition" selections. In addition, both ICC estimates and their 95% confidence intervals should be reported."

## 2. 評価表

| | 点 | 所見 |
|---|---|---|
| a | 3 | §10.6 と `gt_scope.py` の docstring は観測器が「the input method's composition events」を読むと書くが、実装（`ime_winevent.rs`・`cloak.rs`）が読むのは候補ウィンドウの表示・隠す・cloak の事象。D1・D2 の「macOS は変わらない」は記録の残らない手の確認に頼る |
| b | 2 | Windows の観測器のセッションの規則（開閉・150 ms の畳み込み・20 秒の打ち切りの起点）が無いのに、D3 の範囲は「the observer is specified not to report」を根拠にする。範囲を正解の長さで選ぶことの偏りも書かれていない |
| c | 4 | 計画の SHA・生成の命令・手順書・セルの例がそろう |
| d | 3 | §10.1 は 1 段落に状態・タグの差・3 つの逸脱・同値の主張を詰めている。凍結の前なのに過去形 |
| e | 4 | J6・J9 は §3.3・§6.2 を継いで応える。J11 のとおり規程は追補の書式を定めない |
| f | 3 | 新しい文献が無い。「most current applications are TSF clients」に出典が無い |
| g | 2 | 計画・正解の規則・手順・停止規則は固定。固定されていない: 観測器の Windows の規則・Windows の解析に `data.md` のどの run を並べるか・§9 の SHA の表の扱い・問 5 の Windows の CPU の量の違い・参照の経路の機械の検査 |

## 3. 指摘

- **[major] Windows の観測器のセッションの規則が §10 に無く、書かれた説明は実装と合わない。D3 の根拠はその規則に依る**
  - 位置: §10.6「the Windows observer reads the input method's composition events, and no prediction applies to it」／§10.2「Everything not stated in this section is as registered for the macOS cells.」／D3 Reason「The cut-off at 20 seconds is the same on both systems, so without a scope the primary agreement of a Windows cell would mix the sessions that the observer is specified not to report」
  - 実装: `ime_winevent.rs`:12「A display event opens a conversion session and a dismissal closes it.」（`apply_ime_event` に 20 秒の打ち切りは無い）／`cloak.rs`:4-8（cloak/uncloak を `CloakFold` で畳む）／`ime_cloak.rs`（`MAX_SESSION_MS = 20_000` の起点は候補ウィンドウが出た時刻・`FOLD_GAP_MS = 150`）
  - なぜ: 観測器のセッションは「候補ウィンドウが見えている区間」で、正解の `tsf_start`〜`tsf_end` とは別の構成概念。思考の休止のあいだに窓が 150 ms を超えて消えれば観測器のセッションは閉じて行を出す。そうなる試行を「行を出さないと規定された試行」として外す理由が成り立たない。§6.6 の over_limit の点検の「規定」が Windows で決まっていない。どちらの経路が MS-IME 25H2 で働くかも書かれていない（WinEvent の経路なら打ち切りは 25 秒の安全弁になりうる）。G1。
  - 解消: §10 に Windows の観測器の規則（開閉の事象・2 つの経路とどちらが働くか・150 ms・打ち切りの起点と長さ・`nav` と `abandon`）を書き、D3 の理由をそこから導き直す。打ち切りの起点が窓の表示なら、正解の長さ ≥ 20 s と観測器の打ち切りの重なりを、封をした行を読まずに（例: 参照ログの `ui_begin` / `ui_end`）示す。重ならないなら範囲の定義を考え直し §10.10 に書く。
  - 自信: 中
- **[minor] 逸脱が macOS を変えないという主張の根拠が再現できる形で残っていない**: D1・D2 の Effect の「checked on 2026-10-03」に命令もハッシュも無い。`pipeline.py`:2629-2636 の `_case_windows_cell` はタグとのバイト一致を検査しない。→ 命令・両方のタグで作った計画と結果のファイルの SHA-256 を書く。selftest を根拠にするなら何を検査していないかも書く。自信: 高
- **[minor] §9 の SHA の表が Windows のタグでは手順のファイルについて古くなる。Windows の設定と手順のファイルの SHA が §10 に無い** → §10.5 に Windows のタグでのファイルの SHA の表を足し、§9 の表は macOS のタグのものと 1 文。自信: 高
- **[minor] Windows の解析が `data.md` のどの run を読むか、Windows の計画の手での照合が決まっていない**: §10.1「run from the Windows tag with `experiment/run.sh`」・`run.sh`:97・`data.md` 手順 1「(live conversion on or off)」。macOS の run も並べれば Windows のタグのコードで macOS の 2 つ目の結果ができ、どちらを報告するかが分岐になる（G2）。→ Windows のタグの解析には Windows の run だけを並べる（または Windows のタグで出た macOS の結果は報告しない）と書く。`data.md` の手順に §10.5 の SHA を足すことを約束する。自信: 中
- **[minor] D3 の範囲は比べる片側（正解）の値で選ぶ。代わりの指標の裏づけが薄い**: §6.4 は範囲を「decided from the oracle and the plan alone」としていた。20 秒の近くで `dwell_ms` の偏りが選択で歪みうる。617 との一致の根拠は長い試行 10 件 × 2 run（同じ計画なら実質 10 件）。→ 20 秒の付近（例 ±500 ms）の試行の数を報告すると書く。計画の時刻による定義で副次の解析を出すかを 1 つに決める。2 つの run の計画（seed）が同じかを書く。自信: 中
- **[minor] Windows の n と精度が層ごとに示されていない**: 層ごとの表・50 未満の層の数・Windows の計画の Σm²/Σm が無い（G5）。→ §3.3 と同じ形の表と `plan_figures` 相当の値と命令を足す。自信: 中
- **[minor] 問 5 の Windows の条件で、量の定義の違いと 0 の扱いのあとの手続きが §10.8 に無い**: `kit/e3/README.md`:38「a sample of about one second taken at the reading instant」・:65-68「a counter that cannot be read also gives a zero … the flag asks for a check and is not a verdict」。→ 量の定義の違いと、`cpu_all_zero` が立ったときの扱いを固定する。自信: 高
- **[minor] 所要時間の見積もりが直した手順の実測を使っていない**（§10.5「6% above」は直す前の 14.1/13.3。直した後は 15.2 s）。→ 直した後の比でも見積もる。自信: 中
- **[minor] 参照の経路（TSF）を機械で検査していない**: `pipeline.py`:899-900 は os と計画の SHA だけを見る。IMM の run は k = 0 の規則でたまたま捕まるだけ。→ gt のヘッダの `src` が `win_tsf` でない run は解析しないと §10.7 に書く（またはコードで検査）。自信: 中
- **[nit] §10.1 が §8 の範囲の外の変更を列挙しきっていない**（`notes.md`・`generate_plan.py` のコメント・`make_synthetic_run` と selftest）。自信: 中
- **[nit] 凍結の前の文書が過去形**（§10.1「It was written and frozen」「were replaced」）。凍結の commit で事実にする書き方なら可。パイロットは「measurement」に入らないと明記。自信: 高
- **[nit] 再現の手順の細部**: §10.5 は `python3`、README.windows.md は `python`。LF の確保の手順・照合した 2 つの Python の OS が書かれていない。自信: 高
- **[nit] パイロットの封をした行の扱いと run の数え方**: §10.9 は Windows のパイロットの封をしたセッションの行を「not even in an exploratory analysis」と明記していない。§10.6 の「39 of 39 in each of three runs」は IMM の run を含む。自信: 中

確かめて問題が無かった点: `REGISTERED_PLAN_SHA256_WINDOWS`（`pipeline.py`:260）は §10.5・D2 と一致。`plan_config.windows.json` は `_note` 以外で macOS と同じ値。`cancel_converted` は windows 3・macOS 2。D1・D3 は観測器の行を封じたまま参照の側だけで決めた（結果を見て選んだ分岐ではない）。`sha256:` が変わらないことは §9 の定義と整合。

## 4. 総合: major

計画・逸脱の記録・D2 の照合は凍結の水準に近いが、主要な範囲の根拠（D3）が §10 に書かれていない観測器の Windows の規則に依り、その説明は実装と食い違う。規則を書き、D3 の理由と §10.10 を直したうえで再査読を。

## 5. 読めなかった範囲・注入の疑い

読んでいない: `preregistration.md` §6.5〜§6.8・§7。第 1 群の `env.md`・`notes.md`・`pilot-macos.md`・`kit/run/README.md`・`kit/gen/README.md`・`recipes*.json`・`keymap_windows.json`・`kit/emit/README.md`・`refinput-windows/README.md`・`logger/README.md`・`pilot/README.md`・`e2/README.md`。第 2 群の `match.py`・`l1.py`・`delivery.py`・`run_cell.py`・`focus_windows.py`・`away_windows.py`・`start_windows.py`・`backend_windows.py`・`closed_set.py`・`tsf.rs`・`refinput_tsf.rs`・`keyboard.rs`。`gt_sessions.py` は Grep だけ、`ime_cloak.rs`・`cloak.rs`・`ime_winevent.rs`・`pipeline.py` は一部。注入の疑い: なし。一覧の外のファイルは開いていない。
