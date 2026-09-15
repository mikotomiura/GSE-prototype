# 重要な設計判断（★ grill で閉じた判断分岐・2026-09-14）

> ⚠️★★★ **ここに書いてあるのは「ADR で決まっていなかった分岐」だけ**である。
> ★ Tier の枠・投資順序・計器の仕切りは **ADR-030 D10 / D11 で accept 済み**なので蒸し返さない。

## 判断 1: 新しい特徴量計算の置き場

- **判断日時**: 2026-09-14（研究者採択）
- **背景**: ADR-030 D1 が「検出器は**オフライン側**に置く（`features.rs` / `engine.rs` を触らない）」と
  決めているが、**どこに置くか**は決まっていなかった。★ これが `## Allowed Files` の交差を決め、
  issue の並列可能性と DAG を左右する。
- **選択肢**:
  - A: `bin/replay.rs` に `--features` モードを増築し、計算本体は `analysis/feat_offline/tXX.rs` の純関数
  - B: 新規 bin `gse-features` を切る
  - C: `analysis/` にモジュールだけ置き、CLI は作らない
- **採用**: **A**
- **理由**:
  - ★ NDJSON の loader（`ReplayEvent`）は **`bin/replay.rs` 内の private 型**であり、B を採ると
    lib へ移す**先行リファクタが必須**になる。⚠️ そのリファクタはゴールデン回帰の前提を動かすので、
    「最初の単独ウェーブに置く」対象が 1 本増える。
  - ★ `--sweep` / `--nudge-diag` / `--corr-floor` という **同じ増築の前例が既にある**。
  - ⚠️ C は「新特徴が実際に出力に出ていること」を `acceptance.sh` で検査できない。
    ★ `loop-run.sh` のコメント逐語「**`cargo test` が無条件に緑になる issue では AC 未充足のまま
    `issue_done` になる**」に直撃する。
- **トレードオフ**: ⚠️ `bin/replay.rs`（約 3550 行）がさらに伸びる。
  ★ ただし増築はモード分岐 1 本ぶんで、計算本体は `analysis/` 側に閉じる。
- **影響範囲**: `src-tauri/src/bin/replay.rs` / `src-tauri/src/analysis/feat_offline/` / `analysis/mod.rs`
- **見直しタイミング**: ★ `replay.rs` のモードが増えすぎて分岐が読めなくなったとき（★ そのときは
  loader を lib へ出すリファクタを**単独の issue**として切る）

## 判断 2: `--features` の出力単位（＝ 標本の行）

- **判断日時**: 2026-09-14（研究者採択）
- **背景**: ADR-010 D4 が「**Decision Episode を標本単位に**」と決めているが、
  ⚠️ それは**モデルの標本単位**の話であり、**中間成果物である特徴行の粒度**は決まっていなかった。
- **選択肢**:
  - A: **1 Hz tick 単位**（既存 `FeatSnapshot` と同じ仮想時刻グリッド）
  - B: **Decision Episode 単位**（`t0` でアンカー）
  - C: 両方出す
- **採用**: **A**
- **理由**:
  - ★ 既存の `loop_step` の仮想時刻グリッドをそのまま使えるので、**`t0` 検出器が無くても
    `T0` / `T1a` / `T1b` / `T1c` / `Q` が独立に実装できる**。
  - ⚠️ B だと **全 issue が `t0` に直列化**し、DAG の最長 chain が 6 段になる。
    ★ かつ `t0` の定義は ADR-030 が **Proposed** なので、そこで詰まると全部止まる。
  - ★ episode への集約は **`t0` 検出器の issue が後から join する**形で足せる（★ 情報は失われない）。
- **トレードオフ**: ⚠️ 行数が増える（1 セッション = 秒数ぶんの行）。
  ★ ただし `metrics.json` のように共有するものではなく、**手元の解析用中間物**である。
- **影響範囲**: 全 issue の AC と `acceptance.sh`
- **見直しタイミング**: ★ episode 単位でしか計算できない特徴が必要になったとき

## 判断 3: `T1a` の「個人相対 surprise」の baseline

- **判断日時**: 2026-09-14（研究者採択）
- **背景**: ADR-030 D4 は **`θ_person` = 個人 × `task_kind` の分布の分位点**と定めているが、
  ⚠️ それは **`t0` 検出器の閾値**の話であって、`T1a` の surprise の baseline とは別物である。
- **選択肢**:
  - A: **セッション内**の分布からの逸脱
  - B: 個人 × `task_kind`（複数セッション入力）
  - C: `T1a` から surprise を外す
- **採用**: **A**
- **理由**:
  - ★ 単一 NDJSON で完結するので、**既存 fixture 13 本で `acceptance.sh` が書ける**。
  - ⚠️ B は **O1 が未配布で実データが無い**（★ 手元は合成 fixture のみ）。
    ★ 複数セッションを組む検査になるが、それは**合成データ上の形式検査**にしかならない。
  - ⚠️ C は ADR-030 D10 の `T1a` の定義から 1 項目欠けることになる。
- **トレードオフ**: ⚠️★★★ **「本人の平常時」ではなく「このセッションの平常時」になる。**
  ★ 後で個人 baseline へ差し替えると **`T1a` の AC を書き直すことになる**。
  → ★ **issue 002/003 の `## Stop Conditions` に「個人 baseline へ差し替える判断が出たら止める」を書く。**
- **影響範囲**: `analysis/feat_offline/t1a.rs` とその acceptance
- **見直しタイミング**: ★ O1 の実データが届き、個人 × `task_kind` の分布が推定できるようになったとき

## 判断 4: `capability matrix` を Loop に載せない

- **判断日時**: 2026-09-14（研究者採択）
- **背景**: ADR-032 **M7** が `capability matrix`（`OS × ライブ変換設定` で層別）を
  「★ タスク 2 の成果物に含める」と書いている。⚠️ しかし中身は**一次資料の読み込みと判断**であり、
  `cargo test` が無条件に緑になる。
- **選択肢**:
  - A: **実装 issue だけ Loop、matrix は対話で行う**
  - B: matrix も Loop に載せ、`acceptance.sh` を厳しく書く
  - C: matrix を先に対話で作ってから、残りを分解し直す
- **採用**: **A**
- **理由**: ★ 無人 worker は「一次資料を読んで可否を裁く」作業に向かない。
  ⚠️ B の `acceptance.sh` は「**行があること**」しか検査できず、
  ★ 中身が正しいことを担保できない（＝ 客観に見えて無意味な緑）。
- **トレードオフ**: ⚠️ matrix が閉じるまで **ADR-032 の未決 ④ / ⑤ と起票 21 が開いたまま**残る。
- **影響範囲**: `issues/` に matrix の issue を置かない（★ `_issue-plan.md` に「Loop 外」として明記する）
- **見直しタイミング**: —

## 判断 5: `capability matrix` の実証範囲

- **判断日時**: 2026-09-14（研究者採択）
- **背景**: ADR-032 D5 は「**先に測れ**」と命じ、`OS × ライブ変換設定` の層別を要求する。
  ⚠️ しかし **O1 は未配布で実データが 1 本も無い**（★ 手元の fixture は合成 13 本）。
- **選択肢**:
  - A: **現行 schema の静的分析 ＋ 既存 fixture での実測 replay ＋ 起票 6 の既測結果の引用**
  - B: macOS 実機でライブ変換 ON/OFF の新規 fixture を取ってから判定
  - C: 表の枠だけ作り、判定は O1 データ受領後
- **採用**: **A**
- **理由**: ★ 実機作業なしで今日閉じられ、⚠️ `ADR-032 D5` が求める
  「作れる / 作れない / 粒度が足りない」の 3 値判定はこの範囲で出せる。
  ★ macOS ライブ変換の歪みは **2026-09-12 に実測済み**（起票 6）であり、引用できる。
- **トレードオフ**: ⚠️★★★ **合成 fixture 上の判定であることを表に明記する。**
  ★ 実データでの再判定が要る項目は「**要再判定**」と書く（⚠️ 「作れる」と断定しない）。
- **影響範囲**: `docs/architecture/` に置く matrix 文書
- **見直しタイミング**: ★ O1 の実データが届いたとき

## 判断 6: DAG は直列にする（★ Allowed Files が `mod.rs` で交差するため）

- **判断日時**: 2026-09-14
- **背景**: 各 Tier の issue は自分の `tXX.rs` を作るが、**`feat_offline/mod.rs` に
  `pub mod` と行構造体のフィールドを足す**ため、Allowed Files が必ず交差する。
- **選択肢**:
  - A: **直列化する**（`## Dependencies` で chain にする）
  - B: issue 001 が全 Tier の**空のプレースホルダ**を先に作り、以降は自分のファイルだけ触る
  - C: registry / マクロで動的登録にして交差を消す
- **採用**: **A**
- **理由**:
  - ★ 引き継ぎ §6 が **初回は `budget.parallel: 1`** と指示しており、直列でも実時間の損が無い。
  - ⚠️ B は issue 001 が 10 ファイルに膨らみ、**基準 2（≤ 5 ファイル）を超える**。
    ★ かつ 001 は「**最も安い issue 1 本を parallel=1 で回して基盤を検証する**」の対象なので、
    そこを一番大きくするのは目的に反する。
  - ⚠️ C は本タスクの目的（特徴量）と無関係な機構を足す。
- **トレードオフ**: ⚠️ DAG の最長 chain が 7 段になり、実時間は長い。
- **影響範囲**: `_issue-plan.md` の交差表と DAG
- **見直しタイミング**: ★ 2 回目以降のタスクで並列度を上げたくなったとき（★ そのとき初めて B / C を検討する）

## 判断 7: pause 閾値の SSOT を `features.rs` に命名する（★ issue 001 の停止を解く裁定）

- **判断日時**: 2026-09-15（Opus 裁定セッション）
- **背景**: issue 001 が Loop モード C で **6 attempt すべて `acceptance_fail` → `abandoned`**
  （`_loop-run-report.md`: $3.528222 / 7,792,190 tokens・実装コミットはゼロ）。
  worker は **AC 6「pause 閾値は `features.rs` の既存定数を参照する」の参照先が存在しない**ことを理由に、
  issue 001 の Stop Conditions 3 番目に該当すると判断して停止した（★ 判断自体は正しい）。
- ⚠️★★★ **引き継ぎメモの前提のうち 3 件が一次資料で成立しなかった**（★ 2026-09-15 に本文で確認）:
  1. 「生リテラル 2000 が **4 箇所**・一本化する」→ ⚠️ **同じ概念ではない**。
     pause 閾値は `features.rs:221`（F5）/`:233`（F6）の 2 箇所（`// TUNE: ポーズ判定閾値 2000 ms (F5, F6 共通)`）。
     `:133` の `ft < 2000.0` は **F1 Flight Time の外れ値キャップ**、`:281` の `f1 = 2000.0` は**その飽和値**で、
     値が同じだけの**別 knob** である。★ 一方 **worker も引き継ぎメモも見落としていた 5 箇所目**があり、
     `make_silence_observation` の `silence_secs < 2.0`（doc 逐語「ポーズとして認識しない」）は
     **秒で表した同じ閾値**である。
  2. 「案2 なら `features.rs` に触れずに済む」→ ⚠️ **成立しない**。`intervention.rs:7` は
     `const SHORT_PAUSE_MIN_MS`（**`pub` が無い**）。参照するには `pub` 化＝ Allowed Files 外の変更が要る。
  3. 「案2 = ADR-030 に一文追記して裁定」→ ⚠️ **規約違反**。ADR-030 ヘッダ逐語
     「**本 ADR は既存 ADR の本文を 1 文字も書き換えない。改訂は番号の大きい ADR が上書きする**」。
- **選択肢**:
  - A: `features.rs` の pause 閾値を **`pub const` に命名**し（値は不変）、オフライン側がそれを参照する
  - B: `intervention.rs::SHORT_PAUSE_MIN_MS` を `pub` 化して転用する
  - C: AC 6 を撤回し、`T0` から `pauses` を落とす
- **採用**: **A**（⚠️ ただし**実施主体は Loop ではなく本セッション**。下記トレードオフ参照）
- **理由**:
  - ★★★ **ADR-030 D1 は命名だけの最小リファクタを禁じていない**（★ 本文で確認・推測していない）。
    D1 が決めているのは**検出器の設置場所**（逐語「`stall onset` の検出と `Decision Episode` の生成は…
    `metrics.rs` 系の純粋関数に置く」）であり、`features.rs` を避ける理由は逐語
    「**`features.rs` に入れると `HMM_VERSION` bump ＋ ゴールデン再生成が要る**」である。
    ★ A7 の却下対象も「検出器を `features.rs` に入れて**オンライン化**する」。
  - ★ `engine.rs:28-37` の bump 規則の逐語は「`phi` / `make_silence_observation` /
    `calculate_features` の**数値挙動変更**」。`u64` の `>= 2000` を同値の定数へ置き換える操作は
    これに当たらない（★ `engine.rs:19-26` が定数抽出を禁じているのは **EWMA α 系だけ**で、
    理由は `1.0 - 0.3 ≠ 0.7` という IEEE754 の ULP 問題＝**浮動小数経路に限る**）。
    → ★ **実測で確認した**（下記「検証」）。⚠️ 予測で済ませていない。
  - ★ **先例が在る**: `intervention::AWAY_IDLE_MS`（doc 逐語「唯一の真実源 (SSOT) である…
    別の場所で 180_000 を再定義しないこと」）→ `OutcomeConfig::away_gap_ms` が参照し、
    回帰テスト `away_gap_default_matches_intervention_ssot` が結合を固定（ADR-024 D3 / AC-3）。
    ★ 本判断は**同じ型**を pause 閾値に適用しただけで、新しい機構を作っていない。
  - ⚠️ B は意味論が違う（`SHORT_PAUSE_MIN_MS` は Nudge の機会バケットの下限・`intervention.rs:410-444`）。
    ★ Nudge を再チューニングすると **`T0` の特徴定義が黙って変わる**。
  - ⚠️ C は ADR-030 **D10 の `T0` ブロック**（逐語「keys / delete / paste / mean IKI / **単純 pause** /
    net production」）から 1 項目落とすことになり、**D11 が「計器変更不要」と実測した範囲**を自ら狭める。
- ★★★ **実施主体を Loop にしない理由**（⚠️ 引き継ぎメモの案1 は「先行 issue 000 を切る」だった）:
  - ⚠️ `docs/loop-engineering.md` の issue-slicing 基準 1 逐語「**層別の横切り分割は禁止**」。
    命名のみのリファクタ issue は**縦切りではない**。
  - ⚠️ `_issue-plan.md §8` の自己検査「**AC が書けない『リファクタするだけ』の issue を作っていないか → 無し**」を
    自分で破ることになる。
  - ★ 5 行の変更に worktree 1 周（前回 **$3.53**）を使う理由が無い。
  - → ★ **本セッション（Opus・設計裁定の主体）が直接実装し、issue 001 の Allowed Files は変えない。**
    ⚠️ issue 001 の Out「`features.rs` の変更」は **worker に対する制約として維持する**。
- **実装**（★ 2026-09-15・commit は本タスクブランチ）:
  - `features.rs` に `pub const PAUSE_THRESHOLD_MS: u64 = 2_000;` を追加（★ doc に SSOT 宣言）。
  - 参照先は **F5（`:221`）と F6（`:233`）の 2 箇所のみ**。
    ⚠️ `:133` / `:281`（F1 キャップと飽和値）は**別 knob なので触らない**。
  - ⚠️ `make_silence_observation` の `silence_secs < 2.0` は **定数から導出しない**
    （★ 当該関数は `engine.rs` の bump 対象に名指しされており、かつ浮動小数経路）。
    → ★ 代わりに回帰テスト **`features::tests::pause_threshold_matches_silence_gate`** が結合を固定する。
- **検証**（★ 実行した。⚠️ 予測ではない）:
  | pin 済み verify | 結果 |
  |---|---|
  | `cargo test --manifest-path src-tauri/Cargo.toml --workspace` | **exit 0**（**671** passed / 0 failed。★ ベースライン 670 + 新規テスト 1） |
  | `cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json` | **exit 0**（`OK: 15 snapshots match`。⚠️ 既存の `hmm_version 0.2.0 / engine 0.5.0` WARN も**ベースラインと同一**） |
  | `cargo clippy --manifest-path src-tauri/Cargo.toml --workspace --all-targets -- -D warnings` | **exit 0** |
  → ★ **`HMM_VERSION` は bump しない**（0.5.0 のまま）。★ ゴールデンは再生成していない。
- **トレードオフ**:
  - ⚠️ `features.rs` に 1 定数ぶんの公開面が増える（★ `analysis::feat_offline` から `use` される）。
  - ⚠️★★★ **SSOT は完全ではない** —— `silence_secs < 2.0` は**リテラルのまま残している**。
    ★ 「テストで結合を固定した」が「1 箇所に統合した」ではない。⚠️ **未統合であると明記する。**
  - ⚠️ `:133` / `:281` の `2000` は**別 knob として残る**。★ 将来 F1 キャップを触る人が
    pause 閾値と混同しないよう、定数の doc に明示した。
- **影響範囲**: `src-tauri/src/analysis/features.rs` / issue 001 の AC 6 と `001-acceptance.sh` /
  後続 issue 002〜006（★ 共有ヘルパ経由で同じ定数に乗る）
- **見直しタイミング**: ★ `make_silence_observation` を触る改修が別途発生したとき
  （★ そのとき `silence_secs` 側も定数から導出し、SSOT を完成させる）

### ⚠️★★★ 裁定と別に記録する（★ モードC の運用上の発見・次回の分解へ）

1. ⚠️ worker が issue.md の `Status` を `blocked` に書いても **`loop-run.sh` の events には伝わらない**
   （★ モードC の原則「events を書くのは script だけ」の帰結）。
   → **同じ理由で 6 回リトライされ `max_attempts` 到達まで $3.53 を消費した**。
   ★ fingerprint は 6 回とも異なり `no_progress_stop` は発火しなかった。
2. ★ 対策候補（⚠️ 本裁定の範囲外・起票のみ）: **Stop Conditions が前提にしている事実**
   （今回なら「pause 閾値の named constant が存在するか」）を **`acceptance.sh` で先に機械検査**しておけば、
   1 attempt 目の `acceptance_fail` の中身から気づけた。
3. ⚠️★★★ **`001-acceptance.sh` の AC 6 検査には穴があった**（★ 2026-09-15 に発見・本コミットで塞いだ）——
   `const NAME: ... = <数値>` の**宣言**しか見ておらず、**`>= 2000` と直書き**されたら**緑のまま通る**。
   → ★ 「新しい定数が無い」の否定形に加えて、**`PAUSE_THRESHOLD_MS` を実際に参照している**という
   肯定形と、**`feat_offline/` 配下に `2000` リテラルが無い**ことを足した。

## 判断 8: issue 001 は Loop の外（裁定セッション）で仕上げる ＋ `recheck` の watchdog を当てにしない

- **判断日時**: 2026-09-15（Opus 裁定セッション）
- **背景**: 判断 7 の後に issue 001 を再実行したところ、⚠️ **attempt 1 / 2 とも `max_turns`（30）到達**で
  打ち切られつつ実装は積み上がり、`run_verify` は通過した。★ しかし **watchdog が 2 回連続で空応答**を返し、
  `loop-run.sh:238-241` の fail-closed で `blocked` になった（tokens 9,050,167 / cost **$3.604688**）。
  ⚠️ `loop-run.sh:243-246` 自身が逐語「**`recheck` の watchdog は現状まだ完全に信頼できる gate ではない。
  空応答を返すことがある**」「**AC を機械的に検査できるなら `<id>-acceptance.sh` を書くほうが確実**」と明記している。
- **選択肢**:
  - A: **裁定セッションが客観再検証し、レビュー指摘を直して仕上げる**（★ Loop の残り attempt を使わない）
  - B: `max_turns` を上げて 3 回目を回す
  - C: `verify_level` を `parse` に落として回し直す
- **採用**: **A**（⚠️ C の「acceptance を厚くする」部分は**併せて採る**）
- **理由**:
  - ★★★ **watchdog がやるはずだった「客観再検証」を、より強い検査主体が実際に行える**。
    ★ 実測で pin 済み verify 4 本 ＋ acceptance ＋ **AC 対応 test を名前指定**で緑を確認した。
  - ⚠️★★★ **緑は「正しい」を意味しなかった** —— `code-reviewer` / `security-checker` を並列起動したところ、
    **HIGH 相当が 3 件**出た（下記）。★ B / C で回し直しても、**この 3 件は acceptance が検査していない以上
    緑のまま通る**（＝ attempt を増やしても見つからない）。→ ★ **検査を足すことが先**である。
  - ⚠️ B は $3.5/回 を追加で払って `max_turns` の当て推量を試すことになる。
- **レビューで出た HIGH 3 件（★ すべて一次資料で再確認してから直した）**:
  1. ⚠️★★★ **AC 6 の実質違反**: `feat_offline/mod.rs` に `pub const TICK_MS: u64 = 1000;`
     （`loop_step.rs:40 ENGINE_TICK_MS` の再宣言。★ doc 自身が「同じ」と書いていた）。
     → ★ **私が判断 7 で AC 6 検査を `activity.rs` に絞った**（誤検出を恐れて範囲を狭めた）ことが原因。
     ⚠️ **範囲を狭めた判断が、まさにその抜け穴を作った。** → 検査を `feat_offline/` 全体へ広げ、
     `ENGINE_TICK_MS` 参照の**肯定形**も足した。
  2. ⚠️★★★ **時刻スパンに比例した確保**: tick 数は入力バイト数でなく**時刻スパン**に比例するので
     `MAX_SESSION_BYTES` では防げない。★ **実測: 251 バイト・2 行の NDJSON（`t=0` と `t=1e8`）で 100,001 行**。
     ADR-030 **D9**（壁時計の前方跳躍）で現実に発火する。→ `MAX_FEATURE_TICKS` で `Err`。
     ⚠️ ギャップを `saturating_sub` で潰さない（D9 の危険側に落ちる）。
  3. ⚠️ **`pastes` が恒常 0**: `collect_paste_events` は `--metrics` 用で文字数欠落行を落とすため、
     `minimal.ndjson:22` の paste が 1 件も数えられていなかった（★「paste が無い」と「文字数が取れない」の混同）。
     → `collect_all_paste_timestamps` を追加。
  ★ 併せて `t_ms` を**絶対 epoch ms** に変更（⚠️ 相対だと判断 2 の「後から join できる」が出力単体で成立しない）。
- **acceptance の強化（★ 検査自体を実測で試した）**: ① 定数宣言の禁止を `feat_offline/` 全体へ ＋
  ② `ENGINE_TICK_MS` 参照の肯定形 ＋ ③ **出力キー集合の完全一致**（⚠️ 将来 `window_title` 等が増えたら落ちる）
  ＋ ④ `pastes` 総和 > 0 ＋ ⑤ **巨大時刻ギャップ入力で exit ≠ 0**。
  ★ ルール 5b に従い、**旧実装（`TICK_MS` あり）で落ち、現行で通り、余計なフィールド追加を弾く**ことを実際に試した。
- **トレードオフ**:
  - ⚠️★★★ **Loop の自律性は今回実証されなかった** —— ★ 2 回とも人が引き取っている。
    ★ ただし**実装の大枠（363 行）は worker が書いた**もので、人が足したのは修正と検査である。
  - ⚠️ `events.jsonl` に `issue_done` が**書かれていない**（★ script だけが書く規約を破らない）。
    → ★ **issue 002 以降の `deps_met` が満たされない**。⚠️ 手で `issue_done` を捏造しない。
    → ★ 対処は「**002 の `## Dependencies` から 001 を外す**」（★ コード上の依存は **merge 済み**で満たされている）。
      ⚠️ 外すときは `_issue-plan.md` の DAG も同時に直すこと。
- **影響範囲**: `issues/001.md`（Status: done ＋ Execution Result）/ `001-acceptance.sh` /
  `src-tauri/src/analysis/feat_offline/` / `src-tauri/src/bin/replay.rs` / commit `061e6fb`
- **見直しタイミング**: ★ watchdog の空応答が直ったとき（★ そのとき `recheck` を再び当てにしてよい）

### ⚠️★★★ 次に Loop を回す前に決めること（★ 未決・起票）

1. ⚠️ **`headless.max_turns: 30` が足りているか** —— ★ 002〜007 も同程度の規模なら、
   毎 attempt が途中で切れる。★ 上げるか、issue をさらに小さく切るかを決める。
2. ⚠️ **`verify_level: recheck` を 005 / 007 でどうするか** —— ★ watchdog が空応答を返す限り、
   `recheck` は「必ず最後に blocked になる門」である。★ `parse` ＋ 厚い `acceptance.sh` ＋
   **人のレビュー**に寄せるのが現実的（★ `loop-run.sh` 自身の推奨と同じ）。
3. ⚠️ **`permission_denials` の中身は今回も未検証**（★ 前回の引き継ぎ §1b と同じ）。
   ★ `loop-run.sh:342` の `res` を保存する改修を先に入れないと、何が拒否されたか永久に分からない。
