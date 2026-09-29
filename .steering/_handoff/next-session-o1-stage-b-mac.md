# 次セッション（Mac）— O1 v0.1.38 の段階 B: 本当のログインで自動起動するか

> 作成: 2026-09-29（Mac・PR #253 / #257 の出荷の後）。前身: `next-session-o1-autostart-stage-b.md` §2-1（★ 本メモが置き換える）。
> ⚠️ **このメモを一次資料にしない。** 状態は着手時に測り直す。一次: `src-tauri/src/autostart.rs`（`decide` の表・`handle`）・
> `.steering/20260928-o1-resilience-g1-g2-g5/g1-mac-autostart-experiment.md`（段階 A の結果）・
> `experiments/20260801-controlled-friction-task/dist/_common/O1_実施用_macOS/README_先に読む.txt`【3】。
> ⚠️★★ **ログアウトすると Claude のセッションは切れる。** → 本メモは **前半（準備と起動）** と **後半（ログイン後の確認と片付け）** に分かれる。
> 後半は、ログインし直した後の**新しいセッション**が `§0-後半` を打って始める。前半で `~/GSE-autostart-exp/STATE.md` に状態を書き残す。

## §0-前半 打ち込む用（Mac・`/clear` の直後に）

```
git pull --ff-only してから .steering/_handoff/next-session-o1-stage-b-mac.md を読んで、§2 前半（退避 → 実験用コピーの準備 → 起動と同意 → 登録の確認）を進めてください。ログアウトの直前で止めて、私に知らせてください。
Skill: verify-before-claiming・data-privacy。応答は日本語。研究者の操作が要るところは手順を 1 つずつ示す。
```

## §0-後半 打ち込む用（ログインし直した後・新しいセッションで）

```
~/GSE-autostart-exp/STATE.md と .steering/_handoff/next-session-o1-stage-b-mac.md §2 後半を読んで、ログイン後の確認 → オフの試験 → 片付け（★ 退避したものを元に戻す）を進め、結果を .steering/20260928-o1-resilience-g1-g2-g5/g1-mac-autostart-experiment.md に追記して PR にしてください。
Skill: verify-before-claiming・data-privacy・git-workflow。応答は日本語。
```

## §1 状態（2026-09-29 に測った値）

| 何 | 値 |
|---|---|
| 確かめる配布物 | `experiments/20260801-controlled-friction-task/dist/_common/O1_実施用_macOS.zip`（v0.1.38・SHA-256 `f5ad9a90…`・`docs/o1-distribution-tag.md`） |
| 登録の仕組み | 同意確認の後に 1 回だけ `~/Library/LaunchAgents/com.johnd.gse-next.o1.plist`（`RunAtLoad` のみ・`KeepAlive` なし）を書き、配布フォルダに `o1.autostart`（中身 = exe のパス）・`~/.gse/o1_autostart_registered` を置く |
| 判定表（`autostart.rs` `decide`） | 印あり → 何もしない／印なし・記録なし → **Register**／印なし・記録あり・plist あり → **Repoint**（書き直す）／印なし・記録あり・plist なし → 何もしない（消した人に作り直さない） |
| ⚠️★★★ **この Mac の既存の状態** | `~/.gse/o1_participant_id` = `P009`・`~/.gse/o1_consent_ack`（08-30）・`~/.gse/g1_participant_id`・`~/Documents/GSE-sessions/gse_o1_20260910_*.ndjson` 2 本。★ **消さない**。前の handoff の「片付けで `o1_consent_ack`・O1 参加者 ID を消す」は、この状態を壊すので**採らない** → **退避して、最後に戻す** |
| 段階 A（済・09-28） | launchd 起動でも入力監視が効く・`o1_mode` が立つ・通知は未確認（`g1-mac-autostart-experiment.md`） |
| ⚠️ Mac の self-hosted runner | この Mac で動く（`actions.runner…macbook-air-m-arm64.plist`・研究者のユーザー）。**ログアウトで止まる** → ログアウトの前に `gh api repos/mikotomiura/GSE-prototype/actions/runners` で `macbook-air-m-arm64` が `busy=false` か見る。ログイン後に `online` に戻ったかも見る |

## §2 手順

### 前半（Claude ＋ 研究者・ログアウトの直前まで）

1. **退避**（⚠️ 最初に・消さない）:
   ```bash
   EXP="$HOME/GSE-autostart-exp"; mkdir -p "$EXP/backup-gse"
   date +%s > "$EXP/started_epoch"
   for f in o1_participant_id o1_consent_ack o1_autostart_registered; do
     [ -e "$HOME/.gse/$f" ] && mv "$HOME/.gse/$f" "$EXP/backup-gse/$f"
   done
   ls -la "$EXP/backup-gse"
   ```
   ★ 退避しないと、アプリは同意済みとして P009 のまま登録し、**実験用の P-ID を試せない**（`eligible` が同意済みで真になる）。
   ⚠️ `g1_participant_id` は動かさない（G1 の判定に使う・O1 は `o1::resolve` で G1 を落とす）。★ G1 の目印（`g1.mode`）が無い配布物なので影響しない、を `ls` で確かめる。
   ⚠️ 既に `~/Library/LaunchAgents/com.johnd.gse-next.o1.plist` があれば**止める**（前の実験の残り＝判定が Register でなくなる）→ 研究者に聞く。
2. **実験用コピー**（⚠️ 本番の受け口へ送らない）:
   ```bash
   cd "$EXP" && ditto -x -k "<repo>/experiments/20260801-controlled-friction-task/dist/_common/O1_実施用_macOS.zip" A
   # 展開先のフォルダ名を ls で確かめ、その中の g1-submit.json を届かない宛先に差し替える
   printf '{"endpoint":"http://127.0.0.1:9/exec","secret":"exp-dummy-secret-not-real-000000000"}\n' > "<展開先>/g1-submit.json"
   ```
   ⚠️ 差し替えた `g1-submit.json` を `cat` して**本番の endpoint が残っていない**ことを確かめる（★ 値そのものは出力に出さない: `grep -c script.google.com` が 0）。
3. **初回セットアップと起動**（研究者）: README【1】のとおり `初回セットアップ_mac.sh` → `gse-next.app` を開く。入力監視の許可を求められたら許可 → アプリを終了して開き直す。
   最初の画面で **実験用の P-ID `P998`**（⚠️ 実在の P-ID と重ならない値。登録ログには書かれない＝アプリ内の確認だけ）と同意の確認を行う。
4. **登録の確認**（Claude）:
   - `~/Library/LaunchAgents/com.johnd.gse-next.o1.plist` がある・`ProgramArguments` が展開先の `gse-next.app/Contents/MacOS/gse-next` を指す（`plutil -p`）
   - 展開先に `o1.autostart`（中身 = 同じパス）・`~/.gse/o1_autostart_registered` がある
   - applog に `O1 autostart: registered the login entry`
   - **研究者に聞く**: 「バックグラウンド項目が追加されました」の通知が出たか。システム設定 → 一般 → ログイン項目と機能拡張 の「バックグラウンドでの実行を許可」に出る**表示名**（README は「gse-next」と書いている）
5. **状態を書き残す**: `$EXP/STATE.md` に 退避したファイルの一覧・展開先のパス・`started_epoch`・4 の結果・runner の状態 を書く。
6. **ログアウトの前**: runner が `busy=false` か見る → 研究者に「ログアウト → ログイン → 1 分ほど何か打鍵 → `§0-後半` を新しいセッションで」と伝えて止まる。

### 後半（ログインし直した後・新しいセッション）

7. **自動で立ち上がったか**: `pgrep -fl gse-next` の親が launchd（`ps -o ppid= -p <pid>` が 1）・トレイが「計測中」（研究者）・
   `~/Documents/GSE-sessions/` に `started_epoch` より新しい `gse_o1_*.ndjson` があり、meta の `app_version = 0.1.38`・`o1_mode`・`key` 行が増える（⚠️ NDJSON は 8〜12 秒待つ・陰性対照: 打鍵しない 30 秒で増えない）。runner が `online` に戻ったか。
8. **オフにする**（研究者）: システム設定の「バックグラウンドでの実行を許可」で gse-next を**オフ**。→ plist が残っているか（`ls`）を記録（★ オフでも plist は消えない想定＝次の 9 で Repoint が走る条件）。
9. ★★ **オフのまま Repoint されても起動しないか**（security-checker の未確認点）: アプリを終了 → 同じ zip を**別のフォルダ** `B` に展開（`g1-submit.json` を同じく差し替え）→ `B` の `gse-next.app` を開く。
   - applog に `re-pointed the login entry`・plist の `ProgramArguments` が `B` を指す
   - システム設定で gse-next が**オフのまま**か（研究者の目視）
   - アプリを終了 → ログアウト → ログイン → **立ち上がらない**こと（⚠️ ここでセッションがもう一度切れる。STATE.md に 9 の途中まで書いてから）。
   ⚠️ **オンに戻っていたら** = 被験者が切っても次のフォルダで戻る欠陥 → README の【3】と `autostart.rs` の Repoint を見直す（★ 別タスク・版を上げる判断は研究者）。
10. **片付け**（⚠️ 消すのは実験で作ったものだけ）:
    ```bash
    pkill -f "GSE-autostart-exp/.*/gse-next" ; launchctl bootout gui/$(id -u)/com.johnd.gse-next.o1 2>/dev/null
    rm -f "$HOME/Library/LaunchAgents/com.johnd.gse-next.o1.plist" "$HOME/.gse/o1_autostart_registered"
    rm -f "$HOME/.gse/o1_participant_id" "$HOME/.gse/o1_consent_ack"     # ★ 実験で作られた P998 のもの
    mv "$EXP/backup-gse/"* "$HOME/.gse/"                                   # ★ 元に戻す
    cat "$HOME/.gse/o1_participant_id"                                     # ★ P009 に戻ったこと
    ```
    - `~/Documents/GSE-sessions/` と `~/Documents/GSE-submissions/` で **`started_epoch` より新しい**実験のファイルだけを消す（`find … -newer "$EXP/started_epoch"`・⚠️ 09-10 の 2 本は残す）。消す前に一覧を研究者に見せる。
    - システム設定のログイン項目に gse-next が残っていないか（研究者）。
    - 最後に `rm -rf "$EXP"`（★ backup-gse が空になったことを確かめてから）。
11. **記録**: `g1-mac-autostart-experiment.md` に「段階 B の結果」節を追記（通知・表示名・自動起動・オフ＋Repoint）。README と食い違えば README（両 OS）の直し方と、**版を上げずに**配布物だけ作り直せるか（README は zip にだけ入る）を書く。PR にする。

## §3 やらないこと
- 本番の受け口・受領台帳へ送る（`g1-submit.json` は必ず差し替える）。実在の P-ID を使う。
- `~/.gse/` の既存ファイル・09-10 の記録を消す（★ 退避して戻す）。
- G1 の配布物（`v0.1.36` 凍結）。Windows 実機の確認（§2-2 は別・Windows 側）。
