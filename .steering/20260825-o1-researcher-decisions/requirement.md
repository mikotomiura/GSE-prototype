# O1 の研究者判断を確定させる議論（★ mac 実装の後）

> ⚠️★★★ **本タスクは議論・決定のタスクである。コードを書かない。**
> ★ 開始プロンプト: `.steering/_handoff/next-session-prompt-o1-decisions-after-macos.md`

## 背景

★ **前提は満たされた**（2026-08-24・PR #115 merged）:

- ADR-016 **D9 前提 1**（同時稼働の実機確認）が **両 OS で閉じた**
  （mac: `CGEventTap` 2 プロセスで計数完全一致 52=52 / 70=70）。
  → ⚠️ **案 α（同一被験者・別時点）へは降りていない ＝ 研究者判断 2 は生きている。**
- ★ 計器（R3-a）は **両 OS 実装済み**（Win: PR #113 / mac: PR #115）。**記録のみ**で推論には流していない。

★ 一方で **決定が空いているために先へ進めない**ものが 3 層ある:

1. **ADR-016 が Proposed のまま**（⚠️ 研究者判断 4 が未確定）
2. **事前登録ドラフトの未凍結 5 件**（⚠️ 埋めずに収集を始めない）
3. **同意文書がドラフト・未承認**（⚠️ 承認まで配布しない・ADR-014 判断 2）

## ゴール

★ 出るべきものは **3 つだけ**（⚠️ コードではない）:

1. **ADR-016 の研究者判断 4 が埋まり、ADR-016 が Accepted になる**
2. **事前登録ドラフトの未凍結 5 件が埋まる**（⚠️ **凍結はまだしない** —— 日付は G1 収集完了後）
3. **同意文書ドラフトが承認可能な状態になる**（⚠️ 承認そのものは研究者が下す）

⚠️★★★ **決めたら必ず ADR / 事前登録ドラフト / `.steering/` の 3 つに書く**（★ D-8 の再発防止）。

## スコープ

### 含むもの
- 判断 4（`creative` の意味と宣言 UI に含めるか）
- 判断 4b（宣言の **頻度 / 粒度 / 未宣言時の扱い**・2026-08-24 に議題化）
- 事前登録の未凍結 5 件（`L_nk` / `Δ` の集合 / Decision Episode 下限 / 判断 4 / NK-6 の床 `K`）
- 同意文書の穴（研究責任者欄 / 注 A の OS 非対称 / `creative` の呼び方）
- §2-D の実装由来の論点 7 件（D-1〜D-7）それぞれの決定（⚠️ **保留なら保留と書く**）

### 含まないもの
- ⚠️ **コードを書くこと**（★ lock 解除 ＋ 宣言 UI は別セッション）
- ⚠️ **推論への配線（段 3）** —— ADR-011 D4「読む実装は G1 判定後」は不変
- ⚠️ **役割カテゴリ**（★ G2 が落ちてから）
- ⚠️ **6 段階 ablation の事前宣言**（n と検出力の算術が未了）
- ⚠️ **事前登録を `experiments/` へ置くこと**（★ 日付が嘘になる・Migration 4）

## 受け入れ条件

- [ ] 判断 4 が埋まり、ADR-016 のステータスが更新された
- [ ] 判断 4b の 3 点（頻度 / 粒度 / 未宣言時の扱い）がそれぞれ決まった
- [ ] 未凍結 5 件の各々が「埋まった」か「埋まらなかった理由」を持つ
- [ ] §2-D の 7 件それぞれに決定または明示的な保留がある
- [ ] 決定が ADR / 事前登録ドラフト / `.steering/` の 3 つに伝播した
- [ ] 禁止語 grep が 0 件

## 関連ドキュメント

- `docs/adr/ADR-016-nonkeystroke-interval-handling-in-o1.md` §研究者判断
- `.steering/20260823-o1-nonkeystroke-gap-and-prereg/preregistration-draft.md` §12
- `.steering/20260823-o1-nonkeystroke-gap-and-prereg/consent-draft-o1.md`
- `.steering/20260823-o1-nonkeystroke-gap-and-prereg/decisions.md` D-10 / D-11 / D-16
- `.steering/20260823-o1-instrument-r3a/decisions.md` D-A / D-J / D-M
- `.steering/20260824-o1-macos-instrument/decisions.md`（mac の一次記録）
- `docs/architecture/workspace-behavior-observation.md` §4.3 / §9.4
