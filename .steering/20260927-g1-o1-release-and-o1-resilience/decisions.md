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

## 実装した修正（2026-09-27・研究者の選択: ロックの stale 判定のみ）
- 研究者確認: G-1 / G-2 / G-5 は **O1 だけの問題**（G1 は 70 分・1 回きり）。今回実装するのは、共有コードだが G1 の挙動を変えないロックの heartbeat のみ。G-1 / G-2 / G-5 は実装しない（保留・O1 配布前に再度決める）。
- 変更: `reconcile.rs` に `ReconcileLock::refresh()`（mtime を now へ）を足し、梱包・送信の**1 本ごとの直前**に呼ぶ。stale 判定は「1 本ぶんを大きく超えて更新が無い」だけになり、未送信の本数に依存しない。`LOCK_STALE_AFTER` は据え置き（3600s・× 10 の余裕・既存テスト維持）。
- テスト 2 本: 直接（対照つき: 更新なしは奪われる / refresh すれば奪われない）＋配線（3 本の O1 送信で毎回ロックが新しいことを uploader が確認）。**変異検査**: ループ内の refresh を消すと配線テストが赤・refresh を no-op にすると 2 本とも赤（緑から壊して赤を確認済み）。
- 検証: `cargo test --workspace --features package` 813 passed / fmt / clippy `-D warnings` すべて緑（Mac）。⚠️ **Windows は CI 待ち**（`File::set_modified` は std だが実機未確認）。
- ⚠️ 既知の残り: 奪われた側の `Drop` が後続のロックを消す挙動は直していない（heartbeat で奪取自体がほぼ起きなくなるため・YAGNI）。死んだ収束器のロックは 3600s 後に奪える。

### レビュー対応（code-reviewer / security-checker・2026-09-27・すべて一次で確かめてから反映）
| 指摘 | 判定 | 対応 |
|---|---|---|
| code-reviewer **HIGH**: 梱包側の `refresh` を消してもテストが緑 | **本物**（梱包側だけ消す変異で 29/29 緑を実測）。⚠️ 私の最初の変異は両方を同時に消していたので**送信側しか証明できていなかった** | スレッドローカルの呼び出し回数カウンタ（`cfg(test)`）＋テスト `refresh_is_called_once_per_package_and_once_per_upload`（梱包 N＋送信 M ＝ N+M 回）。**梱包側だけ／送信側だけ消す変異が個別に赤**になることを確認 |
| code-reviewer MEDIUM: `LOCK_STALE_AFTER` の旧因果（600 秒で壊れる）が heartbeat 後は不成立・`HttpUploader` 側が未改訂 | 本物 | 2 箇所を「必要条件は 1 本ぶんの所要が閾値より十分に短いこと」へ改訂 |
| code-reviewer MEDIUM: 「12 本 × 300 = 3600」は `>` を満たさない | 本物（算術） | 「13 本以上」へ訂正 |
| code-reviewer/security-checker: `refresh` がパスで開き直す（奪われた後は他人のロックを延命）・所有者識別なし・symlink 追随（LOW） | 指摘は正しい | **今回は直さない**: fd 保持は Windows の「開いたまま `remove_file`」の挙動を手元で確かめられず（CI の Windows でしか検査できない）、heartbeat で奪取自体がほぼ起きなくなるため効果が小さい。所有者識別（pid＋nonce）は別スコープ。→ 残課題として記録。`NotFound` の警告だけ区別して出す（切り分け用） |
| LOW: `backdate_lock` の unwrap / `mem::forget` / impl ブロックの分割 | 任意 | `expect` に変更。他は現状維持 |
| security-checker: プライバシー規約違反なし（URL・メール・ID・氏名・時刻 0 件・`tracing` のパスは提出物に載らない） | — | 対応不要 |

### /cross-review（Codex）と所有印の実装（2026-09-27）
Codex（`scripts/run-codex-review.sh 24c5e3e..016b5f2 -- src-tauri/src/reconcile.rs`）の指摘: (1) **高** ロック喪失後も続行し他人のロックを延命・削除する（＝ code-reviewer / security-checker の MEDIUM と**同じ内容・3 系統一致**）／(2) 中 「必要条件は送信 timeout だけ」は過剰な保証（梱包・読み込みは timeout で抑えられない）／(3) 中 奪取シナリオの回帰テストが無い。
一次で確認して**すべて採用**（前回「今回は直さない」とした判断を、3 系統一致を受けて**撤回**した。fd 保持は Windows の挙動が手元で確かめられないため採らず、**所有印方式**にした）:
- `acquire` がロックファイルへ**所有印**（PID＋ns＋連番）を書く。`refresh` は中身が自分の印のときだけ mtime を進め、違う／消えていれば `lost` を立てる。`Drop` は自分の印のときだけ消す。`reconcile()` は梱包・送信のループで `lost` を見て**中断**し、「ロックを失いました」を errors に出す（収束型なので残りは次の機会に収束する）。所有印を書けなければ Unavailable（Busy に倒さない）。
- 残る限界: 確認と操作の間の競合窓は残る（OS の排他ロックではない。Rust 1.88 の std に `File::try_lock` は無い）。窓は数マイクロ秒で、奪取自体が heartbeat で稀になっている。
- `LOCK_STALE_AFTER` のコメントは「前提は更新の間（1 本の梱包・1 本の送信）が閾値より十分に短いこと。梱包・読み込みは timeout で抑えられていない」に直した。
- テスト 2 本追加（A が奪われても B のロックを延命・削除しない／送信中に奪われた収束が中断して他人のロックを残す）。**変異 3 種（Drop 無条件削除・refresh が所有を見ない・送信ループが中断しない）がそれぞれ赤**になることを確認。
- ⚠️ Codex の (3) の後半「各梱包の**直前**に更新されること」は回数では保証できない、は正しいが、位置は `lock.refresh()` が `package_session_as` の直前の同じブロックにあることをコードで確認済み（回数テストは梱包側・送信側の削除を検出する）。
