# 次セッション — GSE 理論草案の批判的レビュー（pre-SSOT → SSOT 候補の仕分け）

> 作成: 2026-09-18 / ★ **研究者指定の次の主タスク**（`.steering/20260914-mhd-feature-offline-tiers/decisions.md` **判断 25** #1 / #2）
> ⚠️★★★ **このメモを一次資料にしない。** 一次は下の §2 に挙げる文書そのもの。
> ★ このセッションは **`/clear` の後の新しいセッション**で始める（★ タスクが切り替わるため・CLAUDE.md「コンテキスト管理ルール」）。

---

## §0 打ち込む用（★ 新しいセッションにこのまま貼る）

```text
.steering/_handoff/next-session-theory-critical-review.md を読んで、GSE 理論草案の批判的レビューを始めて。
まず /start-task theory-critical-review で作業ディレクトリを作り、§3 の手順で進めること。
モデルは Opus。応答は日本語。研究者判断が要る箇所は推測で埋めず、AskUserQuestion でまとめて聞くこと。
```

## §1 なぜこのタスクか

- 制限期間中に Codex と議論して、`.idea` に理論草案 3 本と評価契約群ができた。
  ★ 別トラックの規約（`.steering/20260916-gse-theory-operationalization-review/requirement.md` 冒頭）は、
  **「Claude Code との批判的検討と人間による採否判断を経るまで `docs/`・ADR・事前登録・実装仕様へ上げない」**と定めている。
  → ★ **このレビューが SSOT 昇格の前に必ず通る段**である。
- ★ 研究者判断（判断 25）で、このレビューに次の 3 件も入った:
  1. **`T1d`（issue 006）の「再停止」「安定生成」を、EVAL-NCC の「再停止」と一体で定義する**（起票 17。⚠️ 転帰の定義を 2 つにしない）
  2. **`T1c`（issue 004）の revision 系 4 項目の算出式**を、CORE-CS / 修正の理論と突き合わせて決める（起票 9）
  3. **ADR-030 の補訂案**を作る —— 観測区間の規則（D8 (b-2) の実装形）・feat 行 0 本で onset を立てない・
     **修飾キー規則を「あり／なしの両極」で挟む**（起票 11）・IME 抑制は P1 まで保留（起票 12）・
     穴の間隔 `hole_gap_ms` と削除 UI の最小幅の制約（起票 15）。⚠️ **補訂案を作るまで。反映は人の採否の後**。

## §2 対象（★ 研究者判断 #2: 3 本 ＋ 評価契約群）

⚠️ `.idea/` は **`.gitignore` の対象**（★ ローカルのディスクにしか無い）。⚠️ **worktree には現れない**ので、サブエージェントを worktree で動かさない。

| # | 文書 | 大きさ | 役割 |
|---|---|---|---|
| A | `.idea/20260915-gse-theory-architecture-and-roadmap.md` | 891 行 | ★ 全体の地図（理論関係図・主張階層・ロードマップ・証拠階梯）→ **最初に読む** |
| B | `.idea/20260915-generative-relinquishment-theory.md` | 658 行 | ★ 上位一般理論（生成的返権論）。構成命題 `GR-C1〜C7`・実証予測 `GR-H1〜H12` |
| C | `.idea/20260916-gse-mitou-research-plan.md` | 472 行 | 未踏分岐型の研究計画・月次ロードマップ（A と B に依存） |
| D | `.steering/20260916-gse-theory-operationalization-review/` の評価契約群 | — | `core-cs-` / `core-art-` / `bridge-dn-evaluation-contract.md`・`core-proposition-coverage-matrix.md`・`measurement-dictionary.md`・`eval-ncc-analysis-contract.md`・`eval-ncc-dag.md`・`gr-h4-h9-h11-h12-falsification-table.md`・`theory-propagation-audit.md`・`decisions.md` |
| 参 | `.idea/20260908-measurement-terminating-practice-portraiture.md` | — | GSE 固有の統合理論（計測終端型実践肖像論）の旧草案。A が参照する |

★ 既存の SSOT で**突き合わせる相手**: `docs/research-positioning.md` / `docs/preregistration-v0.3.md` / `docs/glossary.md`（**禁止用語**）/
`docs/adr/ADR-029`〜`ADR-032`（特に **ADR-030 / ADR-031**）/ `ADR-023` / `ADR-025` / `ADR-027` / `ADR-028` / `docs/architecture/expression-channel.md` /
`docs/references.md`（★ AI 疲労の [P361]〜[P367] は 2026-09-18 にコミット済み・本文未引用）。

## §3 手順

### 段 1: 批判的レビュー（★ このセッションの本体・Opus）

★ **読む順: A → B → C → D**。⚠️★★★ **1 本ずつ全文を読む**（memory「長い一次資料を 1 節だけで代表させない」／`verify-before-claiming` ルール 7・8）。
各文書について、作業ディレクトリに `review-<A|B|C|D>.md` を作り、次の 4 つを書く:

1. **主張台帳**（1 行 1 主張）: ID ／ 主張の要約 ／ 種別（定義・構成命題・実証予測・規範命題・計画・評価量）／
   根拠（出典 `[Pn]`/`[Vn]` か、無し）／ 既存 SSOT との関係（整合・衝突・新規）／ ★ **判定（保持・統合・縮小・棄却・要サーヴェイ）**
2. **SSOT との衝突**: ADR・事前登録・glossary の禁止用語。★ 禁止用語は **`python scripts/check_doc_lexicon.py`** で機械的にも見る
   （⚠️ 例: 「不便益 HCI である」「段階的介入」「回復・消耗・補充」「停滞を検出した」—— `docs/glossary.md` と ADR-030 の却下リストを一次で確認すること）
3. **サーヴェイが要る箇所**: 新規性・「先行研究が無い」系の主張と、根拠の無い理論的依拠 → 段 2 へ回す一覧
4. **研究者判断が要る箇所**: ⚠️ 推測で決めない → セッションの区切りで **AskUserQuestion にまとめて聞く**（★ 2026-09-18 の 16 問と同じ形式）

★ 加えて、このレビューで次を決める（★ 研究者の回答を得てから `decisions.md` に記録）:
- ★ **「再停止」の定義**（EVAL-NCC）→ それを `T1d` の `restop_ms` / `stable_generation_ms` に写す案（起票 17 の候補表を使う）
- ★ **`T1c` の算出式**（起票 9 の候補表を使う）
- ★ **ADR-030 の補訂案**（§1 の 3.）—— ⚠️ 案まで。ADR 本文は人の採否の後に別コミットで

★ 別トラックの受け入れ条件のうち**未チェックのもの**（`requirement.md` §受け入れ条件・`tasklist.md`）もこの段で判定する:
「CS / 芸術 / 規範の中核命題をそれぞれ一文に縮約」「規範命題が父権的介入・放置的返還・負担転嫁・再捕捉を別々に判定できる」
「非支配的協調を共和主義的非支配と同一視しない」「未実証の因果・新規性・一般化・ジャンル成立を断定していない」など。

### 段 2: サーヴェイ（★ 段 1 で「要サーヴェイ」とした箇所だけ）

- ★ `/literature-review`（1 ラウンド＝1 つの問い）。★ WebSearch は**サブエージェントへ並列に委譲**し、`docs/references.md` への追記だけメインが直列に行う（memory「Survey via subagent」）。
- ★ **1 ラウンドごとに即コミット**（memory「Commit each survey round」）。★ 出典は `citation-ssot` の規約（append-only・`[Pn]`/`[Vn]`）。
  ⚠️ `scripts/check_citations.py` は 1 回で全件を出さない —— 「違反なし」まで回す（memory）。
- ★ Codex の第二意見が欲しいときは `codex-consult`（任意）。⚠️ Codex は repo を読めないので資料をプロンプトに貼る（memory）。

### 段 3: SSOT への昇格（★ 別タスク。段 1・2 を通ったものだけ）

- ★ 1 単位（1 命題群・1 ADR 補訂）ごとに `/start-task` → 反映 → `/cross-review` **2 巡**（memory「cross-review は 2 巡」）。
- ★ 反映先の候補: `docs/research-positioning.md` / `docs/glossary.md` / ADR（ADR-030 補訂・新 ADR）/ `docs/preregistration-v0.3.md` の追補。

## §4 ⚠️ 守ること（★ CLAUDE.md とこれまでの教訓）

- ⚠️★★★ **pre-SSOT のまま扱う**: 段 1 の成果物は作業ディレクトリの中だけ。`docs/`・ADR・事前登録・実装を**研究者の採否なしに変更しない**。
- ⚠️★★★ **未実証の因果・新規性・一般化・ジャンル成立を断定しない**。「先行研究が存在しない」は体系的レビューの後でしか書かない。
- ⚠️ **「AI エージェントで実装できたこと」を受容・介入効果の証拠として扱わない**（別トラック `requirement.md`）。
- ⚠️ memory「Amateur thinking, expert execution」: **証拠が無いことを理由に研究の問いを先に狭めない**。狭さは実行側（段・勝ち幅・降格先）に置く。
- ⚠️ memory「Stale doc: revert to primary」: 古い記述は「新しい方に揃える」でなく**一次へ戻す**。埋まらない差分は未決として起票。
- ⚠️ `git add -A` / `git add <dir>` を使わない（★ 明示ファイル指定）。★ 作業ツリーに別トラックの未コミット変更が出たら触らない。
- ⚠️ ブランチは `docs/adr-030-stall-onset-definition` のまま（★ ADR-030 / 031 / 032 はここにしか無い）。**main へ switch しない**。
- ★ 応答は日本語。★ 利用上限: 2026-09-18 に Opus のサブエージェントが HTTP 429（月次上限）で止まった → サブエージェントの本数と範囲を計画的に。

## §5 このタスクの後に待っているもの（★ 研究者判断 25 の再開順）

1. **Loop 基盤の修正**（起票 3 / 10）—— ★ 次に Loop を回す前に
2. **`--features` の封筒 issue**（起票 2 / 5）
3. **004 / 006**（★ このレビューで定義が決まったら）
4. **`capability matrix`**（ADR-032 M7）
5. P1 前: **事前宣言文書**（`W` / `q` / `B` / `hole_gap_ms` / `warmup_count` / 分位点法 / `T1a` の窓）＋ CLI 注入 ＋ 両極（ポインタ・修飾キー）の出力
- ★ タスク 2 の詳細は `next-session-mhd-tiers-researcher-decisions.md`。

## §6 保留したままの判断（★ 研究者に一度も聞いていないもの）

- `.idea/` を版管理（またはバックアップ）するか —— ★ 私的メモとして意図的に外しているなら現状維持。⚠️ ただし Codex と作った成果物がディスクにしか無い。
- 研究計画 §1 の「G1（n=0/3）が最優先の実証ボトルネック」との時間配分 —— ★ 研究者判断 25 #1 で理論レビューを主タスクにしたが、G1 の募集・O1 の配備は別枠で進める前提。
