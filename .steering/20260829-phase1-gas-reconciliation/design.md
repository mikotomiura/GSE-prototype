# design — Phase1 GAS 取り込みと機能棚卸し

作成日: 2026-08-29

---

## 1. 取り込みのアプローチ（実施済み）

### 1-1. 方式の選択: clasp ではなく Chrome + `monaco.getValue()`

| 方式 | 判断 | 根拠（★ 実測） |
|---|---|---|
| `clasp clone` | ❌ 不採用 | ⚠️ **未インストール・未ログイン**。`~/.clasprc.json` が無く、`node_modules/@google/clasp` も無い。→ 研究者の対話ログイン（OAuth 付与）が要る。★ OAuth の付与は勝手に進めない（`browser-verification` §4） |
| Chrome + `monaco.getValue()` | ✅ 採用 | ★ **読み取りのみ**で完結し、承認が要らない。⚠️ 分割の取りこぼしはハッシュで検出できる |

### 1-2. ⚠️★ 分割取得を「私の文脈経由で書き写す」のはやめた

引き継ぎは「8〜10 分割して 1 回ずつファイルに追記」と書いていたが、
★ その形だと **120,825 文字を私が打ち直す**ことになり、⚠️ 無音の写し崩れが起きうる。

→ ★ **ページから直接 `127.0.0.1` のローカル受け口へ POST** した（15,000 文字 × 9 回・逐次 await）。
私は本文を 1 文字も転記していない。⚠️ ハッシュはそれとは独立に突き合わせている。

- ⚠️ 受け口は**自分で立てて自分で止めた**（`python http.server` 相当・ポート 8719）
- ★ CSP / mixed content の懸念は事前に probe で潰した（`http://127.0.0.1` は
  Chrome が potentially trustworthy 扱いなので HTTPS ページからでも到達する）

### 1-3. 実測値

| | 行 | 関数 | UTF-8 バイト | SHA-256 (LF 正規化) |
|---|---|---|---|---|
| 取り込み**前** repo | 1,969 | 41 | 107,994 | `3eb88eec38888b4b…` |
| **GAS 実体** | **3,095** | **84** | **172,411** | **`8c7107f4ca12bd4e471bb96b6006d1549e36822b8ce66afc09c35982dc8517e0`** |
| 取り込み**後** repo | 3,095 | 84 | 172,411 | `8c7107f4ca12bd4e…` ✅ **一致** |

⚠️ `monaco` の `chars` は **UTF-16 単位**（120,825）で、Python の `len()`（120,793）と
**32 だけずれる** = 非 BMP 文字（絵文字）32 個ぶんのサロゲートペア。★ ハッシュで比べているので影響しない。

### 1-4. ⚠️ 「消えていないこと」をどう確かめたか

1. **関数の集合差**: `repo にあって GAS に無い関数 = 0 件`（GAS にしか無い = 43 件）
2. **12 hunk 全部を目視**: 消える 43 行はすべて、対応する上位互換の追加とセットだった
   - `buildDashboardTab_(ss)` → `buildDashboardTab_(ss, f4, f2)` の書き換え（37 行）
   - `applyRosterValidation_` の呼び出し行は `styleRosterModern_` 追加で前後しただけ
3. **全文の SHA-256 一致**（上表）

---

## 2. ★★ 機能の棚卸し（Phase1 / G1 / O1）

> ⚠️ **この表の出所**: いずれも **repo のファイル**を機械で読んだ結果である
> （関数定義の集合 + `ScriptApp.newTrigger` の引数 + `MailApp` / `GmailApp` の呼び出し数）。
> ★ **repo と GAS が一致していることは §3 で別途実測した**ので、repo を読むことが実体を読むことになる。

| 機能 | Phase1 | G1 | O1 | ★ O1 に要るか |
|---|:--:|:--:|:--:|---|
| **未提出者へのリマインダー**（`sendReminders`） | ✅ | ❌ | ❌ | ⚠️★★★ **要検討の筆頭**（→ §4） |
| リマインダーの応答記録（`reminderRecordResponse` / ログタブ） | ✅ | ❌ | ❌ | ★ 上とセット |
| ウェブアプリ `doGet`（メールのボタン受け） | ✅ | ❌ | ❌ | ★ 上とセット |
| 「本日のリマインド予定」監視タブ | ✅ | ❌ | ❌ | ★ 上とセット |
| **進捗ダッシュボード**（到達率・要フォロー・MNAR フラグ） | ✅ | ❌ | ❌ | ⚠️ Phase1 側は凍結する（T-25） |
| **提出状況タブ**（誰がどのブロックを出したか） | ❌ | ✅ `refreshSubmissionTab` | ❌ | ★ G1 が別の形で持っている |
| **定期実行トリガ** | ✅ 2 本 | ✅ 2 本 | ❌ **0 本** | ⚠️★★ **O1 は定期実行が 1 本も無い** |
| フォーム提出トリガ | ✅ `onF1Submit` | ✅ `onG1ConsentSubmit` | ✅ `onO1ConsentSubmit` | — |
| 管理シートの「運用」メニュー（`onOpen`） | ✅ | ❌ | ❌ | ? |
| **運用ステータス トグル**（実施中 / 終了） | ✅ | ❌ | ❌ | ★ 終了時に自動送信を止める仕掛け |
| ロスターの形式・重複検証 | ✅ `validateRoster` | ❌ | ✅ `checkO1RosterShape` ほか | ★ T-23 / T-24 で実装済み |
| ロスターの排他ロック | ❌ | ❌ | ✅ `o1WithRosterLock_` | ★ O1 だけが持つ（T-24） |
| フォーム誤クリア保護 | ✅ `assertClearableForm_` | ✅ `assertSafeToRebuild_` | ✅ `o1AssertSafeToRebuild_` | ✅ 3 者とも有 |
| 実シートのヘッダ突合 | ❌ | ✅ `assertRunHeader_` | ✅ `o1RosterShapeProblem_` | ✅ |
| 配布物の自動送付 | ❌ | ✅ `g1AutoSendPendingMaterials` | ❌ | ★ O1 は配布物が無い（アプリのみ） |

### ⚠️ トリガーの内訳（★ ここが一番効く差）

| | Phase1 | G1 | O1 |
|---|---|---|---|
| 定期実行 | `refreshRosterStatus` / `sendReminders` | `refreshG1RunSheet` / `g1AutoSendPendingMaterials` | **無し** |
| `onOpen` | `onOpenMgmt` | 無し | 無し |
| フォーム提出 | `onF1Submit` | `onG1ConsentSubmit` | `onO1ConsentSubmit` |
| **合計** | **4** | **3** | **1** |

### ⚠️★★★ O1 の監視面は「Drive のフォルダを人が見る」しか無い

`Form_O1/GSE_O1_Submit.gs` は受け取った `.age` を **`DriveApp` でフォルダに置くだけ**である
（`appendRow` / `getSheetByName` / `insertSheet` の呼び出しが **1 件も無い**・実測）。

→ ★ 集計タブもログタブもアラートも無い。**誰がいつ出したか**はファイル名
（`P001_gse_20260302_075721.age`）から人が読み取るしかない。

---

## 3. ★ repo と GAS の乖離を 5 プロジェクト全部で実測した（T-26 の現況）

⚠️ 引き継ぎ §5 は「G1 の GAS プロジェクトも乖離しているかは**未確認**」としていた。
★ 読み取り（ハッシュ比較）は許可されているので、**5 本すべてを測った**。⚠️ 書き込みは一切していない。

| Apps Script プロジェクト | repo のファイル | 行 | 一致 |
|---|---|--:|:--:|
| `GSE_検証フォーム(事前・事後)_Phase1` | `Form_Phase1/GSE_Phase1_Form_Builder.gs` | 3,095 | ⚠️ **乖離していた** → 取り込み済み |
| `GSE_Gate1_Form` | `Form_G1/GSE_G1_Form_Builder.gs` | 3,491 | ✅ 一致 |
| `GSE_Gate1_submit` | `Form_G1/GSE_G1_Submit.gs` | 355 | ✅ 一致 |
| `GSE_O1_Form_Builder` | `Form_O1/GSE_O1_Form_Builder.gs` | 1,663 | ✅ 一致 |
| `GSE_O1_Submit` | `Form_O1/GSE_O1_Submit.gs` | 365 | ✅ 一致 |

→ ★ **乖離していたのは Phase1 だけ**だった。⚠️ ただしこれは「いま測ったら揃っていた」であり、
**乖離を検出し続ける仕掛けは無いまま**である（T-26 は未解決）。

---

## 4. T-25（Phase1 の集計凍結）の実装

### 4-1. ⚠️ `decisions.md` G-1 からの変更点

G-1 は「`refreshRosterStatus()` / `buildDashboardTab_()` は『Phase1 は終了しました』と出して
何もしない形にする」と決めていた。⚠️ ただし **G-1 を書いた時点では GAS の中身が読めていなかった**。

★ 取り込んでみたら、**運用ステータスのトグルが既にあった**
（`PHASE1_CONTROL_TAB` / `PHASE1_STATUS_RANGE` / `実施中` `終了`、`sendReminders` が既に読んでいる）。

→ ★ **新しいトグルを作らず、既にある真実源に相乗りする**形に変えた（→ `decisions.md` D-1）。

### 4-2. 実装

| 追加 | 役割 |
|---|---|
| `phase1Frozen_(ssOpt)` | 凍結判定。⚠️ **fail-closed**（読めなければ凍結） |
| `phase1FrozenNotice_(sh, title, ncol)` | 凍結タブの描画。★ 集計値を 1 つも出さない |

ゲートを置いた場所（★ いずれも `countByPid_` = フォーム全回答の読み出しより**前**）:

- `refreshRosterStatus()` … ロスターの集計列 7〜11 を書かない
- `buildDashboardTab_()` … 凍結表示に差し替え
- `buildReminderPlanTab_()` … 凍結表示に差し替え

### 4-3. ⚠️ fail の倒し方を `phase1Status_` と逆にした理由

| 関数 | 読めないとき | なぜ |
|---|---|---|
| `phase1Status_`（表示用） | 実施中を返す（**fail-open**） | 表示を止めない |
| `reminderSendingAllowed_`（送信用） | 送らない（**fail-closed**） | 送信は取り消せない |
| ★ `phase1Frozen_`（集計用・**新規**） | **凍結する**（fail-closed） | ⚠️ 読めないときに集計を続けると**誤った数字**を出す（下記） |

> ⚠️★★★ ここは「古い数字が残る」問題ではない。**数字が誤りになる**問題である。
> ロスターは 3 研究の共用だが、集計は `active = data.filter(!excluded)` で**全行**を
> Phase1 の母数に数える。→ G1 / O1 の行が増えるほど完了率・平均セッション数が
> **分母だけ増えて下がる**。★ だから凍結時は**数字を 1 つも出さない**。

### 4-4. 検査（`Form_Phase1/phase1_guard_test.cjs`・32 ケース）

- ★ **陽性対照を先に置いた**: 実施中なら集計が**実際に走る**（`FormApp` を開く / ロスターへ書く）。
  ⚠️ これが無いと「常に何もしない実装」でも凍結の検査が緑になる。
- ★ 状態を 3 通り試した: **正常**（実施中 / 終了 × 名前付き範囲 / タブ B2 の両経路）/
  **不在**（コントロール未設置）/ **壊れている**（読取が例外）。
- ★ **変異テストで赤になることを実測**（4 通りすべて赤・無関係な変更では緑のまま）。

> ⚠️★ 検査を書いている途中で **検査自体の空回りを 1 件踏んだ**:
> スタブの `getRange` が A1 表記（`"B2"`）を解釈できず、
> 「終了(タブ B2 フォールバック)」が**値を読めないせいで** false を返していた。
> ★ つまり隣の「実施中(タブ B2)」は**正しい理由で緑だったのではない**。→ スタブを直して両方を有効にした。

---

## 5. ⚠️ T-29: ウェブアプリ URL をコードから外した

取り込んだコードに `REMINDER_WEBAPP_URL = "https://script.google.com/macros/s/…/exec"` があり、
★ そのままコミットすると `check-o1-release-readiness.sh` が
**「⚠️★★★ 秘密が git に入る（実 endpoint）」で赤**になった（実測: 通過 15 / 未達 2）。

→ ★ **push 前だったので、履歴に残す前に**スクリプト プロパティ
（`GSE_REMINDER_WEBAPP_URL`）読み出しへ変えた。→ 通過 16 / 未達 1 に復帰。

⚠️ **したがって取り込みコミットは GAS と 1 箇所だけ異なる。** 貼り戻しで再び一致する。

★ 退避した実 URL: `<scratchpad>/REMINDER_WEBAPP_URL.value.txt`（⚠️ repo 外・コミットしていない）
