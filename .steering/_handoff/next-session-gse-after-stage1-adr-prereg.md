# 引き継ぎ —— 段 1 の ADR（ADR-043）・事前登録の草案・空回しの第 2.1 版の後

> 作成: 2026-11-03（`.steering/20261103-gse-stage1-adr-prereg/` の後）。
> このメモを一次資料にしない。数字と現状は、下に挙げた文書で確かめ直す。

## 1 このセッションで決まったこと（一次は `.steering/20261103-gse-stage1-adr-prereg/decisions.md` 判断 1〜8）

- ADR-043（Accepted）: 次の検証の段 1 の形（next-study-design 判断 2〜13）。ADR-031・ADR-032 の対象と Accepted の条件を、O1 から段 1 の同意文書の承認へ移した。ADR-031 M9 の束ねは段 1 では解く（段 1 の配布は ADR-032 の承認を待たない・計器は始める時点で固定）。
- `docs/preregistration-stage1.md`: 草案（凍結していない・値はすべて空欄）。項目は S1-A1〜S1-G2、出典の対応表つき。
- 空回しの第 2.1 版（`experiments/20261103-mhd-dryrun-v2/`）:
  - (a) 合成の日の模擬（打鍵は作らない・値は仮置き）: 傾きの区間の幅は見分ける力で大きく変わる（同じ日数で AUC 0.60 は 0.80 の 2.4〜2.8 倍）。日のブロックのパーセンタイル区間は評価が数十日以下で名目を下回り、正規近似と basic が近い。日の揺れがあると正しいモデルでも周辺の傾きは 1 より小さい。評価が 10 日を下回ると推定が不安定。
  - (b) CoAuthor の版の直し: 点推定は同じで、区間の端が少し動いただけ。
  - 第 2 版の P3（日のブロックのパーセンタイル区間を門にした）が赤で止まり、研究者の選択で第 2.1 版（門を回答 1 件ずつの区間へ移し、日のブロックの作り方は結果として比べる）にした。結果を見た後の変更として記録してある（判断 7）。
- 詳細は `experiments/20261103-mhd-dryrun-v2/notes.md` §2〜§6。

## 2 残っていること

- PR は出していない（push だけ・研究者に確かめてから）。docs と実験だけなので `[skip ci]` でマージできる。
- 2 巡目の /cross-review は回していない（今日の Codex の予算が足りない・判断 8）。
- 事前登録の値は、本人の段 1 の探索の後に埋める。凍結の前に attack-me を Codex つきでかける（判断 5）。
- notes §4 の候補（区間の作り方とブロックの長さは段 1 に近い日の揺れで 400 回以上回して決める・較正の許容の範囲は母集団の値と並べて決める・評価の日数の下限）は事前登録で決める。ρ = 0.6 でのブロックの長さの比べは未実施。

## 3 次の候補（研究者が選ぶ）

1. O1 が終わったら、見ていない期間で C1・C2・C6 と H4a・H5 を確かめる（`.steering/_handoff/next-session-gse-next-study-design.md` §1）。
2. 取っておいた公開データの書き手で R1〜R5 を確かめる。
3. 段 1 の同意文書を書く（ADR-043 Migration 3・`next-session-esm-consent-next-study.md` §2 の 2〜6・手跡の後期の同意項目・ADR-032 の計器を入れるか）。
4. ADR-031 M5（プローブの発火の配線・6 択 UI）の実装（段 1 の配布の前に要る）。
5. 保留 1（動機づけと同期・共生の感覚の問い方・尺度は文献で接地してから）。
6. 取得した公開データ全部の整理（研究者が 2026-11-03 に追加）。目的は、何をどこに持っていて、何に使い、何をまだ開けていないかを 1 か所で引けるようにすること。
   - 置き場（2026-11-03 に `ls` と `du` だけで見た・中身は開いていない）:
     - `~/gse-public-data/`: `coauthor/raw`（48 MB）・`dux/raw`（304 MB）・`swell/raw`（378 MB）・`klicke/`（`raw`・`bin`・`work.tar.gz`・883 MB）・`landscape/`（`coauthor_work`・`holdout.json`・`klicke_side.json`・108 MB）・`extend/`（`dux_work`・`dux_work_tabnav`・`swell_work`・`holdout.json`・28 MB）。
     - 実験ごとの `raw/`（git に入らない）: `experiments/20261012-public-keystroke-matching/`（KLiCKe ほか・版と SHA-256 は `data.md`・`config.json`）・`experiments/20261009-length-sequence-uniqueness/`（青空文庫）。他の実験の `data.md` も見る。
     - 問い合わせ中・返事待ち: 打鍵の外の信号のデータ 6 件（`.steering/_handoff/next-session-public-data-replies.md`）・CS1（`.steering/_handoff/next-session-cs1-reply.md`）・Clarkson II（`.steering/20261102-gse-synthesis-redesign/clarkson-ii.md`）。
   - 書くもの（案）: データごとに、出典の番号（references.md）・入手先と利用条件・取得日と版と SHA-256・置き場・中間（work）の作り方と作った実験・使った実験と問い・取っておいた部分（holdout）の有無と開ける条件・消す条件（問い合わせの返事しだいのものを含む）。置き場は docs か `experiments/README.md` の近くにするかを研究者と決める。
   - 注意: `holdout.json` は 2 つとも開かない（数えるのはファイルの有無だけ）。記録の中身を外部の LLM（Codex を含む）に送らない。整理のために新しく取得しない。重複（KLiCKe が `~/gse-public-data/klicke` と照合の実験の `raw/` の 2 か所にある可能性）は SHA-256 で確かめ、消すかは研究者に聞く。

## 4 注意

- Codex に O1 の記録・中間・結果の本文を送らない。今日の Codex は 1 回で 80,298 トークンを使った（1,800 行の差分）。
- 空回しの結果を詰まりの推定や MhD が学習できた根拠にしない。(a) の値は仮置きで段 1 の見込みではない。
- 「作業上の認知状態」と書く。停滞の始まりで詰まりを検出したとは書かない。
- `~/gse-public-data/landscape/holdout.json` は、候補 2 を始めるまで開かない。
