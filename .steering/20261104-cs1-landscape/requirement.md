# cs1-landscape — CS1 打鍵データの俯瞰

## 背景

公開データの俯瞰（`experiments/20261102-public-data-landscape/`）で、KLiCKe と CoAuthor では短い単位（CoAuthor は約 11 分）の中で、人の中の揺れが数え上げの揺れに埋もれた。CS1 打鍵データ [V243] の 2021 年版は 1 人に 8 課題あり、長い単位で人の中の揺れを確かめられる。2026-11-02 に研究者が著者へ利用を問い合わせ、2026-11-04 に承諾を得た（条件は [V243] の引用だけ・判断 1）。

引き継ぎ: `.steering/_handoff/next-session-cs1-reply.md`（ブランチ `docs/handoff-order-cs1-first`・main には未マージ）。順番は研究者の決定で、この俯瞰を先に行い、B の続きの改善の試験はその後。

## ゴール

- 2019 年版（doi:10.7910/DVN/6BPCXN）と 2021 年版（doi:10.7910/DVN/BVOF7S）の `keystrokes.csv` に、俯瞰の L1〜L6 を同じ定義で当て、集計値を `experiments/20261104-cs1-landscape/notes.md` に、言える範囲を限って書く。
- notes に、人ごとの課題の数と 1 単位の長さの四分位を残す（改善の試験で 2021 年版を 2 つ目のデータに使うかを選ぶ材料）。

## スコープ

### 含むもの
- Dataverse の API で `keystrokes.csv` と `readme.txt` だけを取る。SHA-256・大きさ・取得の時刻を `data.md` に書く。
- 列名と出来事の種類・件数の確かめ（中身の文字は出さない）。
- 条件（`conditions.md`）と変換の対応表を、件数を見る前にコミットする。書き手の 3 割を種で取っておく。
- 変換 → replay → 集計。中間は repo の外（`~/gse-public-data/cs1/`）で 1 本ずつ消す。

### 含まないもの
- 課題文・雛形・動画・調査票（`keystrokes-survey.csv`）・`students.csv`・`keystrokes-raw.csv`・`runs1.csv`・`runs2.csv` の取得と使用。
- 挿入・削除の文字の保存。個人の特定の試み・他のデータとの結合・再配布。
- 打鍵の本文・生のファイルを外部の LLM（Codex を含む）に送ること。
- 検定・判定の閾値・ゲート。B の続きの改善の試験。

## 受け入れ条件

- [ ] `data.md` に 2 ファイルの SHA-256・大きさ・取得の時刻がある
- [ ] `conditions.md`（変換の対応表を含む）が集計の前にコミットされている（git log で順序が確かめられる）
- [ ] holdout の人数と一覧の SHA-256 が記録され、集計の入力に holdout の書き手がいないことを確かめた
- [ ] `notes.md` に L1〜L6（L5 は課題を単位）・人ごとの課題の数・1 単位の長さの四分位・言える範囲がある
- [ ] repo の差分に ID・本文・生のファイルが無い
- [ ] code-reviewer と /cross-review を回した（Codex に渡すのは集計と docs の diff だけ）

## 関連ドキュメント

- `.steering/_handoff/next-session-cs1-reply.md`（§2・§3）
- `experiments/20261102-public-data-landscape/conditions.md`・`notes.md`
- `.steering/20261031-gse-public-data-fit-ai-request/survey-datasets.md`（CS1 の列）
- `docs/references.md` の [V243]

## 運用メモ
- /reimagine 適用: No
- 理由: 既存の俯瞰の定義をそのまま別のデータに当てる記述の集計で、設計の選択肢が開いていない（変換の対応表は conditions.md で固める）。
