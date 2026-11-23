# GSE の合流 —— 招待の契機・循環・書き場所・主要アウトカムを研究者が決める

## 背景

T1（契機を差し替えられる口）・T2（KLiCKe）・T3（O1 のフォーカス）・俯瞰の材料がそろった。ADR-040 D4 の契機の方向と ADR-024 の主要アウトカムを、材料に照らして研究者が決める（`.steering/_handoff/next-session-gse-merge.md`）。

## ゴール

three-parallel-tracks §4 の 4 問に研究者が答え、決定が ADR と steering に記録されている。

## スコープ

### 含むもの
- 4 問を AskUserQuestion で聞く（推奨と材料の出典つき）
- 決定を `decisions.md` と新しい ADR に書く
- 後に分ける別タスクの引き継ぎ

### 含まないもの
- コードの変更（T1 の口に中身を入れる実装）・O1 の数え直し・`research-positioning.md` の本文の改訂・事前登録

## 受け入れ条件

- [x] 4 問の答えが decisions.md にある
- [x] ADR の本文を書き換えていない（新しい ADR と README の注記だけ）
- [x] 別タスクの引き継ぎがある
