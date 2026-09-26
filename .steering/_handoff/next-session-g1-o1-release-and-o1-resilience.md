# 次セッション — G1 / O1 の配布（v0.1.36 のタグ → build → zip）＋ O1 の耐障害性の修正 ＋ GAS / スプレッドシートの PJ 管理

> 作成: 2026-09-27（Mac 実機のセッション・前段 `.steering/20260926-g1-o1-mac-collection-prep/` の完了直後）。⚠️ **このメモを一次資料にしない。**
> 数字・状態はすべて **2026-09-27 に Mac で測った値**。★ 着手時に測り直す（過去に「メモの数字を信じず走らせたから見つかった」事故がある）。
> ⚠️★★★ タグの push・Drive / フォームの差し替え・被験者への送付・GAS の配備は**共有状態を変える**。実行前に必ず承認を取る。

## §0 打ち込む用（★ Mac で `git pull --ff-only` してから `/clear`、モデルは Sonnet。設計判断は Opus に切り替える）

```
.steering/_handoff/next-session-g1-o1-release-and-o1-resilience.md を読んで、次の 3 本を進めてください。
  T1: v0.1.36 のタグ → build → G1 用 zip（配布）  T2: O1 の耐障害性（自動起動・再送・スリープ・粒度）のサブエージェント調査 → 具体的な修正
  T3: GAS / スプレッドシートでの PJ 管理（O1 受領台帳・人単位ライフサイクル台帳）
⚠️ まず git pull --ff-only し、/start-task（task 名: g1-o1-release-and-o1-resilience）を実行する。docs/agent-shared.md のリンクハブから該当 docs を先に読む。
   Skill: verify-before-claiming（★ メモの数字を写さない）・data-privacy・subagent-delegation・hook-constraints（T2）・architecture-rules（T2）・browser-verification（T3・Chrome を使うとき最初の 1 回で必ず）。
★ 最初に §1 の状態を測り直す（PR #232 の merge・main の CI・ゲート 2 本）。
⚠️ 研究者の裁定・作業（§4）は私が埋めない。一覧にして渡し、答えを待つ。被験者向け文書（同意文書・participant-guide・README・課題ページ）は契約。承認なしに文面を変えない。
⚠️ タグ push は具体名（v0.1.36）を示して承認を取ってから。ADR-034 D3: 最初の G1 配布のタグは G1 の収集完了まで凍結される。
⚠️ subagent は「調査（事実の収集）」に使い、設計判断は渡さない（subagent-delegation ルール 1・5）。model・範囲・禁止事項・締切を毎回明示。
⚠️ 凍結物（docs/preregistration-p1-episode.md・src-tauri/prereg/p1-episode.json）と G1 事前登録の既存の版は書き換えない（改訂は append-only）。
⚠️ URL・Google の ID・氏名・メール・セッション時刻を repo に書かない。git add -A / git add <dir> は使わない。.codex/budget.json は台帳（git checkout -- で戻さない）。
★ 完了時は /finish-task（レビューは model 明示・範囲/禁止/締切つき → /cross-review）→ git-workflow ルール 6。応答は日本語。
```

## §1 現在の状態（2026-09-27・Mac で実測）

| 何 | 値 | 測り方 |
|---|---|---|
| main | `9558510`（PR #231 = 前段の merge・main の CI **success**） | `git log` / `gh run view 36249820419` |
| PR #232 | **v0.1.36 へのバージョン更新**（4 ファイル: `Cargo.toml` / `Cargo.lock` / `tauri.conf.json` / `package.json`）＋ O1 耐障害性の点検記録。作成時点で CI 実行中 → ⚠️ **着手時に状態を確認**（merge 済みでなければ CI 緑を待って merge） | `gh pr view 232` |
| 最新のリリースタグ | **`v0.1.35`**（2026-09-11）。⚠️ **区間指定削除の欠陥を含む**（自己申告行が消えない・修正は 9/14）。`v0.1.36` は**まだ打っていない** | `git tag` |
| G1 ゲート | 通過 17 / 未達 3（記録票 A / B / C のみ＝研究者の人手確認）。selftest 34/0 | `bash scripts/check-g1-collection-readiness.sh` |
| O1 ゲート | 通過 21 / 未達 2（同意文書の状態表に「⚠️ 未了」・リリースタグ陳腐化）。selftest 59/0 | `bash scripts/check-o1-release-readiness.sh` |
| 事前登録 | **第 20 版**（前提条件 7 の 9 マス）・`config.json` revision 20・`analyze.py` `PREREG_REVISION` 20。前提条件 7 は充足。**計器は未対応**（`validate_blocks.py` の FAIL・`analyze.py:196-200` の n 未達 NG）。G1 の人単位の記録破棄手順は未確認 | `preregistration.md` 先頭 |
| 前段の決定記録 | `.steering/20260926-g1-o1-mac-collection-prep/decisions.md` **判断 1〜11**（★ ここが一次）。`tag-candidate.md`（v0.1.35 → main の中身）・`o1-resilience-findings.md`（O1 の点検）・`researcher-decisions.md`・`drafts/01〜04` | 同左 |

### 研究者が決めたこと（2026-09-26〜27）
最初の配布は **G1 から**／署名は **ad-hoc のまま**／前提条件 3 は **ゲートの検査語を実体へ**（被験者向け文書は変えない）／前提条件 7 は推奨 9 マスを採用（⚠️ 「2 名未満は不成立」は凍結 §3.9 と矛盾するため §3.9 に従う形へ訂正済み）／O1-5 は **案 A（配布物が揃ってから O1-C の URL を渡す）**／計器の未対応は **マージして前提条件 8 の裁定を別途**／タグ前の O1 の穴は **運用で受け、今のコードでタグへ**（O1 の改善は O1 用の別タグ）。

## §2 タスク

### T1. [確認] v0.1.36 のタグ → build → G1 用 zip（配布）
0. **測り直す**: PR #232 が merge 済みか／main の CI／ゲート 2 本／ランナーのディスク空き（⚠️ 枯渇で CI が落ちた前例 2026-08-31・`.steering/_handoff/mac-runner-disk-cleanup-prompt.md`）。
1. **バージョンの整合**: `Cargo.toml` / `tauri.conf.json` / `package.json` / `Cargo.lock`（`gse-next`）がすべて 0.1.36 か。⚠️ **`capabilities.rs:309` の `CARGO_PKG_VERSION` が `meta.app_version` になる**。上げずにタグだけ打つと、新バイナリのログが欠陥のある旧 v0.1.35 と同じ版を名乗り、ADR-034 D3「G1 の解析は G1 のタグの `app_version` を持つファイルだけ」が成立しない。
2. **タグ push（承認）**: `git tag v0.1.36 <merge commit>` → `git push origin v0.1.36`。⚠️ push すると `build-macos`（**この Mac が self-hosted ランナー `gse-mac`**）・`build-windows`・`release` が走る。⚠️ **同じ版の再リリースは手順が要る**（memory `build-ci-and-pilot-distribution`: タグ push 発火・同 ver 再リリース手順）。
3. **Release 成果物の実体検証**: ⚠️ ゲート緑 ≠ 配布物が正しい（過去に `v0.1.29` が `o1.rs` を含まないまま署名も実行ビットも正常に見えた）。`LC_ALL=C grep -a`（⚠️ `strings` は日本語で偽陰性）で、`0.1.36` と削除修正の痕跡を実体で確かめる。
4. **G1 用 zip**: `bash experiments/20260801-controlled-friction-task/make-common-app-zip.sh --mode g1 --tag v0.1.36`（⚠️ **`--tag` を必ず明示**。既定は `v0.1.24` で古い。★ 未指定をエラーにする変更は研究者が「提案」段階で未裁定）。4 点の `codesign --verify --strict`（dmg 内 → コピー後 → zip → 展開後）・実行ビット・`g1.mode` の検算。⚠️ **Windows 向け zip を `ditto` で作らない**（UTF-8 フラグが落ちて文字化け・スクリプトは対応済み）。1 人ぶんは `make-distribution.sh`（既定タグ `v0.1.23`・同じく `--tag` 必須）。
5. **記録**: ADR-034 Migration 3 — **使ったタグを記録する**（置き場は配布タスクで決める。候補: `experiments/20260801-controlled-friction-task/`）。以後 `--mode g1` をそのタグ以外で作らない。
6. **Drive の差し替え・被験者への送付は [研究者]**（記録票 C）。課題ページ 200 枚（P001〜P020）は現行ジェネレータ出力と 200/200 バイト一致を確認済み（2026-09-26）。文面の妥当性・HI/LO の取り違えは目視が要る。
7. **実機通し確認**（配布物ができてから）: 初回起動（隔離属性の解除・入力監視の許可）→ 計測 → アプリ内提出 → 復号側で受領。⚠️ O1 は「押してはいけないボタンが出ない・説明文が O1 用」を目視。

### T2. O1 の耐障害性 — サブエージェントで**調査** → 具体的な修正（★ O1 用の別タグ）
一次は `.steering/20260926-g1-o1-mac-collection-prep/o1-resilience-findings.md`。研究者の指摘（2026-09-27）: 「24 時間ごとの送信が失敗したときのフォールバック・PC のシャットダウン後の再開・スリープ後の再開・24 時間おきの NDJSON の粒度」。

**実装済み（コード・テストで確認済み）**: 日次ローテート（60 秒粒度・epoch 差・スリープ含む）／送信失敗 → ローカル保持 → 再送／48 時間猶予（時計異常は fail-closed）／シャットダウン後は起動時に孤立ファイルを閉じる（`session_end` = 検出時刻）／入力フックの失効は macOS の watchdog・Windows の liveness が再有効化。

**穴（修正の対象）**:
| # | 穴 | 一次 | 修正の方向（★ 設計判断はメインが持つ） |
|---|---|---|---|
| G-1 | ⚠️★★★ **自動起動がコードに無い**（`autostart` / LaunchAgent / Run キーの実装 0 件）。再起動後に立ち上げるかは参加者が README でログイン項目を手で登録できるかに掛かる。登録しない人は記録も送信も止まる（母集団に偏り） | `o1.rs:535-560`・`dist-readme-*-o1.txt` | Tauri の autostart プラグイン等。⚠️ **被験者から見える動作の変更＝同意文書・README（契約）に触れる**ので研究者の承認が要る。OS ごとの権限・TCC・ad-hoc 署名との相互作用は**調査してから**決める |
| G-2 | **再送の契機が粗い**: Startup / Approval / O1DailyRotation（＋ G1 の BlockEnd）だけ。**定期リトライも通信復帰時の再送も無い**。回線断の間に猶予が明けると次のローテート（最大 24 時間後）か次の起動まで待つ | `lib.rs:1785-1794`・`:3877-3930` | 低リスクな定期 reconcile（例: 1 時間ごと）。⚠️ `LOCK_STALE_AFTER >= timeout * 10` の不変条件・`InFlightGuard` との相互作用に注意（`reconcile.rs:686-722`） |
| G-3 | **スリープ跨ぎの実機検証が記録上 1 度も成功していない**。手順は研究者へ渡したまま | `experiments/20260903-o1-runtime-cost/notes.md:816`・`.steering/20260910-intake-windows-and-cpu-convention/sleep-test-procedure.md` | ⚠️ **Claude Code が `caffeinate -i -t 300` を握るので `pmset sleepnow` が 0xe00002e2 で拒否される**（memory `claude-code-caffeinate-blocks-sleep-tests`）。→ 研究者手順として渡す |
| G-4 | **NDJSON の粒度**: ファイルは暦日でなく「アプリの起動ごと ＋ 最大 24 時間」。再起動した日は複数本・各先頭で `engine.reset()`。**孤立回収ファイルの `session_end` は最終データ行の時刻ではない**（下流が観測窓とみなすと実在しない沈黙区間を数える） | `o1.rs:48,535-600`・`experiments/20260819-silence-presence-decomposition/scripts/extract.py:314` | 下流（O1 事前登録の「人×日」）は**時刻で集約**する。schema にフィールドは足さない（`session_end − 最終データ行の t` で判別）。`drafts/03` §3 へ反映 |
| G-5 | **32 MB 超のとき被験者・研究者へどう見えるか未確認**（圧縮なし・実測 約 20〜23 MB/日・Google 側は約 37 MB 超で HTTP 400・受け口の上限は 2026-09-07 に 32 MB へ） | `reconcile.rs:686-722`・`o1-upload-timeout-measurement.md` | 読んでから決める |

**サブエージェントの使い方（調査のみ・§3 に brief）**: 各穴の「事実の収集」を並列に投げ、**設計判断はメインが持つ**。戻りは要約なので、**断定の根拠にする箇所はメインが一次で開く**（ルール 5・6）。

**制約（ADR-034 D3 の条件 2〜4）**: `HMM_VERSION` を動かさない／ゴールデンの差分は**新フィールドの追加のみ**／R3 の段 1 に 1 本も足さない。⚠️ O1 の配布物は G1 とは**別のタグ**で作ってよい（`--mode o1`）が、ADR-031 M9 により ADR-032 の Accepted と同じリリース。⚠️ 入力フックのコールバック内は Atomic ＋ channel send のみ（`hook-constraints`）。

### T3. GAS / スプレッドシートでの PJ 管理（研究者の要望: 「スプレッドシートで具体的に PJ 管理を行いたい」）
**結論**: 収集を**始めるための必須の GAS 修正は無い**。ただし「運用で受ける」と決めた以上、**その代替となる管理の部品が無い**（下表）。**本セッションでは GAS を 1 行も変えていない。**

| 事実（一次・2026-09-27） | 所在 |
|---|---|
| **受け口 `doPost` は Drive に保存するだけ**。提出の台帳（誰が・いつ・何本・何 MB）も、**途絶した人の検知**も無い（G1 / O1 とも） | `Form_O1/GSE_O1_Submit.gs:188-252`・`Form_G1/GSE_G1_Submit.gs:113` |
| O1 の管理シートは **「O1 登録ログ」「O1 却下ログ」の 2 タブだけ**（`buildO1MgmtSheet`）。ロスター（`参加者ロスター`）は Phase1 の表で**別の表**（T-28: 氏名だけの行を先に作らない） | `Form_O1/GSE_O1_Form_Builder.gs:1658-1720`・`docs/o1-roster-operations.md` |
| G1 の管理シートは提出・リンク・実施（`refreshG1RunSheet`）のタブを持つが、**第 20 版の人単位の数え方**（登録 k・解析 m・やめた・削除の求め）の台帳は無い | `Form_G1/GSE_G1_Form_Builder.gs:943-1606` |
| **Phase1 側に先例がある**: 名簿・ダッシュボード・リマインド・6 時間ごとの自動集計（`refreshRosterStatus` / `buildDashboardTab_` / `sendReminders` / `installRosterRefreshTrigger`） | `Form_Phase1/GSE_Phase1_Form_Builder.gs:1700-2900` |
| 未 merge の関連ブランチ: `origin/feature/phase1-reminder-and-dashboard`（Phase1 用・G1 / O1 とは別トラック・研究者の手動デプロイ未実施）ほか 5 本 | `git branch -r --no-merged origin/main` |

**提案（★ 研究者の承認 → 設計 → 実装。優先順）**:
1. **O1 受領台帳 ＋ 途絶検知**（最優先。G-1 / G-2 の代替統制）: 時間トリガーで Drive の受領フォルダを走査し、ファイル名から **P-ID × 日 × 本数 × バイト数** を「受領台帳」タブへ追記。「最終受領日」「N 日途絶」をダッシュボードにし、**研究者宛て**に途絶を通知。★ **`doPost` は変えない**（再配備・Web App の新バージョンのリスクを避ける）。⚠️ 被験者宛てのリマインドは連絡文＝被験者向け文書なので別途承認。
2. **G1 / O1 の人単位ライフサイクル台帳**: 案内日／登録／配布／開始／最終受領／状態（未実施・実施中・完了・やめた・削除の求め・解析対象）。⚠️ **第 20 版「公表物の書き方」**: 内訳（未完了・やめた・削除の求め）は**研究者手元の台帳にのみ**残す（n=3 では人数の公表が個人を指す）。→ シートは**研究者のみ閲覧・共有しない**設定にする。`results/` に P0xx 単位の理由ラベルを置かない。
3. **記録票 A の実測**: G1 の `checkConsentFormParity` を**実フォーム**に対して実行し、`consent.md` との一致を確認（9/5・9/6 に `consent.md` が改訂されている）。O1 の同意文書は ADR-031/032 の承認後に `buildO1ConsentForm` / `migrateO1ConsentForm` の更新と配備が要る。
4. **D6（案内日の分離）の重複 P-ID 検査の自動化**: 現状は「案内の翌日にロスター A 列を COUNTIF で確かめる」運用（`o1-roster-operations.md` §5）。シートの条件付き書式 / 検査関数へ。
5. **O1 の配布 URL**: スクリプト プロパティ `O1_APP_DOWNLOAD_URL` の設定と `checkO1FormConfig()`（読み取り専用）。⚠️ 空のまま登録させると受付メールが止まる（fail-closed）。

**GAS の作業上の罠**（memory `gas-live-state-vs-code` / `form-automation-fixed-id-and-shorturls` / Skill `browser-verification`）: repo の `.gs` と Apps Script 上のコードは**必ず食い違う**（貼付が要る）／**関数セレクタはツールバーの表示すら信用できない**（確認しても別の関数が走った）→ 破壊的関数と同居させない・トリガー経由・fail-closed ガード／`FormApp.create` ではなく固定 ID で開く／6 分制限と毎時トリガーの競合／実行の直前に表示を読み直す（リロードで先頭の関数に戻る）。⚠️ **G1 と O1 の GAS は別プロジェクト**（貼り間違いを `o1AssertNotG1Form_` が止める）。

## §3 サブエージェントへの brief（T2 用・★ 調査のみ）

> 渡し方の契約は `subagent-delegation` Skill。⚠️ `general-purpose` など定義ファイルを持たない相手は **model を必ず明示し・入れ子禁止を明記**。定義済み agent（`file-finder` / `impact-analyzer` ほか）は既定の model が効く。

| # | 調べること（ゴール） | 相手 / model | 読む所（指す） | 締切 |
|---|---|---|---|---|
| A1 | G-1: Tauri 2 の autostart プラグインが **macOS 13+ / Windows 11** で実際に何を登録するか（LaunchAgent・SMAppService / ログイン項目・Run キー）、**ad-hoc 署名＋入力監視（TCC）**との相互作用、被験者から見える挙動（通知・設定画面の表示） | `general-purpose`（**model: sonnet**・入れ子禁止・WebSearch / WebFetch 可・一次＝公式ドキュメントの逐語を引く） | `src-tauri/Cargo.toml`・`tauri.conf.json`・`docs/participant-setup-guide.md`・`dist-readme-*-o1.txt` | 10 分 |
| A2 | G-2: 定期 reconcile を足したときの**影響範囲**（`InFlightGuard`・ロック・`LOCK_STALE_AFTER`・`ReconcileReason` の全 caller・テスト） | `impact-analyzer` | `src-tauri/src/lib.rs:1785-2050,3877-3930,4049-4110`・`reconcile.rs` | 8 分 |
| A3 | G-4: `session_end` を観測窓とみなす**下流の消費者を全件**洗い出す（`extract.py` ほか） | `file-finder` | `experiments/`・`scripts/`・`src-tauri/src/bin/` | 5 分 |
| A4 | G-5: 32 MB 超・HTTP 400 のときの**クライアント側の挙動**（再送ループか・画面表示か・ログか） | `file-finder`（発見と分類のみ）→ 読むのはメイン | `reconcile.rs`・`submission.rs`・`src/` の提出 UI | 5 分 |

⚠️ **並列は 1 メッセージで・入れ子禁止・投げた仕事を自分でもやらない**。戻りは**一次で裏取り**してから設計に使う。設計判断（autostart を入れるか・どこに再送を足すか）は**メインが持つ**。

## §4 研究者待ち（★ 私は埋めない・一覧にして渡す）
1. **前提条件 8 として足すか**: 第 20 版の規則を実行する計器（`validate_blocks.py` の未完了マーカ・`analyze.py:196-200` の n 未達ゲートの見直し）と G1 の人単位の記録破棄手順。ゲート [7] は緑だが「計器は未対応」の注意書きを出す（赤にはしていない）。最初の参加者でも未完了・削除は起こりうる。
2. **記録票 A / B / C**（G1 ゲートの残り 3 件）: A＝配布済みフォームとの突合／B＝両 OS の対のテスト（CI の run 番号）／C＝Drive の差し替え。
3. G1 の確証標本の 3 人目（G1-10）・`config.json` の `status` の食い違い（G1-9）・週セレクタ（G1-11）。
4. O1: ADR-031 / 032 を Accepted にするか（同意文書 §3 の改訂の承認）／ O1 事前登録（`drafts/03` の質問 4 件）／ 未実施のまま長期に実施できない人の**期限の日数**（第 20 版で未決）。
5. 取り消し（同一セッション内）の規則を `protocol.md` に置くか（口頭で伝える内容。同意文書は変えない）。
6. **T2 の G-1（自動起動）を入れるか**（被験者から見える動作＝契約に触れる）／ **T3 の提案 1〜5 の採否**。
7. スリープ跨ぎの実機検証（G-3）を**誰が・いつ**行うか。

## §5 ⚠️ 見落としやすい点
1. **バージョンを上げずにタグを打たない**（§2 T1-1）。`app_version` が旧版と同じになる。
2. **ADR-034 D3**: 最初の G1 配布のタグは G1 の収集完了まで凍結される。G1 に効く修正はタグの**前**に入れる。O1 の改善は別タグ。
3. **ゲート緑 ≠ 配布物が正しい**。実体（`LC_ALL=C grep -a`）で確かめる。
4. **`expect_green` 型の selftest 変異は、実 repo が満たした瞬間に空回りする**（本セッションで踏んだ）。ゲートを直すときは「緑から壊す」形にする。
5. **selftest が並列実行中に 1 回だけ不安定に赤くなった**（原因不明・再現せず。検査 7 を pipe なしにした予防のみ）。同型が再び出たら仮説（`printf | grep -q` の SIGPIPE）を捨てて調べ直す。
6. macOS の bash は 3.2・BSD 系ツール（`sed '\?'` は無音で空振り・多バイト文字を含む変数名は `${name}` で括る）。
7. zsh では `echo =====` が**コマンド展開で失敗**する（引用符で括る）。
8. **被験者向け文書は契約**。GAS のフォーム文言・受付メールも同じ。repo は一時 public になりうる（URL・ID・氏名・メール・時刻を書かない）。
9. **`.codex/budget.json` は台帳**（日次 300000・1 回 30000。`git checkout --` で戻さない）。

## §6 やらないこと
- 承認なしのタグ push・Drive / フォームの差し替え・被験者への送付・GAS の配備。
- 署名方式の変更（Developer ID・公証）を裁定なしに始める。被験者向け文書・凍結物・事前登録の既存の版を書き換える。
- 実データを開く／ P1 の PG-1 の値を決める／ C トラック（媒体表現）へ着手。
- 設計判断を subagent に渡す。

## §7 一次資料（読む順）
1. `.steering/20260926-g1-o1-mac-collection-prep/{decisions.md, tag-candidate.md, o1-resilience-findings.md, researcher-decisions.md, evidence.md, drafts/}`
2. `docs/adr/ADR-034-g1-o1-parallel-conduct.md`（D3・D6・Migration 3/6）・`ADR-014`（D6・D8）・`ADR-031` / `ADR-032`
3. `src-tauri/src/{o1.rs, reconcile.rs, lib.rs, submission.rs, capabilities.rs}`・`docs/o1-roster-operations.md`・`docs/o1-deletion-ledger.md`
4. `Form_O1/`・`Form_G1/`・`Form_Phase1/`（GAS）・`experiments/20260801-controlled-friction-task/{make-common-app-zip.sh, make-distribution.sh, collection-readiness-record.md, dist-readme-*-o1.txt}`
5. `.github/workflows/ci.yml`（`build-macos` の署名ステップ）・`.steering/_handoff/mac-runner-disk-cleanup-prompt.md`
