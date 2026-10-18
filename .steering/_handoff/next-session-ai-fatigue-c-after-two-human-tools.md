# 引き継ぎ: C（TRACE）—— 人 2 人の形の道具ができた後・共著者の返事を待つ間と、返事の後

作成 2026-10-19（Mac）。前の `next-session-ai-fatigue-c-three-screeners.md` を置き換える。
- 返答・記録・AskUserQuestion の引数は日本語で書く。記号を多用しない。
- 決めてほしいことは AskUserQuestion で、推奨と理由を添えて聞く。
- 共著者に見せる文には、ルールの明示と具体的な日付・期限を書かない。
- TRACE の符号化は共著者が全部を行う（判断 45・55）。「2 割」の前提で問いを作らない。段 1 の選別の 2 割は別で、今も生きている。

## 始め方

研究の物は `~/TRACE`（https://github.com/mikotomiura/TRACE・非公開）。検討の記録は worktree
`/Users/johnd/GSE-prototype-af-c`（ブランチ `docs/ai-fatigue-c-outline`）の `.steering/20261017-ai-fatigue-c-outline/`。

```
.steering/_handoff/next-session-ai-fatigue-c-after-two-human-tools.md を読んで、§2 を進めて。
```

## 1. ここまで（判断 55〜57）

- 判断 55: 判断 44 の未決を閉じた（80% の単位と全部の締めは問わない・保留の記録は共著者も判定し直す・段 1 の残りは段 2・3 と並べて渡す）。
- 道具（TRACE の a9654d4・267c866・dca4659）: `c_screening.py mode --set two-human | ai-screener`。人 2 人の形は、共著者の冊の取り込み（第一著者のコミットを記録して、後の書き換えを `export-final` と `release` で止める）・段 1 の 2 割の一致と 80%・網（AI が回すべきと答えた記録と、AI の出力が 2 回とも落ちた束の除外）・段 2・3 の 2 人の合意・保留の判定し直しの回の窓・全記録の最終の値（`screening-final.csv`・見落としの推定が読む）。変異 20 個がすべて赤。
- 判断 56: /cross-review（Claude と Codex）の指摘に対応した。
- 判断 57: 相談文と案内から符号化の「2 割」の逃げ道を外し、Drive の案内と段 1 の冊（113 件・`--hold`）を置き換えた。
- 手順は `registration-day.md` の「人 2 人の形」の節。

## 2. 次にやること

共著者の返事の前（研究者）:
1. Drive の案内（docx）と段 1 の冊を開いて見る。相談文（`coauthor-consult.docx`・手元）を共著者に送る。
2. Drive の `fulltext` を共著者に閲覧のみで共有する（研究者が行う。メインは設定を変えない）。

共著者の返事の後（メイン）:
1. 登録の下書きを返事の形に書き換える。引き受けたなら人 2 人の形（GSRR-2・9・33・34・36〜41・44・47・49・62・65・表 1・2・添付 6）。GSRR-41 の公開物に author2 の列・`author2-workbooks.csv`・`screening-final.csv` を足し、片方の人だけが中心を付けた記録は合意で決めて件数を報告すると書く（判断 56）。AI の出力が 2 回落ちた束の除外も網に入れると書く（判断 57）。外枠の分析 5・12 月 31 日の箇所も。GSRR-9 の終わりの日を現実の日に。
2. 引き受けなければ、草稿・README・gif・案内を今の登録の形（第一著者と独立の AI）に戻す。道具は `mode --set ai-screener` で、そのまま使える。
3. 書き換えの後に /cross-review。

## 3. 守ること

- 登録の前に判定を始めない（第一著者・AI・共著者のどれも）。
- 抄録・全文・訳・AI の出力・検索の書き出しを repo（GSE-prototype も TRACE も）に写さない。確かめの検索をやり直さない。
- `git add -A` を使わない。PR は研究者が確かめてから（push で止める）。
- Drive の共有の設定と、GitHub の公開設定は、研究者の確認なしに変えない。Drive の文書を上書きする前に、研究者の手直しが入っていないか比べる。
