# 設計（初案）

## 実装アプローチ

2 層に分ける。Rust の層は量を出すだけにし、解析の判断は experiments/ の層に置く。

### 層 1: `--features` に `context` を足す（Rust・オフラインの計算層）

- `src-tauri/src/analysis/feat_offline/context.rs` を新設する。tick ごとに、因果窓 `[tick_end - W_ctx, tick_end)` の中の次の量を出す。
  - `focus_transitions`: `focus_transition` 行の数。同じアプリの中の窓の切り替えも 1 回に数えるので、注意の逸脱の頻度としては読まない（`schema_dto.rs:240`）。
  - `pointer_active_secs`: `pointer_bin` 行の数（ゼロ抑制されているので、行の数がそのまま活動した秒数になる）。
  - `pointer_moved_sum`: `moved` バケットの合計。
  - `key_presses`: 窓の中の press の数。
  - `cat_counts`: 窓の中の全 press を `KeyCategory` ごとに数えたもの（`BTreeMap<String,u64>`）。既存の `boundary.prev_cat_counts` は pause の直前と直後だけを数えるので、別物になる。
  - `ime_on_ms`: 窓の中で IME がオンだった時間。入力が既存のキー行や IME の行から作れるかは、実装の最初に確かめる。作れなければこの列は出さない（null にして `missing_reasons` に書く）。
- `W_ctx` は封筒の `config` に `context_window_ms` として出す。既定値は 120 000 ms とし、状態の 30 秒窓より遅い時間尺度にする。p1-episode の事前登録には載せない。載せると parity の 3 点更新が要り、P1 の契約を動かしてしまうため。
- 入力は `PoleInputs` と同じ形の `ContextInputs { focus_ts: Option<&[u64]>, pointer_bins: Option<&[PointerBinLite]> }` で渡す。replay.rs に `collect_focus_timestamps` と `collect_pointer_bins` を足す（既存の `collect_pointer_bin_timestamps`・`replay.rs:3165` と同じ形にする）。
- 欠測は 3 状態で分ける（既存の `pointer_applicability` と同じ規則）。
  - capabilities に宣言が無い → 列は null で `capability_undeclared`。
  - 宣言があって 0 行 → 0（測れて、無かった）。
  - `config_gated` で 0 行 → null（判定不能）。
- `context` は HMM・`FeatSnapshot`・`features.rs`・`engine.rs` へは流さない（ADR-014 D4b）。`schema_dto.rs` と `logger.rs` は変えないので、段 1 のアプリと NDJSON の形は不変になる。

### 層 2: 区間の境界・まとめ・判定（Python・`experiments/20261121-auto-context-segmentation/`）

1. **境界**: 2 種類の境界を合わせる。
   - 打鍵もポインタも無い時間が `G_idle`（既定 300 s）以上続いたところ。
   - 文脈の量の分布が前後の窓で変わったところ。前後 `W_cp` の窓で標準化した文脈ベクトルの差を測り、閾値 `τ_cp` を超えた極大を境界にする。
   - 長さ `L_min`（既定 120 s）より短い区間は隣の区間に吸収する。
2. **まとめ**: 人ごとに、区間を文脈ベクトルの平均（時間で重み付け）で表し、人の中で標準化する。混合ガウスで k = 1..6 を BIC で選ぶ。k = 1 も選べるようにする（分けられないという結果を許す）。
3. **名前**: 合計時間の多い順に `task-A`, `task-B`, … と付ける。宣言の名前（writing など）には写し替えない（ADR-012 D3）。
4. **判定**: 基準は `criteria.json` に書き、実データを処理するより前のコミットに入れる。
   - (a) 合成の陽性対照: 切り替えの時刻と文脈が分かっている NDJSON を `gen_synth.py` で作る（seed は固定）。
     - 境界の F1（許容 ±60 s）が 0.8 以上であること。
     - まとまりと真の文脈の ARI が 0.7 以上であること。
     - 陰性対照（文脈が 1 つだけの合成）で k = 1 になること。
   - (b) 宣言との照合（実データの全員）:
     - 宣言の切り替え時刻を境界がどれだけ拾うか（再現率・±120 s）。
     - 宣言の区間とまとまりの NMI。
     - どちらも、宣言の列をブロックごとに巡回させてずらした帰無分布と比べる（片側 p < 0.05）。
     - O1 は宣言が変わるとファイルが分かれる（`o1.rs:301`）ので、宣言の境界はファイルの境界と重なる。人ごとに、ファイルをまたいでまとめる。
   - (c) 循環の検査: まとまりと推定状態（`--snapshot` の HMM の最尤状態）の NMI を数える。これが (b) の NMI 以上なら、そのまとまりは「状態を写しただけ」と判定する。
   - (d) 本人の振り返り: 段 1 の本人の区間の一覧（時刻・長さ・名前・文脈の量の要約だけ。打鍵の中身は出ない）を研究者が見て、当時の作業と合っているかを区間ごとに付ける。宣言の無い区間を補うのに使う。
   - 結論は「使える／使えない／判定できない」の 3 値で書く。宣言がほとんど無い人は「判定できない」とし、無理に数えない。
5. **識別子の見積もり**: 結果の後で、識別子があれば (b) がどれだけ動きうるかを decisions.md に書く。フォーカス遷移が多いのに宣言の境界を拾えていない区間の割合などで見積もる。

## 変更対象

### 修正するファイル
- `src-tauri/src/analysis/feat_offline/mod.rs`: `FeatureRow` に `context` を足し、`ContextInputs` を追加し、構築箇所（`:496`）で計算を呼ぶ。
- `src-tauri/src/bin/replay.rs`: focus と pointer の収集関数を足し、封筒の `config.context_window_ms` を出す。CLI に `--context-window-ms` を足す（任意）。
- `src-tauri/src/analysis/feat_offline/quality.rs`: 欠測の理由語の許可リストを拡張する（要るときだけ）。
- `docs/glossary.md`: 「特徴行」の項に `context` を足し、共有禁止が及ぶことを書く。
- `docs/functional-design.md`: `--features` の `context` と、解析の層の位置づけを書く。

### 新規作成するファイル
- `src-tauri/src/analysis/feat_offline/context.rs`
- `src-tauri/tests/fixtures/context_switch.ndjson`: 文脈の切り替えを含む小さな fixture。
- `experiments/20261121-auto-context-segmentation/`: `run.sh`（Step 0 の capabilities_gate を含む）、`config.json`、`criteria.json`、`SEED`、`gen_synth.py`、`segment.py`、`cluster.py`、`evaluate.py`、`data.md`、`env.md`、`notes.md`。生成物は `results/` に置き、特徴行を含むものはコミットしない。

## 影響範囲

- 影響範囲の分析ではリスクは低いと出た。追加は additive で、段 1 のアプリから `feat_offline` への参照は 0 件。`HMM_VERSION` の bump は不要で、`--snapshot` のゴールデンは不変。
- 読み手（`scripts/p1_features_io.py`・`build_p1_episode_db.py`・`check_no_feature_output.sh`）は未知のキーに寛容。それでも、未知キーを拒まないことを実際に回して確かめる。
- `PoleInputs` のリテラル 5 か所は、`Default` で書かれているかを確認する。

## 既存パターンとの整合性

- 入力の渡し方・欠測の 3 状態・収集関数の形は、極 B のポインタの扱い（issue 006）に乗る。
- 既存の `--segment`（打鍵の沈黙だけで区間を切り、F/I/S を手で付ける）は残し、置き換えない。
- 観測から種別を作らない・融合しない（ADR-010 D3・ADR-012 D3）。宣言は照合にだけ使い、まとまりに宣言の名前を付けない。
- 実験は `experiments/_template` と reproducibility-discipline に従う。

## テスト戦略

- 単体テスト（`context.rs`）:
  - 窓の端（ちょうど `W_ctx` の境目）。
  - 欠測の 3 状態。
  - `cat_counts` の合計が `key_presses` と一致すること。
  - focus を 1 行足すと `focus_transitions` が 1 増え、他の列は動かないこと（陽性対照）。
- 統合テスト: `context_switch.ndjson` で `--features` を回し、切り替えの前後で `context` が変わること。旧ログ（capabilities が無いもの）では null になること。
- 回帰:
  - `cargo test --manifest-path src-tauri/Cargo.toml --workspace` が緑。
  - `gse-replay --snapshot` が `minimal.json` と byte-equal。
  - `check_no_feature_output.sh --self-test` が緑。
- 解析の層:
  - `evaluate.py --synthetic` の終了コードが 0。
  - 境界を消した合成では非 0 になること（壊して赤を見る）。
- 外部送信: Codex の `/cross-review` には Rust と Python の diff だけを渡す。記録・特徴行・結果は渡さない。

## ロールバック計画

- 層 1 は additive なので、`context` のフィールドと収集関数を revert すれば戻る。段 1 の配布物は触らない。
- 層 2 は experiments/ の中に閉じていて、他から読まれない。
