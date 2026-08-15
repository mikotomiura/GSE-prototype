# タスクリスト — Tier 0 配線（`keys` / `bs_keys`）

> ⚠️★★★ **本セッション（2026-08-15）はコードを 1 行も書いていない。** 準備までで止めた（研究者判断・コンテキスト都合）。

## 準備（★ 本セッションで完了）

- [x] 関連 docs を読む（`personalization-and-online-learning.md §5.2/§10` / ADR-008 / ADR-009 / `domain-adapter-boundary.md`）
- [x] ★ 設計の原本を読む（`.steering/20260801-recovery-axis-grounding/tier0-wiring-design.md`・181 行）
- [x] ★ 一次で `f3 = correction_keys / total_keys` を確認（`features.rs:146-152`）
- [x] ★ 一次で `feat` 行の書き出し位置を確認（`logger.rs:1214`。⚠️ memo の `:974` は古い）
- [x] ★ 一次で `FeatSnapshot` を確認（`analysis/loop_step.rs:134`・**golden の byte-equal 比較対象**）
- [x] ★ golden の本数を実測（**4 本**。⚠️ notes.md の「3 本」は古い）
- [x] ★ `C:\gse-dataset` の実在と HEAD を確認（`f3e8566`）
- [x] ⚠️★★★ **`check_schema_parity.py` を実行 → 既存 drift を検出（exit 1）**
- [x] ★ 研究者判断を 2 件取得（D1 順序 / D2 dataset 同時更新）
- [x] ★ 未決を 2 件閉じた（D3 案 B / D4 `FeatSnapshot` に含める）

## ⚠️★★★ 実装の前に（★ ここから次セッション）

- [ ] ⚠️★★★ **B-1: 既存 drift の解消** —— `hook_health` variant と `meta.g1_mode` を
      `C:\gse-dataset/schema/current.json` へ反映し、`check_schema_parity.py` を **exit 0** に戻す
      （★ **本タスクの差分を足す前に**。⚠️ 順序を守らないと切り分け不能になる）
- [ ] ★ B-1 の解消を **単独でコミット**する（★ 本タスクの変更と混ぜない）

## 実装

- [ ] `features.rs` — `total_keys` / `correction_keys` を `FeatSnapshot` まで持ち回す（★ 新規計算ゼロ）
- [ ] `analysis/loop_step.rs` — `FeatSnapshot` に `keys: u64` / `bs_keys: u64` を追加
- [ ] `schema_dto.rs` — `Feat` DTO に `Option<u64>` ＋ `#[serde(default)]` で追加（★ 読むときは省略可）
- [ ] `logger.rs:1214` — フォーマット文字列に 2 フィールド追加（★ **書くときは常に値を書く**）
- [ ] `cargo run --bin emit_schema` → `schema/current.json` を再生成（★ **同じコミットに含める**）
- [ ] ★ gse-dataset 側へ本タスクの additive 変更を反映

## テスト

- [ ] `logger.rs` のフォーマット文字列テストに期待文字列を追加（★ **新フィールドの位置と精度を固定**）
- [ ] `features.rs` の単体テスト（★ `keys` / `bs_keys` が `total_keys` / `correction_keys` と一致）
- [ ] ★ **旧フィクスチャ（新フィールドなし）を `gse-replay` が読めること**
- [ ] ★★★ **golden 4 本を再生成し、差分が「新フィールドの追加のみ」であることを確認**
      —— ⚠️ **`p_*` / `raw_*` / `ewma_*` / `obs` が動いていたら、その場で止める**（★ 契約違反の証拠）
- [ ] `HMM_VERSION` が変わっていないこと
- [ ] `cargo test --workspace` が緑（★ `cd src-tauri` してから。⚠️ repo 直下では空振りする）
- [ ] `python scripts/check_schema_parity.py --dataset C:/gse-dataset` が **exit 0**

## レビュー

- [ ] ★★★ **`code-reviewer` + `security-checker` を並列起動**（★ CLAUDE.md 必須。
      ⚠️ 前セッションでは動作条件で Agent が禁止されていたため実行できなかった）
- [ ] `/cross-review`（★ Codex 独立レビュー。⚠️ **入力は diff のみ。生ログ・NDJSON を渡さない**）
- [ ] HIGH 指摘への対応

## ドキュメント

- [ ] ⚠️★★★ `personalization-and-online-learning.md §10` の順序記述を改訂（★ D1・「G1 は P1 より前」）
- [ ] ★ `§5.2` の Tier 0 表を更新（⚠️ **`bs_rate` を「未配線」としているのは誤り**＝ `f3` として既出。原本 §0 が指摘済み）
- [ ] ★ golden 再生成の差分を `.steering/` に記録（★ Replay-as-Truth の規約）
- [ ] ★ `notes.md §5③` の「golden 3 本」を訂正するか判断（⚠️ 別タスクの記録なので研究者判断）

## 完了処理

- [ ] design.md の最終化
- [ ] decisions.md の追記（★ 実装中に出た判断）
- [ ] `/finish-task`（★ Step 3 で schema parity check が走る）
- [ ] git commit（★ **1 コミットに閉じる** = revert 1 回で戻せるようにする）
