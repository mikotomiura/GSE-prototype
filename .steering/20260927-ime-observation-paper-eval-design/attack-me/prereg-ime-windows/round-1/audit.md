# audit — 意図の監査役の応答（attack-me・prereg・Windows の追補・round 1）

（paper-reviewer・2026-10-03 に返った応答をメインが写した。保存の検査を通してから写す）

## 意図の監査の結果（prereg・Windows の追補・round 1）

読んだもの: context-B の意図の資料（requirement.md 全体、design.md の §0・1.1a・1.1b・§6、decisions.md の判断 131〜139）。対象物は preregistration.md の Status・§8〜§10、deviations.md、pilot-windows.md、README.windows.md、cell.windows.json、plan_config.windows.json、data.md、notes.md と env.md（grep のみ）、run.sh（grep のみ）。コードは gt_scope.py の全体、pipeline.py の 250〜274・780〜829・890〜990 行と grep の当たり、match.py の 100〜159 行と grep の当たり、generate_plan.py の 913〜976 行と grep の当たり、start_windows.py の全体。

全体の見立て: 持ち帰り 1〜3 と既知の限界 7 件は、ほぼすべて §10・deviations.md・pilot-windows.md のどこかに届いている。食い違いの重いものは 2 つ。(a) 1 つの `data.md` で macOS のタグと Windows のタグの 2 つの解析を回す運用が成り立つか、(b) 公開物の中の文の矛盾（Python の呼び名、セルのファイルのパス、pipeline.py の古い docstring と注記）。

### 1. 意図にあって対象物に無いもの

- **1-1** 「IMM の run は凍結の k = 0 では中止に当たる」が §10 に無い。§10.9 "`kit/analysis/delivery.py`, in its registered form, caught none of these runs (with the settings stated in `experiment/pilot-windows.md`)" は「登録の形で 7 本すべてが通った」と読める。IMM の 3 本は k = 1・モードのキーを数える版で通した（pilot-windows.md 156〜158・187〜189 行）。
- **1-2** 問 3 の並べ替えの見方（§6.7 822〜825 行 "over the trials of the scope that are in neither the carried-out nor the received-carry layer of section 6.4, for which reweighting to another mix of scenarios is meant"）が Windows で null になる（gt_scope.py 50〜51 行・pipeline.py 825〜828 行）ことを §10.6 と D3 が名指ししていない（"the prediction's layers are not computed for this cell" だけ）。正解の側の持ち越しの判定を使うかも決めていない。
- **1-3** 持ち帰り 3 の「合成入力」が §10.10 に無い（§7 の参照で足りる・軽い）。
- **1-4** §10.3 "The versions at the time of the run are recorded in `experiment/env.md`" だが env.md の Windows の行は空（計測の時点で埋める前提）。

### 2. 対象物にあって意図に無いもの

- **2-1** `windows_def` が実質 `all` と同じになること（§10.6・pilot-windows.md 80〜83 行）が限界として扱われていない。主張 C2（design §0）の「候補窓が出た変換」の母数の読み方が変わる。
- **2-2** 所要時間: §10.5・pilot-windows.md 174〜175 行 "about 12 hours"（11.2 h × 1.06）。判断 138 は約 11.5 時間。1.06 は凍結の手順の `pilot-*`（14.1 対 13.3 s）から取ったが、直した手順の run は 15.2 s/試行（167 行）。
- **2-3** 「Romaji input」（§10.2・pilot-windows.md 19 行）を読んだ記録が判断に無い（判断 135 は「まだ読んでいない」のまま）。
- **2-4** §10.3 "with automatic updates, network time synchronisation, sleep, screen lock and the screen saver turned off, and the runner's terminal is not elevated" はパイロットで確かめた範囲（スリープ・画面オフ・スクリーンセーバー）より強い。未来の約束なら状態を述べる形になっている。
- **2-5** §10.1 の変更の一覧（網羅に読める）に `experiment/notes.md` が無い。

### 3. 対象物の中の矛盾

- **3-1（重い）** Python の呼び名: §10.5 は `python3`、README.windows.md 30 行は `python`、cell.windows.json の `focus_cmd` は `"python"`。run.sh 37〜38 行 `PY="python3"` / `command -v python3 >/dev/null 2>&1 || PY="python"` は Store のスタブで `python3` を選ぶ。§10.1 "The analysis of the Windows cell is run from the Windows tag with `experiment/run.sh`"。
- **3-2（重い）** README.windows.md 16〜17 行 "Run every command from the top directory of the published materials (the paths in `cell.windows.json` are relative to it)" だが cell.windows.json 13・18・25 行は `"papers/ime-observation/kit/..."`（repo の根から）。手順 3 はパスを直すことに触れない。書き出しがパスを書き換えるかは確かめていない。
- **3-3** pipeline.py 781〜782 行の docstring "Without a prediction (a Windows plan) only gt_obs over all_trials is run." は古い。959 行がすべての結果に `PRIMARY_NOTE`（262〜263 行 "A cell without a prediction … has the comparison gt_obs and the scope all_trials only"）を入れ、973〜974 行が Windows で `note_windows` を足す → 食い違う 2 つの注記が並ぶ。
- **3-4** README.windows.md 59〜60 行 "an earlier version of it in the four runs before" と pilot-windows.md 60 行 "with it (and with an earlier version of it in the pilot runs) no run was refused"・表の 6 本が合わない。
- **3-5（重い）** run.sh（97 行）は `data.md` の `- run_dir:` をすべて読む。macOS のタグの pipeline.py は Windows の run を `_plan_matches_cell` で拒み、InputError で解析全体が止まる（940〜942 行）。1 つの `data.md` に両 OS の run が並ぶと macOS のタグからの解析は回らない。Windows のタグから回すと macOS の run も D2・D3 のコードで解析される。分け方が書かれていない。
- **3-6** data.md 44〜45 行 "check by hand that the plan's SHA-256 is the one that section 2.4 of the pre-registration gives the cell (live conversion on or off)"。Windows では §10.5 を見ることを §10 が明示していない。
- **3-7（軽い）** gt_scope.py 37〜38 行は開いたままのセッションと試行に属さないセッションを数えない。§10.6・D3 の定義に書かれていない。

意図どうしの矛盾: なし（判断 136 が最終の意図で §10.3 と合う・sha256 が同じになることは §10.1 と合う）。§10.1 の過去形は凍結の commit で事実と合うかを確かめること。

### 読んでいない範囲

preregistration.md の §1〜§7（§2.3 の S9 の行・§6.7 の 815〜830 行・見出しを除く）。pipeline.py の上の範囲以外。match.py・generate_plan.py の上の範囲以外。開いていない: recipes*.json・focus_windows.py・away_windows.py・run_cell.py（grep 1 回）・backend_windows.py・delivery.py・gt_sessions.py・l1.py・closed_set.py・Rust のすべて・gt_rules.json・config.json・SEED・plan_config.macos.json・pilot-macos.md・kit の各 README（run/README.md は grep のみ）。notes.md・env.md・run.sh は grep のみ。design.md・decisions.md は指定の範囲だけ。

### 注入の疑い

なし。
