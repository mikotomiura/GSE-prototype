# G-1 の Mac 小実験 — LaunchAgent で起動しても O1 として記録できるか

> 目的: 実装より先に、handoff §2 G-1 の未検証 3 点を実機で確かめる。
> 1. LaunchAgent（launchd）から起動したとき、**入力監視（TCC）の許可が保たれるか**
> 2. `o1.mode` の目印が見つかり、**meta に `o1_mode` が立つか**（一次のコード読みでは実行ファイル基準＝見つかるはず）
> 3. 被験者に見える通知（「バックグラウンド項目が追加されました」など）が出るか

## 前提（一次で確かめたこと・2026-09-28）
- プラグイン（`tauri-plugin-autostart` 2.6.0 → `auto-launch` 0.5.0 `src/macos.rs`）が書く plist は
  `~/Library/LaunchAgents/<app_name>.plist`（`app_name` = `gse-next`）。中身は `Label` / `ProgramArguments`（`.app/Contents/MacOS/gse-next` の `canonicalize` 済みパス）/ `RunAtLoad=true` だけ。
  → 下の手順はこれと同じ plist を手で置く。
- ログイン項目（AppleScript）方式は System Events を操作する＝ **別の TCC 確認（オートメーション）が出る**。LaunchAgent が駄目だったときだけ測る。
- 記録先は `~/Documents/GSE-sessions/`（`logger.rs:2780`）。

## ⚠️ 安全策（本番の受け口へ送らない）
実験用コピーの `g1-submit.json` の `endpoint` を**届かない宛先**（`http://127.0.0.1:9/exec`）に差し替える。
→ reconcile は失敗し、`.age` はローカルに残るだけ（本番の O1 受け口・受領台帳に何も届かない）。
⚠️ 実験中は研究者自身の打鍵の**時刻だけ**が記録される（内容は記録しない）。終わったら下の「片付け」で消す。

## 手順

### 準備（Claude が実行できる）
```bash
EXP="$HOME/GSE-autostart-exp"           # ⚠️ 非 ASCII を含まない場所
SRC="<repo>/experiments/20260801-controlled-friction-task/dist/_common/O1_実施用_macOS"
mkdir -p "$EXP" && cp -R "$SRC/gse-next.app" "$SRC/o1.mode" "$EXP/"
printf '{"endpoint":"http://127.0.0.1:9/exec","secret":"exp-dummy-secret-not-real-000000000"}\n' > "$EXP/g1-submit.json"
```

### 段階 A: launchctl で読み込む（ログアウト不要・Claude が実行できる）
launchd から起動されるので、親プロセスはログイン時と同じ launchd になる。
```bash
PL="$HOME/Library/LaunchAgents/gse-next.plist"
BIN="$(cd "$EXP/gse-next.app/Contents/MacOS" && pwd -P)/gse-next"
cat > "$PL" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>gse-next</string>
<key>ProgramArguments</key><array><string>$BIN</string></array>
<key>RunAtLoad</key><true/>
</dict></plist>
EOF
launchctl bootstrap gui/$(id -u) "$PL"
```
- **研究者**: 入力監視の許可を求められたら許可する（コピーは別のアプリとして扱われることがある）。
  許可したあと、一度アプリを終了（トレイ → 終了）してから `launchctl kickstart gui/$(id -u)/gse-next` で起こし直す。
- 数十秒打鍵してから確かめる（⚠️ NDJSON は 8〜12 秒待たないと 0 件に見える・memory）:
  - 新しい `~/Documents/GSE-sessions/gse_o1_*.ndjson` ができるか
  - 1 行目の meta に `"o1_mode"` があるか・`app_version` が 0.1.37 か
  - `key` 行が増えるか（← **TCC が効いている証拠**。陰性対照: 打鍵しない 30 秒で増えないこと）
  - applog（`~/Documents/GSE-sessions/` の app log）に tap 失敗・liveness の警告が無いか
  - 画面右上に「バックグラウンド項目が追加されました」系の通知が出たか（**研究者が目で見る**）

### 段階 B: 本当のログイン（研究者が実行・Claude のセッションは切れる）
段階 A で plist を置いたまま、ログアウト → ログイン。ログイン後 1 分ほど打鍵し、段階 A と同じ 4 点を見る
（Claude の新しいセッションで確かめてもよい）。

### 片付け
```bash
launchctl bootout gui/$(id -u)/gse-next 2>/dev/null; rm -f "$HOME/Library/LaunchAgents/gse-next.plist"
rm -rf "$HOME/GSE-autostart-exp"
# 実験で増えた gse_o1_*.ndjson / .age / .sent を消す（実験開始時刻より新しいものだけ）
```
- システム設定 → 一般 → ログイン項目と機能拡張 の「バックグラウンドでの実行を許可」に `gse-next` が残っていないか確認。

## 結果（段階 A・2026-09-28 01:52〜01:56 JST・Claude が実行・研究者が入力監視を許可）
⚠️ 実際に置いた plist の Label は実装予定のもの（`com.johnd.gse-next.o1`）。中身はプラグインと同じ 3 キー。

| 確かめたこと | 結果 | 根拠 |
|---|---|---|
| launchd から起動されるか | ✅ `launchctl print` で `state = running`・プロセスの親 pid = 1 | `ps -o ppid` |
| `o1.mode` の目印が見つかるか（懸念 2） | ✅ meta に `"o1_mode":"marker"`・`app_version = 0.1.37` | NDJSON 1 行目 |
| 入力監視（TCC）の責任主体 | ✅ 許可の要求は **gse-next 自身**として出た（launchd や端末ではない） | applog `Input Monitoring permission not granted. Opening System Settings` |
| 許可後、launchd 起動で打鍵が記録されるか（懸念 1） | ✅ `CGEventTap installed … tap_mode=Input Monitoring input_monitoring=true`・トレイ「計測中」・`key` 行 6 | applog・NDJSON |
| 対照 | 許可前の launchd 起動（`gse_o1_…165255`）は `key` 0 行・トレイ `HookDown` | 同上 |
| 送信 | ダミー宛先で `endpoint が https:// で始まっていません` により送信せず | applog |
| 被験者に見える通知（懸念 3） | ⏳ 研究者の目視待ち | — |

副次的な観察:
- 許可を切り替えた直後に 2 個目の起動が来て、single-instance が弾いた（`second instance launch detected and blocked`）。記録は分かれていない。
- `launchctl bootout` だけではプロセスが止まらなかった（`RunAtLoad` のみで `KeepAlive` なしのため、launchd は起動するだけで管理を手放すとみられる）。`kill`（TERM）で止まった。→ 解除手順は「plist を消す／システム設定でオフ」＋「アプリを終了」の 2 つに分けて書く。
- 片付け: plist・実験用コピー・実験で増えた NDJSON 2 本を削除済み。`GSE-submissions` は増えていない。

未実施: 段階 B（本当のログイン）。★ 実装後の新しいビルドが**自分で plist を書く**形で確かめるほうが本番に近いので、そちらでまとめて行う。

## 結果（段階 B・2026-09-29 13:35〜14:22 JST・配布 zip v0.1.38 が自分で plist を書く形）
> 手順は `.steering/_handoff/next-session-o1-stage-b-mac.md` §2。ログアウトをまたぐため 3 セッションに分けて行い、状態は `~/GSE-autostart-exp/STATE.md` に書き継いだ（片付けで削除済み・中身は下に転記）。
> 安全策: 既存の `~/.gse/o1_participant_id`（P009）・`o1_consent_ack`（08-30）を退避してから実験用 P-ID `P998` で同意し、最後に戻した。`g1-submit.json` は `http://127.0.0.1:9/exec` に差し替え（`script.google.com` 0 件）。zip の SHA-256 `f5ad9a90…` は `docs/o1-distribution-tag.md` と一致。

| 確かめたこと | 結果 | 根拠 |
|---|---|---|
| 同意の後に登録されるか（Register） | ✅ `~/Library/LaunchAgents/com.johnd.gse-next.o1.plist`（`RunAtLoad=true` のみ・`ProgramArguments` = 展開先 A の `gse-next.app/Contents/MacOS/gse-next`）・A に `o1.autostart`（同じパス）・`~/.gse/o1_autostart_registered` | `plutil -p`・applog `O1 autostart: registered the login entry (LaunchAgent com.johnd.gse-next.o1)` |
| 登録の直後に launchd へロードされるか | ロードしない（`launchctl print` → not found）。効くのは次のログインから。★ 実装（登録側に `launchctl` の呼び出しが無く plist を置くだけ）と整合 | `launchctl print` |
| 被験者に見える通知 | ✅ 出た。研究者の記録は「gse-next はバックグラウンドで…」（見出しの文言は控えていない） | 研究者の目視 |
| システム設定の表示名 | ✅ 「バックグラウンドでの実行を許可」に **`gse-next`**・スイッチ ON（README【3】の名前と一致）。副題は「バックグラウンドで実行されていません」・アイコンは汎用の実行ファイル | 研究者の目視 |
| 本当のログインで自動起動するか | ✅ 13:51 のログイン → `gse-next` が 13:51:51 に起動・親 pid = 1・`launchctl print` で `state = running`・`runs = 1` | `last`・`ps -o ppid`・`launchctl print` |
| 自動起動で O1 として記録するか | ✅ 新しい NDJSON の meta に `app_version = 0.1.38`・`o1_mode = marker`・`key` 60 行（フィールドは `category`/`press`/`t` のみ＝内容なし）。陰性対照: 打鍵しない 45 秒で 60 → 60 | NDJSON（片付けで削除済み） |
| トレイ | ✅ 「計測中」 | 研究者の目視（⚠️ 画面の「記録中 · 作業の種類」の印は見ていない） |
| システム設定でオフにしたとき | ★ **その瞬間に動いていた gse-next が終了**した。`launchctl print` → Could not find service（bootout された）。plist は残る | 研究者の体感・`pgrep`・`ls` |
| ★★ オフのまま別フォルダ B から開く（Repoint） | ✅ applog `re-pointed the login entry` → plist の `ProgramArguments` が B を指す・B に `o1.autostart`。同意画面は出ない（`~/.gse` の同意を再利用）。**スイッチはオフのまま・通知も出ない** | applog・`plutil -p`・研究者の目視 |
| ★★ オフ＋Repoint の後のログインで立ち上がらないか | ✅ 14:20 のログイン → 14:21 に `pgrep` 0 件・`launchctl print` not found・`print-disabled` に行なし・B の起動（`…051211`）より新しい `gse_o1_*` が無い・applog の最終行は 05:12:12Z。陽性対照 = 上の 13:51（オン）では立ち上がった | `last`・`pgrep`・`launchctl`・`ls` |
| Self-hosted runner | ログアウト前に `busy=false` を確認・どちらのログインの後も `online` に戻った（13:5x は `busy=false`・14:2x は `busy=true`＝ジョブを受けて動いている） | `gh api …/actions/runners` |

→ ★ **README【3】の「オフにしたあと、アプリが勝手にオンに戻すことはありません」は、Repoint（別フォルダに置き直した）場合も含めて macOS 実機で成り立つ**（1 回のログインでの実測・陽性対照あり）。 security-checker の未確認点はこれで閉じた（Mac のみ。Windows は別）。

副次的な観察:
- ⚠️ **ログアウトはきれいな終了にならない。** ログアウト前に動いていたセッションには終了行が無く、次の起動の orphan sweep が閉じた。そのとき `session_end` は **sweep した時刻**になり、実際の最終イベント（例: 04:56 台）とは違う（`…045158` は 05:12:11Z で閉じられた）。→ 自動起動の運用では「ログアウト／再起動のたびに 1 本ずつ孤児ができて、終了時刻が次の起動まで延びる」。集計でセッションの長さに `session_end` を使うなら要注意（★ 影響の有無は未調査・別タスク候補）。
- 初回、入力監視を許可したあとの終了は異常終了扱いになり、次の起動の orphan sweep がそのファイルを閉じた（段階 A と同じ）。
- ログイン項目のアイコンが汎用の実行ファイルになるのは、plist が `.app` ではなく中の実行ファイルを指すためとみられる（未検証）。副題「バックグラウンドで実行されていません」は登録直後（未ロード）の表示で、ログイン後にどう変わるかは見ていない。
- `log show`（unified log）で launchd / BTM の記録を探したが、陽性対照（13:51 の起動）でも 0 件だった → 根拠には使っていない。

README との食い違い（配布物の直し方）:
- **食い違いはない**（表示名 `gse-next`・手順 1〜3・「勝手にオンに戻さない」）。⚠️ 通知は出たが、README の「バックグラウンド項目が追加されました」と**見出しの文言が一致するかは照合していない**（研究者の記録は本文の「gse-next はバックグラウンドで…」のみ）。
- 補足の候補（★ 研究者の判断・直すなら両 OS）: 「オフにすると、**その場で**アプリも終了し、記録も止まります」。今の文は、オフにしても今日の記録は続くと読める。Windows で同じ挙動かは未確認（スタートアップアプリの無効化は動いているプロセスを止めない可能性がある）→ Windows 側で測ってから書く。
- README は zip の中にだけあり、アプリのバイナリに埋め込まれていない → 直すなら **版を上げずに** zip を作り直せる。ただし zip の SHA-256 が変わるので、`docs/o1-distribution-tag.md` に新しい値を追記する必要がある。

片付け（14:22 に完了）: `pkill` / `launchctl bootout` → plist・`~/.gse/o1_autostart_registered`・P998 の `o1_participant_id` / `o1_consent_ack` を削除 → 退避した 2 つを `~/.gse/` に戻した（`o1_participant_id` = P009 を確認）→ `~/Documents/GSE-sessions/` の実験 NDJSON 4 本を研究者の確認のうえ削除（`.o1_clock_hwm`・`gse-app.log` は既存ファイルで更新されただけなので残した。`GSE-submissions` は増えていない）→ `~/GSE-autostart-exp` を削除。システム設定のログイン項目から gse-next が消えたことを研究者が確認した。
