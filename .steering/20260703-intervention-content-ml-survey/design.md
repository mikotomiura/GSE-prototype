# Design: サーヴェイ実施方法と成果物構成

## アプローチ

1. **一次資料の俯瞰**: research-positioning.md / references.md / WBS 半年版 v2 /
   intervention.rs (現行 Need×Opportunity 実装) / intervention-design Skill を先読みし、
   裏付けが薄い箇所を RQ1–RQ4 に定式化。
2. **deep-research workflow** (Run ID: wf_c0a6bdd9-c09): 5 検索角度に分解 → 並列 WebSearch →
   23 ソース fetch → 主張抽出 (105→128) → 3票 adversarial verify → 統合。
   - セッション上限 (12:30am / 5:30am reset) で verify/synthesize が 2 回失敗。
     resume (キャッシュ再生) で fetch まで完全回収、verify は 5 主張のみ通過。
   - 統合はメインループで実施 (journal.jsonl から key→agentId→URL join で 27 ソース・
     128 主張を復元。scratchpad/claims_by_source.json)。
3. **成果物**: docs/literature/20260703-intervention-content-and-ml-grounding.md
   (落合カード 14 枚 + 改善提案振り分け + references 登録候補表) + _index.md 更新。

## 検証状態の扱い

- adversarial verify (3票) 通過 = **[検証済]**: Guo 2022 (メタ認知プロンプト) 3 主張、
  Orvell 2021 (自己距離化) 2 主張。
- それ以外は **[未検証]**: fetch agent の抽出主張 + 原文引用のみ (パネル検証は API 上限で
  未実施)。カード内で効果量を引く際は未検証であることを明示し、採用判断に使う場合は
  原論文の直接確認を推奨。

## 変更対象

- `docs/literature/20260703-intervention-content-and-ml-grounding.md` (新規)
- `docs/literature/_index.md` (行追加)
- references.md は変更しない (登録候補表をカード内に置き、研究者確認後に citation-ssot で append)
