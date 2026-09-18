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

## 判断 9: issue 002 の `## Dependencies` から `001` を外す

- **判断日時**: 2026-09-15（Opus 裁定セッション・2 回目）
- **背景**: 判断 8 のとおり issue 001 は Loop の外で仕上げたため、`_loop-events.jsonl` に
  **`issue_done` 行が 1 行も無い**（★ 実測: event 値の内訳は
  `abandoned 1 / acceptance_fail 6 / attempt_start 18 / blocked 2 / test_fail 1`。`issue_done` はゼロ）。
- **一次資料で確かめたこと**（⚠️ 引き継ぎメモを根拠にしていない）:
  - `scripts/loop-run.sh:435-448` `preflight_dag` は、`## Dependencies` の依存先が
    **`--issues` で選んだ集合 `$ALL` に無ければ `die` する**（逐語「issue $id の依存 $d が issues/ に存在しません」）。
  - 同 `:422-431` は events から `issue_done` の issue だけを `DONE_IDS` に seed する。
    → ★ 001 を `--issues` に含めても `deps_met` は満たされず、**001 が再実行される**。
  - コード上の依存は満たされている（`src/analysis/feat_offline/mod.rs` は commit `061e6fb` で main 側に在る）。
- **採用**: **002 の `## Dependencies` を「なし」にする**（★ 003→002 以降の直列は維持する）。
  ⚠️ `_issue-plan.md §2` の DAG 図も同時に直す（★ 片方だけ直さない）。
- ⚠️ **却下**: events.jsonl に手で `issue_done` を書く。
  → ★ モードC の原則（`docs/loop-engineering.md` 逐語「events の writer は … モードC = `scripts/loop-run.sh` **だけ**」）を破る。
- **影響範囲**: `issues/002.md` / `_issue-plan.md §2`

## 判断 10: `headless.max_turns` を 30 → 60 に上げる

- **判断日時**: 2026-09-15（Opus 裁定セッション・2 回目）
- **背景**: 判断 8 の未決 1。★ 実測（`_loop-events.jsonl`）: issue 001 は
  **`max_turns 到達 (attempt 打ち切り)` を 4 回**記録している（1 回目の run で 1 回・2 回目の run で 3 回）。
  ⚠️ 打ち切られても実装は積み上がるが、次 attempt は**毎回ゼロから文脈を読み直す**ぶんだけ無駄になる。
- **一次資料で確かめたこと**:
  - `loop-run.sh:335-341` は `--max-turns "$MAX_TURNS"` と **`--max-budget-usd "$MAX_USD"` を
    1 attempt ごとに渡している**。→ ★ **真の上限は turn 数ではなく `max_budget_usd: 5.0` / attempt** である。
  - 実績: run1 = 6 attempt / **$3.528222**（≈ $0.59 / attempt）、run2 = 3 attempt / **$3.604688**（≈ $1.20 / attempt）。
    → ★ `$5.0 / attempt` の天井には**一度も当たっていない**。turn 数を倍にしても天井は動かない。
- **採用**: **`max_turns: 60`**（`max_budget_usd: 5.0` は据え置き）。
- **理由**: ★ 002〜007 の 1 本あたりの作業は「ADR/issue を読む → 1 モジュール ＋ 単体テストを書く →
  `cargo test` を数回回す」で、**cargo の 1 回が数 turn**を食う。30 では読み込みだけで尽きる実測がある。
  ⚠️ 費用側は turn ではなく `max_budget_usd` が押さえているので、turn を絞る意味が薄い。
- **トレードオフ**: ⚠️ 1 attempt の最悪費用が上がる（理論上 $5.0 まで）。
  ★ ただし `budget.max_attempts: 6` と `no_progress_threshold: 4` は据え置きなので、issue 1 本の上限構造は変わらない。
- **影響範囲**: `_loop-config.json`

## 判断 11: `verify_level: recheck`（005 / 007）を `parse` に落とし、客観再検証は本セッションが担う

- **判断日時**: 2026-09-15（Opus 裁定セッション・2 回目）
- **背景**: 判断 8 の未決 2。★ 実測で watchdog は **2 回連続で空応答**を返し、
  `loop-run.sh:238-241` の fail-closed で `blocked` になった。
- **一次資料**（⚠️ 引き継ぎメモではなくスクリプト本文）: `loop-run.sh:243-246` 逐語
  「**`recheck` の watchdog は現状まだ完全に信頼できる gate ではない。空応答を返すことがある**」
  「**AC を機械的に検査できるなら `<id>-acceptance.sh` を書くほうが確実**」。
  ★ `:377-381` のとおり `recheck` は **verify が緑になった直後に必ず通る門**なので、
  空応答が出る限り「最後に必ず `blocked` になる門」である。
- **採用**: **005 / 007 を `parse` にする ＋ `acceptance.sh` を厚くする ＋ 本セッションが客観再検証する**。
  ★ 客観再検証の中身は判断 8 の A と同じ: pin 済み verify 4 本 ＋ `<id>-acceptance.sh` ＋
  `code-reviewer` / `security-checker` の**並列**起動。
- ⚠️ **これは基準 5 の緩和ではない**。`docs/loop-engineering.md` の基準 5（AC 直結 / security /
  公開 API に触れるなら `recheck`）が要求しているのは**独立再検証があること**であって、
  **watchdog であること**ではない。★ 再検証の主体を「動かない Haiku watchdog」から
  「実際に走る Opus セッション ＋ 機械検査」へ移す。
  ⚠️★★★ **だから「レビューを省いてよい」とは読まない** —— ★ 005 / 007 は
  merge 前に**必ず** `code-reviewer` ＋ `security-checker` を通す（★ 007 は data-privacy に触る）。
- **見直しタイミング**: ★ watchdog の空応答が直ったとき
- **影響範囲**: `issues/005.md` / `issues/007.md` の `verify_level:` 行 / `_issue-plan.md §6`

## 判断 12: ⚠️★★★ issue 002 / 007 の AC は**実在しない前提**に乗っていた（★ 実行前に潰す）

- **判断日時**: 2026-09-15（Opus 裁定セッション・2 回目）
- **背景**: 判断 7 の「モードC の運用上の発見 2」が起票したこと —— 逐語
  「**Stop Conditions が前提にしている事実を `acceptance.sh` で先に機械検査しておけば、
  1 attempt 目の `acceptance_fail` の中身から気づけた**」—— を、**回す前に**全 issue へ適用した。
  ★ その結果、issue 001 と**同じ失敗様式が 2 件**見つかった。
- **実測（⚠️ 予測ではない・すべて一次資料）**:

  | # | issue | AC の前提 | 実体 |
  |---|---|---|---|
  | 1 | **002** | AC1/AC5 が `ime_dwell_ms` / `ime_nav` / `ime_abandon` を要求 | ⚠️ `bin/replay.rs:159` の `ImeShadow` は **`serde_json::Value` の読み飛ばし専用**（doc 逐語「replay では読み飛ばす」）。★ `build_feature_rows(keys, paste_ts, max_ticks)` に IME は**入っていない**。⚠️ かつ **`bin/replay.rs` は 002 の Allowed Files に無い** |
  | 2 | **002** | AC5 が `argumentative_ime_mixed.ndjson` で `ime_dwell_ms` 総和 > 0 を要求 | ⚠️★★★ **`tests/fixtures/` のどの `.ndjson` にも `ime_shadow` 行が 1 本も無い**（実測: 全 fixture を grep して 0 件）。★ 当該 fixture の行種は `key 244 / ime_state 3 / meta 2 / session_start 1 / session_meta 1` |
  | 3 | **007** | AC1 が `capabilities` / `hook_health` を要求 | ⚠️ `capabilities` は **`meta` 行のフィールド**（`logger.rs:1628`・ADR-013 D1）だが、`ReplayEvent::Meta`（`replay.rs:91-97`）は `session_start` / `session_end` / `hmm_version` **しか持たない**。`HookHealth` も読み飛ばし専用。⚠️ `bin/replay.rs` は 007 の Allowed Files に無い |
  | 4 | **007** | AC6 が `minimal.ndjson` で `capabilities` 非 null を要求（★ 検査の fail 文言は逐語「minimal.ndjson は meta 行を持つ」） | ⚠️★★★ **`minimal.ndjson` の meta 行は `session_start` / `hmm_version` だけ**で、`capabilities` も `app_version` も**無い**（★ ADR-013 D1 より前の形式）。★ `hook_health` 行も全 fixture にゼロ |

  → ★★★ **どちらも「AC が参照する対象が存在しない」**。issue 001 の AC 6（`features.rs` の
  pause 閾値の named constant が無い）と**同一の失敗様式**であり、放置すれば
  **worker が Stop Condition に当たって止まるか、Allowed Files を破る**かのどちらかになる。
  ⚠️ 前者は 1 issue あたり **$3.5 前後**を捨てる（★ 001 の実績）。

- **選択肢**:
  - A: **Allowed Files に `bin/replay.rs` を足し**、欠けている fixture を**裁定セッションが作る**
  - B: AC から IME / `capabilities` / `hook_health` を落として issue を痩せさせる
  - C: 配線だけの先行 issue を切る
- **採用**: **A**
- **理由**:
  - ★★★ **ADR-030 D11 の「計器変更不要」は成立している** —— ⚠️ D11 が言う「計器」は
    **`logger.rs` が行を書き出すか**であり、`logger.rs:478` は `ime_shadow` を、`:1986` は `hook_health` を、
    `:1628` は `capabilities` 入りの `meta` を**実際に書いている**。
    ★ 欠けているのは**オフライン読み出し側**であって、計器ではない。
    → ★ 本タスクが作っているのは**まさにそのオフライン読み出し側**なので、配線は各 issue の縦切りの中身である。
  - ⚠️ B は 007 をほぼ空にする（★ `Q` の中身は `capabilities` / `hook_health` / `dropped` という
    **計器側の事実**そのものであり、ADR-030 D10 の囲みが名指ししている）。
  - ⚠️ C は `docs/loop-engineering.md` 基準 1 逐語「**層別の横切り分割は禁止**」に反する（★ 判断 7 と同じ理由）。
  - ★ **並列度は失われない** —— `_issue-plan.md §3` のとおり **並列可能な組は元々 1 つも無い**
    （交差の実体は `feat_offline/mod.rs` 1 本）。`bin/replay.rs` を足しても DAG は変わらない。
- **`bin/replay.rs` に付ける制約**（⚠️ 無制限には開けない）:
  - ★ 触ってよいのは **`--features` 経路**と **`ReplayEvent` への行型/フィールド追加**、
    および **新しい `collect_*` 関数の追加**だけ。
  - ⚠️★★★ **`--snapshot` / `--metrics` / `--calibration` / `--sweep` 経路を変更しない**
    （★ ゴールデン 15 本は pin 済み verify の `test` に載っており、壊せば必ず赤になる）。
  - ⚠️ `HMM_VERSION` を bump しない / ゴールデンを再生成しない（★ 引き継ぎ §6 の継続）。
- **fixture は裁定セッションが作る**（★ 判断 7 と同じ理由 —— 前提の整備は縦切りではない）:
  - ★ 新規 `src-tauri/tests/fixtures/instrument_rich.ndjson`（**62 行**・合成）。
    ⚠️ 既存 fixture は **1 本も書き換えていない**（★ ゴールデン 15 本の入力を動かさないため）。
  - ★ 中身は **`logger.rs` の実際の出力書式に合わせた**（⚠️ 推測で組んでいない）:
    `meta`（`capabilities` ＋ `app_version` 入り・`capabilities.rs::capabilities_json` の 3 群と同じ形）/
    `session_meta`（`task_kind=argumentative`）/ `ime_shadow`（`logger.rs:478` 逐語書式・
    `dwell_ms` 650 と 920・`nav` 2 と 3・`abandon` false と true）/
    `hook_health`（`logger.rs:1986` 逐語書式・`dropped_delta` 付き）/ `paste` /
    2 本の pause（**2650 ms** と **7550 ms**）/ backspace 3 連（delete run）/
    `188`（`,`）と `190`（`.`）= `SentencePunctuation` / `32`（Space）/ `13`（Enter）。
  - **検証（★ 実行した。⚠️ 予測ではない）**: 既定モード `gse-replay <fixture>` が **exit 0**（14 snapshot 行。
    ⚠️ `hmm_version 0.2.0 / engine 0.5.0` の WARN は**既存 fixture と同じベースライン**）/
    `--features` が **exit 0**（15 行・`pauses` が立つ行 2 件・`pastes` 総和 1）。
  - ⚠️ **ゴールデンの対象にはしない** —— ★ `replay.rs` のゴールデン一覧は
    `(ndjson, json)` の**明示ペア列**（`:3602-3610`）であり、fixture ディレクトリを走査していないので
    **新規ファイルを足しても snapshot テストは増減しない**。
  - ⚠️ ★ `scripts/verify-extraction-parity.sh:170` は fixture ディレクトリを `find` で**全走査する**。
    ★ 新規 fixture でも既定モードが exit 0 なので FAIL しない（★ 上で実測）。
    ⚠️ ただし同スクリプト自身が「差分に fixtures が含まれると偽 FAIL になりうる」と警告するので、
    **base=main と比較する用途では結果を鵜呑みにしない**（★ 同スクリプトは pin 済み verify に載っていない）。
- **トレードオフ**:
  - ⚠️ worker が `bin/replay.rs`（約 3600 行）を触れるようになる。★ 壊れれば pin 済み verify の
    ゴールデン 15 本が赤になるので、**黙って通り抜ける経路は無い**。
  - ⚠️ `instrument_rich.ndjson` は**合成データ**であり、実測の IME 挙動を代表しない。
    ★ `ime_shadow` の**行数は「変換回数」の代理にならない**（★ 起票 6・issue 002 の Background）。
    → ★ 本 fixture は **AC の非退化検査用**であって、分布の根拠には使わない。
- **影響範囲**: `issues/002.md` / `issues/005.md` / `issues/007.md` の Allowed Files /
  `002-acceptance.sh` / `007-acceptance.sh` / `_issue-plan.md §1` /
  ★ 新規 `src-tauri/tests/fixtures/instrument_rich.ndjson`

## 判断 13: ⚠️★★★ 検査は「**実 fixture で正常系が通る**」ところまで確かめないと、検証したことにならない

- **判断日時**: 2026-09-15（Opus 裁定セッション・2 回目／★ issue 002 の実行後）
- **背景**: issue 002 を Loop モードC で回したところ、**6 attempt すべて `acceptance_fail` → `abandoned`**
  （`_loop-run-report.md`: **$5.706873** / 14,591,909 tokens）。
- ⚠️★★★ **原因は実装ではなく、私が判断 12 で書いた検査のバグだった。**
  - ★ 落ちていたのは `002-acceptance.sh` の 1 行:
    「`prev/next_cat_counts` に `sentence_punctuation` が 1 度も現れない」。
  - ⚠️ ところが **`instrument_rich.ndjson` の 2 本の pause は、直前/直後が
    `alphabetic` と `backspace` しか無い**（★ 実測: 出現カテゴリ集合は `["alphabetic","backspace"]`）。
    → ★★★ **fixture の構造上、この検査は原理的に緑にならなかった。**
  - ★ **実装は正しかった**（⚠️ 実測で確認・推測ではない）: 行レベルの `sentence_punctuation` は **2**、
    IME は `dwell 1570`（= 650 + 920）/ `nav 5`（= 2 + 3）/ `abandon 1`、8 フィールドすべて在り、
    `super::extract_pause_resumptions`（001 の共有ヘルパ）を使い、**単体テスト 6 本が緑**。
- ⚠️★★★ **3 状態テストを実施したのに防げなかった。** ★ ここが本判断の要点である。
  - ★ 私は判断 12 で「検査自体を 3 状態（正常 / 壊れている / 誤検出しうる正当な形）で試す」を実行し、
    **17/17 通した**。
  - ⚠️ **しかしそれは「手書きの合成 JSON」に対してであって、「fixture が実際に出せる形」に対してではなかった。**
    ★ 正常系のサンプルを**自分で都合よく作った**ので、`sentence_punctuation` を手で置いてしまった。
  - → ★★★ **ルールを 1 つ足す（4 つ目の状態）**:
    **「実 fixture を実際に流して、正常系の前提が成立することを確かめる」**。
    ⚠️ 実装がまだ無い段階でも、**実装に依存しない前提**（＝ その fixture がその形を作れるか）は
    必ず確かめられる。★ 今回なら「pause の隣に文末句読点が在るか」を
    `jq` で 1 回見れば 6 attempt を使わずに分かった。
- **対処（★ 実行済み・実測で確認）**:
  1. **fixture を直した**: `1700000105450` / `105530` の `vk` を **73（I）→ 190（`.`）** にした。
     ★ 「文を書き終えて止まる」という自然な形であり、**2 本目の pause の直前が文末句読点になる**。
  2. **検査を 2 段にした**:
     - (a) **行レベルの計数** `sentence_punctuation` の総和 > 0 —— ★ pause と無関係に必ず立つので、
       **畳み込み（`punctuation` に統合）を最も確実に検出する**。
     - (b) pause 境界のカテゴリにも現れること —— ★ 14 種の語彙が保たれていることの実地検査。
  3. ★ **実測で (b) が空振りでないことを確認**: 出現カテゴリ集合が
     `["alphabetic","backspace","sentence_punctuation"]` になった。
- **同じ穴を他の issue でも先回りして潰した（★ 判断 13 の適用）**:
  - ⚠️★★★ **issue 004 の AC5** は `minimal.ndjson` で `delete_runs` 総和 > 0 を要求していたが、
    ★ 実測で **`minimal.ndjson` の backspace press は 1 個しかない**。
    → ⚠️ 「delete run は**連続 2 打以上**」と定義した実装では **0 になり、欠陥でないのに落ちる**。
    → ★ fixture を `instrument_rich.ndjson`（**backspace 3 連**）へ差し替え、
      **どちらの定義でも run が立つ**ようにした。併せて `delete_run_max >= 3` を足し、
      「1 打ずつ数えて走りを見ていない」実装を落とせるようにした。
  - ★ 003（`deep_silence` の 2600ms × 2 ＋ 43440ms）/ 007（`instrument_rich` の `capabilities` ＋
    `hook_health` 2 行、`minimal` の `capabilities` 不在）は **fixture 側の前提を実測で確認済み**。
  - ⚠️ 005 / 006 の非退化検査（`onset` が 1 回以上立つ / `restop_ms` が非 null）は
    **実装の既定パラメータに依存する**ので、実装前には確かめられない。
    ★ これは「検出器が何も検出しないなら緑に見えて無意味」という **AC 本来の要求**であり、
    fixture の欠陥ではない。⚠️ ただし落ちたときは **まず実装を疑う前に前提を確かめる**こと。
- **worker の成果は捨てていない**:
  - ★ worktree の未コミット作業（`boundary.rs` 258 行 ＋ `mod.rs` ＋ `replay.rs`）を
    commit **`284c754`** として保存し、**`a4400b9`** で base ブランチへ merge した。
  - ★ pin 済み verify 4 本は緑（**688 passed**（ベースライン 682 + 6）/ `OK: 15 snapshots match` /
    `cargo check` exit 0 / `clippy -D warnings` exit 0）。
  - ★ AC 対応の単体テスト 6 本を**名前指定で実行して緑を確認**した
    （`prev_cat_keys_are_key_categories` / `boundary_categories_match_hand_computed` /
    `space_enter_sentence_punctuation_are_counted_per_tick` / `ime_fields_aggregate_dwell_nav_abandon` /
    `no_pause_yields_empty_boundary_maps` / `duplicate_timestamps_do_not_misalign_pairs`）。
- **費用の記録（⚠️ 楽観的に丸めない）**: issue 002 = **$5.706873** / 14,591,909 tokens。
  ★ うち **実装 372 行は得られている**が、⚠️ **$5.7 のうちの大半は私の検査バグに払った**。
  ★ 001 の $3.53 + $3.60 と合わせ、**本タスクの Loop 費用は累計 $12.84**。
- **トレードオフ**: ⚠️ 検査を厚くするほど「検査自体のバグで落ちる」確率が上がる。
  ★ だから**厚くすることと、実 fixture で正常系を通すことは対**であって、片方だけでは害になる。
- **影響範囲**: `src-tauri/tests/fixtures/instrument_rich.ndjson` /
  `issues/002-acceptance.sh` / `issues/004-acceptance.sh` / `issues/004.md` の AC5 /
  ★ 以後の全 issue の acceptance の書き方

## 判断 14: issue 002 のレビュー指摘の裁定（★ `code-reviewer` ∥ `security-checker` を並列起動）

- **判断日時**: 2026-09-15（Opus 裁定セッション・2 回目）
- **前提**: 判断 11 で 005 / 007 の `recheck` を落とした代わりに
  「**merge 前に必ずレビュー 2 本を通す**」と決めた。★ 002 は `parse` だが、
  ⚠️ **`bin/replay.rs` を開けた最初の issue** なので同じ扱いにした。
- ★★★ **両者が独立に同じ HIGH を挙げた**（⚠️ どちらも**実測で再現**している）。

### HIGH-1: `ReplayEvent::ImeShadow` の型付け化が `--snapshot` の受理集合を狭めた → **採用（修正済み）**

- **指摘**: worker は `ImeShadow(serde_json::Value)`（読み飛ばし専用）を
  **4 フィールド必須の構造体**に変えた。⚠️ `run_replay` は**既知タグのパース失敗も `Err` にして
  中断する**ので、崩れた `ime_shadow` 行 1 本で**リプレイが丸ごと落ちる**。
- ★ 実測された落ち方（⚠️ 推測ではない）:
  | 入力 | 旧実装の結果 |
  |---|---|
  | `"abandon":0`（整数） | 逐語 `invalid type: integer 0, expected a boolean` |
  | `nav` 欠落 | 逐語 `missing field 'nav'` |
  | `"dwell_ms":null` | 逐語 `invalid type: null, expected u64` |
- ⚠️★★★ **これは `issues/002.md` の逐語「`--snapshot` / `--metrics` / `--calibration` / `--sweep`
  経路を変更しない」に直撃する。** ★ 「行型・フィールドの追加」は許可したが、
  **既存 variant の厳格化**は許可範囲の外である（★ 私が書いた制約文が曖昧だった）。
- ⚠️★★★ **私の 1 次案（`Option` ＋ `#[serde(default)]`）では足りなかった** —— ★ 実測で確認:
  `Option<bool>` は `0` を受け取れないので `"abandon":0` は**依然 exit 1**。
  → ★ **`code-reviewer` の案を採る**: variant を `Value` に戻し、構造化は
  `collect_all_ime_shadow_events` 内の専用 DTO（`ImeShadowDto`）が行う。
  ★ **これは `feat` 行の `LoggedFeatDto` という file 内の既存先例と同じ手法**である。
- ★ 併せて **`unwrap_or(0)` にしない**: 形の合わない行は**捨てて件数だけ warn** する。
  ⚠️ 0 に畳むと「変換が 0 だった」と「値が取れなかった」が同じになる
  （`capabilities.rs` 逐語「0 行は依然『判定不能』であって『信号が無かった』ではない」）。
- ★ **回帰を張った**: `tests::partial_ime_shadow_line_does_not_break_run_replay` が
  **上の 3 形すべて**について「`run_replay` が通る ＋ `FeatSnapshot` 列が 1 件も変わらない ＋
  `--features` 側は採らない」を固定する。
  ⚠️★★★ **issue 007 が `hook_health` を構造化するときも同じ形にすること**を variant の doc に書いた。
- ★ これは `hook_health`（2026-08-09）/ `activity_label` / `starve_window`（2026-09-14）と
  **同一の失敗様式の 4 度目**である。

### HIGH-2: fixture 変更が未コミットだった → **採用（本コミットで解消）**

- ★ `code-reviewer` は `db53b98..HEAD` の diff **だけでは AC2(b) が通らない**ことを実測で示した。
  ⚠️ working tree の `vk 73→190` が入って初めて緑になる。→ ★ 本コミットに含める。
- ★ 影響調査済み（`code-reviewer` 実測）: `instrument_rich` を参照する `.rs` / `.json` / golden は **0 件**。

### MEDIUM: 採用したもの

1. ⚠️ **`duplicate_timestamps_do_not_misalign_pairs` が名前どおりの検出力を持っていなかった** ——
   ★ 4 キーとも `Alphabetic` で、`prev_category` を 1 つ手前に取り違えても緑のまま通った。
   → ★ VK を `0x41 / 0x08 / 0x20 / 0x0D`（**全部別カテゴリ**）に替え、
   `prev_category` / `next_category` まで固定した。
   ⚠️★★★ **これは判断 13 と同じ病である**（★ 検査が検査になっていない）。
2. ⚠️ **collector → `build_feature_rows` の配線に `cargo test` 上の網が無かった** ——
   ★ `boundary.rs` の単体テストは `compute_boundary` を直接叩くだけなので、
   **`ime_events` 引数を落としても緑のまま**だった。
   → ★ `tests::ime_shadow_events_reach_feature_rows_through_the_collector` を追加し、
   NDJSON → collector → `build_feature_rows` の合計値と **tick 帰属**を固定した。
3. ⚠️★★★ **`ime_*` の `0` が「使わなかった」と「計器が無い」を区別しない** ——
   ★ `boundary.rs` の module doc に明記した（★ 判別は `Q` = issue 007 が持つ）。
   ⚠️ `Option` にはしない —— **`null` にしても両者は分けられない**ので、責務を 2 か所に散らさない。
4. ⚠️★★★ **`ime_shadow` の有無でグリッド原点が動く** —— ★ 実測で全行の `t_ms` が 100ms シフトする。
   `ime_shadow` は `config_gated`（環境によって丸ごと出ない）なので、
   ⚠️ **同じセッションを計器条件の違う環境で解析すると tick 割りが揃わない**。
   → ★ `mod.rs` の module doc に副作用と対処（**`t_ms` の絶対値で join し、tick 添字で揃えない**）を書き、
   回帰テストで原点の張り方を固定した。

### MEDIUM / LOW: 採らなかったもの（★ 理由を残す）

- ⚠️ **`--features` 出力に「由来の封筒」を付ける**（`security-checker` M2 後半）→ **起票 2 に回した**。
  ★ 出力形状の変更は **002〜007 の全 `acceptance.sh` の前提**（配列である）を壊すので、
  ⚠️ 走行中に変えると走り終えた issue の検査が全部無効になる。★ 007 の完了後に 1 度だけ裁定する。
- ⚠️ **`meta` に `os` を足す**（`security-checker` M2 前半）→ **起票 1 に回した**（★ 計器変更・ADR-032 の領域）。
- ★ `BTreeMap<String, u64>` → `BTreeMap<&'static str, u64>`（LOW・割当削減）→ **見送り**。
  ★ JSON 出力は同一で、`KeyCategory::as_str()` が `&'static str` を返すので安全だが、
  ⚠️ **レビュー修正のついでに型を触る利得が小さい**。
- ★ `KeyCategory::from_vk` の 3 回呼び（LOW）/ セッションファイルの 3 回読み（LOW）→ **見送り**。
  ⚠️ 後者は **tier が増えるたびに N パスになる**ので、**005 以降で 1 パス収集への集約を検討**する
  （★ ただし本 issue の範囲ではない）。
- ★ 戻り値が `Result<_, String>`（`rust-standards` は `anyhow::Result`）→ **見送り**。
  ★ `replay.rs` の `collect_*` は**全て `String`** であり、**ファイル内の一貫性を優先**する。
- ⚠️ エラーメッセージがセッションファイルの**絶対パス**を出す（`security-checker` L1）→ **見送り**。
  ★ 既存 `collect_key_events` と同一パターンで、**利用者自身が渡したパスを返すだけのローカル CLI**。
  ⚠️ 直すなら全 collector を一括で直す（★ 本 issue で 1 か所だけ直すと不整合になる）。
- ⚠️ fixture の `capabilities` ブロックが**手写しで無音 drift する**（`security-checker` L2）
  → **見送り（★ 起票しない）**。⚠️ ★ ただし **drift しても検査が落ちるのは 007 だけ**なので、
  007 の実装時に「`capabilities.rs` の実リストと突き合わせる」検査を足すか判断する。

### ⚠️★★★ Stop Condition の逸脱を 1 行残す（★ `code-reviewer` LOW の指摘）

- ★ `issues/002.md` の Stop Condition 逐語「**変更が 5 ファイル / 300 行を超えそうなとき**」に対し、
  実績は **372 insertions / 12 deletions（3 ファイル）**だった。
  → ★ **ファイル数は満たし、行数は超えた**。⚠️ worker は止まらずに完走した。
- **裁定**: ★ **例外として認める**。理由: 超過分の実体は
  ① `boundary.rs` の `#[cfg(test)] mod tests`（6 本）と ② doc コメントであり、
  ★ **Stop Condition が守ろうとしている「1 issue が大きくなりすぎる」危険とは別物**である。
  ⚠️ ただし **今後 issue を切るときは「300 行」にテストと doc を含めるのかを明示する**こと
  （★ 含めない運用にするなら `docs/loop-engineering.md` の基準 2 側を直す）。
  → ★ **起票はしない**が、次の分解セッションへの申し送りとしてここに残す。

### ★ 両レビューが「問題なし」と**追認**したもの（⚠️ 記録しておく）

- ★ 出力に**生 VK / 文字 / 打鍵順序は 1 バイトも出ていない**（`security-checker` が実測）。
  `prev/next_cat_counts` は `KeyCategory::as_str()` の 14 語彙 ＋ カウントのみで、
  **tick 内の順序を失う**ので匿名化 NDJSON より厳密に粗い。
- ★ 新規 fixture に**実データ混入は無い**（`security-checker` が VK をデコードして確認。
  `app_version:"0.3.0"` は実値 `0.1.35` と不一致＝実ビルドの指紋ではない）。
- ★ `abandon` を「迷い」と解釈する語は**コードにもコメントにも無い**（起票 6 を遵守）。
- ★ テストデータ `"abandon":0` → `false` は**弱体化ではなく訂正**（`logger.rs` の実書式は `bool`）。
- ★ ⚠️ 私が事前に挙げた懸念「同一 timestamp で pause のペア対応がずれるのでは」は **否認された** ——
  ★ `extract_pause_resumptions` の resumption 値は `windows(2)` 由来で、
  同一値 X で終わる窓のうち gap≥閾値になり得るのは **X の最初の出現だけ**（以降は gap=0）。
  → **resumption 列に同じ値は 2 度現れず、昇順どうしの単調走査で対応は一意**。
  ⚠️ ただし**テストがそれを示していなかった**ので、テスト側は上記 MEDIUM 1 で直した。
- ★ 入力検証は `collect_key_events` と**同水準**（`MAX_SESSION_BYTES` → 行ストリーミング → 行単位スキップ）。
  ★ `vec![Vec::new(); tick_count]` の確保は `MAX_FEATURE_TICKS` チェック**より後**にある。
- ★ 依存追加はゼロ（`Cargo.toml` / `Cargo.lock` / `package*.json` の diff が空）。

- **影響範囲**: `src-tauri/src/bin/replay.rs` / `src-tauri/src/analysis/feat_offline/boundary.rs` /
  `src-tauri/src/analysis/feat_offline/mod.rs` / `src-tauri/tests/fixtures/instrument_rich.ndjson` /
  `blockers.md`（起票 1・2・3）

## 判断 15: ⚠️★★★ 1 issue ずつ回す運用では `## Dependencies` の**箇条書き**は構造的に使えない

- **判断日時**: 2026-09-15（Opus 裁定セッション・2 回目／★ issue 003 の起動失敗から）
- **背景**: issue 002 を merge した後に `--issues 003` を起動したところ、**1 秒で die した**。
  ★ 実測の逐語:
  ```text
  loop-run: issue 003 の依存 002 が issues/ に存在しません
  [loop-run] ERROR: DAG の前提が壊れています (上記を修正してください)
  ```
  ⚠️ `issues/002.md` は**存在する**（★ メッセージの文言が誤解を招く）。
- **一次資料で確かめたこと**（⚠️ 推測ではない）:
  - `loop-run.sh:410-411`:
    ```bash
    ALL="$(issue_ids)"
    [ -n "$ONLY_ISSUES" ] && ALL="$(printf '%s' "$ONLY_ISSUES" | tr ',' '\n')"
    ```
    → ★★★ **`--issues` は `$ALL` を「issues/ の全部」から「指定した集合」へ *上書き* する。**
  - `preflight_dag`（`:435-448`）は依存先が **`$ALL` に無ければ die** する。
    → ★ **「issues/ に存在しません」は実際には「*今回の選択に* 入っていません」の意味**である。
  - ★ 仮に依存先を `--issues` に含めても解決しない —— `deps_met` は
    `issue_done` **イベント**で満たされる（`:422-431` / `:432`）ので、
    ⚠️ **完了済みでも events に `issue_done` が無ければ再実行される**（★ 002 がまさにそれ）。
- ★★★ **なぜ 1 issue ずつ回すのか（＝ なぜ回避策でなく前提の修正なのか）**:
  - ⚠️ `loop-spawn.sh:111` は `git worktree add -b "$branch" "$wtdir" "$start"` で
    **毎回 `base_branch` から切る**。★ `loop-run.sh` は issue 間で **merge を一切しない**。
  - → ⚠️ 003〜007 をまとめて 1 回で回すと、**全部が同じ base から枝分かれし、
    `feat_offline/mod.rs`（★ 全 issue の交差点）で衝突する**。
    ★ さらに 006 は 005 の `stall_onset` を**コードとして必要とする**ので、
    **005 を merge する前に 006 を走らせると成立しない**。
  - → ★★★ **「1 issue 回す → 検証 → レビュー → merge → 次」以外に正しい順序が無い。**
    ⚠️ その運用では `--issues` が常に 1 件なので、**箇条書きの依存は必ず die する**。
- **採用**: **003〜007 の `## Dependencies` から箇条書きを外し、散文で残す**。
  - ★ `issue_deps_raw`（`:161-166`）が拾うのは
    `^[[:space:]]*[-*][[:space:]]*(#|issue[[:space:]]*)?[0-9]{3}\b` に**一致する箇条書き行だけ**なので、
    **引用ブロックの散文は解釈されない**（★ エラーメッセージ自身が
    逐語「散文で自分に言及したい場合は箇条書きにしない」と言っている作法に従う）。
  - ★ **順序の制約は消していない** —— 各 issue に「**N-1 を merge してから N を回す**」と明記し、
    ⚠️ **担保するのは DAG ではなく人の merge ゲート**であることを書いた。
- ⚠️ **却下した案**:
  - ★ `--issues 003,004,...` でまとめて回す → ⚠️ 上記のとおり **mod.rs で必ず衝突**し、
    006 は 005 のコードを必要とするので**そもそも成立しない**。
  - ★ events に `issue_done` を手で書いて `deps_met` を満たす → ⚠️ モードC の原則
    （逐語「events の writer は … `scripts/loop-run.sh` **だけ**」）を破る。判断 9 と同じ理由で却下。
  - ★ `loop-run.sh` の `preflight_dag` を直す → ⚠️ **本タスクの範囲外**（★ Loop 基盤の改修）。
    → ★ **起票 4 として残す**（下記）。
- ⚠️★★★ **判断 9 は「002 だけ」を直したが、それは**対症療法**だった。**
  ★ 私は判断 9 の時点で「003→002 以降の直列は維持する」と書いたが、
  ⚠️ **`$ALL` が `--issues` で上書きされることを確かめていなかった**。
  → ★ **判断 13 と同じ病である**（★ 前提を実測せずに「維持できる」と書いた）。
  ⚠️ 今回は 1 秒で die したので費用はゼロだったが、**構造は同じ**である。
- **トレードオフ**: ⚠️ **DAG の機械的な門が無くなる**ので、
  ★ 順序を守るのは**人（＝ 本セッション）の規律だけ**になる。
  → ★ その代わり `tasklist.md` の実行チェックボックスと各 issue の Status が
  「どこまで merge したか」の単一の手掛かりになる。⚠️ **飛ばさないこと。**
- **影響範囲**: `issues/003.md`〜`issues/007.md` の `## Dependencies` / `_issue-plan.md §2`

### ⚠️ 起票 4（★ `blockers.md` へ）

★ `loop-run.sh` の `preflight_dag` は「**依存先が `--issues` の選択に入っていない**」ときに
逐語「**issues/ に存在しません**」と言う。⚠️ **ファイルは存在するので、この文言は誤診を誘う**
（★ 実際に 1 度誤読しかけた）。→ ★ 文言を直すか、
**「完了済み（merge 済み）の依存は満たされたものとして扱う」オプション**を足すかは Loop 基盤側の課題。

## 判断 16: issue 003 のレビュー指摘の裁定（★ 構造的欠陥は**決めずに上げる**）

- **判断日時**: 2026-09-15（Opus 裁定セッション・2 回目）
- **前提**: issue 003 は Loop が **attempt 3 で `issue_done`** に到達した（★ 本タスク初）。
  ⚠️ 自己申告を信じず、pin 済み verify 4 本 ＋ acceptance 2 本 ＋ AC 対応テスト名指定で
  客観確認したうえで `code-reviewer` / `security-checker` を**並列**起動した。

### ★★★ HIGH-1: `T1a` の分位点が構造的に退化している → ⚠️ **本セッションでは決めない**

- ★ `code-reviewer` が**誰も見ていなかった構造的欠陥**を見つけた:
  `PAUSE_THRESHOLD_MS`(2000) > `ENGINE_TICK_MS`(1000) なので **1 tick に pause は高々 1 本**、
  よって **`p50` / `p90` / `max` は常に同値**。★ 私も**全 14 fixture で実測して追認した**
  （`pauses > 1` = 0 件 / `p50 != max` = 0 件）。
- ⚠️★★★ **決めなかった理由**（★ ここが本判断の要点）:
  直し方は**集約窓を決める問題**であり、⚠️ **窓長は事前宣言事項**である。
  ★ `ADR-030 D4` が `W` / `q` / `B` を「P1 前に事前宣言する」と定め、
  `issues/005.md` は逐語で「**`W` / `q` / `B` の値を決めること**」を **Scope Out** にしている。
  → ★★★ **`T1a` の窓だけ裁定セッションが独断で決めるのは、同じ規律を片側だけ破ることになる。**
  ⚠️ **「直せるから直す」を選ばなかった**のは、直す行為そのものが事前登録の侵食だからである。
- ★ 代わりに入れた暫定（⚠️ 放置していない）:
  1. `Dispersion` の doc に**証明と 14 fixture の実測**を書き、
     「**`p50` / `p90` を分布の要約として読むな**」と明記した。
  2. `003-acceptance.sh` に「**現状 3 値が同値であること**」を固定する検査を入れた。
     ⚠️ 裁定が入ったら**この検査を先に書き換える**旨をコメントに書いた。
  3. → `blockers.md` **起票 7** に選択肢 (a) 窓を広げる / (b) `p50`/`p90` を落とす /
     (c) 判断 2 を見直す を、それぞれの代償つきで上げた。
- ⚠️ **issue 003 を差し戻さない**: ★ 実装は AC を満たしており、**欠陥は issue の切り方（判断 2）側**にある。
  ★ 差し戻しても worker には直せない（⚠️ Allowed Files の外の問題）。

### HIGH-2: テストが名前どおりの検出力を持っていなかった → ★ 採用（直した）

- ⚠️ `pause_durations_pairs_gap_with_resuming_ts` の入力は **pause 1 本・時刻重複なし**で、
  `i-1` が常に 0 だった。→ ★ `code-reviewer` が **mutation harness** を作り、
  「正常版 / `gap = sorted[i] - sorted[0]` 版 / `next_expected` を進めない版」の
  **3 実装すべてが同じ出力を返す**ことを実測した。
- ★ pause 2 本 ＋ 同時刻重複（開始側・終了側の両方）を足した。
  ★ **私も mutation で追認した**: `gap = sorted[i] - sorted[0]` に変えると
  逐語 `left: (6000, 6000) / right: (6000, 3000)` で赤くなり、戻すと緑になる。
- ⚠️★★★ **issue 002 の `duplicate_timestamps_do_not_misalign_pairs` と同型で 2 件目**である
  （★ 判断 14 の MEDIUM 1）。→ ★ **「テストを書いたら mutation で検出力を確かめる」を常態にする。**

### MEDIUM / LOW: 採用したもの

1. ★ **`serde_json` は NaN / Inf をエラーにせず黙って `null` に書き換える**
   （`security-checker` L2・`serde_json` の実装を実読して確認）。
   ⚠️ **AC4 の「要素 0 個 = `null`」と見分けがつかなくなる。**
   → ★ `tests::emitted_values_are_always_finite` を追加。
   **私も mutation で追認**（`m == 0.0` ガードを外すと
   逐語「全 IKI が 0ms: iki_cv が非有限 (NaN)」で赤くなる）。
2. ★ **`SessionIkiBaseline` は出力から厳密に復元できる**（`security-checker` L1）——
   `surprise = (tick_mean − μ)/σ` の `tick_mean` が**同じ行の `activity.mean_iki_ms`** として出るので
   2 行あれば μ / σ が解ける（★ reviewer が**小数 10 桁まで一致**を実測）。
   ⚠️ **新しい露出ではない**（★ 提出される匿名化 NDJSON の `key` 行が `(category, 相対 ms)` を
   **ms 分解能のまま**持つ。★ 私も `anonymize_line` を読んで追認した）が、
   → ★ **「baseline は出していない」を前提に判断すると誤る**ので doc に書いた。
3. ★ 標準偏差が**母集団版（÷ n）**であることを doc に明記（⚠️ tick 内 n は 2〜3 が支配的で差が小さくない）。
4. ★ nearest-rank の p50 が**線形補間の median と一致しない**ことを doc に明記
   （`[10,20]` → `10.0`。一般的な median は `15.0`）。
5. ★ `003-acceptance.sh` の非退化検査を **fixture 1 本に賭けない**形にし、
   ⚠️ **全行 null が「正しい」fixture**（`outcome_metrics` / `resumption_outcomes`）を
   **既知として列挙**した（★ 誤診して直しにいかせない）。
6. ★ `--features` の usage / doc コメントが「**T0 (activity)**」のままだったのを
   「Tier 別」に直し、**「手元の解析用中間成果物であり `gse-dataset` へ共有しない」
   「`t_ms` は絶対 epoch ms で匿名化を通っていない」**を明記した（→ 起票 5）。

### ⚠️★★★ 私が書いた検査が**また**誤検出した（★ 判断 13 の再発・ただし今回は 1 分で気づいた）

- ★ 判断 12 で入れた「閾値リテラルの直書き禁止」grep が、
  ⚠️ **私が HIGH-1 の説明として doc コメントに書いた `< 1000 < 2000` に当たって落ちた**。
- → ★ **コメント行を除外する段**（`grep -vE '^[0-9]+:[[:space:]]*//'`）を
  002〜006 の 5 本すべてに入れた。
- ★ **3 状態で確かめた**（⚠️ 今度は実コードで）:
  正常 = OK / **コードに実リテラルを注入** = 逐語「リテラルで直書き比較している」で NG /
  **doc コメント内の数値** = OK（誤検出しない）。
- ⚠️ ★ 教訓は判断 13 と同じで、**検査を厚くするほど検査自身のバグが増える**。
  ★ だから「厚くする」と「3 状態で試す」は**必ず対で**行う。

### 採らなかったもの（★ 理由を残す）

- ⚠️ **`pause_durations`（003）と `pause_boundary_pairs`（002）の 15 行の重複を今すぐ共通化する**
  → ★ **見送り**。`code-reviewer` 自身が「**003 の Allowed Files に `boundary.rs` が無い**ので
  今回抽出するのは違反」と述べ、**issue 005 で `pause_events()` へ一本化する**のが正しいと判断している。
  ★ 同意する。→ ⚠️ ただし **005 への申し送りとして起票 8 に残す**。
- ★ `mod.rs` が同じ press 列に対し **sort + pause 抽出を 3 回**独立に行っている（LOW）
  → ★ 同じく **005 で解消**する（⚠️ 3 か所が drift しうる点は起票 8 に書く）。
- ★ `iki_ms_by_tick.iter().flatten()` で baseline 母集団を作っている（LOW）
  → ⚠️ **tick 帰属規則を変えたとき baseline が黙って変わる**余地はあるが、
  ★ 現状 `press_intervals` と同値であり、**起票 7 の裁定で窓ごと変わる**可能性が高いので今は触らない。
- ★ `BTreeMap<String, _>` → `&'static str`（002 由来の LOW）→ ★ 引き続き見送り。

- **影響範囲**: `src-tauri/src/analysis/feat_offline/dispersion.rs` / `src-tauri/src/bin/replay.rs` /
  `issues/003-acceptance.sh` ＋ 002〜006 の acceptance（コメント除外）/ `blockers.md` 起票 5〜8


## 判断 17: issue 004 は**保留**し、005 へ進む（★ worker の停止を正しいと認める）

- **判断日時**: 2026-09-15（Opus 裁定セッション・2 回目）
- **背景**: issue 004 を Loop で回したところ **6 attempt すべて `acceptance_fail` → `abandoned`**。
  ⚠️ ただし **attempt 1〜3 と attempt 4〜6 は中身が違う**:
  ★ attempt 4 で worker は **issue 004 自身の Stop Condition に該当すると判断し、
  実装せずに停止して候補表を起票した**（commit `bd921b6`）。
- ★★★ **worker の判断は正しい。** ⚠️ 推測で実装しなかったことを**評価する**:
  - ★ `issues/004.md` の Stop Condition 逐語「**`rewrite` / `loop depth` の定義が本文なしでは
    一意に決まらないとき → 定義候補を 2〜3 出して止める（⚠️ 推測で 1 つ選ばない）**」。
  - ★ worker は 4 項目 × 3 候補の表を作り、**候補間で値が食い違うこと**を試算で示した
    （`D I D I D` 系列で alternation 数 = 4 / push-pop 深さ = 1）。
  - ★ かつ `delete_run_max` / `delete_runs` の **2 項目だけは一意に読める**と切り分けた。
- ★★★ **裁定セッションが worker の読めない一次資料を確認した**（⚠️ ここが本判断の核）:
  - ⚠️ worker は「`.idea/` は本 repo に存在しない（`Glob .idea/**` = 0 件）」と書いたが、
    ★ **実際にはローカルディスクに実在する**（20 ファイル）。
    ⚠️ **gitignore されているので worktree に現れないだけ**である
    （★ `git worktree add` は追跡ファイルしか持って行かない）。→ ★ worker には構造的に読めない。
  - ★ **私が `.idea/…-survey.md:189` を実際に読んだ**。逐語:
    `| T1c | revision topology | delete run、rewrite、再削除、loop depth、undo/redo 往復、局所 recurrence |`
  - → ⚠️★★★ **算出式は書かれていない。候補の *名前の一覧* である。**
    ★ 前後（§6.1 / §6.2）にも無く、§17.3 の「transition count と recurrence」は
    **オンライン特徴の類型**であって式ではない。
  - → ★★★ **worker の提案「`.idea/survey:189` の抜粋を転記するのが最短」は *実行できない*。**
    ⚠️ 転記すべき式が存在しない。★ **この経路は閉じた**（→ 起票 9 に追記）。
- **採用**: ⚠️ **issue 004 を保留し、実装しない。★ 005 へ進む。**
- **理由**:
  - ★★★ **定義を作るのは研究者の判断**であり、⚠️ **裁定セッションが代わりに選ぶのは
    「推測で 1 つ選ばない」という issue の指示を、主体を変えて破ることになる。**
    ★ 判断 16（`T1a` の集約窓を決めなかった）と**同じ規律**である。
  - ★ **005 / 006 / 007 は `revision` に依存しない**（★ 005 は `net_production`、
    006 は `t0`、007 は `capabilities` を要る）。→ ⚠️ **004 を待つ理由が無い。**
  - ⚠️ **部分実装（2 項目だけ）もしない** —— ★ AC1 が 6 フィールドを要求しており、
    半分の Tier を出力に載せると**キー集合の検査を 2 度書き換える**ことになる
    （★ 002 / 003 で入れた「キー集合の完全一致」の検査が二重に揺れる）。
- **⚠️ 費用の記録**: issue 004 の 6 attempt。★ うち **attempt 1〜3 は推測実装の試行**で、
  ⚠️ **worker 自身が「3 回の推測実装がすでに失敗している。4 回目を重ねるのは
  issue 002 で $5.7 を捨てた失敗様式の再演になる」と書いて止めた**。
  → ★★★ **モードC は「正しく止まった」ことを表現できない** —— ⚠️ `loop-run.sh` からは
  acceptance が落ち続けたようにしか見えず、`abandoned` になる。
  ★ これは **判断 7 の「運用上の発見 1」と同じ構造の 2 度目**である。
- **★ 併せて起票したもの**:
  - **起票 9 への追記**: `.idea/survey` に算出式は無い（★ 資料探索では解けない）。
  - **起票 10**: ⚠️★★★ worker が **`git checkout main` で worktree 隔離を自分で外せた**。
    ★ `docs/loop-engineering.md` が「未検証」と書いていた
    「`allow: ["Bash(git *)"]` が deny の綴りを迂回する」が**実測された**。
    ⚠️ 今回実害は無かったが**それは偶然**（★ commit 後だったため。
    001 / 002 / 003 の worker は**いずれも未コミットで終わっている**）。
- **見直しタイミング**: ★ 研究者が 4 項目の定義を選んだとき
  （→ `issues/004.md` の Background に算出式を明記してから `/loop-issue 004` を再実行する）。
- **影響範囲**: `issues/004.md`（Status: blocked）/ `blockers.md` 起票 9・10 / `tasklist.md`

## 判断 18: issue 005 のレビュー裁定 —— ⚠️★★★ 削除区間に onset が立つ。**006 の前に是正 issue 008 を回す**

- **判断日時**: 2026-09-18（Opus 裁定セッション・3 回目）
- **前提（⚠️ 手順の逸脱を先に記録する）**: 判断 11 は「005 / 007 は **merge 前に必ず** `code-reviewer` ＋ `security-checker` を通す」と決めたが、
  ⚠️ **005 はレビューを通さずに merge された**（`da1b8b2`・2026-09-15）。→ ★ 本セッションが merge 後にレビュー 2 本 ＋ 客観検証を並列で走らせた。
  ★ **基準 5 を本当に破っていた**（判断 11 逐語「省略したら基準 5 を本当に破ったことになる」）ので、**是正が merge されるまで 005 を「完了」と扱わない**。

### 客観検証（★ test-runner・実測）

| 検査 | 結果 |
|---|---|
| `cargo test --workspace` | **exit 0**（**702** passed = lib 664 ＋ gse_replay 37 ＋ 1。⚠️ worker の「664」は lib だけの本数で、欠落ではない） |
| ゴールデン replay | **exit 0**（`OK: 15 snapshots match`） |
| `cargo check` / `clippy -D warnings` | **exit 0** / **exit 0** |
| `002` / `003` / `005-acceptance.sh` | **OK** |
| ⚠️ `001-acceptance.sh` | ⚠️★★★ **NG** —— 最上位キー集合を `["activity","t_ms"]` に固定しており、**002 で `boundary` が加わった時点から落ちていた**（★ 下記「検査の穴」） |

### ★★★ 両レビューが独立に実測したもの（⚠️ 推測ではない）

- **HIGH（両者）: D8 (b-2) 未実装 → 削除区間の内側に onset が立つ。**
  ★ `security-checker` は `redaction.rs` の `retain_outside_range` を忠実に再現した削除を 4 ケースで行い、
  **全ケースで「元 0 件 → 削除後 1 件、`t0` は区間の内側」**を得た（`s` は「削除直前の最後の打鍵 ＋ W」とミリ秒一致）。
  ★ `code-reviewer` も合成入力で `t0` が穴の内側に出ることを再現した。
  ⚠️ worker の「D8 は Goal (D2〜D6) の外」は**成り立たない** —— ★ **D3 自身**が抑制表 1 行目（「1Hz `feat` 列の穴」）と
  評価時刻集合の但し書き（「D8 の理由で連続が切れた場合 … 第 3 項を置かない」）で (b-2) を Goal の中へ引き込んでいる。
  ⚠️ **ただし worker には作れなかった理由も実在した**: `feat` 行と `key` 行を**両方持つ fixture が 0 本**で、素直に実装すると
  `deep_silence` の onset が 0 になり非退化検査が落ちる。→ ★ **Stop Condition で止めて上げるべき案件だった**。
- **HIGH（`code-reviewer`）: 末尾の沈黙の onset が出力から黙って消える。** ★ グリッドの右端が「最後の入力イベント」なので、
  `t0 >= 最後の打鍵 ＋ W ＋ θ` は**構造的にグリッドの外**に出て捨てられる（★ 検出器の内部では検出できている）。
  ★ 引き継ぎ §3 が「005 が補うこと」と名指しした 2 点（閉じない末尾の沈黙・`feat` 行の穴）が**両方とも残っていた**。
- **HIGH（`code-reviewer`）: テストの検出力** —— mutation 11 本のうち **確認ループを外す / 不応期を外す / θ = max / θ = 中央値 /
  net・θ に 5 秒の先読み / onset を `s` の tick に載せる** が**緑のまま**（★ 判断 14 MEDIUM 1・判断 16 HIGH-2 と同型の **3 件目**）。
- **HIGH（`code-reviewer`）/ MEDIUM（`security-checker`）: D4 の小標本** —— nearest-rank で `n <= 99` なら `ceil(0.99n) = n` なので
  **θ は常に最大値**。★ 削除区間をまたぐ gap が θ に混ざると `θ = 50,064ms`（跨ぎ gap とミリ秒一致）になり、
  **削除していない別エピソードの `t0` が 49.7 秒ずれる**（`security-checker` 実測）。
- MEDIUM: 同一 tick の onset を**黙って上書き** / **O(N²)**（実測: 15 万打鍵 debug で **56 秒**、検出器以外は **2 秒**）/
  既定値が生リテラル `30_000` / `task_kind` が常に `null`（`instrument_rich` は `argumentative` を宣言しているのに）。
- LOW: `t + W` の加算オーバーフローで debug ビルドが panic（`security-checker` 実測）。

### ★★★ 追認したもの（⚠️ 記録しておく）

- ★ 検出器の中核（`s` を「窓から抜ける時刻」に置く・`t0 = s + θ`・θ を `s` 時点で凍結する）は D3 の逐語どおり（`code-reviewer`）。
- ★ **新しい露出は無い** —— `--features` は stdout のみ・配布物に `gse-replay` は入っていない・
  θ は提出される匿名化 NDJSON から再計算できる（`security-checker`）。★ **原因ラベルも無い**（grep 0 件・実測）。

### 裁定

- **採用**: ⚠️★★★ **006 の前に是正 issue 008 を回す。** 理由:
  - ★ 006（`restart`）は **`t0` を原点にする**。偽の onset（削除区間の内側）と消える onset（末尾）を抱えたまま 006 を積むと、
    **転帰側がその歪みをそのまま継承する**。
  - ★ HIGH は**規則として ADR に書かれている**もの（D3 / D8 (b-2) / D4 母集団）であり、**定義を作る案件ではない**
    （⚠️ 判断 16 / 17 の「決めずに上げる」とは性質が違う）。★ memory「HIGH/MEDIUM を backlog に punt しない」にも従う。
  - ⚠️ 005 の差し戻しではなく**新しい issue** にする —— ★ 005 は merge 済みで、Allowed Files も fixture の禁止も 005 の前提のままでは直せない。
- ★ **観測区間の規則**（`issues/008.md` の「規範となる定義」）を裁定した。要点:
  1. ★ **観測区間 = `feat` 行の隣接差が `hole_gap_ms` 以下の極大な連続**。⚠️ **最初の `feat` 行より前・最後の `feat` 行より後は区間外**。
     → ★ D3「セッションが終わった場合は第 3 項を置かない」と D8 (b-2) を **同じ 1 規則**で受ける（★ 原因を 1 つも区別しない）。
  2. ⚠️★★★ **`feat` 行が 1 本も無いファイルでは onset を立てない。** 理由: `feat` は `capabilities.rs::unconditional` の行種であり、
     ★ ADR-013 D4 の読みで **0 行 =「出なかった」**と読める（`threshold_gated` の「判定不能」とは違う）。
     ⚠️ 逆の「0 行なら穴なし扱い」は、**全 `feat` 行が消えた削除済みログで全区間に偽 onset を立てる**（fail-open）。
     ⚠️ 代償: `deep_silence` を含む `feat` 無しの合成 fixture と、`feat` 記録以前の旧形式ログでは onset が 0 になる。
     ★ 出力の `is_onset=false` は「判定不能」と「onset なし」を区別しない —— ★ **その区別は `Q`（007）の `observability_mask` が持つ**
     （★ 判断 14 MEDIUM 3 の `ime_*` の `0` と同じ責務分担）。
  3. ★ `hole_gap_ms` の既定 = **`2 * ENGINE_TICK_MS`**（★ 「1Hz の予定行が少なくとも 1 本欠けた」の構造的な下限）。
     ⚠️ **値は `W` / `q` / `B` と同じ事前宣言事項のプレースホルダ**（→ 起票 15）。
  4. ★ グリッドの右端 = **max(最後の入力イベント, 最後の `feat` 行)**。⚠️ 原点は変えない（★ 002 / 003 の `t_ms` を動かさない）。
     ★ onset は必ず 2 打鍵以上の後にしか立たない（θ に gap が要る）ので、原点より前には落ちない。
  5. ★ `task_kind` = **`s` 時点で有効な宣言**（`ts <= s` の最新）を onset 行に記録。⚠️ θ の計算には使わない（issue 005 Scope Out）。
- ★ **fixture は裁定セッションが作った**（★ 判断 12 の先例）: `src-tauri/tests/fixtures/stall_onset_observed.ndjson`（930 行・合成）。
  ⚠️ 既存 fixture は **1 本も書き換えていない**。
  - ★ **判断 13 の第 4 状態（実 fixture で正常系が通るか）を実装前に確かめた**: Python の参照実装（仕様どおり素直に書いたもの）と
    手計算が一致した（元 = `t0` {40160, 187600} / 削除版 = {40160, 187600}）。
  - ⚠️★★★ **最初の設計では検査が機能しなかった**（★ 実測で気づいた）: 削除区間の後に打鍵が無いと、
    **H1（末尾が落ちる）が H2（削除区間に立つ）を覆い隠し**、現行実装でも削除区間に onset が出なかった。
    → ★ 削除区間の後に打鍵（`T+145000〜155000`）を足し、**現行実装で `t0 = T+132350`（区間の内側）が出る**ことを確認した。
- ★ **`008-acceptance.sh` を 3 状態で試した**（★ 判断 13 / 16 の規律）:
  | 状態 | 結果 |
  |---|---|
  | 壊れている（現行実装） | ★ NG（AC1 逐語「実際: [[37560,40160,2600]]」＝ 末尾の onset が欠ける） |
  | 正しい（参照実装を `ACC_REPLAY_CMD` で差し込む） | ★ 出力検査（AC1 / 2 / 3 / 7 / 14 / 18）はすべて通過し、ソース検査（AC8）で止まる ＝ ソースがまだ旧実装なので想定どおり |
  | 誤検出しうる正当な形 | ★ doc コメント・テスト内の `30_000` は OK、本体の直書きは NG（小さな合成ファイルで確認） |
- ★ **AC18（計算量）の閾値 20 秒の根拠**: 15 万打鍵 debug で **現行 56 秒 / 検出器を空にした一時コピーで 2 秒**（実測）。

### ⚠️★★★ 検査の穴（★ 今回見つけた 2 件）

1. ⚠️ **`001-acceptance.sh` の最上位キー集合が 002 以降ずっと NG だった。** ★ 各 issue の裁定が**自分の acceptance しか回していなかった**ので誰も見ていない。
   → ★ 集合を現状（`activity` / `boundary` / `dispersion` / `stall_onset` / `t_ms`）に直し、「Tier を足す issue を merge したら 1 語足す」をコメントに書いた。
   ★ **以後、merge ゲートでは 001〜最新の acceptance を全部回す**（★ 004 は保留中なので除く）。
2. ⚠️ **判断 16 のコメント除外が 001 に入っていなかった**（★ 002〜006 だけ）。★ 集合を直した途端、
   判断 16 が足した doc コメント「`< 1000 < 2000`」で落ちた。→ ★ `grep -rn` の出力形（`path:line:content`）に合わせた除外を足し、
   3 状態（実リテラル注入 = NG / コメントのみ = OK）で確かめた。

### 本 issue で直さないもの（★ 起票した）

- ⚠️★★★ **修飾キー規則（D3）** —— ★ `KeyCategory::Modifier` は **Shift（`0x10` / `0xA0` / `0xA1`）を含む**（`anonymize.rs` 実測）。
  → ⚠️ 逐語どおり実装すると**大文字・記号の入力まで産出から外れる**。★ 匿名化データでは Shift と Ctrl を区別できない。→ **起票 11**（★ ADR の定義の穴）
- IME 変換中の抑制 → **起票 12** ／ ポインタ両極 → **起票 13** ／ D4 の小標本（`warmup_count` の値・`cold_start` の集団 prior が存在しない・刻印）→ **起票 14**
- `hole_gap_ms` の値 → **起票 15** ／ 事前宣言値を外から渡す経路（CLI）→ **起票 16**
- ★ 起票 8（pause 対の一本化）は **005 の Allowed Files に `boundary.rs` / `dispersion.rs` が無く実行不能だった**（`code-reviewer` L4）。
  ⚠️ 008 でも範囲外（★ 検出器の是正に集中する）。→ ★ **起票 8 は開いたまま**。
- ★ 起票 6（`T1a` にも穴の扱いが要るか）は **008 の観測区間の規則が確定した後に判断する**（★ 同じ規則を `T1a` に当てるかは別裁定）。

- **Stop Condition の「300 行」**: ★ 判断 14 の申し送りに従い、**008 では「テストと doc を含めない」と明示した**。
  ★ 005 の 396 行（本体 約 160 行）は**例外として認める**（★ 判断 14 と同じ理由）。
- **影響範囲**: `issues/008.md`（新規）/ `issues/008-acceptance.sh`（新規）/ `issues/005-acceptance.sh`（fixture 差し替え）/
  `issues/001-acceptance.sh`（最上位集合・コメント除外）/ ★ `src-tauri/tests/fixtures/stall_onset_observed.ndjson`（新規）/
  `blockers.md` 起票 11〜16 / `_issue-plan.md` / `tasklist.md`
