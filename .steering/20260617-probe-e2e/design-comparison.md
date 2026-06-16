## 設計案比較 — Task E cohort orchestration

両案の合意点 (要件・凍結契約から不可避):
- cohort 入力 = 被験者別 calibration レポート JSON (NDJSON はプライバシー上ツリー走査しない・§10)。
- ゲート駆動 = `session_median` (PreReg-4 凍結文言「C-index 中央値」に従う)。pooled は併記のみ。
- `model_gate`/`measurement_gate` を再利用し再実装しない。Python 集約案は不採用 (ゲート再実装 drift)。
- 純関数 (analysis) + I/O (bin) の二層分離。

### v1 の要旨
cohort の純関数 `cohort_verdict` を **D の `calibration_eval.rs` に追記**。読み戻しのため
`CalibrationReport` と全 sub-struct に **`Deserialize` 派生を追加**。I/O 形態 (replay `--cohort`
サブモード vs 独立バイナリ) は未確定で「設計判断 A として後で決める」と留保していた。

### v2 の要旨
**D の `calibration_eval.rs` / `replay.rs` には一切触れない**。cohort は新規 `analysis/cohort.rs`
(純関数 + 必要フィールドだけの read-model DTO。serde の未知フィールド無視を利用し D の JSON を
そのままパース、Deserialize 派生は D に足さない) と新規バイナリ `gse-cohort` に隔離。I/O 形態は
**独立バイナリで確定** (replay の凍結 mode 行列・--snapshot 回帰経路を保護)。

### 主要な差異
| 観点 | v1 | v2 |
|---|---|---|
| D (calibration_eval.rs) | Deserialize 派生を全 struct に追加 | **無変更** (文字通り凍結) |
| replay.rs | --cohort サブモード追加の可能性を留保 | **無変更** (--snapshot 回帰面ゼロ) |
| 読み戻し方式 | 重い CalibrationReport 全体を Deserialize | 必要スカラだけの軽量 read-model DTO |
| I/O 形態 | 未確定 (留保) | 独立バイナリ `gse-cohort` で確定 |
| 新規ファイル数 | 少 (calibration_eval に同居) | やや多 (cohort.rs + bin + fixtures) |
| 変更規模 | D の出力型に派生追加 (広く薄い変更) | 新規追加中心 (既存は 2 行登録のみ) |
| テスト戦略 | 同等 (golden + 境界) | 同等 + DTO subset パースの実 JSON 整合検証 |
| リスク | D 凍結方針と緊張・replay mode 行列に触れる余地 | 既存挙動完全不変・回帰リスク最小 |

### 推奨案
**v2** — 理由:
1. handoff の最重要制約「D を再実装しない／凍結」を最も忠実に満たす。v1 は派生追加とはいえ D の
   出力型に手を入れ、replay mode への波及も留保していた。v2 は D・replay・schema を 1 文字も変えない。
2. serde の未知フィールド無視で「必要スカラだけの read-model」を作れば、重い CalibrationReport 全体の
   Deserialize 化 (約 10 struct + 全 enum) が不要。結合が薄く、D の出力形が増えても cohort は壊れない。
3. 独立バイナリは入力モデル (JSON ツリー vs 1 NDJSON) の違いに素直で、凍結 `--snapshot` 回帰経路を
   保護する。「1 ツール 1 責務」で合成可能。
4. 唯一のコスト (ファイル数増・DTO のフィールド名重複) は、統合テストで「D の実出力 JSON が DTO に
   正しく載る」ことを検証すれば drift を防げる。
