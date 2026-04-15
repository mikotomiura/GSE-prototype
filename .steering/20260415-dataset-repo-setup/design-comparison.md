# 設計案比較 — gse-dataset Phase 1 対応

## v1 の要旨

既存 gse-dataset の構造 (`schema/v1.json` + 3 scripts + raw/anonymized 分離) を **最小拡張**。schema を v1→v2 に手動 bump、anonymized NDJSON を tracked 化して git に入れる。OS 別ディレクトリで raw/anonymized/metrics を分離。ユーザー指示 (B) を文字通り実装する最も直接的な案。

## v2 の要旨

根本原因を **2 つ疑って再設計**:
1. schema drift 問題 → Rust 型から JSON Schema を機械生成 (`schemars`)、gse-dataset は生成物のみ保持、手書き v1/v2/v3 の廃止
2. 共有の本質 → Phase 2a Go/No-Go に必要なのは metrics.json (1 KB) であって 40KB の anonymized NDJSON ではない。anonymize pipeline は保守するがコミットは Phase 2 ML training 時まで先送り

schema を単一ファイル `current.json` に集約し、CI で drift 検知。metrics/ を Phase 1 の「共有の主役」に据える。

## 主要な差異

| 観点 | v1 | v2 |
|---|---|---|
| アプローチ | 既存構造の最小拡張・手書き schema bump | schema 生成 + 共有アーティファクト再定義 |
| schema 管理 | `schema/v1.json` (legacy) + `schema/v2.json` (手書き、新規) | `schema/current.json` のみ (gse-prototype から機械生成) |
| 共有の主役 | anonymized NDJSON (+ metrics.json 副次) | metrics.json (+ anonymized は Phase 2 まで保留) |
| gse-prototype 側変更 | docs + CLAUDE.md の 2 行 | `schemars` 依存追加 + `emit_schema` bin 新規 + DTO ミラー + CI drift check |
| gse-dataset 側変更 | schema/v2.json 手書き、scripts/ 3 ファイル修正、.gitignore 緩め、README 改訂 | schema 生成物コミット、validate/import/aggregate 3 scripts 修正、.gitignore 維持、README 全面改訂 |
| 変更規模 | gse-prototype: 〜10 行 / gse-dataset: 〜150 行 | gse-prototype: 〜100 行 + Cargo 依存 / gse-dataset: 〜120 行 |
| テスト戦略 | schema validate 手動、CI 追加なし | CI drift check 必須 (schema 不整合を機械的にブロック) |
| プライバシー | VK カテゴリ + timestamp が git に入る (private repo 前提) | Phase 1 は集計値のみ git、record 単位の timing データは commit しない |
| Phase 2 以降への適応 | Phase 2a/2b/3 で schema を手で bump (v3/v4/v5) | 型追加するだけで schema 自動更新、CI が gse-dataset 側同期を通知 |
| リスク | schema bump 漏れで validate 失敗 (人的エラー) | DTO ミラー維持コスト (型バリアント追加時の 2 箇所更新)、CI で検知はできる |
| 受け入れ条件との整合 | 完全一致 (11/11) | 受け入れ条件 4 (anonymized tracked) を **却下**、残りは満たす |

## 推奨案

**v2 を推奨**。根拠:

1. **schema drift は Phase 1 内だけの問題ではない** — Phase 2a (Synthetic Friction) で feat に `silence_floor` 等の新フィールド、Phase 2b (IME Shadow) で `ime_shadow` バリアント、Phase 3 で LR スコアが入ることが roadmap で既定。v1 は毎回 `v3.json`/`v4.json` を手書きする運用になり、忘れた瞬間に data 側が壊れる。v2 は構造的に解決する
2. **Phase 1 の「共有の真のニーズ」は集計** — Phase 2a の Go/No-Go は「Stuck precision 平均 ≥ 0.6」であり、これを判定するのに必要なのは各セッションの precision/recall のみ。anonymized NDJSON は record 単位の情報を含むが、Phase 2a の意思決定にはオーバースペック。metrics.json で十分
3. **プライバシー原則 "外部流出経路を 0" と整合** — anonymized NDJSON も timing attack のリスクはゼロではない (打鍵間隔から使用時間帯・集中度が復元可能)。metrics のみなら漏洩リスクが構造的に排除される
4. **Phase 2 ML 時に anonymized NDJSON をコミットする選択肢は残る** — `.gitignore` を 1 行外すだけで v1 の状態に移行でき、不可逆ではない
5. **v1 の受け入れ条件 11 個中 10 個は満たす**。却下した 1 個 (anonymized tracked) は requirement 作成時の仮決定であり、v2 が「なぜ今は不要か」の根拠を提示している

## ハイブリッド案 (v1.5)

v2 の「schema 生成」は採用し、「anonymized commit」は v1 どおり採用する折衷:
- schema は機械生成で drift 解決
- anonymized NDJSON は (B) に従って tracked
- metrics.json も追加で tracked
- cons: 変更量が最大化、CI complexity も最大

ユーザーが (B) の文字通り実装を望むなら v1.5 が安全。v2 の「anonymized 先送り」に懐疑的なら v1.5 を検討。
