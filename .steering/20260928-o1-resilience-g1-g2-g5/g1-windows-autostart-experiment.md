# O1 v0.1.38 の段階 B（Windows 実機）— 本当のサインインで自動起動するか ＋ 無効のまま Repoint されないか

> 手順は `.steering/_handoff/next-session-o1-stage-b-windows.md` §2。サインアウトを 2 回またぐため 3 セッションに分けて行い、状態は `%USERPROFILE%\GSE-autostart-exp\STATE.md` に書き継いだ（片付けで削除・中身は末尾に転記）。
> 比較の相手 = Mac の結果 `g1-mac-autostart-experiment.md`「結果（段階 B・2026-09-29 …）」。
> 安全策: 実験前の `%USERPROFILE%\.gse` に `o1_*` は**無かった**（退避 0 件・`g1_participant_id` / `participant_id` は動かしていない）。実験用 P-ID `P998` で同意した。`g1-submit.json` は `http://127.0.0.1:9/exec` に差し替え（BOM なし・`script.google.com` を含まない）。zip は 5,983,577 B・SHA-256 `e8c69975…c5c8b8`（`docs/o1-distribution-tag.md` と一致）。
> ★ 収集専任: README・`autostart.rs`・bat・配布 zip は直していない。

## 結果（2026-10-01 23:32 〜 10-02 01:05 JST・Windows 11 Home 26200・配布 zip v0.1.38）

| 確かめたこと | 結果 | 根拠 |
|---|---|---|
| 同意の後に登録されるか（Register） | ✅ `HKCU\…\Run\GSE-O1` = **引用符つき**の A の `gse-next.exe`（A の `o1.autostart` の中身を引用符で囲んだものと一致）・`%USERPROFILE%\.gse\o1_autostart_registered`（23:42:58） | `reg query`・applog `O1 autostart: registered the login entry (HKCU\…\Run\GSE-O1)` |
| 登録の直後の `StartupApproved\Run` | ✅ **`GSE-O1` は無い**（アプリは StartupApproved に触らない設計どおり） | `reg query` |
| 被験者に見える通知 | 出なかった（研究者の記憶） | 研究者 |
| タスクマネージャーの表示 | ✅ 「スタートアップ アプリ」に名前 **`gse-next`**（README【3】と一致）・状態 **有効**・発行元 **`johnd`**（＝ユーザー名。署名の無い exe の表示とみられる・未検証） | 研究者の目視 |
| 本当のサインインで自動起動するか | ✅ explorer 23:54:48 → `gse-next` が **23:56:54**（**2 分 06 秒後**）に起動・**親 = explorer.exe**（cmd.exe ＝ bat を経由していない）・CommandLine = 引用符つきの A の exe | `Get-Process`・`Win32_Process` |
| 初回の自動起動で `StartupApproved` が現れるか | ★ サインイン後に `StartupApproved\Run\GSE-O1 = 020000000000000000000000`（REG_BINARY・先頭 02 = 有効）が**現れた**。登録の直後には無かった ＝ **Windows（Explorer）が書いた** | `reg query`（手順 4 と手順 6 の比較） |
| 自動起動で O1 として記録するか | ✅ 新しい NDJSON の meta に `app_version = 0.1.38`・`o1_mode = marker`・`hmm_version = 0.5.0`・`key` 314 行。陰性対照: 打鍵しない 35 秒で `key` 314 → 314（`feat` だけ増えた）。applog `O1 autostart: already handled for this folder (marker present)` | NDJSON の行種の件数（中身は見ていない・片付けで削除）・applog |
| ★ bat を通らない自動起動でプローブ行が出ないか | ✅ **`probe_assignment` / `realtime_label` / `intervention_*` は 0 件**（陽性対照 = 同じファイルで `key` 314 行を数えた）。applog に `probe scheduler DISABLED` は**無く**、`Probe scheduler thread started` が**ある** ＝ env（`GSE_DISABLE_PROBES`）は立っていないが、O1 では発火しない（1 本目の引き金が効いている）。対照: bat 経由の起動（A・B）では `probe scheduler DISABLED (env=true, g1_mode=None)` | NDJSON の行種の件数・applog |
| トレイ | ✅ 「計測中」 | 研究者の目視・applog `tray state (initial) -> Measuring` |
| サインアウトのときの終了 | ⚠️ **きれいな終了にならない**（Mac と同じ）。サインアウト前のセッションに終了行が無く、次の起動で `O1 orphan sweep: closed gse_o1_20261001_144241.ndjson with session_end=…`（= **sweep した時刻** 23:56:57）・`closed=1 failed=0` | applog |
| 送信 | ✅ `endpoint が https:// で始まっていません` → FAILED（★ 想定どおりの安全な失敗・通信は試みていない）。`GSE-submissions` は 1 本も増えなかった（48 時間の保留のため） | applog・`Get-ChildItem` |
| タスクマネージャーで「無効にする」 | ★ `StartupApproved\Run\GSE-O1` が `02…` → **`03000000ABEB6780B951DD01`**（先頭 03 = 無効・残り 8 バイトは FILETIME で **00:28:25.607 JST** ＝無効にした時刻）。**Run の値は残る**（A のまま） | 1 秒おきの `reg query` の監視ログ |
| ★★ 無効にした瞬間に動いていたアプリは止まるか | ★ **止まらない**（⚠️ **Mac と違う**。Mac は launchd の bootout でその場で終了）。pid 10452 が 4 分後も動作中・Responding・記録ファイルも更新され続けた | `Get-Process`・ファイルの更新時刻 |
| ★★ 無効のまま別フォルダ B から開く（Repoint） | ✅ applog `O1 autostart: re-pointed the login entry` → Run の値が引用符つきの B の exe・B に `o1.autostart`（中身 = B の exe のパス）。**同意画面は出ない**（`.gse` の同意を再利用）。★ **`StartupApproved` は `03000000ABEB6780B951DD01` のまま**（Repoint は触れない）・タスクマネージャーでも「無効」のまま | applog・`reg query`・研究者の目視 |
| ★★ 無効＋Repoint の後のサインインで立ち上がらないか | ✅ 00:50:10 のサインイン → 00:56:29〜00:59:40 に 5 回（サインインから 9 分 30 秒＝手順 6 の起動遅れの 4.5 倍）すべて `gse-next` 無し・B の起動より新しい `gse_o1_*` 無し・applog の最終行は B の終了（15:48:53Z）のまま。陽性対照 = 上の 23:56（有効）では立ち上がった | `Get-Process`・`Get-ChildItem`・applog |
| Self-hosted runner | skip（この PC に `gh` が無く、runner のサービスも無い） | — |

→ ★ **README（Windows 版）【3】の「無効にしたあと、アプリが勝手に有効に戻すことはありません」は、Repoint（別フォルダに置き直した）場合も含めて Windows 実機で成り立つ**（1 回のサインインでの実測・陽性対照あり）。理由は構造的: 無効の状態は Windows が `StartupApproved` に持ち、アプリは Run だけを書き直して `StartupApproved` に触れない。
→ ★ **bat を通らない自動起動でもプローブ行は出ない**（O1 で `start_session` が呼ばれないため。env の 2 本目の引き金は自動起動では効いていないことも観測した）。

副次的な観察:
- ⚠️ **ログアウト（サインアウト）はきれいな終了にならない**のは Mac と同じ。`session_end` が次の起動時刻に延びる件（Mac 版の「別タスク候補」）は Windows でも起きる。⚠️ Windows では自動起動が explorer の起動から約 2 分遅れるので、延びる幅にはその遅れも入る。
- トレイ → 終了はきれいな終了（`SessionLogger: session closed`）。このとき記録フォルダがエクスプローラーで開き、`behavioral_gt.py not found` の WARN が出る（被験者の目にフォルダが開く。今回の確かめる対象ではないので記録だけ）。
- 記録中に `keyboard hook may be dead … starved_ms≈30000` → `delivering events again` が何度か出た（A の回に 4 回・無効にした直後・B の起動直後）。原因は断定しない（タスクマネージャーの操作中と重なる回がある）。
- 研究者が手順 3 の前に bat を通さず一度 `gse-next` を開き、同意せず 22 秒で閉じた回があった。同意の前でも NDJSON は作られる（`key` 0 行）・送信経路は開かない（`lib.rs` の設計どおり）。
- 画面の「記録中」の印は目視の回答を得ていない。

README との食い違い（★ 直すのは Mac 側・研究者の判断）:
- **食い違いはない**（表示名 `gse-next`・手順 1〜3・「勝手に有効に戻さない」）。
- ⚠️ Mac 版で補足の候補に挙がった「オフにすると、**その場で**アプリも終了し、記録も止まります」は **Windows では成り立たない**（無効にしても、動いているアプリと今日の記録は続く。止まるのは次のサインインから）。→ README に足すなら **OS ごとに書き分ける**必要がある。Windows 版に足すなら例えば「無効にしても今動いているアプリは止まりません。今日の記録を止めたいときはトレイから終了してください」。
- 発行元が `johnd`（研究者の PC のユーザー名）と出るのは README に書かれていない。被験者の PC では被験者のユーザー名が出るとみられる（未検証）。

## 片付け
片付け（2026-10-02 01:05 JST に完了・研究者が一覧を見て削除を了承）: `gse-next` が動いていないことを確認 → `Run\GSE-O1`（B の exe を指すことを確かめてから）・`StartupApproved\Run\GSE-O1`（実験前は無かった）を削除 → `.gse` の `o1_autostart_registered` / `o1_consent_ack` / `o1_participant_id`（作成 23:42:58・P998 を確かめてから）を削除（★ 退避は 0 件なので戻すものは無い。`g1_participant_id` / `participant_id` は触っていない）→ `Documents\GSE-sessions` で実験開始より後に作られた 5 つ（`gse_o1_*.ndjson` 4 本＝起動 4 回と一致・`.o1_clock_hwm`）を削除（`gse-app.log` と既存の `gse_*.ndjson` 12 本は残した）→ `GSE-submissions` は増えていなかった → `%USERPROFILE%\GSE-autostart-exp` を削除（`backup-gse` が空であることを確かめてから）。タスクマネージャーのスタートアップ アプリから gse-next が消えたことを研究者が確認した。

## 付録: STATE.md の転記
```markdown
# O1 段階 B（Windows）実験の状態 — 次のセッションはここから続ける

手順書: C:\GSE-prototype\.steering\_handoff\next-session-o1-stage-b-windows.md §2

## 手順 1（2026-10-01 23:32 JST・済）
- started_epoch = 1790865158（2026-10-01 23:32:38 +09:00）
- gse-next の実行中プロセス: 無し
- Run の GSE-O1: **無かった**（Run の値は MicrosoftEdgeAutoLaunch_* だけ）
- StartupApproved\Run の GSE-O1: **無かった**（キー自体は在る）
  → 手順 10 で Run・StartupApproved の GSE-O1 は「実験で作られたもの」なので消してよい（Run は A/B の exe を指すことを確かめてから）
- .gse の退避: **0 件**（o1_participant_id / o1_consent_ack / o1_autostart_registered はもともと無かった）
  → 手順 10 で戻すものは無い。.gse には g1_participant_id・participant_id だけが在った（動かしていない）
- GSE_DATASET 環境変数: 無し。記録先 = %USERPROFILE%\Documents\GSE-sessions（logger.rs:2784。OneDrive のドキュメントではない）
- 既存の GSE-sessions（実験前）: gse-app.log（作成 2026/08/09 14:02:35）＋ gse_*.ndjson 12 本（作成はすべて 2026/08/09〜08/26）。gse_o1_* は 0 本
- 既存の GSE-submissions（実験前）: manifest.jsonl ＋ P007_block01〜09 / P009_* の .age 系（作成はすべて 2026/08/26 以前）。P998_* は 0 本

## 手順 2（済）
- zip: Downloads\O1_実施用_Windows.zip・5,983,577 B・SHA-256 一致（e8c69975…c5c8b8）
- $EXP\A\O1_実施用_Windows に展開。名前は化けていない（GSE_起動.bat / README_先に読む.txt / gse-next.exe / gse-submit.exe / o1.mode / pubkey.txt / g1-submit.json）
- g1-submit.json をダミー（endpoint http://127.0.0.1:9/exec）に差し替えた。BOM なし・script.google.com を含まない

## ⚠️ 手順 3 の前に起きたこと（23:34:50〜23:35:12 JST）
- A の起動より前に、bat を通らない gse-next の起動が 1 回あった（applog: `Probe scheduler thread started`＝env 無し。O1 MODE ENABLED。同意なしのまま 22 秒で窓が閉じられた: `main window close requested`）
- 作られたもの: GSE-sessions\gse_o1_20261001_143450.ndjson（26 行: meta 2 / feat 21 / ime_state 2 / pointer_bin 1 / **key 0**）・GSE-sessions\.o1_clock_hwm（23:34:55）
- 同意の前でも記録は始まる。これは設計どおり（lib.rs:2002-2013「確認が済むまで送信経路を開かない。.age は作られる」）。送信の経路は開いていない
- 研究者の回答: 研究者が手順 3 の前に自分で 1 回 gse-next を起動したもの（想定内）
- 片付け（手順 10）では、この 2 つも「実験で作られたもの」として扱う（NDJSON の本数を数えるときに含める）

## 手順 3・4（済・23:42:41 起動 / 23:42:58 同意）
- プロセス: pid 22452・CommandLine = "…\GSE-autostart-exp\A\O1_実施用_Windows\gse-next.exe"
- applog: `probe scheduler DISABLED (env=true, g1_mode=None)`（bat 経由なので env が立っている）→ `O1: enrollment acknowledged` → `O1 autostart: registered the login entry (HKCU\…\Run\GSE-O1)`
- Run\GSE-O1 = "C:\Users\johnd\GSE-autostart-exp\A\O1_実施用_Windows\gse-next.exe"（引用符つき）＝ A の o1.autostart の中身を引用符で囲んだものと一致・exe は存在する
- StartupApproved\Run\GSE-O1: **無い**（設計どおり＝StartupApproved には触らない）
- .gse: o1_autostart_registered / o1_consent_ack / o1_participant_id（作成はどれも 23:42:58・P-ID = P998）
- この回の記録: gse_o1_20261001_144241.ndjson（確認の時点で 198 行: key 103 / feat 80 / ime_state 8 / ime_shadow 3 / meta・focus_transition・pointer_bin・starve_window 各 1）
- 研究者の回答（タスクマネージャー「スタートアップ アプリ」）: 発行元 = **johnd**・状態 = **有効**・名前 = 未回答（★ 後半のセッションで研究者に聞く。README は「gse-next」）
- 通知: 研究者の記憶では特に出なかった

## 手順 5
- runner の確認: **skip**（この PC には gh が無く、actions runner のサービスも無い）

## 手順 6（1 回目のサインインの後・2026-10-01 23:58〜10-02 00:00 JST・Claude の測定は済）
- サインイン: ログオンセッション 23:54:47 / explorer.exe（pid 24552）23:54:48
- ★ 自動起動: gse-next pid 10452・起動 23:56:54（explorer から **2 分 06 秒後**）・**親 = explorer.exe**（cmd.exe ＝ bat を経由していない）・CommandLine = "…\A\O1_実施用_Windows\gse-next.exe"（引用符つき）
- ★ StartupApproved\Run\GSE-O1 = **020000000000000000000000**（REG_BINARY）が**サインイン後に現れた**。手順 4 の時点では無かった＝アプリではなく Windows（Explorer）が初回の起動時に書いた（アプリは StartupApproved に触らない設計どおり）。先頭 02 = 有効
- Run\GSE-O1: A の exe のまま（変化なし）
- applog（自動起動の回）: `O1 MODE ENABLED (source=marker)`・`O1 autostart: already handled for this folder (marker present)`・`tray state (initial) -> Measuring (GSE — 計測中)`
- ★ プローブ: applog に `probe scheduler DISABLED` が**無く**、`Probe scheduler thread started` が**ある**（env 無し＝bat を通っていない）。それでも記録 gse_o1_20261001_145654.ndjson に **probe_assignment / realtime_label / intervention_* は 0 件**（行種: meta 1 / key 314 / feat 147 / ime_state 8 / ime_shadow 3 / focus_transition 2 / paste 1 / starve_window 1・00:00 時点）
- meta: app_version=0.1.38・o1_mode=marker・hmm_version=0.5.0
- 陰性対照: 打鍵しない 35 秒（23:59:43→00:00:18）で key 314→314（行は 492→527＝feat のみ増加）。陽性対照 = サインイン後の打鍵で key 314
- ★ サインアウト時のきれいな終了は**無い**（14:42:58Z の登録の後、14:56:54Z の起動まで shutdown 系の行が無い）。→ 起動時に `O1 orphan sweep: closed gse_o1_20261001_144241.ndjson with session_end=1790866617312`（＝今回の起動時刻 23:56:57。Mac と同じ挙動）`closed=1 failed=0`
- 送信: `O1 auto-submit detail: endpoint が https:// で始まっていません` → FAILED（★ 想定どおりの安全な失敗・通信は試みていない）
- 付記: A の回（サインアウト前）に `keyboard hook may be dead … starved_ms≈30000` → `delivering events again` が 4 回（14:46〜14:53Z）。今回の確かめる対象ではないので記録だけ
- runner: skip（手順 5 と同じ）

- 研究者の目視（00:27 頃）: トレイ = **計測中**／タスクマネージャー「スタートアップ アプリ」の名前 = **gse-next**（README の記載と一致）／画面の「記録中」の印は回答なし

## 手順 7（済・00:28 JST）
- 監視ログ（$EXP\step7-monitor.log）:
  - 00:27:42.044 proc=10452@23:56:54 run=present sa=020000000000000000000000
  - 00:28:25.628 proc=10452@23:56:54 run=present sa=**03000000ABEB6780B951DD01**
- ★ StartupApproved\Run\GSE-O1: 先頭 02（有効）→ **03（無効）**。残りの 8 バイト（ABEB6780B951DD01）を FILETIME として読むと **2026-10-02 00:28:25.607 +09:00**＝無効にした時刻
- ★ Run\GSE-O1: **残っている**（値は A の exe のまま）
- ★★ **無効にしても、動いていたアプリは止まらなかった**（pid 10452 が 00:32 時点でも動作中・Responding=True・記録ファイル 145654 は 00:32:05 まで更新）。⚠️ **Mac とは違う**（Mac では launchd の bootout で、オフにした瞬間に終了した）
- 付記: 無効にした直後の 00:28:27 に `keyboard hook may be dead starved_ms=30003` → 00:31:48 に `delivering events again`（タスクマネージャー pid 19196・00:27:02 起動を操作していた時間帯と重なる。原因の断定はしない。記録だけ）

## 手順 8（準備済・00:35 JST）
- zip の SHA-256 を再照合（一致）→ $EXP\B に展開。フォルダ名は A と同じ・exe は A と同一（SHA-256）
- B の g1-submit.json を A のダミーで上書き（A と同一・BOM なし・script.google.com を含まない）。B に o1.autostart はまだ無い

## 手順 8（済・00:45〜00:47 JST）
- トレイ → 終了: 15:45:45Z に `main window close requested -> shutting down` → `SessionLogger: session closed`（★ こちらはきれいな終了。145654 が閉じた）。付記: 終了時に `Opening session folder`（記録フォルダがエクスプローラーで開く）・`behavioral_gt.py not found` の WARN
- B の bat で起動: pid 23756・00:46:06・CommandLine は B の exe・applog `probe scheduler DISABLED (env=true…)`（bat 経由）
- ★ applog: `O1 autostart: re-pointed the login entry (HKCU\…\Run\GSE-O1)`（15:46:07Z）
- ★ Run\GSE-O1 = 引用符つきの B の gse-next.exe（一致）
- ★ B\…\o1.autostart: 作成 00:46:07・中身 = B の exe のパス（UTF-8 で読んで一致・引用符なし）。⚠️ 最初の照合で「不一致」と出たのは Claude が PS 5.1 の Get-Content（ANSI 既定）で読んだため。UTF-8 で読み直して一致
- ★ StartupApproved\Run\GSE-O1 = **03000000ABEB6780B951DD01 のまま**（手順 7 の無効の値から変わっていない＝Repoint は StartupApproved に触れていない）
- 研究者: **同意画面は出なかった**・タスクマネージャーで gse-next は **無効のまま**
- .gse: o1_* の 3 つは 23:42:58 作成のまま（P998）。新しい記録 gse_o1_20261001_154606.ndjson
- 付記: 15:46:38Z に starve_window → 15:46:44Z に回復（記録だけ）

## 次
- 研究者: アプリを終了（トレイ → 終了）→ サインアウト → サインイン（★ アプリは自分では開かない）→ §0-後半 で新しいセッション
- 新しいセッションは手順 9 から: サインイン（explorer の起動時刻）から**少なくとも 6 分 20 秒**（手順 6 の 2 分 06 秒の 3 倍以上・かつ 3 分以上）、1 分おきに 3 回以上 `Get-Process gse-next` が無い・154606 より新しい gse_o1_* が無い・applog の最終行が B の起動〜終了のままを確かめる
- ★ 立ち上がっていても、立ち上がらなくても、その後 手順 11 の記録 → 手順 10 の片付け（.gse の退避は 0 件なので戻すものは無い。o1_* 3 つ・Run/StartupApproved の GSE-O1・実験の NDJSON 4 本＋.o1_clock_hwm・GSE-submissions の P998_*）→ PR

## 手順 9（済・2026-10-02 00:56〜00:59 JST）★ 上の「次」は完了
- 2 回目のサインイン: ログオンセッション 00:50:09 / explorer.exe（pid 16688）00:50:10
- 監視（$EXP\step9-monitor.log）: 00:56:29（Claude の初回確認）・00:56:38・00:57:39・00:58:39・00:59:40 の 5 回すべて **gse-next 無し**。観測はサインインから 9 分 30 秒（手順 6 の 2 分 06 秒の 4.5 倍）
- 新しい gse_o1_* 無し（最新は B の 154606 のまま。監視の new_o1=1 は 154606 自身＝作成時刻の端数秒で `> 00:46:07` に入っただけ）
- applog の最終行 = 15:48:53Z（B の終了 `tray updater stopping`）のまま
- Run\GSE-O1 = B の exe のまま・StartupApproved\Run\GSE-O1 = 03000000ABEB6780B951DD01（無効のまま）
- ★ 結論: 無効＋Repoint の後のサインインで立ち上がらなかった（陽性対照 = 手順 6）
- GSE-submissions: started_epoch より後のファイルは 0 件（P998_* 無し）

## 次（最新）
- 手順 11 の記録ファイルを repo に書く → 手順 10 の片付け（一覧を研究者に見せてから）→ PR
```

### step7-monitor.log
```
00:27:42.044 proc=10452@23:56:54 run=present sa=020000000000000000000000
00:28:25.628 proc=10452@23:56:54 run=present sa=03000000ABEB6780B951DD01
00:35:42.316 monitor end
```
### step9-monitor.log
```
00:56:38 proc=none new_o1=1 applog_last=2026-10-01T15:48:53.161345Z logon=2026/10/02 0:50:09
00:57:39 proc=none new_o1=1 applog_last=2026-10-01T15:48:53.161345Z logon=2026/10/02 0:50:09
00:58:39 proc=none new_o1=1 applog_last=2026-10-01T15:48:53.161345Z logon=2026/10/02 0:50:09
00:59:40 proc=none new_o1=1 applog_last=2026-10-01T15:48:53.161345Z logon=2026/10/02 0:50:09
```
