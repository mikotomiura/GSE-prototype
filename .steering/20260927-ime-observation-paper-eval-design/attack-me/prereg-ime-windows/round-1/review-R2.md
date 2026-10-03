# review-R2 — 書字研究の利用者と公開の安全（attack-me・prereg・Windows の追補・round 1）

（paper-reviewer・2026-10-03 に返った応答をメインが写した。保存の検査を通してから写す）

総合の推奨: **major（直して再査読）**。主な理由は 3 つ: Windows の観測器が何を測るかを §10 が書いていない／問 4 の判定規則が Windows のセルをどう扱うか決まっていない／人の打鍵が入った run を TSF の規則では見逃せる。

## 1. 接地

- G1 Conijn et al. (2019) l.803-805 "caution should be taken when generalizing the effect of these features across tasks, because these features might differ merely as a result of the task, rather than as a result of the variable of interest"
- G2 同 l.781-784 "Keystrokes are found to be sensitive to other factors, such as handedness, keyboard type (Gunetti & Picardi, 2005; Tappert et al., 2009), typing and writing experience and abilities, environmental conditions"／l.792-793 "This could indicate which factors need to be controlled for when analyzing specific keystroke features."
- G3 同 l.837-839 "it is important to be mindful when deriving conclusions from individual keystroke features, because they are already sensitive to small differences in writing tasks."
- G4 Monaco (2018) l.276-279 "The temporal resolution and precision of each keystroke depends on the sampling rate of the sensor, where in the processing pipeline it was detected, the speed and scheduling policy of the host computer"／l.332-333 "Key press time intervals reveal system timer resolution (top, Windows 64 Hz)"
- G5 同 l.20-22 "nontrivial information gains can be achieved even in the presence of substantial measurement error"

## 2. 評価表

| | 点 | 所見 |
|---|---|---|
| a | 3 | §10.6 と D3 の "reads the input method's composition events" は実装（`ime_winevent.rs`・`cloak.rs`: 候補窓の表示・非表示をシステム全体で畳む）と違う。他の数（617/2,925・574/852/882・11.2 時間・6%）は内部で整合 |
| b | 2 | (1) TSF の参照は IME が消費したキーを受け取らない → 焦点のある参照に人が打つと、どの規則でも止まらず解析・寄託まで進む。(2) 長い試行を比較の片側（正解）で決める。計画の打鍵の長さなら独立。(3) 観測器の 20 秒の打ち切りの起点が書かれていない |
| c | 3 | IMM と TSF の比較（入力欄で確定の時点が変わる）は貴重だが §10.10 は S7 の 1 行だけ。自分の環境で何を確かめるかの指針が無い |
| d | 3 | 「TSF は消費されないキーしか受け取らない」が 4 か所。D3 の理由も 4 か所。§10.1 は約 270 語の 1 段落で `deviations.md` と重なる |
| e | 3 | J1 に照らし `cell.windows.json` のパスが公開物の根から解決しない。J9 は §3.4 を継いで満たす。J11 は規定なし |
| f | 3 | Windows の時刻の基盤（G4）と入力欄による違い（G1）の根拠の文献が無い |
| g | 2 | 決まっていない: 問 4 の "both cells" を 3 セルでどう読むか・Windows の closed_set/open_set の命令（`--config`・入力モードのキーの宣言）・Windows の観測器の規則・IMM のパイロットの寄託の基準とその実装 |

## 3. 指摘

- **[major] Windows の観測器が何を測るかが書かれておらず、書かれている記述は実装と違う**
  - 位置: §10.6 l.1191-1192「the Windows observer reads the input method's composition events, and no prediction applies to it」／D3 l.61「the Windows observer reads the input method's own composition events」／`ime_winevent.rs` l.3-4・12「… `EVENT_OBJECT_IME_SHOW` …」「A display event opens a conversion session and a dismissal closes it.」・l.9-10「the session summary is a system-wide observation rather than one attributed to an application」／`cloak.rs` l.4-8・l.258「A session cut off because its end was never observed. No row is produced」／`ime_cloak.rs` l.167 `MAX_SESSION_MS: u64 = 20_000`
  - なぜ: §1.1 の観測器の規則は macOS のもので、Windows の規則は §10 に無い。Windows のセッションは、どの窓でも IME の候補窓が見えている区間で、開く時点は予測窓が出た時点。2 つの経路・畳み込み・20 秒の打ち切り（自分の開始から）・25 秒の安全弁。これを知らないと問 2 の `dwell_ms` の偏りも over_limit の検証も読めない。D3 の "The cut-off at 20 seconds is the same on both systems" の根拠が無い。G4 により時刻の取り方と遅延源（resolver のスレッド・100 ms のポーリング）も書くべき。
  - 解消: §10 に "The observer on Windows" の小節（開閉の事象・システム全体・畳み込み・20 秒の打ち切りの起点と行を書かないこと〔どちらの経路でも〕・`nav` と `abandon` が他の窓のキーも数える上限であること・時刻の取り方と遅延源）。§10.6 と D3 を直す。
  - 自信: 高
- **[major] 問 4 の判定規則が、Windows のセルを入れたときに 1 通りに決まっていない**
  - 位置: §6.8 l.896-897「A feature set is near chance for the recommendation when it is near chance at both K = 10 and K = 100 in both cells.」／l.835「input-mode switches are not recorded on macOS and are not declared」／l.858 `--config experiment/plan_config.macos.json`／§10.2「question 4 on its observation log … Everything not stated in this section is as registered for the macOS cells.」
  - なぜ: "both cells" が 3 セルでどう読むか（3 セルすべてか・Windows を別に推奨するか・macOS の推奨を Windows で取り消せるか）が決まっていない。`closed_set.py` l.794-796 は設定のハッシュを照合するので §6.8 の命令をそのまま使うと走らない。Windows で入力モードのキーを宣言するか（`closed_set.py` l.553-555 "it has not been confirmed against a logger run"）。判定の確率の表（l.883-890）に Windows の n が無い（S12 を除くと 2,700）。公開の粒度を決める唯一の合否の規則（G5）。
  - 解消: §10 に問 4 の小節（Windows の 2 つの命令を逐語で〔`--config experiment/plan_config.windows.json`・`--recipes kit/gen/recipes.json`・入力モードのキーを宣言しないこと〕・推奨の規則が Windows をどう含むかを 1 文で・Windows の n と判定の確率の行）。
  - 自信: 高
- **[major] 停止規則の盲点の帰結が書かれておらず、補う検査も無い（公開の安全）**
  - 位置: §10.7 l.1209-1211・§10.10 l.1244-1246・`pilot-windows.md` l.154「The TSF field received 3 to 16 key-downs per run in all, against 1,174 to 3,900 presses sent.」・§3.4 l.486-489「Outside the widened spans of the losses of focus … rows of the observation without a sent press are a result of the observer under test … and never make a run count as aborted」
  - なぜ: 計測中は参照に焦点があり IME はオン。人が文字・Space・Enter・Esc・BS を打つと、理由 3 は見えず、理由 4 は焦点の喪失が無いので働かない → 解析・寄託される。人の打鍵は観測の key 行に残り、参照の側にもセッションを作る。macOS では参照がすべての key-down を記録したので閉じていた。§2.1 の "no person's typing is part of the data" を Windows で支えられない。補う手段: パイロットでは "No trial had more rows than presses"（l.148）なので、run 全体で送った打鍵に対応しない観測の行は 0 が期待値。`keyboard.rs` l.9-10 は注入された入力を捨てない。
  - 解消: 少なくとも §10.10 と `pilot-windows.md`（Raw logs）に「焦点がある参照に IME オンで打たれた人の打鍵は、どの規則にも捕まらない」と明記。望ましくは、Windows のセルに限り run 全体で送った打鍵に対応しない観測の key 行が 1 つでもあれば寄託しない（必要なら解析もしない）検査を逸脱 D4 として凍結の前に足す。しないなら、その数を `data.md` の run checks に記録し寄託の判断に使う。
  - 自信: 高（盲点）／中（補う検査）
- **[minor] `cell.windows.json` のパスが手順書のいう「公開物の根」から解決しない**（README.windows.md l.16-17 と cell.windows.json l.13・18・25・§9 l.1075-1076・`run_cell.py` l.237 は cwd を指定しない）→ `kit/…` に直すか手順書を repo の根からに揃える。自信: 高
- **[minor] IMM のパイロットの寄託の基準が登録の道具で実装されておらず、安全の幅も緩い**（`pilot-windows.md` l.187-189・l.193-194・`pipeline.py` l.243・l.248。`--check-deposit` は k=0 で IMM の run を必ず拒む → k=1 は手作業。k=1 は `VK_IME_ON` が届かなかった区間で人の打鍵を 1 つ許す）→ IMM の run を寄託しない・k を引数にした検査を新しいファイルで用意して命令を書く・「`--check-deposit` は IMM の run を拒むので寄託しない」と明記、のどれか。自信: 高
- **[minor] 長い試行を比較の片側（正解の長さ）で決める理由が示されていない**（§10.6 l.1192-1193・l.1198-1199。観測器の打ち切りは自分の開始〔予測窓の表示〕から数えるので境界がずれる。計画の打鍵の長さという独立な規則がある）→ 正解を選ぶ理由と境界の帯（例 19〜21 秒の試行の数）を報告すると決める、または計画の打鍵の長さで範囲を作り正解の版を感度として並べる。自信: 中
- **[minor] 凍結の機械の門が Windows の追補を区別しない**（Status l.6-7・§10.1 l.1104-1106・`pipeline.py` l.899-900。`sha256:` が macOS の値のままなので、追補の凍結の前でも Windows の run を解析できる）→ §10.1 に「この門は追補の凍結を区別しない。Windows の計測が追補の登録より後であることは OSF の日付と run の manifest の日付で示す」。自信: 中
- **[minor] 利用者が自分の Windows の環境で結果をどう読むかの指針が無い**（§10.10 l.1234-1237・`pilot-windows.md` l.110-115）→ §10.10 に、観測器は入力欄に依存しないが正解（確定の時点）は依存する・パイロットの IMM と TSF の差（8/117・S7 と S14）・自分のアプリへ持ち出す前に `kit/pilot` の手順で参照を替えて確かめること、を 2〜3 文。自信: 中
- **[minor] Windows の観測器が key 行を書くキーの種類が §10 に無い**（§1.1 l.21-22・`keyboard.rs` l.47-52: 修飾キー・Win・PgUp/PgDn/Home/End・F1〜F12 を観測）→ §10.3 に、行を書かないキーと macOS と違って書くキー（修飾キー）を 1 文。自信: 中
- **[nit]** §10.1 の差分の一覧に `notes.md` が無い／§10.6「39 of 39 in each of three runs」は IMM を含む（TSF の根拠は 2 本）／`python3` と `python`／§10.1 の過去形／README.windows.md の Notes の最初の 2 項は §10.7 の参照にできる。

## 4. 総合: major

計画・手順・正解の規則・範囲・停止規則の設定値は丁寧に固定され数も整合するが、Windows の観測器の規則が書かれておらず記述は実装と違う。問 4 の判定規則と人の打鍵を外す停止規則が Windows では 1 通りに決まっていないか帰結が書かれていない。`cell.windows.json` のパスのような再現の欠陥もある。

## 5. 読めなかった範囲・注入の疑い

読んでいない: 第 1 群の `pilot-macos.md`・`notes.md`・`config.json`・`gt_rules.json`・`SEED`・`plan_config.*.json`・`recipes*.json`・`keymap_windows.json`・`kit/run/README.md`・`kit/gen/README.md`・`kit/emit/README.md`・`kit/refinput-windows/README.md`・`kit/logger/README.md`・`kit/pilot/README.md`・`kit/e2/README.md`。第 2 群の `match.py`・`gt_sessions.py`・`l1.py`・`generate_plan.py`・`focus_windows.py`・`away_windows.py`・`start_windows.py`・`backend_windows.py`・`tsf.rs`・`refinput_tsf.rs`。部分: `data.md`・`env.md`・`kit/e3/README.md`（Grep）、`pipeline.py`・`closed_set.py`・`delivery.py`（Grep の周辺）、`run_cell.py`（1 か所）、`ime_winevent.rs`（冒頭と Grep）・`cloak.rs`（1-60・240-279）・`ime_cloak.rs`（150-199 と Grep）、`preregistration.md`（Status・§1〜§2・§3.2〜§3.4・§6.8・§7 の末尾・§8〜§10）。`plan_config.windows.json` が「`_note` 以外は同じ」ことは確かめていない（指摘 2 は context-A に依った）。一覧の外は開いていない。注入の疑い: なし。
