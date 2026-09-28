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
