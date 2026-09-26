# 決定記録 — g1-o1-release-and-o1-resilience

> 出所の格: 「一次」= 私が 2026-09-27 に自分で開いた行。「調査報告」= subagent の要約（**断定の根拠にしていない**）。

## 0. 状態の測り直し（一次・2026-09-27 00:5x JST）
| 何 | 実測 |
|---|---|
| PR #232 | MERGED（`24c5e3e`） |
| main の CI（run 36253294897・`24c5e3e`） | completed / **success** |
| バージョン | `Cargo.toml` / `tauri.conf.json` / `package.json` / `Cargo.lock`(`gse-next`) すべて 0.1.36 |
| 最新タグ | `v0.1.35`（`v0.1.36` は未作成） |
| G1 ゲート | 通過 17 / 未達 3（記録票 A/B/C のみ） |
| O1 ゲート | 通過 21 / 未達 2 |
| Mac ランナーのディスク | 空き 21 GiB（使用 38%） |

## T2 の調査（subagent 4 本・調査のみ）と一次での裏取り

### G-1 自動起動（A1: general-purpose / sonnet）
調査報告（外部一次＝tauri-apps/plugins-workspace・auto-launch 0.5.0 のソース逐語）:
- `tauri-plugin-autostart` 2.5.1 は `auto-launch = "0.5"` 依存。**macOS は SMAppService 不可**（0.6 系にはあるがプラグインは 0.5 固定）。選べるのは LaunchAgent（既定・`~/Library/LaunchAgents/{app_name}.plist`・`RunAtLoad`）か AppleScript のログイン項目。
- ⚠️ LaunchAgent モードは **`.app` 内の実行ファイル本体**（`…/Contents/MacOS/gse-next`）を直接起動する。Windows は HKCU Run キーに `current_exe()` を登録（`.bat` を経由しない）。
- **不明（未検証）**: ad-hoc 署名でログイン時起動しても入力監視（TCC）が維持されるか／被験者に見える通知の有無／`o1.mode` 目印（同フォルダ基準）が exe 直起動で効くか。
- 導入に必要な変更の種類: `Cargo.toml` 依存・`lib.rs` のプラグイン登録・（JS から呼ぶ場合のみ）capabilities。

**判断（メイン）**: 実装に進まない。理由 3 つ —
(1) 被験者から見える動作の変更＝同意文書・README（契約）に触れる → 研究者承認が先（handoff §4-6）。
(2) **実機で確かめられる 2 点が未検証**（TCC 維持・`o1.mode` 目印の解決）。これは Mac 実機で LaunchAgent を手で置く小実験（plist を書いて再ログイン→NDJSON が出るか）で確かめられるので、承認を待たずに**実験手順として用意できる**。
(3) `o1.mode` 目印の探索が「実行ファイル基準」か「カレントディレクトリ基準」かは**まだ読んでいない**（次に一次で読む）。→ 読む前に LaunchAgent 案の可否を断定しない。

### G-2 定期 reconcile（A2: impact-analyzer）
一次で裏取り済み: `LOCK_STALE_AFTER` = 3600s・timeout = 300s 固定・不変条件テスト `300*10`（`reconcile.rs:713,1271-1275`）／ロックは mtime 固定で heartbeat 無し・stale で `remove_file` して奪う（`:140-175`）。
調査報告（未裏取り）: 未送信 N≥12 で 1 run が 3600s を超えうる／O1 では G1 の「ブロック中スキップ」が実質無効／`ReconcileReason` の追加は label・DTO・App.tsx の数値契約に波及／「送信不要」でも子プロセス起動・NDJSON 全読み・lock 書込は毎回発生。
**判断（メイン・案）**:
- 定期 reconcile を足すなら、**(a) 周期は 1 時間でなく長め（例 6 時間）** にして全読みのコストを下げ、**(b) O1 だけ**（`is_o1()` で囲む）、**(c) ロックの stale 判定を「mtime 固定」から heartbeat 更新（または stale 閾値を O1 の滞留に合わせる）へ**直す。(c) は既存の潜在欠陥（O1 で回線断が約 12 日続くと二重実行）で、定期化とは独立に直す価値がある。
- 新しい `ReconcileReason` は足さず既存の値を流用するかは、フロント契約（G1 のみ表示）を読んでから。**未決 → 実装前に研究者に「入れるか」を問う**（G-2 は被験者から見えない動作だが、通信量が増える）。

### G-4 NDJSON の粒度（A3: file-finder）
一次で裏取り済み: `extract.py:314` は `file_end = session_end or last_t` で、`:328` で右側打ち切りギャップを足す。
調査報告: **観測窓の終端として使う消費者はこの 1 件だけ**（他は「閉じ済み判定」「猶予の起点」「境界」）。
**判断**: 探索トラック（確証に使わない）で、`README.md` の申し送りが既に同じ懸念を書き、Phase1/G1 由来の既存結果は影響なし。→ **今回は `extract.py` を変えない**。O1 のデータを流す時点で `min(session_end, last_t+猶予)` か除外を入れる、という既存の申し送りを維持する。O1 事前登録の解析単位「人×日」は**時刻で集約**する点だけ `drafts/03` §3 に反映する（研究者が承認する文面のため、追記案として提示のみ）。

### G-5 32 MB 超（A4: file-finder）
一次で裏取り済み: GAS は `too large` を **HTTP 200 + `ok:false`** で返す（`GSE_O1_Submit.gs:218-220`）。O1 の被験者向け提出 UI は**すべて `!!g1Mode &&` の内側**（`App.tsx:546〜877`）。
調査報告: クライアントに 32 MB 定数・送信前検査・4xx/5xx の区別・試行回数上限・隔離は**無い**。失敗した `.age` は残り、**起動のたびとローテートのたびに同じ 32 MB 超を base64 で再 POST し続ける**。研究者向けは `tracing::error!` と `SUBMIT_LAST_ERROR`、被験者には（O1 では）何も出ない。
**判断（メイン・案）**: 実測は 20〜23 MB/日で 32 MB には 1.4 倍以上の余裕があるので**緊急ではない**が、超えたときは「静かに再送し続けて研究者に届かない」形になる。→ (1) 受け口側で `too large` が起きたら**研究者に通知**（GAS の doPost は変えない方針なので、受領台帳側で「ファイルが来ない P-ID」として検知される＝T3 提案 1 が代替統制になる）、(2) クライアントで送信前に 32 MB 超なら**再送を止めてログに明記**。(2) はコード変更なので O1 用の別タグに入れる。

### G-3 スリープ跨ぎの実機検証
Claude Code が `caffeinate` を握るため私からは `pmset sleepnow` を実行できない（memory）。→ 研究者手順として渡す（§4-7）。

## 未着手・保留（研究者の承認待ち）
G-1 の実装 / G-2 の実装 / G-5(2) の実装 / T3 の GAS 変更。
