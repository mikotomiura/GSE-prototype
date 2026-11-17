# stage1-self-run1 —— 本人の段 1 の前期の有効な日を数え、回 1 を 11-23 までに回す

## 背景

本人の段 1 は前期（手跡なし・11-07〜11-23）の途中にある。11-09 午後〜11-16 は記録が止まっていた（`.steering/20261116-stage1-recording-stopped/`）。事前登録 S1-F5 は、回 1（前期の記録で手跡の漏れの机上の確かめ・主のみ）を後期の前に 1 回回すと決めている。日数の門（有効な窓が 20 以上の日が 8 日以上・conditions.md C6）を越えなければ AUC を計算せず、回に数えない。

入口: `.steering/_handoff/next-session-gse-stage1-and-three-checks.md` → `next-session-gse-stage1-self-late-period.md` §2 → `next-session-gse-handmark-records-run.md`「回し方」。

## ゴール

- 前期の有効な日（C6 の定義）の数を、回を始めずに数える。
- 8 日に届いていれば（または 11-23 までに届けば）回 1 を `run.sh records`（`RUN_PHASE=early`）で 1 回回し、`results/records/` をコミットする。
- 11-23 までに届かなければ回 1 は回さず、「後期の前に写像を確かめられなかった」ことを decisions.md に書く。

## スコープ

### 含むもの
- 有効な日の数え上げ（件数だけ）
- 回 1 の実行と結果の記録
- 結果が「満たさない」ときは研究者に聞く（後期の前に写像を直す・S1-F5）

### 含まないもの
- 条件（conditions.md）の変更
- Q3 の 6 択に「作業していた」を足すこと、配布の門に手跡の検査を足すこと（回 1 の後の別タスク）
- 3 つの検査の道具の設計（別 worktree・別タスク）

## 受け入れ条件

- [ ] 有効な日の数（と除いた窓の理由ごとの数）を decisions.md に書いた。日ごとの割付・記録の中身・個々の申告は書いていない
- [ ] 回 1 を回した場合: `results/records/runs.txt` に started と finished があり、要約・入力の一覧・行種の門がコミットされている
- [ ] 回さなかった場合: その理由と、後期の前に写像を確かめられなかったことを decisions.md に書いた
- [ ] 段 1 の gse-next は終わりに Measuring のまま

## 関連ドキュメント

- `docs/preregistration-stage1.md` S1-F5
- `experiments/20261115-handmark-leak-desk/conditions.md` C2・C6
- ADR-051・ADR-052 D4

## 運用メモ
- /reimagine 適用: No
- 理由: 条件は固定済みで、新しい設計判断を伴わない（決めた手順を回すだけ）
- 守ること: 本人の記録の中身・個々の申告・日ごとの割付を出力しない。Codex に記録の本文と集計を送らない
