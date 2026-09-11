# code-reviewer 報告

- **レビュー日**: 2026-09-07 / **対象**: 未コミット差分 (`metrics.rs` / `intervention.rs` / `intervention_eval.rs` / `replay.rs` / `build_analysis_db.py` / fixtures / tests)
- **実行した検証**: `cargo test --lib analysis::metrics` = **41 passed / exit 0** ・ `cargo clippy --lib --all-targets` = **新規コードに警告 0**

## 全体評価

★ 「推定器を出口から外す」という核心は **構造で** 達成されている (`compute_receipt_free_resumption` が `feats` を引数に取らない)。
⚠️ ただし **Aalen-Johansen を地平まで外挿してしまう経路が 2 つ**あり、どちらも主要アウトカムを **1.0 側へ** 押し上げる。

## HIGH (必須対応)

### H1. `metrics.rs:526-560` — 追跡が地平に届いていなくても CIF を「観測済み」として返す

`cif_receipt` は打ち切りを `times` から除外する (`:530-534`) ため、**全事象が `Censored` だと `times` が空**になり、
ループが 1 度も回らず `Some(0.0)` を返す。呼び出し側 (`:593-594`) が `1.0 - 0.0` にするので、
**`receipt_free_at_5min = Some(1.0)` = 「5 分間 1 件も受領しなかった」** と読める値が出る。
実際には *30 秒で観測が終わっただけ* かもしれない。リスク集合が地平で空でも `None` にする判定が無い。

- ★ 一次の裏取り: `scripts/fixtures/analysis_join/metrics/P101/windows/sess_b.metrics.json` が
  まさに `event_count:1 / censored_count:1 / receipt_free_at_5min:1.0` を持つ。★ **フィクスチャ自身がこの病理を正常値として固定してしまっている。**
- ⚠️ 判断 4 (decisions.md) は原点を再開時刻に置いた理由を「B は大半が打ち切りになるから」と書くが、
  ★ A でも **セッション末尾に近い再開は必ず打ち切り**であり、地平 10 分は届かないことが多い。
- **修正方針**: `cif_receipt` の冒頭で追跡上限を見る ——
  `if outcomes.iter().map(|o| o.elapsed_ms).max().unwrap_or(0) < horizon_ms { return None; }`。
  ★ 併せて `ReceiptFreeResumption` に **`n_at_risk_at_5min` / `n_at_risk_at_10min`** を出し、読み手が外挿を棄却できるようにする。

### H2. `metrics.rs:495-499, 510` — 「1 打鍵で再離席」が `elapsed_ms = 0` の競合事象になり、主要アウトカムを飽和させる

`left_again_at` は `w[0].timestamp >= t0` を許すので、**再開後の最初の打鍵がそのまま次のギャップ開始**になれる。
そのとき `at == t0` → `elapsed_ms = 0` (`:510`)。`cif_receipt` では t=0 の競合事象が
`surv *= 1 - (d1+d2)/n_j` (`:557`) で**受領が起きる前にリスク集合を食い潰す** → CIF が下がり **`receipt_free` が 1.0 へ寄る**。

- ★ 一次の裏取り (コード追跡): `keys = [11_000, 192_000, 373_000]` ＋ episode `[10_000, 11_000]` のとき、
  `segment_resumptions` は t0=192_000 の事象を 1 件作る (`:449-466`) → `classify_resumption` は窓 `(192_000, 373_000)`
  (gap 181s >= 180s, `w[0].timestamp == t0`) を拾い `LeftAgain{elapsed_ms: 0}` → `receipt_free_at_5min = Some(1.0)`。
  ⚠️ **「戻ってきて 1 打鍵してまた消えた」が満点になる。**
- **修正方針**: 再開の実体を要求する。`left_again` 候補から `w[0].timestamp == t0` を除く (= 最低 2 打鍵)、
  もしくは `elapsed_ms == 0` の outcome を CIF から外し `degenerate_count` として別に出す。
  ★ どちらでも既存テスト (`resumption_outcome_left_again_is_competing` は elapsed 1_000) は緑のまま。

## MEDIUM (推奨対応)

### M1. `metrics.rs:404-408` — 事象単位のデータが 1 バイトも外に出ないので、CIF を跨いでプールできない

`ResumptionOutcome` は `Serialize` を derive していない。`--metrics --json` に載るのはセッション単位の集計だけ。
⚠️ ところが `scripts/build_analysis_db.py:129-137` の注意書きは
逐語「pool the rfr_* counts (or re-run gse-replay over the pooled sessions)」と書くが、
★ **件数の合算は Aalen-Johansen ではない**し、`gse-replay` はセッション 1 本しか取らない (`replay.rs:829` `args.session_path`)。
→ ⚠️ **N=125 事象 / 6 名 (decisions.md 判断 1) を束ねる本解析が、現状の成果物からは実行できない。**
- **修正方針**: `ResumptionOutcome` に `Serialize` を付け、`--metrics --json` に `(elapsed_ms, kind)` の行を出す
  (★ 内容非依存の相対時間なので `data-privacy` ルール 1 に抵触しない。★ 判断としては ADR-024 に一行足す価値がある)。

### M2. `probe_scheduler.rs:153-154` — 180_000 の再定義が 1 か所残っており、SSOT の主張が repo 全体では成立していない

`metrics.rs:156-157` の新しい doc は逐語「**別の場所で 180_000 を再定義しないこと**」と書き、
テスト `away_gap_default_matches_intervention_ssot` (`metrics.rs:1697-1703`) がそれを固定する。
⚠️ ところが `ProbeConfig::default()` は `away_idle_ms: 180_000` をハードコードし、コメントで
「(intervention.rs AWAY_IDLE_MS と一致)」と*人手で*保証している。★ `pub` 化した今、参照に替えられる。
- **修正方針**: `away_idle_ms: crate::analysis::intervention::AWAY_IDLE_MS` にし、AC-3 のテストに 1 行足す (挙動不変)。

### M3. `scripts/tests/test_build_analysis_db.py:187-199` — t9 が「非 NULL」しか見ておらず、取り違えを検出できない

`assertNotEqual(row["rfr_event_count_sum"], "")` は、`_lift_outcome_field` が
`receipt_count` を `rfr_event_count` 列へ入れてしまっても**緑のまま**通る。
⚠️ かつコメント「sess_a (4 events) and sess_b (1 event) are both P101 ... at least one must be present」は不正確 ——
`scripts/fixtures/analysis_join/sessions.csv` では **sess_a=pre / sess_b=post** なので、
`("P101","pre")` 行は **sess_a 単独**であり、値は一意に決まる。
- **修正方針**: `assertEqual(row["rfr_event_count_sum"], "4")` / `assertEqual(row["rfr_receipt_free_at_5min_avg"], "0.5")`
  のように**期待値を書く**。★ ついでに `rfr_receipt_count_sum == "2"` も足すと列の取り違えを塞げる。

### M4. `metrics.rs:249` — `stuck_episode_count` の新 doc「(= 各比率の分母)」が事実と違う

`pflow_exit_manual_gain_rate` の分母は `pflow_exit_episode_count` (`:660` `ratio(pflow_exit_manual_gain, pflow_exit_count)`)。
⚠️ ADR-023 の指摘 C が **まさにこの分母の違い**を問題にしていたので、ここで曖昧に戻すのは惜しい。
- **修正方針**: 「`pflow_exit_without_receipt` / `paste_after_stuck_rate` の分母」と限定して書く。

### M5. 実装と矛盾したままの一次文書が 2 件残っている (★ レビュー時点)

- `experiments/20260906-interruption-resumption-arm1/notes.md:136-143` — **報告時に必ず併記する定型文**が
  逐語「`receipt_free_resumption` の「再開」判定には 3 クラス事後確率 `p_flow` を用いている」と書いており、
  ⚠️ **本変更で偽になった**。§5 の表も副次を `stuck_exit_without_receipt` と呼んでいる (→ `pflow_exit_without_receipt`)。
  ★ requirement.md のスコープ 6 / AC-7 が未達。
- `.claude/skills/physical-anchor/SKILL.md:180` — `self_recovery_without_paste` を指標名として案内している。
  ★ Skill は実装前に読まれる契約なので、存在しない識別子を指したままにしない。
- ★ `docs/glossary.md` / `docs/adr/README.md` / `ADR-024` はレビュー中に更新が入ったことを確認済み (この 2 件だけ残)。

## LOW (任意対応)

### L1. `metrics.rs:495-498` — `classify_resumption` が事象ごとに `keys` を先頭から走査する
`keys.windows(2).filter(|w| w[0].timestamp >= t0)` は毎回インデックス 0 から回るので O(E·K)。
★ ただし **O(n^2) にはならない**: 事象数 E は「180 秒以上のギャップ」の個数なので `E <= session_len / 180s`
(8 時間でも 160)。★ かつ実行経路は `gse-replay` のオフライン集計 (`replay.rs:834`) で、
**フックコールバック内ではない** (`hook-constraints` 非該当)。
- **提案**: `keys` は昇順が保証されている (`replay.rs:1470` `out.sort_by_key`) ので `partition_point` で
  開始位置を求めれば O(E log K + K)。急がないが、将来 O1 の長時間セッションで効く。

### L2. `metrics.rs:545` — `if n_j <= 0.0 { break; }` は到達しない
`t` は非打ち切り outcome の `elapsed_ms` 由来なので、その outcome 自身が必ず `elapsed_ms >= t` を満たし `n_j >= 1`。
★ 0 除算・NaN はこの関数では起きない (要件 1 の確認結果)。⚠️ ただし「守れているように見える」ことで **H1 を見落としやすくしている**。
- **提案**: この行を H1 の地平ガードに置き換える。

### L3. `metrics.rs:908` — 注意書きの位置が 1 行ずれていて逆の意味に読める
`// ⚠️ 以下 2 本は p_flow 依存` が `manual_contribution_ratio` の引数行末に付いている。
★ `manual_contribution_ratio` は **唯一推定器に依存しない対照**なので、行内注釈だと真逆に読める。
- **提案**: 次の `push_str` の直前に独立行で置く。

### L4. `metrics.rs:673-679` vs `:488-492` — paste 列の整列前提が関数間で食い違う
`observation_end_ms` は `pastes.last()` (昇順前提)、`classify_resumption` は `.filter().min()` (前提なし)。
★ `collect_paste_events` が `sort_by_key` するので現状は無害。
- **提案**: どちらかに寄せる (`pastes.iter().map(|p| p.timestamp).max()` が安い)。

### L5. フィクスチャ 3 件が改名と無関係に全面リフォーマットされている
`scripts/fixtures/analysis_join/metrics/**/sess_{a,b,c}.metrics.json` は
`confusion.matrix` / `per_class` が 1 値 1 行に展開され、キー 3 個の改名に対して **59 行差分**になっている。
- **提案**: 次回は整形を分離するか、整形コミットを 1 本立てる (レビュー負荷と `git blame` の劣化)。

### L6. `scripts/build_analysis_db.py:233,239` — `_collect_survey_files` が二重定義 (★ 既存)
`git show HEAD:` でも `:185,191` に同じ重複があり **本変更が持ち込んだものではない**。
★ ただし本変更が触るファイルなので、ついでに 1 本落とすと安全 (後段の定義が勝つため挙動は変わらない)。

### L7. `scripts/build_analysis_db.py` `_lift_outcome_field` — 新形式の `null` でも legacy を見に行く
`value is None` は「キー不在」と「値が JSON null」を区別しない。★ 新旧のキーが同居するファイルは今は無いので実害なし。
- **提案**: 意図なら 1 行コメント、厳密にするなら `if name not in outcome:` にする。

## 良かった点 (★ 積極的に評価する)

1. ★★★ **AC-2 が「約束」ではなく「型」で守られている** —— `compute_receipt_free_resumption` (`metrics.rs:567-573`) は
   `feats` を**引数に取らない**。★ 将来 p_flow を混ぜようとすると**シグネチャを変えるしかない**ので、レビューで必ず目に入る。
2. ★★★ **`receipt_free_resumption_has_no_pflow_dependency` (`:1795-1837`) は空回りしていない** ——
   `feat(ts, p_flow, p_incubation, p_stuck)` の引数順に照らすと `(0.8,0.1,0.1)` ⇄ `(0.1,0.8,0.1)` で
   **p_stuck 列が完全に同一**であり、`assert_eq!(episodes, ...)` でトリガー同一性も明示的に固定している。
   ★ 対照側の `pflow_exit_without_receipt` が 1.0 → 0.0 と**実際に動く**ので、「不在」の検出力がある。
3. ★★★ **`pflow_exit_without_receipt_is_biased_by_window_length` (`:1846-1880`) が秀逸** ——
   バイアスを直すのではなく**仕様として固定**した。★ paste は同一時刻・同一文字数のまま 0.0 → 1.0 が反転する構成で、
   「窓長依存」という新発見 1 を**実行可能な形で**残している。これは指標を降格するときの正しい作法。
4. ★ **AJ の漸化式そのものは正しい** —— リスク集合 `elapsed_ms >= t` (`:544`)、同時刻の打ち切りを at-risk 扱い、
   `cif += surv * d1/n_j` → `surv *= 1-(d1+d2)/n_j` の順序 (`:556-557`) は標準どおり。
   ★ `cif_receipt_matches_hand_computation` が競合込み 3 事象で 2/3・1/3 を手計算と突き合わせており、「壊れている」を検出する側になっている。
5. ★ **改名がコードでは取りこぼしゼロ** —— 6 識別子を grep したところ、生きた参照は 0 件。
   残るのは (a) 意図した「旧名」doc、(b) 意図的に旧名据え置きの `P104/sess_d` フィクスチャ、
   (c) python の alias 表のみ。★ 据え置き 2 件 (`recovery_window_ms` フィールド群 / `DEFAULT_DEFER_RECOVERY_WINDOW_MS`) も
   **Serialize 済み JSON キーだから**という理由が design.md に一次で書かれている。
6. ★ **`_lift_outcome_field` の legacy fallback は `is None` 判定で正しい** (要件 4) ——
   `0.0` / `false` / `0` は legacy に落ちない。★ かつ t8 が `"0.0"` (≠ `""`) を assert して**その分岐を実際に踏んでいる**。
7. ★ **規約遵守**: `println!`/`eprintln!` なし・依存 crate 追加なし・`analysis/` は OS 非依存のまま・
   `intervention.rs` → `metrics.rs` の参照は `analysis/` 内で閉じている (`architecture-rules` ルール 2 適合)。
   clippy の新規警告 0 (metrics.rs の既存警告は `:936/948/1031/1049` のみで本変更と無関係)。
8. ★ **オーバーフロー処理は網羅的** (要件 1) —— `saturating_sub` / `saturating_add` / `.max(t0)` が
   `:452, :457, :498, :506, :510` に漏れなく入っている。★ u64 の underflow 経路は見つからなかった。
