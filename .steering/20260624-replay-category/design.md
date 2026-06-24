# 設計 — replay-category

## 実装アプローチ

`gse-replay` の `ReplayEvent::Key` を **raw (`vk`) と匿名化 (`category`) の両対応**にする。
匿名化で個々の VK は失われるが、特徴量に効くのは is_backspace (F3 修正率 / F6 削除後停止)・
文字生成キー区分・(Windows) リピート検出のみ。これらは **KeyCategory 単位の代表 VK** で
完全に再現できる。

### 鍵となる設計判断

1. **category → 代表 VK の逆写像** (`category_representative_vk`)。
   `KeyCategory::from_vk` の逆で、同じ category に再分類される代表値を返す
   (例: "alphabetic"→0x41, "backspace"→0x08, "delete"→0x2E, "space"→0x20)。
   これにより `is_backspace(vk)` / 文字生成キー分類 / リピート検出が raw と一致する。
   不変条件「`KeyCategory::from_vk(repr(c)).as_str() == c`」を round-trip テストで保証。

2. **逆写像は replay.rs (bin) 内に置く**。`anonymize.rs` (lib) は #27 で凍結済み・本タスク
   スコープ外。drift は round-trip テストが lib の `KeyCategory::from_vk` を使って検出する。

3. **schema_dto.rs は変更しない**。schema_dto は production logger 出力 (raw・vk を持つ) の
   真実源で、gse-dataset との parity 対象。匿名化 NDJSON は転送アーティファクトであり logger
   出力ではない。category を schema_dto に足すと「logger が category を出す」という誤った含意に
   なり parity を壊す。→ emit_schema parity は不変 (D-RC2)。

4. **Windows リピート検出**: `step()` は `pressed_keys: HashSet<u32>` で press/release ペアを
   追跡しリピート判定する (Windows のみ; macOS は replay で is_repeat=false 固定)。代表 VK は
   category ごとに distinct なので、通常の逐次 press/release と auto-repeat (同一物理キー連打) は
   raw と一致する。唯一 **同一 category 内のキーロールオーバ** (2 つの異なる文字キーの押下が
   重なる) のみ raw と発散しうる (匿名化で個々の VK が失われるため原理的に不可避)。これは
   Windows 限定・稀。known limitation として decisions.md に記録。

5. **相対時刻**: 匿名化は絶対 epoch を session_start 相対へ一律オフセットする。特徴量は
   イベント間隔 (差分) のみに依存するため値は不変。`FeatSnapshot.timestamp` だけが定数分ずれる
   → 検証は timestamp を除く全フィールドの一致で行う (byte-equal でなく特徴量値一致)。

## 変更対象

### 修正するファイル
- `src-tauri/src/bin/replay.rs`
  - `ReplayEvent::Key { t, vk, press }` → `{ t, vk: Option<u32>, category: Option<String>, press }`
    (両方 `#[serde(default)]`; raw は vk のみ・匿名化は category のみ持つ)。
  - `resolve_key_vk(vk, category)` / `category_representative_vk(&str)` を追加。
  - `run_replay` の Key アーム: 解決した VK で InputEvent 構築 (解決不能は warn してスキップ)。
  - `collect_key_events` の Key アーム: 解決した VK で KeyPress 構築 (匿名化でも --metrics outcome 動作)。
  - `timestamp()` / `collect_key_timestamps` は `..` パターンで影響なし。

### 新規作成するファイル
- `src-tauri/tests/fixtures/minimal.anon.ndjson` — minimal.ndjson を実 `anonymize_ndjson` で
  匿名化した golden (人手検査用)。drift-guard テストで実関数出力と byte 一致を保証。

## 影響範囲

- raw 経路は完全不変 (vk=Some の分岐は従来通り)。既存 `--snapshot` byte-equal は不変。
- 匿名化経路は追加経路。既存テスト・他モード (--metrics 等) に影響なし。

## 既存パターンとの整合性

- `#[serde(default)] Option<T>` で新フィールドを後方互換に受ける既存パターン
  (Paste.external_paste_chars / SessionMeta.condition と同様)。
- bin 層の軽量エラーは `Result<_, String>` + tracing::warn 件数可視化 (既存 collect_* と同様)。

## テスト戦略

- **単体**: `category_representative_vk_roundtrips` (全 category で from_vk 逆写像 + is_backspace 検証)、
  `replay_event_key_accepts_vk_and_category` (両 JSON 形のデシリアライズ)。
- **統合 (核心)**: `replay_anonymized_matches_raw_features` — minimal.ndjson を run_replay した
  FeatSnapshot 列と、それを実 `anonymize_ndjson` で匿名化して run_replay した列で、timestamp を
  除く全特徴量 (f1-f6/probs/raw_x/raw_y/ewma/obs/alpha) が一致することを確認。
- **drift guard**: コミット済み fixture `minimal.anon.ndjson` == `anonymize_ndjson(minimal raw)`。
- 既存 `--snapshot` byte-equal 不変・`cargo test --workspace` 緑・emit_schema parity 不変。

## ロールバック計画

replay.rs の差分を revert すれば raw 専用に戻る。fixture/テスト追加のみで production コードや
logger/schema には触れないため影響は replay ツールに限定。
