# 引き継ぎ: TRACE —— 較正の 2 回目を行い、一致を出し、改訂を登録する（2026 年 12 月）

作成 2026-10-29。この引き継ぎは、`next-session-ai-fatigue-c-calibration-pass2-prep-and-d9.md`（2 回目の冊と案内を作る）が済んでから使う。

## 0. いつ始めるか

- 2026-12-01 以降に始める。登録 323 行: 「the second in December 2026, at least four weeks later」。1 回目は 2026-10-28 に閉じた（判断 124）ので、4 週の条件は 11-25 以降で満たし、12 月の条件で 12-01 からになる。
- 12-01 より前にこの引き継ぎを開いたら、何もせずに日付を研究者に伝えて止める。
- 研究者の選択（判断 126）: 12-01 に始め、改訂の案は 12 月中旬までに出す。本番の符号化は締めの日（12-31）の後なので、12 月でも全体は遅れない。
- 同じ 12 月に、選別の締めの日（2026-12-31）の作業もある（6 節）。順は較正が先でも後でもよい。

始める前に読むもの:

- worktree `/Users/johnd/GSE-prototype-af-c`（枝 `docs/ai-fatigue-c-outline`）の `.steering/20261017-ai-fatigue-c-outline/` の decisions.md（判断 106・107・124・125 と、2 回目の冊を作った判断）と tasklist.md
- 登録 `~/TRACE/registration-en.md` の 33 行・49 行・323 行（較正の単位・80% の線・5 件の線・改訂の決まり）・330 行・334 行（GSRR-46）

## 1. 冊を Drive に置く（私）

- 置くもの: `~/Documents/TRACE/calibration/pass2/` の 2 冊（`TRACE_較正2回目_符号化_coder2.xlsx`・`TRACE_較正2回目_案内とZEF_coder2.xlsx`）。置く前に、作ったときの SHA-256（decisions.md）のままかを確かめる。
- 置く先: Drive の `TRACE_calibration/pass2/`（`~/Library/CloudStorage/GoogleDrive-mmiura.network@gmail.com/マイドライブ/Doe_Systems/Reserch_production/GSE/AI-fatigue/TRACE/TRACE_calibration/`）。全文は同じフォルダの `fulltext/` にある。共有の設定は変えない。
- 置いた後に、Drive の版の SHA-256 を手元の版と照らす。
- Drive の `pass1/` を前のセッションで移したかを確かめる（研究者が選んだこと）。移していなければ、2 回目の間は開かないことを研究者に伝える。

## 2. 研究者への手順（私が書いて渡す）

手順の冒頭に、次の 3 つを必ず書く（1 回目と引用の確かめで落ちた・判断 124・125）。

1. この符号化は著者 1 本人が行う。冊・この手順・全文を AI のエージェント（Codex・Claude などを含む）に渡さない。冊を AI や脚本で開いて書き込まない。
2. 1 回目の冊と書き出しを開かない。版 1 の値（核 1 の `items.csv`・`codebook.md`）と C5 の照合（`~/TRACE-calibration-c5/`）も開かない（GSRR-46）。
3. 終わったら、冊を Excel か Google スプレッドシートで保存して知らせる。

手順の中身は 1 回目の案内（判断 123 で示した手順）と同じでよい。記入する冊・ZEF のシート・全文の場所は案内の冊に書いてある。

私は、研究者が符号化している間に冊を開かない。値について聞かれても、1 回目の値は答えない。

## 3. 返ってきた冊を確かめる（私）

- Excel（または Google スプレッドシートの書き出し）で保存されたかを見る。`docProps/app.xml` の Application が `Microsoft Excel` か、Google の書き出し（`app.xml` が無く、`kMDItemWhereFroms` が docs.google.com）であること。openpyxl など脚本の名なら止めて研究者に聞く。
- 同じ時刻に Codex のセッション（`~/.codex/sessions/2026/12/…`）が冊の名を含んでいないかを、`grep -l` で確かめる（本文は開かない）。判断 124・125 では、どちらも Codex の作業が見つかった。
- 控えを読み取り専用で取り、SHA-256 を記録する（`~/Documents/TRACE/calibration/pass2-closed/`・`SHA256SUMS`）。
- Google スプレッドシートを使ったなら、Drive に別の写しができている。研究者にゴミ箱へ移すよう頼む（判断 125）。

## 4. 一致を出す（私）

- 書き出し: `cd ~/TRACE/scripts && uv run -q --with openpyxl python c_coding_book.py export --out <dir> <2 回目の冊>`。`records_coder2.csv`・`instruments_coder2.csv`・`items_coder2.csv`・`c4f_coder2.csv` ができる。
- 1 回目の書き出しは `~/Documents/TRACE/calibration/pass1-closed/export/`（`*_coder1.csv`・読み取り専用）。両方の CSV を 1 つの作業ディレクトリ（repo の外・例 `~/Documents/TRACE/calibration/agreement/`）に写す。
- 一致: `uv run -q python c_synthesis.py --agreement <dir>`。既定の組は著者 1 の 2 回（coder1 と coder2）。`--pair` は付けない（`--pair prediscussion author2` は本番用）。
- ZEF の 15 項目は符号化の冊の外（案内の冊の ZEF のシート）なので、脚本は数えない。型・境界・対象の一致を項目ごとに別に数え、ZEF の項目の一部がコードブックの例と重なるので一致が高く出やすい、と結果に書く（判断 106）。
- C4f は、両方の回で再計算した結果だけを比べる（登録 323 行）。

## 5. 改訂を作り、登録する（研究者と私）

登録 323 行の決まり:

- 比べる数が 5 以上で、百分率の一致が 80% に届かない単位は、定義を直し、本番の符号化の前に改訂として登録する。
- 比べる数が 5 未満の単位は報告するが、改訂のきっかけにしない（較正されない）。その単位の一覧を較正の結果に添える。
- 改訂の根拠は 2 回の食い違いだけにし、根拠にした記録の ID を添える。追加候補の選別で読んだものは使わない。例題 W01〜W04 の 17 点（判断 107）も、そのままでは根拠にならない。
- 派生の値と AI の下書きとの一致は基準にしない。kappa は添えるが基準にしない。
- 改訂した定義は本番の前に確かめ直さない（本番の 2 回で見る・限界に書く）。

進め方:

- 80% 未満の単位ごとに、食い違った記録の ID と、両方の回の値（研究者が見る。私は repo に値を写さない）から、定義の直しの案を作る。案ごとに AskUserQuestion で研究者に聞く。
- 本番の前の改訂の候補に、すでに次が並んでいる: 主の尺度の `instrument_id` を `main` にする決まり、`language` を ISO 639-1 にする決まり（判断 106・案内の冊）。これらは 80% の線とは別の筋（列の辞書の書き漏らし）なので、改訂の文で根拠を分けて書く。
- 登録の改訂は、凍結した登録の文を変えずに、改訂の版として出す（OSF の手続きは研究者が行う）。原稿の表 2 に改訂の行を足す。
- C4f の AI の下書きと C5 の照合は、改訂の後もまだ開かない。開くのは本番の 2 回と 3 回目と、共著者との話し合いが決まった後（GSRR-46）。
- 1 回目が AI の下書きから決めたものであること（D9）を、較正の結果に添える。限界の節の文（`main.tex`「The first calibration pass was settled by the first author…」）と合わせる。

## 6. 同じ 12 月にあること

- 選別の締めの日（2026-12-31）の後: 保留の判定し直しを締める、`c_screening.py screening-csv` を作り直す、`manuscript/draft/screening_values.py` を走らせ直す、状態の注の暫定の文を直す、`release` を走らせ直して `screening/` の公開のファイルを新しいコミットで置き換える（判断 125）。
- 改訂を登録した後（1 月ごろ）: 共著者の練習の冊。付録 7 の架空の 12 例を、鍵も所見も見ずに符号化する（素材は `~/TRACE/registration-attachments/validation-cases/`）。共著者は較正に入らない（登録 330 行）。
- 共著者の本体の集合の符号化は、本体の集合を閉じ、改訂を登録してから。順は `c_synthesis.py --second-coder-order`（seed 20261025）。

## 7. 守ること

- 返答・記録・AskUserQuestion は日本語で書く。記号や絵文字を多用しない。決めてほしいことは、推奨と理由を添えて AskUserQuestion で聞く。
- 較正の値（1 回目・2 回目とも）を repo と steering に写さない。steering には件数・一致の割合・単位の名・記録の ID だけを書く。
- TRACE で rebase・squash をしない。`git add -A` を使わない。PR は研究者が確かめてから出す。
- Drive の共有の設定と GitHub の公開設定は変えない。
- Codex の入力に、較正の冊・書き出しの CSV・全文を含めない。
