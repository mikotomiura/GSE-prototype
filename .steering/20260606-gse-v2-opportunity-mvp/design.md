# Design

## 方針

MVP では Need と Opportunity を明確に分離する。

```text
Need:
  p_stuck を中心に「介入が必要そうか」を表す

Opportunity:
  cooldown / daily_cap / recent_dismiss / Monk Mode / idle_ms / post_burst_pause で
  「今介入してよいか」を判定する

Policy:
  none / nudge / wall / defer を返す
```

## 変更対象

- `src-tauri/src/analysis/intervention.rs`
  - `InterventionPolicyState`
  - `InterventionDecision`
  - `decide()`
  - 単体テスト
- `src-tauri/src/analysis/mod.rs`
  - 新モジュール公開
- `src-tauri/src/lib.rs`
  - `LatestFeatState` と `InterventionState` を管理
  - `get_intervention_decision` / `record_intervention_dismiss` Tauri command を追加
  - 分析スレッドで最新 `FeatSnapshot` を保持
- `src-tauri/src/logger.rs`
  - `LogEntry::InterventionDecision` を追加
- `src-tauri/src/schema_dto.rs`
  - schema DTO に `InterventionDecision` を追加
- `src-tauri/src/bin/replay.rs`
  - 新ログ種別を読み飛ばし対象に追加
- `src/App.tsx`
  - Frontend の閾値・累積 Wall 判定を Rust decision 駆動へ移行
- `src/components/Overlay.tsx`
  - Nudge 表示を `decision.action` ベースへ変更
- `docs/functional-design.md`
- `docs/architecture.md`
- `docs/glossary.md`
- `docs/gse-v2-redesign.md`

## 初期パラメータ

| パラメータ | 値 | 根拠 |
|---|---:|---|
| Nudge need | `p_stuck >= 0.60` | 現行比較を維持 |
| Wall need | `p_stuck >= 0.70` | 現行比較を維持 |
| Wall accumulation | `30_000 ms` | 現行比較を維持 |
| Slack threshold | `p_stuck < 0.50` | 現行の減衰条件を維持 |
| Nudge cooldown | `10 min` | 軽介入の連発防止 |
| Wall cooldown | `60 min` | 強介入の希少化 |
| Nudge daily cap | `6/day` | 1作業日あたり控えめ |
| Wall daily cap | `1/day` | 強制介入の過多防止 |
| Recent dismiss | `20 min` | 拒否直後の再提示防止 |
| Short pause | `2-8 s` | 既存 F5/F6 の 2s pause と接続 |
| Medium pause | `8-30 s` | 熟考/停滞候補 |
| Away idle | `180 s` | 離席候補として Wall 抑制 |

## ログ

`intervention_decision` は固定語彙のみを記録する。

```json
{
  "type": "intervention_decision",
  "t": 123456789,
  "action": "defer",
  "need_score": 0.78,
  "opportunity_score": 0.32,
  "p_stuck": 0.78,
  "idle_ms": 4200,
  "wall_accum_ms": 12000,
  "reason": "high_need_but_low_opportunity",
  "suppressed_by": ["recent_dismiss"]
}
```

## プライバシー

- Unicode 文字、本文、ウィンドウタイトル、選択文字列は扱わない。
- `suppressed_by` / `reason` は固定カテゴリ文字列のみ。
- セッションログは既存どおりローカル FS のみ。

## テスト戦略

- `analysis::intervention` の単体テスト。
- `cargo test`。
- `npm run build`。
- `cargo run --bin emit_schema` で `src-tauri/schema/current.json` を更新。
