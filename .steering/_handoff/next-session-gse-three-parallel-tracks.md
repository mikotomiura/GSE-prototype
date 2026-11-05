# 引き継ぎ — 3 本を並行して進める（実装・項目 2・フォーカスの確かめ）

> 作成: 2026-11-01（研究者の依頼）。3 つのセッションを同時に開いて進めるときの、まとめ役のメモ。
> 各トラックの中身は個別の引き継ぎにある。このメモは「ぶつからないための約束」と「入口の文」と「合流の仕方」だけを持つ。
> このメモを一次資料にしない。事実は一次で確かめ直す。

## 0 3 本と、それぞれの入口

| | トラック | 個別の引き継ぎ | worktree（例） | ブランチ（例） | モデル |
|---|---|---|---|---|---|
| T1 | 実装: Nudge の既定の無効化と招待の配線（ADR-040 Migration 1・2） | `.steering/_handoff/next-session-gse-nudge-off-and-invitation-wiring.md` | `/Users/johnd/GSE-prototype-t1-invitation` | `refactor/nudge-off-invitation-wiring`（下の §2 の 1 を読む） | 設計は Opus・実装は Sonnet（CLAUDE.md のモデル選択） |
| T2 | 公開データの当てはめ 項目 2（KLiCKe） | `.steering/_handoff/next-session-gse-public-data-fit-item2.md` | `/Users/johnd/GSE-prototype-t2-klicke` | `docs/gse-public-data-fit-item2` | Opus |
| T3 | 止まりの最中にフォーカスを離れることは受領に先立つか | `.steering/_handoff/next-session-gse-focus-leave-before-receipt.md` | `/Users/johnd/GSE-prototype-t3-focus` | `docs/gse-focus-leave-before-receipt` | Opus |

3 本の関係（`.steering/20261101-gse-pre-stall-signal/decisions.md` 判断 4）:
- T1 は契機を差し替えられる形で作り、既定は今の挙動（`p_stuck ≥ 0.60` が 30 秒）のまま。T2・T3 の結果を待たずに進められる。
- T2 は「止まりの初期」の値の母集団の分布と、KLiCKe での案 A の追試を出す。
- T3 は、フォーカスの遷移が契機の候補になるか、契機と副のアウトカム（ウィンドウを離れずに再開）の循環をどう解くかの材料を出す。
- 契機の中身と循環の扱いは、3 本が終わった後の合流のセッション（§4）で研究者が決める。T1 の中で決めない。

## 1 各セッションの入口の文（新しいセッションに貼る）

- T1: 「`.steering/_handoff/next-session-gse-three-parallel-tracks.md` の T1 を実施。個別の引き継ぎは `next-session-gse-nudge-off-and-invitation-wiring.md`。§2 の約束を守る」
- T2: 「`.steering/_handoff/next-session-gse-three-parallel-tracks.md` の T2 を実施。個別の引き継ぎは `next-session-gse-public-data-fit-item2.md`。§2 の約束を守る」
- T3: 「`.steering/_handoff/next-session-gse-three-parallel-tracks.md` の T3 を実施。個別の引き継ぎは `next-session-gse-focus-leave-before-receipt.md`。§2 の約束を守る」

## 2 ぶつからないための約束

1. **worktree を分ける**（memory `parallel-sessions-share-checkout`）: 3 本とも、`git fetch` の後に origin/main から自分の worktree を切る。同じチェックアウトを共有しない。コミットの前に `git branch --show-current` を確かめる。
2. **CI を G-GEAR と重ねない**: `.github/workflows/ci.yml` は main と `feature/*` への push、main への PR で走り、self-hosted のランナー（`gse-mac`・Windows 側）に載る。
   - T1 は `feature/` で始まらない名前のブランチにするか、push するコミットに `[skip ci]` を付ける（`git-workflow` の型名と食い違う場合は研究者に聞く）。コードの変更なので main へは CI を通してから入れる。PR を出す時期（G-GEAR が空いているか）は研究者に確かめる（memory `feedback-push-only-no-pr-during-runs`）。
   - T2・T3 は docs と experiments だけなので、研究者の指示どおり PR なし・`[skip ci]` で main へ入れてよい（2026-11-01 の項目 1 と同じ手順: 一時の worktree で origin/main に `--no-ff` でマージし、コードと CI の設定が差分に無いことを確かめて push）。
3. **main へのマージは 1 本ずつ**: マージの直前に `git fetch` し、origin/main を自分のブランチに取り込んでから入れる。押し返されたら、`origin/main..HEAD` と `HEAD..origin/main` の両方を見る（memory `git-write-ops-need-user`）。
4. **共有のファイル**:
   - `.steering/_handoff/README.md`: 自分の行だけを書き換える。マージで衝突したら両方の行を残す。
   - `docs/references.md` の `[Vn]`: 番号は append-only。登録はマージの直前に、最新の origin/main の末尾の番号から採る。衝突したら自分の新しい行の番号を振り直す（既存の番号は変えない）。
   - `.codex/budget.json`（Codex の予算の台帳）: worktree ごとに別の台帳なので、3 本は互いの消費を知らない。/cross-review の前に、他の 2 つの worktree の `today.tokens_used` を足して 1 日の上限（300,000）に収まるかを見る。収まらなければ研究者に聞く（memory `codex-budget-raise-blocked`）。マージで衝突したら和を採る（台帳の先例）。`git checkout -- .codex/budget.json` はしない（記帳が消える）。
5. **ディスク**: 2026-11-01 の空きは約 6.5 GB。CoAuthor の 1 回で 2 GB 前後を使い、一杯になって計算が止まった。重い段（T1 の cargo のビルド・T2 の KLiCKe の展開と replay）の前に `df -h ~` を見て、3 GB を切っていたら始めない。中間は読む項目だけを残す（`experiments/20261031-coauthor-pre-request-signal/scripts/slim.py` の形）。他のトラックの中間（`~/gse-public-data/` の下）を消さない。
6. **データの扱い**: 打鍵の本文・NDJSON の生ログ・被験者のログは外部の LLM（Codex を含む）に送らない（`data-privacy`）。repo に入れるのは集計だけ。書き手・参加者の ID を結果に出さない。
7. **G-GEAR**: 長い計算を G-GEAR に回すかは各トラックで先に考える（memory `feedback-ggear-tasks-stay-on-ggear`）。G-GEAR で重い計算中は PR を出さない。

## 3 各トラックの終わり方

- 完了時は code-reviewer と /cross-review を並列で回し、指摘を反映する（CLAUDE.md）。
- 結果と、研究者が決める材料を自分の `.steering/<日付>-<タスク>/decisions.md` に書き、`_handoff/README.md` の自分の行を「完了」にする。
- T2・T3 は結果を `experiments/<日付>-<名前>/notes.md` に、言える範囲を限って書く。

## 4 合流（3 本が終わった後の別のセッション）

- 入口: T1・T2・T3 の `decisions.md` と notes を読み、研究者に AskUserQuestion で次を聞く。
  1. 招待の契機の中身（止まりの初期の値・フォーカスの遷移を使うか・friction_rising の上がりを残すか）。
  2. 契機と副のアウトカムの循環をどう解くか（契機を替えるか、副のアウトカムを替えるか）。
  3. それを ADR-040 の補訂・新しい ADR・事前登録のどれに書くか（ADR の本文は書き換えない規約）。
  4. 主要アウトカム `receipt_free_resumption`（ADR-024）を残すか（研究者の回答・2026-11-01）。外からの貼り付けを受領と数える定義は「AI・検索に頼る前」の時代のもので、今の位置づけ（ふつうのデスクワークでの作業上の認知状態・詰まる前の身体回帰の招待・`research-positioning.md:49`）に合うかを見直す。T3 の測り直しはその後（アウトカムを替えるなら新しいアウトカムで O1 を数え直す。フォーカスの遷移を曝露とアウトカムの両方に使う循環に注意）。
- 結果の読み方（研究者の指摘・2026-11-01）: 項目 1（CoAuthor で AI の提案を求める手前）は的が AI の要求で、古い形の問い。今の位置づけの「詰まる前」の根拠にも反証にも数えない。今の位置づけに関わるのは案 A（停滞の始まりの手前・AI に依らない）と T2 の KLiCKe での追試（AI なしの作文）。AI 疲労は GSE とは別の研究（AF の系統）で、GSE のアウトカムに持ち込まない。
- T1 で作った差し替えの口に、決まった中身を入れるのは合流の後の別タスク。
