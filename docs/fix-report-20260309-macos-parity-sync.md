# Fix Report: macOS版パリティ同期 (v2.19)

**日付:** 2026-03-09
**対象バージョン:** v2.18 → v2.19

---

## 目的

macOS版 (https://github.com/mikotomiura/GSE-prototype-for-mac) で最適化された推論エンジンの変更をWindows版に移植し、両OS間のロジック差異を解消する。

---

## 修正プロンプトの有効性判定

| Step | 指示内容 | 判定 | 理由 |
|------|---------|------|------|
| 1 | エミッションテーブル同期 | **有効** | x=2/x=3のStuck検出強化が未適用 |
| 2 | 1Hz動的ゲート再設計 | **既実装** | v2.11 Fix ⑤で Instant ベーススケジューリング済み |
| 3a | f1>0.0 ガード | **既実装** | `else if f1 > 0.0` ブランチ内に配置済み |
| 3b | 摩擦フロア最低保証 | **有効** | lib.rs に max(0.15)/max(0.20) 未適用 |
| 3c | Silence-break 3打鍵ゲート | **既実装** | v2.11 Fix ⑦で実装済み |
| 4 | Loggerフラッシュ最適化 | **有効** | 毎回フラッシュ → 5秒アイドルフラッシュ |
| 5a | is_typing_key 移動 | **有効** | features.rs にOS固有コードが残存 |
| 5b | "f6 @ 8s" コメント修正 | **該当なし** | コメント不在 |

---

## 実施した修正

### 1. エミッションテーブル同期 (`engine.rs`)

macOS版のFriction境界(x=2, x=3)チューニングを適用:

| 位置 | 修正前 | 修正後 | 効果 |
|------|--------|--------|------|
| Flow x=2 y=3 (obs=13) | 0.06 | 0.01 | Flow のx=2 y=3 放射を抑制 |
| Incubation x=2 y=3 (obs=13) | 0.01 | 0.02 | Incubation のx=2 y=3 放射を微増 |
| Stuck x=2 y=3 (obs=13) | 0.01 | 0.05 | 中摩擦+高沈黙のStuck検出強化 |
| Stuck x=3 y=3 (obs=18) | 0.02 | 0.07 | 高摩擦+高沈黙のStuck検出強化 |

**副作用考慮:** y=3 ビンのみの変更であり、y=0〜2 の主要ビン（通常タイピング領域）は不変。Stuck の x=2/x=3 領域での検出感度が向上するが、Flow/Incubation 領域への影響はない。

### 2. 摩擦フロア最低保証 (`lib.rs`)

`silence_secs >= 10.0` 時に `f6_floor.max(0.15)` と `f3_floor.max(0.20)` を適用。これにより features.rs の `make_silence_observation()` と同一のフロア保証がバッファ保持パスにも適用される。

### 3. Logger フラッシュ最適化 (`logger.rs`)

- **修正前:** `rx.recv()` + 毎エントリ後に `writer.flush()` → 高I/O負荷
- **修正後:** `rx.recv_timeout(残り時間)` + 5秒アイドルで一括フラッシュ
- `BufWriter` の内部バッファが活用され、高頻度ログ時のI/O負荷を大幅に軽減
- `LogEntry::End` 時は即座に最終フラッシュ（データロスなし）

### 4. `is_typing_key` のフック層移動 (`features.rs` → `hook.rs`)

- `features.rs` から `pub fn is_typing_key()` を削除
- `hook.rs` にローカル関数 `fn is_typing_key()` として移動
- `features.rs` の `calculate_features()` から `is_typing_key` チェックを除去（フック層で既にフィルタ済みのため冗長）
- `features.rs` にOS固有の仮想キーコード定数がゼロに

---

## デグレッション防止チェック

- [x] IME_ACTIVE ログ出力ロジック — 未変更
- [x] ポーズ解除直後のバッファクリア — 未変更
- [x] 3段階 EWMA α 遷移ロジック — 未変更
- [x] ペナルティビン (obs=25) — 未変更
- [x] v2.18 で修正した摩擦リミッター解除 — 互換維持
- [x] Silence-break 3打鍵ゲート — 未変更
- [x] is_backspace 意味論的フラグ — 未変更

---

## ビルド確認

```
cargo build — OK (no warnings, no errors)
```
