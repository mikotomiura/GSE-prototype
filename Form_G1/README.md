# Form_G1 — G1 統制タスク実験の Google Form 一式

`GSE_G1_Form_Builder.gs` が **3 つのフォーム**を構築する。文面の真実源は
`experiments/20260801-controlled-friction-task/consent.md` と `preregistration.md` であり、
**このディレクトリは配布と記録の手段**である（`materials/*.md` → `.docx` と同じ関係）。

| キー | 何 | いつ | PII |
|---|---|---|---|
| `G1-C` | 説明・同意 | 開始前・**1 回** | 氏名・メール |
| `G1-M` | 強制比較（操作チェック） | ブロック 3〜9 の直後・**計 7 回** | ★ 被験者 ID のみ |
| `G1-S` | 終了後アンケート | 最後の copy ブロックの後・**1 回** | ★ 被験者 ID のみ |

---

## 配備手順（★ 固定 ID 方式。これを外すと過去の不具合が再発する）

1. **Google Forms で空のフォームを 3 つ作る**（`FormApp.create` は使わない）。
   > ⚠️ Phase1 では `FormApp.create` が実行のたびに別フォームを量産し、被験者に配った短縮 URL が
   > 指すフォームと集計が読むフォームがズレて「**回答が記録されない**」不具合を起こした。
2. 各フォームの編集 URL `https://docs.google.com/forms/d/<ここ>/edit` の `<ここ>` を
   `GSE_G1_Form_Builder.gs` の `FORM_ID_CONSENT` / `FORM_ID_MCHECK` / `FORM_ID_SURVEY` に貼る。
   空のままだと builder は**エラーで停止する**（量産防止のガード）。
3. Apps Script エディタに `.gs` を貼り、`setupG1Forms()` を実行する。
4. `listG1FormUrls()` で回答 URL / 編集 URL を取り出す。回答 URL を実施端末のブックマークに入れる。
5. 各フォームの「回答」タブで**スプレッドシートへのリンク**を作る（CSV 出力に使う）。

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
