# 引き継ぎ: TRACE —— 較正の 2 回目の冊と案内を作る・D9 の英文を研究者が確かめる

作成 2026-10-29。前のセッションの判断は decisions.md の判断 124・125。

## 0. 次のセッションでやること

研究者の指示（2026-10-29）で、次の 2 つを 1 回のセッションで行う。

1. 較正の 2 回目の冊と案内を作る（私が作る。符号化はしない）
2. D9 の英文を研究者が確かめる（研究者が読み、直すところがあれば私が直す）

2 回目の符号化そのものは、ここではしない。12 月に行う（別の引き継ぎ `next-session-ai-fatigue-c-calibration-pass2-run.md`）。

始める前に読むもの:

- 作業の場所: worktree `/Users/johnd/GSE-prototype-af-c`（枝 `docs/ai-fatigue-c-outline`・push 済み）
- steering: `.steering/20261017-ai-fatigue-c-outline/` の decisions.md（判断 106・107・123・124・125）、deviations-draft.md の D9、tasklist.md
- 登録: `~/TRACE/registration-en.md` の 33 行（Roles の AI assistant）、49 行、323 行（較正）、330 行（GSRR-44 の 6・共著者は較正に入らない）、334 行（GSRR-46）

## 1. 時期の決まり（2 回目を今やらない理由）

- 登録 323 行: 「the first pass in November 2026 and the second in December 2026, at least four weeks later」。
- 1 回目は 2026-10-28 に閉じた（判断 124）。4 週は 11-25 以降で満たし、12 月の条件と合わせて、2 回目は 12-01 以降に始める。
- 研究者は「一気に終わらせてもよいのでは」と聞いた（2026-10-29）。上の 2 つの決まりと、1 回目の全欄を 10-28 に確かめ直したので記憶がいちばん新しいことを理由に、12 月まで待つと答えた。
- 共著者（著者 2）は較正に入らない（登録 330 行・478 行・判断 33）。共著者が全部を符号化するのは本体の集合で、較正の改訂を登録した後に 1 回だけ行う。研究者が「較正も共著者が全部参加すると決めていなかったか」と聞いたので、この文を示して答えた。

## 2. タスク 1: 2 回目の冊と案内を作る

### 2.1 1 回目の作り方（判断 106・107）

- 符号化の冊: `~/TRACE/scripts/c_coding_book.py make --coder coder1 --ids <探索の集合の ID> --out <dir>` で作り、名の頭に「較正1回目」を付けた。ID は `~/Documents/TRACE/calibration/exploration.ids`（11 件）。
- 案内の冊: `.steering/20261017-ai-fatigue-c-outline/scripts/make_calibration_guide.py --pass 1 --coder coder1 --links links.json --items <核 1 の items.csv> --titles-dir ~/TRACE-screening/check34-r3/in --trace ~/TRACE --out <dir>`。中身は、はじめに・一覧（題名と全文のリンク）・ZEF の 15 項目の表。`--pass 2 --coder coder2` を受け付ける。
  - `--items` は核 1 の `items.csv`（`~/GSE-prototype-af-core1/.steering/20261014-ai-fatigue-core1-item-analysis/items.csv`）。脚本は ZEF の項目の文と前置きだけを写し、版 1 の判定の列は写さない（判断 106）。
  - `links.json` は `~/Documents/TRACE/calibration/links.json`。
- 手元の場所は `~/Documents/TRACE/calibration/pass1/`、Drive の場所は `TRACE_calibration/pass1/`。

### 2.2 2 回目で変えること

- 符号化の冊: `make --coder coder2 --ids ~/Documents/TRACE/calibration/exploration.ids --out ~/Documents/TRACE/calibration/pass2` で作り、名を `TRACE_較正2回目_符号化_coder2.xlsx` にする。書き出しは隠しシートの回とファイル名の `_coder2` で読む（名を変えても動くことは 1 回目で確かめた）。
- 案内の冊: `--pass 2 --coder coder2 --out ~/Documents/TRACE/calibration/pass2`。
- 案内の「この冊の位置づけ」に、次の 3 文を足す（脚本を直す。`--pass 2` のときだけ出すか、両方に出すかはコードを見て決める）。1 回目の手順にこれが無かったのは私の落ち（判断 124・125）。
  - この符号化は著者 1 本人が行う。冊・手順・全文を AI のエージェント（Codex・Claude などを含む）に渡さない。冊を AI や脚本で開いて書き込まない。
  - 1 回目の冊と書き出し（Drive の `pass1/`、手元の `pass1/`・`pass1-closed/`・`pass1-returned/`）を開かない。
  - 版 1 の値（核 1 の `items.csv`・`codebook.md`）と、C5 の照合（`~/TRACE-calibration-c5/`）を開かない（GSRR-46）。
- 保存は Excel か Google スプレッドシートで行う。返ってきた冊の保存の道具（`docProps/app.xml`）を見て、openpyxl などの脚本なら止める（判断 125 の Google スプレッドシートの書き出しは `docProps/app.xml` を持たない。そのときは `kMDItemWhereFroms` と、研究者の言葉で確かめる）。

### 2.3 確かめ

- 2 冊が 1 回目と同じ形であること（シートの名・列・プルダウン・ID の並び）。1 回目の冊とシートごとに比べる。値の入った 1 回目の冊ではなく、作ったままの 1 回目の冊が無ければ、`make --coder coder1` を一時ディレクトリで作って比べる。
- 2 回目の冊に値が何も入っていないこと。
- 案内に 1 回目の値が入っていないこと（ZEF の表の型・境界・対象の列が空）。
- 作った 2 冊は読み取り専用にし、SHA-256 を decisions.md に書く。Drive にはまだ置かない（12-01 に置く・別の引き継ぎ）。
- 案内の脚本を直したら、code-reviewer と /cross-review を通す。Codex の今日の残りを `.codex/budget.json`（GSE-prototype 側・未コミット）で確かめる。2026-10-28 は上限を超えた。

### 2.4 決めてほしいこと（研究者に AskUserQuestion で聞く）

- Drive の `TRACE_calibration/pass1/` を、2 回目の間は見えない所へ移すか。推奨は移すこと（見ないで行う条件を物で守るため）。移す先は研究者が選ぶ。移すのは研究者の手で（共有の設定は変えない）。

## 3. タスク 2: D9 の英文を研究者が確かめる

- D9 の日本語の文案: `deviations-draft.md` の 135 行から。
- 英文の場所（TRACE `a30530d` の時点・行は変わりうるので grep で探す）:
  - `~/TRACE/manuscript/draft/tables.tex` の表 2 の 2026-10-28 の行（「Roles (AI assistant); GSRR-44 (calibration…」）
  - `main.tex` の方法の節（「The work is done by people, except the first calibration pass (Table~2)」）
  - `main.tex` の限界の節（「The first calibration pass was settled by the first author…」）
  - `main.tex` の Use of AI（「It also drafted every value of the first calibration…」）
  - 表 4 の注（「the first calibration pass was settled from an AI draft (Table~2)」）
- 研究者に PDF（`~/TRACE/manuscript/draft/main.pdf`）の該当のページを示し、直す点を聞く。直すときは新しいコミットで（rebase・squash をしない）、`latexmk -pdf main.tex`（figure1 を先に組む）と `uv run python make_docx.py` で組み直す。組版の警告は前からある 4 つ（Float too large 1・Overfull 3）。
- 2026-10-29 の引用の確かめは、Codex の冊を使わずに研究者が付け直したので逸脱にしていない（判断 125）。原稿に足すことは無い。
- 確かめが終わったら、Drive の草稿（`TRACE` 直下と共著者のフォルダの docx・PDF）を置き換えるかを研究者に聞く。置き換える前に、Drive の版が前に置いたときのままかを cmp で確かめる。

## 4. 守ること

- 返答・記録・AskUserQuestion は日本語で書く。記号や絵文字を多用しない。決めてほしいことは、推奨と理由を添えて AskUserQuestion で聞く。
- 記録ごとの判定の値・抄録・全文を repo に写さない（道具が書く CSV は除く）。steering には件数だけ書く。
- 較正の冊を私が開いて値を読まない。1 回目の閉じた版（`pass1-closed/`）の値も読まない（2 回目の前に私が中身を話すと、研究者が見たのと同じになる）。
- TRACE で rebase・squash をしない。`git add -A` を使わない。PR は研究者が確かめてから出す（push だけで止める）。
- Drive の共有の設定と GitHub の公開設定は変えない。
- キーストローク内容と NDJSON の生ログは外部 LLM に送らない。Codex の入力に、送信禁止の出力や screening の CSV そのものを含めない。
