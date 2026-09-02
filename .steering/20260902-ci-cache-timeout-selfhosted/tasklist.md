# tasklist — self-hosted の rust-cache 無効化

## 調査（★ 一次資料まで降りる）

- [x] PR #143 の失敗を API で確認 — ⚠️ 実体は `fail` ではなく **`cancelled`**
- [x] step ごとの所要時間を実測（3 job）— ★ 実作業は全 success・3m33s〜6m00s
- [x] run ログで `Cache hit` → `No cache found.` を確認（★ 3 job すべて）
- [x] 転送速度を実測 — ⚠️ 0.0〜0.6 MB/s・578〜730MB
- [x] ⚠️ **過去の run で復元が成功していたか**を確認 → ★ 08-30/08-31 は成功。当初の見立てを訂正
- [x] Actions キャッシュ総量を実測 — ⚠️ **10.56 GB**（上限 10GB 超過）
- [x] self-hosted の `target/` 永続を実測 — ★ 2.1GB・09-02 付 `.rlib` 237 個
- [x] ⚠️ **`build-macos` も同じ欠陥を持つ**ことを発見（★ L516・dmg を作る当のジョブ）

## 実装

- [x] `check` の rust-cache に `runner.environment == 'github-hosted'` を追加
- [x] `build-macos` の rust-cache に同条件を追加
- [x] ⚠️ `build-windows`（hosted）は**触らない**
- [x] `runner.environment` をログに出す step を両ジョブに追加（★ 分岐の証拠）
- [x] ⚠️★★★ `build-macos` の **npm キャッシュ**も無効化（★ v0.1.30 実測で 10m39s＝最大ステップ）
- [x] ⚠️ `frontend-check` / `build-windows` の npm キャッシュは**触らない**（hosted）
- [x] 実測に基づく理由をコメントとして残す

## 検証

- [x] YAML として妥当（ruby -ryaml）
- [x] `actionlint` — ★ 新規の指摘なし（残るのは既存の `gse-mac` ラベル 2 件と SC2012 1 件）
- [x] ⚠️ **変異注入**: `runner.enviroment` (typo) に変えると actionlint が
      `property "enviroment" is not defined ... {..., environment: string, ...}` で**赤になる**
      → ★ 検査が実在の欠陥を捕まえること＋`environment` が実在することの**両方**を確認
- [ ] ⚠️ **CI 実機**: check (win / mac) が両方緑
- [ ] ⚠️ job 全体が **10 分未満**
- [ ] ⚠️ **`Post Run Swatinem/rust-cache@v2` が step 一覧に無い**こと
- [ ] ★ ログに `runner.environment = self-hosted` が出ること

## レビュー

- [ ] `code-reviewer` + `security-checker` を並列起動
- [ ] `/cross-review`（Codex）

## 外界の操作（★ 研究者承認済み・2026-09-02）

- [ ] Actions キャッシュの **rust 系エントリを削除**（⚠️ `node-cache-*` は残す）
- [ ] PR 作成
- [ ] ⚠️ マージ後、**#143 / #144 を再実行**して緑を確認

## ⚠️ 本 PR の範囲外（★ 引き継ぎメモの残件）

- [ ] v0.1.31 のタグ切り・配布物差し替え（引き継ぎメモ §1b）
- [ ] `cargo-sweep` の実機導入（§5-7）
- [ ] `rustup` の復旧（§5-6）
- [ ] self-hosted の action を commit SHA でピン留め（§5-1）
