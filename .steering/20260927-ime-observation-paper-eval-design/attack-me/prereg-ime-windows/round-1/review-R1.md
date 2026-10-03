# review-R1 — 計測の道具の検証（attack-me・prereg・Windows の追補・round 1）

（paper-reviewer・2026-10-03 に返った応答をメインが写した。保存の検査を通してから写す）

総合の推奨: **major（直して再査読）**。計画・手順・規則ファイルの SHA-256 と D1・D2 はよく固定されている。追補の芯の 2 点（Windows の観測器が何をセッションとし 20 秒の打ち切りをどこから数えるか〔指定〕が無い・D3 の「長い試行」がその打ち切りと同じ規則でない）が凍結に足りない。パイロット報告の数に文書の中で整合しないものがある。

## 1. 接地

- S1 Plant (2016)「In closing I would propose that researchers self-validate their own timing accuracy using external chronometry (e.g., using a Black Box ToolKit or oscilloscope) and state confidence intervals on publication.」／「The only way to be sure of timing accuracy is to check it when paradigms are running in-situ, on the experimenter's own equipment, at the time a given study is carried out.」
- S2 Plant (2016)「Generalization across apparently similar hardware types or categories of study is folly.」
- S3 Plant (2016)「the software or script being run can know nothing of the errors introduced by the hardware, rendering engine, or plug-in.」／「a growing trend toward "checking" timing accuracy by proxy」
- S4 Plant (2016)「benchmarking various experiment generators using idealized equipment and simplified scripts is counterproductive, lulls researchers into a false sense of security, and is unrepresentative of what they do and may achieve in the field.」
- S5 Pinet et al. (2017)「A crucial and original feature of the present study is the use of three distinct keys from the keyboard, and the generation of variable delays between keys, just as it happens in actual experiments involving sequence production.」／「The programmed keystroke times were compared to those recorded through the jsPsych procedure.」
- S6 Bridges et al. (2020)「comparisons across packages are no replacement for testing the timing on the system being used」／「most of them should be detectable in your software log files, which you should also check as a part of your testing process.」
- §7 の外部の時計を使わない理由（「an external timing device would time the path of the keys, not the conversion」）は筋が通るので、S1 は「基準が観測器から独立しているか、指定と同じものを測っているか」の物差しとして使う。

## 2. 評価表

| | 点 | 所見 |
|---|---|---|
| a | 3 | §10.6・D3・`gt_scope.py` の「composition events」はコード（IME の窓の表示・消去・cloak）と違う。D3 の「the cut-off at 20 seconds is the same on both systems」は起点・契機・経路が違うので言い過ぎ。D3 の根拠は 20 試行（10/10×2） |
| b | 2 | Windows の観測器の指定が無く、`over_limit` の「as specified」の拠り所が無い。D3 は主要な範囲を基準の測定値で条件づける（§6.4「decided from the oracle and the plan alone」）。境界の近くの扱いも無い |
| c | 4 | `README.windows.md`・`start_windows.py`・S4/S8/S15 の所見・IMM と TSF の確定の時点の違い（S7）は再利用できる |
| d | 3 | §10.2「Everything not stated in this section is as registered for the macOS cells」が macOS 固有の記述（§1.1・§6.4 の over_limit の指定・§7 の入力モードのキー・§6.9 の 22 ms）を持ち込む。置き換わるものの一覧が無い |
| e | 4 | J9 は §6.2 の継承で満たす。J6 は n = 75 と範囲の下の層（30〜75）。J11 は規定なし |
| f | 3 | TSF・IMM・WinEvent の挙動の根拠はパイロットの所見だけ |
| g | 2 | 1 通りに決まっていない: 観測器の指定・長い試行と観測器の打ち切りの対応・主な定義（`windows_def` か `all` か）・手順書とセルのファイルのパスの基準 |

## 3. 指摘

- **[major] Windows の観測器の「指定」が追補に無く、§6.4 の macOS の指定が一括で継承されてしまう**
  - 位置: §10.6「the Windows observer reads the input method's composition events, and no prediction applies to it.」／§10.2「Everything not stated in this section is as registered for the macOS cells.」／§6.4「For these trials the specified behaviour is that the session that is cut off produces no row; a letter or digit pressed after the cut-off opens a fresh session」／D3
  - コード: `ime_winevent.rs` 1–4 行（IME の**窓**の事象）・`apply_ime_event` に打ち切りが無く HIDE で必ず dwell を書く（82–91 行）。`ime_cloak.rs` は cloak を 150 ms で畳み、`MAX_SESSION_MS` を `on_tick` で判定して `forced: true` で行を出さない（292–305 行・`cloak.rs` 256–267 行）。
  - なぜ: 観測器のセッションは IME の窓が見えている区間。打ち切りはタイマーが契機で、経路によっては無い。§6.4 の「a letter or digit pressed after the cut-off opens a fresh session」は Windows で成り立たない。指定が無ければ Q2 の「does the observer write no row, as specified?」と `over_limit` を何に照らすか決まらない（S3）。`dwell_ms` の定義も正解（`tsf_start`→`tsf_end`）と違い、Bland–Altman の偏りに混ざる。
  - 解消: §10 に Windows の観測器の指定を §1.1 と同じ粒度で（2 経路と切り替えの条件・150 ms・20 秒の起点〔窓の表示〕と契機〔タイマー〕と行を出さないこと・WinEvent の経路に打ち切りが無いこと・`nav`・`abandon`）。§10.6・D3・`gt_scope.py` の誤記を直す。§6.4 の over_limit の指定のうち Windows で置き換わる文を明記。
  - 自信: 高
- **[major] D3 の「長い試行」が観測器の打ち切りと同じ規則ではなく、主要な範囲を基準の測定値で条件づける**
  - 位置: D3「For a Windows cell a trial is now long when a ground-truth session assigned to it lasts at least `limit_ms`」「The cut-off at 20 seconds is the same on both systems」／§10.10／`gt_scope.py` 34–40 行／§6.4「The scope is decided from the oracle and the plan alone, so it does not depend on the observation.」
  - なぜ: (a) 観測器の 20 秒は窓の表示から、正解は `tsf_start` から数え、起点がずれる。(b) `on_tick` は畳み込みの待ちの最中にも上限を先に判定する（`ime_cloak.rs` 295 行）→ 窓が 19.85〜20.0 秒で消えたセッションも行を出さず、正解では 20 秒未満なので `under_limit` に残り「見落とし」に数えられる。(c) WinEvent の経路なら 20 秒を越えても行が出て、`over_limit` で「指定に反する行」に見える。(d) macOS の範囲は両方の測定から独立していたが、D3 は参照の測定値（`tsf_end` の遅れ・取りこぼし・分割）が範囲を動かす。根拠は 20 試行（S2）。範囲の作り方の分岐は計画のヘッダの `os` で決まり（`pipeline.py` 804–805 行）、観測を見て選べる分岐ではない（良い）。
  - 解消: (i) 観測器の指定に合わせて「長い」を定義し直す、または (ii) 正解による定義を主にしたまま、計画上の長さ（presses span ≥ 20 s）による範囲を副次として事前に指定し、2 つの定義で分類の違う試行の数と境界の帯（例 19–21 s）の数を層ごとに報告する。「same on both systems」を置き換える。
  - 自信: 中
- **[minor] `pilot-windows.md` の数が文書の中で整合しない**: 「The TSF field received 3 to 16 key-downs per run in all, against 1,174 to 3,900 presses sent.」は、印（1 ブロック 4 回）と S15 の Return を足すと下限・上限と合わない。「1,174」は 39 試行の run（約 1,464〜1,470）と合わず、macOS の「1,174 of 1,180」と同じ値。「3,882 of 3,900 (pilot-*)」と「(corrected runs)」は 1 run あたりか合計か曖昧。→ 何を数えたか（印を含むか）を明記し run ごとの表に。1,174 の出どころを確かめる。「each」と書く。`delivery.py`・`reach.py` のどの欄かを書く。自信: 中
- **[minor] Windows で主にする定義（`windows_def` か `all` か）が 1 通りに決まっていない**: §10.6「both it and the common definition are reported, as on macOS」と §5「the results under `all` are not otherwise reported」が矛盾。長い試行は `all` から作る。→ 主な定義を名指しし、もう一方の扱いと範囲が `all` から作られることを明記。自信: 高
- **[minor] 正解の組み立てが TSF の「編集の終わり」の観察から導いた状態であり、その人工物が報告されない**: `tsf.rs` 83–90 行「If the start offset or the range count changes while a composition is already active … `result_len` is omitted on this synthetic end」・102–111 行（末尾の差から `result_len` を推定）。合成の境界を作り出したもの・末尾が読めない確定は「取消」になる。§7 の第 1 項の理由は macOS の参照の文。→ `result_len` の無い `tsf_end` の数を層ごとの診断として登録し、§10.10 に限界として書く。自信: 中
- **[minor] `cell.windows.json` のパスが手順書の基準と合わない**（README.windows.md と cell.windows.json・§9）。§10.5 の `python3` と README の `python` も揃える。自信: 中〜高
- **[minor] 外からの押下の規則が Windows ではほぼ盲目になる帰結が限界の記述で止まっている**: 参照に人が打った文字は IME が消費し理由 3 に掛からず、焦点も失われないので理由 4 にも掛からない → 正解に余分なセッションが入り、観測の送っていない打鍵の行は観測器の結果として残る。macOS では閉じていた非対称。→ (i) Windows だけ、観測のキーの行のうち送っていない押下に当たるもの（試行の中）を閉じた規則として数え報告する（中止に使わなくてもよい）、または (ii) その数を delivery の報告で必ず示すことと、預ける生ログに人の打鍵が残りうることの扱いを §10.10 に。自信: 中
- **[minor] 時計の差と所要時間の、パイロット（最長 27.5 分）から 12 時間への外挿**: ずれの傾きは 3 点（約 25 分）から。12 時間に伸ばすと最大約 130 ms。6% は修正前の手順（14.1 vs 13.3 s）から。§6.9 の 22 ms は macOS の値。→ Windows の時計の差（観測−参照を含む）を §10 に、傾きは 3 点からと明記、修正後の比を示す、§6.9 の報告を Windows で確かめる文に。自信: 中
- **[minor] 合成入力の代表性: S14 のキー・S4 の Escape の回数・送出の経路**: `VK_IME_ON/OFF`（`keymap_windows.json`「"ime_on": {"vk": 22}, "ime_off": {"vk": 26}」）は人が押す「半角/全角」と別の仮想キー。継承した §7 の文は macOS のまま。S4 は 2 回目と 3 回目の取消が混ざり正解の終わりと dwell が 1 打鍵間隔違う（2 回目の場合は観察されていない）。Windows では手打ちと送出の比較の報告が無い（S5）。→ §10.10 に S14 のキーの限界を、S4 を「何回目の Escape で取消が起きたか」で分ける診断を、`SendInput` と手打ちの比較をしていないことを限界として。自信: 中
- **[minor] §10.1 の変更の一覧がタグの差と一致しない。結果ファイルに矛盾する注記が残る**: `notes.md`・`make_synthetic_run` の `os_name`・selftest が §10.1・D2・D3 に無い。`pipeline.py` 49–50 行「A plan for another system has no prediction: only gt_obs under all_trials is run.」・781–782 行・`PRIMARY_NOTE` が D3 と矛盾。→ §10.1 に試験だけの変更と notes.md を加える。docstring を直す（`PRIMARY_NOTE` を変えないならその旨を `note_windows` に）。自信: 高
- **[minor] 観測器が Windows で行を 1 つも出さなかった場合の扱いが書かれていない**: `pipeline.py` 33–36 行「a run that has ground-truth sessions but no "ime_shadow" row at all is then refused」。MS-IME で観測器の経路が働くかは計測の前に誰も知らない（良い盲検）。→ 行が 0 の場合を「測っていない」か「recall 0」か、事前に決める。自信: 低
- **[nit]** §10.1 の過去形は凍結の前は事実でない／§10.6「39 of 39 in each of three runs」は `verify-imm` を含む（`win_tsf` の根拠は 2 run）／README.windows.md の「four runs before」と `pilot-windows.md` の「in the pilot runs」（toolcheck の前は 6 run）が合わない。

## 4. 総合: major

1. 計画・手順・規則・停止規則の設定は固定され、D1・D2 は理由と影響が十分。2. Windows の観測器の指定が無く、D3 はその打ち切り（窓の表示から・タイマー・経路で違う）と同じ規則ではない。3. パイロットの数に文書の中の矛盾。直した後に再査読。

## 5. 読めなかった範囲・注入の疑い

読んでいない: `preregistration.md` 780–933 行と References、`notes.md`・`data.md`・`env.md`・`pilot-macos.md`・`run.sh`・`config.json`・`SEED`・`plan_config.macos.json`・`recipes*.json`、kit の README（gen・emit・refinput-windows・logger・pilot・e2・e3）、`match.py`・`l1.py`・`delivery.py`・`generate_plan.py`・`run_cell.py`・`focus_windows.py`・`away_windows.py`・`start_windows.py`・`closed_set.py`・`refinput_tsf.rs`。`pipeline.py`・`gt_sessions.py`・`tsf.rs`・`ime_cloak.rs`・`cloak.rs`・`keyboard.rs`・`backend_windows.py` は該当の箇所だけ。接地は Plant 150–299 行と grep・Pinet 120–239 行と grep・Bridges は grep の断片。注入の疑い: なし。一覧の外は開いていない。
