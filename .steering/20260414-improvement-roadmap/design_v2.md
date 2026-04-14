# 設計 v2 — 介入価値駆動型（/reimagine による独立案）

> このファイルは `design_v1.md` を参照せず、`requirement.md` と現状コードだけを材料に生成した独立設計。v1 と比較して採用案を選ぶ前提。

## 0. 実装アプローチ（v2 の原則宣言）

v2 は以下の **3 原則** に従う。これは「基盤を先に固める」という標準的な工学セオリーへの **意識的な対抗軸** として置く。

**原則 A: 介入価値駆動（Intervention Value First）**
GSE の唯一の外向き価値は「ユーザーに Lv1 Nudge / Lv2 Wall を出す判断の正しさ」。したがってロードマップは **「介入判断の正しさを測れるようにする」→「その指標を動かす」** の順に並べる。テスト基盤・パラメータ外部化・ML はこの目的の手段であって、自己目的化しない。

**原則 B: Observability 先行、Refactor は必要最小**
プロダクションでほぼ 1 人（開発者自身）しか触らない Rust コードに対し、本格的なテストピラミッドを敷くのは費用対効果が悪い。代わりに **「セッションリプレイから Stuck 検出率・誤検出率が出る」** という測定軸を先に立て、テストは「この軸が壊れないこと」を守る薄い層に絞る。

**原則 C: 二重化は恐れず、統合は結合損益で判断**
「沈黙の二重パス」のような重複は、統合が新バグを生むリスクが統合の保守利益を上回ることが多い。v2 は **明示的な 3 状態機構（typing / transition / silence）にリネーム＋ドキュメント化** するだけにとどめ、コード削減自体をゴールにしない。

---

## 1. 元ロードマップ 8 項目 + 欠落項目の判定

| # | 項目 | v2 判定 | 根拠 |
|---|---|---|---|
| 1 | Synthetic Friction を「F3≥0.15 かつ F6≥0.15 からの沈黙のみ」に制限 | **条件付き採用（Phase 2）** | 「直前にタイピング摩擦の兆候があった沈黙のみ Stuck に寄せる」のは正しい。ただし閾値 0.15 は `features.rs` の合成フロア 0.15/0.20 と干渉するため、先に GT で「true positive の沈黙」の F3/F6 分布を取ってから決める。先に閾値を書くのは本末転倒。 |
| 2 | GT プロトコル（遡及ラベリング + リアルタイム GT ボタン） | **採用／最優先（Phase 1）** | 介入の正しさを測る軸そのもの。v2 では **リアルタイム GT を先、遡及ラベリングは後**（Phase 1a / 1b）。遡及は記憶バイアスが入り UI も重い。まず「今 Stuck です」ボタン 1 個で十分データが溜まる。 |
| 3 | 訓練/評価データの時系列分割 | **採用（Phase 3 の前提）** | ML をやるならマスト。ただし ML が条件付きなので優先度は中。 |
| 4 | Stage 2 LR / Stage 3 XGBoost | **LR: 条件付き採用（Phase 3）／XGBoost: 却下** | n<50 で XGBoost は過学習確定。LR も「HMM を手動チューニングしきった後、残差で意味があるなら」という条件付き。v2 では **「LR を入れない」という選択肢を Phase 3 Go/No-Go で明示的に残す**。 |
| 5 | Windows IME 追加特徴量（Composition Dwell 等） | **採用（Phase 2 並列・シャドーモード限定）** | 既存 HMM に混ぜずログだけ取る。HMM に統合するのは Phase 3 の LR 特徴量として。 |
| 6 | Lv3 Thought Scaffold（固定テキスト） | **却下（スコープ外扱い）** | 介入判断の正確性が上がる前に介入種類を増やすのは、ユーザー体験の劣化リスクに対して利得が小さい。Phase 4 以降。 |
| 7 | Stuck 回復時間計測 | **採用（Phase 1 と同梱）** | GT ボタンのログに `recovered_at` を併記するだけで取れる。独立タスク不要。 |
| 8 | テスト基盤 | **条件付き採用／最小限（Phase 0）** | `engine.rs::update` と `features.rs::calculate_features` の **ゴールデンテスト 2 本のみ** 先行。E2E / UI テスト・統合テストは作らない。 |
| — | **パラメータ外部化（欠落項目）** | **却下** | §8 で詳述。Rust 定数のまま `// TUNE:` マーカー整理のみ。 |
| — | **セッションリプレイツール（欠落項目）** | **採用／最優先（Phase 0）** | NDJSON → engine 再実行の CLI。**これ 1 本で事実上テスト基盤・GT 評価・チューニング・リグレッション検知を兼ねる**。v2 の背骨。 |
| — | **沈黙の二重パス統一（欠落項目）** | **却下（リネーム＋ドキュメント化のみ）** | §0 原則 C 参照。 |
| — | **Lv1/Lv2 保護（欠落項目）** | **採用（Phase 0）** | feature flag ではなく **セッションリプレイ差分比較** で守る。 |

---

## 2. Phase 分割（v2 独自案）

v2 の切り方は **「測定 → 介入価値 → 最適化」** の 3 軸で、テストと ML は横断的に Phase 0 と Phase 3 に薄く刺す。

```
Phase 0: Replay & Guard       （測定基盤／2〜3 週）
   │
   ├──→ Phase 1: Ground Truth     （GT 収集／2 週）
   │        │
   │        ├──→ Phase 2a: Synthetic Friction 再設計（1 週）
   │        │
   │        └──→ Phase 2b: IME Shadow Features（1 週・並列）
   │                │
   │                └──→ Phase 3: LR / No-LR 判断ゲート（2 週）
   │
   └──→ (Phase 4 はスコープ外: Lv3 / XGBoost / 匿名化公開)
```

Phase 2a と 2b は **並列実行可能**（触るファイルが engine.rs と features.rs／input/ime_*.rs で独立）。Phase 0 完了後、Phase 1 と Phase 2b の着手は並列でよい（2b はシャドーモードなので GT を必要としない）。

---

## 3. Phase 0: Replay & Guard（最重要）

**ゴール**: NDJSON ログ 1 本を食わせると engine の全出力（p_flow, p_inc, p_stuck, 介入トリガー判定）を再現する **オフライン CLI `gse-replay`** が存在し、既知の良いセッションに対するスナップショットを保持する。

### タスク

| ID | タスク | 変更/追加ファイル | 規模 | 依存 |
|---|---|---|---|---|
| P0-1 | `gse-replay` バイナリ新設（`src-tauri/src/bin/replay.rs`） | 新規 | M | — |
| P0-2 | `engine.rs` を `lib.rs` スレッド構築から切り離し可能にする（Tauri API を直接触らない純粋化） | `analysis/engine.rs`, `lib.rs`（呼び出し側のみ） | S | — |
| P0-3 | ゴールデンスナップショット 3 件（Flow 主体 / Incubation 主体 / Stuck 主体） | `tests/fixtures/*.ndjson`, `tests/snapshots/*.json` | S | P0-1 |
| P0-4 | `engine::update` と `features::calculate_features` のユニットテスト 2 本（ペナルティビン遷移、空バッファ挙動） | `analysis/engine.rs` 内 `#[cfg(test)]` | S | P0-2 |
| P0-5 | ローカル `cargo test` で回るゴールデン比較 + `justfile` または `cargo xtask snapshot` | `justfile` | S | P0-3 |
| P0-6 | `docs/architecture.md` に「沈黙 3 状態機構（typing / transition / silence）」セクション追加 + コード内コメントリネーム | `lib.rs:659-678`, `features.rs:230-261`, `docs/architecture.md` | S | — |

### Go/No-Go（Phase 1 へ進む条件）

- [ ] `gse-replay fixtures/flow.ndjson` が `snapshots/flow.json` と byte-equal で一致（誤差 < 1e-9）
- [ ] 既存の Lv1 Nudge 発火タイミングが snapshot に焼き込まれており、変更があれば CI が落ちる
- [ ] `engine.rs` を `lib.rs` から独立してビルドできる（Tauri 依存が analysis/ から消えている）

---

## 4. Phase 1: Ground Truth

**ゴール**: ユーザーが「今 Stuck でした」「今 Flow でした」をリアルタイムで押せる。セッション終了後に `gse-replay --with-gt` で混同行列が出る。

### タスク

| ID | タスク | 変更/追加ファイル | 規模 | 依存 |
|---|---|---|---|---|
| P1-1 | GT ボタン 3 種（Flow / Incubation / Stuck）を Dashboard に追加 | `src/components/Dashboard.tsx` | S | P0 完了 |
| P1-2 | Tauri command `record_user_label` 追加 | `src-tauri/src/lib.rs` | S | P1-1 |
| P1-3 | `LogEntry::UserLabel { ts, label, recovered_at: Option<u64> }` をロガーに追加 | `logger.rs` | S | P1-2 |
| P1-4 | Stuck ラベル後、Flow に戻ったら自動で `recovered_at` を埋める（p_flow > 0.5 が 10 秒継続） | `lib.rs`（分析スレッド） | S | P1-3 |
| P1-5 | `gse-replay --metrics` で混同行列・Stuck 検出リード/ラグ時間・介入発火 precision/recall を出力 | `bin/replay.rs` | M | P1-3 |

**遡及ラベリング UI は Phase 1 では作らない**（v2 独自判断）。リアルタイム GT で 20 セッション集めた段階で再評価。

### Go/No-Go

- [ ] 10 セッション以上の GT ラベル付きログが存在
- [ ] Stuck precision/recall がベースラインとして記録されている（数値の良し悪しは問わない。**「測れている」こと自体がゲート**）
- [ ] リード/ラグ時間の中央値が記録されている

---

## 5. Phase 2a: Synthetic Friction 再設計

**ゴール**: Phase 1 の GT データを使い、`silence_secs → F3/F6 フロア` の関数形を経験的に再設計する。

### タスク

| ID | タスク | 変更/追加ファイル | 規模 | 依存 |
|---|---|---|---|---|
| P2a-1 | GT 付き全セッションで「沈黙開始前 5 秒の F3/F6 実測値」と「その沈黙が Stuck ラベルされたか」の散布図を出力 | `bin/replay.rs --scatter` | S | P1 完了 |
| P2a-2 | Synthetic Friction を「**直前 F3 または F6 ≥ 経験閾値**」からの沈黙のみに変更 | `features.rs::make_silence_observation`, `lib.rs:659-678` | M | P2a-1 |
| P2a-3 | 閾値変更前後で `gse-replay --metrics` を走らせ、precision/recall の差分表を残す | `.steering/` 下の記録 | S | P2a-2 |

### Go/No-Go

- [ ] 変更後、Stuck precision が **低下していない**（recall 低下は許容、precision 低下は即 revert）
- [ ] Lv1/Lv2 発火タイミングのスナップショット差分が意図通り（ゴールデン更新承認を記録）

---

## 6. Phase 2b: IME Shadow Features（並列）

**ゴール**: Windows で Composition Dwell Time / Conversion Count などを **ログにだけ書く**（HMM には入れない）。

### タスク

| ID | タスク | 変更/追加ファイル | 規模 | 依存 |
|---|---|---|---|---|
| P2b-1 | `IME_OPEN` 遷移時の `composition_start_ms` を記録 | `input/ime_windows.rs` | S | P0 完了 |
| P2b-2 | `LogEntry::ImeShadow { ts, dwell_ms, conversion_count }` 追加 | `logger.rs` | S | P2b-1 |
| P2b-3 | macOS 版は **仕様だけ書いて実装は保留**（TCC・dispatch_sync 制約コストが価値を超える） | `docs/functional-design.md` | S | — |

### Go/No-Go

- [ ] Windows で 5 セッション以上のシャドーログが取れている
- [ ] HMM の既存出力に **何も影響していない**（スナップショット差分ゼロ）

---

## 7. Phase 3: LR / No-LR 判断ゲート

**ゴール**: 「LR を入れるべきか？」を **データで決める**。入れないという結論も対等に扱う。

### タスク

| ID | タスク | 変更/追加ファイル | 規模 | 依存 |
|---|---|---|---|---|
| P3-1 | Python オフライン学習スクリプト（sklearn LR、時系列 80/20 分割） | `ml/train_lr.py` | M | Phase 2 完了 |
| P3-2 | LR 係数を Rust 定数として出力（手貼り、数値 6 個程度） | `ml/export_weights.py`, `analysis/engine.rs` 末尾定数 | S | P3-1 |
| P3-3 | LR を **独立関数 `lr_score(features) -> f64`** として Rust に埋め込み、**HMM 出力と AND で介入発火に使う**（置き換えない） | `analysis/engine.rs` | M | P3-2 |
| P3-4 | `gse-replay --metrics` で「HMM のみ vs HMM + LR」の precision/recall 差分表 | `bin/replay.rs` | S | P3-3 |

### 採用しない別案とその理由

- **Python subprocess 非同期スコアリング**: 30 秒 1 回の推論に IPC は過剰。起動レイテンシと TCC が増えるだけ。却下
- **WASM で推論**: LR に WASM は大げさ。定数 6 個なら Rust 定数が速い。却下
- **ONNX Runtime**: LR には過剰。将来 XGBoost/TCN に進むときに再評価。保留

### Go/No-Go

- [ ] LR 追加で precision が 5% 以上改善し、かつ recall が 3% 以上悪化していない
- [ ] 満たさない場合は **「LR を入れない」決定を記録して Phase 3 を閉じる**（失敗ではなく正当な判断）

---

## 8. パラメータ外部化について（v2 の立場）

**v2 判定: 却下**

理由:
1. GSE は単一ユーザー（開発者）用のプロトタイプ。TOML/JSON に出しても読み書きするのは同じ人間
2. `emissions[78]` や `transitions[9]` は Rust 配列リテラルで型チェック + コメント併記ができる。外部化は **パースエラーと整合性チェックを自前で書く必要**
3. トレーサビリティは Git で十分
4. 外部化の唯一の正当な動機「ML と手動チューニングを同じ設定フォーマットで管理」は、v2 では LR 係数を Rust 定数として手貼りするので消える

**代案**: engine.rs の定数に `// TUNE:` マーカーコメントを統一し、`grep -n "TUNE:"` で全チューニングポイントが列挙できるようにする。

---

## 9. v1 と明示的に異なる選択

### 9.1 v1 と違う選択

1. **セッションリプレイを Phase 0 の背骨に据えた**: テストとリプレイを分離せず、ゴールデン比較 = リプレイ出力の byte-equal 比較とする
2. **沈黙パスの二重構造を「統一しない」と明言**: リネームとドキュメント化のみ
3. **パラメータ外部化を却下**
4. **遡及ラベリング UI を Phase 1 で作らない**: リアルタイム GT + リプレイ目視で代替
5. **LR の Go/No-Go に「入れない」選択肢を対等に置いた**
6. **Lv3 Thought Scaffold を Phase 4 以降に落とした**
7. **IME 追加特徴量を Phase 2b として Phase 1 と並列化**（GT 待ち不要）
8. **macOS の IME 追加特徴量を明示的に保留**

### 9.2 v1 と同じ結論に至っているであろう項目（理由は違う）

- **GT が最優先**: v1 は「ML の前提」と位置づけそうだが、v2 は「介入判断の価値を測る唯一の指標」として位置づける（ML をやらなくても GT は要る）
- **Synthetic Friction 修正は Phase 2**: v2 は「GT で観測してから閾値を決める」を必須にしている点が違う
- **XGBoost 却下**: データ量から明白

---

## 10. 既存機能の保護戦略

feature flag は採用しない（単一ユーザーではロールアウトの意味が薄い）。代わりに:

- **ゴールデンスナップショット + リプレイ差分**: 以降の全変更は `gse-replay` の差分を明示承認で通す
- **Lv1/Lv2 トリガータイムスタンプをスナップショットに焼く**: 1ms でもずれれば CI が落ちる
- **`engine.rs` の `is_paused`・`backspace_streak` のような外部状態 Atomic は Phase 3 まで触らない**

---

## 11. リスクと緩和

| リスク | 緩和 |
|---|---|
| GT データが集まらない | Phase 1 でボタン押下時刻が後で確認できる UI を入れる |
| Synthetic Friction 変更で Stuck recall が急落 | P2a-3 の前後比較で即 revert |
| LR が過学習する | 時系列 80/20 分割 + 係数 6 個以下制約。L2 強め |
| リプレイ CLI が engine を純粋化する過程で既存挙動を壊す | Phase 0 で先にスナップショットを取ってから純粋化 |

---

## 12. スケジュール感

| Phase | 推定期間 | 並列度 |
|---|---|---|
| Phase 0 | 2〜3 週 | 単独 |
| Phase 1 | 2 週 | 単独 |
| Phase 2a + 2b | 1〜1.5 週 | 並列 |
| Phase 3 | 2 週 | 単独 |

合計 **7〜8.5 週**。Phase 4 以降（Lv3 / 匿名化 / XGBoost）はスコープ外。

### Critical Files

- `src-tauri/src/analysis/engine.rs`
- `src-tauri/src/analysis/features.rs`
- `src-tauri/src/lib.rs`
- `src-tauri/src/logger.rs`
- `src/components/Dashboard.tsx`
- （新設）`src-tauri/src/bin/replay.rs`
