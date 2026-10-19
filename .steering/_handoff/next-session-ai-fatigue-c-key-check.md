# 引き継ぎ: C（TRACE）—— 反例集のキーの確かめを反映する

作成 2026-10-19（Mac）。研究者が反例集のキーの確かめの表に記入した後に使う。共著者の返事の後の作業（`next-session-ai-fatigue-c-after-coauthor-reply.md`）とは別のセッションで行う（順はどちらが先でもよい。どちらも登録の前に要る）。
- 返答・記録・AskUserQuestion の引数は日本語で書く。記号を多用しない。
- 決めてほしいことは AskUserQuestion で、推奨と理由を添えて聞く。
- キー（期待するコード）は共著者が答えを見ずに解く物。キーの入った物を共著者に見える場所（`TRACE/fulltext/`・共著者に渡す物）に置かない。

## 始め方

研究の物は `~/TRACE`（main は 3105112 以降）。検討の記録は worktree `/Users/johnd/GSE-prototype-af-c`（ブランチ `docs/ai-fatigue-c-outline`）の `.steering/20261017-ai-fatigue-c-outline/`（判断は 63 まで）。

```
.steering/_handoff/next-session-ai-fatigue-c-key-check.md を読んで、§2 の順に進めて。
```

## 1. いまの状態

- 反例集（添付 7・`~/TRACE/registration-attachments/validation-cases/`）: 架空の 12 件と変種 2 件（V05b・V08b）。`cases.md`（事例・共著者が解く）、`key.csv`（入力のコードと導かれる値 exp_*）、`key-items.csv`（C2b の 11 項目）、`findings.md`（決めた点 F1〜F7・冒頭に「author 1 checks every expected code before registration (not yet done)」）。キーは AI と下書きした（判断 58）。
- 照合: `scripts/check_validation_cases.py` が、キーの入力から集計の脚本で導いた値と exp_* を比べる（14 件一致）。脚本とキーが同じ誤りをしていれば見えないので、研究者が導かれる値も定義から確かめる（判断 63）。
- 確かめの表（判断 62・63）: `~/Documents/TRACE/key-check/TRACE_反例集キーの確かめ.xlsx`（手元）と、Drive の `Doe_Systems/Reserch_production/GSE/AI-fatigue/TRACE_第一著者のみ/TRACE_反例集キーの確かめ.xlsx`（研究者が記入する方）。作り直しは `.steering/20261017-ai-fatigue-c-outline/scripts/make_key_check.py`（既にあれば止まる）。
  - 『入力のコード』322 行（14 件×23 列: 入力 17・導かれる値 6）、『項目のコード』11 行。欄は 確認（未確認・合っている・違う・迷う）・正しい値・理由・メモ。『事例』に本文。

## 2. 次にやること（この順）

1. 研究者に、どちらの写しに記入したかを聞き、その表を読む（`uv run --with openpyxl` で読む。Drive の写しは同期を待ってから読み、手元の写しと取り違えない）。「未確認」が残っていれば、残りの数と事例を研究者に伝えて、続けるか止めるかを聞く。
2. 「違う」の行: 事例の本文（`cases.md`）と、登録の下書き GSRR-43 の定義・`findings.md`・コードブック第 2 版（`codebook-c2b-en.md`）に照らし、研究者の値が定義から導けるかを一次で確かめる。
   - 定義どおりなら、キー（`key.csv`・`key-items.csv`）を直す。入力を直したら exp_* は手で直さず、集計の脚本で導いた値と照らして直す（`check_validation_cases.py` が一致するまで）。
   - 研究者の値が定義から導けない、または定義が 2 つの値を許すなら、それは定義の穴。AskUserQuestion で、定義を直すか（どう直すか）を推奨と理由を添えて聞く。
3. 「迷う」の行: 定義が 1 つに決めないなら、2 と同じく定義の穴として聞く。決めたら `findings.md` に新しい所見（F8 以降）として書く。
4. 定義を変えた場合: 登録の下書き GSRR-43（と関係する GSRR）・コードブック・`c_synthesis.py`（導き方が変わるなら）・`make_dummy.py`・`cases.md`（事例の文が定義の変化で意味を変えるなら）・外枠・草稿の該当箇所をそろえる。版を上げる（登録の下書き・外枠）。
5. 全部の行が確かめられたら、`findings.md` の冒頭の「not yet done」を、確かめた日と結果（直した数）に替え、版を上げる。登録の下書きの添付 7 の記述（GSRR-44 の 1）と合うかを見る。
6. 検査を全部（`make_dummy.py`・`check_synthesis_mutants.py`・`check_validation_cases.py`・`check_screening.py`・`check_coding_book.py`）。定義を変えたなら `check_coding_book.py --mutate` も。
7. /cross-review（判断 56・61 のやり方）。判断を `decisions.md` に、タスクリストを `tasklist.md` に。TRACE は main に push、GSE はブランチに push（PR は研究者が確かめてから）。

## 3. 守ること

- 研究者の確かめの結果を、メインが代わりに「合っている」にしない。研究者の答えと定義が食い違うときは、どちらかに寄せず聞く。
- キーの確かめは登録の前の作業で、選別や符号化の判定ではない（登録の前に判定を始めない）。
- 抄録・全文・訳・AI の出力・検索の書き出しを repo に写さない（反例集は架空なので repo に置いてよい）。
- `git add -A` を使わない。Drive の共有の設定は変えない。
