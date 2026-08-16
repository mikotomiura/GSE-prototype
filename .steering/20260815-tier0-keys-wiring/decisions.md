# 重要な設計判断 — Tier 0 配線

> ★ 本セッション（2026-08-15）で研究者が下した判断と、私が一次で閉じた判断を分けて記録する。

---

## 判断 1: Tier 0 配線を「記録のみ」として G1 完了前に先行させる ★★★ 研究者判断

- **判断日時**: 2026-08-15
- **背景**: ⚠️★★★ **既定の順序と正面から当たる。**
  - `docs/architecture/personalization-and-online-learning.md §10` 逐語:
    **「G1（統制タスク実験）は P1 より前——凍結解除後の最初のタスクに置く」**
  - `.steering/20260801-recovery-axis-grounding/tier0-wiring-design.md:85` 逐語:
    **「これは ADR-009 Migration P1『現行 X を置換せず並走』の実装形である」**
  - → ★ **Tier 0 配線 = P1**。★ そして **G1 は確証標本 3 名中 P010 の 1 名のみ実施済み**
    （★ 一次: `experiments/20260801-controlled-friction-task/README.md:24` ／ `results/` は `.gitkeep` のみ）。
- **選択肢**:
  - A: ★ **記録のみとして先行させる**（★ 順序の記述を改訂する）
  - B: G1 の残り 2 名を待つ
  - C: 設計だけ進めて実装は保留
- **採用**: ★ **A**
- **理由**:
  - ★★★ **順序が置かれた理由が Tier 0 に当たらない。** ADR-009 Migration 2 の逐語は
    **「ここで分離できなければ、パイプラインを作る前に軸そのものを疑う」**であり、
    ⚠️ **Tier 0 配線はパイプラインを作らない**（★ 原本 §2「記録するだけで HMM にも X/Y 合成式にも
    1 バイトも流さない」「新フィールドの消費者は将来の recovery 推定器のみ」）。
  - ★ **計測側を先に揃える方が G1 の残り 2 名にも利く**（★ 原本 §8-3: G1 の FS-B には Tier 1 の分布統計が要る）。
- **トレードオフ**: ⚠️ **既定の順序記述を改訂する必要がある**（★ 黙って上書きしない）。
  ⚠️ **軸そのものが G1 で否定される可能性は残る** —— その場合 `keys`/`bs_keys` は
  「記録したが誰も読まないフィールド」として残る（★ ただし additive なので害は無い）。
- **影響範囲**: `personalization-and-online-learning.md §10` の順序記述。★ ADR-009 本体は **改訂しない**
  （★ Proposed だが、D7 の「G1 は免除されない」という主張自体は変えない。★ 変えるのは P1 との前後関係のみ）。
- **見直しタイミング**: ★ **G1 の判定が出たとき。** ⚠️ 軸が否定されたら、新フィールドを読む実装へ進まない。

---

## 判断 2: gse-dataset 側の schema も同時に更新する ★★★ 研究者判断

- **判断日時**: 2026-08-15
- **背景**: ★ `scripts/check_schema_parity.py` は `/finish-task` Step 3 の tier-3 workflow guard であり、
  `schema_dto.rs` または `schema/current.json` に変更があると**必ず走る**。
  ★ 本変更は両方に触れるため **parity check が必ず発火する**。
- **選択肢**: A: ★ **両方やる** ／ B: 本 repo 側だけ ／ C: まず影響調査だけ
- **採用**: ★ **A**
- **理由**: ★ 片側だけ進めると `/finish-task` が Step 4 へ進まず停止する。★ **それが正しい挙動**であり、
  回避せずに両側を揃える。
- **トレードオフ**: ★ 2 repo にまたがるので、**マージのタイミングを近接させる運用が要る**。
- **影響範囲**: `C:\gse-dataset/schema/current.json`（★ 本機は HTTPS clone・SSH 未設定）。
- **見直しタイミング**: ★ dataset 側を CI で自動追随させる仕組みが入ったら。

---

## 判断 3: 案 B（`keys` ＋ `bs_keys` をともに整数）を採る ★ 原本の推奨を追認

- **判断日時**: 2026-08-15
- **背景**: ★ `f3 = correction_keys / total_keys` が既に `feat` 行にあるため、
  ★ 理屈上は `keys` 1 つで削除打鍵数を復元できる（`f3 × keys`）。
- **選択肢**: A: `keys` のみ ／ ★ **B: `keys` ＋ `bs_keys`** ／ C: ＋ `ime_dwell_med`
- **採用**: ★ **B**
- **理由**: ⚠️★★★ **`f3` は `{:.4}` で丸めて書かれている**（★ 一次: `logger.rs:1214` のフォーマット文字列）。
  ★ 丸め済みの値から `correction_keys` を復元すると**整数に戻らない**。
  ★ `progress_proxy` は **ADR-009 D2 の目的変数の構成要素**であり、⚠️ **そこに丸め誤差を持ち込みたくない**。
- **トレードオフ**: ★ `f3` との冗長性を許容する（★ `f3` は既存の本番経路が使用中なので**削除も変更もしない**）。
- **影響範囲**: schema の追加フィールドが 1 → 2 に増える（★ ともに `u64` で**浮動小数の再現性問題が無い**）。
- **見直しタイミング**: ★ Tier 1 を足すときに、フィールド構成をまとめて見直す。

---

## 判断 4: `FeatSnapshot` に含める ★ 原本 §8-2 の未決を一次で閉じた

- **判断日時**: 2026-08-15
- **背景**: ★ 原本 §8-2 は **「含めなければ golden 再生成が不要になるが、replay から recovery ラベルを
  作れなくなる → `gse-replay` の出力仕様を読んでから決める」**として保留していた。
- **選択肢**: A: ★ **含める**（★ golden 4 本の再生成が要る） ／ B: 含めない（★ 再生成不要）
- **採用**: ★ **A**
- **理由**: ★ 一次（`src-tauri/src/analysis/loop_step.rs:133` の doc コメント逐語）
  **「ゴールデンスナップショット (P0-10) の byte-equal 比較対象」**。
  ⚠️★★★ **含めないと `progress_proxy` が NDJSON にしか存在しない値になり、replay から再構成できない
  ＝ Replay-as-Truth が切れる。**
- **トレードオフ**: ★ **golden 4 本の再生成が必要**（★ 受け入れ条件で「差分が新フィールドの追加のみ」を強制する）。
- **影響範囲**: `tests/snapshots/minimal.json` / `phase1_ime_heavy.json` / `category_coverage.json` / `deep_silence.json`。
- **見直しタイミング**: ★ `FeatSnapshot` と NDJSON `feat` 行の形を分離する設計が出たら。

---

## ⚠️★★★ 実測 1: 既存の schema parity drift がある（★ 原本 memo が想定していない）

- **確認日時**: 2026-08-15
- **実測**:
  ```
  $ python scripts/check_schema_parity.py --dataset C:/gse-dataset
  [check_schema_parity] DRIFT detected between:
    A: C:\GSE-prototype\src-tauri\schema\current.json
    B: C:\gse-dataset\schema\current.json
  Missing variants in B: hook_health
  Extra variants in B:   (none)
  （＋ meta variant の g1_mode プロパティが B 側に無い）
  REAL EXIT=1
  ```
- ⚠️★★★ **`check_schema_parity.py` は意味的比較（改行コード・キー順を無視）なので、これは CRLF 起因ではなく本物の drift。**
- ★ **`C:\gse-dataset` の HEAD は `f3e8566 chore(schema): sync current.json — InterventionResponse Wall 応答 (Phase A2)`**
  で、★ その後に本 repo 側へ入った `hook_health` / `g1_mode` が**追随できていない**。
- → ★★★ **本タスクの additive 変更を入れる前に、この drift を先に解消して exit 0 に戻す。**
  ⚠️ **そうしないと「今回の変更で壊れたのか、元から壊れていたのか」が分離できない。**

## ⚠️ 実測 2: 参照の行番号がずれている / golden 本数が古い

| 記述 | 出所 | ★ 実測（2026-08-15） |
|---|---|---|
| `feat` 行の書き出しは `logger.rs:974` | `tier0-wiring-design.md:14` | ⚠️ **`logger.rs:1214`** |
| golden は **3 本** | `experiments/20260731-phase1-calibration-analysis/notes.md §5③` | ⚠️ **4 本**（★ `deep_silence.json` が増えている） |
| `f3 = correction_keys / total_keys` | `tier0-wiring-design.md:15` | ★ **維持されている**（`features.rs:146-152`）。⚠️ **ただし読んだのは 1 経路のみ** |
| `total_keys` はローカル変数で計算済み | 同 `:16` | ★ **維持**（`features.rs:146`）＝ **新規計算ゼロ** |

---

# ★ 実装セッション（2026-08-16）で追加した判断

## 判断 5: 打鍵数は「推論経路に依存しない実測値」を記録する ★ 実装時に浮上・一次で閉じた

- **判断日時**: 2026-08-16
- **背景**: ⚠️ 設計時に想定されていなかった分岐が実装で出た。
  `loop_step::step()` は 3 経路（TypingPath / TransitionPath / **SilencePath**）に分かれ、
  ★ **SilencePath は `make_silence_observation()` が返す「合成観測」を `log_features` に載せる**。
  ★ 合成観測は**打鍵を数えていない**ので、素直に `log_features.keys` を書くと
  ⚠️ **SilencePath の行だけ常に `keys=0`** になる。
- **選択肢**:
  - A: ★ **`calculate_features()` の実測値を退避し、経路に依らずそれを書く**
  - B: `make_silence_observation()` に打鍵を数えさせる（★ 窓の走査が二重になる）
  - C: `log_features` のまま（★ SilencePath で欠測が 0 に化ける）
- **採用**: ★ **A**
- **理由**: ★ **`keys` / `bs_keys` は特徴量ではなく「測った量」である。**
  ★ 推論経路（＝ HMM 側の都合）で記録値が変わるのは筋が悪い。
  ★ A なら**新規の走査ゼロ**（`calculate_features()` の戻り値を退避するだけ）で B のコストも避けられる。
  ⚠️ C は「実測 0 打」と「合成観測だから数えていない」を**同じ 0 で潰す**ので採らない。
- **トレードオフ**: ★ `Features` 構造体の `keys` フィールドが、SilencePath では
  「載らない値」になる（★ `make_silence_observation()` 側に doc コメントで明示し、テストで固定した）。
- **影響範囲**: `loop_step.rs` の `window_keys` / `window_bs_keys`、`features.rs` の合成観測。
- **見直しタイミング**: ★ `FeatSnapshot` と `Features` を型として分離する設計が出たら。

---

## 判断 6: `FeatSnapshot` には `#[serde(default)]` を**付けない** ★ 実装時に一次で閉じた

- **判断日時**: 2026-08-16
- **背景**: ★ 原本 §3 は「DTO 側は `Option<u64>` ＋ `#[serde(default)]`」と決めていたが、
  ⚠️ **`FeatSnapshot` は DTO ではなく「ゴールデンの byte-equal 比較対象」そのもの**である。
- **選択肢**: A: ★ **付けない** ／ B: 付ける（★ 欠けた golden を 0 で受ける）
- **採用**: ★ **A**
- **理由**: ★ golden 4 本は本コミットで**全部再生成する**ので互換の必要が無い。
  ⚠️ B だと、フィールドの欠けた golden を **`0` で黙って受けてしまう**（★ 全行 0 の golden では
  drift が素通りする）。★ `missing field` で落ちるほうが安全。
- **影響範囲**: `analysis/loop_step.rs` の `FeatSnapshot`。
  ★ 旧 NDJSON 互換は **`schema_dto.rs` と `bin/replay.rs` の DTO 層**が担う（★ 原本の意図どおり）。

---

## ⚠️★★ 判断 7: 旧 NDJSON の欠測を `0` に倒す（★ 妥協。研究者に判断を戻す）

- **判断日時**: 2026-08-16
- **背景**: ⚠️ **原本にも本タスクの設計にも書かれていなかった経路**が見つかった。
  ★ `bin/replay.rs` の **`LoggedFeatDto`** は、`--metrics` 経路で **production が書いた `feat` 行を
  そのまま読む**（★ `run_replay` の再生成ではなく、実ログを真実として使う経路）。
  ★ ここに Tier 0 配線**以前**の NDJSON が来ると、新フィールドが存在しない。
- **選択肢**:
  - A: ★ **`Option<u64>` で受けて `FeatSnapshot` では `0` に倒す**（★ 採用）
  - B: `FeatSnapshot` 側も `Option<u64>` にする（★ 欠測と 0 打を型で区別できる）
  - C: 欠測を Err にして弾く（⚠️ **既存 gse-dataset の全ログで `--metrics` が落ちる**ので不可）
- **採用**: ★ **A**（★ tasklist の「`FeatSnapshot` に `keys: u64` / `bs_keys: u64`」に従った）
- **理由**: ★ **現時点で新フィールドを読む消費者はゼロ**なので、実害が出るのは将来だけである。
  ★ B は `Option` を解析コード全体に伝播させるため、消費者が決まる前に払うコストとしては重い。
- ⚠️★★★ **残るリスク（研究者へ）**: ★ **「旧ログで欠測」と「実測 0 打」を `--metrics` 経路で
  区別できない。** ★ `progress_proxy` は ADR-009 D2 の目的変数の構成要素なので、
  **ここに黙って 0 が混ざるのは危険**である。
  → ★ 緩和として、`LoggedFeatDto` / `FeatSnapshot` / `§5.2` の 3 か所に注意書きを置き、
    後方互換テスト（`logged_feat_dto_accepts_legacy_line_without_tier0_fields`）で挙動を固定した。
  → ⚠️ **T0-Q5 として次に渡す**: 消費者を書く時に (i) `Option` へ格上げするか、
    (ii) ログの世代を別の手段で判定するか（★ `HMM_VERSION` は bump していないので判定材料にならない）。

---

## ⚠️★★★ 実測 4: `keys` は「今から遡る 30 秒窓」ではない（★ レビューで発覚・私の記述が誤っていた）

- **確認日時**: 2026-08-16（★ 一次: `features.rs` の `cutoff = last_ts.saturating_sub(30_000)`
  ＋ 実測: `tests/snapshots/deep_silence.json`）
- ⚠️★★★ **`last_ts` は「バッファ最後のイベント時刻」であって `now_ms` ではない。**
  ★ しかも `extractor.reset()` は **IME pause 遷移でしか呼ばれない**ので、通常の沈黙では
  バッファが残り続ける。→ ★ **沈黙が何秒続いても同じ窓・同じ値が毎秒書き出される。**
- ★ **実測**: `deep_silence` は `t=…008000` 〜 `t=…051000` の **44 行連続で `keys=12, bs_keys=2`**。
- ⚠️ **私が最初に書いた doc（「ウィンドウ内の総キー押下数」）とテスト名
  （`..._are_scoped_to_the_30s_window`）は、この事実を誤って伝えていた。**
  ★ そのまま golden と gse-dataset に焼き付いていたら、**`progress_proxy` を feat 行ごとに
  積分する消費者が同じ打鍵を数十回二重計上する**ところだった。
- ★ **対応**: 意味の正本を `loop_step.rs` の `FeatSnapshot::keys` doc に一本化し、
  ★ 解析側が読む `docs/development-guidelines.md §10.3.2` にも表で明記。★ 凍結挙動をテストで固定。
- ⚠️ **これは F1〜F6 が元から持つ性質**であり、本配線が作った挙動ではない。
  ★ ただし `keys` は**率でなく個数**なので、消費者にとっての危険度が段違いに高い。

---

## ⚠️ 実測 3: `keys` は IME ポーズ中の打鍵を数えない（★ 既存の窓を継承した性質）

- **確認日時**: 2026-08-16（★ 一次: `loop_step.rs` のイベント処理分岐）
- ★ `engine.get_paused()` が true の間、打鍵イベントは **`FeatureExtractor` に入れずに `return`** する。
  ★ したがって `keys` / `bs_keys` も **IME 変換中の打鍵を数えない**。
- ⚠️ これは F1〜F6 が既に持つ性質をそのまま継承したものであり、**本タスクが作った制約ではない**。
- ⚠️★ ただし **日本語入力主体のセッションでは `progress_proxy` が系統的に過小**になる。
  ★ 窓の定義を変えると特徴量が変わる＝ HMM 挙動が変わるので、**本タスクでは触らない**。
  → ★ `golden-regeneration.md` に記録。

---

## ⚠️ 私が本セッションで断定していないこと

- ★ **`keys`/`bs_keys` が recovery 予測に効くか** —— ⚠️ **本タスクは記録するだけで、1 文字も主張しない。**
- ★ **G1 の軸が分離可能か** —— ⚠️ **未判定（★ 3 名中 1 名実施済み・`results/` は空）。**
- ★ **`f3` の定義が全経路で同じか** —— ⚠️ **1 経路しか読んでいない。実装時に再確認する。**
