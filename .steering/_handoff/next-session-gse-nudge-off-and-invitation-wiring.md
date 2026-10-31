# 引き継ぎ — Nudge の既定の無効化と、招待の配線（ADR-040 Migration 1・2）

> 作成: 2026-10-31（少人数の研究設計の議論の後・研究者の依頼）。
> このメモを一次資料にしない。事実はコード・ADR・`decisions.md` で確かめ直す。
> 公開データの当てはめのトラック（`next-session-gse-public-data-fit.md`）とは独立で、別の worktree で並行してよい（判断 18）。

## 0 背景（一次の場所）

- 決定: `.steering/20261031-gse-small-n-research-design/decisions.md` 判断 10〜18（ブランチ `docs/gse-small-n-research-design`・worktree `/Users/johnd/GSE-prototype-smalln`・PR は未提出）。
- ADR: `docs/adr/ADR-040-nudge-not-in-core.md`（D1〜D4・Migration 1〜3）。
- 位置づけ: 打鍵の時刻と種類から作業上の認知状態を推定し（本文は保存しない）、詰まる前に介入を促して、身体回帰の機会（採点しない招待）を差し出す。「作業中の認知状態」とは書かない。

## 1 始め方

1. 返答・記録・AskUserQuestion は日本語で。記号を多用しない。決めることは推奨と理由を添えて AskUserQuestion で聞く（1 件 1 問・論点を添える）。
2. 新しい worktree を切る（`git fetch` の後、origin/main から）。上の docs ブランチがまだ main に入っていなければ、研究者に PR の扱いを先に聞く（ADR-040 を参照するため）。
3. 実装は `/start-task` から。2 つのタスクに分ける（下の 2・3）。完了時は `/cross-review` が必須。push までで止め、PR は研究者に確かめてから。
4. Skill: `architecture-rules`・`rust-standards`・`typescript-standards`・`intervention-design`・`data-privacy`・`reproducibility-discipline`（HMM の挙動を変えるなら `HMM_VERSION`）。

## 2 タスク A: Nudge の既定を無効にする（ADR-040 D1・Migration 1）

- 今の事実（2026-10-31 に一次で確認）: `src-tauri/src/lib.rs:122` `INTERVENTION_ENABLED` の初期値は true。`:3081` でセッションの宣言が上書き。`:4003` で O1 は false。`:1286` 無効時は判断を計算せず記録もしない。
- やること: 本体の既定で Nudge を出さない。判断のロジック（`analysis/intervention.rs`）は消さない（`gse-replay --intervention` の評価に使う・D2）。overlay のサイドカードの削除はしない（D2）。
- 確かめること: ゴールデンの byte-equal（`gse-replay` のスナップショット）・`meta` 行の非回帰・G1 / O1 / EH3 の挙動が変わらないこと・`capabilities.rs` の自己記述。
- 先に研究者に聞くこと: 「既定を無効」の実体（定数の初期値か、セッションの宣言の既定か）。

## 3 タスク B: 招待の契機と配線（ADR-040 D4・Migration 2）

- 今の事実: 招待は `analysis/invitation.rs`（EH3 モードでだけ動く）。契機は `p_stuck ≥ 0.60` が 30 秒続いた時・離席候補（180 秒）の中では出さない・1 区間 1 回・60 秒で閉じる・閉じた後 30 分・1 日の上限と時間帯は本人が選ぶ。
- やること:
  1. 契機に `friction_rising` を使えるようにする。値は未決（事前登録の前に研究者が決める・判断 13）なので、値を注入できる形にし、既定は今の挙動のままにする。
  2. 検証用に、頻度を合わせた無作為の時刻で出す条件を足す（判断 14）。
  3. 通常のモード・O1・EH3 のそれぞれで招待を出すか出さないかを決め、通常のモードの配線を足す（D1 の後に本体の介入が何も出ない状態を作らない）。決め方は研究者に聞く。
  4. 新しい契機を `gse-replay` で記録から再現できるようにする（時機のオフライン評価・D2 の補い）。
- 守ること: 招待は応答を入力に持たない（ADR-033）・本人の統制（ADR-035）・EH3 の事前登録が未凍結である点（`experiments/20261011-portrait-eh3/`）を壊さない。EH3 の挙動を変えるなら研究者に先に聞く。

## 4 研究者に聞くことの候補

- 既定の無効化の実体（タスク A）。
- 通常のモードで招待を出すか、出すなら上限と時間帯の既定（タスク B-3）。
- `friction_rising` の値を決める前の既定（今の挙動のままでよいか）。
