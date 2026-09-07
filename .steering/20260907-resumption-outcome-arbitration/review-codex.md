**所見**

1. **High: `source_episode_count` がエピソードを誤集約する可能性**
   `compute_receipt_free_resumption` で `source_episodes` を `episode_end_ms` だけで dedup しています。異なる stuck episode が同じ `end_ms` を持つ場合、寄与エピソード数が過小計上されます。通常は稀かもしれませんが、同一 timestamp の feat/merged episode があり得るならバグです。`StuckEpisode` 全体、または index で dedup する方が堅いです。

2. **Medium: 入力ソート前提が破れると結果が静かに壊れる**
   `segment_resumptions` / `classify_resumption` は `keys` 昇順前提で `windows(2)` や `partition_point` を使っていますが、検証・sort がありません。一方 `observation_end_ms` は「整列前提を持ち込まない」と最大値を取っており、方針が混在しています。上流で必ず sort 済みなら明文化だけでもよいですが、外部ログ由来なら defensive sort または debug assert が欲しいです。未ソートだと next away candidate や resumption 抽出が誤分類されます。

3. **Medium: `classify_resumption` が episode 境界を使っていない**
   `ResumptionEvent` には `episode_end_ms` があるのに、分類は `resumed_at_ms` 以降の全 paste を対象にします。仕様が「再開後の最初の external paste」なら正しいですが、stuck 起因の受領だけを見たいなら、次 episode やセッション内の無関係 paste を拾う設計リスクがあります。誤検知の可能性あり。ADR上の意図確認ポイントです。

4. **Low/Medium: 後方互換は DB 入力側だけで、Rust JSON 出力名は破壊的変更**
   `OutcomeMetrics` の serde field 名が旧名から新名へ変わっています。`build_analysis_db.py` は legacy alias を読めますが、他の下流 consumers が旧フィールドを読む場合は壊れます。必要なら `#[serde(alias = ...)]` は deserialize 用なので不十分で、移行期間だけ旧名も出す、または schema version bump が必要です。

5. **テスト不足**
   追加テストは厚いですが、未ソート `keys/pastes`、同一 `episode_end_ms`、複数 episode に同一 gap が候補になる場合、`observation_end_ms < resumed_at_ms` の打ち切り挙動が未カバーです。特にソート前提の破れは静的解析では拾いにくいです。

セキュリティ面では、相対時刻のみ serialize する設計は妥当です。絶対時刻を持つ `ResumptionEvent` に `Serialize` を付けていない点も良い防御です。
