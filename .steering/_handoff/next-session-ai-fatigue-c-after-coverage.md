# 引き継ぎ: C（TRACE）—— 確かめの検索の後。共著者に送る前の最後の確かめと、返事の後

作成 2026-10-18（Mac）。
- 返答・記録・AskUserQuestion の引数は日本語で書く。記号を多用しない。
- 決めてほしいことは AskUserQuestion で、推奨と理由を添えて聞く。

## 始め方

worktree `/Users/johnd/GSE-prototype-af-c`（ブランチ `docs/ai-fatigue-c-outline`・push 済み・PR なし）で新しいセッションを開き、次を打ち込む。

```
.steering/_handoff/next-session-ai-fatigue-c-after-coverage.md を読んで、§2 の順に進めて。
```

## 1. ここまで（一次は `.steering/20261017-ai-fatigue-c-outline/decisions.md` 判断 38〜42）

- 判断 38: 登録の前に、見落としを数える検索（確かめの検索）を足した。本体の集合の枠は元の DB（追加候補 264 件）のまま。OpenAlex・Europe PMC・ACM DL を Q6 の式で 1 回だけ検索し、元の DB に無い新しい記録から無作為に 300 件（種 20261022）を抜き、判定者 1 と AI で同じ規則でふるう。含めた研究は確かめの層として 2 回符号化する（本体の集合・問題の型の文には入れない）。共著者の仕事には入れない。12/31 の締めは変えない。
- 判断 40: 2026-10-18 に検索を走らせた（OpenAlex 10,827・Europe PMC 1,455・ACM 702 → まとめて 11,052 → 元の DB と重なる 198 → 新しい記録 10,854）。検索はやり直さない（脚本も、記録があれば打ち直しを止める）。書き出しは `~/Documents/TRACE/search/2026-10-18/`（repo の外）、書誌と数と記録は `registration-attachments/coverage/`。
- 判断 41: 300 件を選別の材料にした（`~/Documents/TRACE/data/records-coverage.json`・meta.json・ja.json）。Europe PMC の後始末の誤りを直して抜き直した（189 件は同じ・111 件が入れ替わり。登録の前で誰も判定していない）。選別の順の試し（564 件）は `registration-attachments/dryrun/*-2026-10-18.csv`。Drive の 2 冊（判定者 1 用 564 件・全体の DB 34＋564 件）を作り直した。
- 判断 39・42: /cross-review を 2 巡かけて対応した。
- OpenAlex のキーは研究者が `~/.config/openalex/api_key` に置いた（メインは値を見ていない）。

## 2. 次にやること（この順）

### 2.1 研究者に確かめる
- Drive の `TRACE_database.xlsx` を Excel で開き、段 1 に CS で始まる 300 件が交互に並んでいること、ID から文献DB の抄録（英語と日本語）へ飛べることを見てもらう（Excel は閉じてから脚本を打つ）。
- 共著者への相談文（`coauthor-consult.md` / docx）を送る時期。研究者は「土台・DB・中身が揃って実行するだけになってから送る」と決めている。送るのは研究者。送る物は Drive の `TRACE/共著者へ/` にそろえた（判断 43: 草稿の docx・PDF・全体の案内・`登録の後に使う/` に段 1 の本番の冊）。`TRACE/` 直下の古い `main.docx`・`coauthor-consult.docx` は 2026-10-18 の直しの前の版。

### 2.2 共著者の返事が来たら（判断 34 の未着手）
- 登録版の書き換え（GSRR-2・33・37・38・39・40・41・62・65・表 1・2）、`c_screening.py` を判定者 3 人に、共著者が返したファイルの取り込み。確かめの標本は共著者の分に入れない（判断 38）。`make_coauthor_db.py` は 264 件だけを読む。
- Drive の `TRACE/fulltext` を共著者に閲覧のみで共有する（共有の操作は研究者に確かめてから）。

### 2.3 登録の日
- `registration-day.md` の手順どおり。選別の順は dryrun（2026-10-18・564 件）と diff が空であること、`make_coverage_records.py order` で材料の順を振り直すこと。`hash_attachments.py` の目録には添付 3 の確かめの検索の 9 ファイルが入っている。

## 3. 守ること
- 登録の前に 564 件の判定を始めない（判定者 1・AI・共著者のどれも）。
- 抄録・全文・訳・AI の出力・検索の書き出しを repo に写さない。
- 確かめの検索をやり直さない（やり直すと新しい記録と標本が変わる）。
- `git add -A` を使わない。PR は研究者が確かめてから出す（push で止める）。
- Drive の共有の設定は、研究者の確認なしに変えない。
