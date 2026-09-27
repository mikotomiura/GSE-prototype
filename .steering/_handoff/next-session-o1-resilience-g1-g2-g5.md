# 次セッション — O1 の耐障害性で保留していた G-1 / G-2 / G-5 を実装する

> 作成: 2026-09-28（`.steering/20260927-o1-release-tag-recut/` 完了直後・O1 の配布タグ = `v0.1.37`）。
> ⚠️ **このメモを一次資料にしない。** 数字・状態・行番号は着手時に測り直す。
> ★ 研究者の指示（2026-09-28）:「O1 に関しての保留である G-1〜G-5 などは具体的に修正しましょう」。

## §0 打ち込む用

```
.steering/_handoff/next-session-o1-resilience-g1-g2-g5.md を読んで、次を進めてください。
O1 の耐障害性で保留していた G-1（自動起動）/ G-2（定期 reconcile）/ G-5（32MB 超の送信）を実装し、
O1 用の新しいタグ（v0.1.38 想定）で配布物を作り直すところまで進めてください。
⚠️ まず git pull --ff-only。並行セッションがあれば最初から git worktree を切る（memory: parallel-sessions-share-checkout）。
/start-task（task 名: o1-resilience-g1-g2-g5）→ grilling skill で §3 の判断分岐を閉じる。
★ 被験者に見える動作（G-1）は同意文書・README（契約）に触れるので、文面の変更は研究者承認が先。
★ タグ push・Drive 差し替えは研究者承認が要る。
Skill: verify-before-claiming・rust-standards・data-privacy・git-workflow・subagent-delegation。
応答は日本語。
```

## §1 現在の状態（2026-09-28・測り直し済み）

| 何 | 値 |
|---|---|
| O1 の配布タグ | `v0.1.37`（`7b2846f`）。記録は `docs/o1-distribution-tag.md` |
| O1 ゲート | 通過 23 / 未達 1（同意文書の「未了」＝6 択 ESM 追補の採否・研究者判断待ち） |
| G1 ゲート | 通過 24 / 未達 2（記録票 A / B。C は 2026-09-28 に記入済み） |
| Drive | G1 / O1 の zip 4 点を研究者が配置し、Claude がコネクタでバイト数を照合済み（2026-09-28） |
| 実装済みの耐障害性 | ロックの heartbeat ＋ 所有印（PR #233・`v0.1.37` に収録。`gse-submit` で文字列を確認） |
| 代わりの見張り | O1 受領台帳＋途絶検知（`Form_O1/GSE_O1_Ledger.gs`・PR #235・配備済み。最終受領から 5 日で研究者に通知） |

## §2 課題（一次資料は `.steering/20260927-g1-o1-release-and-o1-resilience/decisions.md` の「T2 の調査」節）

⚠️ 行番号・定数は 2026-09-27 時点の値。**着手時に読み直す。**

### G-1 自動起動が無い（★ 最も影響が大きい）
- 被験者が PC を再起動したあとアプリを起動し忘れると、**その日から何も記録されない**。いまは受領台帳の「5 日途絶」で**後から気づく**だけ。
- 調査結果（未裏取りの部分あり）: `tauri-plugin-autostart` 2.5.1 は `auto-launch = "0.5"` 固定で、**macOS は LaunchAgent**（`~/Library/LaunchAgents/…plist`・`RunAtLoad`）か AppleScript のログイン項目。SMAppService は使えない。Windows は HKCU Run キーに `current_exe()`（`.bat` を経由しない）。
- ⚠️ **未検証で、実装より先に確かめること 3 点**:
  1. ad-hoc 署名の `.app` をログイン時に LaunchAgent で起動したとき、**入力監視（TCC）の許可が維持されるか**。
  2. `o1.mode` の目印の探索が「実行ファイル基準」か「カレントディレクトリ基準」か（**LaunchAgent / Run キーの起動では cwd が変わる** → 目印が見つからないと**黙って通常モードで動き、ランダムプローブが復活する**。memory `gate-green-but-artifact-broken` ② と同型の事故）。
  3. 被験者に見える通知が出るか（macOS の「ログイン項目が追加されました」など）。
- → ★ Mac 実機で plist を手で置く小実験（再ログイン → NDJSON が `gse_o1_*` で出るか・`o1_mode` が meta に立つか）で 1 と 2 を先に測る。
- ⚠️ 被験者に見える動作の変更 ＝ **同意文書・README の文面（契約）に触れる** → 文面案を作って研究者承認を取ってから配る。**やめ方（自動起動の解除手順）も文面に要る。**

### G-2 定期 reconcile が無い
- 送信（reconcile）は起動時とローテート時だけ。回線断で失敗した `.age` は次の契機まで残る。
- 調査時の判断案: 周期は長め（例 6 時間）・**O1 だけ**（`is_o1()` で囲む）・ロックの stale 判定は heartbeat 化済み（PR #233）なので定期化の前提は満たした。
- 未決: 新しい `ReconcileReason` を足すか既存の値を流用するか（**フロントの契約**・App.tsx の数値・DTO に波及する）→ 読んでから決める。送信不要でも子プロセス起動・NDJSON 全読み・ロック書込が毎回走る（通信量・負荷）。

### G-5 32 MB 超のファイル
- GAS は `too large` を **HTTP 200 + `ok:false`** で返す（`Form_O1/GSE_O1_Submit.gs`）。クライアントに 32 MB の定数・送信前検査・試行回数の上限・隔離が**無い** → **起動とローテートのたびに同じ 32 MB 超を base64 で再送し続け、研究者に届かない**。O1 の被験者向け提出 UI は `g1Mode` の内側なので、被験者には何も出ない。
- 実測は 20〜23 MB/日で余裕は 1.4 倍（緊急ではないが、長く書いた日に起きる）。
- 調査時の判断案: クライアントで送信前に 32 MB 超なら**再送を止めてログに明記**（隔離 or 印を付ける）。⚠️ **データを捨てない**（研究者が手で回収できる形で残す）。受け口側は変えない方針（GAS の `doPost` は変えない）で、受領台帳の途絶検知が代わりの見張りになる。
- ⚠️ 32 MB の出所（GAS の上限か自前の定数か）を一次で確かめてから定数を置く。

### 併せて（任意・研究者に確認）
- **G-3** スリープをまたいだ確認: Claude Code が `caffeinate` を握るので私からはスリープできない（memory `claude-code-caffeinate-blocks-sleep-tests`）→ 研究者の手順として渡す。
- **G-4** NDJSON の粒度: `extract.py` は変えない（O1 のデータを解析に流す時点で対応。既存の申し送りを維持）。
- **鮮度ゲートの盲点**（Codex MEDIUM・2026-09-27）: `scripts/check-o1-release-readiness.sh` の鮮度判定は `src-tauri/src` / `src-tauri/Cargo.toml` / `src` だけを見る。`Cargo.lock` / `tauri.conf.json` / フロント依存 / 梱包スクリプトの変更は「古い」と判定されない。今回 `Cargo.toml` に依存（autostart）を足すなら関係する。
- **heartbeat の実機確認**（Codex MEDIUM）: ロックが奪われないことを実機で通したことはない。

## §3 grill で閉じる判断分岐（研究者に聞く）

1. G-1 をやるか・どの方式か（プラグイン / LaunchAgent を自前で置く / 被験者の手順で「ログイン項目に追加」してもらう）。**既定で ON か、初回に同意を取って ON か。**
2. G-1 の文面（同意文書・README）の変更案を誰がいつ承認するか。既に配った `v0.1.37` の被験者への扱い（差し替えるか）。
3. G-2 の周期と、`ReconcileReason` の扱い。
4. G-5 で「送らないと決めたファイル」をどこに置き、研究者がどう気づくか（受領台帳だけで足りるか）。
5. 新しいタグの番号（`v0.1.38` 想定）。G1 は `v0.1.36` のまま凍結（ADR-034 D3）。

## §4 手順（案）

1. 状態を測り直す: 両ゲート・`git log v0.1.37..origin/main`。
2. G-1 の小実験（Mac・plist を手で置く）→ 結果で方式を決める。Windows は CI と研究者の実機に頼る（memory `windows-only-code-needs-ci`）。
3. 実装（G-5 → G-2 → G-1 の順が小さい順）。各修正は TDD（`/fix-bug`）・両 OS に対のテスト・変異検査（壊して赤を見る）。
4. `/finish-task`（code-reviewer ＋ security-checker ＋ `/cross-review`）→ PR → CI 緑 → merge。
5. 版上げ PR → merge → 研究者承認でタグ push → CI → Release の実体検証（**修正の目印は `gse-submit` 側に出る**ことがある。`docs/o1-distribution-tag.md` v0.1.37 節の方法）。
6. `make-common-app-zip.sh --mode o1 --tag vX --config Form_O1/o1_submit.json` → 独立再検算 → `docs/o1-distribution-tag.md` に節を追記 → 研究者が Drive を差し替え → コネクタでバイト数を照合。

## §5 やらないこと

- G1 の配布物（`v0.1.36` 凍結）。
- 同意文書の「未了」（6 択 ESM 追補）の採否。
- GAS の `doPost` の変更（受け口は変えない方針）。

## §6 一次資料（読む順）

1. `.steering/20260927-g1-o1-release-and-o1-resilience/decisions.md`（T2 の調査・G-1〜G-5）
2. `src-tauri/src/reconcile.rs` / `src-tauri/src/o1.rs` / `src-tauri/src/submission.rs` / `src-tauri/src/bin/submit.rs`
3. `Form_O1/GSE_O1_Submit.gs`（`too large` の返し方）・`Form_O1/GSE_O1_Ledger.gs`（途絶検知）
4. `docs/o1-distribution-tag.md`・`.steering/20260927-o1-release-tag-recut/`（タグの切り方の型）
5. `scripts/check-o1-release-readiness.sh`
