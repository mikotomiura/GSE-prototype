# 引き継ぎ — 今の位置づけを 1 枚にまとめ直し、公開データを記述だけで俯瞰する（合流の前）

> 作成: 2026-11-01（研究者の依頼）。T2（KLiCKe）を終えた後の相談で決めた。
> このメモを一次資料にしない。事実は一次で確かめ直す。

## 0 なぜやるか

- 項目 1（CoAuthor で AI の提案を求める手前）は、AI の要求を的にした古い問いで立てていた（`next-session-gse-three-parallel-tracks.md` §4 の「結果の読み方」）。古い基準で見る失敗を繰り返さないため、今の位置づけを先に固めてから公開データを見る。
- 合流（同 §4）で決めることは、招待の契機の中身と、主要アウトカム `receipt_free_resumption` を残すかどうか。この俯瞰はその 2 つの材料になる。

## 1 研究者が決めたこと（2026-11-01・AskUserQuestion）

1. 順番は、位置づけ → 俯瞰 → 合流。
2. 俯瞰に使うデータは KLiCKe・CoAuthor・CS1 の 3 つ。
3. T1（`next-session-gse-nudge-off-and-invitation-wiring.md`・差し替えの口の実装）は、別の worktree で並行して進める。契機の中身を決めずに作れる設計なので、俯瞰を待たない。

## 2 段 1: 今の位置づけを 1 枚にまとめ直す

- 一次の資料: `docs/research-positioning.md` §1 の 2026-10-31 改訂、ADR-040、`.steering/20261031-gse-small-n-research-design/decisions.md` の判断 10〜18、three-parallel-tracks §4。
- 研究者の指示で、`research-positioning.md` の後から変わったことがある。
  - 主要アウトカムは、合流で見直す（同 §4 の 4。`research-positioning.md` は「据え置く」のまま）。
  - GSE の目標は AI を的にしない。ふつうのデスクワークでの作業上の認知状態を見る。AI 疲労は別の研究（AF の系統）。
  - 「作業中の」ではなく「作業上の認知状態」と書く。
- 作るもの
  - 位置づけの要約。何を推定し、いつ何を差し出し、何を主張しないか。
  - GSE が見られる信号の一覧。打鍵の 5 特徴量、休止、停滞の始まり（`stall_onset`）、`friction_rising`、フォーカスの遷移、ポインタ、IME、貼り付けの文字数。それぞれについて、どの公開データで見られ、どれが O1 でしか見られないかを書く。
  - 俯瞰で見る問いの一覧。どの問いが合流の 1〜4 のどれの材料になるかを添える。
- 置き場は新しい `.steering/<日付>-gse-public-data-landscape/`。要約が `research-positioning.md` と食い違うところは、要約に書くだけにする。positioning の本文の改訂は合流の後の別タスクで行い、勝手に直さない。

## 3 段 2: 公開データを記述だけで俯瞰する

- 検定はしない。分布と傾向だけを見る。見る問いと集計の仕方は、計算の前に conditions.md に置いてコミットする（項目 2 の K1〜K7 と同じやり方）。
- 後で確かめに使えるよう、各データの一部（例えば書き手の 3 割）を種で固定して取っておき、見ない。
- データ
  - KLiCKe: 中間 `~/gse-public-data/klicke/work.tar.gz` が使える（`experiments/20261101-klicke-early-stall-trigger/`。θ と onset は replay と全件一致を確かめ済み）。
  - CoAuthor: `~/gse-public-data/coauthor/`（48 MB）。項目 1・案 A で使った。AI の提案を求める出来事の前後を除き、ふつうの書く区間として見直す。
  - CS1: AI が出る前のプログラミング（510 万打鍵・[V317] か [V340] の本文に公開があると書いてある）。まだ取っていない。利用条件・出来事の種類・大きさを先に確かめる。人口統計や ID を尋ねる調査票のファイルは取らない。
- 限界: どれも 1 つの文書の中の打鍵で、フォーカスの遷移・アプリをまたぐ作業・受領は無い。俯瞰で言えるのは打鍵と休止の層まで。デスクワーク全体は研究者本人の O1（T3 と同じ）でしか見られない。

## 4 守ること（three-parallel-tracks §2 を引き継ぐ）

- worktree を分ける。コミットの前に `git branch --show-current` を確かめる。T1 の worktree とファイルが重ならないようにする。
- docs と experiments だけなら、PR なし・`[skip ci]` の `--no-ff` マージで main へ入れてよい。差分にコードと CI の設定が無いことを確かめる。直前に fetch する。
- 打鍵の本文・NDJSON の生ログ・被験者のログは外部の LLM（Codex を含む）に送らない。repo に入れるのは集計だけ。書き手・参加者の ID を結果に出さない。
- KLiCKe の人口統計のファイルは取らない。Kaggle [V265] は KLiCKe 由来なので使わない。
- `docs/references.md` の [Vn] は append-only。
- ディスク: 2026-11-01 時点の空きは約 3.9 GB。3 GB を切ったら重い段を始めない。CS1 を取る前に大きさを確かめる。他のトラックの中間を消さない。
- 照合論文のトラック（`/Users/johnd/GSE-wt-matching-manuscript`）の成果物は読むだけ。

## 5 終わった後

- 結果を持って合流に入る（three-parallel-tracks §4）。合流の問いは AskUserQuestion で、推奨と理由を添えて日本語で聞く。
