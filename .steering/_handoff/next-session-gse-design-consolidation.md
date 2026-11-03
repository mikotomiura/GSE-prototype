# 引き継ぎ —— GSE の全体の設計を整理し、段 1 の配布までの道筋を引く（プローブの配線を含む）

> 作成: 2026-11-03（`.steering/20261103-gse-scale-up-ideal/` の後・研究者の依頼「4. も含めて、もう少し全体の設計などの整理などを行いたい」）。
> このメモを一次資料にしない。事実は ADR・コード・decisions.md で確かめ直す。

## 0 入口の文（新しいセッションに貼る）

「`.steering/_handoff/next-session-gse-design-consolidation.md` を読み、GSE の全体の設計を整理する。`/start-task` から。議論が主で、整理の結果を SSOT の文書へ落とす。プローブの配線（ADR-031 M5）は、その中で位置と設計を決める」

## 1 なぜ整理が要るか（確かめた事実）

2026-10-31 から 11-03 に、決定が短い間に積み重なった。ADR-040〜043 は Accepted になったが、上流の文書が追いついていない。

- `docs/research-positioning.md` §1 の 2026-10-31 改訂ブロックは、まだ「1 段目 = 統制課題で招待を 3 腕に割り付ける」と書く。ADR-043 は、段 1 = 招待を出さずに C4 を取る、段 2 = 招待の 3 腕に組み替えた。改訂は ADR-041 Migration 4・ADR-043 Migration 5 の別タスクで、まだやっていない。
- `docs/wbs-verification-halfyear.md` の B1〜B4 も同じく古い。
- ADR-040 のコードの変更（Nudge の既定の無効化・招待を通常のモードで出す配線・無作為の時刻の条件）は main に入っていない（ADR-040 Migration 1・2）。今は通常のモードで Nudge が出て、招待は EH3 モードでだけ動く。
- ADR-031 M5（プローブの発火の配線・6 択 UI）は未実装。段 1 は、本人の探索で事前登録の値を決めてから凍結する。その探索にもプローブが要るので、段 1 への道でいちばん詰まっている（ADR-043 Migration 4）。
- Proposed のまま残る ADR が多い。ADR-030・031・032・033・035・036・038・039 で、いくつかは Accepted の条件が同意文書に結び付いている。ADR-031・032 は ADR-043 が対象を O1 から段 1 へ読み替えた。
- 2026-11-03 の訂正: Physical Anchor の実体は、身体回帰の招待（PC 側の図像・EH3 で実装済み）。散歩の促進とその計測は行わない。身体回帰の後は、離席候補明けの作業上の状態で見る。主は打鍵の再開と受領、副はフォーカスの遷移で、ポインタも使う（ADR-024・ADR-023 D4・ADR-016・ADR-041）。共通の文書はブランチ `docs/gse-scale-up-ideal` で直した（PR は研究者の判断待ち）。

## 2 整理で作るもの（候補・研究者が選ぶ）

1. 全体の設計の地図（1 枚）。層ごとに、決まったこと・実装の状態・未決を並べ、どの ADR が根拠かを書く。
   - 層は、推定（L0〜L1）・契機（`friction_rising`）・介入（招待）・アウトカム（主・副）・ラベル（C4）・検証の段（段 1・段 2・O1 の見ていない期間）。
   - 置き場所の候補は、`docs/architecture/` の新しい文書か、research-positioning §1 の改訂ブロック。
2. research-positioning §1 と WBS の改訂。段 1・段 2 の組み替えと、人数を増やせた場合の理想（2026-11-03 追記）を入れる。
3. 段 1 の配布までの依存の道筋。
   - 要るもの: プローブの配線（M5）・ADR-040 のコード・同意文書（ADR-043 Migration 3）・倫理審査（PM の大学・規程は未確認）・本人の探索・事前登録の凍結と attack-me（Codex つき）。
   - どれが何を待つか、Mac と G-GEAR のどちらでやるかを書く。
4. プローブの配線（M5）の設計。
   - 無作為の枠と層化の発火、6 択 UI、抑制・未回答・遅れの記録（ADR-043 D5・D6）。
   - ADR-040 の配線と同じ所（`intervention.rs`・`invitation.rs`・`probe_scheduler.rs`）を触るので、順番か同時かを決める。
   - 実装は、設計が決まった後に別の worktree で行う。整理と同じセッションで始めない。

## 3 読むもの

- ADR: 040・041・042・043（Accepted）、031・032（Proposed・ADR-043 が読み替え）、024・023・018・016。
- `docs/preregistration-stage1.md`（草案）・`.steering/20261103-gse-stage1-adr-prereg/decisions.md`。
- `.steering/20261031-gse-small-n-research-design/decisions.md`・`.steering/20261102-gse-synthesis-redesign/synthesis.md`。
- 引き継ぎ: `next-session-gse-after-stage1-adr-prereg.md`（候補 2〜5）・`next-session-gse-nudge-off-and-invitation-wiring.md`（ADR-040 のコード）・`next-session-esm-consent-next-study.md`（同意）・`next-session-gse-small-n-design-revision.md`（positioning・WBS の改訂案）。
  - どれが済んだかは、使用済みの印・worktree・main の log で確かめてから勧める。

## 4 並行して待っているもの

- O1 の見ていない期間の確かめ: O1 の終了後に `next-session-gse-unseen-period-run.md` で run.sh を 1 回だけ回す。それまで 11-01 08:30 以降の O1 の記録を開かない。
- 取っておいた公開データの書き手（`~/gse-public-data/landscape/holdout.json`）は、R1〜R5 の確かめを始めるまで開かない。
- 公開データの問い合わせ 6 件の返事待ち。

## 5 注意

- 返答・問いは日本語で。決めることは AskUserQuestion で 1 問ずつ、推奨と理由を添えて聞く。
- 「作業上の認知状態」と書く。停滞の始まりで詰まりを検出したとは書かない。
- Physical Anchor を「未実装」と書かない。散歩の計測は行わない。離席候補明けの観測は、打鍵だけに絞って書かない。
- O1 が動いている間は、開発版のアプリを AX で操作しない。同じ名前のプロセスを取り違える。
- Codex に O1 の記録・中間・結果の本文を送らない。今日の Codex の予算はほぼ尽きている（11-03 で 574,580 / 600,000）。
