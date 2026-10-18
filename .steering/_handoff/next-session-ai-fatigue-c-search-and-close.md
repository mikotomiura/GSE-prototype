# 引き継ぎ: C（TRACE）—— 登録の前に検索を足すかを決め、そのあと全体を締める

作成 2026-10-18（Mac）。
- 返答・記録・AskUserQuestion の引数は日本語で書く。記号を多用しない。
- 決めてほしいことは AskUserQuestion で、推奨と理由を添えて聞く。

## 始め方

worktree `/Users/johnd/GSE-prototype-af-c`（ブランチ `docs/ai-fatigue-c-outline`・push 済み・PR なし）で新しいセッションを開き、次を打ち込む。

```
.steering/_handoff/next-session-ai-fatigue-c-search-and-close.md を読んで、§2 の順に進めて。
```

## 1. ここまで（一次は `.steering/20261017-ai-fatigue-c-outline/decisions.md` 判断 36・37）

- DB は Google Drive の `Doe_Systems/Reserch_production/GSE/AI-fatigue/TRACE`（フォルダ ID `1HUmAY2q_yqs_qNYENOTnCv2dE8kJMikc`・共有は所有者だけ）にある。
  - `TRACE_database.xlsx`: 判定者 1 が記入する本物（264 件・判定は空）。作り直すと記入を引き継ぐ。
  - `TRACE_database_all.xlsx`: 読むための全体の DB（探索 34 件の最終判定＋追加候補 264 件）。
  - `fulltext/`: 全文 231 ファイル（全文あり 209 件）。
- 更新は `scripts/update_trace_db.py` を 1 回打つ（Drive への写し → リンクの表 → 2 冊の DB）。DB を Excel で開いたまま打たない。
- 元の文献 DB の最終版は `AI-fatigue/AI_fatigue_database_2026-10-18_final.xlsx`（SHA-256 `0db64ecd…`）。AF002 は全文で含めた。探索の集合は含める 11（中心-A 8・中心-B 3）・保留 2（AF003・AF009）・除外 21。登録版の時系列・GSRR-32・`outline.md`・草稿の Sets の節に反映済み。`check-34.csv`（添付 6）は 2026-10-17 の記録のまま。
- OSF の全文 3 件（R02・R22・R35）は登録の書式を API から組み立てて保存した（`osf_registration_html.py`）。
- 叙述的レビューのセッションから、検索を足す提案が来ている: `/Users/johnd/GSE-wt-narrative-review/.steering/_handoff/next-session-trace-search-proposal.md`（提案であって決定ではない）。

## 2. 次にやること（この順）

### 2.1 確かめから始める
- 研究者に 2 つ聞く（会話で）: 共著者から返事が来たか（来ていれば中身）、2 冊の DB を Excel で開いてリンク・プルダウン・判定の色が効いたか。
- 共著者の返事は 2.2 の決め方に効く（案 A なら、引き受けてもらえる量で決まる）。

### 2.2 検索を足すかを決める（登録の前に必ず）
1. 提案ファイルを全部読む。件数と感度の見積もりは 2026-10-18 の 1 回だけなので、決める前に OpenAlex で数え直す（道具は提案ファイル §3 の `trace-search-estimate/`。DB の写し `dump_out2.txt` は git の外なので、最終版の xlsx から作り直す）。
2. AskUserQuestion で聞く（提案 §5）: 案（A〜D）・期間・情報源・12/31 の締めを保つか。メインの傾きは D、または A を期間で絞った形（共著者の負担と 12/31 を変えずに、枠の偏りへの問いに数で答えられる）。
3. 聞くときに添える事実（2026-10-18 にメインが確かめた）:
   - 提案の「264 件の採択分で感度を数え直す」は、登録の前はできない（登録の前は 264 件を誰も判定しない）。登録の前に使える既知の採択は探索の 11 件だけで、検索語を作るもとになった集合なので感度は甘めに出る。
   - 案 A（Q7 で約 3,100 件）なら、共著者への相談を出し直す（送った相談文は 264 件の 2 割＝50 件くらいを前提。3,100 件の 2 割は約 620 件）。12/31 の締めと、判断 34 の締め（遅くとも 2027-01-31）も見直す。
   - 登録版の GSRR-32 に受け皿がある（「元の DB のための系統的検索は未実施。走らせたら、その新しい記録は同じ条件で候補になる」）。
   - 草稿 `main.tex` 171 行目の「This review ran no search of its own」は、どの案でも直す。
4. 決めたことを `decisions.md` に判断 38 として書く。

### 2.3 採った案を形にする（C なら飛ばす）
- 検索を実行し、式・実行日・件数・書き出しのファイルとその SHA-256 を残す（書き出しは repo の外。抄録を repo に入れない）。登録の添付 3（`query-strings.md`）に足す。
- 登録版（GSRR-32 ほか、検索・標本の枠・数え方に関わる項目）と、草稿の Method を直す。
- 新しい候補を選別に入れるなら、選別の順の一覧（添付 4・GSRR-33）・`c_screening.py`・DB の材料（`records264.json` に相当するもの）・`make_trace_db.py` の扱いを決める。どれも登録の前に固めておく。
- 案 A なら、共著者への相談文（`coauthor-consult.md`・docx）を書き直す。送るのは研究者。

### 2.4 全体を締める
1. 共著者の返事が来ていれば、判断 34 の未着手に進む: 登録版の書き換え（GSRR-2・33・37・38・39・40・41・62・65・表 1・2）、`c_screening.py` を判定者 3 人に、共著者が返したファイルの取り込み。Drive の `TRACE/fulltext` を共著者に閲覧のみで共有する（共有の操作は研究者に確認してから）。来ていなければ、締めの残りだけ進めて、返事を待つことを書いて止める。
2. `/cross-review`（判断 36・37 と 2.2・2.3 の差分。まだかけていない）。
3. `registration-day.md` の手順と、添付のハッシュ（`hash_attachments.py`）が今の中身に合っているかを見る（ハッシュを取るのは登録の日）。
4. `tasklist.md` を閉じ、コミット・push。PR は研究者が確かめてから出す。

## 3. 守ること
- 登録の前に 264 件（と新しい検索の候補）の判定を始めない（判定者 1・AI・共著者のどれも）。見本の `--preview` だけ配ってよい。
- 抄録・全文・訳・AI の出力・検索の書き出しを repo に写さない（材料は `~/Documents/TRACE/`・`~/TRACE-screening/`・Drive）。
- 有料の DB（Scopus・Web of Science・PsycINFO）は使わない（費用ゼロの方針）。
- `git add -A` を使わない。PR は研究者が確かめてから出す（push で止める）。
- Drive の共有の設定は、研究者の確認なしに変えない。
- ブラウザでは、研究者が開いているタブに触れない。自分で開いたタブは閉じる。
