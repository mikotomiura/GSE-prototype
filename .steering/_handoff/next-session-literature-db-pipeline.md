# 次のセッション: 文献 DB を 1 つの仕組みにする（スプレッドシートを中心に・/literature-review に組み込む）

> 書いた日: 2026-10-18（Mac・研究者の依頼）
> 機械: Mac（Google Drive for desktop と Chrome を使う）
> 枝: `chore/literature-db`（worktree `/Users/johnd/GSE-prototype-literature-db`・origin/main から切った）
> 返答・記録・AskUserQuestion は日本語で。記号（★・⚠️）を多用しない。決めることは推奨と理由を添えて AskUserQuestion で聞く。

## 0. 新しいセッションで最初に打ち込む文

worktree `/Users/johnd/GSE-prototype-literature-db` で Claude Code を開いてから:

```
.steering/_handoff/next-session-literature-db-pipeline.md を読んで、§2 から始めて。
```

## 1. 先に読むもの

- `.steering/20261018-literature-db/requirement.md`・`decisions.md`（判断 1〜4: 正本は references.md・メモはシート／/literature-review に組み込む／この枝／要約は repo）・`tasklist.md`
- `scripts/refdb/draft/STEPS.md`（2026-10-18 に作った手順の全部。下書きのスクリプトは同じフォルダ。パスが当時の一時ディレクトリのままで、そのままでは動かない）
- `docs/literature/refdb/summaries.json`（675 件の要約・特徴）
- 手元のキャッシュ `~/.cache/gse-refdb/`（`abstracts.json` 579 件・`csl_raw.json` 780 件。repo に入れない）
- memory `abstract-sources-and-drive-ids`（大きな表をシートにする経路）

## 2. やること

1. `design.md` を書く。コマンドの形（例: `python3 scripts/refdb/build.py --branches <設定> --out <出力先>`）、読む枝の設定、キャッシュの場所、出力（CSV・ページの HTML・CSL-JSON・.bib 2 本）、読んだ・メモの結び直し（シートから読んだ JSON を渡す）を決める。決めることは研究者に聞く。
2. 下書きの 1〜8 を 1 本にまとめ、テストを書く（7 列の行・配列の題・null の年・読んだ/メモ・件数）。
3. 要約を書く依頼文を `scripts/refdb/summary_prompt.md` に起こし、要約が無い文献の一覧を出す。
4. シートとページへ反映する手順を `scripts/refdb/README.md` に書く。
5. `/literature-review` に DB を作り直す段を足し、`empirical-prompt-tuning` で確かめる。
6. 実データで作り直し、2026-10-18 の件数（906 件・要約 675 件・カードでの記述 576 件）と一致することを確かめ、シートとページを更新する。
7. `/cross-review`・push（PR は研究者に確かめてから）。

## 3. 外にあるもの（2026-10-18 時点）

- スプレッドシート「GSE 文献DB」: https://docs.google.com/spreadsheets/d/1v7frJm2a6BkXzepEpglB62AT_2c3t0NzJ2mNA8UfRFw/edit （検索・集計・一覧・凡例。フォルダ GSE）
- 検索のページ: https://claude.ai/artifact/Js8ZBgzkWAZBHdgrzqjwSA （同じ URL に出し直す）
- 書誌のファイル: フォルダ GSE の `GSE文献DB_2026-10-18_biblatex.bib`・`_bibtex.bib`・`.csl.json`

## 4. 守ること

- 書誌の正本は `docs/references.md`（判断 1）。シートから references.md へ書き戻さない。
- 抄録は repo に入れない。要約は自分の言葉で、連続 15 語以上の写しを作らない。数値は材料にあるものだけ。
- 連絡先のメールアドレスを外部の API に送らない。
- 読んだ・メモを消さない（作り直しの前に必ず読む）。
- 番号の衝突（48 個）は解消しない（別タスク）。
