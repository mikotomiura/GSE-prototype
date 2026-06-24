# 設計判断 (replay-category)

## D-RC1: category → 代表 VK の逆写像で特徴量を再現 (run_replay は exact)
- 匿名化で個々の VK は失われるが、`run_replay` の特徴量 (f1-f6/probs) が依存するのは
  is_backspace (F3/F6) と is_press/timestamp・(Windows) リピート検出のみ。すべて **KeyCategory 単位**で
  決まるため、`category_representative_vk` (= `KeyCategory::from_vk` の逆) で同じ category へ戻る代表値を
  1 つ選べば raw と完全一致する。
- 全 11 category で特徴量等価性を `replay_anonymized_matches_raw_features_all_categories` が検証
  (OEM 句読点・Tab・テンキー演算子など `Other` 畳み込みキーを含めても特徴量不変。run_replay は
  is_text_producing を使わないため)。
- 逆写像は **replay.rs (bin) に置く** (anonymize.rs は #27 凍結・スコープ外)。drift は
  `category_representative_vk_roundtrips` が lib の `KeyCategory::from_vk` を真実源に検出する。

## D-RC2: schema_dto.rs は変更しない (emit_schema parity 不変)
- schema_dto は **production logger 出力** (raw・vk を持つ) の真実源で gse-dataset parity の対象。
  匿名化 NDJSON は転送アーティファクトであり logger 出力ではない。category を schema_dto に足すと
  「logger が category を出す」誤った含意になり parity を壊す。→ emit_schema byte-equal 不変を確認済。
- `ReplayEvent` は元から deserialize 専用で schema_dto と独立 (ファイル冒頭コメント)。

## D-RC3: `--metrics` の text-producing 判定は匿名化データでやや過小評価 (内在制約・既知)
- `metrics::is_text_producing` は VK 空間を `KeyCategory` **より細かい**境界で分割する。
  OEM 句読点 (0xBA-0xC0/0xDB-0xDF/0xE2)・Tab(0x09)・テンキー演算子(0x6A-0x6F) は raw では
  text-producing だが、匿名化で `Other` に畳まれるため復元不可 (代表 VK 0x07 = 非 text-producing)。
- 影響は **`--metrics` の manual_insert_chars 系のみ**。`--snapshot` / 特徴量再計算 (D6 本来の目的) には
  **無影響** (run_replay は is_text_producing を使わない)。
- これは #27 の匿名化設計 (KeyCategory 粒度) に内在する不可逆損失で、replay 側で fix 不能。完全に
  閉じるには #27 の匿名化が text-producing フラグを別途保持する必要があり本タスク範囲外。
- backspace/delete 判定は専用 category のため **匿名化後も完全一致**。
- silent にせず `anonymized_metrics_text_producing_undercounts_other_folded_keys` テストで差分
  (raw=8 / anon=5、Other 畳み込み 3 キー) を明示・回帰ロックし、`collect_key_events` の doc にも明記。
- code-reviewer の CRITICAL 指摘への対応: スコープを「run_replay 特徴量 exact ＋ --metrics は既知の
  内在制約」と明確化し、過大主張を是正 (requirement.md も qualify)。

## D-RC4: Windows 同一 category 内キーロールオーバの is_repeat 発散 (既知・稀)
- Windows のみ `step()` が `pressed_keys: HashSet<u32>` で press/release ペアからリピート検出する
  (macOS は replay で is_repeat=false 固定 → 発散しない)。代表 VK は category ごとに distinct なので
  通常の逐次入力・auto-repeat (同一物理キー) は raw と一致する。唯一 **同一 category の異なる 2
  物理キーの押下が重なる (rollover)** 場合のみ、匿名化後に同一代表 VK となり 2 つ目が誤って
  is_repeat 判定されうる。匿名化で個々の VK が失われるため原理的に不可避。
- 影響は Windows・同一 category 内 rollover という稀ケースに限定。テスト fixture は逐次 press/release
  で構成し発散を避けている。実運用 (研究データ共有) では許容可能な近似。
