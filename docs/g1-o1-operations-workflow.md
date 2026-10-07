# G1 / O1 の運営ワークフロー — どのフォームを、いつ、誰が記入するか

> 作成 2026-10-07。**研究者が参加者 1 人を受け入れてから終えるまで**を、G1 と O1 について時系列で並べた索引。
> ⚠️ **この文書は手順の本文を持たない。** 本文は各行の「正本」にある（片方だけ直して食い違わせないため）。
> ⚠️ 書いてあるのはコードと文書の記述であって、**Drive・フォーム・Apps Script の実物の状態ではない**。実物は「始める前のゲート」と人手の記録票で確かめる。

| 研究 | 中身 | 期間 | 主な正本 |
|---|---|---|---|
| **G1** | 統制課題実験（10 ブロック・約 70 分・課題ページに文章を書く） | 1 回 | `experiments/20260801-controlled-friction-task/protocol.md`・`Form_G1/README.md` |
| **O1** | ふだんの作業の常時記録（形成的・ADR-014） | 3〜5 名 × 3 週間（暫定・事前登録草案 §3〔`.steering/20261007-o1-preregistration-draft/preregistration-draft.md`・⚠️ 2026-10-07 時点で未追跡・main チェックアウトのみ〕）。⚠️ 同意文書の表記は「数日〜数週間」 | `Form_O1/*.gs` の冒頭コメント・`docs/o1-roster-operations.md`・`docs/o1-deletion-ledger.md` |

---

## 0. 始める前のゲート（★ 緑になるまで始めない）

| 対象 | コマンド | 2026-10-07 の結果 |
|---|---|---|
| G1 の新コホートの収集 | `bash scripts/check-g1-collection-readiness.sh` | ✅ 26/26（schema parity は gse-dataset PR #2 で同期した後） |
| O1 の配布 | `bash scripts/check-o1-release-readiness.sh` | ✅ 24/24（`Form_O1/o1_submit.json` を置いた状態で、秘密の値の混入の判定まで含む） |

- ⚠️ **G1 のゲートが見ていないもの**: 配布したバイナリの実行時の挙動・Drive とフォームの実物・CI の run。→ 人手の記録票 `experiments/20260801-controlled-friction-task/collection-readiness-record.md`。
- ⚠️ **O1 のゲートの [5]** は手順書に「案内日を分ける」規則があることを見るだけで、**実際に日を分けたかは見ない**。
- ⚠️ **O1 のゲートは `Form_O1/o1_submit.json` の無い機械では秘密の値の混入を判定しない**（「未確認」と出る）。設定のある機械で回す。

---

## 1. 1 人の参加者についての大原則

| # | 原則 | 正本 |
|---|---|---|
| 1 | **O1 に先に参加した人を G1 に入れない**（不可逆）。G1 → O1 は、G1 の完了（か本人の「やめた」）の後・**翌日以降**・別の同意・**同じ P-ID** | `docs/person-lifecycle-ledger-template.md` §1 制約 4・ADR-034 D4-2 |
| 2 | **G1 と O1 の記録は結合しない** | 同 制約 5・ADR-034 D4-6 / D4-7 |
| 3 | **G1 と O1 の案内を同じ日に出さない**（2 つの登録フォームは別の Apps Script で、採番の排他が効かない） | `docs/o1-roster-operations.md` §5 |
| 4 | **P-ID は Phase1 と共有**。既に P-ID を持つ人は再利用、新規は採番 | `Form_G1/README.md`・`protocol.md` §2.0 |
| 5 | 「中断」「やめた」「削除の求め」は**別の申し出**。やめた・削除は本人の申し出で確定し、**理由は聞かない** | `docs/person-lifecycle-ledger-template.md` §1 制約 1〜3 |
| 6 | ⚠️ **記録は公開しない**（G1 は「生ログは公開しません」と約束済み・O1 は公開の同意を取っていない）。公開・2 本目の論文の扱いは ADR-039 | ADR-039 D1・D2・D8 |

---

## 2. フォームの早見表

| フォーム | 研究 | 誰が記入 | いつ | 回数 | 記入すると自動で起きること |
|---|---|---|---|---|---|
| **G1-C 説明・同意（＝参加登録）** | G1 | 参加者 | 募集時（当日その場でも可） | 1 | `onG1ConsentSubmit`: P-ID の検証 → 採番（既存なら再利用）→ 管理シート「G1 実施トラッキング」に行 → **受付メール** |
| **G1-M 強制比較** | G1 | 参加者 | **ブロック 3〜9 の直後**の 1 分休憩の中 | 7 | なし（1 時間ごとの集計で「G1-M 回答数」が埋まる） |
| **G1-S 終了後アンケート** | G1 | 参加者 | **最後のブロックの後**。⚠️ デブリーフはこの**後**に渡す | 1 | なし（集計列が埋まる） |
| **O1-C 説明・同意（＝参加登録）** | O1 | 参加者 | 募集時。⚠️ **配布物と入手先 URL がそろってから** URL を渡す | 1 | `onO1ConsentSubmit`: 採番（LockService）→ 管理シート「O1 登録ログ」→ **受付メール**（P-ID・アプリの入手先・毎日の起動・止める/消す・連絡先） |
| **O1-S 終了後アンケート** | O1 | 参加者 | 期間の終わり | 1 | なし。⚠️ **URL を渡す仕組みが無い**（§6 の穴 1） |

管理シート・台帳（研究者が見る）:

| シート | 研究 | 更新 | 正本 |
|---|---|---|---|
| 「リンク集」「G1 実施トラッキング」 | G1 | 登録時に行・**1 時間ごと**に集計列（`refreshG1RunSheet`） | `Form_G1/README.md` |
| 「O1 登録ログ」「O1 却下ログ」 | O1 | 登録時（追記のみ・氏名メールなし） | `GSE_O1_Form_Builder.gs` `buildO1MgmtSheet` |
| 「O1 受領台帳」「O1 途絶」 | O1 | **6 時間ごと**（`o1LedgerRun`）。途絶（最終受領から 5 日）・欠番（5 日）・未受領（登録から 7 日）を研究者宛てに 1 通で通知。⚠️ 被験者には送らない | `Form_O1/GSE_O1_Ledger.gs` |
| 人単位の台帳 | 両方 | 手入力 | `docs/person-lifecycle-ledger-template.md`（⚠️ **設計のみ・実物は未作成**） |

---

## 3. G1 — 時系列

| 段階 | 誰が | 何をする | 使うもの | 自動で起きること | 正本 |
|---|---|---|---|---|---|
| **G-0** 基盤（1 度だけ） | 研究者 | 受け口の配備・トリガー 3 本（`installG1ConsentTrigger`・`installMaterialsAutoSendTrigger`・`installRunSheetRefreshTrigger`）・Drive の親フォルダを「制限付き」に | `Form_G1/` | — | `Form_G1/README.md` 配備手順 |
| **G-1** 前日まで | 研究者 | 割付（`assign.py`・`validate_blocks.py`）→ 課題ページ → 配布フォルダ（`make-distribution.sh`・`prepare-subjects.sh`）→ Drive へ上げて照合（`verify-drive-upload.py` が緑になるまで URL を配らない）。共通アプリ zip は `make-common-app-zip.sh --mode g1 --tag v0.1.36`（⚠️ G1 の配布物は最初の配布のタグで固定・`make-distribution.sh` も同じタグ） | `experiments/20260801-controlled-friction-task/` | — | `protocol.md` §2.1・§6「前日まで」・`distribution-tag.md`（v0.1.36）・ADR-034 D3 |
| **G-2** 募集・登録 | 研究者 → 参加者 | 案内（⚠️ O1 と別の日）→ 参加者が **G1-C** | G1-C | 採番・トラッキング行・**受付メール** | `Form_G1/README.md`・`docs/o1-roster-operations.md` §5 |
| **G-3** 日程・事前資料 | 研究者 | 日程は返信で決める（自動化なし）。管理シートの「配布フォルダURL」列に URL を貼る | 管理シート | **1 時間以内に事前資料メール**（7 本のガード・送付日を記録） | `Form_G1/README.md` 配布と事前資料メール |
| **G-4** 初回起動 | 研究者＋参加者 | zip を展開して初回起動。**研究者が同席**（macOS は同席が必須・Windows は「G1 モードで動作しています」の目視） | 同梱の README・`初回セットアップ_mac.sh` | — | `protocol.md` §1.1「第 13 版の手順」 |
| **G-5** 当日・開始前 | 研究者 | **G1-C が回答済みか**を確かめる（同意の正本）→ `participant-guide.md` を渡す（冒頭の実験者向け注記は切り取る）。ブロック 1 を起動した直後に `HMM_VERSION` を読んで記録する | G1-C の回答・`participant-guide.md` | — | `protocol.md` §4.1・§6「当日・開始前」・§6.1 |
| **G-6** 10 ブロック | 参加者（研究者は台本どおり） | ページを開いてからアプリの「開始する」。**ブロック 3〜9 の直後に G1-M** | 課題ページ・**G1-M** | ブロックごとに `.age` を作り「送信しますか？」→ 押すと受け口経由で Drive へ | `protocol.md` §4.2・§6「各ブロック」（無人在宅は §4b） |
| **G-7** 終了 | 参加者 → 研究者 | **G1-S** → その**後**に `debrief.md`（口外しないお願いを読み上げる）。画面で「未確認 0・未送信 0」を確認。お礼メール（`sendThankYouEmail`・手動） | **G1-S**・`debrief.md` | 集計列が 1 時間ごとに更新 | `protocol.md` §6「当日・終了後」 |
| **G-8** 受領・検証 | 研究者 | `analyze.py --verify-blocks`・`forms_to_blocks.py`・`validate_blocks.py --dataset`。復号は `gse-unpack`。⚠️★★ NDJSON を匿名化して gse-dataset へ送るときは **G1 のセッションだと明記し、Phase1 の較正プールに入らないことを確かめる**（P-ID を Phase1 と共有しているので、怠ると Phase1 の集計に G1 が混ざる）。G1 の解析は `meta` に `g1_mode` と `app_version = 0.1.36` を持つファイルだけ | — | — | `protocol.md` §6「当日・終了後」・`experiments/20260801-controlled-friction-task/data.md` B-4・`distribution-tag.md`・`docs/pilot-runbook.md` §4.1（⚠️ §6 穴 3） |
| **G-9** やめた・削除の求め（随時） | 参加者 → 研究者 | **やめた**: 理由を聞かず、その場で**削除も希望するかを必ず確かめ**、答えを人単位の台帳に書く（⚠️ 沈黙を「削除は求めていない」と読まない。やめただけなら送信済みの記録は保持）／**削除の求め**: P-ID と範囲だけ受け取る → チェックリストを回す → 削除台帳に 1 行 | — | — | `docs/g1-deletion-ledger.md` §1（47-62 行）・§2・§3・§5 |

---

## 4. O1 — 時系列

| 段階 | 誰が | 何をする | 使うもの | 自動で起きること | 正本 |
|---|---|---|---|---|---|
| **O-0** 基盤（1 度だけ） | 研究者 | Apps Script 3 プロジェクト（フォームビルダー・受け口・受領台帳）に貼り、スクリプト プロパティを設定。`checkO1FormConfig()` → `buildO1MgmtSheet()` → `checkO1MgmtSheet()` → `setupO1Forms()` → `previewO1RegisterAckEmail()` → `installO1ConsentTrigger()`。受け口のデプロイ。台帳は `o1LedgerCheck()` → `o1LedgerRun()` → `installO1LedgerTrigger()` | `Form_O1/*.gs` | 設定が欠ければ fail-closed で止まる | 各 `.gs` の冒頭コメント |
| **O-1** 同意文書の改訂（版が変わるとき） | 研究者 | `consent-draft-o1.md` を**先に**直す → `GSE_O1_Form_Builder.gs` に写す → `node Form_O1/o1_form_builder_test.cjs` → `migrateO1ConsentForm()`（⚠️ `setupO1Forms()` で作り直さない） | — | 新しい同意項目は**末尾**に付き、既に回答した人は未同意（ログで警告） | `GSE_O1_Form_Builder.gs` `migrateO1ConsentForm` |
| **O-2** 配布物 | 研究者 | `make-common-app-zip.sh --mode o1 --tag v0.1.40 --config Form_O1/o1_submit.json` → **O1 専用**の Drive フォルダ → `O1_APP_DOWNLOAD_URL` に設定。使ったタグを記録 | — | — | `docs/o1-distribution-tag.md` §v0.1.40 |
| **O-3** 募集・登録 | 研究者 → 参加者 | 案内（⚠️ G1 と別の日）→ 参加者が **O1-C**。⚠️ ロスターに**氏名だけの行を先に作らない**。登録後に `checkO1RosterShape()` で行の増加を確かめてから氏名を埋める。案内の翌日にロスター A 列の重複を確かめる | **O1-C** | 採番・登録ログ・**受付メール** | `docs/o1-roster-operations.md` §2・§5 |
| **O-4** 初回起動 | 研究者＋参加者 | **macOS は研究者と一緒に**初回セットアップ（約 5 分・対面か画面共有）。最初の画面で P-ID と同意の確認 | 同梱の `README_先に読む.txt` 【1】 | 確認後、ログイン時の**自動起動が 1 回だけ登録**される。確認までは研究者へ送らない | `dist-readme-macos-o1.txt`・`dist-readme-windows-o1.txt` |
| **O-5** 常時記録（3 週間・暫定） | 参加者 | ふだんどおり作業。作業種別の宣言（5 択・忘れてよい）。記録中は印が出る。一時停止・時間帯の削除ができる | アプリ | 1 日ごとに閉じ、**48 時間後**に暗号化して自動送信 → 受け口が `<P-ID>/` に保存 | 同意フォームの説明（5 択は `o1ConsentFormDescription_`）・README 【3】〜【6】 |
| （該当者のみ） | 研究者 → 参加者 | 文字をあまり打たない作業の人に、別の測定（宣言ブロック）・短い画面録画を**後日あらためて個別に**お願いすることがある。⚠️ O1-C では同意を取らない（お知らせだけ） | 個別の説明と同意 | — | `consent-draft-o1.md` §6・`buildO1ConsentForm` のお知らせ節。⚠️ 運用しているかは確かめていない |
| **O-6** 見守り（期間中） | 研究者 | 台帳の通知を見て連絡する。⚠️ **「途絶」を「やめた」に変換しない**（やめたは本人の申し出だけ）。⚠️ 通知は**悪化したときだけ** 1 通来る。トリガーが消える・認可が切れると何も来ないので、**通知が無いことは異常が無い証拠にならない** → 台帳の「更新」時刻を見る | 「O1 受領台帳」「O1 途絶」 | 6 時間ごとに更新・悪化時に研究者宛てに通知 | `GSE_O1_Ledger.gs` 冒頭 |
| **O-7** 終了 | 研究者 → 参加者 | 終了を伝え、**O1-S** の URL を渡す。参加者は**自動起動をオフにしてからフォルダを消す** | **O1-S**・README 【4】末尾 | — | ⚠️ 終了の案内の文面と O1-S の渡し方は未整備（§6 穴 1・2） |
| **O-8** 受領・復号 | 研究者 | `gse-unpack` で復号。⚠️ **gse-dataset へ出さない**（削除が git 履歴の書き換えになるため `sync-session` が O1 を弾く）。解析は事前登録（凍結後）どおり。`(P-ID, o1_install_id)` で端末を分ける | — | — | `docs/pilot-runbook.md` §4.1〜4.2・`docs/o1-deletion-ledger.md` §4・事前登録草案 §4 |
| **O-9a** やめた（随時） | 参加者 → 研究者 | 理由を聞かず、その場で**削除も希望するかを確かめ**、答えを人単位の台帳に書く。⚠️ **削除の求めが無くても自動起動を外してもらう**（B-8。外さないと次のログインで記録が再開する） | — | — | `docs/o1-deletion-ledger.md` §2・§3 B-8・`docs/person-lifecycle-ledger-template.md` 制約 3（⚠️ §6 穴 6） |
| **O-9b** 削除の求め（随時） | 参加者 → 研究者 | 理由を聞かず P-ID と時間帯だけ受け取る → チェックリスト A（研究者側）・B（端末側）→ 削除台帳 §6 に 1 行。A-13（O1 登録ログ）・A-14（受領台帳）は**行を消さず**該当列を空にして `削除済` にする（tombstone・手作業） | — | — | `docs/o1-deletion-ledger.md` §2・§3・§6 |

---

## 5. 2026-10-07〜08 の O1 開始に固有のこと

| いつ | 誰が | 何をする | 正本 |
|---|---|---|---|
| 10-07 | 研究者 | Drive の zip を v0.1.40 に差し替える | `docs/o1-distribution-tag.md` §v0.1.40 |
| 10-07 | 研究者 | 同意の改訂（識別子の 1 行＋公表と公開の一文）を O-1 の手順で反映 | `.steering/20261007-o1-install-id/consent-revision-proposal.md`・`.steering/20261007-research-use-and-release/o1-consent-today-proposal.md` |
| 10-07 | 研究者 | **反映の前に登録した人がいれば**、新しい項目について説明して同意を取り直す（取り直すまで、その人の結果は公表の対象にしない） | ADR-039 D2 |
| 10-08 | 研究者 | O1 の案内（G1 の案内と同じ日にしない） | §1 原則 3 |
| 随時 | 研究者 | 参加者ごとに**どの版の同意に答えたか**を人単位の台帳に記録する（ADR-039 の再同意で、足りない層だけを尋ねるために要る） | ADR-039 D2・D4 |
| 並行 | 研究者 | 倫理の問い合わせ（ZEN大学 → 外部の委員会 → BRM の編集者） | `.steering/20261007-research-use-and-release/inquiry-drafts.md` |

---

## 6. ⚠️ まだ決まっていない・仕組みが無いもの（運営の穴）

| # | 穴 | 影響 | 案 |
|---|---|---|---|
| 1 | **O1-S の URL を誰がいつ渡すか**が、コードにも文書にも無い（トリガーは O1-C 用の 1 本だけ） | アンケートが取れない | 終了の連絡メールに URL を入れて研究者が手で送る（文面は被験者向け文書なので研究者の承認が要る） |
| 2 | **O1 の期間の終わり**の決め方と、参加者への**終了の案内**の文面が無い | 自動起動が残り、期間後も記録が続く | 事前登録草案【決 3-a】（3 週間は下限・解析は最初の 3 週間）に合わせ、終了日を登録時に伝えるか、終了の連絡で「自動起動をオフ → フォルダを消す」を案内する |
| 3 | **G1 の受領 `.age` の復号**を G1 向けに書いた手順が無い（`experiments/20260801-controlled-friction-task/data.md` に送付フロー〔匿名化 → `.age` → G1 と明記〕はあるが復号のコマンドは無い。`docs/pilot-runbook.md` §4.1 の流用） | 手順の取り違え | G1 向けの復号の数行を `data.md` に足す |
| 6 | O1 の「やめた」の扱いが正本どうしで食い違う: `docs/o1-deletion-ledger.md` は「参加の取りやめも同じ経路で扱う・時間帯＝全期間」、`docs/person-lifecycle-ledger-template.md` 制約 3 は「やめても削除を求めないことができる（別の申し出）」 | 「やめた」だけの人の記録を消すか残すかが決まらない | 本書 O-9a は後者（確かめてから）に寄せた。正本どうしを揃えるのは研究者が決める |
| 4 | **人単位の台帳の実物が無い**（設計のみ） | 「やめた」「削除」「同意の版」が散らばる | テンプレートから実物を作る |
| 5 | O1 の期間の表記が、同意文書（「数日〜数週間」）と事前登録草案（3 週間）でずれる | 参加者の期待とずれる | 期間を同意文書か受付メールで具体にするかを研究者が決める |

---

## 関連

- ADR-014（O1）・ADR-034（G1 と O1 の並行）・ADR-038（`o1_install_id`）・ADR-039（研究利用と公開）
- `docs/g1-deletion-ledger.md`・`docs/o1-deletion-ledger.md`・`docs/person-lifecycle-ledger-template.md`
- `docs/o1-roster-operations.md`・`docs/o1-distribution-tag.md`・`docs/pilot-runbook.md` §4
