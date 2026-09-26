# 次セッション — O1 受領台帳＋途絶検知の実装（T3-1）／記録票 A の Chrome 実測／人単位台帳の設計

> 作成: 2026-09-27（前段 `.steering/20260927-g1-o1-release-and-o1-resilience/` の完了直後・PR #233 merge 済み）。⚠️ **このメモを一次資料にしない。**
> 数字・状態はすべて **2026-09-27 に Mac で測った値**。★ 着手時に測り直す。
> ⚠️★★★ Drive / フォーム / GAS の配備・被験者への送付・タグ push は**共有状態を変える**。実行前に必ず承認を取る。

## §0 打ち込む用（★ `git pull --ff-only` → `/clear` → モデルは Sonnet。設計判断は Opus）

```
.steering/_handoff/next-session-o1-receipt-ledger.md を読んで、次の 3 本を進めてください。
  T1: O1 受領台帳＋途絶検知の実装（Form_O1/GSE_O1_Ledger.gs を新規・doPost は変えない）  T2: 記録票 A の実測（Claude が Chrome で checkConsentFormParity を実行）  T3: G1/O1 の人単位ライフサイクル台帳の設計（別スプレッドシート・設計のみ）
⚠️ まず git pull --ff-only し、/start-task（task 名: o1-receipt-ledger）を実行する。docs/agent-shared.md のリンクハブから該当 docs を先に読む。
   Skill: verify-before-claiming・data-privacy・subagent-delegation・browser-verification（★ T2 で Chrome を使うとき最初の 1 回で必ず）・grilling。
★ 最初に §1 の状態を測り直す（main の CI・タグ v0.1.36・ゲート 2 本）。
⚠️ 研究者の裁定・作業（§4）は私が埋めない。被験者向け文書（同意文書・README・フォーム文言・受付メール）は契約。承認なしに文面を変えない。
⚠️ GAS の配備・Apps Script への貼付・関数の実行は実行前に承認を取る。関数セレクタは表示を信用しない（押す直前に読み直す）。G1 と O1 の GAS は別プロジェクト。
⚠️ 凍結物・v0.1.36 のタグ・G1 事前登録の既存の版は書き換えない。URL・Google の ID・氏名・メール・セッション時刻を repo に書かない。git add -A / git add <dir> は使わない。.codex/budget.json は台帳（git checkout -- で戻さない）。
★ 完了時は /finish-task（レビューは model 明示・範囲/禁止/締切つき → /cross-review）→ git-workflow ルール 6。応答は日本語。
```

## §1 現在の状態（2026-09-27・Mac で実測）

| 何 | 値 | 測り方 |
|---|---|---|
| main | `cb214c5`（PR #233 = ロックの heartbeat＋所有印・v0.1.36 の配布タグ記録。両 OS の CI 緑で merge）。⚠️ **main の CI（run 36259334890）は merge 直後に実行中**だった → 着手時に success を確認 | `git log` / `gh run view 36259334890` |
| リリースタグ | **`v0.1.36`**（`24c5e3e`・2026-09-27）。Release 資産 5 点・CI 全 job success。⚠️ **G1 の最初の配布のタグ＝G1 の収集完了まで凍結**（ADR-034 D3）。記録: `experiments/20260801-controlled-friction-task/distribution-tag.md` | `git tag` / `gh release view v0.1.36` |
| ⚠️ v0.1.36 に**入っていない** | PR #233 の reconcile 修正（heartbeat＋所有印）。O1 用の**別タグ**で出す（ADR-034 D3・ADR-031 M9＝ADR-032 の Accepted と同じリリース） | — |
| G1 ゲート | 通過 17 / 未達 3（記録票 A / B / C のみ＝研究者の人手確認） | `bash scripts/check-g1-collection-readiness.sh` |
| O1 ゲート | 通過 22 / 未達 1（同意文書の状態表に「⚠️ 未了」） | `bash scripts/check-o1-release-readiness.sh` |
| G1 用 zip | `experiments/20260801-controlled-friction-task/dist/_common/G1_実施用_{macOS,Windows}.zip` を v0.1.36 で生成済み（`.gitignore` 済み）。⚠️ 同じ場所に **2026-09-11 作成の古い O1 用 zip** が残る（配らない） | `ls dist/_common` |
| 前段の一次 | `.steering/20260927-g1-o1-release-and-o1-resilience/{decisions.md, t3-gas-pj-management-design.md}`（★ ここが一次） | 同左 |

### 前段で確定したこと（研究者・2026-09-27）
- G-1（O1 の自動起動）・G-2（定期再送）・G-5（32 MB 超）は **O1 だけの問題**（G1 は 70 分・1 回きり）。**今回は実装しない**。G-1 は**運用で受け続ける**（README のログイン項目登録＋初回の研究者同席）。→ その**代替統制が T1 の受領台帳**。
- T3-1 の「途絶」= **最終受領から 5 日**／T3-2 の人単位台帳は**別のスプレッドシート**（研究者のみ閲覧・共有しない）／記録票 A の実行は **Claude が Chrome で代行**／G-3（スリープ跨ぎの実機検証）は**研究者が手順書どおり実施**／前提条件 8（第 20 版の計器・G1 の人単位の記録破棄手順）は**別タスクとして後で起票**。

## §2 タスク

### T1. O1 受領台帳＋途絶検知の実装（主タスク）
設計案の一次: `.steering/20260927-g1-o1-release-and-o1-resilience/t3-gas-pj-management-design.md`「提案 1」。**着手時に grill で残りを閉じる**（下の「決めること」）。

**変えないもの**: `Form_O1/GSE_O1_Submit.gs` の `doPost`（再配備・Web App の新バージョンのリスクを避ける）。既存の `GSE_O1_Form_Builder.gs` も原則触らない（新規ファイル `Form_O1/GSE_O1_Ledger.gs` に閉じる）。

**一次で確認済みの事実**（2026-09-27）:
- 受領ファイル名は `^[A-Za-z0-9]{1,16}_o1day\d{2,3}_gse_o1_\d{8}_\d{6}(_\d{1,10})?\.age$`（`GSE_O1_Submit.gs:292-297` `sanitizeName_`）。P-ID・日番号・セッション開始日時（実日付）が名前から読める。重複は `_dup-<epoch>` の別名で足される（`:339-347`）。
- 保存先はスクリプト プロパティ `FOLDER_ID` の Drive フォルダ（`:95-97`）。
- O1 の管理シートは「O1 登録ログ」「O1 却下ログ」の 2 タブ（`buildO1MgmtSheet`・`GSE_O1_Form_Builder.gs:1658-1675`）。ロスターは別の表。
- 既存のローカル guard test: `Form_O1/o1_submit_guard_test.cjs`・`o1_form_builder_test.cjs`・`o1_form_builder_mutation_test.sh`（★ 新規の純関数もこの流儀で Node から呼んで固定する。CI への配線は既存テストの配線を見て合わせる）。

**部品（案・承認済みの方向）**: `o1LedgerSync()`（Drive を走査→「O1 受領台帳」タブへ**追記**・Drive ファイル ID で冪等・行は消さない）／`o1LedgerDashboard()`（P-ID ごとに再計算→「O1 途絶」タブへ上書き。列: 最終受領日・経過日数・本数・合計 MB・日番号の欠番・判定）／6 時間ごとの時間トリガー／判定が「途絶（5 日）」に**変わったとき 1 回だけ**研究者宛てメール（宛先はスクリプト プロパティ・未設定なら送らずログ＝fail-closed）。⚠️ 被験者宛てのリマインドは**しない**（連絡文＝被験者向け文書・別承認）。

**決めること（着手時の grill）**:
1. ⚠️ 実行の**単位**: 台帳の置き場を「O1 の管理シートの新タブ」にするか、別スプレッドシートにするか（O1 の管理シートには `参加者ロスター` を置けない制約あり・`:1664-1668`）。
2. ⚠️ **未確認 2 点を実測**（推測で書かない）: 受領フォルダに `.age` 以外が置かれうるか／Drive の `getDateCreated()` を受領時刻とみなしてよいか（実フォルダで 1 回確かめる。⚠️ 偽 Drive は実物の制約を知らない）。
3. 6 分制限: 走査は「前回の最終 ID より新しいものだけ」に絞る方式にするか。
4. 欠番判定（day03 が無く day04 がある）の扱い。⚠️ 猶予 48 時間で**順序が前後して届く**のは正常なので、欠番は「最後の受領から N 日たっても埋まらない」ときだけ。
5. 通知の頻度（案: 状態が変わったとき 1 回）。

**テスト**: 純関数（ファイル名 → P-ID/日番号/開始日、経過日数の判定、欠番検出、冪等）を `.gs` から切り出して Node で固定。⚠️ **検査したら検査自体を 3 状態（正常・不在・壊れ）で試す**（`verify-before-claiming` ルール 5b）。**変異は 1 箇所ずつ入れる**（前段で「両方同時に消して赤」＝片方しか証明できていなかった失敗を踏んだ・memory `measurement-instrument-false-positives`）。
**配備は別承認**: Apps Script 上のコードは repo の `.gs` と必ず食い違う（貼付が要る）。実行後に**実フォルダで通し確認**（`browser-verification`）。

### T2. 記録票 A の実測（Chrome で代行・承認つき）
- 対象: G1 ゲートの残り 1 件。`Form_G1/GSE_G1_Form_Builder.gs:434-480` `checkConsentFormParity()`（**読み取り専用**・実フォームを読み、コード側の同意項目・順序・説明文と比べ `Logger.log` に ✅/❌）。
- ⚠️★★★ **これが確かめるのは「実フォーム ⇔ コード」だけ**。記録票 A が求めるのは「`starve_window` と `app_version` の記載が配布済みの電子フォームで同じか」（`preregistration.md:357-358`）。→ **`consent.md` ⇔ `consentItemTitles_()`（コード）の一致は別に確かめる**（関数 1 本で記録票 A が閉じるとは限らない）。
- ⚠️ `consent.md:178` に「配布済み G1-C の 8 項目目の文言更新は未実施・`migrateConsentForm()` を実行してから `checkConsentFormParity()` で確認」とある。突合が ❌ なら**先に `migrateConsentForm()`（書き換え）が要る可能性**があり、**それは別承認**。`setupG1Forms()` は**実行しない**。
- 手順: **`browser-verification` を最初に読む** → 研究者のログイン済み Chrome で G1 の Apps Script を開く → ⚠️ **関数セレクタは表示を信用しない**（メニューのアニメーション中はクリックが着弾しない・`computer` 座標が約 1.49 倍ずれる。押す直前に zoom で読む）。同居する `setupG1Forms` / `migrateConsentForm` は**書き換える関数**なので、`checkConsentFormParity` を選んだことを**実行前に画面で読み直す** → 実行ログの ✅/❌ を記録票 A の「突合の結果」の**下書き**にする（★ ID・URL は書かない。記録票への記入は研究者）。
- 実行前に**研究者へ「これから Chrome で G1 の Apps Script の読み取り専用関数を 1 本実行します」と承認を取る**。

### T3. G1 / O1 の人単位ライフサイクル台帳の設計（設計のみ・別スプレッドシート）
一次: 設計案「提案 2」。要点: 列（案）= P-ID / 研究 / 案内日 / 登録 / 配布 / 開始 / 最終受領 / 状態 / 状態の変更日。⚠️★★★ **第 20 版「公表物の書き方」**: 内訳（未完了・やめた・削除の求め）は**研究者手元の台帳にのみ**残す（n=3 では人数の公表が個人を指す）→ 別のスプレッドシート・研究者のみ閲覧・共有しない。`results/` に P0xx 単位の理由ラベルを置かない。「やめた」「削除の求め」は**本人の申し出**（ADR-034 D4 2c）なので**自動判定しない**（手入力・入力規則で状態を限定）。T1 の「途絶」を「やめた」へ**自動変換しない**（D4 2b・不可逆）。

## §3 サブエージェントの使い方（`subagent-delegation` Skill が契約）
- **調査（事実の収集）だけ**渡す。設計判断・GAS の実行はメインが持つ。戻りは要約なので、断定に使う箇所は**メインが一次で開く**。
- 定義済み agent は既定の model が効く（`code-reviewer`=opus 等）。`general-purpose` は model を明示・入れ子禁止を明記。範囲・禁止事項・**締切**（レビュー 10〜15 分）を毎回書く。
- 完了時のレビュー: `code-reviewer` ＋ `security-checker` を並列 → `/cross-review`（Codex）。⚠️ `.gs` が主対象なので、`security-checker` には「**メール送信・Drive 走査・シークレットの扱い・宛先ハードコード無し**」を名指しで見てもらう。**レビュー中は作業ツリーを変えない**。コミット済み範囲は `<base>..<head>` の定型で渡す。
- 前段の実績: レビュー指摘は**すべて一次で確かめてから**反映した（HIGH 1 件は本物だった・採らなかった指摘は理由を decisions に書いた）。

## §4 研究者待ち（★ 私は埋めない・質問で聞く）
1. 記録票 **B**（両 OS の対のテスト）: main の run 36253294897（`24c5e3e`）で Windows・macOS の `check` がともに success（記入は研究者）。PR #233 の run でも両 OS 緑。
2. 記録票 **C**・Drive の差し替え・実機通し確認（初回起動 → 計測 → アプリ内提出 → 復号側受領。⚠️ O1 は「押してはいけないボタンが出ない・説明文が O1 用」を目視）。
3. G1 の確証標本の 3 人目（G1-10）・`config.json` の `status` の食い違い（G1-9）・週セレクタ（G1-11）。
4. O1: ADR-031 / 032 を Accepted にするか／ O1 事前登録（`drafts/03` の質問 4 件・**「人×日」は時刻で集約**する追記案）／ 未実施のまま長期に実施できない人の**期限の日数**（第 20 版で未決）。
5. 取り消し（同一セッション内）の規則を `protocol.md` に置くか（口頭で伝える内容・同意文書は変えない）。
6. **G-3 スリープ跨ぎの実機検証**（研究者が `.steering/20260910-intake-windows-and-cpu-convention/sleep-test-procedure.md` どおり実施）。⚠️ Claude Code が `caffeinate` を握るので `pmset sleepnow` は私から実行できない。
7. **前提条件 8**（第 20 版の計器 `validate_blocks.py` の未完了マーカ・`analyze.py:196-200` の n 未達・G1 の人単位の記録破棄手順）— **別タスクとして起票**（最初の参加者の前に）。
8. O1 用の別タグ（heartbeat＋所有印を載せる）は ADR-031/032 の Accepted 待ち。G-1 / G-2 / G-5 は O1 配布前に**再度**「入れるか・運用で受けるか」を決める（今は運用で受ける）。

## §5 ⚠️ 見落としやすい点
1. **v0.1.36 は凍結**。G1 に効く修正はタグの**前**に入れる（もう打ったので、以後 G1 の計器を変える変更は入れない）。O1 の改善は別タグ。
2. **GAS は repo と Apps Script 上でずれる**。貼付・配備・関数の実行は共有状態を変える → 承認。
3. **ゲート緑 ≠ 配布物が正しい**。実体（`LC_ALL=C grep -a`・対照つき）で確かめる。
4. 台帳は**受領の有無**しか言えない（アプリ未起動・回線断・32 MB 超は区別できない）。対応（被験者へ連絡）は同じ。区別が要るなら別の話。
5. 「途絶」を「やめた」に自動変換しない。人数の内訳は公表しない（第 20 版）。
6. macOS の bash は 3.2（多バイト文字を含む変数名は `${name}` で括る）・zsh では `echo =====` が失敗する（引用符で括る）。
7. **`.codex/budget.json` は台帳**（日次 300000・1 回 30000）。`git checkout --` で戻さない。
8. 被験者向け文書（同意文書・README・フォーム文言・受付メール）は契約。repo は一時 public になりうる。

## §6 やらないこと
- 承認なしの GAS 配備・関数の実行・タグ push・Drive/フォームの差し替え・被験者への送付。
- `doPost` の変更（受け口の再配備）・被験者宛てのリマインド送信。
- G-1 / G-2 / G-5 の実装・署名方式の変更・凍結物や事前登録の既存の版の書き換え。
- 実データを開く・P1 の PG-1 の値を決める・C トラック（媒体表現）へ着手。
- 設計判断や GAS の実行を subagent に渡す。

## §7 一次資料（読む順）
1. `.steering/20260927-g1-o1-release-and-o1-resilience/{decisions.md, t3-gas-pj-management-design.md, tasklist.md}`
2. `Form_O1/GSE_O1_Submit.gs`（`doPost`・`sanitizeName_`・`saveWithoutOverwriting_`）・`Form_O1/GSE_O1_Form_Builder.gs`（`buildO1MgmtSheet`・`o1Config_`・`o1AssertNotG1Form_`）・`Form_O1/o1_submit_guard_test.cjs`
3. `Form_G1/GSE_G1_Form_Builder.gs:434-480`（`checkConsentFormParity`）・`experiments/20260801-controlled-friction-task/{collection-readiness-record.md, consent.md, distribution-tag.md}`
4. `docs/o1-roster-operations.md`・`docs/adr/ADR-034-g1-o1-parallel-conduct.md`（D3・D4・D6）
5. `Form_Phase1/GSE_Phase1_Form_Builder.gs`（先例: `refreshRosterStatus` / `buildDashboardTab_` / `installRosterRefreshTrigger`。⚠️ 別プロジェクト・未 merge の `origin/feature/phase1-reminder-and-dashboard` は Phase1 用で別トラック）
6. memory: `gas-live-state-vs-code` / `form-automation-fixed-id-and-shorturls` / `measurement-instrument-false-positives` / `drive-mcp-upload-fidelity`
