# 設計

## アプローチ

1. 一次資料を読む: G1 / O1 の同意文書・ADR-014 判断 3・ADR-038・2026-08-04 D-3（倫理審査の枠の撤去）。
2. 外部の事実を下位エージェント 3 本（Sonnet・read-only・15 分）で並列に調べ、要点を自分で一次確認する
   （BRM の投稿規定・個人情報保護法の条文・日本心理学会の方針・外部の委員会の費用・Monaco & Tappert の抄録）。
3. 明日の O1 開始に効く事実（BRM は開始前の承認を求める）を研究者に先に出し、判断を受けてから書く。
4. 書く: 今日の一文の案 → ADR-039 → 同意文 v2 → 問い合わせ文 → 事前登録草案の修正。

## 変更対象

| ファイル | 変更 |
|---|---|
| `docs/adr/ADR-039-research-use-and-release.md` | 新規（Proposed） |
| `docs/adr/README.md` | 索引に 1 行 |
| `docs/agent-shared.md` | ADR の番号範囲（〜039） |
| `docs/references.md` | [V237]〜[V242] を append |
| `.steering/20261007-research-use-and-release/*` | 作業記録と草案 |
| （main チェックアウト・未追跡）`.steering/20261007-o1-preregistration-draft/preregistration-draft.md` | §0・§4・§12・§13 |

## テスト戦略

- `PYTHONUTF8=1 python3 scripts/check_citations.py` が違反なし。
- コード・フォームは変えないので、フォームの検査は回さない（反映するときに研究者側で回す: `o1-consent-today-proposal.md` §3）。
