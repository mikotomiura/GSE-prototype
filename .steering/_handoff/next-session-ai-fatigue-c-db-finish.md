# 引き継ぎ: C（TRACE）の DB を仕上げる（全体の DB・判定者 1 用の DB・Google Drive との同期）

作成 2026-10-18（Mac）。
- 返答・記録・AskUserQuestion の引数は日本語で書く。記号を多用しない。
- 決めてほしいことは AskUserQuestion で、推奨と理由を添えて聞く。

## 始め方

worktree `/Users/johnd/GSE-prototype-af-c`（ブランチ `docs/ai-fatigue-c-outline`・push 済み・PR なし）で新しいセッションを開き、次を打ち込む。

```
.steering/_handoff/next-session-ai-fatigue-c-db-finish.md を読んで、§2 の順に進めて。
```

## 1. ここまで（一次は `.steering/20261017-ai-fatigue-c-outline/decisions.md` 判断 33〜35）

### 選別の道具（判断 33）
- `scripts/c_screening.py`: 束を切る → AI の入力 → 著者 1 の判定の書き出し → push の門 → AI の出力の書式の検証と目録 → 食い違い → 最終 → 集計 → 公開。検査は `scripts/check_screening.py`（緑・守りを外した写しはすべて赤）。
- 34 件の 3 回目の出力で端から端まで通した。材料は `~/TRACE-screening/check34-r3/`。
- 登録版 GSRR-33・36・37・41 を道具に合わせて直した。道具は添付 6 に入る（`hash_attachments.py`）。

### 共著者を選別の 2 人目にする（判断 34・B+）
- 全文段と中心の段は共著者も全件。題名・抄録の段は無作為の 2 割（53 件・seed 20261018。一致が 80% 未満なら残りも）。最終は人間 2 人の合意。締めは共著者の全文段が終わる日、遅くとも 2027-01-31。
- 相談文は書き換え済み（`coauthor-consult.md`・docx）。研究者が送り、返事を待っている。
- 登録の後、判定者 1 と AI を先に回し、共著者は後を追う。登録の前には誰も判定しない。
- 未着手（共著者の返事の後）: 登録版の書き換え（GSRR-2・33・37・38・39・40・41・62・65・表 1・2）、`c_screening.py` を判定者 3 人に、共著者が返したファイルの取り込み。

### DB（判断 35）
- 判定者 1 用: `~/Documents/TRACE/TRACE_database.xlsx`（`scripts/make_trace_db.py`）。シートは はじめに・段1（全文の列なし）・段2・3・文献DB・全文・判定基準。見た目は `scripts/trace_style.py`。ID から文献DB の抄録（英語と日本語）へ飛ぶ。段2・3 の「ファイル」から全文を Google Drive で開く（XML は本文の .txt へ）。旧版は `TRACE_database.before-2026-10-18.xlsx`。
- 共著者用: `scripts/make_coauthor_db.py`（段 1 は 2 割の 1 冊、段 2 は束ごと）。見本は `~/TRACE-coauthor/stage1-preview/`（登録の前に配ってよいのはこの見本だけ）。
- AI の選別者は xlsx を使わない（`c_screening.py prepare` が DB の材料から入力を作る）。
- DB の材料（repo の外・`~/Documents/TRACE/data/`）:
  - `meta.json`: 抄録。OpenAlex の欠け 12 件を Europe PMC に替え、抄録の無い 24 件のうち 15 件を API・全文の抄録の節・出版社のページから取った。理由は各記録の `abstract_note`。控えは `meta.before-epmc-2026-10-18.json`。題名だけで判定するのは 9 件（S04-30・S12-23・X01・R31・R19・R15・R40・R44・R45）。
  - `ja.json`: 題名と抄録の日本語の機械訳（Claude）。判定の根拠は英語。GSRR-34 に書いた。
  - `drive_links.json`: 全文の Google Drive のリンク（`scripts/drive_links.py` が同期ファイルの拡張属性から作る）。
- 全文は `マイドライブ/TRACE/fulltext`（228 ファイル・共有は所有者だけ）にも写した。

## 2. 次にやること（この順）

1. **「全体の DB」が何を指すかを研究者に聞く（AskUserQuestion）。** 候補:
   - 追加候補 264 件と探索の 34 件を合わせた 1 冊（34 件は元の DB の最終判定つき）。
   - 判定が進んだ後の、判定者 1・AI・共著者の判定と最終を 1 冊に集めた一覧（読むだけ）。
   - 元の文献 DB（AI 疲労の文献 DB・判定者 1 と 2 のワークブック）の更新。
2. **判定者 1 用の DB の残り。**
   - OSF が開いたら、全文 3 件（R02・R22・R35）を取り直す。
   - 全文を足したら: `マイドライブ/TRACE/fulltext` に写す → 同期を待つ → `drive_links.py` → 抄録が変われば `ja.json` の訳も足す → `make_trace_db.py`。
   - Excel で実際に開き、ID のリンク（ブック内の移動）・Drive のリンク・プルダウン・判定の色が効くかを、研究者の画面で確かめてもらう（Quick Look は見た目しか確かめられない）。
3. **Google Drive との同期（研究者の言う「drive とかとの同期とかもない」）。** 決めること:
   - DB（xlsx）そのものを Drive に置くか。置くなら、研究者が記入する本物はどちらか（`~/Documents/TRACE/` か `マイドライブ/TRACE/`）。`c_screening.py` の `--xlsx` をその場所に向ける。Drive のブラウザ表示では、ブック内のリンクや一部の書式が効かないことがある（Excel のアプリで開く前提か、Google スプレッドシートに変えるか）。
   - DB を作り直すときに、記入済みの判定を消さない手順（いまの `make_trace_db.py` は空の DB を作る。判定が入った後に作り直すなら、判定の列を引き継ぐ仕組みが要る）。
   - 全文の追加と Drive の同期を 1 本の手順（脚本）にまとめるか。
4. **共著者の返事が来たら**（来ていなければ飛ばす）: 判断 34 の未着手（登録版・道具）に進む。Drive の `TRACE/fulltext` を共著者に閲覧のみで共有する（共有の操作は研究者に確認してから）。

## 3. 守ること
- 登録の前に 264 件の判定を始めない（判定者 1・AI・共著者のどれも）。見本の `--preview` だけ配ってよい。
- 抄録・全文・訳・AI の出力の引用を repo に写さない（材料はすべて `~/Documents/TRACE/` と `~/TRACE-screening/` と Drive）。
- `git add -A` を使わない。PR は研究者が確かめてから出す（push で止める）。
- Drive の共有の設定は、研究者の確認なしに変えない。
- ブラウザでは、研究者が開いているタブに触れない。自分で開いたタブは閉じる。
