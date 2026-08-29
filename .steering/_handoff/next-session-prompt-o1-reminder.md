# 次セッション開始プロンプト — **O1 に未提出者リマインダーを設計する**

> ★ このファイルの「===」以下をコピペして開始する。
> ⚠️ 前セッションから `/clear` して**新セッション**で始めること。
> ★ モデル: **Opus**（⚠️ 「被験者へ働きかけてよいか」の研究デザイン判断を含む）。

---

===

## §0 ⚠️ 最初に読むもの

1. `CLAUDE.md`
2. `.claude/skills/verify-before-claiming/SKILL.md`
3. `.claude/skills/data-privacy/SKILL.md`（⚠️ ロスターのメール列を読む設計になる）
4. `.claude/skills/intervention-design/SKILL.md`（⚠️ 「介入」との境界を確認する）
5. `.steering/20260829-phase1-gas-reconciliation/design.md` **§2**（★ 棚卸し表・移植元の一覧）
6. `docs/research-positioning.md` の **§8「機会保存」**（★ 主張範囲との整合）

## §1 ★ 何が決まっているか

**研究者判断 2026-08-29: 「足す方向で検討したい」。**

⚠️ ただし **まだ「実装してよい」ではない**。★ 設計を出して、もう一度判断を仰ぐ。

## §2 ⚠️★★★ なぜ要ると考えたか（★ 実測に基づく）

| | Phase1 | G1 | **O1** |
|---|---|---|---|
| 定期実行トリガ | 2 本 | 2 本 | ⚠️ **0 本** |
| トリガ合計 | 4 | 3 | ⚠️ **1**（フォーム提出のみ） |
| 進捗の可視化 | 進捗ダッシュボード | 提出状況タブ | ⚠️ **無し** |
| 未提出への働きかけ | `sendReminders`（日次＋停滞） | 無し | ⚠️ **無し** |

★ `Form_O1/GSE_O1_Submit.gs` は受け取った `.age` を **`DriveApp` でフォルダに置くだけ**で、
`appendRow` / `getSheetByName` / `insertSheet` の呼び出しが **1 件も無い**（実測）。
→ ⚠️ **誰がいつ出したかは、Drive のファイル名を人が読むしかない。**

⚠️★★★ そして O1 の受付メールは**逐語**でこう言っている:

> 「アプリが起動していない日は、記録がまるごと空になります。」

→ ★ **欠測は起きたあとでしか分からず、事後に埋め合わせできない。**

## §3 ★ 移植元（★ すべて `Form_Phase1/GSE_Phase1_Form_Builder.gs` にある・取り込み済み）

| 関数 | 役割 |
|---|---|
| `sendReminders` | 日次リマインド＋停滞チェックインの本体 |
| `reminderClassify_` | ★ **送信判定の一元化**（予定タブと同一真実源）。⚠️ 参加フェーズのゲートあり |
| `reminderSendingAllowed_` | ★ fail-closed な送信ゲート（読めなければ送らない） |
| `doGet` / `reminderConfirmPage_` / `reminderRecordResponse` | メールのボタン受け（ウェブアプリ） |
| `reminderLogAppend_` / `reminderLogQuery_` / `buildReminderLogTab_` | 応答・送信ログ（冪等判定の土台） |
| `buildReminderPlanTab_` | 「本日のリマインド予定」監視タブ |
| `installReminderTrigger` / `removeReminderTriggers` | トリガの設置・削除 |

★ Phase1 版は**既に運用実績がある**（⚠️ ただし現在は「終了」トグルで停止中）。

## §4 ⚠️★★★ 設計で必ず閉じること

1. **⚠️ 研究デザイン**: 日次リマインドは `docs/research-positioning.md` の「機会保存」と衝突しないか。
   ★ 私の見立ては「**作業中の介入ではなく運用連絡なので衝突しない**」だが、⚠️ **これは仮説**である。
   → ★ 事前登録（`docs/preregistration-v0.3.md`）に**書く必要があるか**を確認すること。
   ⚠️ 「毎日メールが来る」こと自体が行動を変えうる（★ reactivity）。**測るなら測ると宣言する。**
2. **⚠️ T-29 を最初から入れる**: ウェブアプリの `exec` URL は**スクリプト プロパティ**に置く。
   ★ Phase1 は直書きされていて `check-o1-release-readiness.sh` が実際に赤にした。
   ⚠️ **capability URL** である（`?pid=…&action=…` で実在 P-ID の応答を偽装できる）。
   → ★ O1 版では **P-ID だけでなく署名つきトークン**にするかを検討する。
3. **⚠️ ロスターは 3 研究の共用**: Phase1 の集計が全行を母数にして誤った数字を出していた（T-25）。
   ★ O1 版は**最初から O1 の行だけ**を対象にすること（⚠️ `o1RosterRowsForPid_` などが既にある）。
4. **⚠️ 「終了」トグル相当を最初から入れる**: ★ 無いと研究終了後にメールが流れ続ける。
   ⚠️ ゲートは **fail-closed**（`reminderSendingAllowed_` と同じ）。
5. **★ 何をもって「未提出」とするか**: Phase1 は F4 の提出日で見ていたが、
   ⚠️ O1 は**フォームではなく `.age` の Drive 到着**が提出である。
   → ★ `DriveApp` でフォルダを走査して P-ID × 日付を作る必要がある（⚠️ Phase1 に無い部分）。
   ⚠️ **ここが移植で一番重い。** ★ ファイル名規約 `P001_gse_YYYYMMDD_HHMMSS.age` に依存する。
6. **⚠️ 検査を同時に書く**: `Form_O1/o1_reminder_test.cjs`。
   ★ **陽性対照つき**（送る条件で実際に送ろうとすることを先に測る）＋ **変異で赤になること**。

## §5 ⚠️ スコープ外

- ⚠️★★★ **`Form_G1/` は 1 バイトも触らない**（G1 実施中）
- ⚠️ **実メール送信**（★ 初日は `AUTO_SEND=false` の下書きで研究者が確認する運用にすること）
- Phase1 側の再開（★ 凍結したまま）

## §6 ★ 関連する起票

- **T-29** ウェブアプリ exec URL が capability URL（→ `.steering/20260828-o1-gate-closeout-and-deployment/open-issues.md`）
- **T-30** 直書き検査が O1 のファイルしか見ない
- **T-26** repo と GAS の乖離を機械で検出できない
