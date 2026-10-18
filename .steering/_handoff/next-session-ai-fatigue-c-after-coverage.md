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

### 2.0 共著者への案内を作り直す（最初にやる・2026-10-18 の研究者の依頼）
- 研究者（逐語）「.docxは, 研究の内容と分析に行い方と、全体の作業の流れを教える感じにしない？」
- 今の案内（`.steering/20261017-ai-fatigue-c-outline/coauthor-guide.md`・Drive は `TRACE/TRACE_Co-Author/TRACE_共著者への案内_2026-10-18.docx`）は、お願いすることとファイルの使い方が中心。これを、共著者が研究の全体を理解できる案内に作り直す。3 本の柱:
  1. 研究の内容: 問い（RQ1〜RQ5・SQ1〜SQ2・登録版 GSRR-11・12）、TRACE の 7 つのコード（C1〜C7）が何を見るか、叙述的レビューとの違い（外枠の「Relation to the authors' earlier narrative review」）、本体の集合・探索の集合・確かめの標本（判断 38）。
  2. 分析の行い方: 選別の段（段 1・段 2・3 の意味と、段に分ける理由）、符号化の中身（records・instruments・items・c4f・links の 5 つの様式に何を書くか。判断 45 の後の説明の会話を参照）、一致の見方（AMSTAR 2 の項目 5・6・80% の規則・判断 34・44）、集計（問題の型が見られたか・見られなかったか・評価できないか・GSRR-57。頻度は言わない）、感度分析。
  3. 全体の作業の流れ: 今の §6 の全体のスケジュールの表（判断 46）と、共著者の 3 回の受け渡し（段 1・全文の段・符号化）と話し合い・原稿の確認。
- 事実は登録版・外枠・判断の記録で確かめてから書く（verify-before-claiming）。docx は `python3 -I scripts/make_guide_docx.py coauthor-guide.md coauthor-guide.docx` で作り、Quick Look で表と日本語を見る。Drive に上書きする前に、Drive の文が最後に置いた版と同じか（研究者が手を入れていないか）を確かめる。研究者はフォルダや冊の名前を何度か変えているので、置き場所は ls で確かめてから。
- 未決の 2 つも研究者に聞く: Word で番号つきの箇条書きの番号が出ているか（Quick Look では描かれない）、相談文の「草稿・登録の下書き・原稿の外枠を貼っておきます」を直すか、登録版と外枠の docx も用意するか（判断 43 では選ばれなかった）。

### 2.1 研究者に確かめる
- Drive の `TRACE_database.xlsx` を Excel で開き、段 1 に CS で始まる 300 件が交互に並んでいること、ID から文献DB の抄録（英語と日本語）へ飛べることを見てもらう（Excel は閉じてから脚本を打つ）。
- 共著者への相談文（`coauthor-consult.md` / docx）を送る時期。研究者は「土台・DB・中身が揃って実行するだけになってから送る」と決めている。送るのは研究者。送る物は Drive の `TRACE/TRACE_Co-Author/` にそろえた（判断 43・46・47: 草稿の PDF・全体の案内〔全体のスケジュールの表つき・docx は `scripts/make_guide_docx.py` で作る〕・`TRACE_Co-Author_judge-sheet/TRACE_co-author_stage1.xlsx` に段 1 の本番の冊。研究者がフォルダと冊の名前を変えた）。`TRACE/` 直下の古い `main.docx`・`coauthor-consult.docx` は 2026-10-18 の直しの前の版。

### 2.2 共著者の返事が来たら（判断 34 の未着手）
- 登録版の書き換え（GSRR-2・9〔終わりの日 2027-03-31 は間に合わない・判断 46〕・33・37・38・39・40・41・44・47・62・65・表 1・2）。判断 44 も入れる（共著者への段 2・3 は 1 冊にまとめて 2 回目に渡す・符号化の 2 割の一致が 80% に届かなければ共著者が全部。80% を見る単位・全部の場合の締め・保留の記録の再判定を決める）。`c_screening.py` を判定者 3 人に、共著者が返したファイルの取り込み。確かめの標本は共著者の分に入れない（判断 38）。`make_coauthor_db.py` は 264 件だけを読む。
- Drive の `TRACE/fulltext` を共著者に閲覧のみで共有する（共有の操作は研究者に確かめてから）。

### 2.3 登録の日
- `registration-day.md` の手順どおり。選別の順は dryrun（2026-10-18・564 件）と diff が空であること、`make_coverage_records.py order` で材料の順を振り直すこと。`hash_attachments.py` の目録には添付 3 の確かめの検索の 9 ファイルが入っている。

## 3. 守ること
- 登録の前に 564 件の判定を始めない（判定者 1・AI・共著者のどれも）。
- 抄録・全文・訳・AI の出力・検索の書き出しを repo に写さない。
- 確かめの検索をやり直さない（やり直すと新しい記録と標本が変わる）。
- `git add -A` を使わない。PR は研究者が確かめてから出す（push で止める）。
- Drive の共有の設定は、研究者の確認なしに変えない。
