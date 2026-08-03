---
name: issue-slicing
description: >
  grill (`grilling` skill) で確定した検証可能なゴールを、独立に検証できる縦切り
  (vertical slice) の issue 群に分解する。`to-prd` → `to-issues` の後段。
  `.steering/[task]/issues/00X.md` (README 2.6 テンプレ = `.steering/_template/loop-issue.md`
  準拠) を生成し、依存 DAG と Allowed Files 交差表を `_issue-plan.md` に出力する。
  「ゴールを issue に分解する」「ループを回す issue を切る」「to-issues を実行する」時に起動する。
allowed-tools: Read, Write, Edit, Grep, Glob
---

# issue-slicing

## 実行モデル
**Opus** で実行する（`/model opus`）。理由: 切り方を誤ると全ループが「正しい方向に無駄に走る」
結果を招き、verify では機械的に検出できない。誤りのコストが最も高いため、実装フェーズの Sonnet
より高い高度を割り当てる (`docs/loop-engineering.md` モデル割当ポリシー準拠)。

## 役割
確定ゴールを「独立に検証できる縦切り (vertical slice)」の issue 群に分解する。
各 issue には必ず Acceptance Criteria (AC) ＋ Test Plan ＋ verify_level (parse | recheck)
＋ Allowed Files ＋ Dependencies を含める。

grill を経ていないゴール (判断分岐が閉じていない・glossary/decisions に記録がない) を
入力に取らない。grill 未実施ならまず `grilling` skill に差し戻す。

## 7 基準 (`docs/loop-engineering.md` と同一・逐語・逸脱禁止)

1. **縦切り**: 1 issue = 層を貫いて価値を 1 本通す。層別の横切り分割は禁止。
2. **粒度**: `budget.max_attempts` (既定 6) 以内に緑にできる大きさ。
   目安 変更 ≤ 5 ファイル / ≤ 300 行 / AC 3〜7 項目。超えたら分割。
3. **独立性**: `## Allowed Files` 集合が交差しない issue だけが並列可能。
   交差するなら `## Dependencies` に書いて直列化する。
4. **検証可能性**: AC は exit code か test 名で言える。「使いやすい」「速い」は AC にしない
   (p95 < 200ms ＋ 対応 test 名に落とす)。AC↔test マッピングが空の issue は issue ではない。
   さらに **その exit code を script が実際に回収できるか** (= `verify` / `acceptance` に
   載っているか) まで確認する。
5. **verify_level**: AC 直結 / security / 公開 API / データ移行 / 課金 に触れるなら `recheck`。
   それ以外は `parse`。全部 `parse` にしない。
6. **DAG**: 依存は DAG。循環禁止。orchestrator は topological order で実行する。
7. **単独 merge 可能性**: 単体 merge しても main が壊れない (feature flag / 後方互換)。
   1 issue = 1 PR 候補。

## 出力に必ず含める

- `.steering/[task]/issues/00X.md` 群
  (テンプレ = `.steering/_template/loop-issue.md`。フィールド: Goal/Background,
  Scope In/Out, Allowed Files, Acceptance Criteria (AC↔test), Test Plan,
  Stop Conditions, Dependencies, Status, Execution Result)
- `.steering/[task]/_issue-plan.md` に次の 2 つを書く:
  - 依存 DAG (循環が無いこと・最長 chain の段数 = 直列時の総 attempt 見積り)
  - Allowed Files 交差表 (どの組が並列可能かの根拠)
  → モード B の `/loop-orchestrate` はこのファイルを読んで実行順と並列度を決める。
    モード A でも人が並列度を決める根拠になる。

## 分解の締めに行う自己検査 (全部 [x] になるまで終わらない)

- [ ] 各 issue を単体 merge しても main が壊れないか
- [ ] 各 AC に対応する test 名を「今」書けるか (書けない = AC が曖昧)
- [ ] Allowed Files 交差表を作り、並列可能な組を根拠付きで示したか
- [ ] DAG に循環がないか。最長 chain は何段か
- [ ] recheck を基準 5 で選別したか (全部 parse になっていないか)
- [ ] AC が書けない「リファクタするだけ」の issue を作っていないか
- [ ] pin 済み verify の前提を変える issue を最初の単独ウェーブに置いたか
- [ ] test/lint が無条件に緑になる issue に `acceptance.sh` を書いたか

## アンチパターン

- 層別の横切り分割 (例: 「バックエンド issue」「フロントエンド issue」に分けるだけ)
- AC 10 項目超の巨大 issue (基準 2 の粒度超過)
- Allowed Files が交差するのに並列と宣言する
- 依存の循環
- recheck が 0 件 (基準 5 を機械的に「全部 parse」で埋めている)
- grill を経ていない曖昧なゴールをそのまま分解する

## セッション境界 (WHY)

`to-issues` 完了後は **`/clear` して新セッションで実行する**。分解セッションには
却下案・議論・暗黙の前提が残っており、そのまま実行に入ると「issue に書いていない前提」を
持ち込んで issue ファイル = SSOT の契約が壊れる。*issue ファイルだけを読んで実行が成立
しないなら、分解が失敗している* — 新セッションはこの契約の検査装置でもある。
実行セッションは Sonnet に切り替える (`docs/loop-engineering.md` モデル割当ポリシー)。

## 関連する他の Skill
- `grilling` — このスキルの前段。判断分岐を閉じてゴールを確定する (Opus)
- `docs/loop-engineering.md` — issue 単位ループの単一 SSOT (このスキルの基準の出典)
