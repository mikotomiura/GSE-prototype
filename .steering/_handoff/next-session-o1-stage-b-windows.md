# 次セッション（Windows）— O1 v0.1.38 の段階 B: 本当のサインインで自動起動するか

> 作成: 2026-09-30（Mac・PR #264 / #265 の後）。前身: `next-session-o1-autostart-stage-b.md` §2-2（★ 本メモが置き換える）。
> ⚠️ **このメモを一次資料にしない。** 状態は着手時に測り直す。一次: `src-tauri/src/autostart.rs`（`decide` の表・`handle`・Windows の `register` / `entry_exists`）・
> `.steering/20260928-o1-resilience-g1-g2-g5/g1-mac-autostart-experiment.md`「結果（段階 B）」（★ Mac の結果＝比較の相手）・
> 配布 zip 内の `README_先に読む.txt`【3】（Windows 版）。
> ★★ **収集専任**（memory `windows-agent-collection-only`）: Windows 側は**測って記録するだけ**。README・コード・配布物は直さない（直すのは Mac 側の文脈）。
> ⚠️★★ **サインアウトすると Claude のセッションは切れる。** → 状態を `%USERPROFILE%\GSE-autostart-exp\STATE.md` に書き継ぎ、サインインし直した後の**新しいセッション**が `§0-後半` を打って続ける（計 2 回切れる）。

## §0-前半 打ち込む用（Windows・`/clear` の直後に）

```
git pull --ff-only してから .steering/_handoff/next-session-o1-stage-b-windows.md を読んで、§2 の手順 1〜5（退避 → 実験用コピー → 起動と同意 → 登録の確認 → サインアウトの直前）を進めてください。サインアウトの直前で止めて、私に知らせてください。
Skill: verify-before-claiming・data-privacy。応答は日本語。研究者の操作が要るところは手順を 1 つずつ示す。収集専任（README・コードは直さない）。
```

## §0-後半 打ち込む用（サインインし直した後・新しいセッションで・2 回目以降も同じ）

```
%USERPROFILE%\GSE-autostart-exp\STATE.md と .steering/_handoff/next-session-o1-stage-b-windows.md §2 を読んで、STATE.md の「次」から続けてください（最後は片付け（★ 退避したものを元に戻す）→ 記録 → PR）。
Skill: verify-before-claiming・data-privacy・git-workflow。応答は日本語。収集専任（README・コードは直さない）。
```

## §1 前提（2026-09-30 に Mac で測った値）

| 何 | 値 |
|---|---|
| 確かめる配布物 | Drive の `O1_実施用_Windows.zip`（v0.1.38・**5,983,577 B**・SHA-256 `e8c69975cb60df96dd4074d6c027d3a14af97daac31ef6a77b8907da8fc5c8b8`・`docs/o1-distribution-tag.md`）。⚠️ zip は **git に入っていない** → 研究者が Drive から落とし、`Get-FileHash -Algorithm SHA256` で照合してから使う |
| 登録の仕組み（`autostart.rs:29-31` / `:376-416`） | 同意確認の後に 1 回だけ `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` の値 **`GSE-O1`** に**引用符つき**の `gse-next.exe` のパスを書く。配布フォルダに `o1.autostart`（中身 = exe のパス）・`%USERPROFILE%\.gse\o1_autostart_registered` を置く。★ **`StartupApproved` には触らない**（タスクマネージャーでの無効化を尊重する設計） |
| 判定表（`decide`） | 印あり → 何もしない／印なし・記録なし → **Register**／印なし・記録あり・Run の値あり → **Repoint**（書き直す）／印なし・記録あり・Run の値なし → 何もしない |
| ★ Mac の結果（段階 B・2026-09-29） | 自動起動 ✅／表示名 `gse-next` ✅／**オフにした瞬間に動いていたアプリが終了**（launchd の bootout）／**オフのまま別フォルダから開いて Repoint → 次のログインで起動しない** ✅／ログアウトはきれいな終了にならず orphan sweep が `session_end` を次の起動時刻にする |
| ⚠️★ Windows だけの論点 | **Run には exe が直接登録される**が、被験者の手動起動は `GSE_起動.bat` 経由で、bat は起動前に `set GSE_DISABLE_PROBES=1`（プローブの 2 本目の引き金）を立てる。→ **自動起動では bat を通らず、この env が無い**。1 本目（O1 は `start_session` を呼ばないのでプローブのスケジューラが構造的に起動しない）は残る想定だが、★ **自動起動の記録に `probe_assignment` / `realtime_label` 行が 0 件か**を実測する（手順 6） |
| ⚠️ 記録先 | 既定は `%USERPROFILE%\Documents\GSE-sessions\`（`logger.rs`）。⚠️ **OneDrive がドキュメントをリダイレクトしていることがある** → パスは applog の記述か `[Environment]::GetFolderPath('MyDocuments')` で確かめる |

## §2 手順

### 前半（Claude ＋ 研究者・サインアウトの直前まで）

1. **状態を測って退避する**（⚠️ 最初に・消さない）:
   ```powershell
   $EXP = "$env:USERPROFILE\GSE-autostart-exp"; New-Item -ItemType Directory -Force "$EXP\backup-gse" | Out-Null
   [DateTimeOffset]::UtcNow.ToUnixTimeSeconds() | Set-Content "$EXP\started_epoch"
   Get-Process gse-next -ErrorAction SilentlyContinue                                   # ⚠️ 動いていたら止めて研究者に聞く（bat は動いていると何もせず終わる＝手順 3 が空振りする・実利用中の記録を乱す）
   reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v GSE-O1          # ⚠️ 既にあれば止めて研究者に聞く
   reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run" /v GSE-O1
   Get-ChildItem -Force "$env:USERPROFILE\.gse"
   ```
   ⚠️★ **ここで一度止まる。** 上の検査のどれかに当たったら（`gse-next` が動いている／Run か StartupApproved に `GSE-O1` がある）、**下の退避を実行せず**研究者に聞く。
   ⚠️ 上と下を 1 回で流さない（止める条件がコメントだけなので、一括実行すると素通りする）。
   ```powershell
   foreach ($f in 'o1_participant_id','o1_consent_ack','o1_autostart_registered') {
     $p = "$env:USERPROFILE\.gse\$f"; if (Test-Path $p) { Move-Item $p "$EXP\backup-gse\$f" }
   }
   Get-ChildItem -Force "$EXP\backup-gse"      # ★ 退避したはずのファイルが揃っているか。欠けていたら先へ進まない
   ```
   ★ **2 つの `reg query` の結果（在った／無かった・在れば値）を STATE.md に書く**（手順 10 の片付けはこれを見て条件分岐する）。
   ★ 退避しないと、同意済みとして既存の P-ID のまま登録し、実験用の P-ID を試せない。⚠️ `g1_participant_id` ほか他のファイルは動かさない（中身も出力に出さない）。
   ★ 既存の `GSE-sessions` の一覧（名前と更新時刻だけ）を STATE.md に控える。
2. **実験用コピー A**（⚠️ 本番の受け口へ送らない）: zip を `$EXP\A` に展開 → `Get-ChildItem` で `O1_実施用_Windows`・`GSE_起動.bat` の名前が化けていないことを確かめる（memory `participant-launcher-encoding`）。
   → 展開先の `g1-submit.json` を、**`next-session-o1-stage-b-mac.md` §2 手順 2 の `printf` と同じダミーの JSON**（endpoint が `127.0.0.1:9`）に差し替える。
   ⚠️ **BOM なし UTF-8** で書く: `[IO.File]::WriteAllText($p, $json, (New-Object Text.UTF8Encoding $false))`（Windows PowerShell 5.1 の `Set-Content -Encoding utf8` は BOM を付け、`>` は UTF-16 になる）。
   → `Select-String -Quiet script.google.com <path>` が `False` を確かめる（★ `-Quiet` を付ける＝行を出さない。値そのものは出力に出さない）。
   ★ endpoint が `http://` なのは意図どおり: アプリは `https://` 以外を拒否し（`submission.rs:496`）、applog に `endpoint が https:// で始まっていません` と出して**通信自体を試みない**（Mac の段階 B で実測）。⚠️ このエラーは「想定どおりの安全な失敗」として記録する。
   ⚠️ パスに非 ASCII が入るので、以後のコマンドは引用符で囲む。
3. **起動と同意**（研究者）: A の `GSE_起動.bat` をダブルクリック → 最初の画面で **実験用の P-ID `P998`** と同意の確認。
4. **登録の確認**（Claude）:
   - `reg query …\Run /v GSE-O1` の値が **引用符つき**の `A\…\gse-next.exe` ＝ A の `o1.autostart` の中身と同じパス
   - `%USERPROFILE%\.gse\o1_autostart_registered` がある・applog に `O1 autostart: registered the login entry`
   - `StartupApproved\Run` に `GSE-O1` があるか（★ この時点で無いのが設計どおりの見込み。あれば値を記録）
   - **研究者に聞く**: タスクマネージャー →「スタートアップ アプリ」に出る**名前**（README は「gse-next」）・状態（有効）・発行元の表示。通知が出たか。
5. **STATE.md に書く → サインアウトの前**: runner（`gh api repos/mikotomiura/GSE-prototype/actions/runners` の `g-gear-win-x64`）が `busy=false` か見る（★ 権限が無くて失敗したら skip と書いて進む）。→ 研究者に「アプリは**終了しないで**サインアウト → サインイン → 1 分ほど打鍵 → `§0-後半`」と伝えて止まる。

### 後半 1（1 回目のサインインの後）

6. **自動で立ち上がったか**:
   - `Get-Process gse-next`（起動時刻がサインインの直後）・`Get-CimInstance Win32_Process -Filter "Name='gse-next.exe'"` の `CommandLine` が A の exe
   - `GSE-sessions` に `started_epoch` より新しい `gse_o1_*.ndjson`: meta の `app_version = 0.1.38`・`o1_mode`・`key` 行が増える（⚠️ 8〜12 秒待つ・陰性対照: 打鍵しない 30 秒で増えない）。⚠️ 行の**中身は出さない**（件数と行種だけ）
   - ★ **`probe_assignment` / `realtime_label` / `intervention_*` 行が 0 件**（bat を通らない起動でもプローブが出ないこと。★ 陽性対照として `key` 行が数えられていること）。
     ★ applog で env が立っていないことも控える: `probe scheduler DISABLED` が**無く**、`Probe scheduler thread started` が**ある**（`lib.rs:4717` / `:4730`）＝ スケジューラは動くが、O1 は `start_session` を拒否するので発火しない、を観測で示す。⚠️ この間、研究者はホットキー類を押さない。
   - サインアウト前のセッションのファイルが orphan sweep で閉じられたか（applog）・runner が `online` に戻ったか
   - トレイ「計測中」と画面の「記録中」の印（研究者の目視）
7. **無効にする**（研究者）: タスクマネージャー → スタートアップ アプリ → gse-next →「無効にする」。
   - ★ **その瞬間に動いているアプリが止まるか**（`Get-Process`。★ Mac では止まった）
   - Run の値が残っているか・`StartupApproved\Run` の `GSE-O1` の値（★ 先頭バイトで有効/無効を表す。値をそのまま記録）
8. ★★ **無効のまま Repoint されても起動しないか**: アプリを終了（トレイ → 終了）→ 同じ zip を `$EXP\B` に展開し `g1-submit.json` を同じく差し替え → B の `GSE_起動.bat` を開く。
   - applog に `re-pointed the login entry`・Run の値が B を指す・B に `o1.autostart`・同意画面が出ないこと
   - `StartupApproved\Run` の値が**無効のまま変わっていない**・タスクマネージャーで「無効」のまま（研究者）
   - STATE.md に書く → アプリを終了 → サインアウト → サインイン → `§0-後半`。

### 後半 2（2 回目のサインインの後）

9. **立ち上がらないこと**（★ 観測時間: サインインから **少なくとも 3 分**、かつ手順 6 で測った「サインイン → 起動」の時間の 3 倍以上。1 分おきに 3 回以上見る）: `Get-Process gse-next` が無い・B を起動した後より新しい `gse_o1_*` が増えていない・applog の最終行が B の起動時のまま。★ 陽性対照 = 手順 6（有効のときは立ち上がった）。
   ⚠️ **立ち上がっていたら** = 被験者が切っても次のフォルダで戻る欠陥 → 状態を記録して研究者に報告（★ 直すのは Mac 側・版を上げる判断は研究者）。★ **失敗しても手順 11 の記録 → 手順 10 の片付け（退避の復元）は必ず行う**（実験用の登録・P998 を端末に残さない）。中断したら STATE.md の「次」に「片付けが未了」と書いて再開できるようにする。
10. **片付け**（⚠️ 消すのは実験で作ったものだけ。★ **先に手順 11 の記録ファイルを repo に書き、STATE.md の中身を転記してから**始める＝根拠を消してから書く、をしない）:
    ```powershell
    Stop-Process -Name gse-next -ErrorAction SilentlyContinue
    # ⚠️ 以下 2 つの reg delete は**条件つき**。コピーして丸ごと流さない。
    #   Run の GSE-O1: 値が $EXP\A か $EXP\B の gse-next.exe を指しているときだけ消す（reg query で確かめてから）
    #   StartupApproved の GSE-O1: STATE.md の手順 1 の記録が「無かった」ときだけ消す（在ったなら値を手順 1 のものに戻すか研究者に聞く）
    reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v GSE-O1 /f
    reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run" /v GSE-O1 /f
    Remove-Item "$env:USERPROFILE\.gse\o1_autostart_registered","$env:USERPROFILE\.gse\o1_participant_id","$env:USERPROFILE\.gse\o1_consent_ack" -ErrorAction SilentlyContinue   # ★ P998 のもの
    Move-Item "$EXP\backup-gse\*" "$env:USERPROFILE\.gse\"   # ★ 元に戻す（-Force を付けない＝同名が残っていれば失敗して止まる。それが正しい）
    ```
    - ⚠️ `Remove-Item` の前に、`.gse` の 3 つが**実験で作られたもの**（作成時刻が `started_epoch` より後・`o1_participant_id` が `P998`）であることを確かめる。退避が空だった場合は戻すものは無い。
    - `GSE-sessions` と `GSE-submissions` で **作成時刻が `started_epoch` より後**のファイルだけを消す。★ 実験中にほかの記録が混ざらないことは手順 1（`gse-next` が動いていたら止まる・既存の O1 の P-ID は退避中）が担保する。⚠️ それでも、候補の `.age` の名前の先頭が `P998_` であること、NDJSON は実験中に起動した回数と本数が合うことを確かめ、合わないものは消さずに研究者に聞く（⚠️ `gse-app.log` など既存ファイルは**更新されただけ**なので残す＝作成時刻で見分ける）。**消す前に一覧を研究者に見せる。**
    - タスクマネージャーのスタートアップ アプリから gse-next が消えたか（研究者）。
    - 最後に `$EXP` を削除（★ `backup-gse` が空になったことを確かめてから）。
11. **記録と PR**: `.steering/20260928-o1-resilience-g1-g2-g5/g1-windows-autostart-experiment.md` を新規に作り、Mac 版の「結果（段階 B）」と同じ表の形で書く（確かめたこと｜結果｜根拠）。★ 必ず入れるもの: 表示名・無効にした瞬間の挙動・`StartupApproved` の値の変化・Repoint 後に無効が保たれたか・**bat を通らない自動起動でのプローブ行 0 件**・orphan sweep の有無。README（Windows 版【3】）と食い違えば**食い違いとして書くだけ**（直さない）。
    → 作業ブランチ `docs/o1-stage-b-windows-result` で commit → push → PR（`git-workflow` ルール 6。CI 緑なら merge）。`.steering/_handoff/README.md` の本メモの行を「完了」に。

## §3 やらないこと
- 本番の受け口・受領台帳へ送る（`g1-submit.json` は必ず差し替える）。実在の P-ID を使う。
- README・`autostart.rs`・bat・配布 zip を直す（★ 収集専任。直すのは Mac 側）。
- `%USERPROFILE%\.gse` の既存ファイル・既存の記録を消す（★ 退避して戻す）。
- NDJSON の行の中身・`g1-submit.json` の値・既存の P-ID を出力や記録に出す。
- G1 の配布物（`v0.1.36` 凍結）。

## §4 任意（研究者が求めたら・段階 B の後）
- **区間指定削除の実機での通し確認**（G1・O1 共通の同意の約束・`distribution-tag.md`「実機での削除の通し確認は未実施」）。実験用の記録で「時間帯を指定して消す」を行い、該当区間の行が消え、`redaction_ledger.jsonl` に記録が残ることを確かめる。
