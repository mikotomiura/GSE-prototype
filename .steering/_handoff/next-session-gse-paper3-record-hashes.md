# 引き継ぎ —— 論文 3 の記号化のキットに、元の記号列の記録ごとのハッシュを足す（Mac で条件とコード → HP Z2 で回す）

> 作成: 2026-11-11（Mac のセッション）。このメモを一次資料にしない。研究者の選択（2026-11-11）: 本文の草稿と並行して、HP Z2 でハッシュを作る。外枠の Open items の 3 つめ（`papers/per-person-learning/manuscript/outline.md`）と、キットの README の Checks の最後の段落（`papers/per-person-learning/kit/symbols/README.md`）が出発点。

## 0 入口の文（Mac の新しいセッションに打ち込む）

```
worktree /Users/johnd/GSE-prototype-paper3（枝 docs/gse-paper3-per-person-learning）で、.steering/_handoff/next-session-gse-paper3-record-hashes.md を読んで、記号化のキットの記録ごとのハッシュの条件とコードを書き、合成の門を通してから HP Z2 の引き継ぎを書いてください。決めることは AskUserQuestion で 1 問ずつ、推奨と理由を添えて日本語で聞いてください。
```

## 1 目的

キットの README はいま「著者の手元の確かめ（CoAuthor 1,157 セッション・775,907 行、CS1 2021 の押下 2 回以上の 177 課題・2,794,277 行で、x と y のビットまで元の実装と同じ）で、読者はまだ繰り返せない」と書いている。元の実装の記号列のハッシュを記録ごとに公開すれば、読者は公開の生データにキットを当てて同じハッシュになるかを自分で照らせる。ハッシュは記号と時刻と x・y のビットから作り、文字も打鍵の内容も含まない。

## 2 決めること（条件を書く前に研究者に問う）

1. 何をハッシュするか。推奨: 記録ごとに、元の実装の行を順に `t_ms,symbol,x.hex(),y.hex()` の 1 行ずつ（LF・UTF-8）に並べた文字列の SHA-256 と行の数。x・y を入れるのは README が「ビットまで同じ」と言っているため。`t_ms` が記録の先頭からの相対か絶対かは、キットの `symbolize(t0, presses)` の出力に合わせる（キットの出力そのものを読者が並べ直せる形にする）。
2. 記録の単位と識別子。CoAuthor はセッション（データセットのセッション ID）、CS1 は（学生・課題）で、作業の塊（30 分以上の隙間で割る）は塊の番号の順に連ねる。識別子は公開データセットの ID をそのまま使うか、ID の SHA-256 にするかを問う（CS1 は著者の承諾を得て使っているので、公開物に ID を並べてよいかを確かめる）。
3. 置き場所。推奨: `papers/per-person-learning/kit/symbols/conformance/data/record_hashes.json`（ハッシュと行の数だけ）と、読者が回す照合のスクリプト `conformance/check_records.py`（生データのパスを引数に取り、アダプタ → symbolize → 同じ並べ → 照合）。

## 3 段取り

1. Mac: 条件（`experiments/<日付>-symbol-record-hashes/conditions.md`・SEED は不要なら書かない）を先にコミット → コード（ハッシュを作る側は元の実装の出力を読む・照合の側はキットを当てる）と合成の門（合成の記録で、作る側と照合の側のハッシュが一致する・1 ビット変えた x で外れる・行を 1 つ落として外れる・CRLF で外れない形に固定する）→ /cross-review（Codex を加える・コードと条件だけを渡す）。
2. HP Z2 の引き継ぎ（`next-session-gse-paper3-record-hashes-run-on-hp-z2.md`）を、`next-session-gse-paper3-objective-and-pause-run-on-hp-z2.md` の形で書く。入力は元の実装の出力（`~/gse-public-data/landscape/coauthor_work`・`cs1/work2021_ref` など、どれが「元の実装」かは `experiments/20261107-unsmoothed-residual-check/` と `20261106-tau-mode-candidate/` の run.sh と notes で一次を確かめる）と生データ。HP Z2 は、作ったハッシュをキットの照合で 0 不一致になることまで確かめて push する。
3. Mac: 結果を照合し、README の Checks の段落を「読者が `check_records.py` で照らせる」に直し、外枠の Open items から外す。本文の再現の文もそれに合わせる。

## 4 守ること

- Mac では実データ・元の記号・pickle を開かない（コードと合成だけ）。HP Z2 でも値を読んで解釈しない。
- 外部の LLM（Codex を含む）に記号・ID・ハッシュの実物を送らない（コードと条件だけ）。
- `papers/` に GSE の名前・内部のパス・判断や条件の番号を書かない。
- Windows で書く JSON は改行を LF に固定する（`open(..., "w", newline="\n")`）。
- push と PR は研究者に確かめてから（PR は出さない方針・[skip ci]）。
