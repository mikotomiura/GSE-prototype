# 引き継ぎ: 手跡の止まり（ADR-056）の試作 —— 回 1 が終わった後に始める

作成 2026-11-20（G-GEAR・Windows）。研究者の指示「回 1 が終了した後に実施する」。新しい Claude Code のセッションで、`/start-task` から始める。
応答・記録は日本語で書く。絵文字や記号（★・⚠️）を多用しない（研究者の指摘）。

## 0. 始める条件（先に確かめる・満たさなければ始めない）

1. 回 1（手跡の机上の確かめ・前期の記録で漏れの検査を 1 回）が終わっていること。
   - 管理は枝 `exp/gse-stage1-self-run1` の `.steering/20261117-stage1-self-run1/`。`git fetch` してから、その `tasklist.md` の「回 1（8 日に届いた翌日・遅くとも 11-21）・results/records/ をコミット」が済みか、または decisions.md に「11-23 までに届かず回さなかった」と書かれているかを見る。どちらでもなければ、まだ始めない。
   - 結果が「満たさない」なら、止まりの試作の前にそれを直す（ADR-051 D3・S1-F5）。研究者に聞く。
   - 回 1 の数字を推測で書かない。results/records/ の一次を読む。回 1 は別の機械で回して、まだ push されていないことがある。fetch で見えなければ研究者に聞く。
   - 「11-23 までに届かず回さなかった」の場合は、守り（写像）を確かめられていない。そのことを研究者に示したうえで、試作を始めるかを研究者が明示的に決める（自動では始めない）。
2. 研究者に「始めてよいか」を確かめる（回 1 の結果を見せてから）。

## 1. 先に読むもの

- `docs/adr/ADR-056-handmark-stopped-state.md`（Accepted・2026-11-20）。D1〜D7 と「決めずに残すもの」。
- `.steering/20261120-handmark-coexistence-design/design-proposal.md` の §0.1（全体のコンセプト）と §4.4（止まりの設計）。試作の値の候補と確かめ方はここ。
- `.steering/20261120-handmark-coexistence-design/decisions.md` の判断 6〜10（なぜ長さを返さないか・cross-review で何を直したか）。
- `docs/literature/20261120-handmark-stop-noticing.md`（S-SN）。効くかは文献で決まらない・評価の枠の表示はストレスを生む。
- 実装: `src-tauri/src/analysis/handmark/state.rs`（`is_idle`・`drift`・splitmix64）、`trace.rs`（ポインタの跡・打鍵は入れない）、`desk.rs`（机上の道具）。
- ADR-051 D3・D5・D7（漏れの検査・再生の契約・PR の順。机上の道具は PR 4）。
- デッキ: `docs/slides/project-overview/GSE_handmark_design.pptx`（34 枚・Drive の `GSE/slides` にも同じもの）。

枝は `docs/handmark-stop-noticing-survey`（worktree `C:\GSE-wt\stop-noticing`）。S-EA → S-CX → 設計案 → S-SN・ADR-056 の順に積んであり、どれも PR を出していない。試作の枝は main が追いついていれば main から、そうでなければこの枝から切る（研究者に確かめる）。並行のセッションがあるので、新しい worktree で切る。

## 2. やること

1. `/start-task`（タスク名の例: `handmark-stopped-state-prototype`）。実装なので `/add-feature` の流れ。新しい `.rs` を足す前に `architecture-rules`・`rust-standards` を読む。
2. design-proposal §4.4 の通りに作る:
   - 見えの度合い v（`is_idle` と短い移り変わりだけで決まり、止まりの長さを持たない）。
   - 自律の動き（絶対の格子の時刻と日の種から擬似乱数を作り、有限の窓で平滑。`grid_start` と周期の関数を使わない）。
   - 境界: 起動の直後・戻した直後（最初の打鍵まで）・記録の一時停止の間は止まりを返さない。
3. 単体テスト（§4.4 の確かめ方 1）と、机上の道具での確かめ（2: 経過が読めない 3 つ・3: 漏れの検査）。
4. 試作の版を研究者自身が数日ずつ試す（§4.4 の 4）。結果は decisions.md に。
5. 値（移り変わりの長さ・記憶の窓・強さ・形）は研究者が決める。決めたら ADR-056 の「決めずに残すもの」の 1 を閉じる記録を、新しい判断として書く（ADR の本文は書き換えない）。
6. 完了時は /cross-review（2 巡）→ /finish-task。

## 3. してはいけないこと

- 止まりの長さ・経過時間・残り時間・累計を、見た目でも数字でも返さない（ADR-025 D1・ADR-048 D2・ADR-056）。止まりの長さで大きさ・速さ・明るさ・数を変えない。衰えや疲れの形・評価の色を使わない。
- 推定の出力（`p_stuck` など）を手跡に入れない（ADR-047 D2・ADR-048 D2）。
- 自律の動きに `drift` をそのまま位相として使わない（`grid_start` に依存し上限なく増える）。
- 参加者に出さない。参加者の画面が変わるのは、段 1 の後期の配布物を作るとき（研究者が決める）。
- 研究者自身の試しで、段 1 の本人の記録と割付の表（ADR-051 D4）を汚さない。記録を切った別のビルドか、段 1 の外の期間で行う。試作が後期の配布物に間に合わないときの扱い（後期は今の手跡のまま・ADR-056 D6 の比べは後に回すか諦める）は研究者に聞く（design-proposal §6 の日程の注意）。
- 再生の決定性（ADR-051 D5 の `to_bits` の一致）を壊さない。`StageState` にフィールドを足すと、serde で送る窓の側も変わる。
- 今ある基層（`drift` で動く霧と粒）を黙って消したり残したりしない。design-proposal §4.4 の通り、確かめ方の (iii) で見てから研究者に確かめる。
- 事実を断定する前は `verify-before-claiming`、サブエージェントへ渡す前は `subagent-delegation` の Skill を読む。
- NDJSON の生ログや打鍵の内容を外部の LLM（Codex を含む）に送らない。`git add -A` を使わない（明示のパスだけ）。権限や allowed-tools を自分で広げない。
- `.codex/budget.json` を `git checkout --` で戻さない（記帳が消える）。

## 4. 回 1 を待つ間に、もし研究者が別の手跡の作業を頼んだら

- S-EA → S-CX → 設計案 → S-SN の枝を PR にする順（下から）を研究者に確かめる。
- 段 2 の事前登録での手跡の扱い（ADR-056 D5）は、段 2 の人数と期間の見積もりの後。
