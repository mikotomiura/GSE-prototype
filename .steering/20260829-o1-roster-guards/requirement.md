# O1 のロスター書き込みに防波堤を足す（OS 列 / P-ID 重複 / 誤指定）

## 背景

★ 2026-08-29 の配備検証と cross-review で、**ロスターの読み書きに 3 つの穴**が見つかった。
⚠️ どれも「P-ID↔個人の対応表」＝ Phase1 / G1 / O1 の**共用 1 枚**に対する書き込みであり、
壊れると `docs/o1-deletion-ledger.md` §5b の削除手順が履行できなくなる。

| 起票 | 穴 | 一次資料 |
|---|---|---|
| **T-22** | O1-C は `a.os` を持っているのに ⚠️ **D 列（OS）を埋めていない** | `onO1ConsentSubmit` が `appendRow([pid, name, email])` の 3 列だけ |
| **T-24** | ⚠️★★★ **採番の排他がプロジェクトを跨がない** | 3 つとも `LockService.getScriptLock()`（O1 `:1048` / G1 `:3393` / Phase1 `:1309`）。★ 別プロジェクト＝**別のロック** |
| **T-23** | ⚠️ ロスターの**誤指定を機械で止められない** | `o1IsKnownWrongRoster_` は既知の 1 シートを弾く denylist。★「参加者ロスター」タブを持つ新シートは素通りする |

★ さらに `.gs` ヘッダの逐語「**自動操作は関数セレクタに効かない**」が**誤り**と判明したので直す
（→ `.steering/20260829-o1-builder-config-to-properties/decisions.md` D-3）。

### ⚠️ T-24 が実害になる筋道（★ 空論ではない）

★ Phase1 自身がこの race をコメントに書いている（`GSE_Phase1_Form_Builder.gs:1306-1308` 逐語）:
> 両方が同じ max を読んで同一 P-ID を**重複発番しうる**（GAS トリガはシリアライズ非保証）。

⚠️ その対策の `getScriptLock()` は**スクリプト プロジェクト単位**である。
★ G1 と O1 を別プロジェクトにするのは 2026-08-07 の事故対策で**必須**なので、この構成は変えられない。
→ ⚠️ **G1-C と O1-C がほぼ同時に提出されると、同じ P-ID が 2 人に出る。**
★ 混ざると `.age` / `metrics/<PID>/` / 同意記録が 1 つの P-ID に同居し、**削除要求が履行不能**になる。

## ゴール（★ Done は exit code で言える形）

- [ ] `node Form_O1/o1_form_builder_test.cjs` が緑（★ 101 → 追加ケースぶん増える）
- [ ] `bash Form_O1/o1_form_builder_mutation_test.sh` が **全変異赤**（★ 新しい検査を外すと赤になる変異を足す）
- [ ] `bash scripts/check-o1-release-readiness.sh` が **通過 16 / 未達 1**（★ 未達は既知の送信 timeout のみ・悪化させない）
- [ ] GAS 上の `GSE_O1_Form_Builder` が repo と **SHA-256 一致**（★ 貼り直して実測）
- [ ] `checkO1FormConfig()` が緑のまま

## スコープ

### 含むもの
- **T-22**: 新規行に `a.os` を D 列へ。★ 既存行は**空のときだけ補充**（C 列と同型）
- **T-24**: 発番直後にロスターを読み返し、⚠️ **自分の P-ID が 2 行あれば受付メールを送らない**（fail-closed）
- **T-23**: ロスターの **ヘッダが `ROSTER_HEADER`(14 列) と一致** ＋ **P-ID 形式のデータ行が 1 行以上ある**ことを要求
- `.gs` ヘッダの「自動操作は関数セレクタに効かない」の訂正
- **T-26 の起票**（repo と GAS の乖離検出）
- macOS 配布 zip の引き継ぎプロンプトを現状（★ 受け口デプロイ済み・ゲート 16/1）へ更新
- 実装後に **O1 プロジェクトへ貼り直し**（★ Claude in Chrome）

### 含まないもの（★ 明示的に Out）
- ⚠️★★★ **`Form_G1/` は 1 バイトも触らない**（★ G1 実施中・研究者判断）
- ⛔ **`Form_Phase1/` と Phase1 の GAS プロジェクト**（→ 下記）
- **T-25**（Phase1 ダッシュボードの凍結）
- O1 側の全行スキャン `validateO1Roster()`（★ 研究者判断で今回は入れない）

## ⛔ ブロッカー: Phase1 は触れない（★ 実測で判明・2026-08-29）

| | 行数 | 関数 |
|---|---|---|
| repo `Form_Phase1/GSE_Phase1_Form_Builder.gs` | 1,969 | 41 |
| **GAS 上の Phase1 プロジェクト** | **3,095** | **84** |

⚠️★★★ **GAS 側にしかないコードが ~1,100 行ある**（リマインダー一式 ＋ ウェブアプリ `doGet`:
`sendReminders` / `reminderClassify_` / `reminderSend_` / `reminderConfirmPage_` /
`reminderRecordResponse` / `reminderHtmlPage_` / `reminderButtonUrl_` / `buildReminderLogTab_` /
`rosterHasPid_`）。

★ 裏取り: `Grep` で repo 全体に **1 件も無い**／`git log --all -S "sendReminders"` が **空**
（＝ **コミットされたことが一度も無い**）。→ ⚠️ **Apps Script が唯一のコピーで、バックアップが無い。**

→ ★ **Phase1 に repo 版を貼るのは破壊行為**なので、T-25 は
`.steering/_handoff/next-session-prompt-phase1-gas-reconciliation.md` へ分離した（研究者判断 2026-08-29）。

## 運用メモ

- /reimagine 適用: **No**（★ 既存の防波堤 3 段と同型の追加であり、設計の選択肢は grill で閉じた）
- grill で閉じた分岐は `decisions.md` を参照
