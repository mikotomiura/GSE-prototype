# GSE: 今の位置づけを 1 枚にまとめ直し、公開データを記述だけで俯瞰する

## 背景

- 引き継ぎ: `.steering/_handoff/next-session-gse-public-data-landscape.md`（2026-11-01・研究者の依頼）。
- 項目 1（CoAuthor で AI の提案を求める手前）は AI の要求を的にした古い問いだった。古い基準で見る失敗を繰り返さないため、今の位置づけを先に固めてから公開データを見る。
- 合流（`next-session-gse-three-parallel-tracks.md` §4）で研究者が決める 4 つ（招待の契機の中身・契機と副のアウトカムの循環・どこに書くか・主要アウトカムを残すか）の材料を作る。

## ゴール

1. 段 1: 位置づけの要約・GSE が見られる信号の一覧（どの公開データで見られ、どれが O1 でしか見られないか）・俯瞰で見る問いの一覧（合流のどの問いの材料か）を `positioning.md` に置く。
2. 段 2: 公開データ（KLiCKe・CoAuthor）を、計算の前にコミットした条件（`experiments/20261102-public-data-landscape/conditions.md`）で記述だけ集計し、`notes.md` に言える範囲を限って書く。
3. CS1 は研究者の決定（2026-11-02）で、著者へ連絡してから使う。連絡の文案を用意し、今回の俯瞰からは外す。

## スコープ

### 含むもの
- 位置づけの要約（`research-positioning.md` と食い違うところは要約に書くだけ）
- KLiCKe・CoAuthor の記述の集計（検定なし）。各データの書き手の 3 割を種で固定して取っておき、見ない
- CS1 の著者への連絡の文案（送るのは研究者）

### 含まないもの
- `research-positioning.md` 本文の改訂（合流の後の別タスク）
- 招待の契機の値の決定（合流で研究者が決める）
- T1 の残り（引き継ぎ §6。実機の確かめは研究者が押す・push は T1 の worktree で行う）
- CS1 のデータの取得

## 受け入れ条件

- [ ] `positioning.md` に要約・信号の一覧・問いの一覧がある
- [ ] `conditions.md` を計算の前にコミットした
- [ ] 取っておく 3 割の書き手を、値を見る前に種で決め、集計に入れていない
- [ ] 集計だけを repo に入れ、書き手の ID・本文を出していない。記録を外部の LLM に送っていない
- [ ] `notes.md` に言える範囲と言えない範囲を書いた
- [ ] code-reviewer と /cross-review を回し、指摘を反映した
- [ ] `_handoff/README.md` の行を更新した

## 関連ドキュメント

- `docs/research-positioning.md` §1（2026-10-31 改訂）・`docs/adr/ADR-040-nudge-not-in-core.md`・ADR-021 D4・ADR-024・ADR-030
- `.steering/20261031-gse-small-n-research-design/decisions.md` 判断 10〜18
- `experiments/20261101-klicke-early-stall-trigger/`（T2）・`experiments/20261101-coauthor-pre-stall-signal/`（案 A）・`experiments/20261101-focus-leave-before-receipt/`（T3）
