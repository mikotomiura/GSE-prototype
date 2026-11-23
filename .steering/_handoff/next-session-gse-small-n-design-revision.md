# 引き継ぎ — 少ない人数の研究設計を SSOT の改訂案に落とす

> 作成: 2026-10-31（`.steering/20261031-gse-small-n-research-design/` の後）。このメモを一次資料にしない。

## 決まっていること（decisions.md 判断 1〜6）

- 倫理審査: 未踏 IT に採択されたら担当 PM の所属大学で出してもらう道を模索（未確認: PM の大学の規程）。
- 読み手: HCI の設計者・研究者。採択後の人数: 研究者本人を含め 3〜5 名。
- 研究の形から見直す。軸は計測と介入効果。主張の上限は個人ごとの効果と事例をまたいだ再現。
- 設計: 段で重ねる。(1) 計測は自然作業の長い記録（時間順に調整区間と評価区間を分ける）。(2) 介入効果は統制課題で {推定器 / 頻度を合わせた無作為 / なし} を個人ごとに無作為化。(3) 効果が見えた人でだけ自然作業の多重ベースラインへ。
- 文献: `docs/literature/20261031-small-n-within-person-design.md`（[V299]–[V311]）。

## 次にやること（研究者と順番を決める）

1. `docs/research-positioning.md` §1（headline）・§6（シナリオ）・§9（スコープ）の改訂案。反映は研究者の承認の後。headline の「Stuck 検出の妥当性 × 介入タイミング」をどう言い換えるかが中心。
2. `docs/wbs-verification-halfyear.md` の改訂案（Y の AB/BA・X2 の MRT を段の設計に置き換える）。凍結済みの `docs/preregistration-v0.3.md` は書き換えない。
3. 統制課題の設計: 答えの入手経路をアプリ内に限る方法、詰まりが起きやすい課題、1 人あたりのセッション数。G1 の基盤（`experiments/20260801-controlled-friction-task/`）を流用できるか。
4. 未踏の期間と 1 人あたりの期間の見積もり（未踏 2027 年度の日程は一次で確かめる）。
5. 文献のやり残し: [V302] の検出力表の照合、まれな二値アウトカムでの個人内の無作為化の検出力、N-of-1 の washout の一次。
6. 研究者本人の記録で手順を試運転する計画（L0 の証拠にはしない）。

## 注意

- 返答・記録・AskUserQuestion は日本語、記号を多用しない。決めることは推奨と理由を添えて AskUserQuestion で 1 件 1 問。
- ADR 本文は書き換えない。研究の主張は研究者のもの。

## 2026-10-31 追記: 同日中に進んだこと（このメモの上の「次にやること」の多くは済んだ）

- 判断 7〜17 を `.steering/20261031-gse-small-n-research-design/decisions.md` に記録した。位置づけの改訂（作業上の認知状態を推定し、詰まる前に介入を促して身体回帰の機会を差し出す）・Nudge を本体で出さない（ADR-040）・「詰まる前」は friction_rising で始めて将来ハザードへ・主要アウトカムは ADR-024 据え置き＋副・1 段目は招待を {推定器 / 無作為 / なし}。
- research-positioning・WBS・glossary・README（日・英）・agent-shared を改訂し、ADR-040 を起こした（コミット 45064fe6・/cross-review 済み）。
- 文献の 2 ラウンド目: `docs/literature/20261031-non-human-substitutes-small-n.md`（[V312]〜[V347]）。

次にやること:
1. 別タスク（`/start-task`）: Nudge の既定を無効にする（ADR-040 Migration 1）。
2. 別タスク: 招待に friction_rising の契機・無作為の時刻の条件・通常のモードの配線・`gse-replay` での再現を足す（ADR-040 Migration 2）。
3. 研究者本人の記録で詰まりの件数を数え、friction_rising の値とシミュレーションの前提を決める（WBS の A0）。
4. 事前登録の項目（ADR-040 Migration 3）。
5. PR はまだ出していない（研究者が確かめてから）。
