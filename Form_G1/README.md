# Form_G1 — G1 統制タスク実験の Google Form 一式

`GSE_G1_Form_Builder.gs` が **3 つのフォーム ＋ 運用管理シート**を構築する。文面の真実源は
`experiments/20260801-controlled-friction-task/consent.md` と `preregistration.md` であり、
**このディレクトリは配布と記録の手段**である（`materials/*.md` → `.docx` と同じ関係）。

| キー | 何 | いつ | PII |
|---|---|---|---|
| `G1-C` | 説明・同意 | 開始前・**1 回** | 氏名・メール（＋任意で P-ID） |
| `G1-M` | 強制比較（操作チェック） | ブロック 3〜9 の直後・**計 7 回** | ★ 被験者 ID のみ |
| `G1-S` | 終了後アンケート | 最後の copy ブロックの後・**1 回** | ★ 被験者 ID のみ |

管理シート（`buildManagementSheet()`）は **2 タブだけ**:

| タブ | 中身 |
|---|---|
| **リンク集** | 3 フォームの URL ＋ 記入パッドの置き場 ＋ 送付先（手動セルは再実行しても保持される） |
| **G1 実施トラッキング** | 1 被験者 1 行。同意 / 実施日 / OS / ビルド / `GSE_DISABLE_PROBES` / `HMM_VERSION` / 配置 / 完了ブロック数 / 各検査の実施 |

★ Phase1 にある **参加者ロスターと進捗ダッシュボードは作らない**（理由は下記）。

---

## ★★ P-ID は Phase1 と共有する（研究者判断 2026-08-03）

**同じ人には同じ P-ID を使う。** 1 人の人間に 2 つの識別子を作らない。

- ★ **採番元は Phase1 の運用管理シート「参加者ロスター」ただ 1 つ。** G1 側では採番しない。
  ⚠️ **2 か所で採番すると必ず衝突する**（別シートを走査しても相手の最大値が見えないため）。
  初参加の被験者は **Phase1 側で採番してから** G1 を回す。
- ★ 同じ理由で **G1 側に参加者ロスターを作らない**。実名↔P-ID の対応表を 2 か所に持たない
  （`data-privacy`）。実名は Phase1 のロスターと G1-C の回答シートにある。
- G1-C に「参加者ID（お持ちの方のみ）」欄を置いた。以前ご参加の方は自分の P-ID を知っているため。
  **必須にしていない**（初参加の方は持っていない）。

### ⚠️⚠️ ID 共有の帰結（必ず読む）

G1 は**第 1 週（blind 較正）モード**で回すので、`session_meta` に
`condition=blind_calibration` / `label_pool=calibration_blind` が刻まれる。
これは **Phase1 の較正セッションとまったく同じラベル**である（`data.md` の B-4）。

★ **ID まで共有すると、被験者 ID による分離が使えなくなる。** 残る分離手段は 2 つだけ:

1. `blocks/P0xx.json` の `file` 列（どの NDJSON が G1 のブロックかを列挙している）
2. ★ **gse-dataset への送付時に G1 であることを明示する** ← **弱い側。省略しない**

（最後の保険として、管理シートに **G1 実施日**を残す。⚠️ ただし日付は成果物には出さない。）

---

## 配備手順（★ 固定 ID 方式。これを外すと過去の不具合が再発する）

1. ✅ **Google Forms で空のフォームを 3 つ作る**（`FormApp.create` は使わない）— **完了**（2026-08-03）。
   > ⚠️ Phase1 では `FormApp.create` が実行のたびに別フォームを量産し、被験者に配った短縮 URL が
   > 指すフォームと集計が読むフォームがズレて「**回答が記録されない**」不具合を起こした。
2. ✅ 各フォームの編集 URL `https://docs.google.com/forms/d/<ここ>/edit` の `<ここ>` を
   `GSE_G1_Form_Builder.gs` の `FORM_ID_CONSENT` / `FORM_ID_MCHECK` / `FORM_ID_SURVEY` に貼る
   — **記入済み**。空のままだと builder は**エラーで停止する**（量産防止のガード）。

   | 定数 | 役割 | 作成時の呼び名 |
   |---|---|---|
   | `FORM_ID_CONSENT` | G1-C 説明・同意 | form1 |
   | `FORM_ID_MCHECK` | G1-M 強制比較 | form2 |
   | `FORM_ID_SURVEY` | G1-S 終了後アンケート | form3 |

   > ⚠️ ★ 3 本とも**空フォーム**だったので、**どれがどの役割になるかはこの割り当てが決める**。
   > `setupG1Forms()` がタイトル・説明・設問を書き込む。
   > **一度でも被験者に URL を配ったら、割り当てを入れ替えてはならない。**
3. Apps Script エディタに `.gs` を貼り、`setupG1Forms()` を実行する
   （3 フォーム ＋ 管理シートが一度に作られる）。
4. `listG1FormUrls()` で回答 URL / 編集 URL を取り出す。回答 URL を実施端末のブックマークに入れる。
5. 各フォームの「回答」タブで**スプレッドシートへのリンク**を作る（CSV 出力に使う）。
6. 管理シートの「リンク集」で、**記入パッドの置き場**と**送付先**の手動セルを埋める。
   ⚠️ 再実行しても手動セルは保持される（Phase1 の `buildLinksTab_` と同じ挙動）。

> ⚠️ 実行時間・クォータに当たったら、`buildConsentForm()` / `buildManipulationCheckForm()` /
> `buildPostSurveyForm()` を単独実行 → 最後に `buildManagementSheet()` を回す
> （URL は Script Properties に残るので集約は成功する）。

### （任意）x.gd で回答 URL を短縮する

★ **G1 は対面実施なので必須ではない**（実験者がブックマークから開く）。
同意フォームだけ**事前にメールで送る**ような場合に効く。

1. x.gd の API キーを取得し、Apps Script エディタで **1 回だけ**次を実行する:

   ```javascript
   function setXgdKey() {
     PropertiesService.getScriptProperties().setProperty("XGD_API_KEY", "★ここにキー★");
   }
   ```

   ⚠️ ★ **実行したらこの関数を消すこと**（エディタのソースにキーが残るため）。
   ⚠️ ★ **キーを `.gs` にもこのリポジトリにも書かない。** 本リポジトリは**一時 public にする運用**がある。
   キーは Script Properties にだけ置く（`.gs` のソースには出ない）。

2. `shortenFormUrls()` を実行する（`setupG1Forms()` からも呼ばれる）。
   結果は Script Properties の `SHORTURL_*` に入り、`buildManagementSheet()` が
   **リンク集タブの「回答URL」列**に反映する（短縮が無ければ通常の回答 URL にフォールバック）。

**設計上の約束**:

- ★ **キー未設定なら何もしない**（ログに案内を出して戻る）。壊れない。
- ★ **冪等**: 既に短縮済みのものは作り直さない。
  ⚠️ 毎回叩くと**別の短縮 URL が量産され**、配った URL と集計が読む URL がズレる
  （Phase1 の `FormApp.create` と同じ壊れ方）。作り直すときは `clearShortUrls()` を明示的に実行する。
- ★ **失敗を黙って飛ばさない**: `status !== 200` ならログに残して**保存しない**
  （エラー文字列を短縮 URL として配る事故を防ぐ）。

## 実施当日

- **G1-C**: 開始前に被験者に回答してもらう。
  ⚠️ 紙の `handouts/G1_説明・同意文書.docx` は**フォームが使えないときの控え**として必ず持参する。
- **G1-M**: ブロック 3〜9 の直後、**1 分休憩の中で** 1 問だけ答えてもらう。
  ⚠️ 紙の様式（`protocol.md §3.1`）を必ず併用可能にしておく。機器トラブルで実験を止めない。
- **G1-S**: 最後の copy ブロックの後。★ **判定には使わない**（`preregistration.md §2.10`）。

## 実施後（★ 手転記を挟まない）

```bash
cd experiments/20260801-controlled-friction-task
python3 assign.py --subject P015 --json > blocks/P015.json      # 割付（実施前でもよい）
python3 forms_to_blocks.py --csv ~/Downloads/G1-M回答.csv --subject P015 --write
python3 validate_blocks.py                                       # 転記の整合を検査
```

⚠️ **CSV を repo に置かない。** タイムスタンプ（実施日時）が入っている。
`blocks/*.json` も `.gitignore` 済みでコミットしない。

---

## ★ 3 フォームの制約は正反対である（取り違えると実験が壊れる）

| | G1-C 同意 | G1-M 強制比較 | G1-S 終了後 |
|---|---|---|---|
| 形式 | 必須チェックボックス ＋ 記名 | ★ **二択のみ**（「どちらでもない」なし） | 二択・3 択 ＋ 自由記述 |
| リッカート | — | ★ **1〜5 は禁止**（`§2.6`） | 使わない |
| 絶対に書かない | どのブロックが難しい条件か（`protocol.md §4.3`） | ★ **HI / LO** | ★ **HI / LO** |
| 「もう一度回答」リンク | 出さない | ★ **出す**（7 回答えるため） | 出さない |

- ★ **G1-M の選択肢は相対表現**（「1つ前のブロックのほう」「直前のブロックのほう」）にしてある。
  被験者にブロック番号を計算させると、そこで 1 つずれる。番号への変換は `forms_to_blocks.py` が行う。
- ★ **設問文を変えたら `forms_to_blocks.py` の `HEADER_KEYS` / 選択肢定数も同じ版に直す。**
  このプロジェクトでは「文書だけ改訂して実装が追随しない」事故が 2 回起きている
  （`.steering/20260802-g1-execution-prep/decisions.md` E-6 / E-7）。

## 関連

- `Form_Phase1/GSE_Phase1_Form_Builder.gs` — 下敷き（固定 ID / `clearForm` / URL 集約の型）
- `experiments/20260801-controlled-friction-task/protocol.md §3` — 紙の様式（バックアップ）
- `.steering/20260802-g1-execution-prep/decisions.md` E-11 — フォーム方式の採用理由
